from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests


FORWORD_PORT = 28080
ECHO_PORT = 38080
BURP_PORT = 8080


class ForwardRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('content-length', 0))

        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
        data = self.rfile.read(content_length)
        if str(self.path) == "/REQUEST":
            r = requests.request('REQUEST', 'http://127.0.0.1:{}/'.format(ECHO_PORT),
                                 proxies={'http': 'http://127.0.0.1:{}'.format(BURP_PORT)},
                                 data=data)
            new_data = r.text
            self.wfile.write(new_data.encode('utf8'))
        else:
            try:
                r = requests.request('RESPONSE', 'http://127.0.0.1:{}/'.format(ECHO_PORT),
                                     proxies={'http': 'http://127.0.0.1:{}'.format(BURP_PORT)},
                                     data=data)
                new_data = r.text
                self.wfile.write(new_data.encode('utf8'))
            except:
                self.wfile.write(data)

class RequestHandler(BaseHTTPRequestHandler):
    def do_REQUEST(self):
        content_length = int(self.headers.get('content-length', 0))
        self.send_response(200)
        self.end_headers()
        self.wfile.write(self.rfile.read(content_length))

    do_RESPONSE = do_REQUEST

def echo_server_thread():
    print('>开始监听镜像服务器,端口:{}'.format(ECHO_PORT))
    server = HTTPServer(('0.0.0.0', ECHO_PORT), RequestHandler)
    server.serve_forever()

def echo_forward_server_thread():
    print('>开始监听转发服务器,端口:{}'.format(FORWORD_PORT))
    server = HTTPServer(('0.0.0.0', FORWORD_PORT), ForwardRequestHandler)
    server.serve_forever()

def get_payload():
    flag = True
    while(flag):
        print("============================================================================================")
        param_name = input(">请输入要forward到Burp的参数名(输入$end结束):")
        if param_name == "$end":
            break
        data_type = input(">请输入" + param_name +  "的数据类型(json/string):")
        request_type = input(">请输入请求标识(例如:REQUEST/RESPONSE):")
        if data_type == "json":
            base_payload = 'var xhr = new XMLHttpRequest();xhr.open(\"post\", \"http://127.0.0.1:' + str(FORWORD_PORT) + '/' + request_type + '\", false);xhr.send(JSON.stringify(' + param_name + '));' + param_name + '=JSON.parse(xhr.responseText);'
        elif data_type == "string":
            base_payload = 'var xhr = new XMLHttpRequest();xhr.open(\"post\", \"http://127.0.0.1:' + str(FORWORD_PORT) + '/' + request_type + '\", false);xhr.send(' + param_name + ');' + param_name + '=xhr.responseText;'
        else:
            print(">您的数据类型输入有误")
            break
        print('payload生成完毕:\n' + base_payload)
        if param_name == "$end":
            flag = False
    print("============================================================================================")


def banner():
    print('''
   _____   ______             ___                                                  __  
   |_   _|.' ____ \          .' ..]                                                |  ] 
     | |  | (___ \_|______  _| |_   .--.   _ .--.  _   _   __  ,--.   _ .--.   .--.| |  
 _   | |   _.____`.|______|'-| |-'/ .'`\ \[ `/'`\][ \ [ \ [  ]`'_\ : [ `/'`\]/ /'`\' |  
| |__' |  | \____) |         | |  | \__. | | |     \ \/\ \/ / // | |, | |    | \__/  |  
`.____.'   \______.'        [___]  '.__.' [___]     \__/\__/  \'-;__/[___]    '.__.;__] 

                                                                    Version 2.0 By Gr33k     
============================================================================================
提示:
    本工具生成payload仅限(string/json)类型参数,若参数为其他类型请自行修改payload                                        
    ''')



if __name__ == '__main__':
    banner()
    get_payload()
    t1 = Thread(target=echo_forward_server_thread)
    t = Thread(target=echo_server_thread)
    t.daemon = True
    t.start()
    t1.daemon = True
    t1.start()
    print(">准备就绪 请启动Burp,端口:8080")
    for t in [t, t1]:
        t.join()


