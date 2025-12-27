#!/usr/bin/env python3
"""통합 추천 시스템 - 일관성 있는 추천"""
from occupancy_analysis import analyze_bus_occupancy, get_comfort_statistics
from quiet_times import get_quiet_time_recommendations
from ml_model import predict_congestion
from datetime import datetime

def get_unified_recommendation():
    """모든 데이터를 종합한 통합 추천"""
    
    # 1. 실제 버스 승객 수 (가장 중요)
    occupancy = analyze_bus_occupancy()
    comfort_stats = get_comfort_statistics()
    
    # 2. 시간대별 패턴
    quiet_times = get_quiet_time_recommendations()
    
    # 3. ML 예측
    ml_prediction = predict_congestion()
    
    # 통합 분석
    current_situation = analyze_current_situation(occupancy, comfort_stats, quiet_times)
    
    return {
        "main_recommendation": current_situation["main_recommendation"],
        "current_status": current_situation["current_status"],
        "best_bus": current_situation["best_bus"],
        "next_quiet_time": quiet_times["next_quiet_time"],
        "confidence": ml_prediction["confidence"]
    }

def analyze_current_situation(occupancy, comfort_stats, quiet_times):
    """현재 상황 종합 분석"""
    
    if "error" in occupancy or "error" in comfort_stats:
        return {
            "main_recommendation": {
                "action": "정보 부족",
                "reason": "실시간 데이터 오류",
                "color": "#6b7280"
            },
            "current_status": "알 수 없음",
            "best_bus": None
        }
    
    # 가장 한적한 버스 찾기
    best_bus = None
    min_passengers = 999
    
    for bus in occupancy["buses"]:
        passengers1 = bus["bus1_passengers"]
        passengers2 = bus["bus2_passengers"]
        
        if isinstance(passengers1, int) and passengers1 < min_passengers:
            min_passengers = passengers1
            best_bus = {
                "route": bus["route"],
                "passengers": passengers1,
                "arrival": bus["arrival1"],
                "comfort": bus["bus1_comfort"]
            }
        
        if isinstance(passengers2, int) and passengers2 < min_passengers:
            min_passengers = passengers2
            best_bus = {
                "route": bus["route"],
                "passengers": passengers2,
                "arrival": bus["arrival2"],
                "comfort": bus["bus2_comfort"]
            }
    
    # 전체 상황 판단
    if not best_bus:
        current_status = "정보없음"
        main_recommendation = {
            "action": "정보 부족",
            "reason": "버스 정보를 확인할 수 없습니다",
            "color": "#6b7280"
        }
    elif min_passengers <= 25:
        current_status = "매우한적"
        main_recommendation = {
            "action": "지금 타세요!",
            "reason": f"{best_bus['route']}번 {min_passengers}명 - 매우 편안",
            "color": "#22c55e"
        }
    elif min_passengers <= 35:
        current_status = "한적"
        main_recommendation = {
            "action": "지금 타세요!",
            "reason": f"{best_bus['route']}번 {min_passengers}명 - 좌석 있음",
            "color": "#22c55e"
        }
    elif min_passengers <= 45:
        current_status = "보통"
        main_recommendation = {
            "action": "괜찮은 시간",
            "reason": f"{best_bus['route']}번 {min_passengers}명 - 적당한 혼잡도",
            "color": "#eab308"
        }
    elif min_passengers <= 55:
        current_status = "혼잡"
        main_recommendation = {
            "action": "다른 시간 고려",
            "reason": f"가장 한적한 {best_bus['route']}번도 {min_passengers}명",
            "color": "#f97316"
        }
    else:
        current_status = "매우혼잡"
        main_recommendation = {
            "action": "다른 시간 추천",
            "reason": f"모든 버스 혼잡 (최소 {min_passengers}명)",
            "color": "#ef4444"
        }
    
    return {
        "main_recommendation": main_recommendation,
        "current_status": current_status,
        "best_bus": best_bus
    }

def get_detailed_bus_recommendations():
    """개별 버스별 상세 추천"""
    occupancy = analyze_bus_occupancy()
    
    if "error" in occupancy:
        return {"error": occupancy["error"]}
    
    recommendations = []
    
    for bus in occupancy["buses"]:
        route = bus["route"]
        passengers1 = bus["bus1_passengers"]
        passengers2 = bus["bus2_passengers"]
        
        if isinstance(passengers1, int) and isinstance(passengers2, int):
            if passengers1 <= passengers2:
                recommendation = f"첫 번째 버스 추천 ({passengers1}명 vs {passengers2}명)"
                best_choice = "first"
            else:
                recommendation = f"두 번째 버스 추천 ({passengers2}명 vs {passengers1}명)"
                best_choice = "second"
        else:
            recommendation = "정보 부족"
            best_choice = "unknown"
        
        recommendations.append({
            "route": route,
            "recommendation": recommendation,
            "best_choice": best_choice,
            "bus1_info": f"{bus['arrival1']} - {passengers1}명",
            "bus2_info": f"{bus['arrival2']} - {passengers2}명"
        })
    
    return {"buses": recommendations}

if __name__ == "__main__":
    print("=== 통합 추천 시스템 ===")
    
    unified = get_unified_recommendation()
    
    print(f"\n🎯 {unified['main_recommendation']['action']}")
    print(f"   {unified['main_recommendation']['reason']}")
    
    if unified['best_bus']:
        best = unified['best_bus']
        print(f"\n🚌 추천 버스: {best['route']}번")
        print(f"   도착시간: {best['arrival']}")
        print(f"   승객 수: {best['passengers']}명")
        print(f"   상태: {best['comfort']}")
    
    print(f"\n📊 현재 상황: {unified['current_status']}")
    print(f"⏰ 다음 한적한 시간: {unified['next_quiet_time']['time']}")
    print(f"🤖 AI 신뢰도: {unified['confidence']*100:.0f}%")
    
    print(f"\n=== 개별 버스 추천 ===")
    detailed = get_detailed_bus_recommendations()
    if "error" not in detailed:
        for bus in detailed["buses"]:
            print(f"{bus['route']}번: {bus['recommendation']}")
            print(f"  첫 번째: {bus['bus1_info']}")
            print(f"  두 번째: {bus['bus2_info']}")
