#!/usr/bin/python
# -*- coding: UTF-8 -*-
import sys
import os
import xml.etree.ElementTree as ET


class ReadInputXml(object):
    def __init__(self, xmlpath):
        self.xmlpath = xmlpath  # xml全路径
        self.field = ''
        self.taskType = ''
        self.apparatus = ''
        self.inputFile = []
        self.inputFileL1=[]
        self.inputFileL2=[]
        self.stationID=''
        self.url=''#hadoop地址
        self.outXMLPath = ''
        self.errors=''
        return

    # 解析输入xml文件
    def readxml(self):
        if not os.path.exists(self.xmlpath):
            #exit("xml:%s is not found" % self.xmlpath)
            self.errors = "%s is not found" % self.xmlpath
            raise Exception (self.errors)
            #raise Exception
        tree = ET.parse(self.xmlpath)
        root = tree.getroot()
        for child in root:
            ####先解析输出xml文件，否则以下有异常的情况，导致程序直接raise异常，导致输出xml文件字段无法解析，导致异常信息无法在输出xml文件中得到
            ####需要xml文件里的outXMLPath放到第1行，否则if条件无法在第一次判断找到outXMLPath字段
            if (child.attrib['identify'] == 'outXMLPath'):
                self.outXMLPath = child.text
                # print('outXMLPath = %s' % self.outXMLPath)
            # print(child.tag,child.attrib,child.text)
            if (child.attrib['identify'] == 'field'):
                self.field = child.text
                print('field = %s' % self.field)
            if (child.attrib['identify'] == 'apparatus'):
                self.apparatus = child.text
                print('apparatus = %s' % self.apparatus)
            if (child.attrib['identify'] == 'taskType'):
                self.taskType = child.text
            if (child.attrib['identify'] == 'inputFile')and (child.attrib['level'] == 'L1'):
                self.inputFileL1.append(child.text)
                # print('inputFile = %s' % child.text)
            if (child.attrib['identify'] == 'inputFile')and (child.attrib['level'] == 'L2'):
                self.inputFileL2.append(child.text)
                # print('inputFile = %s' % child.text)
            if (child.attrib['identify'] == 'url'):
                self.url = child.text
                print('self.url = %s' % self.url)                                
            if (child.attrib['identify'] == 'inputFile'):
                self.inputFile.append(child.text)
                
                try:
                    self.stationID = child.attrib['station']
                except Exception as e:
                    ##自定义异常
                    err = '%s%s%s%s%s' % (__file__, ',LINE ', sys._getframe().f_lineno, ',', "identify=inputFile do not have child.attrib 'station'")
                    raise Exception(err)
               
        #url字段校验
        if(self.url):
            pass
        else:
            err = '%s%s%s%s%s' % (__file__, ',LINE ', sys._getframe().f_lineno, ',', "url is None.......")
            raise Exception(err)

        #pass
        return
