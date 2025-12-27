#!/usr/bin/env python3
"""공통 유틸리티 함수"""
import logging

logger = logging.getLogger(__name__)

# 버스 설정 (하드코드 제거)
BUS_ROUTES = {
    421: {"name": "421번", "start": "보광동주민센터", "end": "매봉역"},
    400: {"name": "400번", "start": "보광동주민센터", "end": "매봉역"},
    405: {"name": "405번", "start": "보광동주민센터", "end": "매봉역"},
}

# 혼잡도 기준
COMFORT_LEVELS = {
    "매우한적": {"range": (0, 25), "color": "#22c55e", "emoji": "😊"},
    "한적": {"range": (25, 35), "color": "#22c55e", "emoji": "🙂"},
    "보통": {"range": (35, 45), "color": "#eab308", "emoji": "😐"},
    "혼잡": {"range": (45, 55), "color": "#f97316", "emoji": "😓"},
    "매우혼잡": {"range": (55, 999), "color": "#ef4444", "emoji": "😫"},
}


def get_comfort_level(passenger_count):
    """승객 수에 따른 혼잡도 레벨 반환"""
    if not isinstance(passenger_count, (int, float)):
        return None
    
    for level, config in COMFORT_LEVELS.items():
        if config["range"][0] <= passenger_count < config["range"][1]:
            return level
    
    return "정보없음"


def get_comfort_config(level):
    """혼잡도 레벨의 설정 반환"""
    return COMFORT_LEVELS.get(level, {"color": "#6b7280", "emoji": "❓"})


def find_best_bus(buses):
    """버스 리스트에서 가장 한적한 버스 찾기"""
    best_bus = None
    min_passengers = 999
    
    for bus in buses:
        passengers1 = bus.get("bus1_passengers")
        passengers2 = bus.get("bus2_passengers")
        
        if isinstance(passengers1, int) and passengers1 < min_passengers:
            min_passengers = passengers1
            best_bus = {
                "route": bus["route"],
                "passengers": passengers1,
                "arrival": bus["arrival1"],
                "comfort": bus.get("bus1_comfort", "알 수 없음")
            }
        
        if isinstance(passengers2, int) and passengers2 < min_passengers:
            min_passengers = passengers2
            best_bus = {
                "route": bus["route"],
                "passengers": passengers2,
                "arrival": bus["arrival2"],
                "comfort": bus.get("bus2_comfort", "알 수 없음")
            }
    
    return best_bus, min_passengers


def format_time(minutes_until):
    """분 단위 시간을 읽기 쉬운 형식으로 변환"""
    if minutes_until < 1:
        return "곧 도착"
    elif minutes_until < 60:
        return f"{int(minutes_until)}분"
    else:
        hours = int(minutes_until / 60)
        mins = int(minutes_until % 60)
        return f"{hours}시간 {mins}분"


def safe_get(obj, path, default=None):
    """중첩된 딕셔너리/리스트에서 안전하게 값 가져오기"""
    try:
        keys = path.split('.')
        current = obj
        for key in keys:
            if isinstance(current, dict):
                current = current[key]
            elif isinstance(current, list):
                current = current[int(key)]
            else:
                return default
        return current
    except (KeyError, IndexError, TypeError, ValueError):
        return default


def validate_api_response(response, required_fields=None):
    """API 응답 검증"""
    if not isinstance(response, dict):
        logger.warning(f"API 응답이 딕셔너리가 아님: {type(response)}")
        return False
    
    if required_fields:
        for field in required_fields:
            if field not in response:
                logger.warning(f"필수 필드 누락: {field}")
                return False
    
    return True
