##############################################################################
#
# Logging related functionality <Peter.Bienstman@UGent.be>
#
##############################################################################

import os, logging, bz2, sets, traceback, time, urllib2
from threading import Thread
from random import randint
from string import joinfields
from mnemosyne.core import *



##############################################################################
#
# Archive log to history folder if it's large enough.
#
##############################################################################

def archive_old_log():

    basedir = get_basedir()
    
    log_name = os.path.join(basedir,"log.txt")
    
    try:
        log_size = os.stat(log_name).st_size
    except:
        log_size = 0

    if log_size > 64000:

        user  = get_config("user_id")
        index = get_config("log_index")

        archive_name = "%s_%05d.bz2" % (user, index)

        f = bz2.BZ2File(os.path.join(basedir, "history", archive_name), 'w')
                                      
        for l in file(log_name):
            f.write(l)

        f.close()

        os.remove(log_name)
              
        set_config("log_index", index+1)



##############################################################################
#
# Upload a single file to our serverside CGI script.
#
#   Based on code by Jeff Bauer, Aaron Watters, Jim Fulton
#
##############################################################################

def upload(filename):

    host, port = get_config("upload_server").split(":")
    uri = '/cgi-bin/cgiupload.py'
    
    boundary = '%s%s_%s_%s' % \
                ('-----', int(time.time()), os.getpid(), randint(1,10000))

    f = file(filename, 'rb')
    data = f.read()
    f.close()

    upload_name = str(filename.split("/")[-1].split("\\")[-1])

    hdr = []; part = []; total = []
    hdr.append('Content-Disposition: form-data;' + \
               ' name="file"; filename="%s"' % (upload_name))
    hdr.append('Content-Type: application/octet-stream')
    hdr.append('Content-Length: %d' % len(data))
    part.append("%s\n\n%s" % (joinfields(hdr,'\n'), data))
    total.append('--%s\n' % boundary)
    total.append(joinfields(part, "\n--%s\n" % boundary))
    total.append('\n--%s--\n' % boundary)
    query = joinfields(total, '')

    contentType = 'multipart/form-data; boundary=%s' % boundary
    contentLength = str(len(query))

    headers = {'Accept'           : '*/*',
               'Proxy-Connection' : 'Keep-Alive',
               'Content-Type'     : contentType,
               'Content-Length'   : contentLength}

    req = urllib2.Request('http://'+host+':'+port+uri, query, headers)
    response = urllib2.urlopen(req)
    html = response.read()



##############################################################################
#
# uploader
#
##############################################################################

class Uploader(Thread):
    
    def run(self):

        basedir = get_basedir()
        
        join = os.path.join
        
        logger = logging.getLogger("mnemosyne")
    
        # Find out which files haven't been uploaded yet.

        dir = os.listdir(unicode(join(basedir, "history")))
        history_files = [x for x in dir if x[-4:] == ".bz2"]
    
        uploaded = None
        try:
            upload_log = file(join(basedir, "history", "uploaded"))
            uploaded = [x.strip() for x in upload_log]
            upload_log.close()
        except:
            uploaded = []

        to_upload = sets.Set(history_files) - sets.Set(uploaded)

        if len(to_upload) == 0:
            return

        # Upload them to our server.

        upload_log = file(join(basedir, "history", "uploaded"), 'a')

        try:
            for f in to_upload:
                print "Uploading", f, "...",
                filename = join(basedir, "history", f)
                upload(filename)
                print >> upload_log, f
                logger.info("Uploaded %s" % f)
                print "done!"           
        except:
            logger.info("Uploading failed")
            traceback.print_exc()

        upload_log.close()



##############################################################################
#
# start_logging
#
#  Note: using logging.basisConfig could result in simpler code here, but
#  then the log file is empty on the very first program invocation.
#  This is probably a Python bug.
#
##############################################################################

def start_logging():

    basedir = get_basedir()

    log_name = os.path.join(basedir, "log.txt")

    logger = logging.getLogger("mnemosyne")

    if get_config("keep_logs") == True:
        logger.setLevel(logging.INFO)
    else:
        logger.setLevel(logging.ERROR)  

    fh = logging.FileHandler(log_name)

    formatter = logging.Formatter("%(asctime)s %(message)s",
                                  "%Y-%m-%d %H:%M:%S :")
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    #logging.basicConfig(level=logging.INFO,
    #                    format="%(asctime)s %(message)s",
    #                    datefmt="%Y-%m-%d %H:%M:%S :",
    #                    filename=log_name)


##############################################################################
#
# update_logging_status
#
##############################################################################

def update_logging_status():
    
    logger = logging.getLogger("mnemosyne")
    if get_config("keep_logs") == True:
        logger.setLevel(logging.INFO)
        logger.info("Logging turned on")
    else:
        logger.info("Logging turned off")
        logger.setLevel(logging.ERROR)   
    
