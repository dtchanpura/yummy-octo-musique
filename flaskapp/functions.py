from threading import Thread, ThreadError
import subprocess

from flaskapp import app, db
from flaskapp.constants import NO_ACTIVE_SESSIONS, SESSION, NOTHING_TO_PLAY, CURRENT_TRACK
from flaskapp.constants import ERR_NO_SESSION, ERR_NO_TRACKS
from flaskapp.errors import FlowException

daemon_thr = None


def run_cmd(cmd):
    """
    This method runs command in linux console of Raspberry Pi
    :param cmd: The command to be executed
    :return: The output of command in console
    """
    app.logger.debug('Command:' + cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate()[0]
    app.logger.debug('Output:' + output)
    return output


def fetch_songs(path):
    """
    This method is used to fetch songs from the path and add its ID
    :param path: Path where the files are stored
    :return: True if successfully fetched
    """
    try:
        import os
        file_list = run_cmd('ls ' + path)
        for file_ in file_list:
            file_data = get_metadata(os.path.join(path, file_))
            db.session.add(file_data)
        db.session.commit()
        return True
    except Exception as e:
        app.logger.error('Error Occurred: fetch_songs, ' + e.message)
        return False


def get_metadata(file_name):
    """
    This method gets the metadata from file
    :param file_name: The input file for fetching metadata from that file
    :return: Returns the metadata of type eyed3 for particular file depending upon the file_name
    """
    import eyed3
    file_details = eyed3.load(file_name)
    return file_details


def get_album_art():
    # jpeg_byte_string = None
    mime_ = 'image/png'
    try:
        images = get_metadata(get_status()['status']['current_track']['path']).tag.images
        if len(images) > 0:
            jpeg_byte_string = images[0].image_data
            mime_ = images[0].mime_type
        else:
            jpeg_byte_string = open('flaskapp/static/images/no_album_art.png', 'r').read()
    except Exception as e:
        app.logger.error(e)
        jpeg_byte_string = open('flaskapp/static/images/no_album_art.png', 'r').read()
    return jpeg_byte_string, mime_


def start_daemon():
    """
    This method starts the Alsaplayer in Daemon mode.
    :return: True if execution successful
    """
    global daemon_thr
    try:
        if not get_daemon_status():
            cmd = 'alsaplayer -i daemon'
            daemon_thr = Thread(target=run_cmd, args=(cmd,))
            daemon_thr.start()
        return True
    except ThreadError:
        app.logger.error("Error Occurred: start_daemon")
        return False


def queue_tracks(path):
    """
    Queuing tracks for alsaplayer -e
    :param path: Path which it has to queue tracks from
    :return:
    """
    try:
        out = run_cmd('alsaplayer -e ' + path)
        if out == NO_ACTIVE_SESSIONS:
            raise FlowException(ERR_NO_SESSION)
        return True
    except FlowException as e:
        app.logger.error("Error Occurred: queue_tracks" + e.message)
        return False


def start_main():
    """
    This method is for starting the daemon.
    :return: True if alsaplayer starts
    """
    try:
        out = run_cmd('alsaplayer --start')
        status_ = get_status()['status']
        if out == NO_ACTIVE_SESSIONS:
            raise FlowException(ERR_NO_SESSION)
        elif status_['session']['playlist_length'] == 0:
            raise FlowException(ERR_NO_TRACKS)
        return True
    except FlowException as e:
        app.logger.error("Error Occurred: start_main" + e.message)
        return False


def pause_unpause():
    """
    This method is for pausing and un-pausing the alsaplayer
    :return: True if successfully paused or un-paused.
    """
    if get_status()['status']['session']['speed'] == '0%':
        run_cmd('alsaplayer --pause')
        out = run_cmd('alsaplayer --speed 1.0')
    else:
        out = run_cmd('alsaplayer --pause')
    if NO_ACTIVE_SESSIONS in out or NOTHING_TO_PLAY in out:
        return False
    return True


def next_song():
    """
    This method is to jump to next song
    :return: True if successfully changed the song to next
    """
    out = run_cmd('alsaplayer --next')
    if NO_ACTIVE_SESSIONS in out:
        return False
    return True


def prev_song():
    out = run_cmd('alsaplayer --prev')
    if NO_ACTIVE_SESSIONS in out:
        return False
    return True


def jump_to_track(track_number):
    """

    :param track_number:
    :return:
    """
    return track_number


def volume(volume_level):
    """

    :param volume_level: Represents Volume level and it should be in range 1 - 100
    :return:
    """
    out = run_cmd('alsaplayer --vol ' + str(volume_level))
    if NO_ACTIVE_SESSIONS in out:
        return False
    return True


def get_volume(status_):
    return status_['session']['volume']


def clear_playlist():
    out = run_cmd('alsaplayer --clear')
    if NO_ACTIVE_SESSIONS in out:
        return False
    return True


def get_status():
    """
    This method is to get the current status of the song playing

    :return: dict
    """
    status_ = run_cmd('alsaplayer --status')
    status_parsed = parse_status(status_)
    status_dict = {'status': status_parsed}
    return status_dict


def parse_status(status_):
    """
    This method is for parsing status from alsaplayer --status command
    :param status_:
    :return:
    """
    split_lines = status_.split('\n')
    parsed = {}
    if CURRENT_TRACK in split_lines:
        parsed['current_track'] = {}
        list_ = split_lines[split_lines.index(CURRENT_TRACK) + 1:]
        for property_ in list_:
            if ':' in property_:
                prop = property_.split(':')
                key_ = prop[0]
                value_ = prop[1]
                parsed['current_track'][key_] = value_.lstrip()

    if SESSION in split_lines:
        parsed['session'] = {}
        list_ = split_lines[1:]
        if CURRENT_TRACK in split_lines:
            list_ = split_lines[1:split_lines.index(CURRENT_TRACK)]

        for property_ in list_:
            if ':' in property_:
                prop = property_.split(':')
                key_ = prop[0]
                value_ = prop[1]
                parsed['session'][key_] = value_.lstrip()

    if 'current_track' in parsed:
        if 'title' not in parsed['current_track']:
            if 'path' in parsed['current_track']:
                parsed['current_track']['title'] = parsed['current_track']['path'].split('/')[-1]
        parsed['current_track']['length_mins'] = conv_to_mins(parsed['current_track']['length'].split(' ')[0])
    return parsed


def conv_to_mins(seconds):
    mins = int(seconds) / 60
    secs = int(seconds) % 60
    mins_str = str(mins)
    secs_str = str(secs)
    if mins < 10:
        mins_str = '0' + mins_str
    if secs < 10:
        secs_str = '0' + secs_str
    return mins_str + ':' + secs_str


def get_files_in_path(path_='~/Music'):
    import os
    user = os.path.abspath('.').split(os.sep)[2]
    if '~/' in path_:
        path_ = path_.replace('~/', '/home/' + user + '/')
    files_dict = {}
    dirs_dict = {}
    for dirname, dirnames, filenames in os.walk(path_):
        # print path to all subdirectories first.
        for subdirname in dirnames:
            if subdirname.startswith('.'):
                continue
                # print path to all filenames.
            dirs_dict[os.path.join(dirname, subdirname)] = subdirname
        for filename in filenames:
            if filename.endswith('.mp3'):
                files_dict[os.path.join(dirname, filename)] = filename
        # Advanced usage:
        # editing the 'dirnames' list will stop os.walk() from recursing into there.
        if '.git' in dirnames:
            # don't go into any .git directories.
            dirnames.remove('.git')
    return files_dict, dirs_dict


def get_daemon_status():
    """
    :return:
    """
    return 'session' in get_status()['status']


def quit_daemon():
    if run_cmd('alsaplayer --quit') is not None:
        return True
    return False
