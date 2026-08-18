# Air Quality Detection and Anomaly Detection System

This repository contains the source code for the **Air Quality Detection and Anomaly Detection System**, developed as a minor project for the Bachelor of Engineering (BE) program (Year III / Part II).

## Project Team
- **Abhishek Tharu**
- **Avinash Kumar Yadav**

## Overview
This system collects real-time air quality data for the Kathmandu Valley (27.72°N, 85.32°E) using the OpenWeatherMap Air Pollution API. It leverages Machine Learning models to not only present the current air quality metrics but also predict the Air Quality Index (AQI) and detect anomalous pollution readings.

The project features a clean, responsive, and professional dashboard interface where users can monitor live data, track historical trends, and view AI-driven insights.

## Key Features
- **Live AQI Monitoring:** View current pollutant concentrations (PM2.5, PM10, CO, NO₂, O₃, SO₂) and AQI levels with health recommendations.
- **AQI Prediction:** Uses a pre-trained **Random Forest Regressor** to predict the AQI based on current pollutant levels and temporal features (hour, day).
- **Anomaly Detection:** Employs an **Isolation Forest** model to flag unusual or abnormal air quality readings that deviate from typical patterns.
- **Historical Trends:** Interactive line charts (powered by Chart.js) visualizing AQI and PM2.5 trends over time.
- **Automated Data Collection:** Scheduled tasks via APScheduler to periodically fetch and store new readings into the local database.

## Technologies Used
- **Backend Framework:** Django (Python)
- **Database:** SQLite
- **Machine Learning:** scikit-learn, joblib
- **Data Processing & EDA:** Pandas, NumPy, Matplotlib
- **Frontend:** HTML5, CSS3, JavaScript (Chart.js)
- **Data Source:** OpenWeatherMap API

## Setup and Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd "Air Quality Prediction"
   ```

2. **Set up a virtual environment (recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install django scikit-learn pandas numpy requests apscheduler
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

## OpenWeatherMap AQI Scale Reference
- **1 (Good):** Air quality is good
- **2 (Fair):** Air quality is acceptable
- **3 (Moderate):** Some pollution is present
- **4 (Poor):** Air quality is unhealthy
- **5 (Very Poor):** Air quality is very unhealthy

## Academic Context
This is a minor project submitted in partial fulfillment of the requirements for the Degree of Bachelor of Engineering (BE) Year III / Part II.
