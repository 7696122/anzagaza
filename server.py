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
        <strong>⭐ 출근 최적 시간: 06:00-06:50</strong>
        421번: 평균 24명 | 400번: 평균 16명 (매우 한적)
        <strong>⭐ 퇴근 최적 시간: 20:00 이후</strong>
        두 노선 모두 18:30 피크 대비 50% 이하
    </div>
    
    <div class="card">
        <h3>🚌 실시간 버스 정보</h3>
        <div id="busInfo">로딩 중...</div>
        <button onclick="refreshBus()">새로고침</button>
    </div>
    
    <div class="card">
        <h3>출근 시간대 승차 인원 (421번) - 10분 간격</h3>
        <canvas id="morningChart421"></canvas>
    </div>
    
    <div class="card">
        <h3>출근 시간대 승차 인원 (400번) - 10분 간격</h3>
        <canvas id="morningChart400"></canvas>
    </div>
    
    <div class="card">
        <h3>퇴근 시간대 하차 인원 (421번) - 10분 간격</h3>
        <canvas id="eveningChart421"></canvas>
    </div>
    
    <div class="card">
        <h3>퇴근 시간대 하차 인원 (400번) - 10분 간격</h3>
        <canvas id="eveningChart400"></canvas>
    </div>
    
    <p class="footer">데이터: 서울시 버스 승하차 정보 (2024.11)</p>
    
    <script>
        // 10분 간격 차트 데이터
        const morning421 = {
            labels: ['06:00', '06:10', '06:20', '06:30', '06:40', '06:50', '07:00', '07:10', '07:20', '07:30', '07:40', '07:50', '08:00', '08:10', '08:20', '08:30', '08:40', '08:50', '09:00', '09:10', '09:20', '09:30', '09:40', '09:50'],
            datasets: [{
                label: '421번 승차',
                data: [18, 22, 25, 28, 24, 25, 145, 168, 185, 195, 201, 200, 220, 225, 218, 210, 205, 200, 195, 190, 185, 180, 175, 170],
                backgroundColor: function(context) {
                    const value = context.parsed.y;
                    if (value < 50) return '#22c55e';
                    if (value < 150) return '#eab308';
                    if (value < 200) return '#f97316';
                    return '#ef4444';
                },
                borderRadius: 4
            }]
        };
        const morning400 = {
            labels: ['06:00', '06:10', '06:20', '06:30', '06:40', '06:50', '07:00', '07:10', '07:20', '07:30', '07:40', '07:50', '08:00', '08:10', '08:20', '08:30', '08:40', '08:50', '09:00', '09:10', '09:20', '09:30', '09:40', '09:50'],
            datasets: [{
                label: '400번 승차',
                data: [12, 15, 18, 20, 16, 18, 110, 125, 140, 155, 165, 161, 195, 200, 192, 185, 180, 175, 170, 165, 160, 155, 150, 145],
                backgroundColor: function(context) {
                    const value = context.parsed.y;
                    if (value < 50) return '#22c55e';
                    if (value < 150) return '#eab308';
                    if (value < 200) return '#f97316';
                    return '#ef4444';
                },
                borderRadius: 4
            }]
        };
        const evening421 = {
            labels: ['17:00', '17:10', '17:20', '17:30', '17:40', '17:50', '18:00', '18:10', '18:20', '18:30', '18:40', '18:50', '19:00', '19:10', '19:20', '19:30', '19:40', '19:50', '20:00', '20:10', '20:20', '20:30', '20:40', '20:50'],
            datasets: [{
                label: '421번 하차',
                data: [95, 105, 115, 125, 135, 140, 145, 155, 165, 175, 180, 178, 125, 120, 115, 110, 105, 100, 85, 80, 75, 70, 65, 60],
                backgroundColor: function(context) {
                    const value = context.parsed.y;
                    if (value < 80) return '#22c55e';
                    if (value < 120) return '#eab308';
                    if (value < 160) return '#f97316';
                    return '#ef4444';
                },
                borderRadius: 4
            }]
        };
        const evening400 = {
            labels: ['17:00', '17:10', '17:20', '17:30', '17:40', '17:50', '18:00', '18:10', '18:20', '18:30', '18:40', '18:50', '19:00', '19:10', '19:20', '19:30', '19:40', '19:50', '20:00', '20:10', '20:20', '20:30', '20:40', '20:50'],
            datasets: [{
                label: '400번 하차',
                data: [78, 85, 92, 98, 105, 110, 115, 125, 135, 145, 150, 148, 105, 100, 95, 90, 85, 80, 70, 65, 60, 55, 50, 45],
                backgroundColor: function(context) {
                    const value = context.parsed.y;
                    if (value < 80) return '#22c55e';
                    if (value < 120) return '#eab308';
                    if (value < 160) return '#f97316';
                    return '#ef4444';
                },
                borderRadius: 4
            }]
        };
        const opts = { 
            responsive: true, 
            plugins: { legend: { display: false } }, 
            scales: { 
                y: { beginAtZero: true },
                x: { 
                    ticks: { 
                        maxTicksLimit: 12,
                        callback: function(value, index) {
                            return index % 2 === 0 ? this.getLabelForValue(value) : '';
                        }
                    }
                }
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
