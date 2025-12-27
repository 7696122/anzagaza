# 🐛 버그 수정 보고서

**날짜**: 2025-12-27  
**상태**: ✅ **해결됨**

---

## 버그 1: 날씨 데이터 undefined 오류

### 증상
프론트엔드에서 날씨 정보 표시 시 `undefined` 표시

### 원인
**server.py의 `/api/weather` 엔드포인트**에서 응답 구조 오류:

```python
# ❌ 잘못된 구조
return jsonify({
    "weather": weather,  # weather 객체를 nested 구조로 감쌈
    "timestamp": ...
})

# 결과 (프론트엔드가 받는 데이터)
{
  "weather": {
    "weather": "맑음",      # ← data.weather.weather 필요
    "temperature": 3.2,
    ...
  },
  "timestamp": "..."
}
```

**app.js의 formatWeatherInfo() 기대 구조**:
```javascript
function formatWeatherInfo(data) {
    data.weather      // 날씨 설명
    data.temperature  // 기온
    data.humidity     // 습도
    data.is_raining   // 비 여부
    ...
}
```

### 해결책
**server.py 수정** - 응답 직렬화 시 객체를 전개

```python
# ✅ 수정된 구조
weather = get_weather_data()
return jsonify({
    **weather,  # 날씨 필드들을 최상위로 전개
    "timestamp": datetime.now().isoformat()
})

# 결과 (프론트엔드가 받는 데이터)
{
  "weather": "맑음",      # ✅ data.weather 접근 가능
  "temperature": 3.2,
  "humidity": 45,
  "is_raining": false,
  "is_snowing": false,
  "impact_factor": 1.0,
  "impact_reason": [],
  "recommendation": "☀️ 날씨 좋음 - 평소 패턴 예상",
  "timestamp": "2025-12-27T..."
}
```

### 파일 변경
- `server.py` - `/api/weather` 엔드포인트 (11-22줄)

---

## 버그 2: 교통 데이터 구조 오류

### 증상
배차간격 정보 표시 안 됨

### 원인
동일한 응답 구조 문제:

```python
# ❌ 잘못된 구조
return jsonify({
    "traffic": headway_data,  # nested
    "timestamp": ...
})

# app.js에서 기대
for (const [route, info] of Object.entries(data)) {
    // data.421, data.400, data.405 직접 접근 필요
}
```

### 해결책
**server.py 수정** - 동일 방식 적용

```python
# ✅ 수정된 구조
headway_data = calculate_headway_pattern()
return jsonify({
    **headway_data,  # 배차간격 데이터 전개
    "timestamp": ...
})
```

### 파일 변경
- `server.py` - `/api/traffic` 엔드포인트 (164-176줄)

---

## 버그 3: 존재하지 않는 DOM 요소 참조

### 증상
JavaScript 콘솔 오류:
```
Uncaught TypeError: Cannot set property 'textContent' of null
```

### 원인
**app.js 354줄**: HTML에 없는 요소 참조

```javascript
// ❌ 버그 - #currentDay 요소 없음
document.getElementById('currentDay').textContent = ...
```

index.html에는 이 요소가 정의되지 않음.

### 해결책
**app.js 수정** - null 체크 추가

```javascript
// ✅ 수정됨
const currentDayEl = document.getElementById('currentDay');
if (currentDayEl) {
    currentDayEl.textContent = days[today] + (isWeekend ? ' (주말)' : ' (평일)');
}
```

### 파일 변경
- `static/app.js` - 350-357줄

---

## 버그 4: 트래픽 데이터 필터링 부족

### 증상
배차간격 섹션에 `timestamp` 필드가 포함되어 처리 오류 발생 가능

### 원인
app.js의 formatTrafficInfo()가 모든 필드를 버스 노선으로 처리하려고 시도

```javascript
// ❌ 전체 필드 순회 (timestamp 포함)
for (const [route, info] of Object.entries(data)) {
    const frequency = info.frequency_per_hour;  // timestamp에는 없음 → undefined
}
```

### 해결책
**app.js 수정** - timestamp/error 필드 필터링

```javascript
// ✅ 수정됨
const routes = Object.entries(data).filter(([key]) => 
    key !== 'timestamp' && key !== 'error'
);

for (const [route, info] of routes) {
    // 안전하게 frequency_per_hour 접근 가능
}
```

### 파일 변경
- `static/app.js` - 227-237줄

---

## 수정 확인

### 테스트 결과
```
✅ /api/weather       → weather, temperature, humidity 필드 정상
✅ /api/traffic       → 3개 노선 정보 정상
✅ /api/weekday       → 응답 정상
✅ /api/quiet-times   → 응답 정상
✅ /health            → 상태 정상
```

### 프론트엔드 동작
```
✅ 날씨 정보 표시      (weather, temperature, humidity 정상)
✅ 배차간격 표시      (3개 노선 정보 정상)
✅ 콘솔 오류 제거      (DOM 요소 체크 추가)
✅ UI 렌더링           (모든 섹션 정상)
```

---

## 변경 파일 요약

| 파일 | 수정 내용 | 줄 수 | 영향도 |
|------|---------|-------|--------|
| `server.py` | `/api/weather`, `/api/traffic` 응답 구조 수정 | 2개 함수 | 🟡 중간 |
| `static/app.js` | DOM 요소 체크 + 필터링 추가 | 2개 함수 | 🟡 중간 |

---

## 근본 원인 분석

### API 응답 설계 패턴 불일치
- **server.py**: 응답을 `{ wrapper: {...} }` 구조로 감쌈
- **app.js**: 응답을 평탄한 구조로 기대 (`{ field1, field2, ... }`)

### 해결 방식
Python의 `**` 전개 연산자 사용:
```python
# 중첩된 딕셔너리 -> 평탄화
data = {"weather": "맑음", "temp": 3.2}

# 방법 1: wrapper 구조 (❌ 버그 원인)
{"weather": data}

# 방법 2: 전개 (✅ 권장)
{**data, "timestamp": "..."}  # {"weather": "맑음", "temp": 3.2, "timestamp": "..."}
```

---

## 예방 방법

### 1. API 응답 스키마 정의
```python
# responses.py
class WeatherResponse:
    """날씨 API 응답 스키마"""
    weather: str
    temperature: float
    humidity: int
    timestamp: str
```

### 2. API 문서화 (OpenAPI/Swagger)
```yaml
/api/weather:
  responses:
    200:
      schema:
        properties:
          weather:
            type: string
          temperature:
            type: number
          humidity:
            type: integer
```

### 3. 자동 테스트
```python
def test_weather_api_schema():
    resp = requests.get('/api/weather')
    data = resp.json()
    assert 'weather' in data
    assert 'temperature' in data
    assert 'humidity' in data
```

---

## 배포 절차

```bash
# 1. 수정사항 확인
git diff

# 2. 테스트
python3 -m unittest test_utils.py -v

# 3. 서버 재시작
python3 server.py

# 4. 브라우저 확인
# - 날씨 섹션 정상 표시
# - 배차간격 3개 노선 표시
# - 콘솔 오류 없음
```

---

## 결론

**3개 버그 모두 해결됨**
- ✅ 날씨 undefined 오류 → 응답 구조 수정
- ✅ 배차간격 오류 → 응답 구조 수정  
- ✅ DOM 오류 → null 체크 추가
- ✅ 필터링 오류 → 필터링 로직 강화

**권장사항**: API 응답 스키마 정의 및 Swagger 문서화
