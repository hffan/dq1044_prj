"""
@modify history
2020-07-21 14:45:53
                    1. 融合的MIXJ_ISM00_ITECmap_L31_STP_更改为MIXJ_ISM00_ITEC_L31_STP_
2020-8-4 11:16:56
                    1. SOLAR绘图V2版本，注释掉read_plot里的plot绘图函数
2020-8-24 09:56:21
				    1. 增加频高图，产品png输出，合并到密度剖面图流程里
					                    
"""



import shutil
import sys
import os
import datetime
from cfg import *
import traceback



##import 整个文件,调用文件里的函数,可以指定文件夹.文件名.函数
# 电离层22所
import IONO.CET.ISM.read_CET_ISM_TEC
import IONO.CET.ISM.read_CET_ISM_TEC_krig
import IONO.CET.ISM.read_CET_ISM_SintL
import IONO.CET.ISM.read_CET_ISM_SintU
import IONO.CET.ISM.read_CET_ISM_S4

import IONO.CET.ION.read_CET_ION_fmin
import IONO.CET.ION.read_CET_ION_foF2
import IONO.CET.ION.read_CET_ION


# 电离层地基
#import IONO.FDS.ISM.read_FDS_ISM_ITEC
import IONO.FDS.ISM.cal_FDS_ISM_vTEC
import IONO.FDS.ISM.read_FDS_ISM_TEC

import IONO.FDS.ISM.read_FDS_ISM_TEC_krig
import IONO.FDS.ISM.read_FDS_ISM_scint
import IONO.FDS.ISM.read_FDS_ISM_scint_alert
import IONO.FDS.ISM.read_FDS_ISM_scint_map
import IONO.FDS.ION.read_FDS_ION_fmin
import IONO.FDS.ION.read_FDS_ION_foF2
import IONO.FDS.ION.read_FDS_ION_MUF
import IONO.FDS.ION.read_FDS_ION_edp
import IONO.FDS.ION.read_FDS_ION_scaled



# 太阳
import SOLAR.FDS.SOT.read_FDS_SOT_V1
import SOLAR.FDS.SOT.read_FDS_SOT_V2
import SOLAR.FDS.SRT.read_FDS_SRT
import SOLAR.CMA.SRT.read_CMA_SRT

# 解析物理要素并入库
import element_opt.element_extract
import element_opt.element_record
import element_opt.read_k



# 临近空间
import ATMOS.FDS.MET.read_FDS_MET_L11
import ATMOS.FDS.MET.read_FDS_MET_L21
import ATMOS.FDS.MST.read_FDS_MST
import ATMOS.FDS.MST.read_FDS_MST_V1
import ATMOS.FDS.MST.read_FDS_MST_V2
import ATMOS.FDS.MST.CAL_FDS_MST_turb
import ATMOS.MDP.LID.read_MDP_LID_DAM_V2
import ATMOS.MDP.LID.read_MDP_LID_DAT_V2
import ATMOS.MDP.LID.read_MDP_LID_V1
import ATMOS.MDP.LID.read_MDP_LID_V2
import ATMOS.FDS.UPAR.read_CMA_UPAR
import ATMOS.FDS.UPAR.read_AFD_UPAR

# 地磁暴
import GEOMAG.FDS.FGM.read_FDS_FGM_DSR
import GEOMAG.FDS.FGM.cal_FDS_Kindex
import GEOMAG.FDS.FGM.cal_FDS_RegionK_V1
import GEOMAG.FDS.FGM.read_FDS_FGM_DDR
import GEOMAG.MDP.FGM.read_MDP_FGM
import GEOMAG.FDS.FGM.make_FDS_FGM_DAR
import GEOMAG.FDS.FGM.make_FDS_FGM_DDR

# 预警、预报使用
import db.postgres_archive

# 获取站名
import station.station_info


class Product(object):
    #def __init__(self, outputpath):
    def __init__(self):
    #def __init__(self, inputfile, outputpath):
        #self.inputfile = inputfile
        self.errorinfo = 'SUCCESS'
        #self.outputpath = outputpath
        self.outputpath = ''
        return

    # # 匹配本地产品目录
    # def match_profile(self, inputfile):
        # print ('into match_profile......')
        # """
        # 匹配本地产品目录，本地产品存放路径
        # """
        # name_list = ['CET', 'CMA', 'FDS', 'MDP']
        # for i in range(4):
            # index = str(inputfile).find(name_list[i])
            # if index != -1:
                # outputfile = inputfile[0:index+3] + 'pro' + inputfile[index+3:]
        # # 判断新目录是否存在，没有就创建
        # propath, profilename = os.path.split(outputfile)
        # if not os.path.exists(propath):
            # os.makedirs(propath)
            # # print('create dir ok')
        # else:
            # # print('dir is exist')
            # pass
        # return outputfile
    
    def match_profile(self,inputfile):
        #print ('into match_profile......')
        """
        根据调度输入路径,映射产品路径
        """
        product_dir     =configs['product_dir']
        name_list = ['CET', 'CMA', 'FDS', 'MDP']
        for i in range(4):
            index = str(inputfile).find(name_list[i])
            if index != -1:
                #outputfile = inputfile[0:index+3] + 'pro' + inputfile[index+3:]
                outputfile = inputfile[index:index+3] + 'pro' + inputfile[index+3:]            
                #print (outputfile)
                outputfile = product_dir + '/' + outputfile
        # 判断新目录是否存在，没有就创建
        propath, profilename = os.path.split(outputfile)
        if not os.path.exists(propath):
            os.makedirs(propath)
            # print('create dir ok')
        else:
            # print('dir is exist')
            pass
        return outputfile

        
    def read_CET_ISM_TEC_main(self, inputfile):
        #     # input: TEC_2019071608_at.dat
        #     # output: XXXM_ISM01_ITEC_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]  ##因为默认有时候传入的是一个list，而路径是string类型，所以需要取出list中的元素

        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        #stations = IONO.CET.ISM.station_info.get_CETC22_station_info()
        #stations = station.station_info.get_CETC22_station_info()
        station_id_name=station.station_info.get_CET_station_id_name()
        inputfilepath, inputfilename = os.path.split(file)
        self.outputpath = inputfilepath

        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[1][0:4])
        month = int(filename.split('_')[1][4:6])
        day = int(filename.split('_')[1][6:8])
        hour = int(filename.split('_')[1][8:10])
        stationID = filename.split('_')[2]
        #print(stationID)
        
        stationID_ZM =stationID.upper()+'ZM'
        instrument = 'ISM01'
        product = 'ITEC'
        #level = 'L21'
        level = 'L11'        
        segement = '72H'
        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join([stationID_ZM, instrument, product, level, segement, YYYYMMDDhhmmss])
        
        ##本地数据路径需要映射到本地产品目录
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
 
        YYYYMMDDhh = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H")
        # 读入TEC数据
        data = IONO.CET.ISM.read_CET_ISM_TEC.read_data(file)
        
        # 绘制TEC时序图
        #station_name = stations[stationID]  # 获取站对应的中文
        station_name = station_id_name[stationID]
        DateTime = datetime.datetime(year, month, day, hour)
        datestr = datetime.datetime(year, month, day, hour).strftime("%Y-%m-%d %H")
        IONO.CET.ISM.read_CET_ISM_TEC.plot_data(station_name, datestr, data, productpath)
        
        return productpath

    def read_CET_ION_fmin_main(self, inputfile):
        # input: fmin_2019071608_at.dat
        # output: XXXM_ION01_Ifmin_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)
        #stations = IONO.CET.ION.station_info.get_CETC22_station_info()
        #stations = station.station_info.get_CETC22_station_info()
        station_id_name=station.station_info.get_CET_station_id_name()
        inputfilepath, inputfilename = os.path.split(file)
        self.outputpath = inputfilepath

        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[1][0:4])
        month = int(filename.split('_')[1][4:6])
        day = int(filename.split('_')[1][6:8])
        hour = int(filename.split('_')[1][8:10])
        stationID = filename.split('_')[2]
        stationIDM=stationID.upper()+'ZM'
        
        instrument = 'ION01'
        product = 'Ifmin'
        level = 'L11'
        #level = 'L21'        
        segement = '72H'

        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join([stationIDM, instrument, product, level, segement, YYYYMMDDhhmmss])
        # productpath = self.outputpath + prefix + suffix
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
        
        YYYYMMDDhh = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H")

        # 读入fmin数据
        data = IONO.CET.ION.read_CET_ION_fmin.read_data(file)

        # 绘制fmin时序图
        
        #station_name = stations[stationID]
        station_name = station_id_name[stationID]
        DateTime = datetime.datetime(year, month, day, hour)
        datestr = datetime.datetime(year, month, day, hour).strftime("%Y-%m-%d %H")
        IONO.CET.ION.read_CET_ION_fmin.plot_data(station_name, datestr, data, productpath)
        return productpath


    def read_CET_ION_foF2_main(self, inputfile):
        # input: foF2_2019071608_at.dat
        # output: XXXM_ION01_IfoF2_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)
        #stations = IONO.CET.ION.station_info.get_CETC22_station_info()
        #stations = station.station_info.get_CETC22_station_info()
        station_id_name=station.station_info.get_CET_station_id_name()
        inputfilepath, inputfilename = os.path.split(file)
        self.outputpath = inputfilepath

        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[1][0:4])
        month = int(filename.split('_')[1][4:6])
        day = int(filename.split('_')[1][6:8])
        hour = int(filename.split('_')[1][8:10])
        stationID = filename.split('_')[2]
        stationIDM=stationID.upper()+'ZM'
        
        instrument = 'ION01'
        product = 'IfoF2'
        #level = 'L21'
        level = 'L11'        
        segement = '72H'

        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join([stationIDM, instrument, product, level, segement, YYYYMMDDhhmmss])
        # productpath = self.outputpath + prefix + suffix
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
        
        YYYYMMDDhh = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H")

        # 读入fmin数据
        data = IONO.CET.ION.read_CET_ION_foF2.read_data(file)

        # 绘制fmin时序图
        station_name = station_id_name[stationID]
        DateTime = datetime.datetime(year, month, day, hour)
        datestr = datetime.datetime(year, month, day, hour).strftime("%Y-%m-%d %H")
        IONO.CET.ION.read_CET_ION_foF2.plot_data(station_name, datestr, data, productpath)
        return productpath
    
    
    def read_CET_ION_main(self, inputfile):
        # input: foF2_2019071608_at.dat
        # output: XXXM_ION01_IfoF2_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        for file in inputfile:
            if (os.path.exists(file)):
                ##
                ####过滤fmin,foF2文件
                if 'fmin' in file:
                    file_fmin = file
                if 'foF2' in file:
                    file_foF2 = file
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        #stations = IONO.CET.ION.station_info.get_CETC22_station_info()
        #stations = station.station_info.get_CETC22_station_info()
        station_id_name=station.station_info.get_CET_station_id_name()
        inputfilepath, inputfilename = os.path.split(file)
        self.outputpath = inputfilepath
        
        ####fmin,foF2站名相同,时间相同
        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[1][0:4])
        month = int(filename.split('_')[1][4:6])
        day = int(filename.split('_')[1][6:8])
        hour = int(filename.split('_')[1][8:10])
        stationID = filename.split('_')[2]
        stationIDM=stationID.upper()+'ZM'
        
        instrument = 'ION01'
        #product = 'IfoF2'
        product = 'ICF'        
        level = 'L21'
        segement = '72H'
        
        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join([stationIDM, instrument, product, level, segement, YYYYMMDDhhmmss])
        # productpath = self.outputpath + prefix + suffix
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
        
        #YYYYMMDDhh = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H")
        
        # 读入fmin数据,foF2数据
        data_fmin = IONO.CET.ION.read_CET_ION.read_data_fmin(file_fmin)
        data_foF2 = IONO.CET.ION.read_CET_ION.read_data_foF2(file_foF2)

        #station_name = station_id_name[stationID]
        #DateTime = datetime.datetime(year, month, day, hour)
        #datestr = datetime.datetime(year, month, day, hour).strftime("%Y-%m-%d %H")
        IONO.CET.ION.read_CET_ION.plot_data(data_fmin,data_foF2,productpath)
        return productpath
        
        
    def read_CET_ISM_SintL_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)
        #stations = IONO.CET.ISM.station_info.get_CETC22_station_info()
        #stations = station.station_info.get_CETC22_station_info()
        station_id_name=station.station_info.get_CET_station_id_name()
        inputfilepath, inputfilename = os.path.split(file)
        self.outputpath = inputfilepath

        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[2][0:4])
        month = int(filename.split('_')[2][4:6])
        day = int(filename.split('_')[2][6:8])
        hour = int(filename.split('_')[2][8:10])
        stationID = filename.split('_')[3]
        stationIDM=stationID.upper()+'ZM'
    
        instrument = 'ISM01'
        product = 'IsintL'
        #level = 'L21'
        level = 'L11'        
        segement = '72H'

        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join([stationIDM, instrument, product, level, segement, YYYYMMDDhhmmss])
        # productpath = self.outputpath + prefix + suffix
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
        
        YYYYMMDDhh = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H")

        # 读入fmin数据
        data = IONO.CET.ISM.read_CET_ISM_SintL.read_data(file)

        # 绘制fmin时序图
        station_name = station_id_name[stationID]
        DateTime = datetime.datetime(year, month, day, hour)
        datestr = datetime.datetime(year, month, day, hour).strftime("%Y-%m-%d %H")
        IONO.CET.ISM.read_CET_ISM_SintL.plot_data(station_name, datestr, data, productpath)
        return productpath

    def read_CET_ISM_SintU_main(self, inputfile):
        # input: sint_UHF_2019071600_at.dat
        # output: XXXM_ISM01_IsintUHF_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)
        #stations = IONO.CET.ISM.station_info.get_CETC22_station_info()
        #stations = station.station_info.get_CETC22_station_info()
        station_id_name=station.station_info.get_CET_station_id_name()
        
        inputfilepath, inputfilename = os.path.split(file)
        self.outputpath = inputfilepath

        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[2][0:4])
        month = int(filename.split('_')[2][4:6])
        day = int(filename.split('_')[2][6:8])
        hour = int(filename.split('_')[2][8:10])
        stationID = filename.split('_')[3]
        stationIDM=stationID.upper()+'ZM'
        
        instrument = 'ISM01'
        product = 'IsintUHF'
        level = 'L11'
        #level = 'L21'        
        segement = '72H'

        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join([stationIDM, instrument, product, level, segement, YYYYMMDDhhmmss])
        # productpath = self.outputpath + prefix + suffix
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
        YYYYMMDDhh = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H")

        # 读入fmin数据
        data = IONO.CET.ISM.read_CET_ISM_SintU.read_data(file)

        # 绘制fmin时序图
        #station_name = stations[stationID]
        station_name = station_id_name[stationID]        
        
        DateTime = datetime.datetime(year, month, day, hour)
        datestr = datetime.datetime(year, month, day, hour).strftime("%Y-%m-%d %H")
        IONO.CET.ISM.read_CET_ISM_SintU.plot_data(station_name, datestr, data, productpath)
        return productpath


    def read_CET_ISM_S4_main(self, inputfile):
        # input: foF2_2019071608_at.dat
        # output: XXXM_ION01_IfoF2_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        for file in inputfile:
            if (os.path.exists(file)):
                ##
                ####过滤fmin,foF2文件
                if 'sint_L' in file:
                    file_sintL = file
                if 'sint_UHF' in file:
                    file_sintUHF = file
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        station_id_name=station.station_info.get_CET_station_id_name()
        ##使用提取日期
        inputfilepath, inputfilename = os.path.split(file)
        self.outputpath = inputfilepath
        
        ####fmin,foF2站名相同,时间相同
        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[2][0:4])
        month = int(filename.split('_')[2][4:6])
        day = int(filename.split('_')[2][6:8])
        hour = int(filename.split('_')[2][8:10])
        stationID = filename.split('_')[-1]
        stationID_ZM=stationID.upper()+'ZM'
        
        instrument = 'ISM01'
        #product = 'IfoF2'
        #product = 'ICF'        
        product = 'IS4'                
        #level = 'L21'
        level = 'L11'        
        segement = '72H'
        
        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join([stationID_ZM, instrument, product, level, segement, YYYYMMDDhhmmss])
        # productpath = self.outputpath + prefix + suffix
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
        
        #YYYYMMDDhh = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H")
        
        # 读入fmin数据,foF2数据
        data_L = IONO.CET.ISM.read_CET_ISM_S4.read_data_SintL(file_sintL)
        data_U = IONO.CET.ISM.read_CET_ISM_S4.read_data_SintUHF(file_sintUHF)

        #station_name = station_id_name[stationID]
        #DateTime = datetime.datetime(year, month, day, hour)
        #datestr = datetime.datetime(year, month, day, hour).strftime("%Y-%m-%d %H")
        IONO.CET.ISM.read_CET_ISM_S4.plot_data(data_L,data_U,productpath)
        return productpath

        
    def cal_FDS_ISM_vTEC_main(self, inputfile, rootpath):
        
        #debug_log('cal_FDS_ISM_vTEC_main')
        ##判断stationID是CDZ
        ##stationID目前没有用，固定是3个字段，CDZ，CDZJ,CDZM需要从任意inputfile里截取第1个字符串

        # input: foF2_2019071608_1.dat
        # output: XXXM_ION01_IfoF2mappre01H_L31_72H_20190716080000.png

        # inputfile = self.inputfile  ##筛选好的1个单站的4个txt文件
        for file in inputfile:
            ####检查路径的合法性
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                #return ''
                raise Exception(self.errorinfo)
        #stations = IONO.FDS.ISM.station_info.get_FDS_station_info()
        #stations = station.station_info.get_FDS_station_info()
        #print (inputfile)
        inputfilepath, inputfilename = os.path.split(inputfile[0])
        filename, suffix = inputfilename.split('.')
        stationID = (filename.split('_')[0]) ####4位，XXXJ，而不是3位，XXX
        #print (filename)
        year = int(filename.split('_')[-1][0:4])
        month = int(filename.split('_')[-1][4:6])
        day = int(filename.split('_')[-1][6:8])
        hour = int(filename.split('_')[-1][8:10])
        
        # print (year )
        # print (month)
        # print (day)
        # print (hour)
        ####计算单个站的硬件误差
        #IONO.FDS.ISM.cal_FDS_ISM_iTEC_error.cal_all_stations_HardWare_error(year, month, day)
        #IONO.FDS.ISM.cal_FDS_ISM_iTEC_error.cal_stations_HardWare_error(rootpath,stationID,year, month, day)
        #debug_log('begin IONO.FDS.ISM.cal_FDS_ISM_iTEC_error.cal_stations_HardWare_error')
        IONO.FDS.ISM.cal_FDS_ISM_iTEC_error.cal_stations_HardWare_error(rootpath, stationID, year, month, day,hour)
        err = '%s%s%s%s%s' % (__file__, ',LINE ', sys._getframe().f_lineno, ',', 'end IONO.FDS.ISM.cal_FDS_ISM_iTEC_error.cal_stations_HardWare_error')
        #debug_log(err)
        
        
        # 2，依次读取4个文件的数据并拼合，4个文件在同1个路径下，日期格式一致
        #debug_log('begin IONO.FDS.ISM.cal_FDS_ISM_vTEC.read_data')
        data_01h_4GNSS = {}
        for fullpath in inputfile:
            data_01h_1GNSS = IONO.FDS.ISM.cal_FDS_ISM_vTEC.read_data(fullpath)
            data_01h_4GNSS = IONO.FDS.ISM.cal_FDS_ISM_vTEC.merge_dict(data_01h_4GNSS, data_01h_1GNSS)
            # print(sorted(data_01h_4GNSS.keys()))
            # print(data_01h_4GNSS['BD01'])'
        #debug_log('end IONO.FDS.ISM.cal_FDS_ISM_vTEC.read_data')
        
        # 3，依据不同卫星的斜向TEC换算单站垂直TEC
        ## 读取之前生成的误差文件，如果文件没有不存在，则err变量默认是0，不剔除硬件误差
        #debug_log('begin ONO.FDS.ISM.cal_FDS_ISM_vTEC.cal_station_vTEC')
        station_vTECs = IONO.FDS.ISM.cal_FDS_ISM_vTEC.cal_station_vTEC(rootpath,stationID, year, month, day, hour,
                                                                        data_01h_4GNSS)
        #debug_log('end ONO.FDS.ISM.cal_FDS_ISM_vTEC.cal_station_vTEC')                                                                        
        
        # 4，保存单台站垂直TEC
        #debug_log('begin IONO.FDS.ISM.cal_FDS_ISM_vTEC.get_savepath')
        productpath = IONO.FDS.ISM.cal_FDS_ISM_vTEC.get_savepath(rootpath, stationID, year, month, day, hour)
        # L1级生成的txt文件是L2级的数据
        productpath = self.match_profile(productpath)
        
        IONO.FDS.ISM.cal_FDS_ISM_vTEC.save_vTEC(station_vTECs, productpath)
        #debug_log('end IONO.FDS.ISM.cal_FDS_ISM_vTEC.save_vTEC')
        
        ##输出路径，返回给输出xml文件
        #productpath = savepath
        return productpath


    def read_FDS_ISM_TEC_main(self, inputfile1, inputfile2, rootpath):
        # input: foF2_2019071608_1.dat
        # output: XXXM_ION01_IfoF2mappre01H_L31_72H_20190716080000.png

        # inputfile = self.inputfile  ##筛选好的1个单站的4个txt文件
        ##需要只需要判断L2文件合法性，L1合法性在L1级产品生产已经判断，不需要重复判断
        for file in inputfile2:
            ####检查路径的合法性
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                #return ''
                raise Exception(self.errorinfo)
        #stations = IONO.FDS.ISM.station_info.get_FDS_station_info()
        #stations = station.station_info.get_FDS_station_info()
        ####png产品日期按L1级文件名截取
        inputfilepath, inputfilename = os.path.split(inputfile1[0])
        filename, suffix = inputfilename.split('.')

        stationID = (filename.split('_')[0])
        year = int(filename.split('_')[-1][0:4])
        month = int(filename.split('_')[-1][4:6])
        day = int(filename.split('_')[-1][6:8])
        hour = int(filename.split('_')[-1][8:10])

        xrange = 72
        # 2，依次读取72个文件的数据并拼合
        data_72h = {}
        ####实际测试发现，inputfile2不区分时间的先后顺序，绘图会更加时间对应的点，绘图
        for fullpath in inputfile2:
            data_01h = IONO.FDS.ISM.read_FDS_ISM_TEC.read_data(fullpath)
            data_72h = IONO.FDS.ISM.read_FDS_ISM_TEC.merge_dict(data_72h, data_01h)

        # 4，保存单台站垂直TEC
        productpath = IONO.FDS.ISM.read_FDS_ISM_TEC.get_savepath(rootpath, stationID, year, month, day, hour, xrange)
        # 不需要match路径，因为L2级的输入数据是L1级的产品路径，FDSpro，如果路径映射报错
        #print(savepath)
        productpath = self.match_profile(productpath)
        
        # (path, filename) = os.path.split(savepath)
        # if not os.path.exists(path):
        #     os.makedirs(path)
        # print('begin  IONO.FDS.read_FDS_ISM_TEC.plot_TEC...')
        IONO.FDS.ISM.read_FDS_ISM_TEC.plot_TEC(stationID, year, month, day, hour, xrange, data_72h, productpath)

        #productpath = savepath
        return productpath
    
    
    def read_CET_ISM_TEC_krig_main(self, inputfile):        
    #def read_CET_ISM_TEC_krig_main(self, inputfile,outputXMLpath):
        productpath = ''
        # input: foF2_2019071608_1.dat
        # output: XXXM_ION01_IfoF2mappre01H_L31_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        for file in inputfile:
            ####检查路径的合法性
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                #return ''
                raise Exception(self.errorinfo)
        ####从任意一个台站的TEC文件名中截取日期
        inputfilepath, inputfilename = os.path.split(inputfile[0])

        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[1][0:4])
        month = int(filename.split('_')[1][4:6])
        day = int(filename.split('_')[1][6:8])
        hour = int(filename.split('_')[1][8:10])
        yyyymm = filename.split('_')[1][0:6]
        yyyymmdd = filename.split('_')[1][0:8]
        yyyymmddhh = filename.split('_')[1][0:10]

        # 收集单台站数据
        #stations = IONO.CET.ISM.station_infos.get_CETC22_station_infos()
        #stations = station.station_infos.get_CETC22_station_infos()
        ####从inputfile里截取每个小时的的时间
        #coord_station, TEC_station = IONO.CET.ISM.read_CET_ISM_TEC_krig.gather_station_data(inputfile, year, month, day, hour, stations)
        coord_station, TEC_station = IONO.CET.ISM.read_CET_ISM_TEC_krig.gather_station_data(inputfile, year, month, day, hour)
        
        # 校正单台站数据，正态分布
        #TEC_station_adj = IONO.CET.ISM.read_CET_ISM_TEC_krig.adjust_data(TEC_station, rate=1.0)
        TEC_station_adj = IONO.CET.ISM.read_CET_ISM_TEC_krig.adjust_data(TEC_station, rate=2.0)
        
        ##调用fortran程序，产生iri的网格数据
        iri_inputpath = configs['iri_inputpath']
        #iri_outputrootpath = configs['outputfilepath']
        Fortran_path = configs['Fortran_path']
        ##cmd拼接fortran调用命令，第1个参数年月日小时，第2个参数输出网格数据文件的路径
        ##10s之内产生，TEC地基，22所，共用iri格点数据，是否需要先判断是否存在
        ##根据iri_rootpath创建YYYYMM/YYYYMMDD的文件夹
        ##路径末尾拼接空字符串，或多\\或者/，避免fortran里拼接路径丢失/或者\\
        
        ##方案1，根据输入数据台站，同1级目录，建立MIXT文件夹，IRI网格数据目录
        # mix_path = inputfilepath.replace(inputfilepath[-4:],'MIXT')
        # iri_outputpath = os.path.join(mix_path, '')
        
        ##方案2，IRI网格数据放到共享目录，提前生产下1天的数据，比如20200421，生产20200422日期的IRI
        iri_outputpath = configs['iri_outputpath']
        iri_outputpath = os.path.join(iri_outputpath,yyyymm,yyyymmdd,'')#拼接年月，年月日文件夹,''保证路径最后保留斜杠
        

        #iri_outputpath = os.path.join(iri_outputrootpath, 'IRI', 'IONO', 'ISM', yyyymm, yyyymmdd, 'MIXT', '')
        # iri_outputpath = os.path.join(iri_outputrootpath,yyyymm,yyyymmdd)
        ####需要判断，存在不需要创建，否则报错
        if not os.path.exists(iri_outputpath):
            print('%s do not exist ' % iri_outputpath)
            print('makedirs...')
            os.makedirs(iri_outputpath)
        else:
            pass

        ##导入iri模型背景数据
        ##根据指定的目录结构规则搜索TEC当前小时对应的17个台站的数据，任意1个台站数据
        inputfilepath, inputfilename = os.path.split(inputfile[0])
        ####输出png图形使用xml输出路径MIX文件夹
        #XMLpath,XMLfile = os.path.split(outputXMLpath)
        
        ## IRI共享路径不能存放MIXM的png产品，和输入数据路径同1级台站建立MIXM文件夹
        ## self.outputpath = iri_outputpath  ##输出png图形的路径和输入txt路径一致
        #mix_path = inputfilepath.replace(inputfilepath[-4:],'MIXM')
        
        mix_path =  os.path.dirname(inputfilepath) + '/' + 'MIXM'
        self.outputpath  = os.path.join(mix_path, '')        
        
        
        filename, suffix = inputfilename.split('.')
        # iri_dir = os.path.join(iri_path,'TEC',yyyymm,yyyymmdd)
        ##增加iri文件判断，如果存在，直接跳过，不用生产
        iri_fullpath = IONO.CET.ISM.read_CET_ISM_TEC_krig.get_iri_fullpath(iri_outputpath, year, month, day, hour)
        if ('Windows' == platform.system()):
            filesize = 132130
        if ('Linux' == platform.system()):
            filesize = 131949
        if not os.path.exists(iri_fullpath) or os.path.getsize(iri_fullpath) < filesize:
            ##如果IRI文件不存在或者IRI文件里得网格不完整，需要重新生产IRI文件
            CMD = Fortran_path + ' ' + yyyymmddhh + ' ' + iri_inputpath + ' ' + iri_outputpath
            print(CMD)
            try:
                # pass
                status = os.system(CMD)
                print("os.system status is %d " % status)
            except Exception as e:
                raise e
                
        ####读取IRI网格数据
        iri_file, coord_iri, TEC_iri = IONO.CET.ISM.read_CET_ISM_TEC_krig.get_iri_data(iri_outputpath, year, month, day, hour)        
        #coord_iri, TEC_iri = IONO.CET.ISM.read_CET_ISM_TEC_krig.get_iri_data(iri_outputpath, year, month, day, hour)
        if coord_iri==[]:
            #return
            err = '%s%s%s%s%s' % (__file__, ',LINE ', sys._getframe().f_lineno, ',', 'coord_iri==[]')
            raise Exception(err)
                    
        # print(coord_iri.shape,TEC_iri.shape)
        # 融合iri模型背景数据
        if coord_station.shape != (0, 2):
            coord_fused, TEC_fused = IONO.CET.ISM.read_CET_ISM_TEC_krig.fuse_data(iri_file,coord_station, TEC_station_adj,coord_iri, TEC_iri)        
            #coord_fused, TEC_fused = IONO.CET.ISM.read_CET_ISM_TEC_krig.fuse_data(coord_station, TEC_station_adj,coord_iri, TEC_iri)
        else:
            ##自定义异常
            err = '%s%s%s%s%s' % (__file__, ',LINE ', sys._getframe().f_lineno, ',', 'coord_station.shape == (0, 2)')
            raise Exception(err)

            # return err,productpath

        # 再次校正数据，正态分布
        print ('再次校正数据，正态分布......')
        TEC_fused_adj = IONO.CET.ISM.read_CET_ISM_TEC_krig.adjust_data(TEC_fused, rate=3.0)

        # 生成中国区域分布
        # lon2d,lat2d,TECmap=gen_map(coord_station,TEC_station)
        # lon2d,lat2d,TECmap=gen_map(coord_fused,TEC_fused)
        print ('gen_map......')        
        lon2d, lat2d, TECmap = IONO.CET.ISM.read_CET_ISM_TEC_krig.gen_map(coord_fused, TEC_fused_adj)

        # 插值结果滤波平滑
        print ('开始插值 filter_data......')
        TECmap = IONO.CET.ISM.read_CET_ISM_TEC_krig.filter_data(TECmap)

        # 制作中国区域地图
        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H%M%S")

        #prefix = 'MIXM_ISM00_ITECmap_L31_STP_' + YYYYMMDDhhmmss
        prefix = 'MIXM_ISM00_ITEC_L31_STP_' + YYYYMMDDhhmmss
        #prefix = 'MIXT_ISM00_ITECmap_L31_STP_' + YYYYMMDDhhmmss
        # prefix = 'MIXT_IRI00_DTEC_L31_STP_' + YYYYMMDDhhmmss
        suffix = '.png'
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
        
        IONO.CET.ISM.read_CET_ISM_TEC_krig.plot_data(year, month, day, hour, coord_station, TEC_station, lon2d, lat2d,
                                                     TECmap, productpath)
        # plot_data(year,month,day,hour,coord_fused,TEC_fused,lon2d,lat2d,TECmap,savepath)

        # productpath = savepath
        print ('productpath = %s'%productpath)
        return productpath


    def read_FDS_ISM_TEC_krig_main(self, inputfile):
        productpath = ''
        # input: foF2_2019071608_1.dat
        # output: XXXM_ION01_IfoF2mappre01H_L31_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        for file in inputfile:
            ####检查路径的合法性
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                #return ''
                raise Exception(self.errorinfo)
        ####从任意一个台站的TEC文件名中截取日期
        inputfilepath, inputfilename = os.path.split(inputfile[0])
        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[-1][0:4])
        month = int(filename.split('_')[-1][4:6])
        day = int(filename.split('_')[-1][6:8])
        hour = int(filename.split('_')[-1][8:10])
        yyyymm = filename.split('_')[-1][0:6]
        yyyymmdd = filename.split('_')[-1][0:8]
        yyyymmddhh = filename.split('_')[-1][0:10]

        # 收集单台站数据
        # station_infos带经纬度
        #stations = station.station_infos.get_FDS_station_infos()
        #stations = station.station_infos.get_FDS_station_infos()
        #stations = IONO.FDS.ISM.station_infos.get_FDS_station_infos()
        ####从inputfile里截取每个小时的的时间
        #coord_station, TEC_station = IONO.FDS.ISM.read_FDS_ISM_TEC_krig.gather_station_data(inputfile, year, month, day,hour, stations)
        coord_station, TEC_station = IONO.FDS.ISM.read_FDS_ISM_TEC_krig.gather_station_data(inputfile, year, month, day,hour)
        
        # 校正单台站数据，正态分布
        print ('校正单台站数据，正态分布......')
        #TEC_station_adj = IONO.FDS.ISM.read_FDS_ISM_TEC_krig.adjust_data(TEC_station, rate=1.0)
        TEC_station_adj = IONO.FDS.ISM.read_FDS_ISM_TEC_krig.adjust_data(TEC_station, rate=3.0)

        ##调用fortran程序，产生iri的网格数据
        iri_inputpath = configs['iri_inputpath']
        #iri_outputrootpath = configs['outputfilepath']
        Fortran_path = configs['Fortran_path']
        ##cmd拼接fortran调用命令，第1个参数年月日小时，第2个参数输出网格数据文件的路径
        ##10s之内产生，TEC地基，22所，共用iri格点数据，是否需要先判断是否存在
        ##根据iri_rootpath创建YYYYMM/YYYYMMDD的文件夹
        ##路径末尾拼接空字符串，或多\\或者/，避免fortran里拼接路径丢失/或者\\
        #iri_outputpath = os.path.join(iri_outputrootpath, 'IRI', 'IONO', 'ISM', yyyymm, yyyymmdd, 'MIXT', '')
        
        ##方案1，本地临时数据目录，每次根据传入的
        # mix_path = inputfilepath.replace(inputfilepath[-4:],'MIXT')
        # iri_outputpath = os.path.join(mix_path, '')        
        ##方案1，根据输入数据台站，同1级目录，建立MIXT文件夹，IRI网格数据目录
        # mix_path = inputfilepath.replace(inputfilepath[-4:],'MIXT')
        # iri_outputpath = os.path.join(mix_path, '')
        
        ##方案2，IRI网格数据放到共享目录，提前生产下1天的数据，比如20200421，生产20200422日期的IRI
        iri_outputpath = configs['iri_outputpath']
        iri_outputpath = os.path.join(iri_outputpath,yyyymm,yyyymmdd,'')#拼接年月，年月日文件夹,''保证路径最后保留斜杠
        
        # iri_outputpath = os.path.join(iri_outputrootpath,yyyymm,yyyymmdd)
        ####需要判断，存在不需要创建，否则报错
        if not os.path.exists(iri_outputpath):
            print('%s do not exist ' % iri_outputpath)
            print('makedirs...')
            os.makedirs(iri_outputpath)
        else:
            pass
            
        ##导入iri模型背景数据
        ##根据指定的目录结构规则搜索TEC当前小时对应的17个台站的数据
        inputfilepath, inputfilename = os.path.split(inputfile[0])
        #self.outputpath = inputfilepath  ##输出png图形的路径和输入txt路径一致
        ####输出png图形使用xml输出路径MIX文件夹
        
        ## self.outputpath = iri_outputpath  ##输出png图形的路径和输入txt路径一致
        ## self.outputpath = iri_outputpath  ##输出png图形的路径和输入txt路径一致
        mix_path = inputfilepath.replace(inputfilepath[-4:],'MIXJ')
        self.outputpath  = os.path.join(mix_path, '')
        print ('融合产品路径 %s' % self.outputpath)
                
        
        filename, suffix = inputfilename.split('.')
        ##增加iri文件判断，如果存在，直接跳过，不用生产
        iri_fullpath = IONO.FDS.ISM.read_FDS_ISM_TEC_krig.get_iri_fullpath(iri_outputpath, year, month, day, hour)
        if ('Windows' == platform.system()):
            filesize = 132130
        if ('Linux' == platform.system()):
            filesize = 131949
        if not os.path.exists(iri_fullpath) or os.path.getsize(iri_fullpath) < filesize:
            ##如果IRI文件不存在或者IRI文件里得网格不完整，需要重新生产IRI文件
            CMD = Fortran_path + ' ' + yyyymmddhh + ' ' + iri_inputpath + ' ' + iri_outputpath
            print(CMD)
            try:
                # pass
                status = os.system(CMD)
                print("os.system status is %d " % status)
            except Exception as e:
                raise e
                
        ####读取IRI网格数据
        iri_file,coord_iri, TEC_iri = IONO.FDS.ISM.read_FDS_ISM_TEC_krig.get_iri_data(iri_outputpath, year, month, day, hour)
        # print(coord_iri.shape,TEC_iri.shape)

        # 融合iri模型背景数据
        if coord_station.shape != (0, 2):
            coord_fused, TEC_fused = IONO.FDS.ISM.read_FDS_ISM_TEC_krig.fuse_data(iri_file,coord_station, TEC_station_adj,
                                                                                  coord_iri, TEC_iri)
        else:
            ##自定义异常
            err = '%s%s%s%s%s' % (__file__, ',LINE ', sys._getframe().f_lineno, ',', 'coord_station.shape == (0, 2)')
            raise Exception(err)

            # return err,productpath

        # 再次校正数据，正态分布
        TEC_fused_adj = IONO.FDS.ISM.read_FDS_ISM_TEC_krig.adjust_data(TEC_fused, rate=3.0)

        # 生成中国区域分布
        # lon2d,lat2d,TECmap=gen_map(coord_station,TEC_station)
        # lon2d,lat2d,TECmap=gen_map(coord_fused,TEC_fused)
        print ('生成中国区域分布 gen_map......')
        lon2d, lat2d, TECmap = IONO.FDS.ISM.read_FDS_ISM_TEC_krig.gen_map(coord_fused, TEC_fused_adj)

        # 插值结果滤波平滑
        TECmap = IONO.FDS.ISM.read_FDS_ISM_TEC_krig.filter_data(TECmap)

        # 制作中国区域地图
        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H%M%S")

        #prefix = 'MIXJ_ISM00_ITECmap_L31_STP_' + YYYYMMDDhhmmss
        prefix = 'MIXJ_ISM00_ITEC_L31_STP_' + YYYYMMDDhhmmss
        # prefix = 'MIXT_ISM00_ITECmap_L31_STP_' + YYYYMMDDhhmmss
        # prefix = 'MIXT_IRI00_DTEC_L31_STP_' + YYYYMMDDhhmmss
        suffix = '.png'
        ##产品路径，需要判断存在与否
        if not os.path.exists(self.outputpath):
            os.makedirs(self.outputpath)
        else:
            print ('路径存在，%s'% self.outputpath)
        productpath = os.path.join(self.outputpath, prefix + suffix)

        #productpath = self.match_profile(productpath)
        
        coord_station20,TEC_station20 = IONO.FDS.ISM.read_FDS_ISM_TEC_krig.gather_station20_background()
        
        IONO.FDS.ISM.read_FDS_ISM_TEC_krig.plot_data(year, month, day, hour, coord_station20, TEC_station20, coord_station, TEC_station, lon2d, lat2d,
                                                     TECmap, productpath)
        # plot_data(year,month,day,hour,coord_fused,TEC_fused,lon2d,lat2d,TECmap,savepath)

        # productpath = savepath
        print (productpath)
        return productpath

    def read_FDS_ISM_scint_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里
        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        ####根据inputfile重新按时间顺序排序，从大到小的时间顺序
        #print (inputfile)
        inputfile0 = {}
        for file in inputfile:
            inputfilepath, inputfilename = os.path.split(file)
            filename, suffix = inputfilename.split('.')
            yymmddHHMMSS = filename.split('_')[-1]
            #print (yymmddHHMMSS)
            if yymmddHHMMSS not in inputfile0.keys():
                inputfile0[yymmddHHMMSS] = [file]
            else:
                inputfile0[yymmddHHMMSS].append(file)
        
        #print ( inputfile0)
        ##按key值从大到小排序
        inputfile1 = sorted(inputfile0.items(), key=lambda d: d[0], reverse=True)
        #print (inputfile1)
        ##提取出72小时，最大日期的时间
        max_inputfile = inputfile1[0][1][0]  # 获取列表第1个元素，元祖中第1个元素的第1个元素
        # max_inputfile_yymmddHHMMSS = inputfile1[0][0]#获取列表第1个元素，第1个元祖第1个元素

        # stations = IONO.FDS.ISM.station_info.get_FDS_station_info()
        inputfilepath, inputfilename = os.path.split(max_inputfile)
        self.outputpath = inputfilepath

        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[-1][0:4])
        month = int(filename.split('_')[-1][4:6])
        day = int(filename.split('_')[-1][6:8])
        hour = int(filename.split('_')[-1][8:10])
        stationID = filename.split('_')[0]  ##包括J，4位字符串

        instrument = 'ISM01'
        #instrument = 'ION01'
        product = 'IS4'
        #level = 'L11'
        #level = 'L21'##L21,L31需要fix
        level = 'L11'##L21,L31需要fix        
        segement = '72H'
        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join([stationID, instrument, product, level, segement, YYYYMMDDhhmmss])
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
        
        YYYYMMDDhh = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H")

        # 2，依次读取单个文件的数据并拼合
        xrange = 72
        data_72h = {}
        for fullpath in inputfile:
            data_01h = IONO.FDS.ISM.read_FDS_ISM_scint.read_data(fullpath)
            data_72h = IONO.FDS.ISM.read_FDS_ISM_scint.merge_dict(data_72h, data_01h)

        # 3，获取闪烁指数S4时序图的保存路径
        IONO.FDS.ISM.read_FDS_ISM_scint.plot_scint(stationID, year, month, day, hour, xrange, data_72h, productpath)

        return productpath
        
    def read_FDS_ISM_scint_alert_main(self, inputfile):
        print ('into  read_FDS_ISM_scint_alert_main...')
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里
        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        ####根据inputfile重新按时间顺序排序，从大到小的时间顺序
        inputfile0 = {}
        for file in inputfile:
            inputfilepath, inputfilename = os.path.split(file)
            filename, suffix = inputfilename.split('.')
            yymmddHHMMSS = filename.split('_')[-1]
            if yymmddHHMMSS not in inputfile0.keys():
                inputfile0[yymmddHHMMSS] = [file]
            else:
                inputfile0[yymmddHHMMSS].append(file)
        ##按key值从大到小排序
        inputfile1 = sorted(inputfile0.items(), key=lambda d: d[0], reverse=True)

        ##提取出72小时，最大日期的时间
        max_inputfile = inputfile1[0][1][0]  # 获取列表第1个元素，元祖中第1个元素的第1个元素
        # max_inputfile_yymmddHHMMSS = inputfile1[0][0]#获取列表第1个元素，第1个元祖第1个元素

        # stations = IONO.FDS.ISM.station_info.get_FDS_station_info()
        inputfilepath, inputfilename = os.path.split(max_inputfile)
        self.outputpath = inputfilepath

        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[-1][0:4])
        month = int(filename.split('_')[-1][4:6])
        day = int(filename.split('_')[-1][6:8])
        hour = int(filename.split('_')[-1][8:10])
        stationID = filename.split('_')[0]  ##包括J，4位字符串

        instrument = 'ISM01'
        #instrument = 'ION01'
        #product = 'IS4alert'
        product = 'IS4A'        
        level = 'L21'##L21,L31需要fix
        #level = 'L11'
        segement = '01H'
        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join([stationID, instrument, product, level, segement, YYYYMMDDhhmmss])
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
        
        
        YYYYMMDDhh = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H")

        # 2，依次读取单个文件的数据并拼合
        xrange = 1
        data_72h = {}
        for fullpath in inputfile:
            data_01h = IONO.FDS.ISM.read_FDS_ISM_scint_alert.read_data(fullpath)
            data_72h = IONO.FDS.ISM.read_FDS_ISM_scint_alert.merge_dict(data_72h, data_01h)

        # 3，获取闪烁指数S4时序图的保存路径
        IONO.FDS.ISM.read_FDS_ISM_scint_alert.plot_scint(stationID, year, month, day, hour, xrange, data_72h, productpath)

        return productpath   
        
    def read_FDS_ISM_alert_main(self, inputfile):
        print ('into  read_FDS_ISM_alert_main...')
        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)
                
        inputfilepath, inputfilename = os.path.split(inputfile[0])
        self.outputpath = inputfilepath[:-4] + 'MIXJ'
                
        filename, suffix = inputfile[0].split('.')
        year = int(filename.split('_')[-1][0:4])
        month = int(filename.split('_')[-1][4:6])
        day = int(filename.split('_')[-1][6:8])
        hour = int(filename.split('_')[-1][8:10])

        # 获取图像产品的保存全路径，
        instrument = 'ISM01'
        product = 'IS4A'        
        level = 'L31'##L21,L31需要fix
        segement = '01H'
        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join(['MIXJ', instrument, product, level, segement, YYYYMMDDhhmmss])
        savepath = os.path.join(self.outputpath, prefix + suffix)
        savepath = self.match_profile(savepath)
        
        # 绘制电离层闪烁指数区域散点图
        IONO.FDS.ISM.read_FDS_ISM_scint_map.plot_all_stations_scint(year,month,day,hour,inputfile,savepath)
        
        productpath = savepath
        
        return productpath       
        

    def read_FDS_ION_fmin_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里
        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        ####根据inputfile重新按时间顺序排序，从大到小的时间顺序
        inputfile0 = {}
        for file in inputfile:
            inputfilepath, inputfilename = os.path.split(file)
            filename, suffix = inputfilename.split('.')
            yymmddHHMMSS = filename.split('_')[-1]
            if yymmddHHMMSS not in inputfile0.keys():
                inputfile0[yymmddHHMMSS] = [file]
            else:
                inputfile0[yymmddHHMMSS].append(file)
        ##按key值从大到小排序
        inputfile1 = sorted(inputfile0.items(), key=lambda d: d[0], reverse=True)

        ##提取出72小时，最大日期的时间
        max_inputfile = inputfile1[0][1][0]  # 获取列表第1个元素，元祖中第1个元素的第1个元素
        # max_inputfile_yymmddHHMMSS = inputfile1[0][0]#获取列表第1个元素，第1个元祖第1个元素

        # stations = IONO.FDS.ISM.station_info.get_FDS_station_info()
        inputfilepath, inputfilename = os.path.split(max_inputfile)
        self.outputpath = inputfilepath

        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[-1][0:4])
        month = int(filename.split('_')[-1][4:6])
        day = int(filename.split('_')[-1][6:8])
        hour = int(filename.split('_')[-1][8:10])
        min = int(filename.split('_')[-1][10:12])
        stationID = filename.split('_')[0]  ##包括J，4位字符串

        instrument = 'ION01'
        product = 'Ifmin'
        level = 'L21'
        segement = '72H'
        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour, min).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join([stationID, instrument, product, level, segement, YYYYMMDDhhmmss])
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
        
        # YYYYMMDDhh = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H")

        # 2，依次读取单个文件的数据并拼合
        xrange = 72
        data_72h = {}
        # inputfile不需要按时间顺序，绘图可以不用连续绘，各自绘制各自时间段，但最后都绘制到1个fig上即可
        for fullpath in inputfile:
            data_15m = IONO.FDS.ION.read_FDS_ION_fmin.read_data(fullpath)
            data_72h = IONO.FDS.ION.read_FDS_ION_fmin.merge_dict(data_72h, data_15m)

        # 3. 获取fmi时序图的保存路径
        IONO.FDS.ION.read_FDS_ION_fmin.plot_data(stationID, year, month, day, hour, min, xrange, data_72h, productpath)
        return productpath

    def read_FDS_ION_foF2_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里
        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        ####根据inputfile重新按时间顺序排序，从大到小的时间顺序
        inputfile0 = {}
        for file in inputfile:
            inputfilepath, inputfilename = os.path.split(file)
            filename, suffix = inputfilename.split('.')
            yymmddHHMMSS = filename.split('_')[-1]
            if yymmddHHMMSS not in inputfile0.keys():
                inputfile0[yymmddHHMMSS] = [file]
            else:
                inputfile0[yymmddHHMMSS].append(file)
        ##按key值从大到小排序
        inputfile1 = sorted(inputfile0.items(), key=lambda d: d[0], reverse=True)

        ##提取出72小时，最大日期的时间
        max_inputfile = inputfile1[0][1][0]  # 获取列表第1个元素，元祖中第1个元素的第1个元素
        # max_inputfile_yymmddHHMMSS = inputfile1[0][0]#获取列表第1个元素，第1个元祖第1个元素

        # stations = IONO.FDS.ISM.station_info.get_FDS_station_info()
        inputfilepath, inputfilename = os.path.split(max_inputfile)
        self.outputpath = inputfilepath

        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[-1][0:4])
        month = int(filename.split('_')[-1][4:6])
        day = int(filename.split('_')[-1][6:8])
        hour = int(filename.split('_')[-1][8:10])
        min = int(filename.split('_')[-1][10:12])
        stationID = filename.split('_')[0]  ##包括J，4位字符串

        instrument = 'ION01'
        product = 'IfoF2'
        level = 'L21'
        segement = '72H'
        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour, min).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join([stationID, instrument, product, level, segement, YYYYMMDDhhmmss])
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
        
        # YYYYMMDDhh = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H")

        # 2，依次读取单个文件的数据并拼合
        xrange = 72
        data_72h = {}
        # inputfile不需要按时间顺序，绘图可以不用连续绘，各自绘制各自时间段，但最后都绘制到1个fig上即可
        for fullpath in inputfile:
            data_15m = IONO.FDS.ION.read_FDS_ION_foF2.read_data(fullpath)
            data_72h = IONO.FDS.ION.read_FDS_ION_foF2.merge_dict(data_72h, data_15m)

        # 3. 获取fmi时序图的保存路径
        IONO.FDS.ION.read_FDS_ION_foF2.plot_data(stationID, year, month, day, hour, min, xrange, data_72h, productpath)
        return productpath

    def read_FDS_ION_MUF_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里
        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        ####根据inputfile重新按时间顺序排序，从大到小的时间顺序
        inputfile0 = {}
        for file in inputfile:
            inputfilepath, inputfilename = os.path.split(file)
            filename, suffix = inputfilename.split('.')
            yymmddHHMMSS = filename.split('_')[-1]
            if yymmddHHMMSS not in inputfile0.keys():
                inputfile0[yymmddHHMMSS] = [file]
            else:
                inputfile0[yymmddHHMMSS].append(file)
        ##按key值从大到小排序
        inputfile1 = sorted(inputfile0.items(), key=lambda d: d[0], reverse=True)

        ##提取出72小时，最大日期的时间
        max_inputfile = inputfile1[0][1][0]  # 获取列表第1个元素，元祖中第1个元素的第1个元素
        # max_inputfile_yymmddHHMMSS = inputfile1[0][0]#获取列表第1个元素，第1个元祖第1个元素

        # stations = IONO.FDS.ISM.station_info.get_FDS_station_info()
        inputfilepath, inputfilename = os.path.split(max_inputfile)
        self.outputpath = inputfilepath

        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[-1][0:4])
        month = int(filename.split('_')[-1][4:6])
        day = int(filename.split('_')[-1][6:8])
        hour = int(filename.split('_')[-1][8:10])
        min = int(filename.split('_')[-1][10:12])
        stationID = filename.split('_')[0]  ##包括J，4位字符串

        instrument = 'ION01'
        product = 'IMUF'
        level = 'L21'
        segement = '72H'
        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour, min).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join([stationID, instrument, product, level, segement, YYYYMMDDhhmmss])
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
        
        # YYYYMMDDhh = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H")

        # 2，依次读取单个文件的数据并拼合
        xrange = 72
        data_72h = {}
        # inputfile不需要按时间顺序，绘图可以不用连续绘，各自绘制各自时间段，但最后都绘制到1个fig上即可
        for fullpath in inputfile:
            data_15m = IONO.FDS.ION.read_FDS_ION_MUF.read_data(fullpath)
            data_72h = IONO.FDS.ION.read_FDS_ION_MUF.merge_dict(data_72h, data_15m)

        # 3. 获取fmi时序图的保存路径
        IONO.FDS.ION.read_FDS_ION_MUF.plot_data(stationID, year, month, day, hour, min, xrange, data_72h, productpath)
        return productpath

    def read_FDS_ION_scaled_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里
        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        ####根据inputfile重新按时间顺序排序，从大到小的时间顺序
        inputfile0 = {}
        for file in inputfile:
            inputfilepath, inputfilename = os.path.split(file)
            filename, suffix = inputfilename.split('.')
            yymmddHHMMSS = filename.split('_')[-1]
            if yymmddHHMMSS not in inputfile0.keys():
                inputfile0[yymmddHHMMSS] = [file]
            else:
                inputfile0[yymmddHHMMSS].append(file)
        ##按key值从大到小排序
        inputfile1 = sorted(inputfile0.items(), key=lambda d: d[0], reverse=True)

        ##提取出72小时，最大日期的时间
        max_inputfile = inputfile1[0][1][0]  # 获取列表第1个元素，元祖中第1个元素的第1个元素
        # max_inputfile_yymmddHHMMSS = inputfile1[0][0]#获取列表第1个元素，第1个元祖第1个元素

        # stations = IONO.FDS.ISM.station_info.get_FDS_station_info()
        inputfilepath, inputfilename = os.path.split(max_inputfile)
        self.outputpath = inputfilepath

        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[-1][0:4])
        month = int(filename.split('_')[-1][4:6])
        day = int(filename.split('_')[-1][6:8])
        hour = int(filename.split('_')[-1][8:10])
        min = int(filename.split('_')[-1][10:12])
        stationID = filename.split('_')[0]  ##包括J，4位字符串

        instrument = 'ION01'
        #product = 'Ifre'
        product = 'ICF'        
        level = 'L21'
        segement = '72H'
        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour, min).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join([stationID, instrument, product, level, segement, YYYYMMDDhhmmss])
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
        
        # YYYYMMDDhh = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H")

        # 2，依次读取单个文件的数据并拼合
        xrange = 72
        data_72h = {}
        # inputfile不需要按时间顺序，绘图可以不用连续绘，各自绘制各自时间段，但最后都绘制到1个fig上即可
        for fullpath in inputfile:
            data_15m = IONO.FDS.ION.read_FDS_ION_scaled.read_data(fullpath)
            data_72h = IONO.FDS.ION.read_FDS_ION_scaled.merge_dict(data_72h, data_15m)

        # 3. 获取fmi时序图的保存路径
        IONO.FDS.ION.read_FDS_ION_scaled.plot_data(stationID, year, month, day, hour, min, xrange, data_72h, productpath)
        return productpath

       
    def read_FDS_ION_edp_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里
        
        ####存放密度剖面图和频高图
        productpath_list=[]
        
        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        # stations = IONO.FDS.ISM.station_info.get_FDS_station_info()
        inputfilepath, inputfilename = os.path.split(file)
        self.outputpath = inputfilepath

        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[-1][0:4])
        month = int(filename.split('_')[-1][4:6])
        day = int(filename.split('_')[-1][6:8])
        hour = int(filename.split('_')[-1][8:10])
        min = int(filename.split('_')[-1][10:12])
        stationID = filename.split('_')[0]  ##包括J，4位字符串

        instrument = 'ION01'
        #product = 'Iedp'
        product = 'IED'        
        level = 'L21'
        segement = 'STP'
        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour, min).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join([stationID, instrument, product, level, segement, YYYYMMDDhhmmss])
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
        
        # YYYYMMDDhh = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H")

        # 2，读取单个文件的数据
        data = IONO.FDS.ION.read_FDS_ION_edp.read_data(file)

        # 3. 获取fmi时序图的保存路径
        IONO.FDS.ION.read_FDS_ION_edp.plot_data(stationID, year, month, day, hour, min, data, productpath)
        
        
        ####频高图处理
        productpath_list.append(productpath)##sao产品
        IIG_file = file.replace('DIP','IIG')
        IIG_file = IIG_file.replace('L21','L31')
        IIG_file = IIG_file.replace('.sao','.png')
        print (IIG_file)
        if not os.path.exists(IIG_file):
            pass##IIG图片不存在跳过            
        else:
            IIG_productpath = self.match_profile(IIG_file)##IIG，输入路径，映射到产品路径
            shutil.copyfile(IIG_file,IIG_productpath)
            productpath_list.append(IIG_productpath)
        # print (productpath_list)
        # input()
        
        return productpath_list

    def read_FDS_SOT_V1_GQ_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里

        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        # 2，读取单个文件的数据
        #print (file)
        my_map,cmap,productpath = SOLAR.FDS.SOT.read_FDS_SOT_V1.read_plot_GQ(file)
        productpath = self.match_profile(productpath)
        SOLAR.FDS.SOT.read_FDS_SOT_V1.plot_data(my_map,cmap,productpath)
        
        # 返回输出路径
        return productpath

    def read_FDS_SOT_V1_GS_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里

        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        # 2，读取单个文件的数据
        # productpath = SOLAR.FDS.SOT.read_FDS_SOT_V1.read_plot_GS(file)
        # productpath = self.match_profile(productpath)
        my_map,cmap,productpath = SOLAR.FDS.SOT.read_FDS_SOT_V1.read_plot_GS(file)
        productpath = self.match_profile(productpath)
        SOLAR.FDS.SOT.read_FDS_SOT_V1.plot_data(my_map,cmap,productpath)        
        # 返回输出路径
        return productpath

    def read_FDS_SOT_V1_HA_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里

        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        # 2，读取单个文件的数据
        # productpath = SOLAR.FDS.SOT.read_FDS_SOT_V1.read_plot_Ha(file)
        # productpath = self.match_profile(productpath)
        # productpath = self.match_profile(productpath)
        my_map,cmap,productpath = SOLAR.FDS.SOT.read_FDS_SOT_V1.read_plot_Ha(file)
        productpath = self.match_profile(productpath)
        SOLAR.FDS.SOT.read_FDS_SOT_V1.plot_data(my_map,cmap,productpath)    
        
        # 返回输出路径
        return productpath

    def read_FDS_SOT_V1_GC_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里

        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        # # 2，读取单个文件的数据
        # productpath = SOLAR.FDS.SOT.read_FDS_SOT_V1.read_plot_GC(file)
        # productpath = self.match_profile(productpath)
        my_map,cmap,productpath = SOLAR.FDS.SOT.read_FDS_SOT_V1.read_plot_GC(file)
        productpath = self.match_profile(productpath)
        SOLAR.FDS.SOT.read_FDS_SOT_V1.plot_data(my_map,cmap,productpath)            
        # 返回输出路径
        return productpath

    def read_FDS_SOT_V2_GQ_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里

        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        # 2，读取单个文件的数据
        #print (file)
        my_map,cmap,productpath = SOLAR.FDS.SOT.read_FDS_SOT_V2.read_plot_GQ(file)
        productpath = self.match_profile(productpath)
        SOLAR.FDS.SOT.read_FDS_SOT_V2.plot_data(my_map,cmap,productpath)
        
        # 返回输出路径
        return productpath

    def read_FDS_SOT_V2_GS_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里

        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        # 2，读取单个文件的数据
        # productpath = SOLAR.FDS.SOT.read_FDS_SOT_V1.read_plot_GS(file)
        # productpath = self.match_profile(productpath)
        my_map,cmap,productpath = SOLAR.FDS.SOT.read_FDS_SOT_V2.read_plot_GS(file)
        productpath = self.match_profile(productpath)
        SOLAR.FDS.SOT.read_FDS_SOT_V2.plot_data(my_map,cmap,productpath)        
        # 返回输出路径
        return productpath

    def read_FDS_SOT_V2_HA_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里

        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        # 2，读取单个文件的数据
        # productpath = SOLAR.FDS.SOT.read_FDS_SOT_V1.read_plot_Ha(file)
        # productpath = self.match_profile(productpath)
        # productpath = self.match_profile(productpath)
        my_map,cmap,productpath = SOLAR.FDS.SOT.read_FDS_SOT_V2.read_plot_Ha(file)
        productpath = self.match_profile(productpath)
        SOLAR.FDS.SOT.read_FDS_SOT_V2.plot_data(my_map,cmap,productpath)    
        
        # 返回输出路径
        return productpath

    def read_FDS_SOT_V2_GC_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里

        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        # # 2，读取单个文件的数据
        # productpath = SOLAR.FDS.SOT.read_FDS_SOT_V1.read_plot_GC(file)
        # productpath = self.match_profile(productpath)
        my_map,cmap,productpath = SOLAR.FDS.SOT.read_FDS_SOT_V2.read_plot_GC(file)
        productpath = self.match_profile(productpath)
        SOLAR.FDS.SOT.read_FDS_SOT_V2.plot_data(my_map,cmap,productpath)            
        # 返回输出路径
        return productpath
        
    def read_FDS_SRT_main(self, inputfile):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里

        ####判断路径的合法性
        for file in inputfile:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        ####根据输入文件，筛选3种频点的数据，分成3大类，存放到list里
        SRT01_files = []
        SRT02_files = []
        SRT03_files = []
        for file in inputfile:
            if 'SRT01' in file:
                SRT01_files.append(file)
            if 'SRT02' in file:
                SRT02_files.append(file)
            if 'SRT03' in file:
                SRT03_files.append(file)

        sort_SRT01_files = []
        sort_SRT02_files = []
        sort_SRT03_files = []
        ####重新排序，按从小到大的时间顺序，绘图需要从小到大的时间顺序
        SRT01_files0 = {}
        for file in SRT01_files:
            inputfilepath, inputfilename = os.path.split(file)
            filename, suffix = inputfilename.split('.')
            yymmddHHMMSS = filename.split('_')[-1]
            if yymmddHHMMSS not in SRT01_files0.keys():
                SRT01_files0[yymmddHHMMSS] = [file]
            else:
                SRT01_files0[yymmddHHMMSS].append(file)
        ##按key值从大到小排序
        SRT01_files1 = sorted(SRT01_files0.items(), key=lambda d: d[0], reverse=False)
        #print(SRT01_files1)
        for i,file in enumerate(SRT01_files1):
            sort_SRT01_files.append(SRT01_files1[i][1][0])#list里的元素是元组，元祖的第2个元素是list，元组的第2个元素[1][0],list变字符串元组的第1个元素是时间

        ####重新排序，按从小到大的时间顺序，绘图需要从小到大的时间顺序
        SRT02_files0 = {}
        for file in SRT02_files:
            inputfilepath, inputfilename = os.path.split(file)
            filename, suffix = inputfilename.split('.')
            yymmddHHMMSS = filename.split('_')[-1]
            if yymmddHHMMSS not in SRT02_files0.keys():
                SRT02_files0[yymmddHHMMSS] = [file]
            else:
                SRT02_files0[yymmddHHMMSS].append(file)
        ##按key值从大到小排序
        SRT02_files1 = sorted(SRT02_files0.items(), key=lambda d: d[0], reverse=False)
        for i,file in enumerate(SRT02_files1):
            sort_SRT02_files.append(SRT02_files1[i][1][0])#list里的元素是元组，元祖的第2个是文件，元祖的第1个是时间

        ####重新排序，按从小到大的时间顺序，绘图需要从小到大的时间顺序
        SRT03_files0 = {}
        for file in SRT03_files:
            inputfilepath, inputfilename = os.path.split(file)
            filename, suffix = inputfilename.split('.')
            yymmddHHMMSS = filename.split('_')[-1]
            if yymmddHHMMSS not in SRT03_files0.keys():
                SRT03_files0[yymmddHHMMSS] = [file]
            else:
                SRT03_files0[yymmddHHMMSS].append(file)
        ##按key值从大到小排序
        SRT03_files1 = sorted(SRT03_files0.items(), key=lambda d: d[0], reverse=False)
        for i,file in enumerate(SRT03_files1):
            sort_SRT03_files.append(SRT03_files1[i][1][0])#list里的元素是元组，元祖的第2个是文件，元祖的第1个是时间


        ####只需要SRT01_files的即可，获取时间
        ##提取出72小时，最大日期的时间，[0]代表[]转string
        max_inputfile = SRT01_files1[-1][1][0]  # 获取列表第1个元素，元组中第1个元素的第1个元素
        # max_inputfile_yymmddHHMMSS = inputfile1[0][0]#获取列表第1个元素，第1个元祖第1个元素

        # stations = IONO.FDS.ISM.station_info.get_FDS_station_info()
        inputfilepath, inputfilename = os.path.split(max_inputfile)
        self.outputpath = inputfilepath

        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[-1][0:4])
        month = int(filename.split('_')[-1][4:6])
        day = int(filename.split('_')[-1][6:8])
        hour = int(filename.split('_')[-1][8:10])
        min = int(filename.split('_')[-1][10:12])
        stationID = filename.split('_')[0]  ##包括J，4位字符串

        ####实际测试，如果inputfile里的时间不是从小到大排列，如下顺序测试绘图有问题
        # HEBJ_SRT01_DSP_L11_15M_20191201001500.fsp
        # HEBJ_SRT01_DSP_L11_15M_20191201003000.fsp
        # HEBJ_SRT02_DSP_L11_15M_20191201003000.fsp
        # HEBJ_SRT02_DSP_L11_15M_20191201001500.fsp
        # HEBJ_SRT03_DSP_L11_15M_20191201001500.fsp
        # HEBJ_SRT03_DSP_L11_15M_20191201003000.fsp

        #instrumentID = 'SRT01'
        #print('0')
        data_4542 = SOLAR.FDS.SRT.read_FDS_SRT.gather_data(sort_SRT01_files)
        #print('1')
        #instrumentID = 'SRT02'
        data_2801 = SOLAR.FDS.SRT.read_FDS_SRT.gather_data(sort_SRT02_files)
        #print(SRT02_files1)
        #print(sort_SRT02_files)

        #instrumentID = 'SRT03'
        data_1427 = SOLAR.FDS.SRT.read_FDS_SRT.gather_data(sort_SRT03_files)

        ##输出年，月，日，时，分怎么获取，前24小时
        instrumentID = 'SRT00'
        #savepath = SOLAR.FDS.SRT.read_FDS_SRT.get_savepath(stationID, instrumentID, year, month, day, hour, min)
        time_end = datetime.datetime(year, month, day, hour, min)
        product = 'ISP'
        level = 'L21'
        segment = '15M'
        date_time = time_end.strftime("%Y%m%d%H%M%S")
        prefix = '_'.join([stationID, instrumentID, product, level, segment, date_time])
        suffix = '.png'
        ####路径需要join，如果是普通的字符串，直接+即可
        productpath = os.path.join(self.outputpath, prefix+suffix)
        productpath = self.match_profile(productpath)
        #savepath = os.path.join(self.outputpath,prefix,suffix)

        SOLAR.FDS.SRT.read_FDS_SRT.plot_data(data_4542, data_2801, data_1427, productpath)
        #productpath = savepath
        # 返回输出路径
        return productpath

    def read_CMA_SRT_main(self, inputfiles):
        # input: sint_L_2019071600_at.dat
        # output: XXXM_ISM01_IsintL_L21_72H_20190716080000.png
        # inputfile = self.inputfile[0]
        ##单个任务，输入一个台站的，4个卫星的数据，72小时，4*72个文件
        ##先按小时排序4个文件，排列出4个卫星的数据，总共72组，每个小时1组
        ##每1个txt文件里
        for file in inputfiles:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)

        ####根据inputfile重新按时间顺序排序，从大到小的时间顺序
        inputfile0 = {}
        sort_inputfiles=[]
        for file in inputfiles:
            inputfilepath, inputfilename = os.path.split(file)
            filename, suffix = inputfilename.split('.')
            year = (filename.split('_')[3][0:4])
            month = (filename.split('_')[3][4:6])
            day = (filename.split('_')[3][6:8])
            hour = (filename.split('_')[4][0:2])
            min = (filename.split('_')[4][2:4])
            sec = (filename.split('_')[4][4:6])
            yymmddHHMMSS =year+month+day+hour+min+sec
            #print(yymmddHHMMSS)
            if yymmddHHMMSS not in inputfile0.keys():
                inputfile0[yymmddHHMMSS] = [file]
            else:
                inputfile0[yymmddHHMMSS].append(file)
        ##按key值从小到大排序
        inputfile1 = sorted(inputfile0.items(), key=lambda d: d[0], reverse=False)
        for i,file in enumerate(inputfile1):
            sort_inputfiles.append(inputfile1[i][1][0])#list里的元素是元组，元组的第2个是文件，元祖的第1个是时间，[1][0]，代表[]转string
        #print(sort_inputfiles)



        #YJGC_SDWH_TYSD_20180328_060600_L0_0000_01S.txt
        ##提取出72小时，最大日期的时间
        max_inputfile = inputfile1[-1][1][0]  # 获取列表最后1个元素，元组中第1个元素是时间
        # max_inputfile_yymmddHHMMSS = inputfile1[0][0]#获取列表第1个元素，第1个元祖第1个元素

        # stations = IONO.FDS.ISM.station_info.get_FDS_station_info()
        inputfilepath, inputfilename = os.path.split(max_inputfile)
        self.outputpath = inputfilepath

        filename, suffix = inputfilename.split('.')
        year = int(filename.split('_')[3][0:4])
        month = int(filename.split('_')[3][4:6])
        day = int(filename.split('_')[3][6:8])
        hour = int(filename.split('_')[4][0:2])
        min = int(filename.split('_')[4][2:4])
        #stationID = filename.split('_')[1]  ##包括J，4位字符串
        stationID = 'SDZM'  ##包括J，4位字符串


        instrumentID = 'SRT01'
        product = 'ISP'
        level = 'L21'
        segment = '24H'
        YYYYMMDDhhmmss = datetime.datetime(year, month, day, hour, min).strftime("%Y%m%d%H%M%S")
        suffix = '.png'
        prefix = '_'.join([stationID, instrumentID, product, level, segment, YYYYMMDDhhmmss])
        productpath = os.path.join(self.outputpath, prefix + suffix)
        productpath = self.match_profile(productpath)
        print (productpath)
        # YYYYMMDDhh = datetime.datetime(year, month, day, hour).strftime("%Y%m%d%H")

        #print(sort_inputfiles)
        data_24h = SOLAR.CMA.SRT.read_CMA_SRT.gather_data(sort_inputfiles)
        SOLAR.CMA.SRT.read_CMA_SRT.plot_data(data_24h, productpath)

        return productpath
        
        
    def read_GEOMAG_INDEX_main(self, tasktype, inputfiles):
        """
        1. 解析地磁K指数,并入库
        2. inputfiles，4个台站 + 1个中国区域
        3. 4个台站的格式固定，中国区域的格式目前未定，需要自己解析
        """

        for file in inputfiles:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                raise Exception(self.errorinfo)
        
        ##按台站分开，解析入库
        for file in inputfiles:
            ##解析文件，提取物理要素
            path,filename = os.path.split(file)
            try:
                el_ext = element_opt.element_extract.ElementExtract(tasktype=tasktype,path=path,filename=filename)
            except Exception as e:
                raise Exception(str(e))
                
            try:            
                data_dicts = el_ext.get_data()##要素提取,返回物理量的字典
            except Exception as e:
                raise Exception(str(e))
            #print (data_dicts)
            
            ##物理要素录入数据库
            print ('FILE: ',__file__ , 'LINE: ',sys._getframe().f_lineno)
            el_rec = element_opt.element_record.ElementRecord(tasktype=tasktype)
            print ('FILE: ',__file__ , 'LINE: ',sys._getframe().f_lineno)
            
            table_name = el_rec.get_table_name()
            print(table_name)
            
            try:
                el_rec.record(table_name,data_dicts)
            except Exception as e:
                raise Exception(str(e))
        
        print ('t_geomag_index 完成数据库录入')
        
        return
        

    def read_IONO_SCALED_main(self, tasktype, inputfiles):
        """
        1. 解析sao文件，提取物理要素并入库
            foF2	float4	4	√	F2层寻常波临界频率
            foF1	float4	4	√	F1层寻常波临界频率
            M_D	float4	4	√	MUF(D)/ foF2
            MUF_D	float4	4	√	大圆距离D上传播的最大可用频率
            fmin	float4	4	√	电离图上回波的最小频率
            foEs	float4	4	√	Es层寻常波临界频率
            fminF	float4	4	√	电离图上F层回波的最小频率
            fminE	float4	4	√	电离图上E层回波的最小频率
            foE	float4	4	√	E层寻常波临界频率
            fxI	float4	4	√	F层回波最大频率
            hF	float4	4	√	F层回波最小虚高
            hF2	float4	4	√	F2层回波最小虚高
            hE	float4	4	√	E层回波最小虚高
            hEs	float4	4	√	Es层回波最小虚高
        """
        print ('into read_IONO_SCALED_main......')
        for file in inputfiles:
            # print (file)
            # input()
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                print(self.errorinfo)
                raise Exception(self.errorinfo)
        
        ##按台站分开，解析入库
        for file in inputfiles:
            ##解析文件，提取物理要素
            path,filename = os.path.split(file)
            el_ext = element_opt.element_extract.ElementExtract(tasktype=tasktype,path=path,filename=filename)
            data_dicts = el_ext.get_data()##要素提取,返回物理量的字典
            #print (data_dicts)
            ##物理要素录入数据库
            print (__file__ , sys._getframe().f_lineno)
            el_rec = element_opt.element_record.ElementRecord(tasktype=tasktype)
            print (__file__ , sys._getframe().f_lineno)
            table_name = el_rec.get_table_name()
            print(table_name)
            el_rec.record(table_name,data_dicts)
        
        print ('t_iono_scaled 完成数据库录入')
        return

    def read_SOLAR_RAD_main(self, tasktype, inputfiles):
        """
        1. 解析文件，提取物理要素并入库,1天1个文件，1个文件里有1个值，实数，0-200
            id	int4	4	√	数据ID
            observetime	Datetime(YYYY-MM-DD HH:mm:SS)		√	观测时间，1次/1日
            apparatus	Varchar	3	√	仪器设备
            apparatusid	Varchar	2	√	仪器设备序号
            station	Varchar	5	√	台站，2个台站
            flux	float4	4		每日12点对应频点射电流量
            createtime	Datetime(YYYY-MM-DD HH:mm:SS)	0	√	入库时间
        """
        print ('into read_SOLAR_RAD_main......')
        for file in inputfiles:
            if (os.path.exists(file)):
                pass
            else:
                self.errorinfo = '%s%s' % (file, ' do not exist.')
                #return ''
                print(self.errorinfo)
                raise Exception(self.errorinfo)
        
        ##按台站分开，解析入库
        for file in inputfiles:
            ##解析文件，提取物理要素
            path,filename = os.path.split(file)
            el_ext = element_opt.element_extract.ElementExtract(tasktype=tasktype,path=path,filename=filename)
            data_dicts = el_ext.get_data()##要素提取,返回物理量的字典
            print (data_dicts)
            ##物理要素录入数据库
            print (__file__ , sys._getframe().f_lineno)
            el_rec = element_opt.element_record.ElementRecord(tasktype=tasktype)
            print (__file__ , sys._getframe().f_lineno)
            table_name = el_rec.get_table_name()
            print(table_name)
            el_rec.record(table_name,data_dicts)
        
        print ('t_solar_rad 完成数据库录入')
        return
        
    ##ATMOS数据接口
    ##地基-流星雷达流星余迹参数信息统计分析数据接口
    def read_Atmos_FDS_MET_L11(self, inputfile):
        productpath = []
        data_24h = {}
        inputfile.sort()
        for file in inputfile:
            # 检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)

            # 收集过去24小时24文件的数据
            data_01h = ATMOS.FDS.MET.read_FDS_MET_L11.read_data(file)
            data_24h = ATMOS.FDS.MET.read_FDS_MET_L11.merge_dict(data_24h, data_01h)

        # 获取图像保存路径及图像文件名
        savepath = inputfile[-1].replace('.dat', '.png')
        savepath = savepath.replace('_D', '_I')
        savepath = savepath.replace('L11', 'L36')
        savepath = savepath.replace('_01H_', '_24H_')

        # 匹配本地产品目录
        savepath = self.match_profile(savepath)
        productpath.append(savepath)

        # 绘制图像
        ATMOS.FDS.MET.read_FDS_MET_L11.plot_data(data_24h, savepath)

        return productpath

    ##地基-流星雷达水平风场矢量分布图绘制数据接口
    def read_Atmos_FDS_MET_L21(self, inputfile):
        data_24h = {}
        inputfile.sort()
        for file in inputfile:
            # 检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)

            # 收集过去24小时24文件的数据
            data_01h = ATMOS.FDS.MET.read_FDS_MET_L21.read_data(file)
            data_24h = ATMOS.FDS.MET.read_FDS_MET_L21.merge_dict(data_24h, data_01h)
        # 获取图像保存路径及图像文件名
        savepath = inputfile[-1].replace('.txt', '.png')
        savepath = savepath.replace('_D', '_I')
        savepath = savepath.replace('L21', 'L35')
        savepath = savepath.replace('_01H_', '_24H_')

        # 匹配本地产品目录
        savepath = self.match_profile(savepath)

        # 绘图
        ATMOS.FDS.MET.read_FDS_MET_L21.plot_data(data_24h, savepath)

        productpath = savepath
        return productpath

    ##地基-MST雷达风场廊线图绘制数据接口
    def read_Atmos_FDS_MST_main(self, inputfile):
        productpath = []
        for file in inputfile:
            # 检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)

            # 截取文件名
            filename = os.path.split(file)[-1]

            if filename[10:13] == 'DWL' or filename[10:13] == 'DWM' or filename[10:13] == 'DWH':
                # 读取数据文件
                datas = ATMOS.FDS.MST.read_FDS_MST.read_data(file)
                # 生成图像文件及路径
                savepath = file.replace('.dat', '.png')
                savepath = savepath.replace('_D', '_I')
                # 匹配本地产品目录
                savepath = self.match_profile(savepath)

                # 获取站名
                station_name = self.match_station(inputfile)
                # 计算文件时间
                datestr = filename[22:26] + "-" + filename[26:28] + "-" + filename[28:30] + " " + filename[30:32]
                # 绘图
                ATMOS.FDS.MST.read_FDS_MST.plot_data(station_name, datestr, datas, savepath)

                productpath.append(savepath)
        return productpath

    # 绘制大气风场廓线
    # 某个时刻前半个小时数据，三个模式
    # CYTM_MST01_IWP_L21_STP_20200302070000.png
    def read_Atmos_FDS_MST_30M_main(self, inputfile):
        for file in inputfile:
            # 检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)

            rootpath, filename = os.path.split(file)

            if (filename.find('DWL') != -1):
                data_DWL = ATMOS.FDS.MST.read_FDS_MST_V1.gather_data([file])
            elif (filename.find('DWM') != -1):
                data_DWM = ATMOS.FDS.MST.read_FDS_MST_V1.gather_data([file])
            elif (filename.find('DWH') != -1):
                data_DWH = ATMOS.FDS.MST.read_FDS_MST_V1.gather_data([file])

        ####根据inputfile重新按时间顺序排序，从大到小的时间顺序
        inputfile0 = {}
        for file in inputfile:
            inputfilepath, inputfilename = os.path.split(file)
            filename, suffix = inputfilename.split('.')
            yymmddHHMMSS = filename.split('_')[-1]
            if yymmddHHMMSS not in inputfile0.keys():
                inputfile0[yymmddHHMMSS] = [file]
            else:
                inputfile0[yymmddHHMMSS].append(file)
        ##按key值从大到小排序
        inputfile1 = sorted(inputfile0.items(), key=lambda d: d[0], reverse=True)

        ##提取出30分钟，最大日期的时间
        max_inputfile = inputfile1[0][1][0]  # 获取列表第1个元素，元祖中第1个元素的第1个元素

        rootpath, filename = os.path.split(max_inputfile)
        if (filename.find('DWL') != -1):
            savepath = max_inputfile.replace('_DWL', '_IWP')
        elif (filename.find('DWM') != -1):
            savepath = max_inputfile.replace('_DWM', '_IWP')
        elif (filename.find('DWH') != -1):
            savepath = max_inputfile.replace('_DWH', '_IWP')

        # 生成图像文件及路径
        savepath = savepath.replace('.dat', '.png')

        # 匹配本地产品目录
        savepath = self.match_profile(savepath)

        # 绘图
        ATMOS.FDS.MST.read_FDS_MST_V1.plot_data(data_DWL, data_DWM, data_DWH, savepath)

        productpath = savepath
        return productpath

    # 大气风场湍流廓线
    # 使用过去24小时的MST雷达产品数据，三个模式
    # 图像产品为0时，图像名字为：CYTM_MST01_IWT_L21_STP_20200302000000.png
    def read_Atmos_FDS_MST_24H_main(self, inputfile):
        DWL_files = []
        DWM_files = []
        DWH_files = []

        for file in inputfile:
            # 检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)

            rootpath, filename = os.path.split(file)

            if(filename.find('DWL') != -1):
                DWL_files.append(file)
            elif (filename.find('DWM') != -1):
                DWM_files.append(file)
            elif (filename.find('DWH') != -1):
                DWH_files.append(file)
        #print(DWL_files)
        #print(DWM_files)
        #print(DWH_files)

        data_DWL = ATMOS.FDS.MST.CAL_FDS_MST_turb.gather_data(DWL_files)
        print('data_DWL:', data_DWL)

        data_DWM = ATMOS.FDS.MST.CAL_FDS_MST_turb.gather_data(DWM_files)
        #print('data_DWM:', data_DWM)

        data_DWH = ATMOS.FDS.MST.CAL_FDS_MST_turb.gather_data(DWH_files)
        #print('data_DWH:', data_DWH)

        ####根据inputfile重新按时间顺序排序，从大到小的时间顺序
        inputfile0 = {}
        for file in inputfile:
            inputfilepath, inputfilename = os.path.split(file)
            filename, suffix = inputfilename.split('.')
            yymmddHHMMSS = filename.split('_')[-1]
            if yymmddHHMMSS not in inputfile0.keys():
                inputfile0[yymmddHHMMSS] = [file]
            else:
                inputfile0[yymmddHHMMSS].append(file)
        ##按key值从大到小排序
        inputfile1 = sorted(inputfile0.items(), key=lambda d: d[0], reverse=True)

        ##提取出72小时，最大日期的时间
        max_inputfile = inputfile1[0][1][0]  # 获取列表第1个元素，元祖中第1个元素的第1个元素

        rootpath, filename = os.path.split(max_inputfile)
        if (filename.find('DWL') != -1):
            savepath = max_inputfile.replace('_DWL', '_IWT')
        elif (filename.find('DWM') != -1):
            savepath = max_inputfile.replace('_DWM', '_IWT')
        elif (filename.find('DWH') != -1):
            savepath = max_inputfile.replace('_DWH', '_IWT')
            
        # 生成图像文件及路径
        savepath = savepath.replace('.dat', '.png')
        # 匹配本地产品目录
        savepath = self.match_profile(savepath)

        # 绘图
        ATMOS.FDS.MST.CAL_FDS_MST_turb.plot_data(data_DWL, data_DWM, data_DWH, savepath)

        productpath = savepath
        return productpath

    # 大气风场廓线演化图
    # 过去72小时数据
    # CYTM_MST01_IWS_L21_STP_20200302000000.png
    def read_Atmos_FDS_MST_72H_main(self, inputfile):
        DWL_files = []
        DWM_files = []
        DWH_files = []

        for file in inputfile:
            # 检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)

            rootpath, filename = os.path.split(file)

            if(filename.find('DWL') != -1):
                DWL_files.append(file)
            elif (filename.find('DWM') != -1):
                DWM_files.append(file)
            elif (filename.find('DWH') != -1):
                DWH_files.append(file)

        data_DWL = ATMOS.FDS.MST.read_FDS_MST_V2.gather_data(DWL_files)

        data_DWM = ATMOS.FDS.MST.read_FDS_MST_V2.gather_data(DWM_files)

        data_DWH = ATMOS.FDS.MST.read_FDS_MST_V2.gather_data(DWH_files)

        ####根据inputfile重新按时间顺序排序，从大到小的时间顺序
        inputfile0 = {}
        for file in inputfile:
            inputfilepath, inputfilename = os.path.split(file)
            filename, suffix = inputfilename.split('.')
            yymmddHHMMSS = filename.split('_')[-1]
            if yymmddHHMMSS not in inputfile0.keys():
                inputfile0[yymmddHHMMSS] = [file]
            else:
                inputfile0[yymmddHHMMSS].append(file)
        ##按key值从大到小排序
        inputfile1 = sorted(inputfile0.items(), key=lambda d: d[0], reverse=True)

        ##提取出72小时，最大日期的时间
        max_inputfile = inputfile1[0][1][0]  # 获取列表第1个元素，元祖中第1个元素的第1个元素

        rootpath, filename = os.path.split(max_inputfile)
        if (filename.find('DWL') != -1):
            savepath = max_inputfile.replace('_DWL', '_IWS')
        elif (filename.find('DWM') != -1):
            savepath = max_inputfile.replace('_DWM', '_IWS')
        elif (filename.find('DWH') != -1):
            savepath = max_inputfile.replace('_DWH', '_IWS')

        # 生成图像文件及路径
        savepath = savepath.replace('.dat', '.png')
        savepath = savepath.replace('_STP', '_72H')
        # 匹配本地产品目录
        savepath = self.match_profile(savepath)

        # 绘图
        xrange = 72
        ATMOS.FDS.MST.read_FDS_MST_V2.plot_data(data_DWL, data_DWM, data_DWH, xrange, savepath)

        productpath = savepath
        return productpath

    ##子午-激光雷达大气参数（动态）廊线图生成数据接口
    ##大气密度文件
    def read_Atmos_MDP_LID_DAM_main(self, inputfile):
        productpath = []
        for file in inputfile:
            ####检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)
            # 读取数据文件
            data = ATMOS.MDP.LID.read_MDP_LID_DAM_V2.read_data(file)
            # 获取文件路径及图像文件名称
            savepath = ATMOS.MDP.LID.read_MDP_LID_DAM_V2.get_savepath(file)

            # 获取站名
            station_name = self.match_station(inputfile)
            # 计算文件时间
            filename = os.path.split(savepath)[-1]
            datestr = filename[22:26] + "-" + filename[26:28] + "-" + filename[28:30] + " " + filename[30:32]
            # 绘图
            ATMOS.MDP.LID.read_MDP_LID_DAM_V2.plot_data(station_name, datestr, data, savepath)

            productpath.append(savepath)
        return productpath

    ##大气温度文件
    def read_Atmos_MDP_LID_DAT_main(self, inputfile):
        productpath = []
        for file in inputfile:
            ####检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)
            # 读取数据文件
            data = ATMOS.MDP.LID.read_MDP_LID_DAT_V2.read_data(file)
            # 获取文件路径及图像文件名称
            savepath = ATMOS.MDP.LID.read_MDP_LID_DAT_V2.get_savepath(file)

            # 获取站名
            station_name = self.match_station(inputfile)
            # 计算文件时间
            filename = os.path.split(savepath)[-1]
            datestr = filename[22:26] + "-" + filename[26:28] + "-" + filename[28:30] + " " + filename[30:32]
            # 绘图
            ATMOS.MDP.LID.read_MDP_LID_DAT_V2.plot_data(station_name, datestr, data, savepath)

            productpath.append(savepath)
        return productpath

    # 生成大气密度、温度、压强
    def read_Atmos_MDP_LID_main(self, inputfile):
        productpath = []
        # 判断文件个数，判断是否存在DAM、DAT文件，少一个就报错推出
        if len(inputfile) < 2:
            self.errorinfo = '%s' % ('leak necessary file.')
            # 若出错直接抛出异常信息
            raise Exception(self.errorinfo)
        else:
            dat_flag = ''
            dam_flag = ''
            for file in inputfile:
                filename = os.path.split(file)[-1]
                if str(filename)[:-3].find('DAM') != -1:
                    dam_flag = 'DAM'
                if str(filename)[:-3].find('DAT') != -1:
                    dat_flag = 'DAT'
            if dam_flag == 'DAM' and dat_flag == 'DAT':
                pass
            else:
                self.errorinfo = '%s' % ('file not match')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)

        for file in inputfile:
            ####检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)

            filename = os.path.split(file)[-1]

            # 读取DAM数据文件,密度
            if str(filename)[:-3].find('DAM') != -1:
                DAM = ATMOS.MDP.LID.read_MDP_LID_V1.read_data_DAM(file)

            # 读取DAT数据文件,温度
            if str(filename)[:-3].find('DAT') != -1:
                DAT = ATMOS.MDP.LID.read_MDP_LID_V1.read_data_DAT(file)

                # 匹配本地产品目录
                savepath = self.match_profile(file)

                # 版本V1绘图
                savepath_gif_v1 = ATMOS.MDP.LID.read_MDP_LID_V1.get_savepath_gif(savepath)
                savepath_png_v1 = ATMOS.MDP.LID.read_MDP_LID_V1.get_savepath_png(savepath)
                productpath.append(savepath_gif_v1)

                # 版本V2绘图
                savepath_v2 = ATMOS.MDP.LID.read_MDP_LID_V2.get_savepath(savepath)
                productpath.append(savepath_v2)

        # 压强
        # 版本V1绘图
        DAP = ATMOS.MDP.LID.read_MDP_LID_V1.cal_data_DAP(DAM, DAT)
        ATMOS.MDP.LID.read_MDP_LID_V1.plot_data_DAP(DAM, DAT, DAP, savepath_png_v1, savepath_gif_v1)

        # # 版本V2绘图
        ATMOS.MDP.LID.read_MDP_LID_V2.plot_data_DAP(DAM, DAT, DAP, savepath_v2)
        return productpath

    # 融合数据处理---MST雷达产品数据文件和气象高空气球数据
    def read_Atmos_FDS_UPAR_main(self, inputfile):
        # 判断文件个数，少于4个报错推出
        if len(inputfile) < 4:
            self.errorinfo = 'file num is not four.'
            # 若出错直接抛出异常信息
            raise Exception(self.errorinfo)
    
        for file in inputfile:
            ####检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)

            station_name_upar = '武汉'

            rootpath, filename = os.path.split(file)

            # station_id_MST = str(filename)[:3]

            # 读取高空气球风场数据
            if(str(rootpath)[-4:] == 'MIXM'):
                if (os.path.exists(file) == False):
                    self.errorinfo = '%s%s' % (file, ' does not exist.')
                    # 若出错直接抛出异常信息
                    raise Exception(self.errorinfo)
                str_data = filename.split('_')[-1][:-4]
                #path = rootpath
                data_upar = ATMOS.FDS.UPAR.read_CMA_UPAR.read_data_upar(file, station_name_upar)
            elif(filename[11:14] == 'DWL'):
                if (os.path.exists(file) == False):
                    self.errorinfo = '%s%s' % (file, ' does not exist.')
                    # 若出错直接抛出异常信息
                    raise Exception(self.errorinfo)
                stationID = filename[:3]
                station_id_MST = stationID
                path = rootpath
                data_DWL = ATMOS.FDS.UPAR.read_CMA_UPAR.gather_data_MST([file])
            elif(filename[11:14] == 'DWM'):
                if (os.path.exists(file) == False):
                    self.errorinfo = '%s%s' % (file, ' does not exist.')
                    # 若出错直接抛出异常信息
                    raise Exception(self.errorinfo)
                # stationID = filename[:3]
                # path = rootpath
                data_DWM = ATMOS.FDS.UPAR.read_CMA_UPAR.gather_data_MST([file])
            elif(filename[11:14] == 'DWH'):
                if (os.path.exists(file) == False):
                    self.errorinfo = '%s%s' % (file, ' does not exist.')
                    # 若出错直接抛出异常信息
                    raise Exception(self.errorinfo)
                data_DWH = ATMOS.FDS.UPAR.read_CMA_UPAR.gather_data_MST([file])
                # tationID = filename[:3]
                # path = rootpath

        # 校正崇阳台MST数据中的高度
        data_comp = ATMOS.FDS.UPAR.read_CMA_UPAR.correct_data(data_upar, data_DWL, data_DWM, data_DWH)
        
        print('stationID = ', stationID)

        # 拼接图像文件存储目录及名称
        stationIDJ = stationID + 'J'
        instrumentID = 'MST01'
        product = 'IWC'
        level = 'L31'
        segment = 'STP'
        prefix = '_'.join([stationIDJ, instrumentID, product, level, segment, str_data])
        suffix = prefix + '.png'
        # print('path = ', path)
        # path = path[:-4] + stationIDJ
        # print('path1 = ', path)
        savepath = os.path.join(path, suffix)
        # 匹配本地产品目录
        savepath = self.match_profile(savepath)
        print('savepath = ', savepath)
        # 绘图
        ATMOS.FDS.UPAR.read_CMA_UPAR.plot_data(station_name_upar, data_upar, station_id_MST, data_DWL, data_DWM,\
                                                    data_DWH, data_comp, savepath)
        productpath = savepath
        return productpath

    ##GEOMAG数据接口
    ##地基-地磁7要素监测数据接口
    # \FDS\geomag\FGM\202003\20200330\SYZJ\SYZJ_FGM01_DPR_L21_15M_20200311000000.dat
    # 只做4个站['HSZ', 'KSZ', 'LSZ', 'SYZ']
    def read_GEOMAG_FDS_FGM_DSR_main(self, inputfile):
        stations = ['HSZ', 'KSZ', 'LSZ', 'SYZ']
        inputfile.sort()
        data_24h = {}
        for file in inputfile:
            # 检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)
            # 检查台站是否符合
            if(os.path.split(file)[-1][:3] not in stations):
                self.errorinfo = '%s%s' % (file, ' station is not match.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)

            # 收集过去24小时96文件的数据
            data_15m = GEOMAG.FDS.FGM.read_FDS_FGM_DSR.read_data(file)
            data_24h = GEOMAG.FDS.FGM.read_FDS_FGM_DSR.merge_dict(data_24h, data_15m)

        savepath = inputfile[-1].replace('.dat', '.png')
        savepath = savepath.replace('_DPR_', '_IMD_')
        savepath = savepath.replace('_15M_', '_24H_')
        # 匹配本地产品目录
        savepath = self.match_profile(savepath)

        # 绘图
        xrange = 24
        GEOMAG.FDS.FGM.read_FDS_FGM_DSR.plot_data(data_24h, xrange, savepath)
        productpath = savepath
        return productpath

    ##子午-地磁7要素监测数据接口
    # \MDP\geomag\FGM\201910\20191021\ZQTM\ZQT_FGM01_DMD_L01_01D_20191021000000.dat
    def read_GEOMAG_MDP_FGM_main(self, inputfile):
        productpath = []
        for file in inputfile:
            ####检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)
            # 读取文件数据
            data = GEOMAG.MDP.FGM.read_MDP_FGM.read_data(file)
            # 图像保存路径及图像名
            savepath = GEOMAG.MDP.FGM.read_MDP_FGM.get_savepath(file)
            # 匹配本地产品目录
            savepath = self.match_profile(savepath)
            # 绘图
            GEOMAG.MDP.FGM.read_MDP_FGM.plot_data(data, savepath)

            productpath.append(savepath)
        return productpath

    # 地基-单站K指数计算
    # \FDS\geomag\FGM\202003\20200310\SYZJ\SYZJ_FGM01_DPR_L21_15M_20200311000000.dat
    def read_GEOMAG_FDS_RK_H_main(self, inputfile):
        inputfile.sort()
        for file in inputfile:
            ####检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)

        # 截取年月日
        rootpath, filename = os.path.split(inputfile[-1])
        strdata = filename.split('_')[-1][:-4]
        year = int(strdata[0:4])
        month = int(strdata[4:6])
        day = int(strdata[6:8])
        hour = int(strdata[8:10])
        # min = int(strdata[10:12])

        # 获取区域k指数保存路径
        savepath = inputfile[-1].replace('_DPR', '_DKI')
        savepath = savepath.replace('_15M', '_03H')
        savepath = savepath.replace('.dat', '.txt')
        # 匹配本地产品目录
        savepath = self.match_profile(savepath)

        # 获取站点ID
        stationID = filename[:3]

        # 计算单站地磁k指数
        k = GEOMAG.FDS.FGM.cal_FDS_Kindex.cal_station_kindex(inputfile, year, month, day, hour)

        GEOMAG.FDS.FGM.cal_FDS_Kindex.save_data_k(year, month, day, hour, k, savepath)

        productpath = savepath
        return productpath

    # 地基-中国区域K指数计算
    # \FDS\geomag\FGM\202003\20200331\HSZJ\HSZJ_FGM01_DKR_L31_03H_20200331000000.dat
    def read_GEOMAG_FDS_RK_main(self, inputfile):
        productpath = []
        # 收集过去4个台站的数据
        data4 = {}
        for file in inputfile:
            ####检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)
            # 读取单站k指数
            data1 = GEOMAG.FDS.FGM.cal_FDS_RegionK_V1.read_data(file)
            data4 = GEOMAG.FDS.FGM.cal_FDS_RegionK_V1.merge_dict(data4, data1)

        # 计算区域K指数
        RK = GEOMAG.FDS.FGM.cal_FDS_RegionK_V1.cal_region_kindex(data4)

        # 截取年月日
        rootpath, filename = os.path.split(inputfile[0])
        strdata = filename.split('_')[-1][:-4]
        year = int(strdata[0:4])
        month = int(strdata[4:6])
        day = int(strdata[6:8])
        hour = int(strdata[8:10])

        # 获取区域k指数保存路径
        savepath = inputfile[0].replace('.dat', '.txt')
        savepath = savepath.replace('_DKR', '_DRK')
        savepath = savepath.replace('_L21', '_L31')
        strpath = os.path.split(savepath)[-1][0:4]
        savepath = savepath.replace(strpath, 'MIXJ')
        # 匹配本地产品目录
        savepath = self.match_profile(savepath)

        # 保存区域K指数
        GEOMAG.FDS.FGM.cal_FDS_RegionK_V1.save_data(year, month, day, hour, RK, savepath)
        productpath.append(savepath)
        
        ##区域K指数录入数据库
        el_rec = element_opt.element_record.ElementRecord()
        table_name=['t_geomag_index']
        station='MIX'
        apparatus = 'FGM'
        k_data = RK
        yyyymmddhhmmss=strdata
        date_str= datetime.datetime.strptime(yyyymmddhhmmss, "%Y%m%d%H%M%S").strftime("%Y-%m-%d %H:%M:%S")
        data_dicts = element_opt.read_k.merge_k_dicts(station,date_str,apparatus,k_data)        
        try:
            el_rec.record(table_name,data_dicts)
        except Exception as e:
            raise Exception(str(e))

        # 制作地磁暴报告文档
        # 1，获取过去72小时中国区域K指数
        RK72h = GEOMAG.FDS.FGM.make_FDS_FGM_DDR.get_RK72H(year, month, day, hour)

        # 2，绘制区域K指数曲线图
        savepath_fig = GEOMAG.FDS.FGM.make_FDS_FGM_DDR.get_savepath_RK72h(year, month, day, hour)
        # 路径拼接
        rootpath = os.path.split(savepath)[:-1][0]
        savepath_fig = os.path.join(rootpath, os.path.split(savepath_fig)[-1])
        GEOMAG.FDS.FGM.make_FDS_FGM_DDR.plot_data_RK72h(year, month, day, hour, RK72h, savepath_fig)

        # 3，生成地磁暴警报文档
        savepath_doc = GEOMAG.FDS.FGM.make_FDS_FGM_DDR.get_savepath_doc(year, month, day)
        # 路径拼接
        savepath_doc = os.path.join(rootpath, os.path.split(savepath_doc)[-1])
        fullpath_template = GEOMAG.FDS.FGM.make_FDS_FGM_DDR.get_doc_template()
        alert_doc_re = GEOMAG.FDS.FGM.make_FDS_FGM_DDR.make_alert_doc(year, month, day, hour, RK72h, fullpath_template, savepath_fig, savepath_doc)
        if(alert_doc_re != -1):
            productpath.append(savepath_doc)

        # 制作地磁暴警报文档
        # 1，获取过去72小时中国区域K指数
        RK72h = GEOMAG.FDS.FGM.make_FDS_FGM_DAR.get_RK72H(year, month, day, hour)

        # 2，绘制区域K指数曲线图
        savepath_fig = GEOMAG.FDS.FGM.make_FDS_FGM_DAR.get_savepath_RK72h(year, month, day, hour)
        savepath_fig = os.path.join(rootpath, os.path.split(savepath_fig)[-1])
        GEOMAG.FDS.FGM.make_FDS_FGM_DAR.plot_data_RK72h(year, month, day, hour, RK72h, savepath_fig)

        # 3，生成地磁暴警报文档
        savepath_doc = GEOMAG.FDS.FGM.make_FDS_FGM_DAR.get_savepath_doc(year, month, day)

        # 路径拼接
        savepath_doc = os.path.join(rootpath, os.path.split(savepath_doc)[-1])
        fullpath_template = GEOMAG.FDS.FGM.make_FDS_FGM_DAR.get_doc_template()
        alert_doc_re = GEOMAG.FDS.FGM.make_FDS_FGM_DAR.make_alert_doc(year, month, day, hour, RK72h, fullpath_template, savepath_fig, savepath_doc)
        if (alert_doc_re != -1):
            productpath.append(savepath_doc)

        return productpath
        

    # 读取地磁暴日志文件，生成地磁暴报告文档
    # 读取4个台站同一时刻数据--暂停使用
    # \FDS\geomag\FGM\202003\20200331\HSZJ\HSZJ_FGM01_DDR_L31_01D_20200331000000.dat
    def read_GEOMAG_FDS_FGM_DDR_main(self, inputfile):
        productpath = []
        stations = ['HSZ', 'KSZ', 'LSZ', 'SYZ']
        rootpath, filename = os.path.split(inputfile[0])
        year = int(filename.split('_')[-1][:4])
        month = int(filename.split('_')[-1][4:6])
        day = int(filename.split('_')[-1][6:8])
        for file in inputfile:
            ####检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)

            # 检查台站是否符合
            if(os.path.split(file)[-1][:3] not in stations):
                self.errorinfo = '%s%s' % (file, ' station is not match.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)

        # 1，获取当日4个台站的地磁暴探测仪日报告文件的路径
        # inputfile

        # 2，解析地磁暴探测仪日报告文件
        data = GEOMAG.FDS.FGM.read_FDS_FGM_DDR.read_data(inputfile)

        # 3，绘制K指数柱状图存储路径
        savepath_figs = GEOMAG.FDS.FGM.read_FDS_FGM_DDR.get_savepath_fig(inputfile, year, month, day)

        for k in savepath_figs.keys():
            savepath_figs[k] = self.match_profile(savepath_figs[k])
            productpath.append(savepath_figs[k])

        # 4，绘制K指数柱状图
        fig_paths = GEOMAG.FDS.FGM.read_FDS_FGM_DDR.plot_data(year, month, day, data, savepath_figs)

        # 5，获取地磁暴时间段
        storm_range = GEOMAG.FDS.FGM.read_FDS_FGM_DDR.get_strom_range(year, month, day, data)

        # 6，获取地磁包报告文档保存路径
        savepath = GEOMAG.FDS.FGM.read_FDS_FGM_DDR.get_savepath_doc(rootpath, year, month, day)
        savepath = self.match_profile(savepath)
        productpath.append(savepath)

        # 7，生成地磁暴报告文档
        GEOMAG.FDS.FGM.read_FDS_FGM_DDR.gen_DDR_doc(year, month, day, data, storm_range, fig_paths, savepath)

        # 8,将word转换为pdf
        # pdfsavepath = savepath.replace('.docx', '.pdf')
        # productpath.append(pdfsavepath)
        # GEOMAG.FDS.FGM.wordtopfd.createPdf(savepath, pdfsavepath)

        return productpath

    # 高空数据AFD_UPAR
    def read_AFD_UPAR_main(self, inputfile):
        for file in inputfile:
            ####检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)

        data = ATMOS.FDS.UPAR.read_AFD_UPAR.read_data_upar(inputfile[0])
        
        savepath = inputfile[0].replace('txt', 'png')
        savepath = savepath.replace('DAP', 'IAP')
        # 匹配本地产品目录
        savepath = self.match_profile(savepath)
        
        ATMOS.FDS.UPAR.read_AFD_UPAR.plot_data(data, savepath)

        productpath = savepath
        return productpath

    # 地基-太阳耀斑监测预警
    # 地基-太阳暗条预警
    def solar_flare_filament_alert_main(self, inputfile):
        productpath = []
        print('inputfile = ', inputfile)
        for file in inputfile:
            ####检查路径的合法性
            if (os.path.exists(file) == False):
                self.errorinfo = '%s%s' % (file, ' does not exist.')
                # 若出错直接抛出异常信息
                raise Exception(self.errorinfo)

        temp_savepath = inputfile[0].split('.')[0]
        if not os.path.exists(temp_savepath):
            os.makedirs(temp_savepath)

        # 修改默认目录,确保是程序当前目录
        cwd = os.path.dirname(os.path.abspath(__file__))
        os.chdir(cwd)
        print(cwd)

        # 匹配本地产品目录
        savepath = self.match_profile(inputfile[0])
        png_file = savepath.replace('.FITS', '.PNG')
        png_file = png_file.replace('_L11_', '_L31_')

        # 太阳耀斑产品图像文件
        flare_png_file = png_file.replace('_CHA_', '_IFM_')
        # 太阳暗条产品图像文件
        filament_png_file = png_file.replace('_CHA_', '_IDM_')

        # 太阳耀斑
        # 创建配置文件并写入数据
        flare_config_file = os.path.join(temp_savepath, 'alert.ini')
        with open(flare_config_file, "w", encoding='utf-8') as fp:
            fp.write("flare_alert\n")
            fp.write(inputfile[0]+'\n')
            fp.write(flare_png_file)
        fp.close()

        # 拼接执行命令字符串
        exec_cmd = 'ALERT_INI_PATH=%s '%flare_config_file + 'SolarExec/alert/Solar_Alert-0.9.4.bin'
        print(exec_cmd)

        # 执行可执行程序
        os.system(exec_cmd)
        productpath.append(flare_png_file)

        # 太阳暗条
        # 创建配置文件并写入数据
        filament_config_file = os.path.join(temp_savepath, 'alert.ini')
        with open(filament_config_file, "w", encoding='utf-8') as fp:
            fp.write("filament_alert\n")
            fp.write(inputfile[0]+'\n')
            fp.write(filament_png_file)
        fp.close()

        # 拼接执行命令字符串
        exec_cmd = 'ALERT_INI_PATH=%s '%filament_config_file + 'SolarExec/alert/Solar_Alert-0.9.4.bin'
        print(exec_cmd)

        # 执行可执行程序
        os.system(exec_cmd)
        productpath.append(filament_png_file)

        return productpath

    # 可视化界面调用太阳质子事件预警、太阳耀斑预报、太阳质子事件预报
    def solar_interface_dispatch(self, select_id):
        # 通过id查询数据库
        database_name = 'dq1044'
        sqlcmd = 'select * from t_solar_pre where id = ' + select_id

        print('sqlcmd = ', sqlcmd)

        postar = db.postgres_archive.PostgresArchive()
        dbresult = postar.search_db_table_usercmd(database_name, sqlcmd)

        print('dbresult = ', dbresult)

        task_type = dbresult[0]['tasktype']

        print('task_type = ', task_type)

        #task_type = 'spe_alert'
        #task_type = 'flare_forecast'
        #task_type = 'spe_forecast'

        print('task_type = ', task_type)

        # 太阳质子事件预警
        if task_type == 'spe_alert':
            self.solar_spe_alert_main(postar, database_name, select_id, dbresult)

        # 太阳耀斑预报
        elif task_type == 'flare_forecast':
            self.solar_flare_forecast_main(postar, database_name, select_id, dbresult)

        # 太阳质子事件预报
        elif task_type == 'spe_forecast':
            self.solar_spe_forecast_main(postar, database_name, select_id, dbresult)

        # 其他类型报错
        else:
            self.errorinfo = 'ERROR:tasktype is not match'
            raise Exception(self.errorinfo)

    # 太阳质子事件预警
    def solar_spe_alert_main(self, postar, database_name, select_id, dbresult):
        # 修改默认目录,确保是程序当前目录
        #cwd = os.getcwd()
        cwd = r"/home/DQ1044/code/code_prj" 
        os.chdir(cwd)
        print('cwd = ',cwd)

        inputfile = dbresult[0]['inputfile']
        #inputfile = r'/home/DQ1044/code/code_prj/SolarExec/alert/datas/KSZJ_SOT01_CGC_L11_STP_20200520123004.FITS'
        x = dbresult[0]['x']
        y = dbresult[0]['y']
        width = dbresult[0]['width']
        outputfile = self.match_profile(outputfile)
        temp_value = str(int(float(x))) + ',' + str(int(float(y))) + ',' + str(int(float(width)))
        outputfile = inputfile.split('.')[0] + '.txt'
        # 匹配本地产品目录
        outputfile = self.match_profile(outputfile)
        outputfile = outputfile.replace('_L11_', '_L31_')

        print('temp_value = ', temp_value)

        # 创建配置文件并写入数据
        config_file = os.path.join(inputfile.split('.')[0], 'alert.ini')
        if not os.path.exists(inputfile.split('.')[0]):
            os.makedirs(inputfile.split('.')[0])
        with open(config_file, "w", encoding='utf-8') as fp:
            fp.write("spe_alert\n")
            fp.write(inputfile + '\n')
            fp.write(outputfile + '\n')
            fp.write(temp_value)
        fp.close()
        print('config_file = ', config_file)

        # 拼接执行命令字符串
        exec_cmd = 'ALERT_INI_PATH=%s ' % config_file + 'SolarExec/alert/Solar_Alert-0.9.4.bin'

        # 执行可执行程序
        os.system(exec_cmd)
        
        # 读文件
        with open(outputfile, "r", encoding='utf-8') as fp:
            lines = fp.read().splitlines()
        result = lines[0] + ',' + lines[1] + ',' + lines[2]
        flag = 1

        outputfile = outputfile[outputfile.find('FDS')-1:]
        
        update_dict = {}
        where_dict = {}
        
        update_dict['result'] = result
        update_dict['resultfile'] = outputfile
        update_dict['flag'] = flag
        
        where_dict['id'] = select_id
        
        # 数据更新到表
        table_name = 't_solar_pre'
        postar.update_db_table(database_name, table_name, update_dict, where_dict)

    #太阳耀斑预报
    def solar_flare_forecast_main(self, postar, database_name, select_id, dbresult):
        # 修改默认目录,确保是程序当前目录
        #cwd = os.getcwd()
        cwd = r"/home/DQ1044/code/code_prj" 
        os.chdir(cwd)
        print('cwd = ',cwd)

        inputfile = dbresult[0]['inputfile']
        #inputfile = r'/home/DQ1044/code/code_prj/SolarExec/alert/datas/KSZJ_SOT01_CHA_L11_STP_20200520131004.FITS'
        x = dbresult[0]['x']
        y = dbresult[0]['y']
        width = dbresult[0]['width']
        temp_value = str(int(float(x))) + ',' + str(int(float(y))) + ',' + str(int(float(width)))
        outputfile = inputfile.split('.')[0] + '.txt'
        # 匹配本地产品目录
        outputfile = self.match_profile(outputfile)
        outputfile = outputfile.replace('_CHA_', '_DFF_')
        outputfile = outputfile.replace('_L11_', '_L31_')

        print('temp_value = ', temp_value)

        # 创建配置文件并写入数据
        config_file = os.path.join(inputfile.split('.')[0], 'forecast.ini')
        if not os.path.exists(inputfile.split('.')[0]):
            os.makedirs(inputfile.split('.')[0])
        with open(config_file, "w", encoding='utf-8') as fp:
            fp.write("flare_forecast\n")
            fp.write(inputfile + '\n')
            fp.write(temp_value + '\n')
            fp.write(outputfile)
        fp.close()
        print('config_file = ', config_file)

        # 拼接执行命令字符串
        exec_cmd = 'FORECAST_INI_PATH=%s ' % config_file + 'SolarExec/forecast/Solar_Forecast-0.9.2.bin'

        # 执行可执行程序
        os.system(exec_cmd)
        
        # 读文件
        with open(outputfile, "r", encoding='utf-8') as fp:
            lines = fp.read().splitlines()
        result = lines[0]
        flag = 1
        
        outputfile = outputfile[outputfile.find('FDS')-1:]
        print('outputfile = ', outputfile)

        update_dict = {}
        where_dict = {}
        
        update_dict['result'] = result
        update_dict['resultfile'] = outputfile
        update_dict['flag'] = flag
        
        where_dict['id'] = select_id
        
        # 数据更新到表
        table_name = 't_solar_pre'
        postar.update_db_table(database_name, table_name, update_dict, where_dict)

    #太阳质子事件预报
    def solar_spe_forecast_main(self, postar, database_name, select_id, dbresult):
        # 修改默认目录,确保是程序当前目录
        #cwd = os.getcwd()
        cwd = r"/home/DQ1044/code/code_prj" 
        os.chdir(cwd)
        print('cwd = ',cwd)

        inputfile = dbresult[0]['inputfile']
        #inputfile = r'/home/DQ1044/code/code_prj/SolarExec/alert/datas/KSZJ_SOT01_CHA_L11_STP_20200520131004.FITS'
        x = dbresult[0]['x']
        y = dbresult[0]['y']
        width = dbresult[0]['width']
        ssarea = str(int(float(dbresult[0]['ssarea'])))
        i_location = int(float(dbresult[0]['location']))
        location = ''
        if i_location > 0:
            location = 'E' + str(i_location)  
        elif i_location < 0:
            location = 'W' + str(abs(i_location))
        else:
            self.errorinfo = 'ERROR:tasktype is not match'
            raise Exception(self.errorinfo)

        magtype = dbresult[0]['magtype']
        mcintoch = dbresult[0]['mcintoch']
        xflux = dbresult[0]['xflux']

        temp_value = str(int(float(x))) + ',' + str(int(float(y))) + ',' + str(int(float(width)))
        outputfile = inputfile.split('.')[0] + '.txt'
        # 匹配本地产品目录
        outputfile = self.match_profile(outputfile)
        outputfile = outputfile.replace('_CHA_', '_DPF_')
        outputfile = outputfile.replace('_L11_', '_L31_')

        print('temp_value = ', temp_value)

        # 创建配置文件并写入数据
        config_file = os.path.join(inputfile.split('.')[0], 'forecast.ini')
        if not os.path.exists(inputfile.split('.')[0]):
            os.makedirs(inputfile.split('.')[0])
        with open(config_file, "w", encoding='utf-8') as fp:
            fp.write("spe_forecast\n")
            fp.write(inputfile + '\n')
            fp.write(temp_value + '\n')
            fp.write(ssarea + '\n')
            fp.write(location + '\n')
            fp.write(magtype + '\n')
            fp.write(mcintoch + '\n')
            fp.write(xflux + '\n')
            fp.write(outputfile)
        fp.close()
        print('config_file = ', config_file)

        # 拼接执行命令字符串
        exec_cmd = 'FORECAST_INI_PATH=%s ' % config_file + 'SolarExec/forecast/Solar_Forecast-0.9.2.bin'

        # 执行可执行程序
        os.system(exec_cmd)
        
        # 读文件
        with open(outputfile, "r", encoding='utf-8') as fp:
            lines = fp.read().splitlines()
        result = lines[0]
        flag = 1

        outputfile = outputfile[outputfile.find('FDS')-1:]
        print('outputfile = ', outputfile)
        
        update_dict = {}
        where_dict = {}
        
        update_dict['result'] = result
        update_dict['resultfile'] = outputfile
        update_dict['flag'] = flag
        
        where_dict['id'] = select_id
        
        # 数据更新到表
        table_name = 't_solar_pre'
        postar.update_db_table(database_name, table_name, update_dict, where_dict)

    # 匹配台站
    def match_station(self, inputFile):
        rootpath, filename = os.path.split(inputFile[0])
        stationID = filename[:3]
        if str(inputFile).find('FDS') != -1:
            stations = station.station_info.get_FDS_station_id_name()
        elif str(inputFile).find('MDP') != -1:
            stations = station.station_info.get_MDP_station_id_name()

        # station_name = stations[stationID]
        for stations_id in stations.keys():
            if (stationID == stations_id):
                station_name = stations[stationID]
                break
            station_name = "未知"
            # print(station_name)

        # print(station_name)
        return station_name
