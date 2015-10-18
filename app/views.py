from flask import jsonify, request, Response

from app import app, db
from app import functions
from app.models import User


@app.route('/register', methods=['POST'])
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


@app.route('/start', methods=['POST'])
def start():
    return_type = check_token(request)
    if return_type is not None:
        return return_type
    data = {'ok': False}
    if functions.start_daemon():
        data['ok'] = True
        data['daemon'] = functions.get_daemon_status()
    return jsonify(data), 200


@app.route('/play', methods=['GET', 'POST'])
def play():
    return_type = check_token(request)
    if return_type is not None:
        return return_type
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
    return_type = check_token(request)
    if return_type is not None:
        return return_type

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


@app.route('/action', methods=['POST'])
def do_action():
    return_type = check_token(request)
    if return_type is not None:
        return return_type

    data = {'ok': False}
    if 'action' in request.json:
        action = request.json['action']
        if action == 'pause' or action == 'unpause':
            data['ok'] = functions.pause_unpause()
        elif action == 'next':
            data['ok'] = functions.next_song()
        elif action == 'previous':
            data['ok'] = functions.prev_song()
        elif action == 'volume':
            data['ok'] = functions.volume(request.json['volume'])
    data['daemon'] = functions.get_daemon_status()
    return jsonify(data), 200


@app.route('/quit', methods=['GET', 'POST'])
def quit_daemon():
    return_type = check_token(request)
    if return_type is not None:
        return return_type

    data = {'ok': False}
    flag = functions.get_daemon_status()
    if functions.quit_daemon():
        data['ok'] = True
        data['daemon'] = flag
    return jsonify(data), 200


@app.route('/album_art')
def get_album_art():
    image_response, mime_type = functions.get_album_art(functions.get_status()['status']['current_track']['path'])
    return Response(response=image_response, mimetype=mime_type)


def check_token(request_):
    if 'token' not in request_.json:
        return jsonify({'ok': False, 'error': 'token required'})
    query = User.query.filter(User.token == request_.json['token'])
    if query.count() == 0:
        return jsonify({'ok': False, 'error': 'invalid token'})
