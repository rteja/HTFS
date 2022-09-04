#!/usr/bin/env python3

import os
import sys
import logging

import inotify.adapters
import TagfsUtilities

logging.basicConfig(level='INFO')
logobj = logging.getLogger(__name__)

def _tagfs_track_resource_changes(tag_boundary_path) :
    logobj.info("initializing inotify..")    
    i = inotify.adapters.InotifyTree(tag_boundary_path)
    logobj.info("inode tracking on path: %s" % tag_boundary_path)
    th_utils = TagfsUtilities.TagfsTagHandlerUtilities(tag_boundary_path)

    eventlist = []
    for event in i.event_gen(yield_nones=False) :
        (ievent, type_names, path, filename) = event
        #print("type_names: " + str(type_names) + "path: " + path + " filname: " + filename)
        path = os.path.join(path, filename)
        if type_names.count('IN_MOVED_FROM') :
            originalpath = path
            if (not type_names.count('IN_ISDIR')) : 
                tracked = th_utils.is_resource_tracked(originalpath)
                if not tracked :
                    continue
                eventlist.append((ievent.cookie, 'MF', originalpath))
            else :
                eventlist.append((ievent.cookie, 'MD', originalpath))
        elif type_names.count('IN_MOVED_TO') :
            for e in eventlist :
                event_cookie = e[0]
                dir_or_file = e[1]
                originalpath = e[2]
                movedpath = path
                # we have moved out of tracking zone and dont make any edits
                if not movedpath.startswith(tag_boundary_path) :
                    eventlist.remove(e)
                    continue
                if event_cookie == ievent.cookie :
                    if dir_or_file == 'MF' :
                        th_utils.move_resource(originalpath, movedpath)
                    else :
                        th_utils.update_resource_sub_url(originalpath, movedpath)
                    logobj.info("%s -> %s" % (originalpath, movedpath))
                    eventlist.remove(e)

if __name__ == '__main__' :
    if len(sys.argv) > 1 :
        _tagfs_track_resource_changes(sys.argv[1])
    else :
        _tagfs_track_resource_changes(TagfsUtilities.get_tag_fs_boundary())
