#!/usr/bin/env python3
"""실시간 버스 데이터 수집기 - 10분 간격 패턴 분석용"""
import json
import time
from datetime import datetime
from seoul_api import get_bus_arrival_info
from pathlib import Path

def collect_realtime_data():
    """실시간 버스 데이터 수집"""
    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    
    data = get_bus_arrival_info("03278")
    
    if "buses" in data:
        result = {
            "timestamp": timestamp,
            "hour": now.hour,
            "minute": now.minute,
            "buses": data["buses"]
        }
        
        data_file = Path("realtime_data.jsonl")
        with open(data_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")
        
        print(f"[{timestamp}] 수집 완료")
        for bus in data["buses"]:
            print(f"  {bus['route']}번: {bus['arrival1']}")
    else:
        print(f"[{timestamp}] 실패: {data}")

def analyze_collected_data():
    """수집된 데이터로 10분 간격 패턴 분석"""
    data_file = Path("realtime_data.jsonl")
    if not data_file.exists():
        print("수집된 데이터가 없습니다")
        return {}
    
    # 10분 간격별 버스 빈도 분석
    patterns = {}  # {time_slot: {route: frequency}}
    
    with open(data_file, encoding="utf-8") as f:
        for line in f:
            data = json.loads(line)
            hour = data["hour"]
            minute = data["minute"] // 10 * 10  # 10분 단위
            slot = f"{hour:02d}:{minute:02d}"
            
            if slot not in patterns:
                patterns[slot] = {"421": 0, "400": 0, "405": 0}
            
            for bus in data["buses"]:
                route = bus["route"]
                if route in patterns[slot]:
                    patterns[slot][route] += 1
    
    return patterns

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
        generate_10min_chart_data()
    else:
        print("1회 테스트:")
        collect_realtime_data()
        print("\n사용법:")
        print("  python3 collect_data.py start    # 지속 수집")
        print("  python3 collect_data.py analyze  # 데이터 분석")
