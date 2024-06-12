from flask import Flask, request, jsonify
import requests,threading
from awvs import awvs_api  
from oneforall import OneForAll
from io import BytesIO


app = Flask(__name__)

TELEGRAM_URL = "https://api.telegram.org/bot"
TOKEN = ""

awvs_url='https://1/'
awvs_key='11026'
awvs_scan = awvs_api(awvs_url,awvs_key)
thread = threading.Thread(target=awvs_scan.pool_scan)
thread.start()

def get_file_path(file_id):
    url = f"https://api.telegram.org/bot{TOKEN}/getFile?file_id={file_id}"
    response = requests.get(url).json()
    return response['result']['file_path']


def download_file(file_path):
    url = f"https://api.telegram.org/file/bot{TOKEN}/{file_path}"
    response = requests.get(url)
    return response.content

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()
    chat_id = req['message']['chat']['id']
    return_text="返回出错"
    if 'document' in req['message']:
        document = req['message']['document']
        file_id = document['file_id']
        file_name = document['file_name']
        file_path = get_file_path(file_id)
        file_bytes = download_file(file_path)
        cc = file_bytes.decode('utf-8').splitlines()
        return_text=document_req(chat_id,cc,file_name)
    else:
        text = req['message']['text']
        #print(text)
        return_text=handler_req(chat_id, text)
    send_message(chat_id, return_text)
    return jsonify(success=True)


def oneforall(domain):
    test = OneForAll(target=domain)
    test.dns = True
    test.brute = True
    test.req = True
    test.takeover = True
    test.alive = True
    test.run()
    results = test.datas
    #print(results)
    a=[]
    for url in results:
        #print(url['url'])  
        a.append("url:"+url['url']+"   title:"+url['title'][:30]+"   ip:"+url['ip']   )
         
    results = list(set(a))
    return results

def oneforall_scan_i(domain):
    test = OneForAll(target=domain)
    test.dns = True
    test.brute = True
    test.req = True
    test.takeover = True
    test.alive = True
    test.run()
    results = test.datas
    #print(results)
    a=[]
    for url in results:
        #print(url['url'])  
        if( url['title']!=None ) or  (url['title']!="None" ):
            a.append(url['url'])
         
    results = list(set(a))
    return results   




def oneforall_scan(url,chat_id):
    result=oneforall_scan_i(url)
    awvs_scan.add_pool(result)
    now_num=awvs_scan.get_list_num()
    text=f"{url}子域名扫描完成,扫描到{len(result)}子域名,并添加到awvs扫描队列成功 目前扫描队列有{now_num}"
    send_message(chat_id, text)
    
def only_oneforall_scan(url,chat_id):
    result=oneforall(url)
    result_string = '\n'.join(result)
    result_file = BytesIO(result_string.encode('utf-8'))
    result_file.name = f"{url}.txt" 
    send_file_to_telegram(chat_id, result_file)
    
def im_add_awvs_s(url,chat_id):
    awvs_scan.im_add_scans_out([url])
    text=f"立即{url}添加完成!请在awvs查看!"
    send_message(chat_id, text)
    
def oneforall_scan_arr(url_list,chat_id):
    for url in url_list:
        result=oneforall_scan_i(url)
        awvs_scan.add_pool(result)
        now_num=awvs_scan.get_list_num()
        
    text=f"批量子域名扫描完成,完成了{len(url)}的扫描,并添加到awvs扫描队列成功 目前扫描队列有{now_num}"
    send_message(chat_id, text)
    
def document_req(chat_id, stearm,file_name):
    command = file_name
    print("file_name:"+command)
    if command == 'plsm.txt':
        for index in stearm:
            index=index.strip("")
            awvs_scan.add_pool(index)
    now_num=awvs_scan.get_list_num()
    return f"运行批量添加文件到awvs完成,目前队列有{now_num}!"        
    
def handler_req(chat_id, text):
    parts = text.split()
    if len(parts) == 0:
        return "输入不正确"
    command = parts[0]
    if command == 'help':
        return "你现在可以使用我来进行半自动扫描! 目前的命令有  ljsm(立即扫描 将一个url地址立即添加到awvs扫描!)   zysm(子域扫描 首先爆破子域名  提取用title的子域名推送到awvs 但有队列)  lzysm(list子域名扫描 多个子域名扫描 使用,分割多个扫描 然后子域名 然后推awvs )  zym(单纯的子域名扫描  扫描完成后发个文件回来!) 如果发送了一个文件名为plsm.txt的文件 则会将文件内的每一行推送到扫描池! "
    elif command == 'sm':
        if len(parts) < 2:
            return "参数不足"
        awvs_scan.add_pool(parts[1])
        now_num=awvs_scan.get_list_num()
        return f"添加到队列成功 目前队列有{now_num}"
    elif command=="zysm":
        if len(parts) < 2:
            return "参数不足"
        now_num=awvs_scan.get_list_num()
        zym_thread = threading.Thread(target=oneforall_scan,args=(parts[1],chat_id,))
        zym_thread.start()
        return f"正在运行子域名扫描并添加awvs,完成后会回复，目前队列有{now_num}"
    elif command == 'ljsm':
        if len(parts) < 2:
            return "参数不足"
        rpym_thread = threading.Thread(target=im_add_awvs_s,args=(parts[1],chat_id,))
        rpym_thread.start()
        return f"正在运行立即添加到awvs,完成后会回复!"
    elif command == 'pljsm':
        if len(parts) < 2:
            return "参数不足"
        a=parts[1].splits(',')
        for index in  a:
            rpym_thread = threading.Thread(target=im_add_awvs_s,args=(index,chat_id,))
            rpym_thread.start()
        return f"正在运行立即添加到awvs,完成后会回复!"
    elif command == 'lzysm':
        if len(parts) < 2:
            return "参数不足"
        items = parts[1].split(',')
        pym_thread = threading.Thread(target=oneforall_scan_arr,args=(items,chat_id,))
        pym_thread.start()
        now_num=awvs_scan.get_list_num()
        return f"正在运行子域名批量域名扫描并添加awvs,完成后会回复，目前队列有{now_num}"
    elif command == 'zym':
        if len(parts) < 2:
            return "参数不足"
        onlyym_thread = threading.Thread(target=only_oneforall_scan,args=(parts[1],chat_id,))
        onlyym_thread.start()    
        return f"正在运行子域名扫描,完成后会回复文件!"
    else:
        return "当前不支持"

    
    

def send_message(chat_id, text):
    url = f"{TELEGRAM_URL}{TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text
    }
    requests.post(url, json=payload)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    chat_id = request.form.get('chat_id')
    if not chat_id:
        return jsonify({"error": "No chat_id provided"}), 400
    
    # 发送文件到 Telegram
    send_file_to_telegram(chat_id, file)
    
    return jsonify(success=True)

def send_file_to_telegram(chat_id, file):
    url = f"{TELEGRAM_URL}{TOKEN}/sendDocument"
    files = {
        'document': file, 
        'chat_id': (None, str(chat_id)),
    }
    response = requests.post(url, files=files)

if __name__ == '__main__':
    
    app.run(host="0.0.0.0",port=80)
