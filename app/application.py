from flask import Flask, jsonify, request, render_template
from ModelException import ModelException
from ModelManager import ModelManager
import json

application = app = Flask(__name__)
manager = ModelManager()


@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template("index.html")


@app.route("/byneighborhood", methods=['GET', 'POST'])
def crimesbyneighborhood():
    return render_template("neighborhood.html")


# api to upload data set file
@app.route("/api/upload", methods=['POST'])
def upload_data():
    try:
        file = request.files['data']
        name = request.form['name']
        return jsonify(manager.upload_data(name, file))
    except Exception as ex:
        return ModelException.to_json(ex), 500


# api to create time series model
@app.route("/api/generatemodel", methods=['POST'])
def generate_model():
    try:
        year = request.form['year']
        return jsonify(manager.generate_model(year))

    except Exception as ex:
        return ModelException.to_json(ex), 500


if __name__ == '__main__':
    app.run(debug=True)




