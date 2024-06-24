import json
import time
import sys
import requests
import argparse
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import socket
from time import strftime,gmtime
requests.packages.urllib3.disable_warnings(InsecureRequestWarning) 
class awvs_api:
   
    def __init__(self,self_host,api_key,max_scan=10,wait_time=3):
        self.max_scan=max_scan
        self.wait_time=wait_time
        self.pool_list=[]
        self.self_host=self_host
        dashbord_url = self_host+'/api/v1/me/stats' # 基本信息面板
        self.dashbord_url=dashbord_url
        add_scan_url = self_host+'/api/v1/scans' # 添加扫描url
        self.add_scan_url=add_scan_url
        self.api_key=api_key
        self.total_target_url = self.self_host+'/api/v1/targets' 
        
    def get_scans_num(self,url, headers):

        '''
        获取当前正在扫描的目标数
        scans_running_count 正在扫描的个数
        scans_conducted_count 扫完的个数
        targets_count 总个数
        '''

        r = requests.get(url=url, headers=headers, verify=False).text
        my_dict = json.loads(r)
        return int(my_dict['scans_running_count'])


    def get_target(self,target_file): 
        '''
        从本地获取url
        '''
        try:
            with open(target_file, "r", encoding='utf-8') as f:
                content = f.read().splitlines()
                content = list(set(content))
            return content
        except Exception as e:
            print("\n未找到文件！\n")
            sys.exit(0)


    def add_targets(self,url_list, headers, total_target_url,zican_name):
        '''
        添加目标
        '''
        count = 1
        target_id = []

        r = requests.get(url = total_target_url, headers = headers, verify = False).text
        print(r)        
         
        for i in url_list:
            data = {
                "address" : str(i),
                "description" : zican_name,
                "criticality" : "20"
            }
            r = requests.post(url = total_target_url, headers = headers, verify = False, data = json.dumps(data)).text
            my_dict = json.loads(r)
            target_id.append(my_dict["target_id"])
            count += 1
            print(my_dict)
        #print('\n本次添加了' + str(count-1) + '个目标\n')
        return target_id


    def add_scans(self,add_scan_url, headers, total_target_url, count, target_id,max_num=10,sleep_num=60):
        '''
        添加扫描目标
        '''
        count = count
        for i in target_id: # 速度设置
            url = self.self_host+'/api/v1/targets/' + str(i) + '/configuration'
            data = {
                    "scan_speed":"moderate"
                }
            r = requests.patch(url = url, data = json.dumps(data), headers = headers, verify = False)
            scans_num = self.get_scans_num(self.dashbord_url, headers) # 获取当前扫描数
            print("scans_num:"+scans_num)            
            while int(scans_num) >= int(max_num):
                print('\n当前扫描数已超过最大设定值，等待' + str(sleep_num) + '秒后再次扫描。\n')
                time.sleep(int(sleep_num))
                scans_num = self.get_scans_num(self.dashbord_url, headers)
           
            data = {
                    "target_id": str(i),
                    "profile_id": "11111111-1111-1111-1111-111111111119",
                    "schedule": {
                                    "disable":False,
                                    "start_date":None,
                                    "time_sensitive":False
                            }
                }
            r = requests.post(url = add_scan_url, data = json.dumps(data), headers = headers, verify = False).text
            count += 1
            
            print('添加第' + str(count) + '个目标扫描。\n')
            time.sleep(1)
            if count % int(max_num) == 0:
                print('检查扫描数中，等待十秒。。\n')
                time.sleep(10)
        print('\n添加结束！\n')
                
    def im_add_scans(self,add_scan_url, headers, total_target_url, count, target_id,max_num=10,sleep_num=60):
        '''
        添加扫描目标
        '''
        for i in target_id: # 速度设置
            
      
            
           
            data = {
                    "target_id": str(i),
                    "profile_id": "11111111-1111-1111-1111-111111111119",
                    "schedule": {
                                    "disable":False,
                                    "start_date":None,
                                    "time_sensitive":False
                            }
                }
            r = requests.post(url = add_scan_url, data = json.dumps(data), headers = headers, verify = False).text
            print("-------------im_add_scans-------------------------")
            print(r)
            print("-------------im_add_scans-------------------------")
            #print('添加第' + str(count) + '个目标扫描。\n')
            time.sleep(1)
    
    def del_tasks(self):
        aheaders = {
            'X-Auth': self.api_key,
            'Content-type': 'application/json'
        }
        try:
            # 获取所有目标信息
            
            delreq = requests.get(url=self.self_host + "/api/v1/targets",
                                  headers=aheaders,
                                  timeout=30,
                                  verify=False)
        except Exception as e:
            print(self.self_host + "/api/v1/targets", e)
        if delreq and delreq.status_code == 200:
            now_targets = delreq.json()
            if now_targets['pagination']['count'] == 0:
                return True
                #print("已经全部清除")
            else:
                for tid in range(now_targets['pagination']['count']):
                    targets_id =""
                    try:
                        targets_id = now_targets['targets'][tid]['target_id']
                        del_target = requests.delete(url=self.self_host + "/api/v1/targets/" + targets_id,
                                                     headers=aheaders,
                                                     timeout=30,
                                                     verify=False)
                        if del_target and del_target.status_code == 204:
                            pass
                    except Exception as e:
                        #print("for tid in range(now_targets['pagination']['count'])")
                        pass
                
                if self.del_tasks():
                    print("self.del_tasks()")
                    return True
                else:
                    return False
                    
                    

    def message_push(self):
        try:
            print("hree")
            headers = {
            'X-Auth': self.api_key,
            'Content-type': 'application/json'
            }
            get_target_url=self.self_host+'/api/v1/vulnerability_types?l=100&q=status:open;severity:3;'
            r = requests.get(get_target_url, headers=headers, timeout=30, verify=False)
            result = json.loads(r.content.decode())
            #print(result)
            init_high_count = 0
            current_date = str(strftime("%Y-%m-%d %H:%M:%S", gmtime()))
            message_push=str(socket.gethostname())+'\n'+current_date+'\n'
            for xxxx in result['vulnerability_types']:
                message_push = message_push+'漏洞: ' + xxxx['name'] + '数量: '+str(xxxx['count'])+'\n'
            
            return message_push
        except Exception as e:
                        print(e)
                
    def im_add_scans_out(self, target_list):
        '''
        添加扫描目标
        '''
        headers = {
        'X-Auth': self.api_key,
        'Content-type': 'application/json'
        }
        target_id = self.add_targets(target_list, headers, self.total_target_url,"im_add_scans_api")
        for i in target_id: # 速度设置
            url = self.self_host+'/api/v1/targets/' + str(i) + '/configuration'
            data = {
                    "scan_speed":"moderate"
                }
            r = requests.patch(url = url, data = json.dumps(data), headers = headers, verify = False)
            scans_num = self.get_scans_num(self.dashbord_url, headers) # 获取当前扫描数
            
           
            data = {
                    "target_id": str(i),
                    "profile_id": "11111111-1111-1111-1111-111111111119",
                    "schedule": {
                                    "disable":False,
                                    "start_date":None,
                                    "time_sensitive":False
                            }
                }
            r = requests.post(url = self.add_scan_url, data = json.dumps(data), headers = headers, verify = False).text
           
            
            #print('添加第' + str(count) + '个目标扫描。\n')
            time.sleep(1)  
        
    def begin(self,t_list,z_name,max_num=10,sleep_num=60):
        headers = {
        'X-Auth': self.api_key,
        'Content-type': 'application/json'
        }
        total_target_url = self.self_host+'/api/v1/targets' # 获取所有目标信息
        dashbord_url = self.self_host+'/api/v1/me/stats' # 基本信息面板
        add_scan_url = self.self_host+'/api/v1/scans' # 添加扫描url
        count = 0
        target_list = t_list # 获取url列表
        target_id = self.add_targets(target_list, headers, total_target_url,z_name)
        self.add_scans(add_scan_url, headers, total_target_url, count, target_id,max_num,sleep_num)
        
    def add_pool(self,url):
        if not hasattr(self, 'pool_list'):
            self.pool_list = []
        if isinstance(url, str):
            self.pool_list.append(url)
        elif isinstance(url, list):
            self.pool_list.extend(url)
        else:
            pass
        self.pool_list = list(set(self.pool_list))
        
    def get_pool(self):
        return self.pool_list
        
    def get_list_num(self):
        return len(self.pool_list)
    def clean_all(self):
        self.pool_list.clear()
        return  True
    def pool_scan(self):
    
        #url = self.self_host+'/api/v1/targets/' + str(i) + '/configuration'
        headers = {
            'X-Auth': self.api_key,
            'Content-type': 'application/json'
            }
        scans_num = self.get_scans_num(self.dashbord_url, headers) # 获取当前扫描数
            
        while True:
            try:
                scans_num = self.get_scans_num(self.dashbord_url, headers)
                if (int(scans_num) <= int(self.max_scan)) and len(self.pool_list)>0:   
                    next_scan=self.pool_list.pop(0)
                    target_id = self.add_targets([next_scan], headers, self.total_target_url,f"api_pool_{int(time.time())}")
                    self.im_add_scans(self.add_scan_url, headers, self.total_target_url, 0, target_id,self.max_scan,self.wait_time)
                    print(f"add {next_scan}!")
                print(f"now scan {scans_num}")
                time.sleep(self.wait_time)    
            except Exception as error:
                time.sleep(self.wait_time) 
                print("An exception occurred:", error) 


