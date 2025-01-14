from flask_json import FlaskJSON, JsonError, json_response, as_json
from flask import Flask, request
from flask_cors import CORS
import os
from prometheus_client import start_http_server, Counter
from flask import Flask
from dataclasses import dataclass


DIR_PATH = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__, template_folder='templates')
CORS(app)
json = FlaskJSON(app)
# the minimal Flask application


@app.route('/get_value')
@as_json
def get_value():
    return dict(value=12)

@dataclass
class DataBuriedPoint:
    name :str
    doc : str

COUNTER_MAP : dict[str, Counter]  = {}

@app.route('/data_buried_point', methods=['POST'])
def images_comparison():
    # We use 'force' to skip mimetype checking to have shorter curl command.
    data = request.get_json(force=True)
    try:
        name = data['name']
        doc = data['doc']

        if not name in COUNTER_MAP :
            COUNTER_MAP[name] = Counter(name ,doc)
        
        COUNTER_MAP[name].inc()

        return json_response(msg ='ok')

    except (KeyError, TypeError, ValueError):
        raise JsonError(description='Invalid value.')


if __name__ == '__main__':
    from gevent import pywsgi
    start_http_server(8022)
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    server.serve_forever()
