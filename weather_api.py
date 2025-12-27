#!/usr/bin/env python3
"""날씨 데이터 연동 - 버스 이용 패턴 예측용"""
import requests
import json
from datetime import datetime

def get_weather_data():
    """OpenWeatherMap API로 현재 날씨 조회"""
    # 무료 API 키 (제한적)
    api_key = "demo"  # 실제로는 환경변수에서 가져와야 함
    
    # 보광동 좌표 (위도: 37.5265, 경도: 127.0005)
    lat, lon = 37.5265, 127.0005
    
    try:
        # 현재 날씨
        current_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric&lang=kr"
        
        # 데모용 - 실제 API 대신 샘플 데이터
        sample_weather = {
            "weather": [{"main": "Clear", "description": "맑음"}],
            "main": {"temp": 3.2, "humidity": 45},
            "wind": {"speed": 2.1},
            "rain": None,  # 비 없음
            "snow": None   # 눈 없음
        }
        
        return parse_weather_data(sample_weather)
        
    except Exception as e:
        return {"error": str(e)}

def parse_weather_data(data):
    """날씨 데이터 파싱 및 버스 이용 영향 분석"""
    if "error" in data:
        return data
    
    weather_main = data["weather"][0]["main"]
    description = data["weather"][0]["description"]
    temp = data["main"]["temp"]
    humidity = data["main"]["humidity"]
    
    # 비/눈 여부
    is_raining = data.get("rain") is not None
    is_snowing = data.get("snow") is not None
    
    # 버스 이용 영향도 계산
    impact_factor = 1.0  # 기본값
    impact_reason = []
    
    if is_raining:
        impact_factor *= 1.3  # 비 올 때 30% 증가
        impact_reason.append("비로 인한 이용 증가")
    
    if is_snowing:
        impact_factor *= 1.5  # 눈 올 때 50% 증가
        impact_reason.append("눈으로 인한 이용 급증")
    
    if temp < 0:
        impact_factor *= 1.2  # 영하일 때 20% 증가
        impact_reason.append("혹한으로 인한 이용 증가")
    elif temp > 30:
        impact_factor *= 1.1  # 폭염일 때 10% 증가
        impact_reason.append("폭염으로 인한 이용 증가")
    
    if humidity > 80:
        impact_factor *= 1.1  # 습도 높을 때 10% 증가
        impact_reason.append("높은 습도로 인한 이용 증가")
    
    return {
        "weather": description,
        "temperature": temp,
        "humidity": humidity,
        "is_raining": is_raining,
        "is_snowing": is_snowing,
        "impact_factor": round(impact_factor, 2),
        "impact_reason": impact_reason,
        "recommendation": get_weather_recommendation(impact_factor, impact_reason)
    }

def get_weather_recommendation(impact_factor, reasons):
    """날씨 기반 추천 메시지"""
    if impact_factor >= 1.4:
        return f"⚠️ 평소보다 {int((impact_factor-1)*100)}% 더 혼잡 예상 - 더 일찍 출발하세요"
    elif impact_factor >= 1.2:
        return f"🌧️ 평소보다 {int((impact_factor-1)*100)}% 혼잡 예상 - 여유시간 확보"
    elif impact_factor >= 1.1:
        return f"☁️ 평소보다 약간 혼잡 예상"
    else:
        return "☀️ 날씨 좋음 - 평소 패턴 예상"

if __name__ == "__main__":
    print("=== 현재 날씨 및 버스 이용 영향 ===")
    weather = get_weather_data()
    
    if "error" in weather:
        print(f"오류: {weather['error']}")
    else:
        print(f"날씨: {weather['weather']}")
        print(f"기온: {weather['temperature']}°C")
        print(f"습도: {weather['humidity']}%")
        print(f"영향도: {weather['impact_factor']}배")
        print(f"추천: {weather['recommendation']}")
        
        if weather['impact_reason']:
            print(f"이유: {', '.join(weather['impact_reason'])}")
