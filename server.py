#!/usr/bin/env python3
"""앉아가자 - 버스 한적한 시간대 추천 웹서비스"""
from http.server import HTTPServer, SimpleHTTPRequestHandler

HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>앉아가자 - 버스 한적한 시간대</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background: #f9fafb; }
        h1 { color: #2563eb; margin-bottom: 5px; }
        .subtitle { color: #6b7280; margin-bottom: 20px; }
        .card { background: white; padding: 20px; border-radius: 12px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
        .recommend { background: linear-gradient(135deg, #dcfce7, #bbf7d0); padding: 20px; border-radius: 12px; margin-bottom: 20px; }
        .recommend strong { font-size: 1.2em; }
        canvas { max-height: 250px; }
        .footer { color: #9ca3af; font-size: 12px; text-align: center; margin-top: 30px; }
    </style>
</head>
<body>
    <h1>🚌 앉아가자</h1>
    <p class="subtitle">421번 보광동주민센터 → 매봉역</p>
    
    <div class="recommend">
        <strong>⭐ 출근: 06시대</strong> (08시 대비 1/9)<br>
        <strong>⭐ 퇴근: 20시 이후</strong> (18시 대비 60%)
    </div>
    
    <div class="card">
        <h3>출근 시간대 승차 인원</h3>
        <canvas id="morningChart"></canvas>
    </div>
    
    <div class="card">
        <h3>퇴근 시간대 하차 인원</h3>
        <canvas id="eveningChart"></canvas>
    </div>
    
    <p class="footer">데이터: 서울시 버스 승하차 정보 (2024.11)</p>
    
    <script>
        const morning = {
            labels: ['06시', '07시', '08시', '09시', '10시'],
            datasets: [{
                label: '승차',
                data: [142, 994, 1303, 1219, 1190],
                backgroundColor: ['#22c55e', '#ef4444', '#ef4444', '#ef4444', '#ef4444'],
                borderRadius: 8
            }]
        };
        const evening = {
            labels: ['17시', '18시', '19시', '20시', '21시'],
            datasets: [{
                label: '하차',
                data: [640, 798, 698, 490, 507],
                backgroundColor: ['#ef4444', '#ef4444', '#ef4444', '#22c55e', '#22c55e'],
                borderRadius: 8
            }]
        };
        const opts = { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true } } };
        new Chart(document.getElementById('morningChart'), { type: 'bar', data: morning, options: opts });
        new Chart(document.getElementById('eveningChart'), { type: 'bar', data: evening, options: opts });
    </script>
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
