#!/usr/bin/env python3
# -*- coding:utf-8 -*-


__author__    = 'Mu Yang <emfomy@gmail.com>'
__copyright__ = 'Copyright 2019'

from flask import Flask
from flask import json
from flask import jsonify
from flask import request
from flask import send_from_directory

app = Flask(__name__, static_folder='assets')


@app.route('/favicon.ico')
def favicon_route():
    return app.send_static_file('favicon/favicon.ico')


@app.route('/')
def index_route():
    return send_from_directory('src', 'index.html')


@app.route('/data/data.js')
def data_route():
    demo = app.config['demo']
    data = {
        'pardata': demo.pardata(),
        'qadata':  demo.qadata(),
    }
    return 'var _data = ' + json.dumps(data)


@app.route('/post', methods=['POST'])
def post_route():
    demo = app.config['demo']

    try:
        data = request.data.decode()
        print(colored('1;95', data))
        jdata = json.loads(data)
        astr  = demo.predict(jdata['paragraph'], jdata['question'], jdata['id'])
        print(colored('1;96', astr))
        return jsonify({'result': astr})
    except Exception as e:
        msg = f'{type(e).__name__}: {e}'
        print(colored('1;31', msg))
        return jsonify(message=msg), 500


def colored(code, string):
    """Color string."""
    return f'\033[{code}m{string}\033[0m'

def run(demo, host, port, threaded=True, debug=True, **kwargs):
    """Run server."""

    app.config['demo'] = demo

    app.run(host=host, port=port, threaded=threaded, debug=debug, **kwargs)
