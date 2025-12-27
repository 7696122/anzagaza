#!/usr/bin/env python3
"""앉아가자 - 버스 한적한 시간대 추천 웹서비스"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import urllib.parse
from seoul_api import get_bus_arrival_info, get_bus_position

HTML = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>앉아가자 - 버스 한적한 시간대</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * { box-sizing: border-box; }
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; 
            max-width: 800px; 
            margin: 0 auto; 
            padding: 16px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        h1 { 
            color: white; 
            margin-bottom: 5px; 
            text-align: center;
            font-size: 2.5em;
            text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        .subtitle { 
            color: rgba(255,255,255,0.9); 
            margin-bottom: 24px; 
            text-align: center;
            font-size: 1.1em;
        }
        .card { 
            background: white; 
            padding: 24px; 
            border-radius: 16px; 
            margin-bottom: 20px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .card h3 {
            margin-top: 0;
            color: #374151;
            font-size: 1.2em;
        }
        .recommend { 
            background: linear-gradient(135deg, #10b981, #059669); 
            color: white;
            padding: 24px; 
            border-radius: 16px; 
            margin-bottom: 24px;
            box-shadow: 0 8px 32px rgba(16, 185, 129, 0.3);
        }
        .recommend strong { 
            font-size: 1.3em; 
            display: block;
            margin-bottom: 8px;
        }
        .bus-info {
            display: grid;
            gap: 12px;
        }
        .bus-item {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 16px;
            background: #f9fafb;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .bus-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .bus-route {
            font-weight: bold;
            font-size: 1.1em;
            color: #1f2937;
        }
        .bus-direction {
            color: #6b7280;
            font-size: 0.9em;
        }
        .bus-arrival {
            margin: 8px 0;
            font-size: 1em;
        }
        button {
            background: #3b82f6;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 1em;
            transition: background 0.2s;
        }
        button:hover {
            background: #2563eb;
        }
        canvas { max-height: 300px; }
        .footer { 
            color: rgba(255,255,255,0.8); 
            font-size: 12px; 
            text-align: center; 
            margin-top: 30px; 
        }
        
        @media (max-width: 768px) {
            body { padding: 12px; }
            h1 { font-size: 2em; }
            .card { padding: 16px; }
            .recommend { padding: 16px; }
            canvas { max-height: 250px; }
        }
    </style>
</head>
<body>
    <h1>🚌 앉아가자</h1>
    <p class="subtitle">421번 보광동주민센터 → 매봉역</p>
    
    <div class="recommend">
        <strong>⭐ 출근 최적 시간: 06시대</strong>
        421번: 142명 | 400번: 233명 (실제 데이터 기준)
        <strong>⭐ 퇴근 최적 시간: 23시 또는 20시</strong>
        421번: 23시 367명, 20시 490명 | 400번: 23시 59명, 20시 160명
    </div>
    
    <div class="card">
        <h3>🚌 실시간 버스 정보</h3>
        <div id="busInfo">로딩 중...</div>
        <button onclick="refreshBus()">새로고침</button>
    </div>
    
    <div class="card">
        <h3>출근 시간대 승차 인원 (421번) - 실제 데이터</h3>
        <canvas id="morningChart421"></canvas>
    </div>
    
    <div class="card">
        <h3>출근 시간대 승차 인원 (400번) - 실제 데이터</h3>
        <canvas id="morningChart400"></canvas>
    </div>
    
    <div class="card">
        <h3>퇴근 시간대 하차 인원 (421번) - 실제 데이터</h3>
        <canvas id="eveningChart421"></canvas>
    </div>
    
    <div class="card">
        <h3>퇴근 시간대 하차 인원 (400번) - 실제 데이터</h3>
        <canvas id="eveningChart400"></canvas>
    </div>
    
    <p class="footer">데이터: 서울시 버스 승하차 정보 (2024.11)</p>
    
    <script>
        // 실제 서울시 OpenAPI 데이터 (2024년 11월)
        const morning421 = {
            labels: ['06시', '07시', '08시', '09시', '10시'],
            datasets: [{
                label: '421번 승차',
                data: [142, 994, 1303, 1219, 1190],
                backgroundColor: ['#22c55e', '#ef4444', '#ef4444', '#ef4444', '#ef4444'],
                borderRadius: 8
            }]
        };
        const morning400 = {
            labels: ['04시', '05시', '06시', '07시', '08시', '09시', '10시'],
            datasets: [{
                label: '400번 승차',
                data: [40, 107, 233, 389, 401, 386, 403],
                backgroundColor: function(context) {
                    const value = context.parsed.y;
                    if (value < 150) return '#22c55e';
                    if (value < 300) return '#eab308';
                    return '#ef4444';
                },
                borderRadius: 8
            }]
        };
        const evening421 = {
            labels: ['17시', '18시', '19시', '20시', '21시', '22시', '23시'],
            datasets: [{
                label: '421번 하차',
                data: [640, 798, 698, 490, 507, 500, 367],
                backgroundColor: function(context) {
                    const value = context.parsed.y;
                    if (value < 400) return '#22c55e';
                    if (value < 600) return '#eab308';
                    return '#ef4444';
                },
                borderRadius: 8
            }]
        };
        const evening400 = {
            labels: ['17시', '18시', '19시', '20시', '21시', '22시', '23시'],
            datasets: [{
                label: '400번 하차',
                data: [191, 226, 250, 160, 174, 134, 59],
                backgroundColor: function(context) {
                    const value = context.parsed.y;
                    if (value < 150) return '#22c55e';
                    if (value < 200) return '#eab308';
                    return '#ef4444';
                },
                borderRadius: 8
            }]
        };
        const opts = { 
            responsive: true, 
            plugins: { legend: { display: false } }, 
            scales: { 
                y: { beginAtZero: true }
            }
        };
        new Chart(document.getElementById('morningChart421'), { type: 'bar', data: morning421, options: opts });
        new Chart(document.getElementById('morningChart400'), { type: 'bar', data: morning400, options: opts });
        new Chart(document.getElementById('eveningChart421'), { type: 'bar', data: evening421, options: opts });
        new Chart(document.getElementById('eveningChart400'), { type: 'bar', data: evening400, options: opts });
        
        // 실시간 버스 정보
        async function refreshBus() {
            document.getElementById('busInfo').innerHTML = '로딩 중...';
            try {
                const response = await fetch('/api/bus');
                const data = await response.json();
                document.getElementById('busInfo').innerHTML = formatBusInfo(data);
            } catch (e) {
                document.getElementById('busInfo').innerHTML = '오류: ' + e.message;
            }
        }
        
        function formatBusInfo(data) {
            if (data.error) return `<div class="bus-item">❌ ${data.error}</div>`;
            if (!data.buses) return '<div class="bus-item">📍 버스 정보 없음</div>';
            
            let html = '<div class="bus-info">';
            data.buses.forEach(bus => {
                const congestionIcon = ['🟢', '🟡', '🟠', '🔴', '⚫'][bus.congestion1] || '❓';
                const congestionIcon2 = ['🟢', '🟡', '🟠', '🔴', '⚫'][bus.congestion2] || '❓';
                html += `
                    <div class="bus-item">
                        <div class="bus-route">${bus.route}번</div>
                        <div class="bus-direction">→ ${bus.direction}</div>
                        <div class="bus-arrival">🚌 ${bus.arrival1} ${congestionIcon}</div>
                        <div class="bus-arrival">🚌 ${bus.arrival2} ${congestionIcon2}</div>
                    </div>
                `;
            });
            html += '</div>';
            return html;
        }
        
        // 페이지 로드시 버스 정보 가져오기
        refreshBus();
    </script>
</body>
</html>
"""

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/bus':
            self.send_response(200)
            self.send_header("Content-type", "application/json; charset=utf-8")
            self.end_headers()
            data = get_bus_arrival_info()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode())
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML.encode())

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    print(f"서버 시작: http://0.0.0.0:{port}")
    HTTPServer(("0.0.0.0", port), Handler).serve_forever()
