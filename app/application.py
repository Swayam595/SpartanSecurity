from flask import Flask, jsonify, request, render_template
from ModelException import ModelException
# from ModelManager import ModelManager
import json

application = app = Flask(__name__)
# manager = ModelManager()


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/intersection')
def intersection():
    return render_template('intersection.html')


@app.route('/hotspots')
def hot_spots():
    return render_template('hotspots.html')


@app.route('/predanalytics')
def predictive_analytics():
    return render_template('predictive_analytics.html')


@app.route('/crimesbyneighborhood')
def neighborhood_analytics():
    return render_template('neighborhood_analytics.html')


@app.route("/crimesbydistrict", methods=['GET', 'POST'])
def district_analytics():
    return render_template("district_analytics.html")


@app.route('/newsfeed')
def newsfeed():
    return render_template('newsfeed.html')


@app.route('/safety')
def safety():
    return render_template('safety.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# # api to upload data set file
# @app.route("/api/upload", methods=['POST'])
# def upload_data():
#     try:
#         file = request.files['data']
#         name = request.form['name']
#         return jsonify(manager.upload_data(name, file))
#     except Exception as ex:
#         return ModelException.to_json(ex), 500
#
#
# # api to create time series model
# @app.route("/api/generatemodel", methods=['POST'])
# def generate_model():
#     try:
#         year = request.form['year']
#         return jsonify(manager.generate_model(year))
#
#     except Exception as ex:
#         return ModelException.to_json(ex), 500


if __name__ == '__main__':
    app.run(debug=True)




