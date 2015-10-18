from flask import jsonify, request

from app import app, db
from app import functions
from app.models import User


@app.route('/register')
def register():
    if 'username' not in request.json or 'password' not in request.json:
        return jsonify({'ok': False, 'error': "username or password not found"}), 400
    user = User(request.json['username'], request.json['password'])
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'ok': True, 'username': user.username, 'token': user.token}), 200
    except Exception as e:
        app.logger.error(e)
        return jsonify({'ok': False, 'error': "error while creating user"}), 400


@app.route('/status')
def status():
    flag = functions.get_daemon_status()
    status_ = functions.get_status()
    data = {'ok': True, 'daemon': flag, 'return': status_}
    return jsonify(data), 200


@app.route('/start')
def start():
    flag = functions.get_daemon_status()
    data = {'ok': False}
    if functions.start_daemon():
        data['ok'] = True
        data['daemon'] = flag
    return jsonify(data), 200


@app.route('/play')
def play():
    data = {'ok': False}
    flag = functions.get_daemon_status()
    if not flag:
        functions.start_daemon()
    if functions.start_main():
        data['ok'] = True
        data['daemon'] = functions.get_daemon_status()
    return jsonify(data), 200


@app.route('/queue', methods=['POST'])
def queue():
    flag = functions.get_daemon_status()
    data = {'ok': False}
    if 'path' not in request.json:
        return jsonify(data)
    if flag:
        return_ = functions.queue_tracks(request.json['path'])
        data['ok'] = True
        data['daemon'] = flag
        data['return'] = return_
    return jsonify(data)


# todo remove this service add it to action
@app.route('/volume', methods=['GET', 'POST'])
def volume():
    data = {}
    flag = functions.get_daemon_status()
    if request.method == 'GET':
        status_ = functions.get_status()
        volume_ = functions.get_volume(status_['status'])
        data['ok'] = True
        data['daemon'] = flag
        data['return'] = {'volume': volume_}
    if request.method == 'POST':
        if 'volume' in request.json:
            if functions.volume(request.json['volume']):
                data['ok'] = True
                data['daemon'] = flag
            else:
                data['ok'] = False
    return jsonify(data), 200


@app.route('/action', methods=['POST'])
def do_action():
    data = {'ok': False}
    if 'action' in request.json:
        action = request.json['action']
        if action == 'pause' or action == 'unpause':
            data['ok'] = functions.pause_unpause()
        elif action == 'next':
            data['ok'] = functions.next_song()
        elif action == 'previous':
            data['ok'] = functions.prev_song()
    return jsonify(data), 200


@app.route('/quit')
def quit_daemon():
    data = {'ok': False}
    flag = functions.get_daemon_status()
    if functions.quit_daemon():
        data['ok'] = True
        data['daemon'] = flag
    return jsonify(data), 200
