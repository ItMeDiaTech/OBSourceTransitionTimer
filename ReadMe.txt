REQUIRED: 
-Must use obswebsocket version > 5.0
    -https://github.com/obsproject/obs-websocket/releases
        -Select obs-websocket-5.0.0-beta1-Windows-Installer.exe
        -Make sure to uninstall older version if you haven't beforehand
-Must have Python 3.6 in OBS Scripts > Settings
-Must have Python 3.10 installed (or newest)
-Must have Python in System Environment
    -To check, open cmd and run 'py --version'
    -If it doesn't work, hit the windows key
        -Type 'system environment'
        -Click on 'Edit...'
        -Click on 'Environmental Variables'
        -Under System Variables, click on 'Path' and hit 'Edit'
        -Hit 'new' and paste Python version >= Python 3.10 Path
        -Hit 'OK' or 'Apply" on all Windows

HOW TO USE:
-The files can be placed anywhere that is readable by your computer / OBS - just make sure they are all together at all times
-Import SourceTransitionTimer.py into OBS
    -This will set and save transitions for sources into a text file to be used by the timer, run later
-Set transitions using the interface created in OBS Scripts
-Open TransitionTimerWithWebsockets.py in any text editor
    -Edit password and port at the top of the file, should have documentation to make it easy to find
-After timers are created and settings are saved, run the StartTimers.bat file to launch TransitionTimerWithWebsocket.py for you
-That's all!
