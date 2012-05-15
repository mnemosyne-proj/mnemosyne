#
# log_uploader.py <Peter.Bienstman@UGent.be>
#

import os
import time
import random
import urllib2
from threading import Thread

from mnemosyne.libmnemosyne.translator import _
from mnemosyne.libmnemosyne.component import Component
from mnemosyne.libmnemosyne.utils import traceback_string


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

        host, port = self.config()["science_server"].split(":")
        uri = '/cgi-bin/cgiupload.py'
        boundary = '%s%s_%s_%s' % \
                    ('-----', int(time.time()), os.getpid(),
                     random.randint(1, 10000))
        f = file(filename, 'rb')
        data = f.read()
        f.close()
        upload_name = str(filename.split("/")[-1].split("\\")[-1])
        hdr, part, total = [], [], []
        hdr.append('Content-Disposition: form-data;' + \
                   ' name="file"; filename="%s"' % (upload_name))
        hdr.append('Content-Type: application/octet-stream')
        hdr.append('Content-Length: %d' % len(data))
        part.append("%s\n\n%s" % ('\n'.join(hdr), data))
        total.append('--%s\n' % boundary)
        total.append(("\n--%s\n" % boundary).join(part))
        total.append('\n--%s--\n' % boundary)
        query = ''.join(total)
        contentType = 'multipart/form-data; boundary=%s' % boundary
        contentLength = str(len(query))
        headers = {'Accept' : '*/*',
                   'Proxy-Connection' : 'Keep-Alive',
                   'Content-Type' : contentType,
                   'Content-Length' : contentLength}
        req = urllib2.Request('http://' + host + ':' + port+uri, query, headers)
        response = urllib2.urlopen(req)
        html = response.read()

    def run(self):
        data_dir = self.config().data_dir
        join = os.path.join
        dir = os.listdir(unicode(join(data_dir, "history")))
        # Find out which files haven't been uploaded yet.
        dir = os.listdir(unicode(join(data_dir, "history")))
        history_files = [x for x in dir if x.endswith(".bz2")]
        uploaded = None
        try:
            upload_log = file(join(data_dir, "history", "uploaded"))
            uploaded = [x.strip() for x in upload_log]
            upload_log.close()
        except:
            uploaded = []
        to_upload = set(history_files) - set(uploaded)
        if len(to_upload) == 0:
            return
        # Upload them to our server.
        upload_log = file(join(data_dir, "history", "uploaded"), 'a')
        try:
            for f in to_upload:
                print _("Uploading"), f, "...",
                filename = join(data_dir, "history", f)
                self.upload(filename)
                print >> upload_log, f
                print _("done!")
        except:
            print _("Upload failed")
            print traceback_string()
        upload_log.close()

