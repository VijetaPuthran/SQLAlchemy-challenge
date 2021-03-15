import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite",connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
# View all of the classes that automap found
Base.classes.keys()
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

# Find the most recent date in the data set.
recent_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

# Design a query to retrieve the last 12 months of precipitation data and plot the results. 
# Starting from the most recent data point in the database. 
# Calculate the date one year from the last date in data set.
from datetime import date
from dateutil.relativedelta import relativedelta
date_oneyear_from_lastdate = date(2017,8,23)+relativedelta(years=-1)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return (f"Welcome to Hawaii's Climate API<br/>"
            f"------------------------------------------------<br/>"
            f"Available Routes:<br/>"
            f"<br/>"
            f'<a href="/api/v1.0/precipitaton">/api/v1.0/precipitaton</a> : A list of precipitation data.<br/>'
            f"<br/>"
            f'<a href="/api/v1.0/stations">/api/v1.0/stations</a> : A list of all the stations.<br/>'
            f"<br/>"
            f'<a href="/api/v1.0/tobs">/api/v1.0/temperature</a> : A list of temperature observation for the previous year.<br/>'
            f"<br/>"
            f'<a href="/api/v1.0/<start>">/api/v1.0/<start></a> : A list of the minimum temperature, the average temperature, and the maximum temperature for a given start date.<br/>'
            f"<br/>"
            f'<a href="/api/v1.0/<start>/<end>">/api/v1.0/<start>/<end></a> : A list of the minimum temperature, the average temperature, and the maximum temperature for a given start-end date range.<br/>'
            f"<br/>"
            f"------------------------------------------------<br/>")
   #           f"~~~ datesearch (yyyy-mm-dd)<br/>"
   #         f"/api/v1.0/datesearch/2015-05-30  ~~~~~~~~~~~ low, high, and average temp for date given and each date after<br/>"
   #         f"/api/v1.0/datesearch/2015-05-30/2016-01-30 ~~ low, high, and average temp for date given and each date up to and including end date<br/>"
   #         f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~<br/>"
   #         f"~ data available from 2010-01-01 to 2017-08-23 ~<br/>"
   #         f"~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

@app.route("/api/v1.0/precipitaton")
def precipitation():
    
    results = session.query(Measurement.date, Measurement.prcp, Measurement.station).\
              filter(Measurement.date > date_oneyear_from_lastdate).\
              order_by(Measurement.date).\
              all()
    
    precipitation_data = []
    for result in results:
        precipitaion_dict = {result.date: result.prcp, "Station": result.station}
        precipitation_data.append(precipitaion_dict)

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    results = session.query(Station.name).all()
    total_stations = list(np.ravel(results))
    return jsonify(total_stations)


@app.route("/api/v1.0/tobs")
def temperature():

    results = session.query(Measurement.date, Measurement.tobs, Measurement.station).\
              filter(Measurement.date > date_oneyear_from_lastdate).\
              order_by(Measurement.date).\
              all()

    temp_data = []
    for result in results:
        temp_dict = {result.date: result.tobs, "Station": result.station}
        temp_data.append(temp_dict)

    return jsonify(temp_data)

@app.route('/api/v1.0/<start>')
def start_date(start):
    select = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  session.query(*select).\
               filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
               group_by(Measurement.date).\
               all()

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

@app.route('/api/v1.0/<start>/<end>')
def startEnd(start, end):
    select = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  session.query(*select).\
               filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).\
               filter(func.strftime("%Y-%m-%d", Measurement.date) <= end).\
               group_by(Measurement.date).\
               all()

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Date"] = result[0]
        date_dict["Low Temp"] = result[1]
        date_dict["Avg Temp"] = result[2]
        date_dict["High Temp"] = result[3]
        dates.append(date_dict)
    return jsonify(dates)

if __name__ == "__main__":
    app.run(debug=True)