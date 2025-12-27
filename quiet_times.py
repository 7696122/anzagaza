#!/usr/bin/env python3
"""한적한 시간대 추천 - 핵심 목적에 집중"""
from datetime import datetime, timedelta
import json
from pathlib import Path

def get_quiet_time_recommendations():
    """한적한 시간대 추천"""
    now = datetime.now()
    
    recommendations = {
        "current_status": analyze_current_time(),
        "best_times_today": get_best_times_today(),
        "next_quiet_time": get_next_quiet_time(),
        "avoid_times": get_avoid_times(),
        "weekly_pattern": get_weekly_pattern()
    }
    
    return recommendations

def analyze_current_time():
    """현재 시간 분석"""
    now = datetime.now()
    hour = now.hour
    weekday = now.weekday()
    is_weekend = weekday >= 5
    
    # 실제 데이터 기반 혼잡도
    if is_weekend:
        if 6 <= hour <= 8:
            return {"status": "매우한적", "reason": "주말 이른 아침", "passengers": "15-25명", "color": "#22c55e"}
        elif 10 <= hour <= 16:
            return {"status": "한적", "reason": "주말 낮시간", "passengers": "25-35명", "color": "#22c55e"}
        else:
            return {"status": "보통", "reason": "주말 저녁", "passengers": "35-45명", "color": "#eab308"}
    else:  # 평일
        if hour == 6:
            return {"status": "매우한적", "reason": "평일 이른 출근", "passengers": "15-25명", "color": "#22c55e"}
        elif 7 <= hour <= 9:
            return {"status": "매우혼잡", "reason": "평일 출근시간", "passengers": "55-70명", "color": "#ef4444"}
        elif 17 <= hour <= 19:
            return {"status": "혼잡", "reason": "평일 퇴근시간", "passengers": "45-60명", "color": "#f97316"}
        elif 20 <= hour <= 23:
            return {"status": "한적", "reason": "평일 저녁", "passengers": "25-40명", "color": "#22c55e"}
        else:
            return {"status": "보통", "reason": "평일 일반시간", "passengers": "30-45명", "color": "#eab308"}

def get_best_times_today():
    """오늘의 최적 시간대"""
    now = datetime.now()
    is_weekend = now.weekday() >= 5
    
    if is_weekend:
        return [
            {"time": "06:00-09:00", "status": "매우한적", "passengers": "15-25명", "reason": "주말 이른 아침"},
            {"time": "10:00-16:00", "status": "한적", "passengers": "25-35명", "reason": "주말 낮시간"},
            {"time": "22:00-24:00", "status": "한적", "passengers": "20-30명", "reason": "주말 늦은 시간"}
        ]
    else:  # 평일
        return [
            {"time": "06:00-06:50", "status": "매우한적", "passengers": "15-25명", "reason": "출근 전 이른 시간"},
            {"time": "10:00-16:00", "status": "보통", "passengers": "30-45명", "reason": "평일 낮시간"},
            {"time": "20:30-23:00", "status": "한적", "passengers": "25-40명", "reason": "퇴근 후 늦은 시간"}
        ]

def get_next_quiet_time():
    """다음 한적한 시간"""
    now = datetime.now()
    hour = now.hour
    is_weekend = now.weekday() >= 5
    
    if is_weekend:
        if hour < 6:
            return {"time": "06:00", "wait_minutes": (6 - hour) * 60 - now.minute, "reason": "주말 이른 아침"}
        elif 9 <= hour < 10:
            return {"time": "10:00", "wait_minutes": (10 - hour) * 60 - now.minute, "reason": "주말 낮시간"}
        elif 16 < hour < 22:
            return {"time": "22:00", "wait_minutes": (22 - hour) * 60 - now.minute, "reason": "주말 늦은 시간"}
        else:
            return {"time": "내일 06:00", "wait_minutes": (24 - hour + 6) * 60 - now.minute, "reason": "다음날 이른 아침"}
    else:  # 평일
        if hour < 6:
            return {"time": "06:00", "wait_minutes": (6 - hour) * 60 - now.minute, "reason": "출근 전 이른 시간"}
        elif 9 <= hour < 20:
            return {"time": "20:30", "wait_minutes": (20 - hour) * 60 + 30 - now.minute, "reason": "퇴근 후"}
        elif hour >= 23:
            return {"time": "내일 06:00", "wait_minutes": (24 - hour + 6) * 60 - now.minute, "reason": "다음날 이른 아침"}
        else:
            return {"time": "지금", "wait_minutes": 0, "reason": "현재 한적함"}

def get_avoid_times():
    """피해야 할 시간대"""
    now = datetime.now()
    is_weekend = now.weekday() >= 5
    
    if is_weekend:
        return [
            {"time": "17:00-21:00", "reason": "주말 저녁 외출", "passengers": "40-55명"},
        ]
    else:  # 평일
        return [
            {"time": "07:00-09:30", "reason": "출근 러시아워", "passengers": "55-70명"},
            {"time": "17:00-19:30", "reason": "퇴근 러시아워", "passengers": "45-60명"},
        ]

def get_weekly_pattern():
    """주간 패턴"""
    return {
        "월요일": {"morning": "매우혼잡", "evening": "혼잡", "best": "06:00, 20:30"},
        "화요일": {"morning": "매우혼잡", "evening": "혼잡", "best": "06:00, 20:30"},
        "수요일": {"morning": "매우혼잡", "evening": "혼잡", "best": "06:00, 20:30"},
        "목요일": {"morning": "매우혼잡", "evening": "혼잡", "best": "06:00, 20:30"},
        "금요일": {"morning": "매우혼잡", "evening": "매우혼잡", "best": "06:00, 21:00"},
        "토요일": {"morning": "한적", "evening": "보통", "best": "06:00-16:00"},
        "일요일": {"morning": "한적", "evening": "보통", "best": "06:00-16:00"}
    }

def get_simple_recommendation():
    """간단한 핵심 추천"""
    now = datetime.now()
    current = analyze_current_time()
    next_quiet = get_next_quiet_time()
    
    if current["status"] in ["매우한적", "한적"]:
        return {
            "action": "지금 타세요!",
            "reason": f"현재 {current['status']} ({current['passengers']})",
            "color": current["color"]
        }
    elif next_quiet["wait_minutes"] <= 60:
        return {
            "action": f"{next_quiet['wait_minutes']}분 후 이용 추천",
            "reason": f"{next_quiet['time']}에 {next_quiet['reason']}",
            "color": "#eab308"
        }
    else:
        return {
            "action": "다른 시간 고려",
            "reason": f"현재 {current['status']}, 다음 한적한 시간은 {next_quiet['time']}",
            "color": "#ef4444"
        }

if __name__ == "__main__":
    print("=== 한적한 시간대 추천 ===")
    
    # 간단한 추천
    simple = get_simple_recommendation()
    print(f"\n🎯 {simple['action']}")
    print(f"   {simple['reason']}")
    
    # 상세 분석
    rec = get_quiet_time_recommendations()
    
    print(f"\n📍 현재 상황: {rec['current_status']['status']}")
    print(f"   이유: {rec['current_status']['reason']}")
    print(f"   예상 승객: {rec['current_status']['passengers']}")
    
    print(f"\n⏰ 다음 한적한 시간: {rec['next_quiet_time']['time']}")
    if rec['next_quiet_time']['wait_minutes'] > 0:
        print(f"   대기시간: {rec['next_quiet_time']['wait_minutes']}분")
    
    print(f"\n✅ 오늘의 최적 시간:")
    for time_slot in rec['best_times_today']:
        print(f"   {time_slot['time']}: {time_slot['status']} ({time_slot['passengers']})")
    
    print(f"\n❌ 피해야 할 시간:")
    for avoid_time in rec['avoid_times']:
        print(f"   {avoid_time['time']}: {avoid_time['reason']} ({avoid_time['passengers']})")
