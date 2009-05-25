#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
from os.path import isfile, islink

def exiftool_read(filenames, exiftool = 'exiftool'):
    """
    Uses exiftool to read metadata from files. Generates tupples of (filename, metadata).
    Metadata are stored in a key-value form in a dictionary.
    """
    if not filenames: return
    p = subprocess.PIPE
    #read arguments from stdin
    argz = (exiftool, '-@', '-')
    # spawn exiftool and talk to it through pipes
    child = subprocess.Popen(argz, bufsize=512, executable=exiftool, stdin=p, stdout=p, universal_newlines=True)
    
    # send parameters through stdin
    parameters = ['-groupNames', '-fast', '-ignoreMinorErrors', '-short', '-unknown']
    plen = len(parameters)
    parameters.extend(filenames)
    for param in parameters:
        child.stdin.write(param + '\n')
    child.stdin.close()
    
    current = {}
    filename = parameters[plen]
    entries_separator = '======== '
    for line in child.stdout:
        # ignore empty lines and lines starting with space
        # such as: "    2 image files read"
        if not line or line[0].isspace():
            continue

        if line.startswith(entries_separator):
            # yield this entry and open new entry
            if current:
                yield (filename, current)
            skip = len(entries_separator)
            filename = line.strip('\n')[skip:]
            current = {}
            continue

        if not line.startswith('[') or not ':' in line:
            print "Warning: skipping ",  line.strip()
            continue

        # [EXIF] Orientation : Rotate 90 CW -> '[EXIF] Orientation' 'Rotate 90 CW'
        prop, val = (t.strip() for t in line.split(':', 1))
        # '[EXIF] Orientation' -> 'EXIF' 'Orientation'
        group, propname = prop.split(']', 1)
        propname = propname.strip()
        group = group[1:].strip()
        # 'EXIF:Orientation'
        prop = ":".join((group, propname))        
        # add property to dictionary
        current[prop] = val

    # Yield the last files properties
    if current:
        yield (filename, current)

    child.wait()
    if child.returncode != 0:
        print "warning: Exiftool returned with:", child.returncode

if __name__ == '__main__':
    files = (r'/Users/spirux/Desktop/DSC_3702.JPG',)
    import os.path
    for file, metadata in exiftool_read(files):
        print "-------", file, "-------"
        for key in metadata:
            print key, "=", metadata[key]
            