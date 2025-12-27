#!/usr/bin/env python3
"""이벤트 캘린더 - 공휴일 및 대형 행사"""
import json
from datetime import datetime, date, timedelta

# 2025년 공휴일 (고정)
HOLIDAYS_2025 = {
    "2025-01-01": "신정",
    "2025-01-28": "설날 연휴",
    "2025-01-29": "설날",
    "2025-01-30": "설날 연휴",
    "2025-03-01": "삼일절",
    "2025-05-05": "어린이날",
    "2025-05-06": "대체공휴일",
    "2025-06-06": "현충일",
    "2025-08-15": "광복절",
    "2025-09-06": "추석 연휴",
    "2025-09-07": "추석 연휴",
    "2025-09-08": "추석",
    "2025-09-09": "추석 연휴",
    "2025-10-03": "개천절",
    "2025-10-09": "한글날",
    "2025-12-25": "크리스마스"
}

# 대형 행사 (예시)
MAJOR_EVENTS = {
    "2025-03-15": {"name": "서울모터쇼", "location": "킨텍스", "impact": "중간"},
    "2025-05-01": {"name": "근로자의날 집회", "location": "여의도", "impact": "높음"},
    "2025-07-15": {"name": "여름휴가철 시작", "location": "전국", "impact": "높음"},
    "2025-12-31": {"name": "연말 행사", "location": "강남/홍대", "impact": "높음"}
}

def get_today_events():
    """오늘의 이벤트 확인"""
    today = date.today().strftime("%Y-%m-%d")
    events = []
    
    # 공휴일 확인
    if today in HOLIDAYS_2025:
        events.append({
            "type": "holiday",
            "name": HOLIDAYS_2025[today],
            "impact": "높음",
            "description": "공휴일로 인한 교통 패턴 변화"
        })
    
    # 대형 행사 확인
    if today in MAJOR_EVENTS:
        event = MAJOR_EVENTS[today]
        events.append({
            "type": "event",
            "name": event["name"],
            "location": event["location"],
            "impact": event["impact"],
            "description": f"{event['location']}에서 {event['name']} 개최"
        })
    
    return events

def get_week_events():
    """이번 주 이벤트 확인"""
    today = datetime.now().date()
    week_events = []
    
    for i in range(7):
        check_date = today + timedelta(days=i)
        date_str = check_date.strftime("%Y-%m-%d")
        
        if date_str in HOLIDAYS_2025:
            week_events.append({
                "date": date_str,
                "day": check_date.strftime("%A"),
                "type": "holiday",
                "name": HOLIDAYS_2025[date_str]
            })
        
        if date_str in MAJOR_EVENTS:
            event = MAJOR_EVENTS[date_str]
            week_events.append({
                "date": date_str,
                "day": check_date.strftime("%A"),
                "type": "event",
                "name": event["name"],
                "impact": event["impact"]
            })
    
    return week_events

def calculate_event_impact():
    """이벤트 기반 교통 영향도 계산"""
    events = get_today_events()
    
    if not events:
        return {
            "impact_factor": 1.0,
            "events": [],
            "recommendation": "평상시 패턴 예상"
        }
    
    total_impact = 1.0
    recommendations = []
    
    for event in events:
        if event["type"] == "holiday":
            if "연휴" in event["name"] or event["name"] in ["설날", "추석"]:
                total_impact *= 0.3  # 대형 연휴: 70% 감소
                recommendations.append("🏖️ 대형 연휴 - 매우 한적")
            else:
                total_impact *= 0.6  # 일반 공휴일: 40% 감소
                recommendations.append("🎉 공휴일 - 한적함")
        
        elif event["type"] == "event":
            if event["impact"] == "높음":
                total_impact *= 1.3  # 30% 증가
                recommendations.append(f"🎪 {event['name']} - 혼잡 예상")
            elif event["impact"] == "중간":
                total_impact *= 1.1  # 10% 증가
                recommendations.append(f"📅 {event['name']} - 약간 혼잡")
    
    return {
        "impact_factor": round(total_impact, 2),
        "events": events,
        "recommendation": " | ".join(recommendations) if recommendations else "평상시 패턴"
    }

def get_special_days():
    """특별한 날 패턴"""
    now = datetime.now()
    today = now.date()
    
    special = []
    
    # 월초/월말
    if today.day <= 3:
        special.append("월초 - 직장인 출근 증가")
    elif today.day >= 28:
        special.append("월말 - 야근 증가")
    
    # 급여일 (25일 전후)
    if 23 <= today.day <= 27:
        special.append("급여일 전후 - 외출 증가")
    
    # 금요일 저녁
    if now.weekday() == 4 and now.hour >= 17:
        special.append("불금 - 퇴근 후 외출 증가")
    
    return special

if __name__ == "__main__":
    print("=== 이벤트 캘린더 분석 ===")
    
    # 오늘의 이벤트
    impact = calculate_event_impact()
    print(f"이벤트 영향도: {impact['impact_factor']}배")
    print(f"추천: {impact['recommendation']}")
    
    if impact['events']:
        print("\n오늘의 이벤트:")
        for event in impact['events']:
            print(f"  - {event['name']} ({event['type']})")
    
    # 특별한 날
    special = get_special_days()
    if special:
        print(f"\n특별 패턴: {', '.join(special)}")
    
    # 이번 주 이벤트
    week_events = get_week_events()
    if week_events:
        print(f"\n이번 주 이벤트:")
        for event in week_events:
            print(f"  {event['date']} ({event['day']}): {event['name']}")
