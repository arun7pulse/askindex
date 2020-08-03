# import json
from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
import traceback
from waitress import serve
from askindex import Indices

app = Flask(__name__)
app.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(app, resources={r"/indices": {"origins": "*"}})

@app.route('/indices',methods=["GET"])
@cross_origin(origin='*' ,headers=['Content- Type'])
def indices():
    try:
        symbol = request.args.get('symbol')
        nf = Indices(symbol=symbol)
        return nf.df.tail(5).to_html()
    except Exception:
        return traceback.format_exc()

@app.route("/")
def main():
    return """<h2>Indices</h2>
              <ul>
              <li><a href="/indices?symbol=NIFTY%2050"> NIFTY 50</a> </li>
              <li><a href="/indices?symbol=NIFTY%20BANK"> NIFTY BANK</a> </li>
              </ul>"""

if __name__ == "__main__":
   #app.run(debug=True)##Replaced with below code to run it using waitress 
   serve(app, host='0.0.0.0', port=8000)