#!/usr/bin/env python3
"""앉아가자 - 버스 한적한 시간대 추천 웹서비스"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json

DATA = {
    "421": {
        "보광동주민센터": {
            6: {"on": 142, "off": 75},
            7: {"on": 994, "off": 322},
            8: {"on": 1303, "off": 697},
            9: {"on": 1219, "off": 411},
            10: {"on": 1190, "off": 354},
        }
    }
}

HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>앉아가자 - 버스 한적한 시간대</title>
    <style>
        body { font-family: -apple-system, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
        h1 { color: #2563eb; }
        .recommend { background: #dcfce7; padding: 15px; border-radius: 8px; margin: 20px 0; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 10px; text-align: center; border-bottom: 1px solid #e5e7eb; }
        .busy { background: #fee2e2; }
        .quiet { background: #dcfce7; }
    </style>
</head>
<body>
    <h1>🚌 앉아가자</h1>
    <p>421번 보광동주민센터 → 매봉역</p>
    
    <div class="recommend">
        <strong>⭐ 추천 시간: 06시대</strong><br>
        08시 대비 승차 인원 1/9 수준
    </div>
    
    <h2>시간대별 승차 인원 (2024년 11월)</h2>
    <table>
        <tr><th>시간</th><th>승차</th><th>하차</th><th>혼잡도</th></tr>
        <tr class="quiet"><td>06시</td><td>142</td><td>75</td><td>⭐ 한적</td></tr>
        <tr class="busy"><td>07시</td><td>994</td><td>322</td><td>🔴 혼잡</td></tr>
        <tr class="busy"><td>08시</td><td>1,303</td><td>697</td><td>🔴 매우 혼잡</td></tr>
        <tr class="busy"><td>09시</td><td>1,219</td><td>411</td><td>🔴 혼잡</td></tr>
        <tr class="busy"><td>10시</td><td>1,190</td><td>354</td><td>🔴 혼잡</td></tr>
    </table>
    
    <h2>퇴근 시간대 (하차 기준)</h2>
    <div class="recommend">
        <strong>⭐ 퇴근 추천: 20시 이후</strong><br>
        18시 대비 하차 인원 60% 수준
    </div>
    <table>
        <tr><th>시간</th><th>하차</th><th>혼잡도</th></tr>
        <tr class="busy"><td>17시</td><td>640</td><td>🔴 혼잡</td></tr>
        <tr class="busy"><td>18시</td><td>798</td><td>🔴 매우 혼잡</td></tr>
        <tr class="busy"><td>19시</td><td>698</td><td>🔴 혼잡</td></tr>
        <tr class="quiet"><td>20시</td><td>490</td><td>⭐ 한적</td></tr>
        <tr class="quiet"><td>21시</td><td>507</td><td>⭐ 한적</td></tr>
    </table>
    
    <p style="color:#6b7280;margin-top:30px;font-size:14px;">
        데이터: 서울시 버스노선별 정류장별 시간대별 승하차 인원 정보
    </p>
</body>
</html>
"""

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode())

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    print(f"서버 시작: http://0.0.0.0:{port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
