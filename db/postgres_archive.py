# -*- coding:utf-8 -*-
import os
import sys
import time
import re
import datetime
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import psycopg2.extras ##返回字典类型
from db_conf import *


class PostgresArchive:

    def __init__(self):
        #####统一配置参数，便于统一修改
        self.host = configs['host']
        self.user = configs['user']
        self.password = configs['password']
        self.port = configs['port']
        return
    
 
    ####默认查询到的是tuple数据类型，需要增加psycopg2.extras.RealDictCursor返回字典类型
    def search_db_table(self,database_name,table_name,condition_element):
        conn = psycopg2.connect(database=database_name, host=self.host, user=self.user, password=self.password, port=self.port)
        #cursor=conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        #cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor=conn.cursor()
        try:
            ####执行数据库语言
            #for key,value in config_element.items():
                #print (key,value)
                #sqlcmd='update %s (%s) values (%s)'%(table_name,key,value)
                #sqlcmd='update %s set %s = %s'%(table_name,key,value)
                #print (sqlcmd)
                #cursor.execute(sqlcmd)
                #break
            #cfg_kv = [(k, v) for k, v in config_element.items() if v is not None]
            cdt_kv = [(k, v) for k, v in condition_element.items() if v is not None]
            #print (cfg_kv)
            print (cdt_kv)
            
            #sqlcmd = 'UPDATE %s set (' % table_name + ', '.join(["%s ='%s'" % ([i[0] for i in ls],[i[1] for i in ls])) ');'
            #a = repr(j[1]) for j in ls
            #print (a)
            #sqlcmd = 'UPDATE %s set (' % table_name + ', '.join(["%s ='%s'" % ([i[0],repr(i[1]) for i in ls])) ');'
            #sqlcmd = 'UPDATE %s set '% table_name + ', '.join("%s ='%s'" % ('filename','sssssss.png')) ');
            sqlcmd = "SELECT * from %s "%table_name
            #sqlcmd += ", ".join(["%s='%s'" % key,vaule for f in zip(ls)])
            #sqlcmd += ", ".join(["%s='%s'" % f for f in (cfg_kv)])
            #sqlcmd += " WHERE id=1"    ##条件可以更加实际情况定
           
            if(len(cdt_kv)>1):
                sqlcmd += " WHERE "          ##条件可以更加实际情况定
                sqlcmd += "and ".join(["%s='%s'" % f for f in (cdt_kv)])
            elif(len(cdt_kv)==1):
                sqlcmd += " WHERE "          ##条件可以更加实际情况定
                sqlcmd += "".join(["%s='%s'" % f for f in (cdt_kv)])
                
            print (sqlcmd)
            cursor.execute(sqlcmd)
            
        except Exception as e:
            print (e)
            raise Exception(e)
            #exit()
            
        conn.commit()##一定要有conn.commit()这句来提交事务，要不然不能真正的插入数据        
        ####获取结果
        ####系统内置函数，默认返回元组类型，不方便调用
        #rs = cursor.fetchone()
        #rs = cursor.fetchall()
        
        ####获取表中所有字段
        coloumns = [row[0] for row in cursor.description]
        result = [[str(item) for item in row] for row in cursor.fetchall()]
        rs=[dict(zip(coloumns, row)) for row in result]
        #rs=dict(zip(coloumns, row)) for row in result

        conn.close()
        print ('search_db_table finished!')
        #print (rs)
        #input()
        
        ####[{}],取列表元素，即可去掉括号[]
        
        #return rs[0]##查询到1个dict可以获取[0]
        return rs    ##查询到多个就不行
    
    
    ####用户自己传入sql语句
    def search_db_table_usercmd(self,database_name,sqlcmd):
        conn = psycopg2.connect(database=database_name, host=self.host, user=self.user, password=self.password, port=self.port)
        cursor=conn.cursor()
        try:               
            # print (sqlcmd)
            cursor.execute(sqlcmd)
            
        except Exception as e:
            print (e)
            raise Exception(e)
            #exit()
            
        conn.commit()##一定要有conn.commit()这句来提交事务，要不然不能真正的插入数据
        
        ####获取表中所有字段
        coloumns = [row[0] for row in cursor.description]
        result = [[str(item) for item in row] for row in cursor.fetchall()]
        rs=[dict(zip(coloumns, row)) for row in result]

        ####获取结果
        conn.close()
        return rs

        
    def update_db_table(self,database_name,table_name,config_element,condition_element):
        conn = psycopg2.connect(database=database_name, host=self.host, user=self.user, password=self.password, port=self.port)
        cursor=conn.cursor()
        try:
            ####执行数据库语言
            #for key,value in config_element.items():
                #print (key,value)
                #sqlcmd='update %s (%s) values (%s)'%(table_name,key,value)
                #sqlcmd='update %s set %s = %s'%(table_name,key,value)
                #print (sqlcmd)
                #cursor.execute(sqlcmd)
                #break
            cfg_kv = [(k, v) for k, v in config_element.items() if v is not None]
            cdt_kv = [(k, v) for k, v in condition_element.items() if v is not None]
            print (cfg_kv)
            print (cdt_kv)
            
            #sqlcmd = 'UPDATE %s set (' % table_name + ', '.join(["%s ='%s'" % ([i[0] for i in ls],[i[1] for i in ls])) ');'
            #a = repr(j[1]) for j in ls
            #print (a)
            #sqlcmd = 'UPDATE %s set (' % table_name + ', '.join(["%s ='%s'" % ([i[0],repr(i[1]) for i in ls])) ');'
            #sqlcmd = 'UPDATE %s set '% table_name + ', '.join("%s ='%s'" % ('filename','sssssss.png')) ');
            sqlcmd = "UPDATE %s set "%table_name
            #sqlcmd += ", ".join(["%s='%s'" % key,vaule for f in zip(ls)])
            sqlcmd += ", ".join(["%s='%s'" % f for f in (cfg_kv)])
            #sqlcmd += " WHERE id=1"     ##条件可以更加实际情况定
            sqlcmd += " WHERE "          ##条件可以更加实际情况定
            if(len(cdt_kv)>1):
                sqlcmd += "and ".join(["%s='%s'" % f for f in (cdt_kv)])
            elif(len(cdt_kv)==1):
                sqlcmd += "".join(["%s='%s'" % f for f in (cdt_kv)])
                
            print (sqlcmd)
            cursor.execute(sqlcmd)
            
        except Exception as e:
            print (e)
            raise Exception(e)
            #exit()
        conn.commit()##一定要有conn.commit()这句来提交事务，要不然不能真正的插入数据
        conn.close()
        print ('update_db_table finished!')
    
    
    ####插入，主键自增
    def insert_db_table(self,database_name,table_name,config_element):
        conn = psycopg2.connect(database=database_name, host=self.host, user=self.user, password=self.password, port=self.port)
        cursor=conn.cursor()
        try:
            ####执行数据库语言
            #for key,value in config_element.items():
                #print (key,value)
                #sqlcmd='''insert into %s (%s,%s) values (%d,%s)'''%(table_name,'id',key,ID,value)
                ####ID自动增加，不需要管,insert 语句 是插入语句，不跟条件的
                #sqlcmd='insert into %s (%s) values (%s)' table_name,[key,'11']
                #sqlcmd='insert into %s (%s) values (%s) where id = %d'%(table_name,key,value,1)
                #sqlcmd='insert into %s (%s) values (%s)'%(table_name,key,value)
                #print (sqlcmd)
                #cursor.execute(sqlcmd)
                ##null value in column “id” violates not-null constraintDetail: Failing row contains (11110, 1, null),插入的主键Id为空引起的，检查一下 插入语句就好了
                #break
                
            ls = [(k, v) for k, v in config_element.items() if v is not None]
            sqlcmd = 'INSERT into %s (' % table_name + ','.join([i[0] for i in ls]) +') VALUES (' + ','.join(repr(i[1]) for i in ls) + ');'
            print (sqlcmd)
            cursor.execute(sqlcmd)
            
        except Exception as e:
            print (e)
            raise Exception(e)            
            #exit()
        conn.commit()##一定要有conn.commit()这句来提交事务，要不然不能真正的插入数据
        conn.close()
        print ('insert_db_table finished!')
    
    ####删除表记录
    def delete_table_record(self,database_name,table_name,condition_element):
        conn = psycopg2.connect(database=database_name, host=self.host, user=self.user, password=self.password, port=self.port)
        cursor=conn.cursor()
        try:
            ####执行数据库语言
            #cfg_kv = [(k, v) for k, v in config_element.items() if v is not None]
            cdt_kv = [(k, v) for k, v in condition_element.items() if v is not None]
            #print (cfg_kv)
            print (cdt_kv)

            sqlcmd = "DELETE FROM %s "%table_name
            sqlcmd += " WHERE "          ##条件可以更加实际情况定
            if(len(cdt_kv)>1):
                sqlcmd += "and ".join(["%s='%s'" % f for f in (cdt_kv)])
            elif(len(cdt_kv)==1):
                sqlcmd += "".join(["%s='%s'" % f for f in (cdt_kv)])
                
            print (sqlcmd)
            cursor.execute(sqlcmd)
            
        except Exception as e:
            print (e)
         
        conn.commit()##一定要有conn.commit()这句来提交事务，要不然不能真正的插入数据
        conn.close()
        print ('delete_table_record finished!')

 