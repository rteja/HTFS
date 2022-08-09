import os
import TagHandler

def test():
    print("Initializing db..")
    testdb = "testdb.db"
    if os.path.exists(testdb) :
        os.remove(testdb)
    th = TagHandler.TagHandler('testdb.db')
    th.add_tag("eresources")
    th.add_tag("books")
    th.add_tag("articles")
    th.add_tag("researchpaper")
    th.link_tag("books", "eresources")
    th.link_tag("articles", "eresources")
    th.link_tag("researchpaper", "articles")

    th.add_tag("topics")
    th.add_tag("mathematics")
    th.add_tag("appliedmathematics")
    th.add_tag("calculus")
    th.add_tag("physics")
    th.link_tag("mathematics", "topics")
    th.link_tag("physics", "topics")
    th.link_tag("appliedmathematics", "mathematics")
    th.link_tag("calculus", "mathematics")

    pids = th.get_parent_tags("articles")
    print(pids)
    tid = th.get_tag_id("books")
    print(tid)
    tname = th.get_tag_name(tid)
    print(tname)
    cids = th.get_child_tags("eresources")
    print(cids)
    dids = th.get_downstream_tags("eresources")
    print(dids)
    dids = th.get_downstream_tags("topics")
    print(dids)

    res_path = "/this/is/dummy/path"
    th.addResource(res_path)
    rid = th.get_resource_id(res_path)
    print(rid)
    th.add_resource_tags(res_path, ["books", "calculus"])
    tags = th.get_resource_tags(res_path)
    print(tags)
