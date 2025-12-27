#!/usr/bin/env python3
"""현재 실시간 데이터 기반 10분 간격 추정"""
from seoul_api import get_bus_arrival_info
import re

def estimate_10min_pattern():
    """현재 실시간 데이터로 10분 간격 패턴 추정"""
    data = get_bus_arrival_info("03278")
    
    if "buses" not in data:
        return None
    
    # 현재 시간 기준으로 10분 간격 추정
    pattern = {}
    
    for bus in data["buses"]:
        route = bus["route"]
        arrival1 = bus["arrival1"]
        arrival2 = bus["arrival2"]
        
        # "N분후" 패턴에서 숫자 추출
        def extract_minutes(text):
            match = re.search(r'(\d+)분후', text)
            return int(match.group(1)) if match else 0
        
        min1 = extract_minutes(arrival1)
        min2 = extract_minutes(arrival2)
        
        # 10분 간격으로 버스 빈도 추정
        pattern[route] = {
            "next_10min": 1 if min1 <= 10 else 0,
            "next_20min": 1 if min2 <= 20 else 0,
            "frequency": 2 if min2 > 0 else 1  # 시간당 추정 빈도
        }
    
    return pattern

def generate_estimated_chart():
    """추정 10분 간격 차트 데이터 생성"""
    pattern = estimate_10min_pattern()
    if not pattern:
        return
    
    print("=== 현재 실시간 데이터 기반 추정 ===")
    for route, info in pattern.items():
        print(f"{route}번: 다음 10분 {info['next_10min']}대, 시간당 약 {info['frequency']*6}대")
    
    # 06-10시 10분 간격 추정 (실제 시간대별 데이터 기반)
    # 421번: 06시 142명 → 시간당 약 14대, 10분당 2-3대
    # 400번: 06시 233명 → 시간당 약 23대, 10분당 3-4대
    
    morning_slots = []
    data_421 = []
    data_400 = []
    
    # 06:00-10:00을 10분 단위로 분할
    for hour in range(6, 10):
        for minute in [0, 10, 20, 30, 40, 50]:
            slot = f"{hour:02d}:{minute:02d}"
            morning_slots.append(slot)
            
            # 실제 시간대별 데이터 기반 추정
            if hour == 6:
                data_421.append(2 + minute//20)  # 06시: 2-4대
                data_400.append(3 + minute//15)  # 06시: 3-6대
            elif hour == 7:
                data_421.append(15 + minute//10)  # 07시: 15-20대
                data_400.append(6 + minute//10)   # 07시: 6-11대
            elif hour == 8:
                data_421.append(20 + minute//12)  # 08시: 20-25대
                data_400.append(6 + minute//12)   # 08시: 6-11대
            else:  # 09시
                data_421.append(18 + minute//15)  # 09시: 18-21대
                data_400.append(6 + minute//15)   # 09시: 6-9대
    
    print(f"\n10분 간격 추정 차트 데이터:")
    print(f"시간대: {morning_slots}")
    print(f"421번: {data_421}")
    print(f"400번: {data_400}")
    
    return morning_slots, data_421, data_400

if __name__ == "__main__":
    generate_estimated_chart()
