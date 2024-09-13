# Budget Buddy Spending Prediction Service

## Overview
This is a Python-based service that leverages the Prophet library to predicts future spending trends for Budget Buddy.
The service processes transaction data to generate accurate forecasts.

## Disclaimer
This service is a **work in progress**. Certain features may not work as expected. 

## To start the Flask server

   ```bash
   python prophetService.py
   ```

## Technologies

This service was built using the following technologies:

- **Prophet**: A time series forecasting library used to predict future spending based on transaction data.
- **Flask**: A web framework for building the API routes and handling requests.
- **pandas**: A data manipulation library, used to handle transaction data and prepare it for the Prophet model.
- **Faker**: A library for generating fake data, which is used to create synthetic transactions for testing purposes.


## Usage
The service accepts transaction data via API requests and returns spending forecasts. It can be integrated with other Budget Buddy microservices and supports synthetic data generation for testing.

## How It Works
This service uses the `Prophet` library to predict future spending trends. Here's the basic flow:

1. **Data Collection**: The service accepts real transaction data or generates synthetic data.
2. **Modeling**: The Prophet model is trained on historical transaction data.
3. **Forecasting**: The model predicts future spending for up to 16 months, providing insights into users' financial habits.

