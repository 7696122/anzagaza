#!/usr/bin/env python3
"""실시간 버스 데이터 수집기 - 10분 간격 패턴 분석용"""
import json
import time
from datetime import datetime
from seoul_api import get_bus_arrival_info
from weather_api import get_weather_data
from traffic_data import calculate_headway_pattern
from pathlib import Path

def collect_realtime_data():
    """실시간 버스 데이터 수집"""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    weekday = now.weekday()  # 0=월요일, 6=일요일
    weekday_name = ['월', '화', '수', '목', '금', '토', '일'][weekday]
    
    data = get_bus_arrival_info("03278")
    weather = get_weather_data()
    traffic = calculate_headway_pattern()
    
    if "buses" in data:
        result = {
            "timestamp": timestamp,
            "hour": now.hour,
            "minute": now.minute,
            "weekday": weekday,
            "weekday_name": weekday_name,
            "is_weekend": weekday >= 5,
            "weather": weather,
            "traffic": traffic,
            "buses": data["buses"]
        }
        
        data_file = Path("realtime_data.jsonl")
        with open(data_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
        
        print(f"[{timestamp} {weekday_name}] 수집 완료")
        if "weather" in result and not result["weather"].get("error"):
            weather_info = result["weather"]
            print(f"  날씨: {weather_info['weather']} {weather_info['temperature']}°C (영향도: {weather_info['impact_factor']}배)")
        if "traffic" in result:
            traffic_info = result["traffic"]
            for route, info in traffic_info.items():
                if "error" not in info:
                    print(f"  {route}번 배차: {info['estimated_headway']}분 간격")
        for bus in data["buses"]:
            print(f"  {bus['route']}번: {bus['arrival1']}")
    else:
        print(f"[{timestamp} {weekday_name}] 실패: {data}")

def analyze_weekday_patterns():
    """요일별 패턴 분석"""
    data_file = Path("realtime_data.jsonl")
    if not data_file.exists():
        print("수집된 데이터가 없습니다")
        return {}
    
    # 요일별 시간대별 패턴
    weekday_patterns = {}  # {weekday: {hour: {route: count}}}
    
    with open(data_file, encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            weekday = data.get("weekday", 0)
            weekday_name = data.get("weekday_name", "?")
            hour = data["hour"]
            
            if weekday not in weekday_patterns:
                weekday_patterns[weekday] = {}
            if hour not in weekday_patterns[weekday]:
                weekday_patterns[weekday][hour] = {"421": 0, "400": 0, "405": 0}
            
            for bus in data["buses"]:
                route = bus["route"]
                if route in weekday_patterns[weekday][hour]:
                    weekday_patterns[weekday][hour][route] += 1
    
    return weekday_patterns

def compare_weekday_weekend():
    """평일 vs 주말 패턴 비교"""
    patterns = analyze_weekday_patterns()
    if not patterns:
        return
    
    weekday_data = {}  # 평일 (월-금)
    weekend_data = {}  # 주말 (토-일)
    
    for weekday, hours in patterns.items():
        target = weekday_data if weekday < 5 else weekend_data
        
        for hour, routes in hours.items():
            if hour not in target:
                target[hour] = {"421": 0, "400": 0, "405": 0}
            for route, count in routes.items():
                target[hour][route] += count
    
    print("=== 평일 vs 주말 패턴 비교 ===")
    print("\n평일 (월-금):")
    for hour in sorted(weekday_data.keys()):
        print(f"{hour:02d}시: 421번 {weekday_data[hour]['421']}회, 400번 {weekday_data[hour]['400']}회")
    
    print("\n주말 (토-일):")
    for hour in sorted(weekend_data.keys()):
        print(f"{hour:02d}시: 421번 {weekend_data[hour]['421']}회, 400번 {weekend_data[hour]['400']}회")
    
    return weekday_data, weekend_data

def generate_10min_chart_data():
    """10분 간격 차트 데이터 생성"""
    patterns = analyze_collected_data()
    if not patterns:
        print("분석할 데이터가 없습니다")
        return
    
    print("=== 10분 간격 버스 운행 패턴 ===")
    for slot in sorted(patterns.keys()):
        print(f"{slot}: 421번 {patterns[slot]['421']}회, 400번 {patterns[slot]['400']}회")
    
    # JavaScript 차트 데이터 형태로 출력
    slots = sorted(patterns.keys())
    data_421 = [patterns[slot]["421"] for slot in slots]
    data_400 = [patterns[slot]["400"] for slot in slots]
    
    print(f"\nJavaScript 차트 데이터:")
    print(f"labels: {slots}")
    print(f"421번 data: {data_421}")
    print(f"400번 data: {data_400}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "start":
        print("10분 간격 데이터 수집 시작...")
        while True:
            collect_realtime_data()
            print("10분 대기 중...")
            time.sleep(600)  # 10분
    elif len(sys.argv) > 1 and sys.argv[1] == "analyze":
        compare_weekday_weekend()
    elif len(sys.argv) > 1 and sys.argv[1] == "weekday":
        patterns = analyze_weekday_patterns()
        weekday_names = ['월', '화', '수', '목', '금', '토', '일']
        for weekday, hours in patterns.items():
            print(f"\n=== {weekday_names[weekday]}요일 ===")
            for hour in sorted(hours.keys()):
                print(f"{hour:02d}시: {hours[hour]}")
    else:
        print("1회 테스트:")
        collect_realtime_data()
        print("\n사용법:")
        print("  python3 collect_data.py start    # 지속 수집")
        print("  python3 collect_data.py analyze  # 평일/주말 비교")
        print("  python3 collect_data.py weekday  # 요일별 상세")
