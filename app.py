# import json
from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
import traceback
# from waitress import serve
from askindex import Indices
# from flask_apscheduler import APScheduler
from datetime import datetime
import logging
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'
# scheduler = APScheduler()
cors = CORS(app, resources={r"/indices": {"origins": "*"}})

# # initialize scheduler with your preferred timezone
# scheduler = BackgroundScheduler({'apscheduler.timezone': 'Asia/Calcutta'})
# # add a custom jobstore to persist jobs across sessions (default is in-memory)
# scheduler.add_jobstore('sqlalchemy', url='sqlite:////tmp/schedule.db')
# scheduler.start()

from pytz import utc

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ProcessPoolExecutor


jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///jobs.db')
}
executors = {
    'default': {'type': 'threadpool', 'max_workers': 20},
    'processpool': ProcessPoolExecutor(max_workers=5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 3
}
scheduler = BackgroundScheduler()

@app.route('/indices',methods=["GET"])
@cross_origin(origin='*' ,headers=['Content- Type'])
def indices():
    try:
        symbol = request.args.get('symbol')
        nf = Indices(symbol=symbol)
        return nf.df.tail(5).to_html()
    except Exception:
        return traceback.format_exc()

def load_job():
    print("This is running from Scheduled job", datetime.now())
    for symbol in ["NIFTY 50"]:
        df = Indices(symbol=symbol)
        df.load_livedata()
    print("Data Loaded", df.dff.tail(1).to_json())

@app.route("/")
def main():
    return """<h2>Indices</h2>
              <ul>
              <li><a href="/indices?symbol=NIFTY%2050"> NIFTY 50</a> </li>
              <li><a href="/indices?symbol=NIFTY%20BANK"> NIFTY BANK</a> </li>
              </ul>"""

if __name__ == "__main__":
    # scheduler.add_job(id="JOb1", func=load_job, trigger='interval', seconds=15)
    # scheduler.start()
    scheduler.add_job(func=load_job, trigger='interval', seconds=120)
    scheduler.configure(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
    
    scheduler.start()
    app.run(debug=True, host='0.0.0.0', port=8000)##Replaced with below code to run it using waitress 
   # serve(app, host='0.0.0.0', port=8000)
   