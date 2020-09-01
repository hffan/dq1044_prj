#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
@modify history
2020-04-27 18:21:43 
                    1. 增加22所fmin,foF2接口合并；
                    2. 增加22所L，UHF波段接口合并；
                    3. 增加太阳SOT图像，都更改成V2版本，去掉白色边界
2020-04-29 14:22:32 
                    1. 增加进度条显示功能
2020-07-17 12:47:20
                    1. S4闪烁指数,png产品L11更改为L21
                    2. TEC过去72小时png产品,L11更改为L21
2020-8-24 09:54:47
				    1. 注释掉S4闪烁警报流程
					2. edp密度剖面图增加频高图文件输出                   

"""

import sys
import os
import xml.etree.ElementTree as ET
from cfg import *
from rdwrxml.rd_xml import *  # xml文件夹和xml库冲突
from rdwrxml.wr_xml import *
from logger.logger import *
from time_interface.time_format import get_current_time
import hdfs_interface.hdfs_handle
import traceback


# java调用basemap需要配置如下环境变量
import conda
conda_file_dir = conda.__file__
conda_dir = conda_file_dir.split('lib')[0]
proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
os.environ["PROJ_LIB"] = proj_lib
from productInterface import *




##异常直接输出xml文件，结束程序
def product_xml(rdxml,status_text,info_text,producttype_attribute,file_text):
    ##xml输出路径不存在可能导致xml文件无法正常输出
    xml_rootpath, xml_filename = os.path.split(rdxml.outXMLPath)
    if not os.path.exists(xml_rootpath):
        os.makedirs(xml_rootpath)

    wrxml = WriteOutputXml(rdxml.outXMLPath)
    identify_attribute = rdxml.field
    #debug_log('begin wrxml.writexml...')
    wrxml.writexml(identify_attribute, status_text, info_text, producttype_attribute, file_text)
    print ('输出xml文件 %s' % rdxml.outXMLPath)
    #debug_log(rdxml.outXMLPath)
    #debug_log('finish wrxml.writexml...')
    #debug_log('')
    #debug_log('')
    print ('-----------------结束--------------------')        
    print ('')
    exit(0)#正常退出
    

if __name__ == '__main__':
    if (len(sys.argv) != 2):
        print('')
        print('第1个参数： 主程序 %s' % os.path.abspath(__file__))
        print('第2个参数： 输入xml配置文件全路径')
        exit('请输入正确的命令行调用格式')


    xmlpath = sys.argv[1]
    print ('')
    print ('-----------------开始--------------------')
    prd = Product()  # 实例化
    taskStarttime = get_current_time()

    print ('sys.argv[1] = %s'%xmlpath)
        
    ##读取配置参数
    outputproduct = ''      # 定义空，try except失败导致outputproduct返回空
    outputproducts = []     # 针对输出多个产品的情况
    hadoop_products = []
    info_text = 'failed'    # 默认处理failed,防止以下if条件不满足或者try,except导致info_text没有信息输出
    status_text = '0'
    producttype_attribute=''

    # 可视化界面调用太阳质子事件预警、太阳耀斑预报、太阳质子事件预报
    taskType = 'solar_alert_forecast'
    solar_logs = Loggings(taskStarttime, taskType)  # 实例化日志类
    if len(sys.argv[1]) < 10:
        try:
            prd.solar_interface_dispatch(sys.argv[1])
        except Exception as e:
            solar_logs.debug_log(str(e))  # 输出hadoop异常操作到log日志里
        print('-----------------结束--------------------')
        exit(0)

    ##解析输入的xml文件,异常直接
    try:
        rdxml = ReadInputXml(xmlpath)
        rdxml.readxml()
    except Exception as e:
        info_text = str(e)
        traceback.print_exc()        
        product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    print ('finish read xml.')

    ##日志文件名称按任务类型命名
    print(rdxml.taskType)
    loggings=Loggings(taskStarttime,rdxml.taskType)#实例化日志类

    ##根据xml文件里的hdfs路径，映射到本地存储路径
    ##如果有L1,L2标识，单独处理
    ##如果没有L1,L2标识，统一处理
    ##情况：1.有L1，没有L2     2.有L1,有L2   3.没有L1,没有L2     


    ####没有hadoop接口
    localfilesL1    = []
    localfilesL2    = []
    localfiles      = []
    ####
    localfilesL1 = rdxml.inputFileL1
    localfilesL2 = rdxml.inputFileL2
    localfiles = rdxml.inputFile    
    
    
    ####测试hadoop接口
    # localdir=configs['localdir']
    # localfilesL1 = []
    # localfilesL2 = []
    # localfiles = []
    # #print ('localdir = %s'% localdir)
    # if (rdxml.inputFileL1) or (rdxml.inputFileL2):#tag中有L1,L2
        # if rdxml.inputFileL1:
            # try:        
                # localfilesL1 = hdfs_interface.hdfs_handle.get_from_hdfs(rdxml.url, rdxml.inputFileL1, localdir)
            # except Exception as e:
                # loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里            
                # loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
                # loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                
                # #raise Exception(str(e))
                # status_text='0'
                # info_text=str(e)
                # product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
        # if rdxml.inputFileL2:
            # try:        
                # localfilesL2 = hdfs_interface.hdfs_handle.get_from_hdfs(rdxml.url, rdxml.inputFileL2, localdir)
            # except Exception as e:
                # loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里            
                # loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
                # loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                      
                # #raise Exception(str(e))
                # status_text='0'
                # info_text=str(e)
                # product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)                
    # else:#tag中没有L1或L2
        # if rdxml.inputFile:
            # try:
                # print('111')
                # localfiles = hdfs_interface.hdfs_handle.get_from_hdfs(rdxml.url, rdxml.inputFile, localdir)
                # print('222')
            # except Exception as e:
                # loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里            
                # loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
                # loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                      
                # #raise Exception(str(e))
                # status_text='0'
                # info_text=str(e)
                # product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)                


    ####产品生产接口
    if (rdxml.taskType == 'inon_measured_TEC'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_CET_ISM_TEC_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                  
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'inon_measured_fmin'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_CET_ION_fmin_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'inon_measured_foF2'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_CET_ION_foF2_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'inon_measured_SintL'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_CET_ISM_SintL_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里        
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'inon_measured_SintUHF'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_CET_ISM_SintU_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里      
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'CET_ISM_S4'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_CET_ISM_S4_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里      
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'inon_vtec_cal_fds_TEC'):
        
        ####得到rootpath,从xml配置文件里解析，stationID也可以从xml文件里解析
        ####所有文件统一存放到1个固定路径下，取任意1个路径即可
        #rootpath, filename = os.path.split(localfiles[0])
        rootpath, filename = os.path.split(localfilesL1[0])
        if (localfilesL1):  # L1不为空
            producttype_attribute = 'std'
            try:
                outputproduct = prd.cal_FDS_ISM_vTEC_main(localfilesL1, rootpath)
                outputproducts.append(outputproduct)
                info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
                status_text = '1'
            except Exception as e:
                loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里            
                loggings.debug_log(str(e))#输出hadoop异常操作到log日志里     
                loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                     
                info_text = str(e)
                #info_text = traceback.format_exc()                
                status_text = '0'
                product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
        if (localfilesL2) and (status_text == '1'): # L2不为空
            producttype_attribute = 'std'
            try:
                ####需要71个小时之前的文件，0-71个，比如当前时刻20200319090000，前71小时20200319080000，20200319070000，......
                ####需要L1文件上的当前时间，作为产品png图形时间
                outputproduct = prd.read_FDS_ISM_TEC_main(localfilesL1, localfilesL2, rootpath)
                #outputproduct = prd.plot_FDS_ISM_VTEC_main(rdxml.inputFileL2, rootpath, rdxml.stationID)
                outputproducts.append(outputproduct)
                info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
                status_text = '1'
            except Exception as e:
                loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里            
                loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
                loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                     
                info_text = str(e)
                status_text = '0'
                product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'inon_measured_TEC_krig'):
        """区域融合，需要截取rdxml.outXMLPath路径里MIX"""
        producttype_attribute = 'sub'
        try:
            outputproduct = prd.read_CET_ISM_TEC_krig_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'iono_fds_ism_TEC_krig_FDS'):
        producttype_attribute = 'sub'
        try:
            outputproduct = prd.read_FDS_ISM_TEC_krig_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo   #类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath) #输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))  #输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'iono_fds_ism_scint'):
        producttype_attribute = 'std'
        ####第1步生产S4闪烁指数现报
        try:
            print (localfiles)
            outputproduct = prd.read_FDS_ISM_scint_main( localfilesL1)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo       #类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)     #输出hadoop异常操作到log日志里
            loggings.debug_log(str(e))      #输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
        ####第2步生产S4闪烁指数警报
        # try:
            # outputproduct = prd.read_FDS_ISM_scint_alert_main( localfilesL1)
            # outputproducts.append(outputproduct)
            # info_text = prd.errorinfo       #类里提取错误信息，没有错误，返回默认值SUCCESS
            # status_text = '1'
        # except Exception as e:
            # loggings.debug_log(xmlpath)     #输出hadoop异常操作到log日志里        
            # loggings.debug_log(str(e))      #输出hadoop异常操作到log日志里
            # loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            # info_text = str(e)
            # status_text = '0'
            # product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products) 
    
    if (rdxml.taskType == 'iono_fds_ism_alert'):
        producttype_attribute = 'std'
        ####生产S4闪烁指数警报
        try:
            print (localfiles)
            outputproduct = prd.read_FDS_ISM_alert_main( localfilesL1)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo       #类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)     #输出hadoop异常操作到log日志里
            loggings.debug_log(str(e))      #输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
          
            
    if (rdxml.taskType == 'iono_fds_ion_fmin'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_FDS_ION_fmin_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e)) #输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'iono_fds_ion_foF2'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_FDS_ION_foF2_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'iono_fds_ion_MUF'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_FDS_ION_MUF_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'iono_fds_ion_scaled'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_FDS_ION_scaled_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)            
    if (rdxml.taskType == 'iono_fds_ion_edp'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_FDS_ION_edp_main(localfiles)
            #outputproducts.append(outputproduct)
            outputproducts.extend(outputproduct)##extend,list追加到list里，append,list嵌套到list里 
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'cet_ion'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_CET_ION_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)            
    ####太阳接口
    if (rdxml.taskType == 'solar_fds_sot_cgq'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_FDS_SOT_V2_GQ_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'solar_fds_sot_cgs'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_FDS_SOT_V2_GS_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'solar_fds_sot_cha'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_FDS_SOT_V2_HA_main(localfiles)
            outputproducts.append(outputproduct)
            # 太阳耀斑预警、太阳暗条预警
            outputproduct = prd.solar_flare_filament_alert_main(localfiles)
            outputproducts.extend(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里  
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'solar_fds_sot_cgc'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_FDS_SOT_V2_GC_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'solar_fds_srt'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_FDS_SRT_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'solar_cma_srt'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_CMA_SRT_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'geomag_index'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_GEOMAG_INDEX_main(rdxml.taskType,localfiles)
            #outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'iono_scaled'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_IONO_SCALED_main(rdxml.taskType,localfiles)
            #outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    if (rdxml.taskType == 'solar_rad'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_SOLAR_RAD_main(rdxml.taskType,localfiles)
            #outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
   
    ##ATMOS数据接口
    ##流星雷达包括地基-流星雷达流星余迹参数信息统计分析数据接口、地基-流星雷达水平风场矢量分布图绘制数据接口
    if(rdxml.taskType == 'ATMOS_FDS_MET'):
        producttype_attribute = 'std'
        if (localfilesL1):  # L1不为空 地基-流星雷达流星余迹参数信息统计分析数据接口
            try:
                outputproduct = prd.read_Atmos_FDS_MET_L11(localfilesL1)
                outputproducts.extend(outputproduct)
                info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
                status_text = '1'
            except Exception as e:
                loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
                loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
                loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
                info_text = str(e)
                status_text = '0'
                product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
        if(localfilesL2 and status_text=='1'):#L2不为空 地基-流星雷达水平风场矢量分布图绘制数据接口
            try:
                outputproduct = prd.read_Atmos_FDS_MET_L21(localfilesL2)
                outputproducts.append(outputproduct)
                info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
                status_text = '1'
            except Exception as e:
                loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
                loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
                loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
                info_text = str(e)
                status_text = '0'
                product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)

    ##地基-MST雷达风场廊线图绘制数据接口
    # --暂停使用
    if (rdxml.taskType == 'ATMOS_FDS_MST'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_Atmos_FDS_MST_main(localfiles)
            outputproducts.extend(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    # 绘制大气风场廓线
    if (rdxml.taskType == 'ATMOS_FDS_MST_30M'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_Atmos_FDS_MST_30M_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    # 大气风场湍流廓线
    if (rdxml.taskType == 'ATMOS_FDS_MST_24H'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_Atmos_FDS_MST_24H_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    # 大气风场廓线演化图
    if (rdxml.taskType == 'ATMOS_FDS_MST_72H'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_Atmos_FDS_MST_72H_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)

    ##子午-激光雷达
    ##大气密度文件
    # --暂停使用
    if (rdxml.taskType == 'ATMOS_MDP_LID_DAM'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_Atmos_MDP_LID_DAM_main(localfiles)
            outputproducts.extend(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)

    ##大气温度文件
    # --暂停使用
    if (rdxml.taskType == 'ATMOS_MDP_LID_DAT'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_Atmos_MDP_LID_DAT_main(localfiles)
            outputproducts.extend(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)

    # 生成大气密度、温度、压强
    if (rdxml.taskType == 'ATMOS_MDP_LID'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_Atmos_MDP_LID_main(localfiles)
            outputproducts.extend(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
            

    # 融合数据处理---MST雷达产品数据文件和气象高空气球数据
    # 只做酒泉和海尔滨站--每12小时启动一次
    if (rdxml.taskType == 'ATMOS_FDS_MST_UPAR'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_Atmos_FDS_UPAR_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)


    ##GEOMAG数据接口
    ##地基-地磁7要素监测数据接口
    if (rdxml.taskType == 'GEOMAG_FDS_FGM_DSR'):
        producttype_attribute = 'std'
        stationID = 'XXXJ'
        try:
            outputproduct = prd.read_GEOMAG_FDS_FGM_DSR_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)

    ##子午-地磁7要素监测数据接口
    if (rdxml.taskType == 'GEOMAG_MDP_FGM'):
        producttype_attribute = 'std'
        stationID = 'XXXJ'
        try:
            outputproduct = prd.read_GEOMAG_MDP_FGM_main(localfiles)
            outputproducts.extend(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)

    # 地基-单站K指数计算
    if (rdxml.taskType == 'GEOMAG_FDS_RK_H'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_GEOMAG_FDS_RK_H_main(localfiles)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)

    # 地基-中国区域K指数计算
    if (rdxml.taskType == 'GEOMAG_FDS_RK'):
        producttype_attribute = 'sub'
        try:
            outputproduct = prd.read_GEOMAG_FDS_RK_main(localfiles)
            outputproducts.extend(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)

    # 读取地磁暴日志文件，生成地磁暴报告文档
    if (rdxml.taskType == 'GEOMAG_FDS_FGM_DDR'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_GEOMAG_FDS_FGM_DDR_main(localfiles)
            outputproducts.extend(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
            loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)

    # 高空数据AFD_UPAR
    if (rdxml.taskType == 'AFD_UPAR'):
        producttype_attribute = 'std'
        try:
            outputproduct = prd.read_AFD_UPAR_main(rdxml.inputFile)
            outputproducts.append(outputproduct)
            info_text = prd.errorinfo  # 类里提取错误信息，没有错误，返回默认值SUCCESS
            status_text = '1'
        except Exception as e:
            loggings.debug_log(xmlpath)  # 输出hadoop异常操作到log日志里
            loggings.debug_log(str(e))  # 输出hadoop异常操作到log日志里
            loggings.debug_log(traceback.format_exc())  # 输出hadoop异常操作到log日志里
            info_text = str(e)
            status_text = '0'
            product_xml(rdxml, status_text, info_text, producttype_attribute, hadoop_products)

    # ##产品推送hadoop
    # try:
        # hadoop_products = hdfs_interface.hdfs_handle.put_to_hdfs(rdxml.url, outputproducts)
        # print ('push to hadoop.')
        # loggings.debug_log(hadoop_products[0])#输出hadoop异常操作到log日志里
    # except Exception as e:
        # loggings.debug_log(xmlpath)#输出hadoop异常操作到log日志里        
        # loggings.debug_log(str(e))#输出hadoop异常操作到log日志里
        # loggings.debug_log(traceback.format_exc())#输出hadoop异常操作到log日志里                 
        # info_text = str(e)
        # status_text = '0'
        # product_xml(rdxml,status_text,info_text,producttype_attribute,hadoop_products)
    
    
    ##正常输出xml文件,产品路径hadoop目录
    product_xml(rdxml,status_text,info_text,producttype_attribute,outputproducts)
    #loggings.debug_log(outputproducts[0])#输出hadoop异常操作到log日志里
    #print ('finish.')
    