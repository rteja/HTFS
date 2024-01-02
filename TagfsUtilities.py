import os
import re
import logging

import TagHandler
import QueryEvaluator

_tagfsdb = ".tagfs.db"

logging.basicConfig(level='INFO')
logobj = logging.getLogger(__name__)

def normalize_url(resource_url) :
    tag_boundary = get_tag_fs_boundary()
    normalized_url = get_relative_path(os.path.realpath(resource_url), tag_boundary)
    normalized_url = normalized_url.replace("\\","/")
    return normalized_url

def get_tag_fs_boundary() :
    tag_fs_db_file = _tagfsdb
    tag_fs_db_file_path = ""
    while True :
        if os.path.exists(tag_fs_db_file) :
            return os.path.realpath(tag_fs_db_file_path)
        else :
            realpath = os.path.realpath(tag_fs_db_file_path)
            if realpath == "/" :
                return None
            elif re.fullmatch("[A-Z]:\\\\", realpath) :
                return None
        tag_fs_db_file_path = os.path.pardir + os.path.sep + tag_fs_db_file_path
        tag_fs_db_file = tag_fs_db_file_path + _tagfsdb

def full_url(normzlied_resource_url) :
    url = os.path.join(get_tag_fs_boundary(), normzlied_resource_url)
    return url

def get_relative_path(url, base_path) :
    return os.path.relpath(url, base_path)

def get_tags_db() :
    tag_boundary = get_tag_fs_boundary()
    if tag_boundary == None :
        logobj.error("db not initialized")
        exit(1)
    tagdb = os.path.join(tag_boundary, _tagfsdb)
    return tagdb

def is_hierarchial_tag(tag) :
    if tag.find('/') == -1 :
        return True
    return False

def get_hierarchical_tag_split(tag) :
    atomic_tags = tag.split('/')
    return atomic_tags

class TagfsTagHandlerUtilities :
    def __init__(self, tagfs_boundary) :
        self.tagfs_boundary = tagfs_boundary
        tagsdb_file_path = os.path.join(tagfs_boundary, _tagfsdb)
        self.th = TagHandler.TagHandler(tagsdb_file_path)

    def get_tags_list(self, tags) :
        taglist = []
        if len(tags) == 0 :
            taglist = self.th.get_tag_list()
        else :
            taglist = self.th.get_tag_closure(tags)
        return taglist
        
    def add_tags(self, tags) :
        added_tags = []
        for tag in tags :
            htags = get_hierarchical_tag_split(tag);            
            prev_tag = htags[0]
            assert(len(prev_tag) != 0)
            is_new_tag = self.th.add_tag(prev_tag)
            if is_new_tag :
                added_tags.append(prev_tag)
            for i in range(1,len(htags)) :
                cur_tag = htags[i]
                is_new_tag = self.th.add_tag(cur_tag)
                if is_new_tag :
                    added_tags.append(cur_tag)
                self.th.link_tag(cur_tag, prev_tag)            
        return added_tags

    def rename_tag(self, tag_name, new_tag_name) :
        res = self.th.rename_tag(tag_name, new_tag_name)
        return res

    def add_resource(self, resource_url) :
        resource_url = normalize_url(resource_url)
        rid = self.th.get_resource_id(resource_url)
        if rid == -1 :
            rid = self.th.add_resource(resource_url)
        return rid

    def is_resource_tracked(self, resource_url) :
        resource_url = normalize_url(resource_url)
        rid = self.th.get_resource_id(resource_url)
        return (rid > 0)

    def del_resource(self, resource_url) :
        resource_url = normalize_url(resource_url)
        self.th.del_resource(resource_url)

    def tag_resource(self, resource_url, tags) :
        resource_url = normalize_url(resource_url)
        unsuccessful_tags = self.th.add_resource_tags(resource_url, tags)
        return unsuccessful_tags

    def untag_resource(self, resource_url, tags) :
        resource_url = normalize_url(resource_url)
        self.th.del_resource_tags(resource_url, tags)

    def move_resource(self, resource_url, target_url) :
        # validate if target_url falls under the same tagfs hierarchy
        resource_url = normalize_url(resource_url)
        target_url = normalize_url(target_url)
        self.th.update_resource_url(resource_url, target_url)

    def update_resource_sub_url(self, resource_url, update_url) :
        resource_url = normalize_url(resource_url)
        update_url = normalize_url(update_url)
        self.th.update_resource_sub_url(resource_url, update_url)
        
    def get_resources_by_tag(self, tags) :
        tags_closure = self.th.get_tag_closure(tags)
        resource_urls = self.th.get_resources_by_tag(tags_closure)
        resource_urls = list(map(full_url, resource_urls))
        return resource_urls
        
    def get_resources_by_tag_expr(self, tagsexpr) :
        qe = QueryEvaluator.QueryEvaluator(self.th)
        resource_urls = qe.evaluate_query(tagsexpr)
        resource_urls = list(map(full_url, resource_urls))
        return resource_urls

    def link_tags(self, tag, parent_tag) :
        res = self.th.link_tag(tag, parent_tag)
        return res

    def get_resource_tags(self, resource_url) :
        resource_url = normalize_url(resource_url)
        res_id = self.th.get_resource_id(resource_url)
        tags = []
        if res_id > 0 :
            tags = self.th.get_resource_tags(resource_url)
        return tags
