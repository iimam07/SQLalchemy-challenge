# import dependencies 
import datetime as dt
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
engine = create_engine("sqlite:///hawaii.sqlite")
#################################################
# reflect the database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurements = Base.classes.measurements

#################################################
# Flask Set-up
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )

# Convert the query results to a dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
   
    """Return a list of all precipitation and date"""
    results = session.query(Measurements.date,Measurements.prcp).all()

    session.close()

    
    precipiation_info=[]
    for date,prcp in results:
        precipitation_dict = {}
        precipitation_dict[date] = prcp
    precipiation_info.append(precipitation_dict)

    return jsonify(precipiation_info)

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    results = session.query(Station.id,Station.station,Station.name).all()
    session.close()

    station_info=[]
    for id,station,name in results:
        station_dict={}
        station_dict['Id']=id
        station_dict['station']=station
        station_dict['name']=name
        station_info.append(station_dict)
    return jsonify(station_info)

# Query the dates and temperature observations of the most active station for the previous year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tempartureobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all previous temparture observations"""
    results_date=session.query(Measurements.date).order_by(Measurements.date.desc()).first()
    str_date=list(np.ravel(results_date))[0]
    latest_date=dt.datetime.strptime(str_date,"%Y-%m-%d")
    year_back=latest_date-dt.timedelta(days=366)

    results=session.query(Measurements.date, Measurements.tobs).order_by(Measurements.date.desc()).\
            filter(Measurements.date>=year_back).all()
    session.close()
    
    prev_temperature=[]
    for tobs,date in results:
        tobs_dict={}
        tobs_dict['date']=date
        tobs_dict['tobs']=tobs
        prev_temperature.append(tobs_dict)
    return jsonify(prev_temperature)

## Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.
## When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than or equal to the start date.
## When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates from the start date through the end date (inclusive).

@app.route("/api/v1.0/<start>")
def calc_temps_sd(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    results=session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
                filter(Measurements.date >= start).all()
    session.close()
    
    temp_obs={}
    temp_obs["Min_Temp"]=results[0][0]
    temp_obs["avg_Temp"]=results[0][1]
    temp_obs["max_Temp"]=results[0][2]
    return jsonify(temp_obs)

@app.route("/api/v1.0/<start>/<end>")
def calc_temps(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    results=session.query(func.min(Measurements.tobs), func.avg(Measurements.tobs), func.max(Measurements.tobs)).\
                filter(Measurements.date >= start).filter(Measurements.date <= end).all()
    session.close()
    temp_obs={}
    temp_obs["Min_Temp"]=results[0][0]
    temp_obs["avg_Temp"]=results[0][1]
    temp_obs["max_Temp"]=results[0][2]
    return jsonify(temp_obs)
    
if __name__ == '__main__':
    app.run(debug=True)
