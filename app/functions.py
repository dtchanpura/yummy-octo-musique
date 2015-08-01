from app import app, status
from app.models import Song

import subprocess


def run_cmd(cmd):
    """

    :rtype : object
    """
    app.logger.debug('Command:' + cmd)
    p = subprocess.Popen(cmd, shell=True)
    output, err = p.communicate()
    app.logger.debug('Output:' + output)
    return output, err


# while True:
#     out = p.stderr.read(1)
#     if out == '' and p.poll() != None:
#         break
#     if out != '':
#         sys.stdout.write(out)
#         sys.stdout.flush()


def start_daemon():
    """
    This function starts the Alsaplayer in Daemon mode.
    :return:
    """
    try:
        out = run_cmd('alsaplayer -i daemon &')
        status['startd'] = True
        status['paused'] = True
        return True
    except:
        app.logger.error("Error Occured: start_daemon")
        return False


def queue_tracks(path):
    try:
        out = run_cmd('alsaplayer -e ' + path)
        status['paused'] = False
        return True
    except:
        app.logger.error("Error Occured: queue_tracks")
        return False


def start_main():
    pass


def pause_unpause():
    out = run_cmd('alsaplayer --pause')
    if out == 'No active sessions' or out == 'Nothing to play.':
        status['paused'] = True
        return False
    else:
        status['paused'] = not status['paused']
        return True


def next_song():
    out = run_cmd('alsaplayer --next')
    if out == 'No active sessions' or out == 'Nothing to play.':
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
    pass


def volume(volume_level):  # Should be in range 1 - 100
    pass
