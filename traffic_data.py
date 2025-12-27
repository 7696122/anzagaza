#!/usr/bin/env python3
"""서울시 교통 빅데이터 연동 - 버스 GPS 및 운행 패턴"""
import requests
import json
from datetime import datetime
from seoul_api import get_api_key

def get_bus_gps_data(route_id="100100409"):  # 421번
    """버스 GPS 위치 정보 조회"""
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
        data = response.json()
        
        if data.get('msgBody', {}).get('itemList'):
            buses = []
            for item in data['msgBody']['itemList']:
                buses.append({
                    'plateNo': item.get('plainNo', 'N/A'),
                    'stationId': item.get('stId', ''),
                    'stationName': item.get('stNm', ''),
                    'stationSeq': int(item.get('sectOrd', 0)),
                    'direction': item.get('adirection', ''),
                    'lastUpdateTime': item.get('tmX', ''),  # GPS 시간
                    'busType': item.get('busType', '0')  # 0: 일반, 1: 저상
                })
            return {'buses': buses, 'total_count': len(buses)}
        return data
    except Exception as e:
        return {"error": str(e)}

def get_route_stations(route_id="100100409"):
    """노선의 모든 정류장 정보 조회"""
    api_key = get_api_key()
    if not api_key:
        return {"error": "API 키를 찾을 수 없습니다"}
    
    url = "http://ws.bus.go.kr/api/rest/busRouteInfo/getStaionByRoute"
    params = {
        "serviceKey": api_key,
        "busRouteId": route_id,
        "resultType": "json"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        if data.get('msgBody', {}).get('itemList'):
            stations = []
            for item in data['msgBody']['itemList']:
                stations.append({
                    'stationId': item.get('station', ''),
                    'stationName': item.get('stationNm', ''),
                    'stationSeq': int(item.get('seq', 0)),
                    'arsId': item.get('arsId', ''),
                    'x': float(item.get('gpsX', 0)),
                    'y': float(item.get('gpsY', 0))
                })
            return {'stations': stations, 'total_stations': len(stations)}
        return data
    except Exception as e:
        return {"error": str(e)}

def analyze_bus_distribution():
    """421번과 400번 버스 분포 분석"""
    routes = {
        "421": "100100409",
        "400": "100100596"
    }
    
    analysis = {}
    
    for route_name, route_id in routes.items():
        print(f"\n=== {route_name}번 버스 분석 ===")
        
        # GPS 데이터
        gps_data = get_bus_gps_data(route_id)
        if "buses" in gps_data:
            buses = gps_data["buses"]
            total_buses = len(buses)
            
            # 보광동주민센터 근처 버스 찾기
            bogwang_nearby = []
            for bus in buses:
                if "보광동" in bus["stationName"] or bus["stationSeq"] in [23, 24, 25]:  # 보광동 근처 정류장 순번
                    bogwang_nearby.append(bus)
            
            analysis[route_name] = {
                "total_buses": total_buses,
                "bogwang_nearby": len(bogwang_nearby),
                "buses_detail": bogwang_nearby,
                "coverage": f"{len(bogwang_nearby)}/{total_buses}"
            }
            
            print(f"총 운행 버스: {total_buses}대")
            print(f"보광동 근처: {len(bogwang_nearby)}대")
            
            for bus in bogwang_nearby:
                print(f"  {bus['plateNo']} - {bus['stationName']} ({bus['stationSeq']}번째)")
        else:
            print(f"데이터 조회 실패: {gps_data}")
            analysis[route_name] = {"error": gps_data.get("error", "Unknown error")}
    
    return analysis

def calculate_headway_pattern():
    """배차간격 패턴 분석"""
    # 실시간 도착 정보로 배차간격 추정
    from seoul_api import get_bus_arrival_info
    
    arrival_data = get_bus_arrival_info("03278")
    if "buses" not in arrival_data:
        return {"error": "도착 정보 없음"}
    
    headway_analysis = {}
    
    for bus in arrival_data["buses"]:
        route = bus["route"]
        
        # 첫 번째와 두 번째 버스 도착 시간 차이로 배차간격 추정
        arrival1 = bus["arrival1"]
        arrival2 = bus["arrival2"]
        
        # "N분후" 패턴에서 숫자 추출
        import re
        min1_match = re.search(r'(\d+)분후', arrival1)
        min2_match = re.search(r'(\d+)분후', arrival2)
        
        if min1_match and min2_match:
            min1 = int(min1_match.group(1))
            min2 = int(min2_match.group(1))
            headway = min2 - min1
            
            headway_analysis[route] = {
                "next_bus": min1,
                "second_bus": min2,
                "estimated_headway": headway,
                "frequency_per_hour": 60 // headway if headway > 0 else "N/A"
            }
    
    return headway_analysis

if __name__ == "__main__":
    print("=== 서울시 교통 빅데이터 분석 ===")
    
    # 버스 분포 분석
    distribution = analyze_bus_distribution()
    
    print("\n=== 배차간격 분석 ===")
    headway = calculate_headway_pattern()
    for route, data in headway.items():
        if "error" not in data:
            print(f"{route}번: 배차간격 약 {data['estimated_headway']}분, 시간당 {data['frequency_per_hour']}대")
