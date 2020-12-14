from http.server import HTTPServer, BaseHTTPRequestHandler
import webbrowser
import mimetypes
import sys
import os
import re
import json
import auto
# from multiprocessing import Pool, Queue

class Handler(BaseHTTPRequestHandler):

    def get_path(self, path):
        base = "./"
        return base + path

    def do_POST(self):
        data = self.rfile.read(int(self.headers['content-length']))
        url = data.decode()
        if url[-1] != "/":
            url = url + "/"
        if re.match("https://twitter.com/[^/]*/status/[0-9]*/", url):
            #p = Pool(1)
            #task = p.apply_async(a.execute, args=(url,))
            #p.close()
            #p.join()
            #data = task.get()
            data = auto.execute(url)
            msg = {"code": 200, "data": data}
            self.send_response(200)
            self.send_header("content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(msg).encode())
        else:
            self.send_error(404)
            self.end_headers()

    def do_GET(self):
        print(self.get_path(self.path))
        if self.path == "/":
            path = self.get_path("/static/index.html")
        else:
            path = self.get_path(self.path)
        try:
            self.send_response(200)
            self.send_header("content-type", mimetypes.guess_type(path)[0])
            self.end_headers()
            with open(path, "rb") as f:
                self.wfile.write(f.read())
        except:
            self.send_error(404, "File not found")
        return

def run(server_class=HTTPServer, handler_class=Handler, port=8000, bind=""):
    server_address = (bind, port)
    try:
        with server_class(server_address, handler_class) as httpd:

            sa = httpd.socket.getsockname()
            host = "localhost" if sa[0] == "0.0.0.0" else sa[0]
            port = sa[1]
            url = "http://{host}:{port}/".format(host=host, port=port)
            serve_message = "Running at: "
            print(serve_message + url)
            print("注意：运行时请勿关闭本窗口。\n你可以在这里看到一些运行信息。")

            webbrowser.open_new(url)

            httpd.serve_forever()
    except KeyboardInterrupt:
        print("exiting.")
        sys.exit()

if __name__ == "__main__":
    run()