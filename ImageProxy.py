#!/usr/bin/env python
#
#  ImageProxy.py
#  Pyview
#
#  Created by spirux on 28/03/2009.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.
#

import EXIF
import datetime
import os
from os.path import basename
import stat

def parse_exif_time(timestring, format = '%Y:%m:%d %H:%M:%S'):
    return datetime.datetime.strptime(timestring, format)

class ImageProxy(object):
    def __init__(self, fname, stop_tag = None):
        named = {'details':False}
        if stop_tag: named['stop_tag'] = stop_tag
        file = open(fname,'rb')
        #Initialize members
        self.tags = EXIF.process_file(file, **named)
        self.dt_original = None
        self.originalFileName = fname
        
        #some attributes for the outline view
        self.name = basename(fname)
    
    @property
    def DateTimeOriginal(self):
        if self.dt_original is None:
            try:
                exiftime = self.tags['EXIF DateTimeOriginal'].values
                self.dt_original = parse_exif_time(exiftime)
            except KeyError:
                # fallback to file creation time
                creation_time = os.stat(self.originalFileName)[stat.ST_CTIME]
                self.dt_original = datetime.fromtimestamp(creation_time)
        return self.dt_original
        
    date = DateTimeOriginal
        
    def human_readable_tags(self):
        lines = []
        for tag in self.tags.keys():
            if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'EXIF MakerNote'):
                lines.append(': '.join( (tag, str(self.tags[tag])) ))
        return '\n'.join(lines)
        

# To stop processing after a certain tag is retrieved,
# pass the -t TAG or --stop-tag TAG argument, or as
#    tags = EXIF.process_file(f, stop_tag='TAG')

#if __name__ = '__main__':
#    i = ImageProxy(r'/Users/spirux/Desktop/100NCD40/DSC_1820.JPG')
#    print (i.DateTimeOriginal + datetime.timedelta(1)).isoformat()
#    print i.DateTimeOriginal.isoformat()
#    print i.human_readable_tags()
            