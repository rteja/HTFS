#!/usr/bin/env python3

import os
import sys
import logging

import inotify.adapters
import TagfsUtilities

logging.basicConfig(level='INFO')
logobj = logging.getLogger(__name__)

def _tagfs_track_resource_changes(tag_boundary_path) :    
    i = inotify.adapters.InotifyTree(tag_boundary_path)
    logobj.info("inode tracking on path: %s" % tag_boundary_path)
    th_utils = TagfsUtilities.TagfsTagHandlerUtilities(tag_boundary_path)

    eventlist = []
    for event in i.event_gen(yield_nones=False) :
        (ievent, type_names, path, filename) = event
        path = os.path.join(path, filename)
        if type_names.count('IN_MOVED_FROM') :
            originalpath = path
            tracked = th_utils.is_resource_tracked(originalpath)
            if not tracked : 
                continue
            eventlist.append((ievent.cookie, 'MOVED', originalpath))
        elif type_names.count('IN_MOVED_TO') :    
            for e in eventlist :
                event_cookie = e[0]
                movedpath = path
                if event_cookie == ievent.cookie :
                    originalpath = e[2]
                    th_utils.move_resource(originalpath, movedpath)
                    logobj.info("%s -> %s" % (originalpath, movedpath))
                    eventlist.remove(e)

if __name__ == '__main__' :
    if len(sys.argv) > 1 :
        _tagfs_track_resource_changes(sys.argv[1])
    else :
        _tagfs_track_resource_changes(TagfsUtilities.get_tag_fs_boundary())
