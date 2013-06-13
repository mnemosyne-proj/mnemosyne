#
# quick_and_dirty_offline_client.py <Peter.Bienstman@UGent.be>
#

# Simple review webserver to be run on a mobile device which can also sync
# to a sync server running e.g. on a desktop or a different server.

# Modify the settings below to reflect your situation.
data_dir = "/sdcard/Mnemosyne/"
filename =  "default.db"
sync_server = "192.168.2.55"
sync_port = 8512
sync_username = ""
sync_password = ""

# Determine system.
android = False
try:
    import android
    droid = android.Android()
    android = True
    # Work around QPython issue.
    import sys
    sys.platform = "linux2"
except:
    pass

# Initialise Mnemosyne.
from mnemosyne.libmnemosyne import Mnemosyne
mnemosyne = Mnemosyne(upload_science_logs=False, interested_in_old_reps=True)
mnemosyne.components.insert(0,
        ("mnemosyne.libmnemosyne.translators.no_translator", "NoTranslator"))
mnemosyne.components.append(\
        ("mnemosyne.libmnemosyne.ui_components.main_widget", "MainWidget"))
mnemosyne.initialise(data_dir=data_dir, filename=filename)

# Sync.
do_sync = True
if android:
    droid.dialogCreateAlert("Mnemosyne", "Perform sync?") 
    droid.dialogSetPositiveButtonText("Yes")
    droid.dialogSetNegativeButtonText("No")
    droid.dialogShow()
    result = droid.dialogGetResponce()
    print result
    droid.dialogDismiss()

if do_sync:
    mnemosyne.controller().sync(sync_server, sync_port, 
        sync_username, sync_password)

# Start review server.
from mnemosyne.webserver.webserver import WebServerThread
web_server_thread = WebServerThread(mnemosyne.component_manager)
web_server_thread.daemon = True
web_server_thread.start() 

if android:
    #droid.view("http://127.0.0.1:8513")
    droid.webViewShow("http://127.0.0.1:8513")

import time
try:
    while True:
        time.sleep(0.1)
except KeyboardInterrupt:
    pass


