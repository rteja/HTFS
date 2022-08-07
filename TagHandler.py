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
    def getTagId(self, tag_name) -> int:
        query_str = "SELECT ID FROM TAGS WHERE TAGNAME='" + tag_name + "';"
        res = self.conn.execute(query_str)
        r = res.fetchone()
        tid = -1
        if r != None :
            tid = r[0]
        return tid

    def getTagName(self, tag_id) -> str:
        query_str = "SELECT TAGNAME FROM TAGS WHERE ID=" + str(tag_id) + ";"
        res = self.conn.execute(query_str)
        r = res.fetchone()
        tag_name = ""
        if r != None :
            tag_name = str(r[0])
        return tag_name
    
    def getTagList(self) -> list:
        query_str = "SELECT TAGNAME FROM TAGS WHERE ID > 0;"
        res = self.conn.execute(query_str)
        taglist = []
        for r in res :
            taglist.append(r[0])
        return taglist

    def addTag(self, tag_name) -> int :
        tag_exists = self.getTagId(tag_name)
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

    def linkTag(self, tag_name, tag_parent_name) :
        src_tag_id = self.getTagId(tag_name)
        parent_tag_id = self.getTagId(tag_parent_name)
        if (src_tag_id < 0 | parent_tag_id < 0) :
            if src_tag_id < 0 :
                logobj.error("tags not in db")
            return False
        query_str = "INSERT INTO TAGLINKS VALUES (" + str(src_tag_id) + "," + str(parent_tag_id) + ");"
        self.conn.execute(query_str)
        self.conn.commit()
        return True

    def getParentTagsById(self, tag_id) -> list :
        query_str = "SELECT TAGPARENTID FROM TAGLINKS WHERE TAGID=" + str(tag_id) + ";"
        res = self.conn.execute(query_str)
        parent_ids = []
        for r in res :
            parent_ids.append(r[0])
        return parent_ids

    def getParentTags(self, tag_name) -> list :
        tag_id = self.getTagId(tag_name)
        parent_ids = self.getParentTagsById(tag_id)
        parent_tags = map(self.getTagName, parent_ids)
        return list(parent_tags)

    def getChildTagsById(self, tag_id) -> list :
        query_str = "SELECT TAGID FROM TAGLINKS WHERE TAGPARENTID=" + str(tag_id) + ";"
        res = self.conn.execute(query_str)
        child_ids = []
        for r in res :
            child_ids.append(r[0])
        return child_ids

    def getChildTags(self, tag_name) -> list :
        tag_id = self.getTagId(tag_name)
        child_ids = self.getChildTagsById(tag_id)
        child_tags = map(self.getTagName, child_ids)
        return list(child_tags)

    def getDownstreamTagsById(self, tag_id) -> list :
        traverse_ids = [tag_id]
        downstream_ids = []
        visited_ids = set()
        while (len(traverse_ids) > 0) :
            node_id = traverse_ids.pop(0)
            if node_id in visited_ids :
                continue
            visited_ids.add(node_id)
            child_ids = self.getChildTagsById(node_id)
            for cid in child_ids :
                downstream_ids.append(cid)
                traverse_ids.append(cid)
        return downstream_ids

    def getDownstreamTags(self, tag_name) -> list :
        tag_id = self.getTagId(tag_name)
        downstream_tagids = self.getDownstreamTagsById(tag_id)
        downstream_tags = map(self.getTagName, downstream_tagids)
        return list(downstream_tags)
    
    def getTagClosure(self, tags) :
        tags_closure = []
        for tag in tags :
            tags_closure.append(tag)
            downstreamtags = self.getDownstreamTags(tag)
            for dtag in downstreamtags :
                tags_closure.append(dtag)
        tags_closure = list(set(tags_closure))
        return tags_closure

    def addResource(self, resourceurl) :
        res = self.conn.execute("SELECT max(ID) FROM RESOURCES;")
        r = res.fetchone()
        max_res_id = 0
        if r != None :
            max_res_id = r[0]
        new_res_id = max_res_id + 1
        query_str = "INSERT INTO RESOURCES VALUES (" + str(new_res_id) +  ",\"" + resourceurl + "\")"        
        self.conn.execute(query_str)
        self.conn.commit()
        return new_res_id

    def getResourceUrl(self, res_id) :
        query_str = "SELECT URL FROM RESOURCES WHERE ID=" + str(res_id)+ ";"
        res = self.conn.execute(query_str)
        r = res.fetchone()
        url = ""
        if r != None :
            url = r[0]
        return url

    def getResourceId(self, resourceurl) :
        query_str = "SELECT ID FROM RESOURCES WHERE URL=\"" + resourceurl + "\";"
        res = self.conn.execute(query_str)
        r = res.fetchone()
        res_id = -1
        if r != None :
            res_id = r[0]
        return res_id
 
    def getResourceTagsById(self, resource_id) -> list :
        query_str = "SELECT TAGID FROM RESOURCELINKS WHERE RESID=" + str(resource_id) + ";"
        res = self.conn.execute(query_str)
        tag_ids = []
        for r in res :            
            tag_ids.append(r[0])
        return tag_ids 

    def addResourceTagById(self, resource_id, tag_id) :
        current_tags = self.getResourceTagsById(resource_id)
        if current_tags.count(tag_id) == 0 :
            query_str = "INSERT INTO RESOURCELINKS VALUES (" + str(resource_id) + "," + str(tag_id) + ");"
            self.conn.execute(query_str)
            self.conn.commit()
        
    def delResourceTagById(self, resource_id, tag_id) :
        current_tags = self.getResourceTagsById(resource_id)
        if current_tags.count(tag_id) > 0 :
            query_str = "DELETE FROM RESOURCELINKS WHERE RESID=" + str(resource_id) + " AND TAGID=" + str(tag_id) + ";"
            self.conn.execute(query_str)
            self.conn.commit()
    
    def delResourceTags(self, resourceurl, tags) :
        res_id = self.getResourceId(resourceurl)
        tag_ids = list(map(self.getTagId, tags))
        for tid in tag_ids :
            self.delResourceTagById(res_id, tid)
        
    def addResourceTags(self, resourceurl, tags) :
        res_id = self.getResourceId(resourceurl)
        unsuccessful_tags = []
        for tag in tags :
            tag_id = self.getTagId(tag)
            if tag_id > 0 :
                self.addResourceTagById(res_id, tag_id)
            else :
                unsuccessful_tags.append(tag)
        return unsuccessful_tags

    def getResourceTags(self, resourceurl) :
        res_id = self.getResourceId(resourceurl)
        tag_ids = self.getResourceTagsById(res_id)
        return list(map(self.getTagName, tag_ids))

    def getResourcesByTagId(self, tag_ids) :
        resource_ids = []
        for tid in tag_ids :
            query_str = "SELECT RESID FROM RESOURCELINKS WHERE TAGID=" + str(tid) + ";"
            res = self.conn.execute(query_str)
            for r in res :
                resource_ids.append(r[0])
        resource_ids = list(set(resource_ids))
        return resource_ids    

    def getResourcesByTag(self, tags) :
        tag_ids = list(map(self.getTagId, tags))
        res_ids = self.getResourcesByTagId(tag_ids)
        res = list(map(self.getResourceUrl, res_ids))
        return res


def test():
    print("Initializing db..")
    testdb = "testdb.db"
    if os.path.exists(testdb) :
        os.remove(testdb)
    th = TagHandler('testdb.db')
    th.addTag("eresources")
    th.addTag("books")
    th.addTag("articles")
    th.addTag("researchpaper")
    th.linkTag("books", "eresources")
    th.linkTag("articles", "eresources")
    th.linkTag("researchpaper", "articles")

    th.addTag("topics")
    th.addTag("mathematics")
    th.addTag("appliedmathematics")
    th.addTag("calculus")
    th.addTag("physics")
    th.linkTag("mathematics", "topics")
    th.linkTag("physics", "topics")
    th.linkTag("appliedmathematics", "mathematics")
    th.linkTag("calculus", "mathematics")

    pids = th.getParentTags("articles")
    print(pids)
    tid = th.getTagId("books")
    print(tid)
    tname = th.getTagName(tid)
    print(tname)
    cids = th.getChildTags("eresources")
    print(cids)
    dids = th.getDownstreamTags("eresources")
    print(dids)
    dids = th.getDownstreamTags("topics")
    print(dids)

    res_path = "/this/is/dummy/path"
    th.addResource(res_path)
    rid = th.getResourceId(res_path)
    print(rid)
    th.addResourceTags(res_path, ["books", "calculus"])
    tags = th.getResourceTags(res_path)
    print(tags)


if __name__ == '__main__':
    test()