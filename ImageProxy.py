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
        self.original_fname = fname
    
    @property
    def DateTimeOriginal(self):
        if self.dt_original is None:
            exiftime = self.tags['EXIF DateTimeOriginal'].values
            self.dt_original = parse_exif_time(exiftime)
        return self.dt_original
        
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
            