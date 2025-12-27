# 🚌 앉아가자 (AnzaGaza)

보광동주민센터에서 매봉역으로 가는 버스의 한적한 시간대를 분석하는 웹서비스

## 🎯 주요 기능

- **실시간 버스 정보**: 421번, 400번, 405번 도착 시간 및 혼잡도
- **시간대별 분석**: 실제 서울시 OpenAPI 데이터 기반
- **10분 간격 추정**: 세밀한 출퇴근 시간 추천
- **요일별 패턴**: 평일 vs 주말 비교 분석

## 📊 주요 인사이트

### 출근 추천
- **최적 시간**: 06:00-06:30
- **421번**: 10분당 2-3명 (08시 대비 1/9)
- **400번**: 10분당 3-5명 (08시 대비 1/7)

### 퇴근 추천
- **최적 시간**: 20:30 이후
- **주말**: 평일보다 30% 한적

## 🚀 실행 방법

### 로컬 실행
```bash
# 의존성 설치
pip install -r requirements.txt

# 웹서버 실행
python3 server.py

# 브라우저에서 http://127.0.0.1:8080 접속
```

### 실시간 데이터 수집
```bash
# 백그라운드 수집 시작
python3 collect_data.py start

# 평일/주말 패턴 분석
python3 collect_data.py analyze

# 요일별 상세 분석
python3 collect_data.py weekday
```

## 🌐 배포

- **라이브 사이트**: https://web-production-97f9d.up.railway.app/
- **플랫폼**: Railway
- **환경변수**: `DATA_GO_KR_API_KEY` (data.go.kr API 키)

## 📁 파일 구조

```
├── server.py           # 웹서버 (Flask 대신 내장 서버 사용)
├── seoul_api.py        # 서울시 버스 API 연동
├── collect_data.py     # 실시간 데이터 수집 및 분석
├── real_data.py        # 서울시 OpenAPI 데이터 조회
├── requirements.txt    # Python 의존성
├── Procfile           # Railway 배포 설정
└── realtime_data.jsonl # 수집된 실시간 데이터
```

## 🔧 API 엔드포인트

- `GET /` - 메인 웹페이지
- `GET /api/bus` - 실시간 버스 도착 정보
- `GET /api/weekday` - 현재 요일 및 패턴 정보

## 📈 데이터 소스

- **실시간 버스**: data.go.kr 버스 도착 정보 API
- **승하차 데이터**: 서울시 OpenAPI (2024년 11월)
- **정류장**: 보광동주민센터 (ARS: 03278, 03518)

## 🛠️ 기술 스택

- **Backend**: Python 3.12
- **Frontend**: Vanilla JavaScript + Chart.js
- **API**: 서울시 OpenAPI, data.go.kr
- **배포**: Railway
- **스타일**: 글래스모피즘 디자인

## 📝 개발 히스토리

- 2024.12.20: 프로젝트 시작
- 2024.12.26: 실시간 API 연동
- 2024.12.27: 10분 간격 분석 및 요일별 패턴 완성
