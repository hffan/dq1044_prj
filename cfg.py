#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@modify history
2020-04-29 17:37:23     
                    1.字体修改为宋体
2020-8-5 09:40:55
                    1.统一修改配置路径
                    
                    

"""
import platform
import os
from io_interface.iostat import is_executable



#config_rootpath='/kjtq/'            ##真实环境路径
config_rootpath='/home/DQ1044/'    ##公司环境路径




##用户可以根据不同的操作系统，修改如下参数，配置代码存放的根路径,不能使用os.path.join
print (os.path.dirname(os.path.abspath(__file__)))
rootpath = os.path.dirname(os.path.abspath(__file__))
# rootpath = "/home/DQ1044/code_prj/"
# rootpath = "C:\\Users\\Administrator\\Desktop\\DQ1044_centos7.1\\code_prj\\"
# print (rootpath)


if ('Windows' == platform.system()):
    outputfilepath = rootpath + '\\product\\output\\'
    shp_rootpath =  rootpath + '\\shp\\'
    fonts_path =  rootpath + '\\fonts\\SimSun.ttf'
    iri_inputpath =  rootpath + '\\IRI_2016\\input\\'
    iri_outputpath =  rootpath + '\\localplugins\\IRI\\'    
    Fortran_path =  rootpath + '\\IRI_2016\\IRI_2016_windows.exe'
    format_path =  rootpath + '\\IONO\\FDS\\ION\\format.lst'
    #localdir = rootpath + '\\localdatafiles\\'#windows hadoop接口暂时无法测试
    product_dir = rootpath + '\\productfiles\\'#windows hadoop接口暂时无法测试
    station_txt = rootpath + '\\station\\station_info.txt'
if ('Linux' == platform.system()):            
    outputfilepath = rootpath + '/product/output/'
    shp_rootpath =  rootpath + '/shp/'
    fonts_path =  rootpath + '/fonts/SimSun.ttf'
    iri_inputpath =  rootpath + '/IRI_2016/input/'
    #iri_outputpath =  rootpath + '/home/DQ1044/localplugins/IRI/'
    iri_outputpath = config_rootpath + '/localplugins/IRI/'    
    Fortran_path =  rootpath + '/IRI_2016/IRI_2016_linux.exe'
    format_path =  rootpath + '/IONO/FDS/ION/format.lst'
    #localdir = '/home/DQ1044/localdatafiles/' 
    product_dir = config_rootpath + '/productfiles/' 
    station_txt = rootpath + '/station/station_info.txt'
    datasource_path = config_rootpath + '/datafiles' 
    log_path = config_rootpath + '/debuglog/'	
    ##需要增加exe可执行权限判断，否则拷贝之后没有可执行权限，导致程序调用失败
    is_executable(Fortran_path)

    
configs = { 'outputfilepath': outputfilepath,
            'shp_rootpath': shp_rootpath,
            'fonts_path':fonts_path,
            'iri_inputpath':iri_inputpath,
            'iri_outputpath':iri_outputpath,
            'Fortran_path':Fortran_path,
            'format_path':format_path,
            'product_dir':product_dir,
            'station_txt':station_txt,
            'datasource_path':datasource_path,
            'log_path':log_path}
            
print (configs)
