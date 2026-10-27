
# Hadoop-Based Web Server Log File Analysis

## Overview
This project analyzes web server access logs using Apache Hadoop MapReduce and displays HTTP status-code statistics through a Flask web dashboard.

## Technologies
- Java
- Apache Hadoop 3.4.2
- HDFS
- YARN
- Python and Flask
- HTML and CSS
- JavaScript and Chart.js

## Features
- Stores log files in HDFS
- Extracts HTTP status codes using a Java Mapper
- Aggregates status-code counts using a Reducer
- Displays summary cards and a status-code table
- Visualizes counts and percentages using charts

## Run the Web Dashboard
Activate the Python environment:

    source venv/bin/activate

Start the dashboard:

    python app.py

Open http://localhost:5000 in your browser.

## Expected Sample Results
- HTTP 200: 3 requests
- HTTP 404: 2 requests
- HTTP 500: 1 request
