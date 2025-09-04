# Handwritten Linear Equation Solver (CNN)

Simple web app that recognizes handwritten linear equations (1, 2 or 3 variables) from a canvas or uploaded image, parses coefficients, and solves them using a trained CNN model.

---

## Prerequisites
- Recommended: Conda (Miniconda / Anaconda) or Python 3.8+
- Git (for repo)
- On Windows: use the Anaconda Prompt or PowerShell with conda available

Note: TensorFlow versions can be platform-sensitive. If you have GPU/Windows compatibility concerns, consider installing TensorFlow via pip.

---

## Setup (Conda, recommended)

1. Open terminal (Windows: Anaconda Prompt / PowerShell)
2. From the repo root (where `environment.yaml` is located) run:

   conda env create -f environment.yaml
   conda activate linearEqn

3. Verify dependencies installed, then run the app:

   python app.py

4. Open browser: http://127.0.0.1:5000/ (1-variable solver)
   - `/2` → 2-variable solver
   - `/3` → 3-variable solver

---

## Alternative setup (pip + venv)

1. Create and activate venv (Windows):

   python -m venv venv
   venv\Scripts\activate

2. Install packages (example):

   pip install tensorflow==2.5 numpy opencv-python flask pillow h5py scikit-image scikit-learn matplotlib imageio keras-preprocessing tqdm requests

3. Run:

   python app.py

---

## Required files before running
- `model/17class.h5` must exist. The app loads this file in `validate.py`.
- `templates/` and `static/` folders must be present (they are used by Flask `render_template`).

---

## How to use (quick)
1. Open the web UI: http://127.0.0.1:5000/
2. Draw the equation on the canvas or upload an image.
3. Click "Calculate" — the frontend sends base64 image(s) to `/upload1`, `/upload2`, or `/upload3`.
4. Backend saves images to `./img/` and runs `get_response()` to:
   - detect character bounding boxes (bb.py),
   - crop/preprocess symbols,
   - call `Predict.get_class()` (validate.py) to classify characters,
   - reconstruct equation string(s) and parse coefficients (main.py),
   - solve and return JSON with `Success`, `Eqn_#`, and `Soln_*` keys.

Returned JSON example (1-variable):
{
  "Success": true,
  "Soln_X": 0.3333333333,
  "Eqn_1": "3X+2=3"
}
---


