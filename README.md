# Air Quality Prediction, Detection and Anomaly Detection System

This repository contains the source code for the **Air Quality Prediction, Detection and Anomaly Detection System**, developed as a minor project for the Bachelor of Engineering (BE) program (Year III / Part II).

## Project Team
- **Abhishek Tharu**
- **Avinash Kumar Yadav**

## Overview
This system collects real-time air quality data for the Kathmandu Valley (27.72°N, 85.32°E) using the OpenWeatherMap Air Pollution API. It leverages Machine Learning models to not only present the current air quality metrics but also predict the Air Quality Index (AQI) and detect anomalous pollution readings.

The AQI is calculated using the **U.S. EPA breakpoint interpolation method**, producing values on the standard **0-500 scale**. The API provides raw pollutant concentrations in μg/m³, which are converted to the appropriate EPA units (ppm for CO, ppb for NO₂, O₃, SO₂) before applying the breakpoint tables.

The project features a clean, responsive, and professional dashboard interface where users can monitor live data, track historical trends, and view AI-driven insights.

## Key Features
- **Live AQI Monitoring:** View current pollutant concentrations (PM2.5, PM10, CO, NO₂, O₃, SO₂) and AQI levels with health recommendations.
- **AQI Prediction:** Uses a pre-trained **Random Forest Regressor** to predict the AQI based on current pollutant levels and temporal features (hour, day).
- **Custom Date/Time Forecast:** Select any future date and time to predict what the AQI might be, with detailed health recommendations and activity suggestions.
- **Anomaly Detection:** Employs an **Isolation Forest** model to flag unusual or abnormal air quality readings that deviates from typical patterns.
- **Email Alerts:** Automated email notifications (via Gmail SMTP) when anomalous readings are detected.
- **Historical Trends:** Interactive line charts (powered by Chart.js) visualizing AQI and PM2.5 trends over time with time range filters (24h, 7d, 30d).
- **Automated Data Collection:** Scheduled tasks via APScheduler to periodically fetch and store new readings into the local database.

## Technologies Used
- **Backend Framework:** Django (Python)
- **Database:** SQLite
- **Machine Learning:** scikit-learn, joblib
- **Data Processing & EDA:** Pandas, NumPy, Matplotlib
- **Frontend:** HTML5, CSS3, JavaScript (Chart.js)
- **Data Source:** OpenWeatherMap API
- **Email Service:** Gmail SMTP

## AQI Scale Reference (U.S. EPA)
| AQI Range | Category | Health Implications |
|-----------|----------|-------------------|
| 0-50 | Good | Air quality is satisfactory, little or no risk |
| 51-100 | Moderate | Acceptable; sensitive individuals may be affected |
| 101-150 | Unhealthy for Sensitive Groups | Sensitive groups may experience health effects |
| 151-200 | Unhealthy | Everyone may begin to experience health effects |
| 201-300 | Very Unhealthy | Health alert: everyone may experience serious effects |
| 301-500 | Hazardous | Health emergency for the entire population |

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/ProgAbhishek/aqi-prediction-system.git
   cd "Air Quality Prediction"
   ```

2. **Set up a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install django scikit-learn pandas numpy requests apscheduler joblib matplotlib
   ```

4. **Run Database Migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start the Development Server:**
   ```bash
   python manage.py runserver
   ```
   The dashboard will be available at `http://127.0.0.1:8000/`.

## Project Structure
```
Air Quality Prediction/
├── aqi_calculation/       # EPA breakpoint interpolation calculator
├── aqi_dashboard/         # Django project settings
├── dashboard/             # Main app with views, ML services, and utilities
├── data/                  # Processed air quality CSV data
├── data_collection/       # API data fetching and scheduling
├── database/              # SQLite database utilities
├── ML/                    # Model training notebooks and saved models
├── preprocessing/         # Data preprocessing and EDA notebooks
├── static/                # CSS, JS, and static assets
├── templates/             # Django HTML templates
└── tests/                 # Unit tests for AQI calculator
```

## Academic Context
This is a minor project submitted in partial fulfillment of the requirements for the Degree of Bachelor of Engineering (BE) Year III / Part II.
