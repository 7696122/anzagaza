#!/usr/bin/env python3
"""버스 내 실제 승객 수 분석"""
import json
from seoul_api import get_bus_arrival_info

def analyze_bus_occupancy():
    """버스 혼잡도를 실제 승객 수로 변환"""
    data = get_bus_arrival_info("03278")
    
    if "buses" not in data:
        return {"error": "버스 정보 없음"}
    
    occupancy_analysis = []
    
    for bus in data["buses"]:
        route = bus["route"]
        
        # 혼잡도 레벨 (1-4)
        congestion1 = int(bus.get("congestion1", 0))
        congestion2 = int(bus.get("congestion2", 0))
        
        # 혼잡도별 예상 승객 수 (버스 정원 기준)
        bus_capacity = get_bus_capacity(route)
        
        occupancy1 = estimate_passenger_count(congestion1, bus_capacity, route)
        occupancy2 = estimate_passenger_count(congestion2, bus_capacity, route)
        
        occupancy_analysis.append({
            "route": route,
            "direction": bus["direction"],
            "arrival1": bus["arrival1"],
            "arrival2": bus["arrival2"],
            "bus1_passengers": occupancy1["passengers"],
            "bus1_occupancy_rate": occupancy1["rate"],
            "bus1_comfort": occupancy1["comfort"],
            "bus2_passengers": occupancy2["passengers"],
            "bus2_occupancy_rate": occupancy2["rate"],
            "bus2_comfort": occupancy2["comfort"],
            "recommendation": get_occupancy_recommendation(occupancy1, occupancy2)
        })
    
    return {"buses": occupancy_analysis}

def get_bus_capacity(route):
    """노선별 버스 정원"""
    # 서울시 시내버스 표준 정원
    capacity_map = {
        "421": {"seats": 28, "standing": 42, "total": 70},  # 일반버스
        "400": {"seats": 28, "standing": 42, "total": 70},  # 일반버스
        "405": {"seats": 28, "standing": 42, "total": 70}   # 일반버스
    }
    
    return capacity_map.get(route, {"seats": 28, "standing": 42, "total": 70})

def estimate_passenger_count(congestion_level, capacity, route=None):
    """혼잡도 레벨을 실제 승객 수로 변환 (노선별 차이 반영)"""
    total_capacity = capacity["total"]
    
    # 문자열을 정수로 변환
    try:
        congestion_level = int(congestion_level)
    except (ValueError, TypeError):
        congestion_level = 0
    
    if congestion_level == 0:  # 정보 없음
        return {
            "passengers": "정보없음",
            "rate": 0,
            "comfort": "알 수 없음"
        }
    
    # 노선별 기본 승객 수 조정
    route_factor = 1.0
    if route == "421":
        route_factor = 1.1  # 421번이 더 인기
    elif route == "400":
        route_factor = 0.9  # 400번이 덜 혼잡
    elif route == "405":
        route_factor = 0.8  # 405번이 가장 한적
    
    # 시간대별 조정
    from datetime import datetime
    now = datetime.now()
    time_factor = 1.0
    if 7 <= now.hour <= 9 or 17 <= now.hour <= 19:
        time_factor = 1.2  # 출퇴근 시간
    elif now.weekday() >= 5:  # 주말
        time_factor = 0.8
    
    if congestion_level == 1:  # 여유
        base_passengers = 20
    elif congestion_level == 2:  # 보통
        base_passengers = 38
    elif congestion_level == 3:  # 혼잡
        base_passengers = 54
    else:  # congestion_level == 4, 매우혼잡
        base_passengers = 66
    
    # 노선별, 시간대별 조정 적용
    passengers = int(base_passengers * route_factor * time_factor)
    passengers = min(max(passengers, 5), total_capacity)  # 5명~70명 범위
    
    # 최종 승객 수 기반으로 comfort 결정 (일관성 보장)
    if passengers <= 25:
        comfort = "🟢 매우 편안 - 좌석 여유"
    elif passengers <= 40:
        comfort = "🟡 보통 - 좌석 대부분 차있음"
    elif passengers <= 55:
        comfort = "🟠 혼잡 - 입석 승객 많음"
    else:
        comfort = "🔴 매우혼잡 - 승차 어려움"
    
    occupancy_rate = round((passengers / total_capacity) * 100, 1)
    
    return {
        "passengers": passengers,
        "rate": occupancy_rate,
        "comfort": comfort
    }

def get_occupancy_recommendation(bus1, bus2):
    """승객 수 기반 추천"""
    if isinstance(bus1["passengers"], str):  # 정보 없음
        return "정보 부족으로 추천 불가"
    
    if bus1["passengers"] <= 20:
        return f"🟢 첫 번째 버스 추천 - 약 {bus1['passengers']}명 탑승 (매우 편안)"
    elif bus1["passengers"] <= 40:
        return f"🟡 첫 번째 버스 양호 - 약 {bus1['passengers']}명 탑승 (좌석 있음)"
    elif bus2["passengers"] < bus1["passengers"]:
        return f"⏰ 두 번째 버스 대기 추천 - {bus2['passengers']}명 vs {bus1['passengers']}명"
    else:
        return f"🔴 두 버스 모두 혼잡 - 다른 시간 고려 ({bus1['passengers']}명, {bus2['passengers']}명)"

def get_comfort_statistics():
    """편안함 통계"""
    analysis = analyze_bus_occupancy()
    
    if "error" in analysis:
        return analysis
    
    comfort_stats = {
        "very_comfortable": 0,  # 20명 이하
        "comfortable": 0,       # 21-40명
        "crowded": 0,          # 41-60명
        "very_crowded": 0      # 61명 이상
    }
    
    total_buses = 0
    
    for bus in analysis["buses"]:
        for bus_num in [1, 2]:
            passengers = bus[f"bus{bus_num}_passengers"]
            if isinstance(passengers, int):
                total_buses += 1
                if passengers <= 20:
                    comfort_stats["very_comfortable"] += 1
                elif passengers <= 40:
                    comfort_stats["comfortable"] += 1
                elif passengers <= 60:
                    comfort_stats["crowded"] += 1
                else:
                    comfort_stats["very_crowded"] += 1
    
    if total_buses == 0:
        return {"error": "분석할 버스 없음"}
    
    # 백분율 계산
    for key in comfort_stats:
        comfort_stats[key] = round((comfort_stats[key] / total_buses) * 100, 1)
    
    return {
        "total_buses_analyzed": total_buses,
        "comfort_distribution": comfort_stats,
        "recommendation": get_overall_recommendation(comfort_stats)
    }

def get_overall_recommendation(stats):
    """전체 상황 기반 추천"""
    if stats["very_comfortable"] >= 50:
        return "🟢 현재 시간대 매우 좋음 - 편안한 버스 많음"
    elif stats["comfortable"] >= 40:
        return "🟡 현재 시간대 양호 - 적당한 혼잡도"
    elif stats["very_crowded"] >= 50:
        return "🔴 현재 시간대 피하세요 - 대부분 매우 혼잡"
    else:
        return "🟠 현재 시간대 보통 - 선택적 이용"

if __name__ == "__main__":
    print("=== 버스 내 실제 승객 수 분석 ===")
    
    # 개별 버스 분석
    occupancy = analyze_bus_occupancy()
    if "error" in occupancy:
        print(f"오류: {occupancy['error']}")
    else:
        for bus in occupancy["buses"]:
            print(f"\n{bus['route']}번 → {bus['direction']}")
            print(f"  첫 번째: {bus['arrival1']} - {bus['bus1_passengers']}명 ({bus['bus1_occupancy_rate']}%)")
            print(f"           {bus['bus1_comfort']}")
            print(f"  두 번째: {bus['arrival2']} - {bus['bus2_passengers']}명 ({bus['bus2_occupancy_rate']}%)")
            print(f"           {bus['bus2_comfort']}")
            print(f"  추천: {bus['recommendation']}")
    
    # 전체 통계
    print(f"\n=== 현재 시간대 편안함 통계 ===")
    stats = get_comfort_statistics()
    if "error" not in stats:
        print(f"분석 버스: {stats['total_buses_analyzed']}대")
        dist = stats['comfort_distribution']
        print(f"매우 편안: {dist['very_comfortable']}%")
        print(f"편안함: {dist['comfortable']}%")
        print(f"혼잡: {dist['crowded']}%")
        print(f"매우 혼잡: {dist['very_crowded']}%")
        print(f"추천: {stats['recommendation']}")
