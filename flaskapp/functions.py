import subprocess

import alsaplayer

from flaskapp import app


def run_cmd(cmd):
    """
    This method runs command in linux console of Raspberry Pi
    :param cmd: The command to be executed
    :return: The output of command in console
    """
    app.logger.debug('Command:' + cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = p.communicate()[0]
    app.logger.debug('Output: %s' % output)
    return output


def start_daemon():
    """
    This method starts the alsaplayeraplayer in Daemon mode.
    :return: True if execution successful
    """
    cmd = 'alsaplayer -i daemon > /dev/null 2>&1 &'
    run_cmd(cmd)
    return True


def get_metadata(file_name):
    """
    This method gets the metadata from file
    :param file_name: The input file for fetching metadata from that file
    :return: Returns the metadata of type eyed3 for particular file depending upon the file_name
    """
    import eyed3
    file_details = eyed3.load(file_name)
    return file_details


def get_album_art(session_id=0):
    # jpeg_byte_string = None
    mime_ = 'image/png'
    try:
        images = get_metadata(alsaplayer.get_file_path(session_id)).tag.images
        if len(images) > 0:
            jpeg_byte_string = images[0].image_data
            mime_ = images[0].mime_type
        else:
            jpeg_byte_string = open('flaskapp/static/images/no_album_art.png', 'r').read()
    except Exception as e:
        app.logger.error(e)
        jpeg_byte_string = open('flaskapp/static/images/no_album_art.png', 'r').read()
    return jpeg_byte_string, mime_


def queue_tracks(path_, session_id=0):
    """
    Queuing tracks for alsaplayer -e
    :param path_: Path which it has to queue tracks from
    :param session_id: Session's ID
    :type session_id: int
    :return:
    """
    app.logger.info(path_)
    return alsaplayer.add_and_play(session_id, str(path_)) == 1


def pause_unpause(session_id=0):
    """
    This method is for pausing and un-pausing the alsaplayer
    :return: True if successfully paused or un-paused.
    """
    if alsaplayer.get_speed(session_id) == 0:
        return alsaplayer.unpause(session_id) == 1
    else:
        return alsaplayer.pause(session_id) == 1


def next_song(session_id=0):
    """
    This method is to jump to next song
    :return: True if successfully changed the song to next
    """
    return alsaplayer.next(session_id) == 1


def prev_song(session_id=0):
    if alsaplayer.prev(session_id) == 1:
        return True
    return False


def volume(volume_level, session_id=0):
    """
    :param volume_level: Represents Volume level and it should be in range 1 - 100
    :param session_id: Session ID
    :return:
    """
    if alsaplayer.set_volume(session_id, volume_level) == 1:
        return True
    return False


def clear_playlist(session_id=0):
    if alsaplayer.clear_playlist(session_id) == 1:
        return True
    return False


def get_status(session_id=0):
    """
    This method is to get the current status of the song playing
    :param session_id: Session ID
    :type session_id: int
    :return: dict
    """
    length = 0
    position = 0
    session_name = 'none'
    playlist_length = 0
    speed = 0
    volume_level = 1
    song_title = ''
    song_artist = ''
    song_album = ''
    try:
        length = alsaplayer.get_length(session_id)
        position = alsaplayer.get_position(session_id)
        session_name = alsaplayer.get_session_name(session_id)
        # playlist = alsaplayer.get_playlist(session_id)
        playlist_length = alsaplayer.get_playlist_length(session_id)
        speed = alsaplayer.get_speed(session_id)
        volume_level = alsaplayer.get_volume(session_id)
        song_title = alsaplayer.get_title(session_id)
        song_artist = alsaplayer.get_artist(session_id)
        song_album = alsaplayer.get_album(session_id)
    except Exception as e:
        app.logger.error(e)
    
    status = {
        "current_track": {
            "length_mins": conv_to_mins(length),
            "length": length,
            "position": position,
            "title": song_title,
            "album": song_album,
            "artist": song_artist
        },
        "session": {
            "name": session_name,
            "playlist_length": playlist_length,
            "speed": "%s%s" % (speed * 100, '%'),
            "volume": volume_level
        }

    }
    status_dict = {'status': status}
    return status_dict


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


def get_current_song_path(session_id=0):
    try:
        path_ = alsaplayer.get_file_path_for_track(session_id)
        return path_.replace('//', '/')
    except Exception as e:
        app.logger.error(e)
        pass


def get_daemon_status(session_id=0):
    """
    :return:
    """
    try:
        return alsaplayer.session_running(session_id)
    except Exception as e:
        app.logger.error(e)
        return False


def quit_daemon(session_id=0):
    if alsaplayer.quit(session_id):
        return True
    return False
