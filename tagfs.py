#!/usr/bin/env python3


import os
import sys
import shutil
import logging
import TagHandler
import QueryEvaluator
from TagfsUtilities import TagfsTagHandlerUtilities, get_tag_fs_boundary

_tagfsdb = ".tagfs.db"

logging.basicConfig(level='INFO')
logobj = logging.getLogger(__name__)

def _init_tag_fs():
    TagHandler.TagHandler(_tagfsdb)
    logobj.info("initialized in " + os.path.realpath(os.curdir))

def _get_tags_list(tags) :
    th_utils = TagfsTagHandlerUtilities(get_tag_fs_boundary())
    tags_list = th_utils.get_tags_list(tags)
    for tag in tags_list :
        print(tag)

def _add_tags(tags) :
    th_utils = TagfsTagHandlerUtilities(get_tag_fs_boundary())
    th_utils.add_tags(tags)
            
def _add_resource(resource_url) :
    th_utils = TagfsTagHandlerUtilities(get_tag_fs_boundary())
    th_utils.add_resource(resource_url)

def _del_resource(resource_url) :
    th_utils = TagfsTagHandlerUtilities(get_tag_fs_boundary())
    th_utils.del_resource(resource_url)

def _tag_resource(resource_url, tags) :
    th_utils = TagfsTagHandlerUtilities(get_tag_fs_boundary())
    unsuccessful_tags = th_utils.tag_resource(resource_url, tags)
    if len(unsuccessful_tags) > 0 :
        logobj.warning("following tags not in db " + str(unsuccessful_tags))

def _move_resource(resource_url, target_url) :
    # validate if target_url falls under the same tagfs hierarchy
    src_is_file = os.path.isfile(resource_url)
    target_is_dir = os.path.isdir(target_url)
    if target_is_dir & src_is_file :
        target_url = target_url + os.sep + os.path.basename(resource_url)
    shutil.move(resource_url, target_url)
    th_utils = TagfsTagHandlerUtilities(get_tag_fs_boundary())
    th_utils.move_resource(resource_url, target_url)

def full_url(normzlied_resource_url) :
    url = os.path.join(get_tag_fs_boundary(), normzlied_resource_url)
    return url

def _get_resources_by_tag(tags) :
    th_utils = TagfsTagHandlerUtilities(get_tag_fs_boundary())
    resource_urls = th_utils.get_resources_by_tag(tags)
    for res in resource_urls :
        print(full_url(res))
    
def _get_resources_by_tag_expr(tagsexpr) :
    th_utils = TagfsTagHandlerUtilities(get_tag_fs_boundary())
    resource_urls = th_utils.get_resources_by_tag_expr(tagsexpr)
    for res in resource_urls :
        print(full_url(res))

def _link_tags(tag, parent_tag) :
    th_utils = TagfsTagHandlerUtilities(get_tag_fs_boundary())
    res = th_utils.link_tags(tag, parent_tag)
    if not res :
        logobj.error("invalid tags used.")

def _get_resource_tags(resource_url) :
    th_utils = TagfsTagHandlerUtilities(get_tag_fs_boundary())
    tags = th_utils._get_resource_tags(resource_url)
    for tag in tags :
        print(tag)

def print_usage():
    print("HTFS: Hierarchially Tagged File System")
    cmd = "\t" + os.path.basename(sys.argv[0])
    print(cmd + " init \t\t initialize the tags db")
    print(cmd + " getboundary \t fs boundary starting which tags are tracked")
    print(cmd + " lstags \t\t list tags")
    print(cmd + " addtags \t\t add new tags")
    print(cmd + " linktags \t\t link existing tags")
    print(cmd + " addresource \t track a new resource")
    print(cmd + " tagresource \t add tags to tracked resources")
    print(cmd + " lsresources \t list resources with given tags")
    print(cmd + " getresourcetags \t list all the tags of the resource")
    print(cmd + " rmresource \t untrack the resource in the db")
    print(cmd + " mvresource \t move resource to a new path")

def unimplemented_feature_error() :
    logobj.error("unimplemented feature")
    exit(1)

def improper_usage() :
    logobj.error("improper usage")
    print_usage()
    exit(1)

def tagfs(arg) :
    if len(arg) == 0 :
        improper_usage()

    if arg[0] == "init" :
        _init_tag_fs()
    elif arg[0] == "getboundary" :
        bdr = get_tag_fs_boundary()
        if bdr == None :
            improper_usage()
        print(bdr)
    elif arg[0] == "lstags" :
        _get_tags_list(arg[1:])
    elif arg[0] == "addtags" :
        _add_tags(arg[1:])
    elif arg[0] == "linktags" :
        if len(arg) < 3 :
            improper_usage()
        _link_tags(arg[1], arg[2])
    elif arg[0] == "unlinktags" :
        unimplemented_feature_error()
    elif arg[0] == "addresource" :
        _add_resource(arg[1])
    elif arg[0] == "tagresource" :
        if len(arg) < 3 :
            improper_usage()
        _tag_resource(arg[1], arg[2:])
    elif arg[0] == "updateresourceurl" :
        unimplemented_feature_error()
    elif arg[0] == "lsresources" :
        #get_resources_by_tag(arg[1:])
        if len(arg) < 2 :
            improper_usage()
        _get_resources_by_tag_expr(arg[1])
    elif arg[0] == "getresourcetags" :
        if len(arg) < 2 :
            improper_usage()
        _get_resource_tags(arg[1])
    elif arg[0] == "rmresourcetags" :
        unimplemented_feature_error()
    elif arg[0] == "rmresource" :
        if len(arg) < 2:
            improper_usage()
        _del_resource(arg[1])
    elif arg[0] == "mvresource" :
        if len(arg) < 2 :
            improper_usage()
        _move_resource(arg[1], arg[2])
    elif arg[0] == "sanitize" :
        #remove resources not present on filesystems
        unimplemented_feature_error()
    elif arg[0] == "help" :
        print_usage()
    else :
        improper_usage()
    exit(0)

if __name__ == "__main__" :
    tagfs(sys.argv[1:])
