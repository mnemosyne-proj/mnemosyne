#
# log_uploader.py <Peter.Bienstman@gmail.com>
#

import os
import time
import random
import urllib.request, urllib.error, urllib.parse
from threading import Thread

from mnemosyne.libmnemosyne.gui_translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import traceback_string, MnemosyneError


class LogUploader(Thread, Component):

    def __init__(self, component_manager):
        Thread.__init__(self)
        Component.__init__(self, component_manager)

    def upload(self, filename):

        """Upload a single file to our serverside CGI script.
        Based on code by Jeff Bauer, Aaron Watters, Jim Fulton.

        """

        # Note: we could make the following code a lot cleaner by doing a HTTP
        # PUT, but then we need to change the server side script which would
        # cause problems with backwards compatibility.
        print("upload", filename)
        host, port = self.config()["science_server"].split(":")
        uri = '/cgi-bin/cgiupload.py'
        boundary = '%s%s_%s_%s' % \
                    ('-----', int(time.time()), os.getpid(),
                     random.randint(1, 10000))
        f = open(filename, 'rb')
        data = f.read()
        f.close()
        upload_name = str(filename.split("/")[-1].split("\\")[-1])
        hdr, part, total = [], [], []
        hdr.append('Content-Disposition: form-data;' + \
                   ' name="file"; filename="%s"' % (upload_name))
        hdr.append('Content-Type: application/octet-stream')
        hdr.append('Content-Length: %d' % len(data))
        header = (('--%s\n' % boundary) + "\n".join(hdr) + "\n\n")\
            .encode("utf-8")
        footer = ('\n--%s--\n' % boundary).encode("utf-8")
        query = header + data + footer
        contentType = 'multipart/form-data; boundary=%s' % boundary
        contentLength = str(len(query))
        headers = {'Accept' : '*/*',
                   'Proxy-Connection' : 'Keep-Alive',
                   'Content-Type' : contentType,
                   'Content-Length' : contentLength}
        req = urllib.request.Request('http://' + host + ':' + port+uri,
                                     query, headers)
        response = urllib.request.urlopen(req)
        html = str(response.read())
        print(html)
        if "<pre>" in html:
            raise MnemosyneError(html)

    def run(self):
        data_dir = self.config().data_dir
        join = os.path.join
        # Find out which files haven't been uploaded yet.
        dir = os.listdir(join(data_dir, "history"))
        history_files = [x for x in dir if x.endswith(".bz2")]
        uploaded_filename = join(data_dir, "history", "uploaded2")
        if os.path.exists(uploaded_filename):
            upload_log = open(uploaded_filename)
            uploaded = [x.strip() for x in upload_log]
            upload_log.close()
        else:
            uploaded = []
        to_upload = set(history_files) - set(uploaded)
        if len(to_upload) == 0:
            return
        # Upload them to our server.
        upload_log = open(uploaded_filename, 'a')
        try:
            for f in to_upload:
                print(_("Uploading"), f, "...", end=' ')
                filename = join(data_dir, "history", f)
                self.upload(filename)
                print(f, file=upload_log)
                print(_("done!"))
        except Exception as e:
            print(_("Upload failed"))
            print(str(e))
            print(traceback_string())
        upload_log.close()

