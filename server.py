#!/usr/bin/env python3
"""앉아가자 - 버스 한적한 시간대 추천 웹서비스"""
from http.server import HTTPServer, SimpleHTTPRequestHandler
import json
import os
from pathlib import Path
from datetime import datetime
from seoul_api import get_bus_arrival_info
from weather_api import get_weather_data
from traffic_data import analyze_bus_distribution, calculate_headway_pattern
from ml_model import predict_congestion
from event_calendar import calculate_event_impact
from road_traffic import get_traffic_info
from occupancy_analysis import analyze_bus_occupancy, get_comfort_statistics
from quiet_times import get_quiet_time_recommendations, get_simple_recommendation

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
        elif self.path == '/api/quiet-times':
            # 한적한 시간대 추천
            recommendations = get_quiet_time_recommendations()
            simple = get_simple_recommendation()
            
            result = {
                "simple_recommendation": simple,
                "detailed_recommendations": recommendations
            }
            self.serve_json(result)
        elif self.path == '/api/bus':
            # 실제 승객 수 포함 버스 정보
            occupancy_data = analyze_bus_occupancy()
            comfort_stats = get_comfort_statistics()
            
            result = {
                "buses": occupancy_data.get("buses", []),
                "comfort_stats": comfort_stats,
                "error": occupancy_data.get("error")
            }
            self.serve_json(result)
        elif self.path == '/api/prediction':
            # ML 예측 모델
            prediction = predict_congestion()
            events = calculate_event_impact()
            road_traffic = get_traffic_info()
            
            # 모든 영향 반영
            final_prediction = (prediction['predicted_congestion'] * 
                              events['impact_factor'] * 
                              road_traffic['total_impact'])
            
            result = {
                "predicted_congestion": round(final_prediction, 2),
                "base_prediction": prediction['predicted_congestion'],
                "event_impact": events['impact_factor'],
                "traffic_impact": road_traffic['total_impact'],
                "confidence": prediction['confidence'],
                "recommendation": prediction['recommendation'],
                "events": events['events'],
                "event_recommendation": events['recommendation'],
                "traffic_recommendation": road_traffic['recommendation'],
                "congested_roads": road_traffic['congested_roads'],
                "smooth_roads": road_traffic['smooth_roads']
            }
            self.serve_json(result)
        elif self.path == '/api/traffic':
            # 교통 빅데이터 (배차간격 분석)
            headway_data = calculate_headway_pattern()
            self.serve_json(headway_data)
        elif self.path == '/api/weather':
            self.serve_json(get_weather_data())
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
