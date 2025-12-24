#!/usr/bin/env python3
"""버스 시간대별 승하차 데이터 분석 (OpenAPI 사용)"""
import json
import urllib.request
import os

API_KEY = os.environ.get("SEOUL_API_KEY", "sample")
BASE_URL = f"http://openapi.seoul.go.kr:8088/{API_KEY}/json/CardBusTimeNew"
TARGET_ROUTES = ["421", "400"]
USE_YM = "202411"

def fetch_data(start: int, end: int, route: str = None) -> dict:
    """OpenAPI에서 데이터 조회"""
    url = f"{BASE_URL}/{start}/{end}/{USE_YM}/"
    if route:
        url += f"{route}/"
    with urllib.request.urlopen(url) as res:
        return json.load(res)

def analyze_route(route: str):
    """노선별 시간대 분석"""
    print(f"\n=== {route}번 버스 ===")
    try:
        data = fetch_data(1, 5, route)
        if "CardBusTimeNew" in data:
            rows = data["CardBusTimeNew"]["row"]
            total = data["CardBusTimeNew"]["list_total_count"]
            print(f"정류장 수: {total}개 (샘플 {len(rows)}개)")
            for r in rows:
                print(f"\n정류장: {r['SBWY_STNS_NM']}")
                print("시간대 | 승차 | 하차")
                for h in range(4, 24):
                    on = r.get(f"HR_{h}_GET_ON_TNOPE", 0)
                    off = r.get(f"HR_{h}_GET_OFF_TNOPE", 0)
                    if on > 0 or off > 0:
                        print(f"  {h:02d}시 | {on:4.0f} | {off:4.0f}")
        else:
            print(f"에러: {data}")
    except Exception as e:
        print(f"에러: {e}")

if __name__ == "__main__":
    print("서울시 버스 시간대별 승하차 분석")
    print(f"API 키: {API_KEY}")
    print(f"대상 월: {USE_YM}")
    
    if API_KEY == "sample":
        print("\n⚠️  샘플 키는 5건 제한. 전체 데이터는 인증키 필요:")
        print("   https://data.seoul.go.kr 회원가입 → 인증키 발급")
        print("   export SEOUL_API_KEY=발급받은키")
    
    for route in TARGET_ROUTES:
        analyze_route(route)
