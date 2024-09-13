from flask import Flask, jsonify, request  # import flask, jsonify, request for handling API requests
from flask_cors import CORS  
from prophet import Prophet  # prophet for time series forecasting
import pandas as pd  # import pandas for data manipulation
from dataGenerator import generate_synthetic_data


app = Flask(__name__)  # initialize flask web app
CORS(app)  # enable cors for all routes


# this endpoint generates synthetic transaction data for a given date range
@app.route('/api/transactions', methods=['GET'])
def get_synthetic_transactions():
    # generate synthetic data starting from january 1, 2022, to september 10, 2024
    synthetic_data = generate_synthetic_data(pd.Timestamp('2022-01-01'), pd.Timestamp('2024-09-10'))

    # date column must be correctly formatted as a datetime object
    synthetic_data['date'] = pd.to_datetime(synthetic_data['date'])
    # print(synthetic_data.groupby([synthetic_data['date'].dt.year, synthetic_data['date'].dt.month])['amount'].sum())
    
    # return the generated synthetic data in JSON format with an array structure
    return jsonify(synthetic_data.to_dict(orient="records"))  

# to accept real transaction data and return forecast
@app.route('/api/forecast', methods=['POST'])  
def forecast_with_real_data():

    # transaction data from frontend
    data = request.json

    # convert transaction data to a pandas dataframe for processing
    transactions = pd.DataFrame(data['transactions'])
    

    # rename columns to match prophet's expected input format!!!
    transactions.rename(columns={'date': 'ds', 'amount': 'y'}, inplace=True)
    transactions['ds'] = pd.to_datetime(transactions['ds'])

    # scale the amounts to increase predicted values
    #transactions['y'] = transactions['y'] * 1.2 
 

    # initialize the prophet model
    model = Prophet()

   # weekly seasonality
    model.add_seasonality(name='weekly', period=7, fourier_order=5)

    # monthly seasonality (captures patterns over the course of a month)
    model.add_seasonality(name='monthly', period=30.5, fourier_order=10)

    # yearly seasonality (to account for year-to-year fluctuations like holidays)
    model.add_seasonality(name='yearly', period=365.25, fourier_order=10)

    # custom seasonality for holidays and shopping spikes (ex holiday season in dec)
    model.add_seasonality(name='holiday_spending', period=12, fourier_order=15)

    # fit the model to the real transaction data
    model.fit(transactions[['ds', 'y']])

    # generate future dates from september 2024 to jan 2026 (17 months) for forecasting
    future = model.make_future_dataframe(periods=17, freq='ME')  
    print(future)  #verify the dates

    # make predictions for future dates based on historical data
    forecast = model.predict(future)

    #log predictions to see whats going wrong
    # to fix: numbers are abnormally small 
    print(forecast[['ds', 'yhat']])
    print(forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail())  # last few predictions


    # extract only the relevant columns (date and predicted values)
    predictions = forecast[['ds', 'yhat']]



    # convert predictions to match the transaction structure expected by the frontend
    prediction_data = []
    for idx, row in predictions.iterrows():
        prediction_data.append({
            'transactionId': idx + 10000,  # mock transaction id
            'userId': 1,  
            'accountId': 1,  
            'vendorName': "Predicted",  # label predictions as 'predicted'
            'amount': round(row['yhat'], 2),  # round predicted amount to two decimal places
            'description': "Predicted spending",  
            'category': "Misc",  # random category
            'date': row['ds'].strftime('%Y-%m-%d')  # format date as 'yyyy-mm-dd'
        })

    # split predictions into two separate arrays: 2024, 2025
    predictions_2024 = [pred for pred in prediction_data if '2024' in pred['date']]
    predictions_2025 = [pred for pred in prediction_data if '2025' in pred['date']]

   # return the predictions as a json response
    return jsonify({
        'predictions_2024': predictions_2024,
        'predictions_2025': predictions_2025
    })


if __name__ == '__main__':
    app.run(port=5000)  # run app on port 5000



# type this in terminal to run: python prophetService.py