import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Flask Setup
app = Flask(__name__)

# Flask Routes

#####################################################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/temperature<br/>"
        f"/api/v1.0/temperature/start-date/YYYY-MM-DD<br/>"
        f"/api/v1.0/temperature/start-date/YYYY-MM-DD/end-date/YYYY-MM-DD"
    )

#####################################################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and prcp
    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    
    precipitation_dict = dict()

    for date, prcp in results:
        precipitation_dict[date] = prcp

    # Return the JSON representation of your dictionary.
    return jsonify(precipitation_dict)

#####################################################################################

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all stations
    results = session.query(Station.station).distinct().all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    # Return a JSON list of stations from the dataset
    return jsonify(all_stations)

#####################################################################################

@app.route("/api/v1.0/temperature")
def temperature():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data.
    latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    latest_date_converted = dt.datetime.strptime(latest_date[0], "%Y-%m-%d")

    one_year_ago = latest_date_converted - dt.timedelta(days=366)

    count_per_station = session.query(Station.station, Station.name, func.count(Measurement.station)).\
                            filter(Station.station == Measurement.station).\
                            group_by(Station.station, Station.name).\
                            order_by(func.count(Measurement.station).desc()).all()

    highest_station = count_per_station[0][0]

    highest_station_temp = session.query(Measurement.tobs).\
                            filter(Measurement.station == highest_station).\
                            filter(Measurement.date >= one_year_ago).all()

    session.close()

    highest_station_temp_list = list(np.ravel(highest_station_temp))

    # Return a JSON list of temperature observations (TOBS) for the previous year
    return jsonify(highest_station_temp_list)

#####################################################################################

@app.route("/api/v1.0/temperature/start-date/<start>")
def temp_by_startdate(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

    session.close()

    temp_list = list(np.ravel(results))

    return jsonify(temp_list)
#####################################################################################

@app.route("/api/v1.0/temperature/start-date/<start>/end-date/<end>")
def temp_by_startend(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    session.close()

    temp_list = list(np.ravel(results))

    return jsonify(temp_list)


if __name__ == '__main__':
    app.run(debug=True)