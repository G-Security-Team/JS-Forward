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
    server = HTTPServer(('', ECHO_PORT), RequestHandler)
    server.serve_forever()

def echo_forward_server_thread():
    print('>开始监听转发服务器,端口:{}'.format(FORWORD_PORT))
    server = HTTPServer(('', FORWORD_PORT), ForwardRequestHandler)
    server.serve_forever()


def get_payload():
    flag = True
    while(flag):
        print("============================================================================================")
        param_name = input(">请输入要forward到Burp的参数名(输入$end结束):")
        if param_name == "$end":
            break
        base_payload = '$.ajax({type:\"POST\",url:\"http://127.0.0.1:28080/REQUEST\",data:BSAEDATA,async:false,success:function(resultdata){BSAEDATA=resultdata}});'
        payload = base_payload.replace('BSAEDATA',param_name)
        print('payload生成完毕:\n' + payload)
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

                                                                    Version 1.0 By Gr33k     
============================================================================================
提示:
    本工具生成payload仅限字符串类型参数,若参数为其他类型请自行修改payload        
    本工具依靠jquery提供ajax同步请求，使用前请自行寻找js的转发点，若测试的项目没有使用jquery,推荐手动添加
    https:<script src=\"https://code.jquery.com/jquery-2.1.1.min.js\"></script> 
    http:<script src=\"http://code.jquery.com/jquery-2.1.1.min.js\"></script>    
    返回包加载进入浏览器时插入,浏览器便会将jquery加载进运行环境                                                                  
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
    print(">请启动Burp,端口:8080")
    for t in [t, t1]:
        t.join()


