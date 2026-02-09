# Bike-sharing systems

## Motivation
City bike-sharing systems generate large amounts of data daily, including trips, station usage, maintenance, and user activity. Managing such systems requires tracking bikes, analyzing demand, scheduling maintenance, and generating reports for stakeholders.

## Project Overview
This project implements a complete backend for a fictional city bike-sharing system. It integrates:
- Modular, multi-file Python code
- Object-oriented design (Bike, Station, Entity, etc.)
- Algorithms for sorting and searching
- Data analysis with Pandas and NumPy
- Visualization with Matplotlib
- Pricing strategies via Strategy Pattern
- Factory Pattern for object creation
- Version control with Git/GitHub

## Structure
citybike/
│
├─ main.py # Entry point
├─ models.py # OOP classes
├─ analyzer.py # Analysis methods
├─ algorithms.py # Sorting/searching
├─ numerical.py # NumPy computations
├─ visualization.py # Charts
├─ pricing.py # Pricing strategies
├─ factories.py # Object creation
├─ utils.py # Helpers
├─ data/
│ ├─ trips.csv
│ ├─ stations.csv
│ ├─ maintenance.csv
│ ├─ trips_clean.csv
│ └─ stations_clean.csv
├─ output/
│ ├─ summary_report.txt
│ ├─ top_stations.csv
│ ├─ top_users.csv
│ └─ figures/ # PNG visualizations
└─ README.md

## Getting Started
1. Clone the repo:
git clone <repository_url>
cd citybike
Install dependencies:

pip install pandas numpy matplotlib
Generate datasets (if not provided):

python data/generate_data.py
Run main script:

python main.py