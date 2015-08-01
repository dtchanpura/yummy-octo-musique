from app import app, status
# from app.models import Song
from constants import NO_ACTIVE_SESSIONS, ERR_NO_SESSION, NOTHING_TO_PLAY
from errors import FlowException
from threading import Thread, ThreadError
import subprocess


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
    :param path:
    :return:
    """

    return path

def get_metadata(file):
    import eyed3
    file_details = eyed3.load(file)

def start_daemon():
    """
    This function starts the Alsaplayer in Daemon mode.
    :return: True if execution successful
    """
    try:
        cmd = 'alsaplayer -i daemon'
        daemon_thr = Thread(target=run_cmd, args=(cmd,))
        daemon_thr.start()
        status['startd'] = True
        status['paused'] = True
        return True
    except ThreadError:
        app.logger.error("Error Occurred: start_daemon")
        return False


def queue_tracks(path):
    try:
        out = run_cmd('alsaplayer -e ' + path)
        if out == NO_ACTIVE_SESSIONS:
            raise FlowException(ERR_NO_SESSION)
        else:
            status['paused'] = False
            return True
    except FlowException as e:
        app.logger.error("Error Occurred: queue_tracks" + e.message)
        return False


def start_main():
    pass


def pause_unpause():
    out = run_cmd('alsaplayer --pause')
    if NO_ACTIVE_SESSIONS in out or NOTHING_TO_PLAY in out:
        status['paused'] = True
        return False
    else:
        status['paused'] = not status['paused']
        return True


def next_song():
    """
    This method is to jump to next song
    :return: True if successfully changed the song to next
    """
    out = run_cmd('alsaplayer --next')
    if out in NO_ACTIVE_SESSIONS or out in '':
        status['paused'] = True
        return False
    else:
        status['paused'] = False
        return True
    pass


def prev_song():
    pass


def stop():
    pass


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
    return volume_level
