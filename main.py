# -*- coding: utf-8 -*-
"""
Created on Thu Apr  9 21:57:26 2020

@author: 王志
"""
import json
import time
import sys
import os
sys.path.append("help_database.py")
import help_database
import configparser

'''首先定义几个要有的变量
   关于重复数据的确定，学号一样一定认为是完全同一个人，直接进行覆盖或更新
   在没有学号的情况下，如果姓名和学院一样，且都存在，认为是疑似，放到重复库里
   其他情况全部认为不一样
   
   在读取其他问卷信息中，采取的策略是识别姓名和手机，均一样视为一个人
   如果没有手机或者不一样，读取学院，一样的话认为是近似，放到专门的重复数据库里，不一样的话认为是新的人
   
   除了people规定的字段，其他在问卷中遇到的信息，会放到“其他”信息栏中
'''

# Base_file="B_resuult.xlsx"  ##基础数据
# Base_update_time="2019-12-15" ##基础数据的时间戳
# Base_plus1="B_plus1.xlsx"
# Base_plus2="B_plus2.xlsx"
# Config_file="config_test.json"    ##配置文件，保存时间和要读的文件名
# Identify_file="identify.json"             ##配置文件，说明读取字段的时候识别情况
# Database_file_path="D:\\校友会校友资料\\筹200220\\"  ##所有的需要读取的文件位置


# OUT_path=""   ##输出结果文件的路径
# OUT_resume_path=""
# OUT_Same_database_file="Same_database"  ##疑似数据库的结构
# OUT_total_result_file="All_result"   ##输出的文件结果

# IF_read_plus1=True
# IF_read_plus2=True
    
 #版权相关信息
Copy_right='''All rights reserved from wangzhi 2020.4.9 from PKU@SAM
update data:2020.9.27
version number :2.0''' 


##程序只需要感知一个路径，就是user_config的路径，其他都写在里面   
User_config_path="H:\\my_code\\some_programs\\database_xiaoyou\\整理数据库\\"   
def main():   
    print("{0:-^30}".format(Copy_right))
    print("-----------------------------------------------------")
    print("\n")     
    
  
    
    
   
    #首先读取目录下面的配置文件  
    ##包括基础命令，和基本文件信息
    cf=configparser.ConfigParser()
    try:        
        cf.read(User_config_path+"user_config.ini",encoding='utf-8')
        
        base_file=cf.get("file_name","Base_file")
        base_plus1=cf.get("file_name","Base_plus1")
        base_plus2=cf.get("file_name","Base_plus2")
        ##配置要读取什么文件
        Config_file=cf.get("file_name","Config_file")
        Identify_file=cf.get("file_name","Identify_file")
        print("文件名字段读取完毕！")        
        
        Database_file_path=cf.get("path","Database_file_path")
        OUT_path=cf.get("path","OUT_path")
        OUT_resume_path=cf.get("path","OUT_resume_path")
        Other_config_path=cf.get("path","Other_config_path")
        print("路径信息读取完毕！")        
        
        base_update_time=cf.get("base_time","Base_update_time")
        OUT_Same_database_file=cf.get("out_put","OUT_Same_database_file")
        OUT_total_result_file=cf.get("out_put","OUT_total_result_file")  
        ##其他的由于特殊业务需求的输出文件
        OUT_selected=cf.get("out_put","OUT_selected")
        print("输出信息读取完毕！")
        
        if_read_plus1=cf.get("command","if_read_plus1")
        if_read_plus2=cf.get("command","if_read_plus2")
        print("命令信息读取完毕！")
        
        print("用户配置信息读取完毕！")        
    except Exception as e:        
        print("配置文件:user_config.ini读取异常，错误:{}请检查后重试（程序5s后退出）",format(e))        
        time.sleep(5)
        sys.exit()
    load_json=[]
    try:
        with open(Other_config_path+Config_file,"r",encoding="utf-8") as f:
            load_json=json.load(f)
            print("加载文件：{}完成...".format(Config_file)) 
            f.close()
    except Exception as e:           
        print("配置文件:{} 读取异常，,错误{}请检查后重试（程序2s后退出）".format(Config_file,e))
        time.sleep(2)
        os._exit(0)
        
    ##读取基础的数据信息，包括三个部分
    base_data=[]  #储存全部基础信息
    same_database=[]   ##储存全部相同库信息
#    print(load_json.keys())    
#    print(type(load_json))
    all_people_name=[]  ##所有人的名字
    all_stu_id=[] ##所有人的学号
    
    ##首先读取base和plus1和plus2文件
    all_people_name,all_stu_id=help_database.read_base_excel(base_file,base_data,base_update_time)
    help_database.read_base_plus_file(base_plus1,base_plus2,base_data,all_people_name,all_stu_id,same_database,if_read_plus1,if_read_plus2)
    
#     ##读取其他文件的信息，需要建立好重复的单独库封装
    identi_json=[]
    try:
        with open(Other_config_path+Identify_file,"r",encoding="utf-8") as f:
            identi_json=json.load(f)
            print("加载文件完成...")   
            f.close()
    except Exception as e:           
        print("配置文件:{}读取异常,错误{}，请检查后重试（程序2s后退出）".format(Identify_file,e))
        time.sleep(2)
        os._exit(0)
    for i in load_json.keys():
        help_database.read_singel_excel(Database_file_path+i,load_json[i],base_data,all_people_name,all_stu_id,identi_json,same_database)
#        print(load_json[i])
#    os.system("pause")
    
    
    ##输出疑似数据库信息
    f=open(OUT_path+OUT_Same_database_file,"w",encoding='utf-8')
    for i in identi_json.keys():         
        f.write(identi_json[i][0])
        f.write("\t")
    for head in help_database.new_headers:
        f.write(head)
        f.write("\t")
    f.write("\n")
    for i in range(len(same_database)):
        if(help_database.check_valid(same_database[i].name)==True):
            same_database[i].out_print(f)
            same_database[i].out_print_plus(f)
            f.write("\n")
        if(same_database[i].resume_data_num>0):
            same_database[i].save_resume(OUT_resume_path)           
    f.close()
    print("疑似数据库输出完毕{}".format(OUT_Same_database_file))
    
    ##输出全部信息
    f=open(OUT_path+OUT_total_result_file,"w",encoding='utf-8')
    for i in identi_json.keys():  
        f.write(identi_json[i][0])
        f.write("\t")
    for head in help_database.new_headers:
        f.write(head)
        f.write("\t")
    f.write("\n")
    for i in range(len(base_data)):
        if(help_database.check_valid(base_data[i].name)==True):
            base_data[i].out_print(f)
            base_data[i].out_print_plus(f)
            f.write("\n")
        if(base_data[i].resume_data_num>0):
            base_data[i].save_resume(OUT_resume_path)
        
    f.close()
    print("数据库结果整理完毕{}".format(OUT_total_result_file))
    
    
    ##其他的业务需求
    #print_selected_database(OUT_path+OUT_selected,base_data,identi_json,help_database.new_headers,help_database.big_valley_area,"big_valley")
    
    print("所有数据整理完毕，请检查路径 {}的输出文件".format(OUT_path))


    
    
    

##其他业务，基于一种规则挑选校友信息，例如工作单位或者所在地等
##产生关于互联网公司的校友信息  
##其他业务，产生大湾区相关情
def print_selected_database(path,database,identi_json,new_headers,rule,flag):
    flag_break=False
    try:
      with open(path,"w",encoding='utf-8') as f:
        ##首先打印表头
        for i in identi_json.keys():         
          f.write(identi_json[i][0])
          f.write("\t")
        for head in new_headers:
          f.write(head)
          f.write("\t")
        f.write("\n")
        ##然后是打印具体内容
        for i in range(len(database)):
          flag_break=False
          if(flag=="network"):
              for net_com in rule:
                if(net_com in str(database[i].company)):
                  flag_break=True
                  break
              
          elif(flag=="big_valley"):
              for city in rule:
                if(city in str(database[i].city) or city in str(database[i].head_loc)):
                  flag_break=True
                  break
          elif(flag=="oversea"):
              if("国外" in str(database[i].city) or "国外" in str(database[i].head_loc)):
                flag_break=True
                break
          else:
              print("unkown the business order!please check!")
              os.system("pause")
          if(flag_break==True):
                database[i].out_print(f)
                database[i].out_print_plus(f)
                f.write("\n")   
    except Exception as e:           
        print("产生文件{}失败,{}".format(path,e))
        time.sleep(10)
        os._exit(0)
    return

  


if __name__ =='__main__':          
    main()        
    os.system("pause")
    print("all total work done!")
    
    
    