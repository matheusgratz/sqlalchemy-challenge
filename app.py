import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

# /
# Home page.
# List all routes that are available.
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        """Available Routes:
        
        /api/v1.0/precipitation
        Convert the query results to a dictionary using date as the key and prcp as the value.
        Return the JSON representation of your dictionary.
        
        /api/v1.0/stations
        Return a JSON list of stations from the dataset.
        
        /api/v1.0/tobs
        Return a JSON list of temperature observations (TOBS) for the previous year.
        
        /api/v1.0/start_date
        /api/v1.0/start_date/end_date
        Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
        When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
        When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
        """
    )
    
# /api/v1.0/precipitation
# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """
    Convert the query results to a dictionary using date as the key and prcp as the value.
    Return the JSON representation of your dictionary
    """
    # Query
    results = session.query(Measurement.date, Measurement.prcp).limit(100).all()

    session.close()

    date_prcp = []
    for date, prcp in results:
        precipitation_dict = {}
        precipitation_dict["date"] = date
        precipitation_dict["prcp"] = prcp
        date_prcp.append(precipitation_dict)
    
    return jsonify(date_prcp)


# /api/v1.0/stations
# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """
    Return a JSON list of stations from the dataset.
    """
    # Query
    results = session.query(Measurement.station, Station.name).\
                            group_by(Station.name).\
                            filter(Measurement.station == Station.station).\
                            all()

    session.close()

    all_stations = []
    for station, name in results:
        stations_dict = {}
        stations_dict["station"] = station
        stations_dict["name"] = name
        all_stations.append(stations_dict)
    
    return jsonify(all_stations)

# /api/v1.0/tobs
# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """
    Return a JSON list of stations from the dataset.
    """
    #one year ago
    import datetime as dt
    datepoint = session.query(func.max(Measurement.date)).\
                select_from(Measurement).\
                order_by(Measurement.date).all()
                
    datepoint = datepoint[0][0]
    last_datepoint = dt.datetime.strptime(datepoint, '%Y-%m-%d').date()
    one_year_ago = last_datepoint.replace(year=last_datepoint.year-1)
    
    # Query
    results = session.query(Station.name, Measurement.date, Measurement.tobs
                            ).filter(Measurement.date >= one_year_ago
                            ).filter(Measurement.station == Station.station
                            ).all()

    session.close()

    list_tobs = []
    for name, date, tobs in results:
        tobs_dict = {}
        tobs_dict["name"] = name
        tobs_dict["date"] = date
        tobs_dict["tobs"] = tobs
        list_tobs.append(tobs_dict)
    
    return jsonify(list_tobs)

# /api/v1.0/<start> and /api/v1.0/<start>/<end>
# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
# When given the start only (format YYYY-MM-DD), calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
# When given the start (format YYYY-MM-DD) and the end date (format YYYY-MM-DD), calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start_date>")
def minavgmax_start(start_date):

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    When given the start only (format YYYY-MM-DD), calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""
    
    
    std = start_date.split("-")
    canonicalized = dt.date(int(std[0]), int(std[1]), int(std[2]))   
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(Measurement.date,\
        func.min(Measurement.tobs),\
        func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).\
            filter(Measurement.date >= canonicalized).\
            group_by(Measurement.date).all()
        
    session.close()

    start_temps = []
    
    for date, t_min, t_avg, t_max in results:
        start_temps_dict = {}
        start_temps_dict["date"] = date
        start_temps_dict["min"] = t_min
        start_temps_dict["avg"] = t_avg
        start_temps_dict["max"] = t_max
        start_temps.append(start_temps_dict)
    
    return jsonify(start_temps) 


@app.route("/api/v1.0/<start_date>/<end_date>")
def minavgmax_start_end(start_date, end_date):

    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    When given the start (format YYYY-MM-DD) and the end date (format YYYY-MM-DD), calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""
    
    
    std = start_date.split("-")
    etd = end_date.split("-")
    
    canonicalized_start = dt.date(int(std[0]), int(std[1]), int(std[2]))   
    canonicalized_end = dt.date(int(etd[0]), int(etd[1]), int(etd[2]))   
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    results = session.query(Measurement.date,\
        func.min(Measurement.tobs),\
        func.avg(Measurement.tobs),\
        func.max(Measurement.tobs)).\
            filter(Measurement.date >= canonicalized_start).\
            filter(Measurement.date <= canonicalized_end).\
            group_by(Measurement.date).all()
        
    session.close()

    start_end_temps = []
    
    for date, t_min, t_avg, t_max in results:
        start_temps_dict = {}
        start_temps_dict["date"] = date
        start_temps_dict["min"] = t_min
        start_temps_dict["avg"] = t_avg
        start_temps_dict["max"] = t_max
        start_end_temps.append(start_temps_dict)
    
    return jsonify(start_end_temps) 


if __name__ == '__main__':
    app.run(debug=True)