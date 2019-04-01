
# Import dependencies
import pandas as pd
import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy import create_engine, func
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from flask import Flask, jsonify

from flask import Flask, jsonify

# Set up Flask
app = Flask(__name__)

# Create the connection engine to the sqlite database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Establish Base for which classes will be constructed 
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(engine, reflect=True)

# Assign the stations class to a variable called `Station`
Station = Base.classes.station

# Assign the measurements class to a variable called `Measurement`
Measurement = Base.classes.measurement

# To query the server we use a Session object
session = Session(bind=engine)

# Calulate the date 1 year from max date
max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
end_date = max_date[0]
start_date = dt.datetime.strptime(end_date, "%Y-%m-%d") - dt.timedelta(days=365)

@app.route("/")
def Homepage():
    return (
        f"Welcome to my Climate API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation --Precipitation Data For Previous Year<br/>"
        f"/api/v1.0/stations --Station List<br/>"
        f"/api/v1.0/tobs --Temperature Data for Previous Year<br/>"
        f"/api/v1.0/[start date: yyyy-mm-dd] --Choose Start Date for Avg/Min/Max Temps for Start Date through Today<br>/" 
        f"/api/v1.0/[start date: yyyy-mm-dd]/[end date: yyyy-mm-dd] --Choose Start and End Date for Avg/Min/Max Temps for give Range"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(bind=engine)    
    # query to retrieve date and precipitation data    
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
     filter(Measurement.date >= start_date, Measurement.prcp != None).all()
    
    # Convert object to a dictionary
    prcp_dict={}
    for item in prcp_data:
        prcp_dict[item[0]]=item[1]
    
    # Return jsonified list
    return (jsonify(prcp_dict))

@app.route("/api/v1.0/stations")
def stations():
    session = Session(bind=engine)
    # Query database for stations
    stations = session.query(Station.station).all()
    
    # Convert object to a list
    station_list=[]
    for sublist in stations:
        for item in sublist:
            station_list.append(item)
    
    # Return jsonified list
    return (jsonify(station_list))

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(bind=engine)
    # query to retrieve date and precipitation data    
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
     filter(Measurement.date >= start_date, Measurement.tobs != None).all()
    
    # Convert object to a dictionary
    tobs_dict={}
    for item in tobs_data:
        tobs_dict[str(item[0])]=str(item[1])
    
    # Return jsonified list
    return (jsonify(tobs_dict))

@app.route("/api/v1.0/<start_date>")
@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_stats(start_date, end_date=0):
    session = Session(bind=engine)    
    # If no end date, then make end date today's date 
    if end_date == 0:
        end_date = dt.date.today()
    
    # Query database for tobs between start and end date
    selection = session.query(Measurement.tobs)\
            .filter(Measurement.date >= start_date,\
            Measurement.date <= end_date,\
            Measurement.tobs != None).all()
    tobs_df = pd.DataFrame(selection, columns = ['tobs'])
    # Append items into a list
    tobs_list = []
    tobs_list.append(np.asscalar(np.int16(tobs_df['tobs'].min())))
    tobs_list.append(np.asscalar(np.int16(tobs_df['tobs'].mean())))
    tobs_list.append(np.asscalar(np.int16(tobs_df['tobs'].max())))
    
    # Return JSONified list of minimum, average and maximum temperatures
    return (jsonify(tobs_list))

if __name__ == "__main__":
    app.run(debug=True)