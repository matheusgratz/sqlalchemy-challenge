import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
start_date = '2017-01-01'
std = start_date.split("-")
canonicalized = dt.date(int(std[0]), int(std[1]), int(std[2]))   
    
    # Create our session (link) from Python to the DB
session = Session(engine)
    
results = session.query(Measurement.date,\
    func.min(Measurement.tobs),\
    func.avg(Measurement.tobs),\
    func.max(Measurement.tobs)).\
        filter(Measurement.date > canonicalized).\
        group_by(Measurement.date).all()

        
session.close()

    # start_temps = []
    
    # for date, t_min, t_avg, t_max in results:
    #     start_temps_dict = {}
    #     start_temps_dict["date"] = date
    #     start_temps_dict["min"] = t_min
    #     start_temps_dict["avg"] = t_avg
    #     start_temps_dict["max"] = t_max
    #     start_temps.append(start_temps_dict)
    
print(results)
