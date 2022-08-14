#!/usr/bin/env python3

import os
import sys
import shutil
import logging

import TagHandler
import TagfsUtilities

logging.basicConfig(level='INFO')
logobj = logging.getLogger(__name__)

def get_tagfs_utils() :
    tagfs_boundary = TagfsUtilities.get_tag_fs_boundary()
    if tagfs_boundary == None :
        logobj.error('db not initialized')
        print_usage()
        exit(1)
    th_utils = TagfsUtilities.TagfsTagHandlerUtilities(tagfs_boundary)
    return th_utils

def _get_tag_fs_boundary() :
    tagfs_boundary = TagfsUtilities.get_tag_fs_boundary()
    if tagfs_boundary == None :
        improper_usage()
    print(tagfs_boundary)
    exit(0)
    
def _init_tag_fs() :
    TagHandler.TagHandler(TagfsUtilities._tagfsdb)
    logobj.info("initialized in " + os.path.realpath(os.curdir))
    if not os.path.exists(TagfsUtilities._tagfsdb) :
        exit(0)
    exit(0)

def _get_tags_list(tags) :
    th_utils = get_tagfs_utils()
    tags_list = th_utils.get_tags_list(tags)
    for tag in tags_list :
        print(tag)
    exit(0)

def _add_tags(tags) :
    if len(tags) < 1 :
        improper_usage()
    th_utils = get_tagfs_utils()
    th_utils.add_tags(tags)
    exit(0)
            
def _add_resource(args) :
    if len(args) < 1 :
        improper_usage()
    resource_url = args[0]
    th_utils = get_tagfs_utils()
    th_utils.add_resource(resource_url)
    exit(0)

def _del_resource(args) :
    if len(args) < 1 :
        improper_usage()
    resource_url = args[0]
    th_utils = get_tagfs_utils()
    th_utils.del_resource(resource_url)
    exit(0)

def _tag_resource(args) :
    if len(args) < 2 :
        improper_usage()
    resource_url = args[0]
    tags = args[1]
    th_utils = get_tagfs_utils()
    unsuccessful_tags = th_utils.tag_resource(resource_url, tags)
    if len(unsuccessful_tags) > 0 :
        logobj.warning("following tags not in db " + str(unsuccessful_tags))
    exit(0)

def _move_resource(args) :
    if len(args) < 2 :
        improper_usage()
    resource_url = args[0]
    target_url = args[1]
    # validate if target_url falls under the same tagfs hierarchy
    src_is_file = os.path.isfile(resource_url)
    target_is_dir = os.path.isdir(target_url)
    if target_is_dir & src_is_file :
        target_url = target_url + os.sep + os.path.basename(resource_url)
    shutil.move(resource_url, target_url)
    th_utils = get_tagfs_utils()
    th_utils.move_resource(resource_url, target_url)
    exit(0)

def _get_resources_by_tag(tags) :
    th_utils = get_tagfs_utils()
    resource_urls = th_utils.get_resources_by_tag(tags)
    for res_url in resource_urls :
        print(res_url)
    exit(0)
    
def _get_resources_by_tag_expr(args) :
    if len(args) < 1 :
        improper_usage()
    tagsexpr = args[0]
    th_utils = get_tagfs_utils()
    resource_urls = th_utils.get_resources_by_tag_expr(tagsexpr)
    for res_url in resource_urls :
        print(res_url)
    exit(0)

def _link_tags(args) :
    if len(args) < 2 :
        improper_usage()
    tag = args[0]
    parent_tag = args[1]
    th_utils = get_tagfs_utils()
    res = th_utils.link_tags(tag, parent_tag)
    if not res :
        logobj.error("invalid tags used.")
        exit(1)
    exit(0)

def _get_resource_tags(args) :
    if len(args) != 1 :
        improper_usage()
    resource_url = args[0]
    th_utils = get_tagfs_utils()
    tags = th_utils.get_resource_tags(resource_url)
    for tag in tags :
        print(tag)
    exit(0)

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
        _get_tag_fs_boundary()
    elif arg[0] == "lstags" :
        _get_tags_list(arg[1:])
    elif arg[0] == "addtags" :
        _add_tags(arg[1:])
    elif arg[0] == "linktags" :
        _link_tags(arg[1:])
    elif arg[0] == "unlinktags" :
        unimplemented_feature_error()
    elif arg[0] == "addresource" :
        _add_resource(arg[1:])
    elif arg[0] == "tagresource" :
        _tag_resource(arg[1:])
    elif arg[0] == "updateresourceurl" :
        unimplemented_feature_error()
    elif arg[0] == "lsresources" :
        #get_resources_by_tag(arg[1:])
        _get_resources_by_tag_expr(arg[1:])
    elif arg[0] == "getresourcetags" :
        _get_resource_tags(arg[1:])
    elif arg[0] == "rmresourcetags" :
        unimplemented_feature_error()
    elif arg[0] == "rmresource" :
        _del_resource(arg[1:])
    elif arg[0] == "mvresource" :
        _move_resource(arg[1:])
    elif arg[0] == "sanitize" :
        #remove resources not present on filesystems
        unimplemented_feature_error()
    elif arg[0] == "help" :
        print_usage()
    else :
        improper_usage()

if __name__ == "__main__" :
    tagfs(sys.argv[1:])
