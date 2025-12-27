#!/usr/bin/env python3
"""날씨 데이터 연동 - 버스 이용 패턴 예측용"""

import os
import requests
import json
from datetime import datetime, timedelta
import math


def convert_to_grid(lat, lon):
    """위경도를 기상청 격자좌표로 변환"""
    # 기상청 격자 변환 상수
    RE = 6371.00877  # 지구 반경(km)
    GRID = 5.0  # 격자 간격(km)
    SLAT1 = 30.0  # 투영 위도1(degree)
    SLAT2 = 60.0  # 투영 위도2(degree)
    OLON = 126.0  # 기준점 경도(degree)
    OLAT = 38.0  # 기준점 위도(degree)
    XO = 43  # 기준점 X좌표(GRID)
    YO = 136  # 기준점 Y좌표(GRID)

    DEGRAD = math.pi / 180.0
    RADDEG = 180.0 / math.pi

    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)

    ra = math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / math.pow(ra, sn)
    theta = lon * DEGRAD - olon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn
    x = ra * math.sin(theta) + XO
    y = ro - ra * math.cos(theta) + YO

    return int(x + 1.5), int(y + 1.5)


def get_weather_data():
    """기상청 동네예보 API로 날씨 조회"""
    # 환경변수에서 API 키 가져오기
    api_key = os.environ.get("KMA_API_KEY")
    if not api_key:
        return {"error": "KMA_API_KEY 환경변수가 설정되지 않았습니다"}

    # 보광동 좌표 (위도: 37.5265, 경도: 127.0005)
    lat, lon = 37.5265, 127.0005

    # 격자 좌표로 변환
    nx, ny = convert_to_grid(lat, lon)

    # 기상청 API는 3시간 단위로 예보 제공
    # 현재 시간 기준으로 가장 최근 예보 시간 계산
    now = datetime.now()
    base_time = now.replace(
        hour=now.hour - now.hour % 3, minute=0, second=0, microsecond=0
    )
    base_date = base_time.strftime("%Y%m%d")
    base_time_str = base_time.strftime("%H%M")

    # 만약 현재 시간이 3시간 단위 경계에 있다면 이전 시간으로 조정
    if now.minute < 10:  # API 갱신 시간 고려
        base_time = base_time - timedelta(hours=3)
        base_date = base_time.strftime("%Y%m%d")
        base_time_str = base_time.strftime("%H%M")

    try:
        url = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
        params = {
            "serviceKey": api_key,
            "pageNo": "1",
            "numOfRows": "1000",
            "dataType": "JSON",
            "base_date": base_date,
            "base_time": base_time_str,
            "nx": str(nx),
            "ny": str(ny),
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("response", {}).get("header", {}).get("resultCode") != "00":
            return {"error": "기상청 API 응답 오류"}

        items = (
            data.get("response", {}).get("body", {}).get("items", {}).get("item", [])
        )
        if not items:
            return {"error": "날씨 데이터가 없습니다"}

        return parse_kma_weather_data(items)

    except requests.exceptions.RequestException as e:
        return {"error": f"API 요청 실패: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}


def parse_kma_weather_data(items):
    """기상청 날씨 데이터 파싱"""
    # 카테고리별 최신 데이터 추출
    latest_data = {}
    for item in items:
        category = item["category"]
        if category not in latest_data:
            latest_data[category] = item

    # 필요한 데이터 추출
    temp = (
        float(latest_data.get("TMP", {}).get("fcstValue", "0"))
        if "TMP" in latest_data
        else None
    )
    humidity = (
        float(latest_data.get("REH", {}).get("fcstValue", "0"))
        if "REH" in latest_data
        else None
    )
    sky = (
        int(latest_data.get("SKY", {}).get("fcstValue", "1"))
        if "SKY" in latest_data
        else 1
    )
    pty = (
        int(latest_data.get("PTY", {}).get("fcstValue", "0"))
        if "PTY" in latest_data
        else 0
    )
    pop = (
        int(latest_data.get("POP", {}).get("fcstValue", "0"))
        if "POP" in latest_data
        else 0
    )

    # 날씨 설명 생성
    weather_desc = get_weather_description(sky, pty)

    # 비/눈 여부
    is_raining = pty in [1, 2, 4]  # 비, 비/눈, 소나기
    is_snowing = pty in [2, 3]  # 비/눈, 눈

    # 버스 이용 영향도 계산
    impact_factor = 1.0
    impact_reason = []

    if is_raining:
        impact_factor *= 1.3 + (pop / 100) * 0.2  # 강수확률에 따른 추가 영향
        impact_reason.append("비로 인한 이용 증가")

    if is_snowing:
        impact_factor *= 1.5
        impact_reason.append("눈으로 인한 이용 급증")

    if temp is not None:
        if temp < 0:
            impact_factor *= 1.2
            impact_reason.append("혹한으로 인한 이용 증가")
        elif temp > 30:
            impact_factor *= 1.1
            impact_reason.append("폭염으로 인한 이용 증가")

    if humidity is not None and humidity > 80:
        impact_factor *= 1.1
        impact_reason.append("높은 습도로 인한 이용 증가")

    return {
        "weather": weather_desc,
        "temperature": temp,
        "humidity": humidity,
        "is_raining": is_raining,
        "is_snowing": is_snowing,
        "precipitation_probability": pop,
        "impact_factor": round(impact_factor, 2),
        "impact_reason": impact_reason,
        "recommendation": get_weather_recommendation(impact_factor, impact_reason),
    }


def parse_weather_data(data):
    """기존 호환성을 위한 함수 - 이제 parse_kma_weather_data 사용"""
    return (
        parse_kma_weather_data(data)
        if isinstance(data, list)
        else {"error": "잘못된 데이터 형식"}
    )


def get_weather_description(sky, pty):
    """기상청 코드로 날씨 설명 생성"""
    pty_desc = {0: "", 1: "비", 2: "비/눈", 3: "눈", 4: "소나기"}

    sky_desc = {1: "맑음", 3: "구름많음", 4: "흐림"}

    desc = pty_desc.get(pty, "")
    if not desc:
        desc = sky_desc.get(sky, "맑음")

    return desc


def get_weather_recommendation(impact_factor, reasons):
    """날씨 기반 추천 메시지"""
    if impact_factor >= 1.4:
        return f"⚠️ 평소보다 {int((impact_factor - 1) * 100)}% 더 혼잡 예상 - 더 일찍 출발하세요"
    elif impact_factor >= 1.2:
        return f"🌧️ 평소보다 {int((impact_factor - 1) * 100)}% 혼잡 예상 - 여유시간 확보"
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

        if weather["impact_reason"]:
            print(f"이유: {', '.join(weather['impact_reason'])}")
