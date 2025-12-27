#!/usr/bin/env python3
"""앉아가자 - 버스 한적한 시간대 추천 웹서비스"""
import os
import json
import logging
from functools import lru_cache
from datetime import datetime, timedelta
from flask import Flask, jsonify, send_from_directory

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static', template_folder='templates')

# API 모듈 임포트
try:
    from seoul_api import get_bus_arrival_info
    from weather_api import get_weather_data
    from traffic_data import analyze_bus_distribution, calculate_headway_pattern
    from ml_model import predict_congestion
    from event_calendar import calculate_event_impact
    from road_traffic import get_traffic_info
    from occupancy_analysis import analyze_bus_occupancy, get_comfort_statistics
    from quiet_times import get_quiet_time_recommendations, get_simple_recommendation
    from unified_recommendation import get_unified_recommendation, get_detailed_bus_recommendations
except ImportError as e:
    logger.error(f"모듈 임포트 실패: {e}")
    raise


# 캐싱 데코레이터 (5분)
def cache_for(seconds=300):
    def decorator(func):
        cache = {}
        cache_time = {}
        
        def wrapper(*args, **kwargs):
            key = (func.__name__, args, tuple(sorted(kwargs.items())))
            now = datetime.now()
            
            if key in cache and (now - cache_time[key]).total_seconds() < seconds:
                return cache[key]
            
            try:
                result = func(*args, **kwargs)
                cache[key] = result
                cache_time[key] = now
                return result
            except Exception as e:
                logger.error(f"캐시 함수 실행 실패 {func.__name__}: {e}")
                return {"error": str(e)}
        
        wrapper.__name__ = func.__name__  # Flask 엔드포인트 이름 설정 중요!
        return wrapper
    return decorator


# ============ API 엔드포인트 ============

@app.route('/')
def index():
    """메인 페이지"""
    try:
        return send_from_directory('templates', 'index.html')
    except Exception as e:
        logger.error(f"메인 페이지 로드 실패: {e}")
        return jsonify({"error": "페이지를 찾을 수 없습니다"}), 404


@app.route('/static/<path:path>')
def serve_static(path):
    """정적 파일 제공"""
    try:
        return send_from_directory('static', path)
    except Exception as e:
        logger.error(f"정적 파일 로드 실패 ({path}): {e}")
        return jsonify({"error": "파일을 찾을 수 없습니다"}), 404


@app.route('/api/quiet-times')
@cache_for(seconds=60)
def api_quiet_times():
    """통합 추천 시스템"""
    try:
        unified = get_unified_recommendation()
        detailed_recommendations = get_quiet_time_recommendations()
        
        return jsonify({
            "unified_recommendation": unified,
            "detailed_recommendations": detailed_recommendations,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"quiet-times API 오류: {e}", exc_info=True)
        return jsonify({"error": "추천 데이터를 가져올 수 없습니다"}), 500


@app.route('/api/bus')
@cache_for(seconds=60)
def api_bus():
    """개별 버스별 상세 추천"""
    try:
        detailed_buses = get_detailed_bus_recommendations()
        occupancy_data = analyze_bus_occupancy()
        comfort_stats = get_comfort_statistics()
        
        result = {
            "buses": occupancy_data.get("buses", []),
            "detailed_recommendations": detailed_buses.get("buses", []),
            "comfort_stats": comfort_stats,
            "timestamp": datetime.now().isoformat()
        }
        
        if "error" in occupancy_data:
            result["warning"] = occupancy_data["error"]
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"bus API 오류: {e}", exc_info=True)
        return jsonify({"error": "버스 정보를 가져올 수 없습니다"}), 500


@app.route('/api/prediction')
@cache_for(seconds=300)
def api_prediction():
    """ML 예측 모델 + 이벤트 + 교통"""
    try:
        prediction = predict_congestion()
        events = calculate_event_impact()
        road_traffic = get_traffic_info()
        
        # 모든 영향 반영
        base_pred = prediction.get('predicted_congestion', 0)
        event_factor = events.get('impact_factor', 1)
        traffic_factor = road_traffic.get('total_impact', 1)
        
        final_prediction = base_pred * event_factor * traffic_factor
        
        result = {
            "predicted_congestion": round(final_prediction, 2),
            "base_prediction": base_pred,
            "event_impact": event_factor,
            "traffic_impact": traffic_factor,
            "confidence": prediction.get('confidence', 0),
            "recommendation": prediction.get('recommendation', ''),
            "events": events.get('events', []),
            "event_recommendation": events.get('recommendation', ''),
            "traffic_recommendation": road_traffic.get('recommendation', ''),
            "congested_roads": road_traffic.get('congested_roads', []),
            "smooth_roads": road_traffic.get('smooth_roads', []),
            "timestamp": datetime.now().isoformat()
        }
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"prediction API 오류: {e}", exc_info=True)
        return jsonify({"error": "예측 데이터를 가져올 수 없습니다"}), 500


@app.route('/api/traffic')
@cache_for(seconds=300)
def api_traffic():
    """교통 빅데이터 (배차간격 분석)"""
    try:
        headway_data = calculate_headway_pattern()
        return jsonify({
            **headway_data,  # 배차간격 데이터 직접 포함
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"traffic API 오류: {e}", exc_info=True)
        return jsonify({"error": "교통 데이터를 가져올 수 없습니다"}), 500


@app.route('/api/weather')
@cache_for(seconds=600)
def api_weather():
    """날씨 정보"""
    try:
        weather = get_weather_data()
        if "error" in weather:
            return jsonify(weather), 500
        
        return jsonify({
            **weather,  # 날씨 데이터 필드들 직접 포함
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"weather API 오류: {e}", exc_info=True)
        return jsonify({"error": "날씨 데이터를 가져올 수 없습니다"}), 500


@app.route('/api/weekday')
@cache_for(seconds=3600)
def api_weekday():
    """요일 정보 및 패턴"""
    try:
        now = datetime.now()
        weekday = now.weekday()
        is_weekend = weekday >= 5
        
        result = {
            "current_day": ['월', '화', '수', '목', '금', '토', '일'][weekday],
            "is_weekend": is_weekend,
            "recommendation": "주말은 평일보다 30% 한적합니다" if is_weekend else "평일 출근시간 피하세요",
            "timestamp": now.isoformat()
        }
        
        return jsonify(result)
    except Exception as e:
        logger.error(f"weekday API 오류: {e}", exc_info=True)
        return jsonify({"error": "요일 정보를 가져올 수 없습니다"}), 500


# ============ 에러 핸들러 ============

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"404 에러: {error}")
    return jsonify({"error": "요청한 페이지를 찾을 수 없습니다"}), 404


@app.errorhandler(500)
def server_error(error):
    logger.error(f"500 에러: {error}", exc_info=True)
    return jsonify({"error": "서버 오류가 발생했습니다"}), 500


# ============ 헬스체크 ============

@app.route('/health')
def health():
    """서버 상태 확인"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    logger.info(f"서버 시작: http://0.0.0.0:{port}")
    
    # 개발 환경: debug=True, 프로덕션: debug=False
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
