#!/usr/bin/python
# -*- coding: UTF-8 -*-
from matplotlib.font_manager import FontProperties #字体管理器
from cfg import *

##读取配置文件中文字体
fonts_path=configs['fonts_path']
#myfont = FontProperties(fname=fonts_path)
myfont = FontProperties(fname=fonts_path,size=12)