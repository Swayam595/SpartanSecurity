from flask import Flask, jsonify, request, render_template
application = app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/intersection')
def intersection():
    return render_template('intersection.html')


@app.route('/predanalytics')
def predictive_analytics():
    return render_template('predictive_analytics.html')


@app.route('/predwithcensus')
def predictive_census():
    return render_template('predictive_with_census.html')


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


if __name__ == '__main__':
    app.run(debug=True)




