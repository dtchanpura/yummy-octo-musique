from flask import jsonify, request, Response, send_from_directory
from flask_cors import cross_origin

from flaskapp import app, db
from flaskapp import functions
from flaskapp.models import User


@app.route('/check')
@cross_origin()
def check():
    return '{"ok":true}', 200


@app.route('/register', methods=['POST'])
@cross_origin()
def register():
    if 'username' not in request.json or 'password' not in request.json:
        return jsonify({'ok': False, 'error': "username or password not found"}), 200
    user = User(request.json['username'], request.json['password'])
    try:
        db.session.add(user)
        db.session.commit()
        return jsonify({'ok': True, 'username': user.username, 'token': user.token}), 200
    except Exception as e:
        app.logger.error(e)
        return jsonify({'ok': False, 'error': "error while creating user"}), 200


@app.route('/status', methods=['GET'])
@cross_origin()
def status():
    flag = functions.get_daemon_status()
    status_ = functions.get_status()
    data = {'ok': True, 'daemon': flag, 'return': status_}
    return jsonify(data), 200


@app.route('/start_daemon', methods=['POST', 'OPTIONS'])
@cross_origin()
def start():
    return_type = check_token(request)
    if return_type is not None:
        return return_type
    data = {'ok': False}
    if not functions.get_daemon_status():
        if functions.start_daemon():
            data['ok'] = True
            data['daemon'] = functions.get_daemon_status()
    return jsonify(data), 200


@app.route('/play', methods=['GET', 'POST'])
@cross_origin()
def play():
    return_type = check_token(request)
    if return_type is not None:
        return return_type
    data = {'ok': False}
    flag = functions.get_daemon_status()
    if not flag:
        functions.start_daemon()
    data['daemon'] = functions.get_daemon_status()
    return jsonify(data), 200


@app.route('/queue', methods=['POST'])
@cross_origin()
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
        data['return'] = return_
    return jsonify(data)


@app.route('/action', methods=['POST'])
@cross_origin()
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
@cross_origin()
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
    image_response, mime_type = functions.get_album_art()
    return Response(response=image_response, mimetype=mime_type)


#    except Exception as e:
#        app.logger.error(e.message)
#        jpeg_byte_string = open('flaskapp/static/images/no_album_art.png', 'r').read()
#        return Response(jpeg_byte_string, 'image/png')


@app.route('/get_files', methods=['POST'])
@cross_origin()
def get_files():
    return_type = check_token(request)
    if return_type is not None:
        return return_type
    if 'path' not in request.json:
        return jsonify({'ok': False, 'error': 'path not found in request'})
    files_dict, dirs_dict = functions.get_files_in_path(request.json['path'])
    return jsonify({'ok': True, 'files': files_dict, 'dirs': dirs_dict})


@app.route('/get_token', methods=['POST'])
@cross_origin()
def get_token():
    import hashlib
    if 'username' not in request.json or 'password' not in request.json:
        return jsonify({'ok': False, 'error': 'username or password not found'})
    query = User.query.filter(User.username == request.json['username'])
    if query.count() == 0:
        return jsonify({'ok': False, 'error': 'username or password invalid'})
    user = query.all()[0]
    pass_req = hashlib.sha256(request.json['password'] + user.salt_string).hexdigest()
    if pass_req != user.password:
        return jsonify({'ok': False, 'error': 'username or password invalid'})
    return jsonify({'ok': True, 'token': user.token, 'username': user.username})


@app.route('/upload_song')
def upload_song():
    pass


@app.route('/download_song')
def download_song():
    import os
    song_path = functions.get_current_song_path()
    sng_path = os.sep.join(song_path.split('/')[:-1])
    file_name = song_path.split('/')[-1]
    app.logger.debug('file_name = ' + file_name + ' sng_path= ' + sng_path)
    file_size = os.path.getsize(song_path)
    response = send_from_directory(directory=sng_path, filename=file_name)
    response.headers['Content-Description'] = 'File Transfer'
    response.headers['Cache-Control'] = 'no-cache'
    response.headers['Content-Type'] = 'application/octet-stream'
    response.headers['Content-Disposition'] = 'attachment; filename=%s' % file_name
    response.headers['Content-Length'] = file_size
    return response


def check_token(request_):
    if 'token' not in request_.json:
        return jsonify({'ok': False, 'error': 'token required'})
    query = User.query.filter(User.token == request_.json['token'])
    if query.count() == 0:
        return jsonify({'ok': False, 'error': 'invalid token'})
