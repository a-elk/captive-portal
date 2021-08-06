#!/usr/bin/python3
from http.server import BaseHTTPRequestHandler,HTTPServer
import logging,urllib.request,re,subprocess
import urllib.parse as urlparse


class S(BaseHTTPRequestHandler):
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
    def do_GET(self):
        logging.info("GETrequest,\nPath:%s\nHeaders:\n%s\n",str(self.path),str(self.headers))
        self._set_response()
        self.wfile.write("<form action=\"/\" method=\"post\">    <div class=\"imgcontainer\">        <img src=\"img_avatar2.png\" alt=\"Avatar\" class=\"avatar\">    </div>    <div class=\"container\">          <label for=\"uname\"><b>Username</b></label>        <input type=\"text\" placeholder=\"Enter Username\" name=\"uname\" required>        <label for=\"psw\"><b>Password</b></label>        <input type=\"password\" placeholder=\"Enter Password\" name=\"psw\" required>        <button type=\"submit\">Login</button>          <label>            <input type=\"checkbox\" checked=\"checked\" name=\"remember\"> Remember me        </label>    </div>    <div class=\"container\" style=\"background-color:#f1f1f1\">        <button type=\"button\" class=\"cancelbtn\">Cancel</button>        <span class=\"psw\">Forgot <a href=\"#\">password?</a></span>    </div></form>".encode('utf-8'))
    def do_POST(self):
        self._set_response()
        client_ip = self.client_address[0]
        if self.rfile:
            body = dict(urlparse.parse_qs(self.rfile.read(int(self.headers['Content-Length']))))
            if len(body) != 3:
                return
            if("uname".encode() in body and "psw".encode() in body):
                username = body["uname".encode()][0].decode("utf-8")
                password = body["psw".encode()][0].decode("utf-8")
                url = "https://cas.unilim.fr"
                r = urllib.request.urlopen(url)
                data = r.read()
                general_pattern = re.compile("name=\"token\" value=\"[0-9]*_[0-9]*\" />")
                result = general_pattern.search(data.decode("utf8"))
                result = result.group(0)
                token_pattern = re.compile("[0-9]*_[0-9]*")
                token = token_pattern.search(result).group(0)
                cookieProcessor = urllib.request.HTTPCookieProcessor()
                opener = urllib.request.build_opener(cookieProcessor)
                data = urllib.parse.urlencode({"user":username,"password":password,"token":token})
                request = urllib.request.Request("https://cas.unilim.fr",bytes(data,encoding="ascii"))
                response = opener.open(request)
                cookies = [c for c in cookieProcessor.cookiejar if c.name =='lemonldap']
                if(len(cookies) > 0):
                    subprocess.check_output("iptables -t nat -I PREROUTING -p tcp --dport 80 -i openvswitch -s " + client_ip+"  -j ACCEPT",stderr=subprocess.STDOUT,shell=True)
                    subprocess.check_output("iptables -t nat -I POSTROUTING -s " + client_ip+" -j MASQUERADE",stderr=subprocess.STDOUT,shell=True)
                    subprocess.check_output("iptables -I FORWARD -i openvswitch -s "+ client_ip+" -p tcp -m multiport --dport 80,443 -j ACCEPT",stderr=subprocess.STDOUT,shell=True)
                    self.wfile.write("your are authenticated!".encode('utf-8'))
                else:
                    self.wfile.write("Try again :(".encode('utf-8'))







                
def run(server_class=HTTPServer,handler_class=S,port=8080):
    logging.basicConfig(level=logging.INFO)
    server_address=('',port)
    httpd=server_class(server_address,handler_class)
    logging.info('Startinghttpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        passhttpd.server_close()
        logging.info('Stoppinghttpd...\n')

if __name__=='__main__':
    from sys import argv 
    if len(argv)==2:
        run(port=int(argv[1]))
    else:
        run()
