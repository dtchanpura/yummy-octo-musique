# Yummy Octo Musique 

[![Build Status](https://travis-ci.org/dtchanpura/yummy-octo-musique.svg?branch=master)](https://travis-ci.org/dtchanpura/yummy-octo-musique)

Music Player for Remote devices.

This is a start for using Alsaplayer to make it work with Raspberry Pi and make a simple API that could share status and perform operations like play, pause, navigation, etc.

Right now it is using simple commands to control the alsaplayer in terminal but it needs to add following things in future:

1. alsaplayer Github repo for python module
1. libboost for building python module

####Objects:
`status` Object:
```json
{	
	"current_track": current_track,
	"session": session
}
```
`current_track` Object:


`session` Object:


####Functions:
* register [POST]:
	* This is to register with username and password to get a token generated.
	* Params: `{"username": username, "password": password}`
	* Returns: `{"ok": true/false, "error": message}` error is displayed only if username is duplicated or invalid. Currently no limitations set on password.
* get_token [POST]:
 	* Params: `{"username": username, "password": password}`
	* Returns: `{"ok": true/false, "error": message}` 
* start_daemon [POST]:
	* This function is to start the alsaplayer in daemon mode.
	* Params: `{"token": token}`
	* Returns: `{"ok": true/false}`
* play [POST]:
	* This function starts playing if the songs are queued. Even if the daemon is not started it will start it and then play the songs.
	* Params: `{"token": token}`
	* Returns: `{"ok": true/false}`
* status [GET]:
	* This is basic function which returns the status of the alsaplayer. This return structure may change in future.
	* Params: None
	* Returns: 
	```{"ok": ok, "status":status}```
* queue [POST]:
* action [POST]:
* quit [POST]:
* album_art [GET]:
