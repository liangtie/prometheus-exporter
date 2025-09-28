import datetime
from typing import Optional
from flask_json import FlaskJSON, JsonError, json_response, as_json
from flask import Flask, request
from flask_cors import CORS
import os
from prometheus_client import start_http_server, Counter
from dataclasses import dataclass
import threading
import time
import requests
import json

DIR_PATH = os.path.dirname(os.path.realpath(__file__))

app = Flask(__name__, template_folder='templates')
CORS(app)
json = FlaskJSON(app)


@app.route('/get_value')
@as_json
def get_value():
    return dict(value=12)


@dataclass
class Exemplar:
    href: str
    search: str


@dataclass
class DataBuriedPoint:
    name: str
    doc: str
    source: 'Optional[str]' = None


EDA_CN_LABELS = ['from']


def json_to_databuriedpoint(json_obj) -> DataBuriedPoint:
    if not isinstance(json_obj, dict):
        raise ValueError("Input must be a dictionary.")

    name = json_obj.get("name")
    doc = json_obj.get("doc")
    source = json_obj.get("source")

    if not isinstance(name, str) or not isinstance(doc, str):
        raise ValueError("Fields 'name' and 'doc' must be strings.")

    if source is not None and not isinstance(source, str):
        raise ValueError("Field 'exemplar' must be dict.")

    return DataBuriedPoint(name=name, doc=doc, source=source)


class COUNTER_MIX:
    def __init__(self, name, doc):
        self.pv_counter = Counter(f'pv_{name}', doc, EDA_CN_LABELS)
        self.uv_counter = Counter(f'uv_{name}', doc, EDA_CN_LABELS)
        self.new_usr_counter = Counter(f'new_usr_{name}', doc, EDA_CN_LABELS)
        self.mau_counter = Counter(f'mau_{name}', doc, EDA_CN_LABELS)  # 新增月活计数器


COUNTER_MAP: dict[str, COUNTER_MIX] = {}
SOURCE_VISITED_IPS: dict[str, set[str]] = {}
ALL_UNIQUE_IPS: set[str] = set()

SOURCE_VISITED_IPS_MONTHLY: dict[str, set[str]] = {}
ALL_UNIQUE_IPS_MONTHLY: set[str] = set()


def clear_visited_ips_daily():
    """Clears the VISITED_IPS dictionary every day."""
    while True:
        time.sleep(24 * 60 * 60)  # Sleep for 24 hours
        SOURCE_VISITED_IPS.clear()
        print("Cleared VISITED_IPS")


# Start the background thread to clear VISITED_IPS daily
threading.Thread(target=clear_visited_ips_daily, daemon=True).start()


def clear_visited_ips_monthly():
    """Clears the VISITED_IPS_MONTHLY dictionary on the first day of each month."""
    while True:
        now = datetime.datetime.now()
        # Calculate seconds until next month's first day
        next_month = (now.replace(day=28) + datetime.timedelta(days=4)).replace(day=1, hour=0, minute=0, second=0)
        time_to_sleep = (next_month - now).total_seconds()
        time.sleep(time_to_sleep)

        SOURCE_VISITED_IPS_MONTHLY.clear()
        print("Cleared VISITED_IPS_MONTHLY")


# Start the background thread to clear VISITED_IPS_MONTHLY monthly
threading.Thread(target=clear_visited_ips_monthly, daemon=True).start()


LOG_URL= 'https://www.eda.cn/api/chiplet/kicad/download/log'
def send_log(channelCode : str , ip : str):
    return requests.post(LOG_URL, json={'channelCode': channelCode, 'ip': ip}).json()


@app.route('/data_buried_point', methods=['POST'])
def data_buried_point():
    data = request.get_json(force=True)
    req_ip = request.headers.get('X-Real-IP') 
    client_ip = req_ip if req_ip is not None else "unknown"

    try:
        data_buried_point = json_to_databuriedpoint(data)
        name = data_buried_point.name
        doc = data_buried_point.doc
        source = data_buried_point.source

        if source is None or source == '':
            source = 'self'

        if source not in SOURCE_VISITED_IPS:
            SOURCE_VISITED_IPS[source] = set()

        source_today_visited = client_ip in SOURCE_VISITED_IPS.get(source)

        if not source_today_visited:
            SOURCE_VISITED_IPS[source].add(client_ip)

        # 月活相关逻辑
        if source not in SOURCE_VISITED_IPS_MONTHLY:
            SOURCE_VISITED_IPS_MONTHLY[source] = set()
        source_this_month_visited = client_ip in SOURCE_VISITED_IPS_MONTHLY.get(source)
        if not source_this_month_visited:
            SOURCE_VISITED_IPS_MONTHLY[source].add(client_ip)
            COUNTER_MAP[name].mau_counter.labels(source).inc()

        if name not in COUNTER_MAP:
            COUNTER_MAP[name] = COUNTER_MIX(name, doc)

        COUNTER_MAP[name].pv_counter.labels(source).inc()

        if not source_today_visited:
            COUNTER_MAP[name].uv_counter.labels(source).inc()

        if client_ip not in ALL_UNIQUE_IPS:
            COUNTER_MAP[name].new_usr_counter.labels(source).inc()
            ALL_UNIQUE_IPS.add(client_ip)

        log_res = send_log(source, client_ip)

        return json_response(msg='ok', visited_before=source_today_visited, client_ip=client_ip,
                             source_visited_ips=SOURCE_VISITED_IPS, unique_ips=ALL_UNIQUE_IPS , log_res=log_res)

    except Exception as e:
        raise JsonError(description=str(e))


if __name__ == '__main__':
    from gevent import pywsgi

    start_http_server(8022)
    server = pywsgi.WSGIServer(('0.0.0.0', 5000), app)
    server.serve_forever()
