# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

class MysqlPipeline(object):
    def __init__(self):
        self.conn =None
        self.cur = None
    def open_spider(self,spider):
        # 初始化mysql链接
        self.conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='root',
            passwd='W1549983991',
            db='xpc',
            charset='utf8',
        )
        # 初始化游标对象
        self.cur = self.conn.cursor()
        


    def process_item(self,item,spider):
        if not hasattr(item,'table_name'):
            return item
        cols,values = zip(*item.items())
        sql = "INSERT INTO `%s`(%s)VALUES(%s)" %(item.table_name,','.join(cols),','.join(['%s'] * len(values)))
        self.cur.execute(sql,values)
        self.conn.commit()
        print(self.cur._last_executed)
        return item
    
    def close_spider(self,spider):
        self.cur.close()
        self.conn.close()