from flask import Flask, jsonify, request, render_template

from ModelException import ModelException
from ModelManager import ModelManager
from S3Repository import S3Repository

application = app = Flask(__name__)
manager = ModelManager()
repository = None


@app.route("/", methods=['GET', 'POST'])
def index():
    # return jsonify({"api": "up and running!!!"})
    return render_template("index.html")


@app.route("/api/init", methods=['GET'])
def initialize():

    try:
        repository = S3Repository()
        return jsonify({})

    except Exception as ex:
        return ModelException.to_json(ex), 500


@app.route("/api/upload", methods=['POST'])
def upload():

    try:
        file = request.files['data']
        name = request.form['name']
        return jsonify(manager.upload(name, file))

    except Exception as ex:
        return ModelException.to_json(ex), 500


@app.route("/api/getmeta", methods=['GET'])
def getMeta():

    try:
        res = manager.getMeta()
        return jsonify(res)

    except Exception as ex:
        return ModelException.to_json(ex), 500


@app.route("/api/updatemeta/<name>", methods=['POST'])
def updateMeta(name):

    try:
        res = manager.updateMeta(name, request.json)
        return jsonify(res)

    except Exception as ex:
        return ModelException.to_json(ex), 500


@app.route("/api/deletemeta/<name>", methods=['POST'])
def deleteMeta(name):

    try:
        res = manager.deleteMeta(name)
        return jsonify(res)

    except Exception as ex:
        return ModelException.to_json(ex), 500


@app.route("/api/addmodel", methods=['POST'])
def create():

    try:
        model = manager.create(request.json)
        return jsonify(model.to_json())

    except Exception as ex:
        return ModelException.to_json(ex), 500


@app.route("/api/getmodel/<modelName>", methods=['GET'])
def get(modelName):

    try:
        model = manager.get(modelName)
        return jsonify(model)

    except Exception as ex:
        return ModelException.to_json(ex), 500


@app.route("/api/updatemodel", methods=['POST'])
def update():

    try:
        model = manager.update(request.json)
        return jsonify(model.to_json())

    except Exception as ex:
        return ModelException.to_json(ex), 500


@app.route("/api/deletemodel/<modelName>", methods=['POST'])
def delete(modelName):

    try:
        model = manager.delete(modelName)
        return jsonify(model)

    except Exception as ex:
        return ModelException.to_json(ex), 500


@app.route("/api/generatemodel/<modelName>", methods=['POST'])
def generate(modelName):

    try:
        model = manager.generate(modelName)
        return jsonify(model.to_json())

    except Exception as ex:
        return ModelException.to_json(ex), 500


@app.route("/api/hibernatemodel/<modelName>", methods=['POST'])
def hibernate(modelName):

    try:
        model = manager.hibernate_model(modelName)
        if model is None:
            return jsonify({})
        else:
            return jsonify(model.to_json())

    except Exception as ex:
        return ModelException.to_json(ex), 500


@app.route("/api/activatemodel/<modelName>", methods=['POST'])
def activate(modelName):

    try:
        model = manager.activate_model(modelName)
        return jsonify(model.to_json())

    except Exception as ex:
        return ModelException.to_json(ex), 500


@app.route("/api/predict", methods=['POST'])
def predict():

    try:
        row = manager.predict(request.json)
        return jsonify(row)

    except Exception as ex:
        return ModelException.to_json(ex), 500


@app.route("/api/getallmodels", methods=['GET'])
def getAllModels():

    try:
        models = manager.getAllModels()
        return jsonify(models)

    except Exception as ex:
        return ModelException.to_json(ex), 500


if __name__ == '__main__':
    app.run(debug=True)