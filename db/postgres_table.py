# -*- coding:utf-8 -*-
import os
import sys
import time
import re
import datetime
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from db_conf import *

class PostgresTable:
       
    def __init__(self):
        #####统一配置参数，便于修改
        self.database = configs['database']
        self.host = configs['host']
        self.user = configs['user']
        self.password = configs['password']
        self.port = configs['port']
        return

        
    ####连接数据路
    def connecte_db(self, database_name):
        con = psycopg2.connect(database=database_name, host=self.host, user=self.user, password=self.password,
                               port=self.port)
        ##创建游标对象
        print('connect %s successful!' % database_name)

        
    ##创建数据库
    def create_db(self, database_name):
        con = psycopg2.connect(database=self.database, host=self.host, user=self.user, password=self.password,
                               port=self.port)
        ##创建游标对象
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = con.cursor()
        ##创建数据库
        try:
            cursor.execute('create database {}'.format(database_name))
        except Exception as e:
            print(e)
            raise Exception(e)            
            # exit()
        print('create_db %s successful!' % database_name)
    
    
    ##删除数据库
    def delete_db(self, database_name):
        con = psycopg2.connect(database=self.database, host=self.host, user=self.user, password=self.password,
                               port=self.port)
        ##创建游标对象
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = con.cursor()
        ##创建数据库
        try:
            cursor.execute('drop database {}'.format(database_name))
        except Exception as e:
            print(e)
            raise Exception(e)            
            # exit()
        print('delete_db %s successful!' % database_name)

        
    ##删除数据库中的表
    def delete_table(self,database_name,table_name):
        con = psycopg2.connect(database=database_name, host=self.host, user=self.user, password=self.password,
                               port=self.port)
        ##创建游标对象
        con.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = con.cursor()
        ##创建数据库
        try:
            cursor.execute('drop table {}'.format(table_name))
        except Exception as e:
            print(e)
            raise Exception(e)            
            # exit()
        print('delete_table %s successful!' % table_name)

 
    def create_t_geomag_index_table(self, database_name):
        """创建地磁指数表"""
        conn = psycopg2.connect(database=database_name, host=self.host, user=self.user, password=self.password,
                                port=self.port)
        cursor = conn.cursor()
        # serial自动增加
        # 需要根据常用的变量创建索引，便于查询
        # 查询时候，也使用复合索引查询，另外插入的时效性要求不高，可以建立复合索引，查询效率高
        # 表字段不区分大小写
        try:
            sqlcmd = '''create table t_geomag_index(
                            id serial not null primary key,
                            observetime TIMESTAMP(0) not null,
                            station varchar(5) not null,
                            apparatus varchar(3) not null,                            
                            K int4 not null,                            
                            createtime TIMESTAMP(0) not null
                            )'''
            cursor.execute(sqlcmd)
        except Exception as e:
            print(e)
            raise Exception(e)            
            # exit()
        conn.commit()
        conn.close()
        print('create_t_geomag_index_table finished!')    


    def create_t_solar_rad_table(self, database_name):
        """太阳射电流量数据表"""
        conn = psycopg2.connect(database=database_name, host=self.host, user=self.user, password=self.password,
                                port=self.port)
        cursor = conn.cursor()
        # serial自动增加
        # 需要根据常用的变量创建索引，便于查询
        # 查询时候，也使用复合索引查询，另外插入的时效性要求不高，可以建立复合索引，查询效率高
        # 表字段不区分大小写
        try:
            sqlcmd = '''create table t_solar_rad(
                            id serial not null primary key,
                            type varchar(10) not null,
                            observetime TIMESTAMP(0) not null,
                            apparatus varchar(3) not null,                                
                            apparatusid varchar(2) not null,
                            station varchar(5) not null,                        
                            flux float4 not null,
                            createtime TIMESTAMP(0) not null
                            )'''
            cursor.execute(sqlcmd)
        except Exception as e:
            print(e)
            raise Exception(e)            
            # exit()
        conn.commit()
        conn.close()
        print('create_t_solar_rad_table finished!')
        
        
    def create_t_solar_pre_table(self, database_name):
        """太阳活动预报表"""
        conn = psycopg2.connect(database=database_name, host=self.host, user=self.user, password=self.password,
                                port=self.port)
        cursor = conn.cursor()
        # serial自动增加
        # 需要根据常用的变量创建索引，便于查询
        # 查询时候，也使用复合索引查询，另外插入的时效性要求不高，可以建立复合索引，查询效率高
        # 表字段不区分大小写
        try:
            sqlcmd = '''create table t_solar_pre(
                            id serial not null primary key,
                            observetime TIMESTAMP(0) not null,
                            physical varchar(3) not null,                                
                            prob varchar(1) not null,
                            station varchar(5) not null,
                            createtime TIMESTAMP(0) not null
                            )'''
            cursor.execute(sqlcmd)
        except Exception as e:
            print(e)
            raise Exception(e)            
            # exit()
        conn.commit()
        conn.close()
        print('create_t_solar_pre_table finished!')



    def create_t_iono_scaled_table(self, database_name):
        """电离层参数数据表"""
        conn = psycopg2.connect(database=database_name, host=self.host, user=self.user, password=self.password,
                                port=self.port)
        cursor = conn.cursor()
        # serial自动增加
        # 需要根据常用的变量创建索引，便于查询
        # 查询时候，也使用复合索引查询，另外插入的时效性要求不高，可以建立复合索引，查询效率高
        # 表字段不区分大小写
        try:
            sqlcmd = '''create table t_iono_scaled(
                            id serial not null primary key,
                            observetime TIMESTAMP(0) not null,
                            station varchar(5) not null,                                
                            apparatus varchar(3) not null,                      
                            foF2 float4 not null,                            
                            foF1 float4 not null,
                            M_D float4 not null,
                            MUF_D float4 not null,                            
                            fmin float4 not null,
                            foEs float4 not null,
                            fminF float4 not null,
                            fminE float4 not null,
                            foE float4 not null,
                            fxI float4 not null,
                            hF float4 not null,  
                            hF2 float4 not null,  
                            hE float4 not null, 
                            hEs float4 not null,                          
                            createtime TIMESTAMP(0) not null
                            )'''
            cursor.execute(sqlcmd)
        except Exception as e:
            print(e)
            raise Exception(e)            
            # exit()
        conn.commit()
        conn.close()
        print('create_t_solar_rad_table finished!')

        
        