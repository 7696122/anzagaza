#!/usr/bin/env python3
"""유틸리티 함수 테스트"""
import unittest
from utils import (
    get_comfort_level, find_best_bus, format_time, 
    safe_get, validate_api_response
)


class TestComfortLevel(unittest.TestCase):
    """혼잡도 레벨 테스트"""
    
    def test_comfort_very_quiet(self):
        self.assertEqual(get_comfort_level(20), "매우한적")
    
    def test_comfort_quiet(self):
        self.assertEqual(get_comfort_level(30), "한적")
    
    def test_comfort_normal(self):
        self.assertEqual(get_comfort_level(40), "보통")
    
    def test_comfort_crowded(self):
        self.assertEqual(get_comfort_level(50), "혼잡")
    
    def test_comfort_very_crowded(self):
        self.assertEqual(get_comfort_level(60), "매우혼잡")
    
    def test_comfort_invalid_input(self):
        self.assertIsNone(get_comfort_level("invalid"))


class TestFindBestBus(unittest.TestCase):
    """최고 버스 찾기 테스트"""
    
    def test_find_best_bus(self):
        buses = [
            {
                "route": "421",
                "bus1_passengers": 30,
                "bus2_passengers": 50,
                "arrival1": "2분",
                "arrival2": "7분",
                "bus1_comfort": "한적",
                "bus2_comfort": "혼잡"
            }
        ]
        best, min_pass = find_best_bus(buses)
        
        self.assertEqual(best["route"], "421")
        self.assertEqual(best["passengers"], 30)
        self.assertEqual(min_pass, 30)
    
    def test_find_best_bus_empty(self):
        best, min_pass = find_best_bus([])
        self.assertIsNone(best)
        self.assertEqual(min_pass, 999)


class TestFormatTime(unittest.TestCase):
    """시간 포맷팅 테스트"""
    
    def test_format_time_soon(self):
        self.assertEqual(format_time(0.5), "곧 도착")
    
    def test_format_time_minutes(self):
        self.assertEqual(format_time(15), "15분")
    
    def test_format_time_hours(self):
        self.assertEqual(format_time(90), "1시간 30분")


class TestSafeGet(unittest.TestCase):
    """안전한 딕셔너리 조회 테스트"""
    
    def test_safe_get_simple(self):
        obj = {"name": "John", "age": 30}
        self.assertEqual(safe_get(obj, "name"), "John")
    
    def test_safe_get_nested(self):
        obj = {"user": {"profile": {"name": "John"}}}
        self.assertEqual(safe_get(obj, "user.profile.name"), "John")
    
    def test_safe_get_default(self):
        obj = {"name": "John"}
        self.assertEqual(safe_get(obj, "age", 0), 0)
    
    def test_safe_get_invalid_path(self):
        obj = {"name": "John"}
        self.assertIsNone(safe_get(obj, "user.profile.name"))


class TestValidateApiResponse(unittest.TestCase):
    """API 응답 검증 테스트"""
    
    def test_validate_valid_response(self):
        response = {"status": "ok", "data": []}
        self.assertTrue(validate_api_response(response))
    
    def test_validate_required_fields(self):
        response = {"status": "ok", "data": []}
        self.assertTrue(validate_api_response(response, ["status", "data"]))
    
    def test_validate_missing_required_field(self):
        response = {"status": "ok"}
        self.assertFalse(validate_api_response(response, ["status", "data"]))
    
    def test_validate_invalid_type(self):
        self.assertFalse(validate_api_response([1, 2, 3]))


if __name__ == '__main__':
    unittest.main()
