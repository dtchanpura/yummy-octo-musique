from threading import Thread, ThreadError
import subprocess

from app import app, db
from constants import NO_ACTIVE_SESSIONS, SESSION, NOTHING_TO_PLAY, CURRENT_TRACK
from constants import ERR_NO_SESSION, ERR_NO_TRACKS
from errors import FlowException

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


def get_album_art(file_name):
    # jpeg_byte_string = None
    mime_ = 'image/png'
    try:
        images = get_metadata(file_name).tag.images
        if len(images) > 0:
            jpeg_byte_string = images[0].image_data
            mime_ = images[0].mime_type
        else:
            jpeg_byte_string = open('app/static/images/no_album_art.png', 'r').read()
    except Exception as e:
        app.logger.error(e)
        jpeg_byte_string = open('app/static/images/no_album_art.png', 'r').read()
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
    return parsed


def get_daemon_status():
    """
    :return:
    """
    return 'session' in get_status()['status']


def quit_daemon():
    if run_cmd('alsaplayer --quit') is not None:
        return True
    return False
