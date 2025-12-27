#!/usr/bin/env python3
"""서울시 OpenAPI에서 실제 10분 간격 버스 데이터 조회"""
import requests
import json
from seoul_api import get_api_key

def get_seoul_api_key():
    """서울시 API 키 가져오기 (data.seoul.go.kr용)"""
    # ~/.authinfo에서 data.seoul.go.kr 키 찾기
    from pathlib import Path
    authinfo = Path.home() / ".authinfo"
    if not authinfo.exists():
        return None
    
    with open(authinfo) as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if "data.seoul.go.kr" in line:
            for j in range(i+1, min(i+5, len(lines))):
                if "password" in lines[j]:
                    return lines[j].split("password")[1].strip()
    return None

def get_bus_time_data(route="421", year_month="202411"):
    """버스 시간대별 승하차 데이터 조회"""
    api_key = get_seoul_api_key()
    if not api_key:
        return {"error": "서울시 API 키를 찾을 수 없습니다"}
    
    # 서울시 버스노선별 정류장별 시간대별 승하차 인원 정보
    url = f"http://openapi.seoul.go.kr:8088/{api_key}/json/CardBusTimeNew/1/100/{year_month}/{route}/"
    
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def analyze_bogwang_station(data, route):
    """보광동주민센터 정류장 데이터 분석"""
    if "CardBusTimeNew" not in data:
        return None
    
    stations = data["CardBusTimeNew"]["row"]
    bogwang_data = None
    
    # 보광동주민센터 찾기
    for station in stations:
        if "보광동주민센터" in station["SBWY_STNS_NM"]:
            bogwang_data = station
            break
    
    if not bogwang_data:
        return None
    
    # 시간대별 데이터 추출
    hourly_data = {}
    for hour in range(4, 24):  # 04시부터 23시까지
        on_key = f"HR_{hour}_GET_ON_TNOPE"
        off_key = f"HR_{hour}_GET_OFF_TNOPE"
        hourly_data[hour] = {
            "on": int(bogwang_data.get(on_key, 0)),
            "off": int(bogwang_data.get(off_key, 0))
        }
    
    return {
        "station_name": bogwang_data["SBWY_STNS_NM"],
        "route": route,
        "hourly_data": hourly_data
    }

if __name__ == "__main__":
    print("서울시 OpenAPI에서 실제 버스 데이터 조회")
    
    # 421번 데이터 조회
    print("\n=== 421번 버스 데이터 ===")
    data_421 = get_bus_time_data("421")
    if "error" in data_421:
        print(f"오류: {data_421['error']}")
    else:
        result_421 = analyze_bogwang_station(data_421, "421")
        if result_421:
            print(f"정류장: {result_421['station_name']}")
            print("시간 | 승차 | 하차")
            for hour, data in result_421['hourly_data'].items():
                if data['on'] > 0 or data['off'] > 0:
                    print(f"{hour:02d}시 | {data['on']:4d} | {data['off']:4d}")
        else:
            print("보광동주민센터 정류장을 찾을 수 없습니다")
    
    # 400번 데이터 조회
    print("\n=== 400번 버스 데이터 ===")
    data_400 = get_bus_time_data("400")
    if "error" in data_400:
        print(f"오류: {data_400['error']}")
    else:
        result_400 = analyze_bogwang_station(data_400, "400")
        if result_400:
            print(f"정류장: {result_400['station_name']}")
            print("시간 | 승차 | 하차")
            for hour, data in result_400['hourly_data'].items():
                if data['on'] > 0 or data['off'] > 0:
                    print(f"{hour:02d}시 | {data['on']:4d} | {data['off']:4d}")
        else:
            print("보광동주민센터 정류장을 찾을 수 없습니다")
