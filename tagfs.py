#!/usr/bin/env python3

import os
import sys
import logging
import TagHandler
import QueryEvaluator

_tagfsdb = ".tagfs.db"

logging.basicConfig(level='INFO')
logobj = logging.getLogger(__name__)

def init_tag_fs():
    TagHandler.TagHandler(_tagfsdb)
    logobj.info("initialized in " + os.path.realpath(os.curdir))

def get_tag_fs_boundary() :
    tag_fs_db_file = _tagfsdb
    tag_fs_db_file_path = ""
    while True :
        if os.path.exists(tag_fs_db_file) :
            return os.path.realpath(tag_fs_db_file_path)
        else :
            # this is os dependent -- reconsider this implementation
            if os.path.realpath(tag_fs_db_file_path) == "/" :
                return None
        tag_fs_db_file_path = os.path.pardir + "/" + tag_fs_db_file_path
        tag_fs_db_file = tag_fs_db_file_path + _tagfsdb

def get_relative_path(url, base_path) :
    return os.path.relpath(url, base_path)

def get_tags_db() :
    tag_boundary = get_tag_fs_boundary()
    if tag_boundary == None :
        logobj.error("db not initialized")
        exit(1)
    tagdb = tag_boundary + "/" + _tagfsdb
    return tagdb

def get_tags_list(tags) :
    taglist = []
    th = TagHandler.TagHandler(get_tags_db())
    if len(tags) == 0 :
        taglist = th.get_tag_list()
    else :
        taglist = th.get_tag_closure(tags)
    for tag in taglist :
        print(tag)

def add_tags(tags) :
    th = TagHandler.TagHandler(get_tags_db())
    for tag in tags :
        th.add_tag(tag)

def normalize_url(resource_url) :
    tagdb = get_tags_db()
    tag_boundary = os.path.dirname(tagdb)
    normalized_url = get_relative_path(os.path.realpath(resource_url), tag_boundary)
    normalized_url = normalized_url.replace("\\","/")
    return normalized_url

def full_url(normzlied_resource_url) :
    url = get_tag_fs_boundary() + "/" + normzlied_resource_url
    return url
        
def add_resource(resource_url) :
    th = TagHandler.TagHandler(get_tags_db())
    resource_url = normalize_url(resource_url)
    rid = th.get_resource_id(resource_url)
    if rid == -1 :
        rid = th.add_resource(resource_url)
    return rid

def tag_resource(resource_url, tags) :
    resource_url = normalize_url(resource_url)
    th = TagHandler.TagHandler(get_tags_db())
    unsuccessful_tags = th.add_resource_tags(resource_url, tags)
    if len(unsuccessful_tags) > 0 :
        logobj.warning("following tags not in db " + str(unsuccessful_tags))

def get_resources_by_tag(tags) :
    th = TagHandler.TagHandler(get_tags_db())
    tags_closure = th.get_tag_closure(tags)
    resource_urls = th.get_resources_by_tag(tags_closure)
    for res in resource_urls :
        print(full_url(res))
    
def get_resources_by_tag_expr(tagsexpr) :
    qe = QueryEvaluator.QueryEvaluator(get_tags_db())
    resource_urls = qe.evaluate_query(tagsexpr)
    for res in resource_urls :
        print(full_url(res))

def link_tags(tag, parent_tag) :
    th = TagHandler.TagHandler(get_tags_db())
    res = th.link_tag(tag, parent_tag)
    if not res :
        logobj.error("invalid tags used.")

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
        init_tag_fs()
    elif arg[0] == "getboundary" :
        bdr = get_tag_fs_boundary()
        if bdr == None :
            improper_usage()
        print(bdr)
    elif arg[0] == "lstags" :
        get_tags_list(arg[1:])
    elif arg[0] == "addtags" :
        add_tags(arg[1:])
    elif arg[0] == "linktags" :
        if len(arg) < 3 :
            improper_usage()
        link_tags(arg[1], arg[2])
    elif arg[0] == "unlinktags" :
        unimplemented_feature_error()
    elif arg[0] == "addresource" :
        add_resource(arg[1])
    elif arg[0] == "tagresource" :
        tag_resource(arg[1], arg[2:])
    elif arg[0] == "lsresources" :
        #get_resources_by_tag(arg[1:])
        get_resources_by_tag_expr(arg[1])
    elif arg[0] == "getresourcetags" :
        unimplemented_feature_error()
    elif arg[0] == "rmresource" :
        unimplemented_feature_error()
    elif arg[0] == "help" :
        print_usage()
    else :
        improper_usage()
    exit(0)

if __name__ == "__main__" :
    tagfs(sys.argv[1:])
