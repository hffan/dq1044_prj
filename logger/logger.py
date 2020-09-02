#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import logging
import datetime
from sys_interface.optsys import get_pid
from socket_interface.sockets import *
from cfg import *

"""
@modify
2020-04-11 10:17:46
1. 任务日志按天命名文件夹
2. 每天的文件夹里有各自接口名称命名的日志
3. 日志第1列运行程序当前系统时间,第2列运行程序的PID, 第3列运行节点的IP地址

2020-04-23 10:18:13
1. 任务日志去掉hostname，增加1列任务启动时间

"""
class Loggings(object):
    def __init__(self, taskStarttime,taskType):
        self.taskType = taskType
        self.taskStarttime = taskStarttime
        self.log_path = configs['log_path']
        return

    def debug_log(self, infos=None, root_logpath=os.path.dirname(os.path.abspath(__file__))):
        
        ####如果业务系统正常运行,可以直接return,跳过程序日志
        #return
        
        ####如果默认infos参数为空，程序日志自动跳出，不创建程序日志
        if infos==None:
            return
			
		#日志指定目录
        root_logpath = self.log_path
        
        ##程序日志模块
        ##先创建日志目标文件夹
        ##默认当前路径创建log文件夹，如果root_logpath传入参数，则按传入参数的路径创建log根路径
        ip = get_ip()
        user_name = get_username()
        host_name = get_hostname()

        sys_time = datetime.datetime.now().strftime('%Y-%m-%d')
        #sys_time = '2020-04-12'
        #print (sys_time)
        pid = get_pid()
        #print (pid)
        
        logpath = os.path.join(root_logpath,'log',sys_time)
        if not os.path.exists(logpath):
            os.makedirs(logpath)
        logname=os.path.join(logpath,self.taskType + '.log')

        ##添加自定义日志格式
        dic = {'user_name':user_name,
                'host_name':host_name,
                'ip':ip,
                'starttime':self.taskStarttime}
        
        #log_format = "[%(user_name)s %(host_name)s %(ip)s %(asctime)s %(process)9d]:  %(message)s"
        #log_format = "[%(user_name)s] [%(host_name)24s] [%(ip)s] [%(asctime)s] [%(process)10d]:  %(message)s"
        #log_format = "[%(user_name)s] [%(ip)s] [%(starttime)s] [%(asctime)s] [%(process)10d]:  %(message)s"
        log_format = "[%(user_name)s][%(ip)s][%(starttime)s][%(asctime)s][%(process)10d]:  %(message)s"        
        logging.basicConfig(level=logging.INFO,
                            filename=logname,
                            filemode='a',                       ##日志追加
                            format=log_format,  ##''里的[]是信息输出，加的'[%(
                            #format='[%(process)9d] [%(asctime)s] %(message)s',   ##''里的[]是信息输出，加的'[%(asctime)s %(message)s]'可以去掉
                            #format='[%(asctime)s] [%(process)9d] %(message)s',   ##''里的[]是信息输出，加的'[%(asctime)s %(message)s]'可以去掉
                            #format='%(asctime)s %(funcName)s %(lineno)d %(message)s',   ##''里的[]是信息输出，加的'[%(asctime)s %(message)s]'可以去掉
                            datefmt='%Y-%m-%d %H:%M:%S'         ##默认输出格式带毫秒'%Y-%m-%d %H:%M:%S%p'
                            )
        # ip + infos
        #infos = '[%s]   %s' % (ip,infos)
        logging.info(infos,extra=dic)##输出info内容到log文件, extra 是把字典里的属性添加到record中
    

