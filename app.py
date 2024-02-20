from flask import Flask, render_template, request, jsonify
import pandas as pd
import joblib

app = Flask(__name__)

# Load your trained model
model = joblib.load('airquality.joblib')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Get the input data from the HTML form
        pm25 = float(request.form['PM2.5'])
        pm10 = float(request.form['PM10'])
        o3 = float(request.form['O3'])
        no2 = float(request.form['NO2'])
        co = float(request.form['CO'])
        so2 = float(request.form['SO2'])

        # Create a sample data array for prediction
        sample = [[pm25, pm10, o3, no2, co, so2]]

        # Make predictions using the loaded model
        prediction = model.predict(sample)
        print(f'Prediction: {prediction}')

        if prediction < 50:
            result = 'Air Quality is Good'
            conclusion = 'The air quality is excellent. It poses little or no risk to human health.'
        elif 51 <= prediction < 100:
            result = 'Air Quality is Satisfactory'
            conclusion = 'The air quality is satisfactory, but there may be a slight risk for some individuals who are unusually sensitive to air pollution.'
        elif 101 <= prediction < 200:
            result = 'Air Quality is Moderately Polluted'
            conclusion = 'The air quality is moderately polluted. People with respiratory or heart conditions may experience health effects. The general public is not likely to be affected.'
        elif 201 <= prediction < 300:
            result = 'Air Quality is Poor'
            conclusion = 'The air quality is poor and may cause health effects to everyone. People with respiratory or heart conditions may experience more serious health effects.'
        elif 301 <= prediction < 400:
            result = 'Air Quality is Very Poor'
            conclusion = 'The air quality is very poor, and it may have a severe impact on health. The entire population is likely to be affected.'
        else:
            result = 'Air Quality is Severe'
            conclusion = 'The air quality is severe, posing a serious health risk to everyone. The situation requires immediate attention and action to protect public health.'
            

        # You can return the prediction to the user
        return render_template('results.html', prediction=prediction,result=result,conclusion=conclusion)

if __name__ == '__main__':
    app.run(debug=True)
