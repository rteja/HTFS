import os
import sqlite3
import logging


logobj = logging.getLogger(__name__)
class TagHandler() :
    def __init__(self, tagdb_file):
        self.tagdb = tagdb_file
        if not os.path.exists(self.tagdb):
            self.init()
        self.conn = sqlite3.connect(self.tagdb)
    
    def __del__(self):
        self.conn.close()

    def init(self) :
        self.conn = sqlite3.connect(self.tagdb)
        self.conn.execute('''CREATE TABLE TAGS
                        (ID INT PRIMARY KEY NOT NULL,
                        TAGNAME TEXT NOT NULL);''')
        self.conn.execute('''INSERT INTO TAGS
                        VALUES (0, 'dummy');''')
        self.conn.execute('''CREATE TABLE TAGLINKS
                        (TAGID INT NOT NULL,
                        TAGPARENTID INT NOT NULL);''')
        self.conn.execute('''INSERT INTO TAGLINKS
                        VALUES (0, 0);''')
        self.conn.execute('''CREATE TABLE RESOURCES
                        (ID INT PRIMARY KEY NOT NULL,
                        URL TEXT NOT NULL);''')
        self.conn.execute('''INSERT INTO RESOURCES
                        VALUES (0,"dummy");''')
        self.conn.execute('''CREATE TABLE RESOURCELINKS
                        (RESID INT NOT NULL, 
                        TAGID INT NOT NULL)''')
        self.conn.execute('''INSERT INTO RESOURCELINKS
                        VALUES (0,0);''')
        self.conn.commit()

    # can also be used to check if tag is valid
    def get_tag_id(self, tag_name) -> int:
        query_str = "SELECT ID FROM TAGS WHERE TAGNAME='" + tag_name + "';"
        res = self.conn.execute(query_str)
        r = res.fetchone()
        tid = -1
        if r != None :
            tid = r[0]
        return tid

    def get_tag_name(self, tag_id) -> str:
        query_str = "SELECT TAGNAME FROM TAGS WHERE ID=" + str(tag_id) + ";"
        res = self.conn.execute(query_str)
        r = res.fetchone()
        tag_name = ""
        if r != None :
            tag_name = str(r[0])
        return tag_name
    
    def get_tag_list(self) -> list:
        query_str = "SELECT TAGNAME FROM TAGS WHERE ID > 0;"
        res = self.conn.execute(query_str)
        taglist = []
        for r in res :
            taglist.append(r[0])
        return taglist

    def add_tag(self, tag_name) -> int :
        tag_exists = self.get_tag_id(tag_name)
        if tag_exists > 0 :
            return tag_exists
        res = self.conn.execute("SELECT max(ID) FROM TAGS;")
        r = res.fetchone()
        max_tag_id = r[0]
        new_tag_id = max_tag_id + 1
        query_str = "INSERT INTO TAGS VALUES (" + str(new_tag_id) + ",'" + tag_name + "');"
        self.conn.execute(query_str)
        self.conn.commit()
        return new_tag_id

    def link_tag(self, tag_name, tag_parent_name) :
        src_tag_id = self.get_tag_id(tag_name)
        parent_tag_id = self.get_tag_id(tag_parent_name)
        if (src_tag_id < 0 or parent_tag_id < 0) :
            if src_tag_id < 0 :
                logobj.error("tags not in db")
            return False
        query_str = "INSERT INTO TAGLINKS VALUES (" + str(src_tag_id) + "," + str(parent_tag_id) + ");"
        self.conn.execute(query_str)
        self.conn.commit()
        return True

    def get_parent_tags_by_id(self, tag_id) -> list :
        query_str = "SELECT TAGPARENTID FROM TAGLINKS WHERE TAGID=" + str(tag_id) + ";"
        res = self.conn.execute(query_str)
        parent_ids = []
        for r in res :
            parent_ids.append(r[0])
        return parent_ids

    def get_parent_tags(self, tag_name) -> list :
        tag_id = self.get_tag_id(tag_name)
        parent_ids = self.get_parent_tags_by_id(tag_id)
        parent_tags = map(self.get_tag_name, parent_ids)
        return list(parent_tags)

    def get_child_tags_by_id(self, tag_id) -> list :
        query_str = "SELECT TAGID FROM TAGLINKS WHERE TAGPARENTID=" + str(tag_id) + ";"
        res = self.conn.execute(query_str)
        child_ids = []
        for r in res :
            child_ids.append(r[0])
        return child_ids

    def get_child_tags(self, tag_name) -> list :
        tag_id = self.get_tag_id(tag_name)
        child_ids = self.get_child_tags_by_id(tag_id)
        child_tags = map(self.get_tag_name, child_ids)
        return list(child_tags)

    def get_downstream_tags_by_id(self, tag_id) -> list :
        traverse_ids = [tag_id]
        downstream_ids = []
        visited_ids = set()
        while (len(traverse_ids) > 0) :
            node_id = traverse_ids.pop(0)
            if node_id in visited_ids :
                continue
            visited_ids.add(node_id)
            child_ids = self.get_child_tags_by_id(node_id)
            for cid in child_ids :
                downstream_ids.append(cid)
                traverse_ids.append(cid)
        return downstream_ids

    def get_downstream_tags(self, tag_name) -> list :
        tag_id = self.get_tag_id(tag_name)
        downstream_tagids = self.get_downstream_tags_by_id(tag_id)
        downstream_tags = map(self.get_tag_name, downstream_tagids)
        return list(downstream_tags)
    
    def get_tag_closure(self, tags) :
        tags_closure = []
        for tag in tags :
            tagid = self.get_tag_id(tag)
            if tagid < 0 :
                logobj.warning("tag " + tag + " not present in the db")
                continue
            tags_closure.append(tag)
            downstreamtags = self.get_downstream_tags(tag)
            for dtag in downstreamtags :
                tags_closure.append(dtag)
        tags_closure = list(set(tags_closure))
        return tags_closure

    def add_resource(self, resource_url) :
        res = self.conn.execute("SELECT max(ID) FROM RESOURCES;")
        r = res.fetchone()
        max_res_id = 0
        if r != None :
            max_res_id = r[0]
        new_res_id = max_res_id + 1
        query_str = "INSERT INTO RESOURCES VALUES (" + str(new_res_id) +  ",\"" + resource_url + "\")"        
        self.conn.execute(query_str)
        self.conn.commit()
        return new_res_id

    def get_resource_ids(self) :
        res = self.conn.execute("SELECT ID FROM RESOURCES WHERE ID > 0;")
        tag_ids = []
        for r in res :
            tag_ids.append(r[0])
        return tag_ids

    def get_resource_url(self, res_id) :
        query_str = "SELECT URL FROM RESOURCES WHERE ID=" + str(res_id)+ ";"
        res = self.conn.execute(query_str)
        r = res.fetchone()
        url = ""
        if r != None :
            url = r[0]
        return url

    def update_resource_url(self, resource_url, new_resource_url) :
        res_id = self.get_resource_id(resource_url)
        if res_id < 0 :
            logobj.error("resource not tracked")
        query_str = "UPDATE RESOURCES SET URL=\"" + str(new_resource_url) + "\"" + " WHERE ID=" + str(res_id) + ";"
        self.conn.execute(query_str)
        self.conn.commit()


    def get_resource_id(self, resource_url) :
        query_str = "SELECT ID FROM RESOURCES WHERE URL=\"" + resource_url + "\";"
        res = self.conn.execute(query_str)
        r = res.fetchone()
        res_id = -1
        if r != None :
            res_id = r[0]
        return res_id
 
    def get_resource_tags_by_id(self, resource_id) -> list :
        query_str = "SELECT TAGID FROM RESOURCELINKS WHERE RESID=" + str(resource_id) + ";"
        res = self.conn.execute(query_str)
        tag_ids = []
        for r in res :            
            tag_ids.append(r[0])
        return tag_ids 
    
    def get_resource_tags(self , resource_url) -> list :
        res_id = self.get_resource_id(resource_url)
        tag_ids = self.get_resource_tags_by_id(res_id)
        return tag_ids

    def add_resource_tag_by_id(self, resource_id, tag_id) :
        current_tags = self.get_resource_tags_by_id(resource_id)
        if current_tags.count(tag_id) == 0 :
            query_str = "INSERT INTO RESOURCELINKS VALUES (" + str(resource_id) + "," + str(tag_id) + ");"
            self.conn.execute(query_str)
            self.conn.commit()
        else :
            logobj.warning("resource already has the tag")
        
    def del_resource_tags(self, resource_id) :
        query_str = "DELETE FROM RESOURCELINKS WHERE RESID=" + str(resource_id) + ";"
        self.conn.execute(query_str)
        self.conn.commit()
        
    def del_resource_tag_by_id(self, resource_id, tag_id) :
        current_tags = self.get_resource_tags_by_id(resource_id)
        if current_tags.count(tag_id) > 0 :
            query_str = "DELETE FROM RESOURCELINKS WHERE RESID=" + str(resource_id) + " AND TAGID=" + str(tag_id) + ";"
            self.conn.execute(query_str)
            self.conn.commit()

    def del_resource_tags(self, resource_url, tags) :
        res_id = self.get_resource_id(resource_url)
        if res_id < 0 :
            logobj.error("resource not tracked")
        tag_ids = list(map(self.get_tag_id, tags))
        for tid in tag_ids :
            if tid < 0 :
                logobj.error("tag not id db")
            self.del_resource_tag_by_id(res_id, tid)
        
    def add_resource_tags(self, resource_url, tags) :
        res_id = self.get_resource_id(resource_url)
        if res_id < 0 :
            logobj.error("resource not tracked")
        unsuccessful_tags = []
        for tag in tags :
            tag_id = self.get_tag_id(tag)
            if tag_id > 0 :
                self.add_resource_tag_by_id(res_id, tag_id)
            else :
                unsuccessful_tags.append(tag)
        return unsuccessful_tags

    def get_resource_tags(self, resource_url) :
        res_id = self.get_resource_id(resource_url)
        if res_id < 0 :
            logobj.error("resource not tracked")
        tag_ids = self.get_resource_tags_by_id(res_id)
        return list(map(self.get_tag_name, tag_ids))

    def get_resources_by_tag_id(self, tag_ids) :
        resource_ids = []
        for tid in tag_ids :
            query_str = "SELECT RESID FROM RESOURCELINKS WHERE TAGID=" + str(tid) + ";"
            res = self.conn.execute(query_str)
            for r in res :
                resource_ids.append(r[0])
        resource_ids = list(set(resource_ids))
        return resource_ids    

    def get_resources_by_tag(self, tags) :
        tag_ids = list(map(self.get_tag_id, tags))
        res_ids = self.get_resources_by_tag_id(tag_ids)
        res = list(map(self.get_resource_url, res_ids))
        return res

    def del_resource(self, resource_url) :
        res_id = self.get_resource_id(resource_url)
        if res_id < 0 :
            logobj.warning("resource not tracked")
            return
        self.del_resource_tags(res_id)
        query_str = "DELETE FROM RESOURCES WHERE ID=" + str(res_id) + ";"
        self.conn.execute(query_str)
        self.conn.commit()