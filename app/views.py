from app import app, status
from app.models import Song
from flask import render_template, redirect, url_for, jsonify
from app import functions


@app.route('/')
def index():
    return jsonify({}), 200


@app.route('/status')
def status():
    return jsonify(status)


@app.route('/play')
def play():
    functions.start_daemon()
    functions.start_main()
    return jsonify(data)
