#!/usr/bin/env python
#
#  ImageProxy.py
#  Pyview
#
#  Created by spirux on 28/03/2009.
#  Copyright (c) 2009 __MyCompanyName__. All rights reserved.
#
import EXIF
from datetime import datetime, timedelta
import os, errno
from os.path import basename, isdir
import stat

accepted_extensions = ('jpg', 'jpeg', 'nef', 'cr2', 'dng', \
                    'tif', 'tiff', 'png', 'orf', 'crw', 'pef', \
                    'raw', 'mrw', 'rw2', 'x3f', 'raf', 'sr2', 'arw')

# these are replaced when found in the filename/path patterns by the return values
# of the associated functions, performed on the object at hand
replaceable_tokens = {
    '%date': lambda x:x.date.strftime("%Y_%m_%d"),
    '%filename': lambda x:x.name
}

# On the OS X platform, we will derive all classes from the NSObject
# to play better with the NSOutlineView control. For anything else,
# or when running as a standalone script, derive from "object".
ObjectBase = object
try:
    from Foundation import NSObject
    # Don't derive from NSObject when called directly
    if __name__ != '__main__':
        ObjectBase = NSObject
except ImportError:
    pass

def parse_exif_time(timestring, format = '%Y:%m:%d %H:%M:%S'):
    return datetime.strptime(timestring, format)

class ImageProxy(ObjectBase):
    isExpandable = False
    
    def __init__(self, fname, stop_tags = ()):
        #named arguments for EXIF.process_file
        named = {'details':False}
        if stop_tags: named['stop_tags'] = stop_tags
        file = open(fname,'rb')
        #Initialize members
        self.tags = EXIF.process_file(file, **named)
        self.dt_original = None
        self.originalFileName = fname
        
        #some attributes for the outline view
        self.name = basename(fname)
        
    def __str__(self):
        return  self.date.isoformat() + ": " + self.name
    
    @property
    def dateTimeOriginal(self):
        if self.dt_original is None:
            try:
                exiftime = self.tags['EXIF DateTimeOriginal'].values
                self.dt_original = parse_exif_time(exiftime)
            except KeyError:
                # fallback to file modification time
                mod_time = os.stat(self.originalFileName)[stat.ST_MTIME]
                self.dt_original = datetime.fromtimestamp(mod_time)
        return self.dt_original
        
    date = dateTimeOriginal
        
    def human_readable_tags(self):
        lines = []
        for tag in self.tags.keys():
            if tag not in ('JPEGThumbnail', 'TIFFThumbnail', 'EXIF MakerNote'):
                lines.append(': '.join( (tag, str(self.tags[tag])) ))
        return '\n'.join(lines)


class PhotoSession(ObjectBase):
    """
    A group of images or Photosessions. It also can hold some properties (keywords, comments, etc.)
    common for all its children
    """
    isExpandable = True
    def __init__(self):
        self._images = []
        self._name = None
        self._keywords = []
        self._comment = None
        self.consistent = False
    
    #TODO implement caching/maintenance of dates for better efficiency
    @property
    def startDate(self):
        if len(self._images):
            return min(self._images, key = lambda a:a.dateTimeOriginal).dateTimeOriginal
        return datetime.now()
    
    date = startDate
    
    @property
    def endDate(self):
        if len(self._images):
            return max(self._images, key = lambda a:a.dateTimeOriginal).dateTimeOriginal
        return datetime.now()
    
    def getName(self):
        if self._name is None:
            return self.date.strftime("Session-%y-%m-%d")
        return self._name
        
    def setName(self, name):
        self._name = name
    
    #access name as a property
    name = property(getName, setName)
    del setName, getName
    
    # defer the other attributes to the first object that we own
    def __getattr__(self, name):
        if self._images:
            return getattr(self._images[0], name)
        else:
            raise AttributeError("PhotoSession object contains no image to defer attribute access.")

    # we give a list-like interface for access to our contents 
    def append(self, image):
        return self._images.append(image)
    
    def insert(self, index, item):
        return self._images.insert(index, item)
    
    def remove(self, image):
        return self._images.remove(image)
    
    def __contains__(self, image):
        return image in self._images
        
    def __delitem__(self, itemno):
        return self._images.__delitem__(itemno)
        
    def __getitem__(self, itemno):
        return self._images[itemno]
        
    def __setitem__(self, itemno, val):
        self._images[itemno] = val
        
    def __iter__(self):
        return iter(self._images)
        
    def __len__(self):
        return len(self._images)
    
    def __str__(self):
        return "PhotoSession(" + self.name + ")"
    
    

def by_day(img, session, mindelta = timedelta(0)):
    """
    Groupping predicate. Groups each day in a different group.
    But don't start a new day ntil you find a gap longer than mindelta.
    """
    return session.date.date() == img.date.date() or (img.date - session.endDate) <= mindelta

def by_month(img, session, mindelta = timedelta(0)):
    ses_start = session.startDate
    ses_end = session.endDate
    return (ses_start.month == img.date.month and ses_start.year == img.date.year) \
        or (img.date - ses_end) <= mindelta

def by_timespan(img, session, mindelta = timedelta(0)):
    return (img.date - session.endDate) <= mindelta

def cluster_images(images, belongs_rule, sessionFactory = PhotoSession):
    """
    Cluster images in photo sessions and return a list of PhotoSessions
    """
    all_sessions = []
    s = None
    #examine objects in chronological order    
    for img in sorted(images, key = lambda a:a.date):
        # leave existing sessions unaltered
        if isinstance(img, PhotoSession):
            all_sessions.append(img)
            continue
        
        if s and belongs_rule(img, s):
            s.append(img)
        else:
            #open a new session
            s = sessionFactory()
            s.append(img)
            all_sessions.append(s)
            
    # TODO: implement optional session merging logic
    return all_sessions

def replace_tokens(pattern, obj, repl_tokens = replaceable_tokens):
    # perform replacements
    for token in repl_tokens:
        if pattern.find(token) >= 0:
            val = repl_tokens[token](obj)
            pattern = pattern.replace(token, val)

    #perform date related replacements, exactly like in strftime
    if isinstance(pattern, unicode):
        pattern = obj.date.strftime(pattern.encode('UTF-8')).decode('UTF-8')
    else:
        pattern = obj.date.strftime(pattern)
    return pattern

def pathOfSession(psession, basepath, root_basepath, pattern1, pattern2):
    """
    return the path corresponding to the PhotoSession at hand. The path must 
    be relative to basepath and is formed according to pattern1 if the basepath
    coincides with the root_basepath (level 0 photosessions), and according to 
    pattern2 in all other cases (inner photosessions)
    """
    pattern = pattern2
    if basepath == root_basepath:
        pattern = pattern1

    #do all possible token replacements on the pattern
    pattern = replace_tokens(pattern, psession, replaceable_tokens)
    return os.path.join(basepath, pattern)
    
def symlink_image(img, basepath, pattern = "%filename"):
    target = replace_tokens(pattern, img, replaceable_tokens)
    target = os.path.join(basepath, target)
    src = img.originalFileName
    print "linking", src, '->', target
    try:
        os.symlink(src, target)
    except Exception, ex:
        print ex
        return False

    return True
    

def store_image_tree(root, basepath, pathOfSession, imgProxyProcess):
    """
    Create the path structure and store the related images on disk.
    """
    groups = filter(lambda x: isinstance(x, PhotoSession), root)
    images = filter(lambda x: isinstance(x, ImageProxy), root)

    for image in images:
        imgProxyProcess(image, basepath)
    
    for group in groups:
        grouppath = pathOfSession(group, basepath)
        try:
            os.makedirs(grouppath)
        except OSError, ex:
            if ex.errno == errno.EEXIST:
                pass
            else:
                print ex
        if group:
            store_image_tree(group, grouppath, pathOfSession, imgProxyProcess)
    

def isLoadableFileType(fname):
    """
    Tests if the file under fname is loadable in an ImageProxy object
    """
    # Check the extension against known extensions
    extension = fname.split('.')[-1].lower()
    if not extension in accepted_extensions:
        return False
        
    # Check that the file can be opened
    try:
        open(fname)
    except OSError, ex:
        return False
    return True

def loadableFileNames(paths):
    "Locate a set of loadable filenames by recursively traversing all the directories in paths"
    #use a set to avoid possible duplicates
    picked_files = set()
    for d in paths:
        #handle non dirs
        if not isdir(d):
            if isLoadableFileType(d):
                picked_files.add(d)
            continue
        
        #walk directory and pick loadable files
        for root, dirs, files in os.walk(d):
            allfiles = (os.path.join(root, name) for name in files)
            for fname in filter(isLoadableFileType, allfiles):
                picked_files.add(fname)
    return picked_files
       
def count_images(tree):
    images = len(filter(lambda x: isinstance(x, ImageProxy), tree))
    for group in filter(lambda x: isinstance(x, PhotoSession), tree):
        images += count_images(group)
    return images

if __name__ == '__main__':
    import sys
    #load some images in ImageProxies
    filenames = loadableFileNames(sys.argv[1:])
    images = [ImageProxy(fname.strip(), stop_tags=('DateTimeOriginal',)) for fname in filenames]
    hours5 = timedelta(0, 5*3600, 0)
    print len(images), "images read"
    
    sessions = cluster_images(images, lambda s,m:by_day(s,m, hours5) )
    for ses in sessions:
        print "---- session start ----"
        for img in ses:
            print img

    root_basepath = r'/tmp/images'
    print "Creating hierarchy under", root_basepath
    sess_path = lambda ps, bp: pathOfSession(ps, bp, root_basepath, "%Y/%m - %B/%b%d", "%date")
    store_image_tree(sessions, root_basepath, sess_path, symlink_image)

