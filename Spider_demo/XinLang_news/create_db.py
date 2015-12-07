#coding=utf-8

import sys

import MySQLdb

##2014/04/25修改了qq、cell类型
##qq bigint(20) DEFAULT NULL,
##cell bigint(20) DEFAULT NULL,
##

server_post_sql = """  CREATE TABLE %s (
                      `id` varchar(255) NOT NULL,
                      `url` varchar(255) DEFAULT NULL,
                      `board` varchar(64) DEFAULT NULL,
                      `site_id` varchar(64) DEFAULT NULL,
                      `data_type` tinyint(11) DEFAULT NULL,
                      `title` varchar(255) DEFAULT NULL,
                      `content` text,
                      `post_time` datetime DEFAULT NULL,
                      `scratch_time` datetime DEFAULT NULL,
                      `poster_name` varchar(64) DEFAULT NULL,
                      `poster_id` int(15) DEFAULT NULL,
                      `poster_url` varchar(255) DEFAULT NULL,
                      `poster_pic_url` varchar(255) DEFAULT NULL,
                      `read_num` int(11) DEFAULT NULL,
                      `comment_num` int(11) DEFAULT NULL,
                      `repost_num` int(11) DEFAULT NULL,
                      `language_type` int(11) DEFAULT '0',
                      `image_url` varchar(255) DEFAULT NULL,
                      `thread_content` mediumblob,
                      `is_read` tinyint(4) unsigned DEFAULT '0',
                      `repost_post_id` varchar(255) DEFAULT NULL,
                      `text_type` tinyint(3) unsigned  DEFAULT '0',
                      PRIMARY KEY (`id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
                    """
                       
def main():
    if len(sys.argv) == 2:
        conn = MySQLdb.connect(host="127.0.0.1", db="yuqing", user="root",
                    passwd="minus")
        #conn = MySQLdb.connect(host="1.85.37.139", db="yq", user="root",
        #            passwd="QAZ))#@%@2012")
        cursor = conn.cursor()
        date1 = sys.argv[1]
        table_name = date1
        print table_name
        #print (server_post_sql %table_name)
        cursor.execute(server_post_sql %table_name)
        cursor.close()
        conn.close()
    else:
        print "invalid parameters \
               create_db type id"
    

if __name__ == "__main__":
    main()
    
