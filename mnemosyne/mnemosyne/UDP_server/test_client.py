#
# test_client.py <Peter.Bienstman@UGent.be>
#

PORT = 6666

import subprocess
subprocess.Popen(["./bin/python", "./mnemosyne/UDP_server/server.py"])

import time
time.sleep(1)

import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Connect to server and send data.

sock.connect(("localhost", PORT))
sock.send("mnemosyne.start_review()" + "\n")

# Receive data from the server and shut down
received = sock.recv(1024)

print received

sock.close()

