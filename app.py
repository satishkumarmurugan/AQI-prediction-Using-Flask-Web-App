from flask import Flask, request, jsonify, render_template
import joblib
import requests

app = Flask(__name__)

# Load your trained model
model = joblib.load('airquality.joblib')

# OpenWeather API Key
API_KEY = 'Enter Your API Key'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/heatmap')
def heatmap():
    return render_template('heatmap.html')

@app.route('/predict_manually', methods=['POST','GET'])
def predict_manually():
    if request.method == 'POST':
        # Extract data from form
        pm25 = float(request.form['PM2.5'])
        pm10 = float(request.form['PM10'])
        o3 = float(request.form['O3'])
        no2 = float(request.form['NO2'])
        co = float(request.form['CO'])
        so2 = float(request.form['SO2'])

        # Prepare data for prediction
        sample = [[pm25, pm10, o3, no2, co, so2]]
        prediction = model.predict(sample)[0]

        # Determine Air Quality Index based on prediction
        result, conclusion = determine_air_quality(prediction)

        # Return the result to the user
        return render_template('results.html', prediction=prediction, result=result, conclusion=conclusion)
    else:
        return render_template('index.html')
@app.route('/predict_automatically', methods=['GET', 'POST'])
def predict_automatically():
    if request.method == 'POST':
        city_name = request.form.get('city_name')
        if not city_name:
            error_message = "Missing city name parameter"
            error_code = 400
            return render_template('error.html', error=error_message ,error_code=error_code), 400

        # Geocoding API to get lat and lon from city name
        geocode_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&limit=1&appid={API_KEY}"
        geocode_response = requests.get(geocode_url)
        if geocode_response.status_code != 200:
            error_message = "Failed to fetch location data"
            error_code = 500
            return render_template('error.html', error=error_message ,error_code=error_code), 500
        
        geocode_data = geocode_response.json()
        if not geocode_data:
            error_message = "City not found"
            error_code = 404
            return render_template('error.html', error=error_message ,error_code=error_code), 404


        # Assuming the first result is the most relevant
        lat = geocode_data[0]['lat']
        lon = geocode_data[0]['lon']

        # Now use lat and lon to get air pollution data
        air_quality_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
        air_quality_response = requests.get(air_quality_url)
        if air_quality_response.status_code != 200:
            error_message = "Failed to fetch Air Quality Index data"
            error_code = 500
            return render_template('error.html', error=error_message ,error_code=error_code), 500


        air_quality_data = air_quality_response.json()['list'][0]['components']
        sample = [
            [air_quality_data['pm2_5'], air_quality_data['pm10'], air_quality_data['o3'],
             air_quality_data['no2'], air_quality_data['co'], air_quality_data['so2']]
        ]
        prediction = round(model.predict(sample)[0],2)

        result, conclusion = determine_air_quality(prediction)

        return render_template('results.html', prediction=prediction, result=result, conclusion=conclusion)

    else:
        return render_template('city.html')

def determine_air_quality(prediction):
    if prediction < 50:
        return 'Air Quality Index is Good', 'The Air Quality Index is excellent. It poses little or no risk to human health.'
    elif 51 <= prediction < 100:
        return 'Air Quality Index is Satisfactory', 'The Air Quality Index is satisfactory, but there may be a risk for sensitive individuals.'
    elif 101 <= prediction < 200:
        return 'Air Quality Index is Moderately Polluted', 'Moderate health risk for sensitive individuals.'
    elif 201 <= prediction < 300:
        return 'Air Quality Index is Poor', 'Health warnings of emergency conditions.'
    elif 301 <= prediction < 400:
        return 'Air Quality Index is Very Poor', 'Health alert: everyone may experience more serious health effects.'
    else:
        return 'Air Quality Index is Severe', 'Health warnings of emergency conditions. The entire population is more likely to be affected.'

if __name__ == '__main__':
    app.run(debug=True)
