#!/usr/bin/env python3

import os
import sys
import logging
import TagHandler
import QueryEvaluator

_tagfsdb = ".tagfs.db"

logging.basicConfig(level='INFO')
logobj = logging.getLogger(__name__)

def initTagFs():
    TagHandler.TagHandler(_tagfsdb)
    logobj.info("initialized in " + os.path.realpath(os.curdir))

def getTagFsBoundary() :
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

def getRelativePath(url, base_path) :
    return os.path.relpath(url, base_path)

def getTagDB() :
    tag_boundary = getTagFsBoundary()
    if tag_boundary == None :
        logobj.error("db not initialized")
        exit(1)
    tagdb = tag_boundary + "/" + _tagfsdb
    return tagdb

def getTagList(tags) :
    taglist = []
    th = TagHandler.TagHandler(getTagDB())
    if len(tags) == 0 :
        taglist = th.getTagList()
    else :
        taglist = th.getTagClosure(tags)
    for tag in taglist :
        print(tag)

def addTags(tags) :
    th = TagHandler.TagHandler(getTagDB())
    for tag in tags :
        th.addTag(tag)

def normalizeUrl(resource_url) :
    tagdb = getTagDB()
    tag_boundary = os.path.dirname(tagdb)
    normalized_url = getRelativePath(os.path.realpath(resource_url), tag_boundary)
    return normalized_url

def fullUrl(normzlied_resource_url) :
    url = getTagFsBoundary() + "/" + normzlied_resource_url
    return url
        
def addResource(resource_url) :
    th = TagHandler.TagHandler(getTagDB())
    resource_url = normalizeUrl(resource_url)
    rid = th.getResourceId(resource_url)
    if rid == -1 :
        rid = th.addResource(resource_url)
    return rid

def tagResource(resource_url, tags) :
    resource_url = normalizeUrl(resource_url)
    th = TagHandler.TagHandler(getTagDB())
    unsuccessful_tags = th.addResourceTags(resource_url, tags)
    if len(unsuccessful_tags) > 0 :
        logobj.warning("following tags not in db " + str(unsuccessful_tags))

def getResourcesByTag(tags) :
    th = TagHandler.TagHandler(getTagDB())
    tags_closure = th.getTagClosure(tags)
    resource_urls = th.getResourcesByTag(tags_closure)
    for res in resource_urls :
        print(fullUrl(res))
    
def getResourcesByTagExpr(tagsexpr) :
    qe = QueryEvaluator.QueryEvaluator(getTagDB())
    resource_urls = qe.evaluate_query(tagsexpr)
    for res in resource_urls :
        print(fullUrl(res))

def linkTags(tag, parent_tag) :
    th = TagHandler.TagHandler(getTagDB())
    res = th.linkTag(tag, parent_tag)
    if not res :
        logobj.error("invalid tags used.")

def printUsage():
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

def unimplementedFeatureError() :
    logobj.error("unimplemented feature")
    exit(1)

def tagfs(arg) :
    if len(arg) == 0 :
        printUsage()
        exit(1)

    if arg[0] == "init" :
        initTagFs()
    elif arg[0] == "getboundary" :
        bdr = getTagFsBoundary()
        if bdr == None :
            logobj.error("db not initialized")
            exit(1)
        print(bdr)
    elif arg[0] == "lstags" :
        getTagList(arg[1:])
    elif arg[0] == "addtags" :
        addTags(arg[1:])
    elif arg[0] == "linktags" :
        if len(arg) < 3 :
            logobj.error("improper usage")
            printUsage()
            exit(1)
        linkTags(arg[1], arg[2])
    elif arg[0] == "unlinktags" :
        unimplementedFeatureError()
    elif arg[0] == "addresource" :
        addResource(arg[1])
    elif arg[0] == "tagresource" :
        tagResource(arg[1], arg[2:])
    elif arg[0] == "lsresources" :
        #getResourcesByTag(arg[1:])
        getResourcesByTagExpr(arg[1])
    elif arg[0] == "rmresource" :
        unimplementedFeatureError()
    elif arg[0] == "help" :
        printUsage()
    else :
        logobj.error("unknown input")
        printUsage()
        exit(1)
    exit(0)

if __name__ == "__main__" :
    tagfs(sys.argv[1:])
