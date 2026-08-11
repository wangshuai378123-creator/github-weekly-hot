# -*- coding: utf-8 -*-
"""容错静态服务器：忽略 URL 尾部多余 * 字符，/ 跳转周报页，禁用缓存。
用法: python serve.py [端口]   (默认 8765)"""
import http.server, os, sys

VIZ = r'C:\Users\Administrator\.codex\visualizations\2026\08\10\019fedfb-b0cb-73d3-b9be-0555626c7e6a'
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8765

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=VIZ, **kw)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def translate_path(self, path):
        p = super().translate_path(path)
        if not os.path.exists(p) and path.rstrip('/').endswith('*'):
            p2 = super().translate_path(path.rstrip('*'))
            if os.path.exists(p2):
                return p2
        return p

    def do_GET(self):
        if self.path in ('/', ''):
            self.send_response(302)
            self.send_header('Location', '/github-trending.html')
            self.end_headers()
            return
        super().do_GET()

    def log_message(self, *a):
        pass

http.server.ThreadingHTTPServer.allow_reuse_address = True
srv = http.server.ThreadingHTTPServer(('127.0.0.1', PORT), Handler)
print('serving on', PORT)
srv.serve_forever()
