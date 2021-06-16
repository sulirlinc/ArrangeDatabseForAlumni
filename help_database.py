# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 21:52:37 2020

@author: 王志
"""

##帮助进行数据库的数据处理

import xlrd
import pandas as pd
import numpy as np
import os
import shutil
from mpl_toolkits.mplot3d import Axes3D
import matplotlib as mpl
from scipy import interpolate
import matplotlib.cm as cm
import matplotlib.pyplot as plt
import re
from enum import Enum
from datetime import datetime
import time
import json

##无效的回答信息
unvalid_str=["nan","(空)","暂无","(跳过)","无"]
#互联网公司的枚举
network_rule=["腾讯","阿里","百度","字节跳动","小米","美团",
              "拼多多","oppo","OPPO","vivo","VIVO","华为",
              "中兴","苹果","京东","360","奇虎","网易","平安科技",
              "微软","亚马逊","Face","招联金融","微众银行","乐信","富途",
              "银联","qq音乐","爱奇艺","携程","滴滴","猿","旷视","寒武纪"]
##无用的表头信息的筛选
unused_comment_header=["时间","序号","代码","来源","来自IP","愿意","参与"]

##主流城市或省市的筛选
common_city_list=["深圳","广州","厦门","上海","北京","成都","苏州",
                           "福州","杭州","东莞","潮州","重庆","武汉","西安",
                           "天津","大连","济南","南京","郑州","长沙","沈阳",
                           "青岛","海口","宁波","无锡","佛山","合肥","石家庄","中山"]
common_province_list=["广东","浙江","湖南","江西","山东","海南","江苏","河北","山西","陕西","福建","湖北","四川","广西","云南"]
##大湾区相关城市
big_valley_area=["香港","澳门","广州","深圳","珠海","佛山","惠州","东莞","中山","江门","肇庆"]
##深圳相关
shenzhen_about_area=["蛇口","南山","福田","罗湖","宝安","盐田","龙华","坪山","龙岗"]



new_headers=["其他"]
Header_judge_rule=30
TWO_much_header_judge=36##内容大于该长度无效

def check_valid(data):
    ##判断当前的字段是有效的字段    
    if("/" in str(data) or str(data)=='' or str(data) in unvalid_str or pd.isnull(data)):
        return False
    else:
        return True
def check_useful_header(data):
    for head in unused_comment_header:
        if head in data:
            return False
    return True
    
class work_save:
      '''
      具体到每一条的简历信息记录
      '''
      def __init__(self,time_str):
        self.work_time=time_str ##对应时间
        self.company='' ##曾经的公司名字
        self.old_level='' ##曾经的职务
        self.old_industry='' ##曾经的工作行  业 
      def to_dict(self):
        res={}
        res["工作时间"]=str(self.work_time)
        res["单位名称"]=self.company
        res["公司职务"]=self.old_level
        res["工作行业"]=self.old_industry
        return res
          
    
class resume:
    '''
    用来储存每个人的过往工作经历，方便后期可以转化为json等其他格式
    '''
    def __init__(self,name=""): 
        self.data_num=0 ##简历的条数
        self.past_work=[] ##储存过往经历   


class school(Enum):
    '''
    枚举了可能的学院或者叫来源
    
    '''
    huifeng_sc="汇丰商学院"
    law_sc="法学院"
    inter_law_sc="国际法学院"
    elec_sc="信息工程学院"
    city_sc="城市规划与设计学院"
    chemi_sc="化学生物学与生物技术学院"
    human_sc="人文社会科学学院"
    energy_sc="环境与能源学院"
    new_mate_sc="新材料学院"
    manage_sc="培训中心"
    others="其他"
    
    
class people:
    '''
    这里储存了每个人的基本信息，主要包括如下'''
    count=0##计数   
    def __init__(self,name=""): 
 ##程辅助信息##
        self.resume_data_num=0 ##简历的数据条数
        self.resume=resume()
        self.last_update_time=""
  #首先基本信息#    
        self.number="" #入库编号
        self.name=""#姓名
        self.stu_number="" ##学号
        self.sex="" ##性别，1是男，2是女
        self.birth="" ##出生年月日，字符串表示
        self.degree="" ##学位，硕士或者博士
        self.in_school_year=""#入学年份
        self.out_school_year=""#毕业年份
        self.school="" #所在学院或者来源
        self.master=""#专业
        self.master_deri=""#专业方向
        self.teacher=""#导师名字
        self.rais_ways="" ##培养方式，全日制或者非全日制
   #后是工作相关'''     
        self.head_loc="" ##现在的省地址
        self.city="" ##现在的城市
        self.company="" ##现在的工作单位
        self.old_company=""##曾经工作单位
        self.interpiece="" ##所在行业
        self.level="" ##对应的职务
     #联系方式相关   
        self.contect_people=""##单位联系人
        self.com_phone=""##单位联系电话
        self.com_emial=""#单位的邮箱
        self.phone=""#手机电话
        self.emial="" #电子邮箱
        self.contact_loc=""#通讯地址
        self.qq="" ##qq号
        self.wechat="" #微信号
        self.idtype=""#证件类别
        self.id=""#证件号码
        
        #最后是其他无关的信息'''
        self.jiguan="" #对应籍贯
        self.if_has_card="" #是否有校友卡
        self.card_number="" #校友卡号
        self.plus="" #备注
        self.marrige="" #婚姻情况
        self.lover_in="" #爱人的情况
        self.family_loc="" #家庭住址
        self.family_contect=""#家庭联系方式
        self.flag=""#标签是什么
        self.head="" #校友头像
        self.habbit="" #爱好
        self.stu_from="" #生源所在地
        
        ##后期补充的信息
        self.others_information={} ##其他信息，放到键值对里面
    def save_resume(self,OUT_path):
        ##向给定的路径下书写对应的简历        
        file_name=str(self.name)+'_'+str(self.number)
        with open(OUT_path+file_name+".json",'a',encoding='utf-8') as f:
            out=[]
            for i in range(len(self.resume.past_work)):
                out.append(self.resume.past_work[i].to_dict())
            json.dump(out,f,ensure_ascii=False,indent=4)
        f.close()
        return
    def updata_base_plus1(self,data): ##基于plus1文件进行信息的更新
        self.number=people.count
#        people.count+=1        
        if(self.name == np.nan and data[1]!= np.nan):
            self.name=str(data[1]).strip()
        if(check_valid(data[2])==True):
            self.stu_number=data[2]
        if(check_valid(data[3])==True):
            self.sex=data[3]
        if(check_valid(data[5])==True):
            self.school=data[5]
        if(check_valid(data[6])==True):
            self.master=data[6]
        if(check_valid(data[8])==True):  
            self.degree=data[8]
        if(check_valid(data[10])==True):
            self.stu_from=data[10]
        if(check_valid(data[12])==True):
            self.phone=data[12]
        if(check_valid(data[14])==True):
            self.emial=data[14]
        if(check_valid(data[17])==True):
            self.family_loc=data[17]
        if(check_valid(data[18])==True):
            self.family_contect=data[18]
        if(check_valid(data[27])==True):
            self.head_loc=data[27]
            ##关于公司的判断
        if(check_valid(data[24])==True):
            self.company=data[24]
        if(check_valid(data[25])==True):
            self.company=data[25]
        if(check_valid(data[26])==True):
            self.company=data[26]
        if(check_valid(data[28])==True):
            self.interpiece=data[28]
        if(check_valid(data[33])==True):
            self.interpiece=data[33]
        if(check_valid(data[37])==True):
            self.contact_loc=data[37]
        if(check_valid(data[38])==True):
            self.contect_people=data[38]
        if(check_valid(data[39])==True):
            self.com_phone=data[39]
        if(check_valid(data[41])==True):
            self.com_emial=data[41]           
        if(check_valid(data[46])==True):
            self.level=data[46]
        if(check_valid(data[47])==True):
            self.level=data[47]
        if(check_valid(data[70])==True): 
            self.contact_loc=data[70]
        if(check_valid(data[93])==True):
            self.in_school_year=data[93]
        if(check_valid(data[94])==True):
            self.out_school_year=data[94]
        if(check_valid(data[95])==True):
            self.qq=data[95]
        if(check_valid(data[96])==True):
            self.wechat=data[96] 
        if(check_valid(data[97])==True):
            self.idtype=data[97]
        if(check_valid(data[98])==True):
            self.id=data[98]
        if(check_valid(data[99])==True):
            self.birth=data[99]
        if(check_valid(data[100])==True):
            self.sex=data[100]
        return
        
    def update_resume_baseindex(self,flag_update,flag_index,data,update_time):
        ##读取其他的旧的信息，更新自己的简历
        falg_use=False
        if("15" in flag_update or "17" in flag_update or "18" in flag_update):
            falg_use=True
        else:
            falg_use=False
            return
        one_work=work_save(self.last_update_time)
        if ("15" in flag_update):
            com_index=flag_update.index("15")
            one_work.company=data[flag_index[com_index]]
        if("17" in flag_update):
            com_index=flag_update.index("17")
            one_work.old_industry=data[flag_index[com_index]]
        if("18" in flag_update):
            com_index=flag_update.index("18")
            one_work.old_level=data[flag_index[com_index]]
        self.resume.past_work.append(one_work)
        self.resume_data_num+=1
        return 
    def out_print_plus(self,file_f):
        ##其他业务需求下，输出的其他信息,注意和new_headers对应
        file_f.write(str(self.others_information))
        file_f.write("\t")
        return
        
    def out_print(self,file_f):
        ##像一个文件输出所有信息
        if(check_valid(self.name)==False):
            print("{}无效，本记录无效！".format(self.name))
            os.system("pause")
            return
    
        file_f.write(str(self.number))
        file_f.write("\t")
        file_f.write(str(self.name))
        file_f.write("\t")
        file_f.write(str(self.stu_number))
        file_f.write("\t")
        file_f.write(str(self.sex))
        file_f.write("\t")
        ##注意输出生日的修改，只输出年月日就好
        
        try:
            input_str=str(self.birth).split()[0]
            input_str=input_str.split("\r")[0]
            time_col=time.strptime(input_str,"%Y-%m-%d")
            birth_str=time.strftime('%Y-%m-%d',time_col)
            file_f.write(str(birth_str))
        except:
            file_f.write(str(self.birth))           
            
        file_f.write("\t")
        file_f.write(str(self.degree))
        file_f.write("\t")
        file_f.write(str(self.in_school_year))
        file_f.write("\t")
        file_f.write(str(self.out_school_year))
        file_f.write("\t")
        file_f.write(str(self.school))
        file_f.write("\t")
        file_f.write(str(self.master))
        file_f.write("\t")
        file_f.write(str(self.master_deri))
        file_f.write("\t")
        file_f.write(str(self.teacher))
        file_f.write("\t")
        file_f.write(str(self.rais_ways))
        file_f.write("\t")
        file_f.write(str(self.head_loc))
        file_f.write("\t")
        file_f.write(str(self.city))
        file_f.write("\t")
        file_f.write(str(self.company))
        file_f.write("\t")
        file_f.write(str(self.old_company))
        file_f.write("\t")
        file_f.write(str(self.interpiece))
        file_f.write("\t")
        file_f.write(str(self.level))
        file_f.write("\t")
        
        ##工作相关
        file_f.write(str(self.contect_people))
        file_f.write("\t")
        file_f.write(str(self.com_phone))
        file_f.write("\t")
        file_f.write(str(self.com_emial))
        file_f.write("\t")
        file_f.write(str(self.phone))
        file_f.write("\t")
        file_f.write(str(self.emial))
        file_f.write("\t")
        file_f.write(str(self.contact_loc))
        file_f.write("\t")
        file_f.write(str(self.qq))
        file_f.write("\t")
        file_f.write(str(self.wechat))
        file_f.write("\t")      
#    ##证件号和其他信息
        file_f.write(str(self.idtype))
        file_f.write("\t")
        file_f.write(str(self.id))
        file_f.write("\t")
        file_f.write(str(self.jiguan))
        file_f.write("\t")
        file_f.write(str(self.if_has_card))
        file_f.write("\t")
        file_f.write(str(self.card_number))
        file_f.write("\t")
        file_f.write(str(self.plus))
        file_f.write("\t")
##家庭信息
        file_f.write(str(self.marrige))
        file_f.write("\t")
        file_f.write(str(self.lover_in))
        file_f.write("\t")
        file_f.write(str(self.family_loc))
        file_f.write("\t")
        file_f.write(str(self.family_contect))
        file_f.write("\t")
        file_f.write(str(self.flag))
        file_f.write("\t")
        file_f.write(str(self.head))
        file_f.write("\t")
        file_f.write(str(self.habbit))
        file_f.write("\t")
        file_f.write(str(self.stu_from))
        file_f.write("\t")        
        return 
    def update_base_index(self,flag_update,flag_index,data,update_time):
        ##核心函数之一，读取外界的标记，返回相关信息
        self.last_update_time=update_time        
        for i in range(len(flag_update)):
            if(check_valid(data[flag_index[i]])==False):
                continue
            if(flag_update[i]=="1"):
                self.name=data[flag_index[i]]
            elif(flag_update[i]=="2"):
                self.stu_number=data[flag_index[i]]
            elif(flag_update[i]=="3"):
                self.sex= data[flag_index[i]]
            elif(flag_update[i]=="4"):
                self.birth=data[flag_index[i]]
            elif(flag_update[i]=="5"):
                self.degree=data[flag_index[i]]
            elif(flag_update[i]=="6"):
                self.in_school_year= data[flag_index[i]]
            elif(flag_update[i]=="7"):
                self.out_school_year=data[flag_index[i]]
            elif(flag_update[i]=="8"):
                self.school=data[flag_index[i]]
            elif(flag_update[i]=="9"):
                self.master= data[flag_index[i]]
            elif(flag_update[i]=="10"):
                self.master_deri=data[flag_index[i]]
            elif(flag_update[i]=="11"):
                self.teacher=data[flag_index[i]]
            elif(flag_update[i]=="12"):
                self.rais_ways= data[flag_index[i]]
            elif(flag_update[i]=="13"):
                self.head_loc=data[flag_index[i]]
            elif(flag_update[i]=="14"):
                self.city=data[flag_index[i]]
            elif(flag_update[i]=="15"):
                self.company= data[flag_index[i]]
            elif(flag_update[i]=="16"):
                self.old_company=data[flag_index[i]]
            elif(flag_update[i]=="17"):
                self.interpiece=data[flag_index[i]]
            elif(flag_update[i]=="18"):
                self.level= data[flag_index[i]]
            elif(flag_update[i]=="19"):
                self.contect_people=data[flag_index[i]]
            elif(flag_update[i]=="20"):
                self.com_phone=data[flag_index[i]]
            elif(flag_update[i]=="21"):
                self.com_emial= data[flag_index[i]]
            elif(flag_update[i]=="22"):
                self.phone=data[flag_index[i]]
            elif(flag_update[i]=="23"):
                self.emial=data[flag_index[i]]
            elif(flag_update[i]=="24"):
                self.contact_loc= data[flag_index[i]]
            elif(flag_update[i]=="25"):
                self.qq=data[flag_index[i]]
            elif(flag_update[i]=="26"):
                self.wechat=data[flag_index[i]]   

    ##证件号和其他信息
            elif(flag_update[i]=="27"):
                self.idtype=data[flag_index[i]]
            elif(flag_update[i]=="28"):
                self.id=data[flag_index[i]]
            elif(flag_update[i]=="29"):
                self.jiguan= data[flag_index[i]]
            elif(flag_update[i]=="30"):
                self.if_has_card=data[flag_index[i]]
            elif(flag_update[i]=="31"):
                self.card_number=data[flag_index[i]]
            elif(flag_update[i]=="32"):
                self.plus= data[flag_index[i]]
                ##家庭信息
            elif(flag_update[i]=="33"):
                self.marrige=data[flag_index[i]]
            elif(flag_update[i]=="34"):
                self.lover_in=data[flag_index[i]]
            elif(flag_update[i]=="35"):
                self.family_loc=data[flag_index[i]]
            elif(flag_update[i]=="36"):
                self.family_contect=data[flag_index[i]]
            elif(flag_update[i]=="37"):
                self.flag=data[flag_index[i]]
            elif(flag_update[i]=="38"):
                self.head=data[flag_index[i]]
            elif(flag_update[i]=="39"):
                self.habbit=data[flag_index[i]]
            elif(flag_update[i]=="40"):
                self.stu_from=data[flag_index[i]]
        return 
                
            
            
    def plus_self_resume(self):  ##自我更新简历信息
        self.resume_data_num+=1
        one_work=work_save(self.last_update_time)
        one_work.company=self.company
        one_work.old_industry=self.interpiece
        one_work.old_level=self.level
        self.resume.past_work.append(one_work)
    def update_resume_out(self,data,time):  ##读外面更新简历信息
        self.resume_data_num+=1
        one_work=work_save(time)
        if(str(data[24])!=""):
            one_work.company=data[24]
        if(str(data[25])!=""):
            one_work.company=data[25]
        if(str(data[26])!=""):
            one_work.company=data[26]
        one_work.old_industry=data[28]
        if(str(data[46])!=""):
            one_work.old_level=data[46]
        if(str(data[47])!=""):
            one_work.old_level=data[47]
        self.resume.past_work.append(one_work)
    def inrich_others_inforamtion(self,save):
        for key in save.keys():
          if key not in dict(self.others_information).keys():            
              self.others_information[key]=save[key]
        return
    def fulfill_location(self):
        ##根据工作的公司推算出当前的定居地
        if(check_valid(self.city)==False and check_valid(self.company)==True):
          ##首先是筛选深圳的可能
          for area in shenzhen_about_area:
              if(area in self.company):
                  self.city="深圳"
                  break
          ##然后是热门城市的
          for city in common_city_list:
              if(city in self.company):
                  self.city=city
                  break
          ##最后是相关省份的
          for province in common_province_list:
              if(province in self.company):
                  self.city=province
                  break    
          #print("城市："+str(self.city)+"，工作单位是:"+str(self.company))
        return
              



def get_time_col_heng_excel(time_str):
    try:
        time_col=time.strptime(str(time_str),"%Y-%m-%d %H:%M:%S")
        return time.mktime(time_col)
    except:
        try:
            time_col=time.strptime(str(time_str),"%Y-%m-%d")
            return time.mktime(time_col)
        except:
            return 0.0
def get_time_col_hengxian(time_in):
    time_str=time.strptime(str(time_in),"%Y-%m-%d")
    return time.mktime(time_str)
    
    return time.mktime(time_str)
def generate_file(path,result_name="path_file.txt"):
    name=[]   
    name=os.listdir(path)   
    fo=open(result_name,"w")
    for line in name:
      fo.write(str(line))
      fo.write("\n")
    fo.close()
def compare_date(time1,time2):
    ##输入两个时间字符串，返回两个时间的比较，0表示相同，1表示前面时间大，-1表示后面时间大
#    print(time1)
#    print(time2)
    if(str(time1)=="NaT" and str(time2)=="NaT"):
        return 0
    if(str(time1)=="NaT"):
        return -1
    if(str(time2)=="NaT"):
        return 1
    if(pd.isnull(time1) and pd.isnull(time2)):
        return 0
    if(pd.isnull(time1)):
        return -1
    if(pd.isnull(time2)):
        return 1
    try:
        time_stra=time.strptime(str(time1),"%Y-%m-%d %H:%M:%S")
    except:
        time_stra=time.strptime(str(time1),"%Y-%m-%d")
    try:
        time_strb=time.strptime(str(time2),"%Y-%m-%d")
    except:
        time_strb=time.strptime(str(time1),"%Y-%m-%d %H:%M:%S")        
    col_a=time.mktime(time_stra)
    col_b=time.mktime(time_strb)
    if(col_a==col_b):
        return 0
    elif(col_a>col_b):
        return 1
    else:
        return -1
def full_fill_base_datasingleline(data_line):
    schoolfellow=people()
    schoolfellow.number= data_line[0]
    people.count+=1
    schoolfellow.name=str(data_line[1]).strip()
    schoolfellow.stu_number=data_line[2]   
    schoolfellow.sex= data_line[3]
    schoolfellow.birth=data_line[4]
    schoolfellow.degree=data_line[5]
    schoolfellow.in_school_year= data_line[6]
    schoolfellow.out_school_year=data_line[7]
    schoolfellow.school=data_line[8]
    schoolfellow.master= data_line[9]
    schoolfellow.master_deri=data_line[10]
    schoolfellow.teacher=data_line[11]
    schoolfellow.rais_ways= data_line[12]
    schoolfellow.head_loc=data_line[13]
    schoolfellow.city=data_line[14]
    schoolfellow.company= data_line[15]
    schoolfellow.old_company=data_line[16]
    schoolfellow.interpiece=data_line[17]
    schoolfellow.level= data_line[18]
    schoolfellow.contect_people=data_line[19]
    schoolfellow.com_phone=data_line[20]
    schoolfellow.com_emial= data_line[21]
    schoolfellow.phone=data_line[22]
    schoolfellow.emial=data_line[23]
    schoolfellow.contact_loc= data_line[24]
    schoolfellow.qq=data_line[25]
    schoolfellow.wechat=data_line[26]      

    ##证件号和其他信息
    schoolfellow.idtype=data_line[27]
    schoolfellow.id=data_line[28]
    schoolfellow.jiguan= data_line[29]
    schoolfellow.if_has_card=data_line[30]
    schoolfellow.card_number=data_line[31]
    schoolfellow.plus= data_line[32]
    ##家庭信息
    schoolfellow.marrige=data_line[33]
    schoolfellow.lover_in=data_line[34] 
    schoolfellow.family_loc=data_line[35]
    schoolfellow.family_contect=data_line[36] 
    schoolfellow.flag=data_line[37]
    schoolfellow.head=data_line[38] 
    schoolfellow.habbit=data_line[39]
    schoolfellow.stu_from=data_line[40] 
    
    ##备注信息
    schoolfellow.others_information=eval(data_line[41])
    return schoolfellow
      



def check_name_and_phone(temp_name,temp_school,base_data):  
    ##用来确定是不是疑似的函数
    if(temp_name=='' or temp_school==''):
        return False,-2
    for i in range(len(base_data)):
        if(temp_name==base_data[i].name and temp_school==base_data[i].phone):
            return True,i
    return False,-2

def match_name(name):
    if("(" in name and ")" in name):  
        return True    
    if("（" in name and "）" in name):
        return True
    if('/' in name or "海闻" in name):
        return False
    res=re.match(r'^(?:[\u4e00-\u9fa5]+)(?:·[\u4e00-\u9fa5]+)*$|^[a-zA-Z0-9]+\s?[\s\.·\-()a-zA-Z]*[a-zA-Z]+$',str(name))
#    print(res)
    if(res):
        return True
    else: 
        return False

def wash_the_excel(file,raws,cols):
    for raw in raws:
            for col in cols:
                replace_str=str(file.loc[raw][col])
                if("\n" in replace_str):
                    replace_str=replace_str.replace("\n",' ')     
                    file.loc[raw,col]=replace_str
                
def check_name_and_id(temp_name,temp_school,base_data):  
    ##用来确定是不是疑似的函数
    if(temp_name=='' or temp_school==''):
        return False,-2
    for i in range(len(base_data)):
        if(temp_name==base_data[i].name and temp_school==base_data[i].school):
            return True,i
    return False,-2

def read_base_excel(file,base_data,update_time):  ##读取一个excel信息，并且完善base——data部分
    print("读取基础整理的数据，文件列的顺序不要改变！")
    all_school_fellownames=[]
    all_id=[]
    try:
        wb = xlrd.open_workbook(file)
    except:
        print("找不到文件{},请检查".format(file))
        time.sleep(5)
        os._exit(0)
    #获取workbook中所有的表格
    sheets = wb.sheet_names()
    # print(sheets) 
    # 循环遍历所有sheet
    for i in range(len(sheets)):
    # skiprows=2 忽略前两行
        print("开始处理表格:{}.".format(sheets[i]))
        com_res = pd.read_excel(file, sheet_name=sheets[i], header=0,index=False, encoding='utf8')        
        hang,lie=com_res.shape
        #print(com_res.columns)
        lie_flag=com_res.columns.to_list()
        hang_flag=com_res.index.to_list()        
        ##先把每个的所有的回车都替换掉
        # wash_the_excel(com_res,hang_flag,lie_flag)
        for j in range(hang):           
                ##开始读取每一个人
            ##我日这里也有坑   
            if(j%100==0):
                print("has finished users："+str(j))
            temp_name=str(com_res.iloc[j][1]).strip()
            if(match_name(temp_name)==False):
                print("{}无效！".format(com_res.iloc[j][1]))
#                os.system("pause")
                continue
            
            schoolfellow=full_fill_base_datasingleline(com_res.iloc[j])
            schoolfellow.last_update_time=update_time
            schoolfellow.fulfill_location()
            base_data.append(schoolfellow)
            all_school_fellownames.append(schoolfellow.name)
            all_id.append(schoolfellow.stu_number)
            #print(schoolfellow.name,schoolfellow.teacher)
        print("处理表格:{}完成.".format(sheets[i]))
    wb.release_resources()
    del wb
    return all_school_fellownames,all_id
  

def  read_base_plus_file(plus1,plus2,base_data,all_names,all_stuid,same_database,FALG1,FLAG2):
    if(FALG1=="True"):
        try:
            data1=pd.read_excel(plus1, header=0,index=False, encoding='utf8') 
        except:
            print("找不到文件:{},请检查".format(plus1))
            time.sleep(5)
            os._exit(0)
        hang,lie=data1.shape    
        lie_flag=data1.columns.to_list()
        hang_flag=data1.index.to_list()
        ##先替换掉
        wash_the_excel(data1,hang_flag,lie_flag)        
#    for i in range(len(lie_flag)):
#        print(lie_flag[i])
#    print(data1.columns)
        print("基础数据库补充：{} 开始整理".format(plus1))
    #os.system("pause") 
        for i in range(hang):
            temp_name=data1.iloc[i][1]
            temp_time=data1.loc[hang_flag[i]]['填报时间']
            temp_name=str(temp_name).strip()
            if(match_name(temp_name)==False):
                print("{} :该姓名无效！".format(temp_name))
                continue
                
            if(check_valid(temp_name)==False):
                continue
#        print(temp_name)
            temp_time_col=get_time_col_heng_excel(temp_time)
            temp_stuid=data1.iloc[i][2]
            temp_school=data1.iloc[i][5]
            if(check_valid(temp_stuid)==True and temp_stuid in all_stuid):
                index=all_stuid.index(temp_stuid)
#            print(temp_name)
#            print("上次的时间是{}".format(base_data[index].last_update_time))
                old_time_col=get_time_col_heng_excel(base_data[index].last_update_time)            
                if(temp_time_col>old_time_col):
                ##说明需要更新
                    print("用户：{}更新，时间由{}变为{}。".format(temp_name,base_data[index].last_update_time,temp_time))
                    base_data[index].last_update_time=temp_time
                    base_data[index].plus_self_resume()
                    base_data[index].updata_base_plus1(data1.iloc[i])
                
                else:
                    base_data[index].update_resume_out(data1.iloc[i],temp_time)             
                
            else:
                flag,index=check_name_and_id(temp_name,temp_school,base_data)
                question_people=people()
                question_people.updata_base_plus1(data1.iloc[i])
            ##再加上上面找到的东西
                question_people.name=temp_name
                question_people.stu_number=temp_stuid
                question_people.scool=temp_school
                question_people.last_update_time=temp_time
                if(flag==True):
                ##说明存在疑似的情况，需要补充到疑似数据库中   
                    print("用户：{} 列为疑似对象，放到疑似数据库中，工作单位为：{}。".format(temp_name,question_people.company))
                    same_database.append(question_people)
                else:
                    people.count+=1
                    question_people.number=people.count
                    base_data.append(question_people)
                    all_names.append(temp_name)
                    all_stuid.append(temp_stuid)
    
    print("基础数据库补充{}整理完成".format(plus1))
    
    if(FLAG2=="True"):
        print("基础数据库补充：{} 开始整理".format(plus2))
        plus2_update_time="2019-12-31" ##默认的base2的整理时间
        try:
            data2=pd.read_excel(plus2, header=0,index=False, encoding='utf8') 
        except:
            print("找不到文件：{},请检查。".format(plus2))
            time.sleep(5)
            os._exit(0)
        hang,lie=data2.shape    
        lie_flag=data2.columns.to_list()
        hang_flag=data2.index.to_list()
        print("基础数据库补充：{}整理完成。".format(plus2))
    ##第二个文件没有任何价值，直接放弃
    return
    
  
  
def get_infor_baseindex(flag_update,flag_index,data):
    ##输入index,返回几个特定的信息     
    name=""
    phone=""
    school=""
    stu_id=""
#    print(flag_update)
    if( "1" in flag_update):
        index=flag_update.index("1")
        name=data[flag_index[index]]
    if("22" in flag_update):
        index=flag_update.index("22")
        phone=data[flag_index[index]]
    if("8" in flag_update):
        index=flag_update.index("8")
        school=data[flag_index[index]]
    if("2" in flag_update):
        index=flag_update.index("2")
        stu_id=data[flag_index[index]]
    return name,phone,school,stu_id
def analyse_infor(identify_json,lie_flag):
    ##输入表格头，和json，返回被识别的信息    
    ##这里需要重载相关方法，应该以需求的字段为顺序放置在最外层循环里里面
    ##防止excel多个表头被视为同一个字段的情况
    flag_update=[]
    flag_index=[]   
    flag_others=[]
    others_headers=[]
    flag=False 
    flag_used=[False]*len(lie_flag)
    all_keys=list(identify_json.keys())
    # print(lie_flag)
    for i in range(len(all_keys)): 
      for j in range (len(lie_flag)): 
      # print(lie_flag[j]) 
          ##开始匹配每个列的名字
          flag=False
          for k in range(len(identify_json[all_keys[i]])):          
            if(flag_used[j]==False and identify_json[all_keys[i]][k] in lie_flag[j]and len(lie_flag[j])<Header_judge_rule):
            ##说明找到了匹配   
              # print(identify_json[all_keys[i]][k],lie_flag[j])
              flag_update.append(all_keys[i])
              flag_index.append(j)
              flag_used[j]=True
              flag=True  
              break
          if(flag==True):            
            flag=False
            break
    ##然后统计哪些没有匹配上
    for i in range(len(flag_used)):
        if(flag_used[i]==False and check_useful_header(str(lie_flag[i]))==True):
            flag_others.append(i)
            others_headers.append(lie_flag[i])
      
    print(flag_update,flag_index,flag_others,others_headers)
    # os.system("pause")
    return flag_update,flag_index,flag_others,others_headers
def read_singel_excel(file,update_time,base_data,all_namse,all_stuid,identify_json,same_database):
    ##普适性的读取一个文件，更新相关的信息，增强适应性，默认读入的是一个多工作表的 
    try:
        wb = xlrd.open_workbook(file)
    except:
        print("找不到文件{},请检查".format(file))
        time.sleep(5)
        os._exit(0)
    #获取workbook中所有的表格
    print("处理表格{}".format(file))
    sheets = wb.sheet_names()
    # print(sheets) 
    # 循环遍历所有sheet
    for i in range(len(sheets)):   
        print("开始处理sheet：{},标记时间为：{}。".format(sheets[i],update_time))
        data = pd.read_excel(file, sheet_name=sheets[i], header=0,index=False, encoding='utf8')        
        hang,lie=data.shape    
        lie_flag=data.columns.to_list()
        hang_flag=data.index.to_list()
        wash_the_excel(data,hang_flag,lie_flag)
        flag_update=[]  ##标记这个表格拥有什么字段
        flag_index=[] ##标记字段对应的原表格的位置
        flag_others=[]##标记哪些字段放到“其他”中
        flag_others_headers=[] ##储存具体的“其他”信息的表头是什么
        flag_update,flag_index,flag_others,flag_others_headers=analyse_infor(identify_json,lie_flag)
        if(len(flag_update)==0):
              ##说明该问卷没有价值，直接下一个
              continue
        
        for j in range(hang):           
                ##开始读取每一个人 
              name,phone,school,stu_id=get_infor_baseindex(flag_update,flag_index,data.iloc[j])
              supplement_information=get_others_information(data.iloc[j],flag_others,flag_others_headers)
#              print(name,phone,school,stu_id)   
              name=str(name).strip()
              if(name==""):
                  continue
              if(match_name(name)==False):
                  print("{}：该姓名无效！".format(name))
                  continue
              if( name in all_namse):
                  flag,index=check_name_and_phone(name,phone,base_data)
                  if(flag==True):##说明是同一个人
                      base_data[index].inrich_others_inforamtion(supplement_information)
                      print("校友：{}发生重复，更新简历信息。".format(name))
                      if(compare_date(base_data[index].last_update_time,update_time)>0): ##说明是旧的信息
                          base_data[index].update_resume_baseindex(flag_update,flag_index,data.iloc[j],update_time)
                      else:
                          base_data[index].plus_self_resume()
                          base_data[index].update_base_index(flag_update,flag_index,data.iloc[j],update_time)
                  else:
                      ##下面判断学院的问题
                      flag,index=check_name_and_id(name,school,base_data)
                      school_fellow =people(name)
                      school_fellow.inrich_others_inforamtion(supplement_information)
                      school_fellow.update_base_index(flag_update,flag_index,data.iloc[j],update_time)
                      if(flag==True):
                          ##说明进入疑似数据库
                          print("校友：{}放置到疑似数据库。".format(name))
                          same_database.append(school_fellow)
                      else:
                          school_fellow.number=people.count
                          people.count+=1
                          base_data.append(school_fellow)
                          all_namse.append(name)
                          all_stuid.append(stu_id)
              else:
                  school_fellow =people(name)
                  school_fellow.update_base_index(flag_update,flag_index,data.iloc[j],update_time)
                  school_fellow.others_information=supplement_information
#                  print(flag_update,flag_index)
#                  print("用户{}的手机号为：{}".format(name,school_fellow.phone))
                  school_fellow.number=people.count
                  people.count+=1
                  base_data.append(school_fellow)
                  all_namse.append(name)
                  all_stuid.append(stu_id)
              ##处理完一个人的信息之后，进行其他工作
              
        print("处理表格：{},工作表：{}完成".format(file,sheets[i]))
    print("处理表格{}完成".format(file))
    wb.release_resources()
    del wb
    
    return                  
          
##根据标志，从单条信息中读取出“其他”的信息，返回字典
def get_others_information(data,flag_others,headers):
    save={}
    if(len(flag_others)!=len(headers)):
        print("其他信息的表头字段数目不匹配，请检查")
        os.system("pause")
    falg=True
    for i in range(len(flag_others)):
        falg=True
        for unaued in unvalid_str:
            if unaued in str(data[flag_others[i]]):
              falg=False
              break
        if(len(str(data[flag_others[i]]))>TWO_much_header_judge):
            falg=False
        if(falg==True):
            save[headers[i]]=str(data[flag_others[i]])
    return save
        
    
          
          
          
          
          
          
