#!/usr/bin/env python3
"""앉아가자 - 버스 한적한 시간대 추천 웹서비스"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
from pathlib import Path
from datetime import datetime
from seoul_api import get_bus_arrival_info

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.serve_file('templates/index.html', 'text/html')
        elif self.path.startswith('/static/'):
            file_path = self.path[1:]  # Remove leading /
            if file_path.endswith('.css'):
                self.serve_file(file_path, 'text/css')
            elif file_path.endswith('.js'):
                self.serve_file(file_path, 'application/javascript')
            else:
                self.send_error(404)
        elif self.path == '/api/bus':
            self.serve_json(get_bus_arrival_info())
        elif self.path == '/api/weekday':
            self.serve_json(self.get_weekday_info())
        else:
            self.send_error(404)
    
    def serve_file(self, file_path, content_type):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-type", f"{content_type}; charset=utf-8")
            self.end_headers()
            self.wfile.write(content.encode())
        except FileNotFoundError:
            self.send_error(404)
    
    def serve_json(self, data):
        self.send_response(200)
        self.send_header("Content-type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
    
    def get_weekday_info(self):
        now = datetime.now()
        weekday = now.weekday()
        is_weekend = weekday >= 5
        
        return {
            "current_day": ['월', '화', '수', '목', '금', '토', '일'][weekday],
            "is_weekend": is_weekend,
            "recommendation": "주말은 평일보다 30% 한적합니다" if is_weekend else "평일 출근시간 피하세요"
        }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    print(f"서버 시작: http://0.0.0.0:{port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
