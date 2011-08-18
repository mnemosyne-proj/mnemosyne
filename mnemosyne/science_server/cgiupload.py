#!/usr/bin/env python

# Mnemosyne CGI upload server.
# Based on code by JeffBauer@bigfoot.com, Aaron Watters, Jim Fulton

import os, sys, traceback, cgi

class FileUploadAcquisition:
    
    def __init__(self):
        
        print "Content-type: text/html"
        print "Expires: Monday, 1-Jan-96 00:00:00 GMT"
        print "Pragma: no-cache"
        print
        sys.stderr = sys.stdout

        try:
            self.process()
        except:
            print "<pre>"
            traceback.print_exc()			
	
    def process(self):
        
        fs = cgi.FieldStorage()
        uf = fs["file"]

        filename = os.path.join("/home/mnemosyne", uf.filename)
        f = file(filename, "wb")
        while 1:
            line = uf.file.readline()
            if line:
                f.write(line)
            else:
                break
        f.close()


FileUploadAcquisition()	
