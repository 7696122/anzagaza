#!/usr/bin/env python3
"""서울시 OpenAPI 호출 모듈"""
import os
import requests
from pathlib import Path

def get_api_key():
    """~/.authinfo에서 data.go.kr API 키 읽기"""
    authinfo = Path.home() / ".authinfo"
    if not authinfo.exists():
        return None
    
    with open(authinfo) as f:
        lines = f.readlines()
        
    for i, line in enumerate(lines):
        if "data.go.kr" in line:
            # 다음 줄들에서 password 찾기
            for j in range(i+1, min(i+5, len(lines))):
                if "password" in lines[j]:
                    return lines[j].split("password")[1].strip()
    return None

def get_bus_arrival_info(station_id="03278"):
    """버스 도착 정보 조회 (보광동주민센터)"""
    api_key = get_api_key()
    if not api_key:
        return {"error": "API 키를 찾을 수 없습니다"}
    
    url = "http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid"
    params = {
        "serviceKey": api_key,
        "arsId": station_id,
        "resultType": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        # 데이터 가공
        if data.get('msgBody', {}).get('itemList'):
            buses = []
            for item in data['msgBody']['itemList']:
                buses.append({
                    'route': item['rtNm'],
                    'direction': item['adirection'],
                    'arrival1': item['arrmsg1'],
                    'arrival2': item['arrmsg2'],
                    'congestion1': item['congestion1'],
                    'congestion2': item['congestion2']
                })
            return {'buses': buses}
        return data
    except Exception as e:
        return {"error": str(e)}

def get_bus_position(route_id="100100421"):
    """버스 위치 정보 조회 (421번: 100100421)"""
    api_key = get_api_key()
    if not api_key:
        return {"error": "API 키를 찾을 수 없습니다"}
    
    url = "http://ws.bus.go.kr/api/rest/buspos/getBusPosByRtid"
    params = {
        "serviceKey": api_key,
        "busRouteId": route_id,
        "resultType": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def search_bus_stop(stop_name="보광동주민센터"):
    """정류장 검색"""
    api_key = get_api_key()
    if not api_key:
        return {"error": "API 키를 찾을 수 없습니다"}
    
    url = "http://ws.bus.go.kr/api/rest/stationinfo/getStationByName"
    params = {
        "serviceKey": api_key,
        "stSrch": stop_name,
        "resultType": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def search_bus_route(route_name="421"):
    """노선 검색"""
    api_key = get_api_key()
    if not api_key:
        return {"error": "API 키를 찾을 수 없습니다"}
    
    url = "http://ws.bus.go.kr/api/rest/busRouteInfo/getBusRouteList"
    params = {
        "serviceKey": api_key,
        "strSrch": route_name,
        "resultType": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
if __name__ == "__main__":
    # 테스트
    print("API 키:", get_api_key()[:20] + "..." if get_api_key() else "없음")
    print("\n=== 보광동주민센터 정류장 정보 ===")
    print("ARS ID 03278:")
    print(get_bus_arrival_info("03278"))
    print("\nARS ID 03518:")
    print(get_bus_arrival_info("03518"))
