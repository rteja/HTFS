#!/usr/bin/env python3

import os
import resource
import sys
from turtle import down
import TagHandler

_tagfsdb = ".tagfs.db"

def initTagFs():
    th = TagHandler.TagHandler(_tagfsdb)
    s = "TAGFS: initialized in " + os.path.realpath(os.curdir)
    print(s)

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
        tag_fs_db_file = tag_fs_db_file_path + tag_fs_db_file

def getRelativePath(url, base_path) :
    return os.path.relpath(url, base_path)

def getTagDB() :
    tag_boundary = getTagFsBoundary()
    if tag_boundary == None :
        print("TAGFS: not initalized")
        exit(1)
    tagdb = tag_boundary + "/" + _tagfsdb
    return tagdb

def getTagClosure(tags) :
    th = TagHandler.TagHandler(getTagDB())
    tags_closure = []
    for tag in tags :
        tags_closure.append(tag)
        downstreamtags = th.getDownstreamTags(tag)
        for dtag in downstreamtags :
            tags_closure.append(dtag)
    tags_closure = list(set(tags_closure))
    return tags_closure

def getTagList(tags) :
    taglist = []
    th = TagHandler.TagHandler(getTagDB())
    if len(tags) == 0 :
        taglist = th.getTagList()
    else :
        taglist = getTagClosure(tags)

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
        print("TAGFS: following tags not in db " + str(unsuccessful_tags))

def getResourcesByTag(tags) :
    tags_closure = getTagClosure(tags)
    th = TagHandler.TagHandler(getTagDB())
    resource_urls = th.getResourcesByTag(tags_closure)
    for res in resource_urls :
        print(fullUrl(res))

def linkTags(tag, parent_tag) :
    th = TagHandler.TagHandler(getTagDB())
    th.linkTag(tag, parent_tag)


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


def tagfs(arg) :
    if len(arg) == 0 :
        printUsage()
        exit(1)

    if arg[0] == "init" :
        initTagFs()
    elif arg[0] == "getboundary" :
        bdr = getTagFsBoundary()
        if bdr != None :
            print(bdr)
        else :
            print("TAGFS: not initialized")
    elif arg[0] == "lstags" :
        getTagList(arg[1:])
    elif arg[0] == "addtags" :
        addTags(arg[1:])
    elif arg[0] == "linktags" :
        linkTags(arg[1], arg[2])
        print("TAGFS: " + arg[1] + " ---> " + arg[2])
    elif arg[0] == "unlinktags" :
        print("TAGFS: Unimplemented feature")
        exit(1)
    elif arg[0] == "addresource" :
        addResource(arg[1])
    elif arg[0] == "tagresource" :
        tagResource(arg[1], arg[2:])
    elif arg[0] == "lsresources" :
        getResourcesByTag(arg[1:])
    elif arg[0] == "help" :
        printUsage()
    else :
        print("TAGFS: Unknown input")
        printUsage()
        exit(1)
    exit(0)

if __name__ == "__main__" :
    tagfs(sys.argv[1:])
