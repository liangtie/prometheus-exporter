from flask_json import FlaskJSON, JsonError, json_response, as_json
from flask import Flask, request
from flask_cors import CORS
import os
from prometheus_client import start_http_server, Counter
from dataclasses import dataclass
from datetime import datetime, timedelta

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__, template_folder='templates')
CORS(app)
json = FlaskJSON(app)

@app.route('/get_value')
@as_json
def get_value():
    return dict(value=12)

@dataclass
class DataBuriedPoint:
    name: str
    doc: str

def json_to_databuriedpoint(json_obj) -> DataBuriedPoint:
    return DataBuriedPoint(**json_obj)

class COUNTER_MIX:
    def __init__(self, name, doc):
        self.pv_counter = Counter(f'pv_{name}', doc)
        self.uv_counter = Counter(f'uv_{name}', doc)

COUNTER_MAP: dict[str, COUNTER_MIX] = {}
VISITED_IPS: dict[str, str] = {}

def clear_old_ips():
    current_date = datetime.now()
    cutoff_date = current_date - timedelta(days=3)
    for ip, date_str in list(VISITED_IPS.items()):
        visit_date = datetime.strptime(date_str, '%Y-%m-%d')
        if visit_date < cutoff_date:
            del VISITED_IPS[ip]

@app.route('/data_buried_point', methods=['POST'])
def data_buried_point():
    clear_old_ips()
    data = request.get_json(force=True)
    client_ip = request.remote_addr
    current_date = datetime.now().strftime('%Y-%m-%d')
    visited_before = VISITED_IPS.get(client_ip) == current_date
    VISITED_IPS[client_ip] = current_date

    try:
        data_buried_point = json_to_databuriedpoint(data)
        name = data_buried_point.name
        doc = data_buried_point.doc

        if name not in COUNTER_MAP:
            COUNTER_MAP[name] = COUNTER_MIX(name, doc)

        COUNTER_MAP[name].pv_counter.inc()

        if not visited_before:
            COUNTER_MAP[name].uv_counter.inc()

        return json_response(msg='ok', visited_before=visited_before)

    except Exception as e:
        raise JsonError(description= str(e))

if __name__ == '__main__':
    from gevent import pywsgi
    start_http_server(8022)
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    server.serve_forever()
