################################################
# Import Libraries
#################################################

import numpy as np
import datetime as dt
from datetime import datetime
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Meas = Base.classes.measurement
Stion = Base.classes.station

################################################
# Application Setup
#################################################

app = Flask(__name__)

#Define static routes
@app.route('/')
def index():
    return (f'Welcome to the Hawaii API.<br/>'
            f'<br/>'
            f'These are the available routes:<br/>'
            f'<br/>'
            f'/api/v1.0/precipitation<br/>'
            f'/api/v1.0/stations<br/>'
            f'/api/v1.0/tobs<br/>'
            f'/api/v1.0/start Date Format YYYY-MM-DD<br/>'
            f'/api/v1.0/start/end ate Format YYYY-MM-DD<br/>')

@app.route('/api/v1.0/precipitation')
def precip():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Get all precipitation values by date
    results = session.query(Meas.date,Meas.prcp).all()

    #Close session
    session.close()

    # Convert list of results into a dictionary
    precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        precipitation.append(prcp_dict)

    return jsonify(precipitation)

@app.route('/api/v1.0/stations')
def station():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Get information for all stations
    results = session.query(Stion.station,Stion.name).all()

    #Close session
    session.close()

    # Convert list of results into a dictionary
    stations = []
    for station_id, name in results:
        station_dict = {}
        station_dict['station_id'] = station_id
        station_dict['station_name'] = name
        stations.append(station_dict)

    return jsonify(stations)

@app.route('/api/v1.0/tobs')
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Get list of stations counting rows
    stations = session.query(Meas.station, func.count(Meas.station)). \
                        group_by(Meas.station).order_by(func.count(Meas.station).desc()).all()
    #Get id of most active station
    top_station = stations[0][0]

    #Finding the most recent date in the Dataset and store as Str
    start_date = session.query(Meas.date).order_by(Meas.date.desc()).first()[0]

    #Calculate 12 months back
    end_date = (datetime.strptime(start_date,'%Y-%m-%d')-dt.timedelta(days=365)).strftime('%Y-%m-%d')

    #Query to get temperatures for the most active station for the last 12 months
    results = session.query(Meas.date,Meas.tobs).filter(Meas.date<=start_date).filter(Meas.date>=end_date). \
                    filter(Meas.station==top_station).all()

    #Close session
    session.close()

    # Convert list of results into a dictionary
    temp = []
    for date, tobs in results:
        temp_dict = {}
        temp_dict[date] = tobs
        temp.append(temp_dict)

    return jsonify(temp)

@app.route('/api/v1.0/<start>')
def start(start):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Query to get TMIN`, `TAVG`, and `TMAX` for <start> date onwards
    results = session.query(func.min(Meas.tobs),func.max(Meas.tobs), func.round(func.avg(Meas.tobs),2)). \
        filter(Meas.date>=start).all()

    #Close session
    session.close()

    # Convert list of results into a dictionary
    stats = []
    for TMIN, TMAX, TAVG in results:
        stats_dict = {}
        stats_dict['TMIN'] = TMIN
        stats_dict['TMAX'] = TMAX
        stats_dict['TAVG'] = TAVG
        stats.append(stats_dict)

    return jsonify(stats)

@app.route('/api/v1.0/<start>/<end>')
def start_end(start,end):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Query to get TMIN`, `TAVG`, and `TMAX` for <start> date onwards
    results = session.query(func.min(Meas.tobs),func.max(Meas.tobs), func.round(func.avg(Meas.tobs),2)). \
        filter(Meas.date>=start).filter(Meas.date<=end).all()

    #Close session
    session.close()

    # Convert list of results into a dictionary
    stats = []
    for TMIN, TMAX, TAVG in results:
        stats_dict = {}
        stats_dict['TMIN'] = TMIN
        stats_dict['TMAX'] = TMAX
        stats_dict['TAVG'] = TAVG
        stats.append(stats_dict)

    return jsonify(stats)

#4. Define main behaviour
if __name__=='__main__':
    app.run(debug=True)