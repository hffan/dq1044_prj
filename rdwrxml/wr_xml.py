import sys
import os
import xml.etree.ElementTree as ET


class WriteOutputXml(object):
    def __init__(self, xmlpath):
        self.xmlpath = xmlpath  # xml输出全路径
        return

    ####xml自动缩进,类函数，需要self参数
    def indent(self, elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, (level + 1))
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    # # 输出xml文件
    # def test_writexml(self):
    #     ## tag,attribute,text
    #     # 创建根节点xml，并为xml添加熟性值
    #     xml = ET.Element('xml', {'identify': 'Iono'})
    #
    #     # 添加子节点SubElement(父节点Element对象， Tag字符串格式， Attribute字典格式)
    #     log = ET.SubElement(xml, 'log')  ##为log添加熟性
    #     # 添加子节点
    #     status = ET.SubElement(log, 'status')
    #     # 给节点status添加熟性
    #     status.text = '1'
    #     # 添加子节点
    #     status = ET.SubElement(log, 'info')
    #     # 给节点status添加熟性
    #     status.text = 'Success!'
    #
    #     outFiles = ET.SubElement(xml, 'outFiles')
    #     type = ET.SubElement(outFiles, 'type', {'producttype': 'std'})
    #     file = ET.SubElement(type, 'file', {'type': '.jpg'})
    #     ##windows路径使用双斜杠，否则会当成转义字符处理，输出产品目录自己定义
    #     file.text = 'C:\\Users\\Administrator\\Desktop\\DQ1044_centos7.1\\code_prj\\product\\a.jpg'
    #
    #     # xml文件添加自动缩进操作
    #     self.indent(xml, level=0)
    #     # 将根目录转化为xml树状结构(即ElementTree对象) 
    #     tree = ET.ElementTree(xml)
    #     # 在终端显示整个xml内容 
    #     ET.dump(xml)
    #     # 写入xml文件,<?xml version='1.0' encoding='utf-8'?> 文件头声明
    #     tree.write(self.xmlpath, encoding="utf-8", xml_declaration=True)
    
    # 输出xml文件
    def writexml(self, identify_attribute,
                 status_text,
                 info_text,
                 producttype_attribute,
                 #type_attribute,
                 file_texts):
        ## tag,attribute,text
        # 创建根节点xml，并为xml添加属性值
        xml = ET.Element('xml', {'identify': identify_attribute})

        # 添加子节点SubElement(父节点Element对象， Tag字符串格式， Attribute字典格式)
        log = ET.SubElement(xml, 'log')  ##为log添加
        # 添加子节点
        status = ET.SubElement(log, 'status')
        # 给节点status添加熟性
        status.text = status_text
        # 添加子节点
        info = ET.SubElement(log, 'info')
        # 给节点status添加熟性
        info.text = info_text

        outFiles = ET.SubElement(xml, 'outFiles')


        type = ET.SubElement(outFiles, 'type', {'producttype': producttype_attribute})

        for file_text in file_texts:
            productname, type_attribute = os.path.splitext(file_text)
            file = ET.SubElement(type, 'file', {'type': type_attribute})
            ##windows路径使用双斜杠，否则会当成转义字符处理，输出产品目录自己定义
            file.text = file_text

        # xml文件添加自动缩进操作
        self.indent(xml, level=0)
        # 将根目录转化为xml树状结构(即ElementTree对象) 
        tree = ET.ElementTree(xml)
        # 在终端显示整个xml内容 
        
        #### java调用的时候，显示是乱码，编码格式不兼容
        #ET.dump(xml)
        
        
        # 写入xml文件,<?xml version='1.0' encoding='utf-8'?> 文件头声明
        tree.write(self.xmlpath, encoding="utf-8", xml_declaration=True)
