from os import error
import numpy as np
import re
import cv2
import glob
from bb import getIMAGEPOSITION
from validate import Predict
import tensorflow as tf
import itertools
import logging

logging.basicConfig(level=logging.DEBUG)

numeric = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0']
characters = ['X', 'Y', 'Z']
symbols = ['-', '+']
pc = Predict()


def get_equtaion_list(path_list):
    import time
    main_list = []
    for idx, image_path in enumerate(path_list):
        logging.debug(f"Processing image {idx+1}/{len(path_list)}: {image_path}")
        start_time = time.time()
        
        char_list = []
        final_crop = cv2.imread(image_path)
        if final_crop is None:
            logging.error(f"Could not read image: {image_path}")
            continue
            
        bbgetter = getIMAGEPOSITION(image_path)
        bbs = bbgetter.get_bounding_box()
        logging.debug(f"Found {len(bbs)} bounding boxes in {time.time() - start_time:.2f}s")

        char_start_time = time.time()
        for i, c in enumerate(bbs):
            if i % 5 == 0:  # Log progress every 5 characters
                logging.debug(f"Processing character {i+1}/{len(bbs)}")
            
            (x, y, w, h) = (c[0], c[1], c[2], c[3])
            roi = final_crop[y:h, x:w]
            height, width = roi.shape[0], roi.shape[1]
            if width > 15:
                if height > width:
                    blank_image = np.zeros((height, height, 3), np.uint8)
                    blank_image[:, 0:height] = (255, 255, 255)
                    x_start = int(((height - width) / 2))
                    blank_image[0:int(height), x_start:x_start + width] = roi
                else:
                    blank_image = np.zeros((width, width, 3), np.uint8)
                    blank_image[:, 0:width] = (255, 255, 255)
                    x_start = int(((width - height) / 2))
                    blank_image[x_start:x_start + height, 0:int(width)] = roi

                kernel = np.ones((3, 3), np.uint8)
                dilation = cv2.erode(blank_image, kernel, iterations=1)
                blank_image = cv2.resize(dilation, (45, 45))
                blank_image = cv2.cvtColor(blank_image, cv2.COLOR_BGR2GRAY)
                result = pc.get_class(blank_image)
                char_list.append(str(result))
            else:
                char_list.append('.')
        
        logging.debug(f"Character processing took {time.time() - char_start_time:.2f}s")
        main_list.append(char_list)
        logging.debug(f"Total time for image {idx+1}: {time.time() - start_time:.2f}s")
    
    return main_list


def convert_equation_list_to_string(main_list):
    equation_list = []
    for charset in main_list:
        equation_str = ''.join(charset).replace('.', '')
        parts = equation_str.split('=')
        if len(parts) == 2:
            left_side = parts[0]
            right_side = parts[1]
            equation = f"{left_side}={right_side}"
            equation_list.append(equation)
        else:
            logging.warning(f"Equation format issue: {equation_str}")
            equation_list.append(equation_str)  # Keep as is for debugging
    logging.debug(f"Formatted equations: {equation_list}")
    return equation_list


def get_coeff(all_equations):
    coeff_list = []
    for equation_str in all_equations:
        parts = equation_str.split('=')
        if len(parts) != 2:
            logging.error(f"Invalid equation format: {equation_str}")
            continue

        left_part = parts[0]
        right_part = parts[1]

        # Extract coefficients for X, Y, Z
        coeff_x = extract_coefficient(left_part, 'X')
        coeff_y = extract_coefficient(left_part, 'Y')
        coeff_z = extract_coefficient(left_part, 'Z')

        # Extract constant term from the left part
        constant = 0.0
        constant_matches = re.findall(r"([+-]?\d*\.?\d+)(?![XYZ])", left_part)
        for match in constant_matches:
            try:
                constant += float(match)
            except ValueError:
                pass

        # Extract intercept from the right part
        try:
            intercept = float(right_part)
        except ValueError:
            intercept = 0.0

        logging.debug(f"Equation: '{equation_str}', Coeff_X: {coeff_x}, Coeff_Y: {coeff_y}, Coeff_Z: {coeff_z}, Constant (left): {constant}, Intercept (right): {intercept}")
        coeff_list.append([coeff_x, coeff_y, coeff_z, constant, intercept])
    logging.debug(f"Extracted coefficients: {coeff_list}")
    return coeff_list


def extract_coefficient(part, variable):
    match = re.search(rf'([+-]?\d*\.?\d*){variable}', part)
    if match:
        coeff_str = match.group(1)
        if coeff_str == "" or coeff_str == "+":
            return 1.0
        elif coeff_str == "-":
            return -1.0
        else:
            try:
                return float(coeff_str)
            except ValueError:
                return 0.0
    return 0.0


def solve_1d(equation_list):
    coeff_x, constant, intercept = equation_list[0][0], equation_list[0][3], equation_list[0][4]
    if coeff_x == 0:
        raise ValueError("Invalid equation: Coefficient of X cannot be zero.")
    solution = (intercept - constant) / coeff_x
    logging.debug(f"Solved value for X: {solution}")
    return [solution]


def solve_2d(equation_list):
    A = np.array([
        equation_list[0][:2],  # Coefficients of X and Y for the first equation
        equation_list[1][:2]   # Coefficients of X and Y for the second equation
    ])
    B = np.array([
        equation_list[0][4],  # Intercept for the first equation
        equation_list[1][4]   # Intercept for the second equation
    ])
    try:
        result = np.linalg.solve(A, B)
        logging.debug(f"Solved values for X and Y: {result}")
        return result.tolist()
    except np.linalg.LinAlgError as e:
        logging.error(f"Error solving 2D equations: {e}")
        raise ValueError("The equations are parallel or invalid.")


def solve_3d(equation_list):
    A = np.array([
        equation_list[0][:3],  
        equation_list[1][:3],  
        equation_list[2][:3]   
    ])
    B = np.array([
        equation_list[0][4],  
        equation_list[1][4],  
        equation_list[2][4]   
    ])
    try:
        result = np.linalg.solve(A, B)
        logging.debug(f"Solved values for X, Y, Z: {result}")
        return result.tolist()
    except np.linalg.LinAlgError as e:
        logging.error(f"Error solving 3D equations: {e}")
        raise ValueError("The equations are parallel or invalid.")


def get_response():
    import time
    overall_start = time.time()
    
    try:
        logging.debug("Starting to process images...")
        path_list = glob.glob('img/*.png')
        logging.debug(f"Found images: {path_list}")
        
        if not path_list:
            return {"Success": False, "Error": "No images found to process"}

        # Check if processing might timeout (limit to 150 seconds to be safe)
        max_processing_time = 150
        
        logging.debug(f"Starting equation extraction at {time.time() - overall_start:.2f}s")
        eq_list = get_equtaion_list(path_list)
        
        if time.time() - overall_start > max_processing_time:
            return {"Success": False, "Error": "Processing timeout - image too complex"}
            
        logging.debug(f"Extracted equation list: {eq_list}")

        eq_str = convert_equation_list_to_string(eq_list)
        logging.debug(f"Cleaned equations: {eq_str}")

        coeff = get_coeff(eq_str)
        logging.debug(f"Extracted coefficients: {coeff}")

        if len(coeff) == 1:
            result = solve_1d(coeff)
            response = {
                "Success": True,
                "Soln_X": result[0],
                "Eqn_1": eq_str[0],
            }
        elif len(coeff) == 2:
            result = solve_2d(coeff)
            response = {
                "Success": True,
                "Soln_X": result[0],
                "Soln_Y": result[1],
                "Eqn_1": eq_str[0],
                "Eqn_2": eq_str[1],
            }
        elif len(coeff) == 3:
            result = solve_3d(coeff)
            response = {
                "Success": True,
                "Soln_X": result[0],
                "Soln_Y": result[1],
                "Soln_Z": result[2],
                "Eqn_1": eq_str[0],
                "Eqn_2": eq_str[1],
                "Eqn_3": eq_str[2],
            }
        else:
            response = {
                "Success": False,
                "Error": f"Expected 1, 2, or 3 equations, but got {len(coeff)}."
            }
    except Exception as e:
        logging.error(f"An error occurred in get_response: {e}")
        response = {
            "Success": False,
            "Error": str(e)
        }
    finally:
        return response