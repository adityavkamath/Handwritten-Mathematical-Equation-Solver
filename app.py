from flask import Flask, render_template, request, jsonify
import base64
from main import get_response
import os
import glob

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index_1.html')  # Default to 1-degree solver

@app.route('/2')
def index2():
    return render_template('index.html')  # 2-degree solver

@app.route('/3')
def index3():
    return render_template('index_3.html')  # 3-degree solver

@app.route('/upload1', methods=['POST'])
def upload1():
    data = request.get_json()
    Image1 = data['Image1']

    delete_all()
    with open("./img/Image1.png", "wb") as fh:
        ImageBin = base64.b64decode(Image1)
        fh.write(ImageBin)
        fh.close()

    response = get_response()
    return jsonify(response)

@app.route('/upload2', methods=['POST'])
def upload2():
    data = request.get_json()
    Image1 = data['Image1']
    Image2 = data['Image2']

    delete_all()
    with open("./img/Image1.png", "wb") as fh:
        ImageBin = base64.b64decode(Image1)
        fh.write(ImageBin)
        fh.close()

    with open("./img/Image2.png", "wb") as fh:
        fh.write(base64.b64decode(Image2))
        fh.close()

    response = get_response()
    return jsonify(response)

@app.route('/upload3', methods=['POST'])
def upload3():
    data = request.get_json()
    Image1 = data['Image1']
    Image2 = data['Image2']
    Image3 = data['Image3']

    delete_all()
    with open("./img/Image1.png", "wb") as fh:
        ImageBin = base64.b64decode(Image1)
        fh.write(ImageBin)
        fh.close()

    with open("./img/Image2.png", "wb") as fh:
        fh.write(base64.b64decode(Image2))
        fh.close()

    with open("./img/Image3.png", "wb") as fh:
        fh.write(base64.b64decode(Image3))
        fh.close()

    response = get_response()
    return jsonify(response)

def delete_all():
    files = glob.glob('./img/*.png')
    for f in files:
        os.remove(f)

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)