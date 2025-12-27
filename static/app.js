// 하루 전체 혼잡도 패턴 차트
const hourlyPattern = {
    labels: ['06시', '07시', '08시', '09시', '10시', '11시', '12시', '13시', '14시', '15시', '16시', '17시', '18시', '19시', '20시', '21시', '22시', '23시'],
    datasets: [{
        label: '평일 평균 승객 수',
        data: [20, 55, 65, 50, 35, 35, 40, 40, 35, 35, 40, 50, 55, 45, 35, 30, 25, 20],
        backgroundColor: function(context) {
            const value = context.parsed.y;
            if (value <= 25) return '#22c55e';  // 한적
            if (value <= 40) return '#eab308';  // 보통
            if (value <= 55) return '#f97316';  // 혼잡
            return '#ef4444';                   // 매우혼잡
        },
        borderRadius: 6
    }]
};

const opts = { 
    responsive: true, 
    plugins: { 
        legend: { display: false },
        tooltip: {
            callbacks: {
                label: function(context) {
                    const value = context.parsed.y;
                    let status = '';
                    if (value <= 25) status = '한적';
                    else if (value <= 40) status = '보통';
                    else if (value <= 55) status = '혼잡';
                    else status = '매우혼잡';
                    return `${context.label}: ${value}명 (${status})`;
                }
            }
        }
    }, 
    scales: { 
        y: { 
            beginAtZero: true,
            title: {
                display: true,
                text: '평균 승객 수'
            }
        },
        x: {
            title: {
                display: true,
                text: '시간대'
            }
        }
    }
};

new Chart(document.getElementById('hourlyPattern'), { type: 'bar', data: hourlyPattern, options: opts });

// 한적한 시간대 추천
async function refreshQuietTimes() {
    document.getElementById('mainRecommendation').innerHTML = '로딩 중...';
    document.getElementById('quietTimesInfo').innerHTML = '로딩 중...';
    
    try {
        const response = await fetch('/api/quiet-times');
        const data = await response.json();
        
        document.getElementById('mainRecommendation').innerHTML = formatMainRecommendation(data.unified_recommendation);
        document.getElementById('quietTimesInfo').innerHTML = formatQuietTimesInfo(data.detailed_recommendations);
    } catch (e) {
        document.getElementById('mainRecommendation').innerHTML = '오류: ' + e.message;
        document.getElementById('quietTimesInfo').innerHTML = '오류: ' + e.message;
    }
}

function formatMainRecommendation(unified) {
    const main = unified.main_recommendation;
    const statusClass = main.color === '#22c55e' ? 'status-success' : 
                       main.color === '#eab308' ? 'status-warning' : 'status-danger';
    
    let html = `
        <div class="status-box ${statusClass}" style="text-align: center; font-size: 1.2em; padding: 20px;">
            <strong style="font-size: 1.4em; display: block; margin-bottom: 8px;">${main.action}</strong>
            <span>${main.reason}</span>
        </div>
    `;
    
    if (unified.best_bus) {
        const bus = unified.best_bus;
        html += `
            <div class="status-box status-info">
                <strong>🚌 추천: ${bus.route}번</strong><br>
                ${bus.arrival} | ${bus.passengers}명 탑승<br>
                <small>${bus.comfort}</small>
            </div>
        `;
    }
    
    return html;
}

function formatQuietTimesInfo(rec) {
    let html = `
        <div class="grid-1">
            <div class="status-box status-info">
                <strong>⏰ 다음 한적한 시간: ${rec.next_quiet_time.time}</strong><br>
                ${rec.next_quiet_time.reason}`;
    
    if (rec.next_quiet_time.wait_minutes > 0) {
        html += `<br><small>대기시간: ${rec.next_quiet_time.wait_minutes}분</small>`;
    }
    html += '</div>';
    
    html += '<div><strong>✅ 오늘의 최적 시간:</strong><br>';
    rec.best_times_today.forEach(time => {
        const statusClass = time.status === '매우한적' ? 'status-success' : 
                           time.status === '한적' ? 'status-warning' : 'status-danger';
        html += `<div class="status-box ${statusClass}" style="margin: 4px 0; font-size: 0.9em;">
            ${time.time}: ${time.status} (${time.passengers})
        </div>`;
    });
    html += '</div>';
    
    html += '<div><strong>❌ 피해야 할 시간:</strong><br>';
    rec.avoid_times.forEach(avoid => {
        html += `<div class="status-box status-danger" style="margin: 4px 0; font-size: 0.9em;">
            ${avoid.time}: ${avoid.reason} (${avoid.passengers})
        </div>`;
    });
    html += '</div>';
    
    html += '</div>';
    return html;
}

// AI 예측 분석
async function refreshPrediction() {
    document.getElementById('predictionInfo').innerHTML = '로딩 중...';
    try {
        const response = await fetch('/api/prediction');
        const data = await response.json();
        document.getElementById('predictionInfo').innerHTML = formatPredictionInfo(data);
    } catch (e) {
        document.getElementById('predictionInfo').innerHTML = '오류: ' + e.message;
    }
}

function formatPredictionInfo(data) {
    const confidence = Math.round(data.confidence * 100);
    const congestionColor = data.predicted_congestion < 0.7 ? '#22c55e' : 
                           data.predicted_congestion < 1.2 ? '#eab308' : '#ef4444';
    
    let html = `
        <div style="display: grid; gap: 12px;">
            <div style="background: ${congestionColor}; color: white; padding: 12px; border-radius: 8px;">
                <strong>🎯 종합 예측 혼잡도: ${data.predicted_congestion}배</strong><br>
                <small>신뢰도: ${confidence}% | 기본: ${data.base_prediction}배 | 이벤트: ${data.event_impact}배 | 교통: ${data.traffic_impact}배</small>
            </div>
            <div>${data.recommendation}</div>
    `;
    
    if (data.events && data.events.length > 0) {
        html += `<div style="background: #fef3c7; padding: 8px; border-radius: 6px;">
            <strong>📅 특별 이벤트:</strong><br>`;
        data.events.forEach(event => {
            html += `${event.name} (${event.type}) `;
        });
        html += `<br>${data.event_recommendation}</div>`;
    }
    
    if (data.traffic_recommendation) {
        html += `<div style="background: #f0f9ff; padding: 8px; border-radius: 6px;">
            <strong>🚗 도로 상황:</strong><br>
            ${data.traffic_recommendation}`;
        
        if (data.congested_roads && data.congested_roads.length > 0) {
            html += `<br><small>혼잡: ${data.congested_roads.join(', ')}</small>`;
        }
        if (data.smooth_roads && data.smooth_roads.length > 0) {
            html += `<br><small>원활: ${data.smooth_roads.join(', ')}</small>`;
        }
        html += '</div>';
    }
    
    html += '</div>';
    return html;
}

// 날씨 정보
async function refreshWeather() {
    document.getElementById('weatherInfo').innerHTML = '로딩 중...';
    try {
        const response = await fetch('/api/weather');
        const data = await response.json();
        document.getElementById('weatherInfo').innerHTML = formatWeatherInfo(data);
    } catch (e) {
        document.getElementById('weatherInfo').innerHTML = '오류: ' + e.message;
    }
}

function formatWeatherInfo(data) {
    if (data.error) return `<div class="status-box status-danger">❌ ${data.error}</div>`;
    
    const tempIcon = data.temperature < 0 ? '🥶' : data.temperature > 25 ? '🔥' : '🌡️';
    const weatherIcon = data.is_raining ? '🌧️' : data.is_snowing ? '❄️' : '☀️';
    
    return `
        <div class="status-box status-light">
            <strong>${weatherIcon} ${data.weather}</strong><br>
            ${tempIcon} 기온: ${data.temperature}°C | 💧 습도: ${data.humidity}%
        </div>
        <div class="status-box ${data.impact_factor > 1.2 ? 'status-warning' : 'status-success'}">
            <strong>📊 혼잡도 예상: ${data.impact_factor}배</strong><br>
            ${data.recommendation}
        </div>
    `;
}

// 교통 빅데이터
async function refreshTraffic() {
    document.getElementById('trafficInfo').innerHTML = '로딩 중...';
    try {
        const response = await fetch('/api/traffic');
        const data = await response.json();
        document.getElementById('trafficInfo').innerHTML = formatTrafficInfo(data);
    } catch (e) {
        document.getElementById('trafficInfo').innerHTML = '오류: ' + e.message;
    }
}

function formatTrafficInfo(data) {
    // timestamp 제외한 실제 데이터만 필터링
    const routes = Object.entries(data).filter(([key]) => key !== 'timestamp' && key !== 'error');
    
    if (routes.length === 0) return '<div class="status-box status-light">📍 배차간격 정보 없음</div>';
    
    let html = '<div class="grid-3">';
    
    for (const [route, info] of routes) {
        if (info.error) continue;
        
        const frequency = info.frequency_per_hour;
        const headway = info.estimated_headway;
        const nextBus = info.next_bus;
        
        // 배차간격에 따른 상태 클래스
        const statusClass = headway <= 8 ? 'status-success' : headway <= 12 ? 'status-warning' : 'status-danger';
        
        html += `
            <div class="status-box ${statusClass}">
                <div style="font-weight: bold;">${route}번</div>
                <div style="font-size: 0.9em; margin: 4px 0;">
                    🚌 다음: ${nextBus}분 후
                </div>
                <div style="font-size: 0.8em;">
                    배차: ${headway}분 | 시간당 ${frequency}대
                </div>
            </div>
        `;
    }
    
    html += '</div>';
    return html;
}

// 실시간 버스 정보
async function refreshBus() {
    document.getElementById('busInfo').innerHTML = '로딩 중...';
    try {
        const response = await fetch('/api/bus');
        const data = await response.json();
        document.getElementById('busInfo').innerHTML = formatBusInfo(data);
    } catch (e) {
        document.getElementById('busInfo').innerHTML = '오류: ' + e.message;
    }
}

function formatBusInfo(data) {
    if (data.error) return `<div class="bus-item"><div class="status-box status-danger">❌ ${data.error}</div></div>`;
    if (!data.buses || data.buses.length === 0) return '<div class="bus-item"><div class="status-box status-light">📍 버스 정보 없음</div></div>';
    
    let html = '<div class="bus-info">';
    
    // 전체 편안함 통계
    if (data.comfort_stats && !data.comfort_stats.error) {
        const stats = data.comfort_stats.comfort_distribution;
        html += `
            <div class="status-box status-info">
                <strong>📊 현재 시간대 편안함</strong><br>
                <small>매우편안 ${stats.very_comfortable}% | 편안 ${stats.comfortable}% | 혼잡 ${stats.crowded}% | 매우혼잡 ${stats.very_crowded}%</small><br>
                ${data.comfort_stats.recommendation}
            </div>
        `;
    }
    
    // 개별 버스 추천 통합
    const detailedRecs = data.detailed_recommendations?.buses || [];
    
    data.buses.forEach((bus, index) => {
        const getStatusClass = (passengers) => {
            if (passengers <= 25) return 'status-success';
            if (passengers <= 35) return 'status-warning';
            if (passengers <= 45) return 'status-danger';
            return 'status-danger';
        };
        
        const passengers1 = bus.bus1_passengers;
        const passengers2 = bus.bus2_passengers;
        
        // 해당 노선의 상세 추천 찾기
        const detailedRec = detailedRecs.find(rec => rec.route === bus.route);
        
        html += `
            <div class="bus-item">
                <div class="bus-route">${bus.route}번</div>
                <div class="bus-direction">→ ${bus.direction}</div>
                
                <div class="status-box ${getStatusClass(passengers1)}">
                    🚌 ${bus.arrival1}<br>
                    <strong>👥 ${passengers1}명 탑승</strong><br>
                    <small>${bus.bus1_comfort}</small>
                </div>
                
                <div class="status-box ${getStatusClass(passengers2)}">
                    🚌 ${bus.arrival2}<br>
                    <strong>👥 ${passengers2}명 탑승</strong><br>
                    <small>${bus.bus2_comfort}</small>
                </div>
                
                <div class="status-box status-light">
                    💡 ${detailedRec ? detailedRec.recommendation : bus.recommendation}
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

// 페이지 로드시 정보 가져오기
function refreshAll() {
    refreshQuietTimes();
    refreshBus();
    refreshPrediction();
    refreshWeather();
    refreshTraffic();
    document.getElementById('lastUpdate').textContent = 
        '마지막 업데이트: ' + new Date().toLocaleTimeString('ko-KR');
}

refreshAll();

// 60초마다 자동 새로고침
setInterval(refreshAll, 60000);

// 현재 요일 표시 (요소가 있으면 표시)
const days = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'];
const today = new Date().getDay();
const isWeekend = today === 0 || today === 6;
const currentDayEl = document.getElementById('currentDay');
if (currentDayEl) {
    currentDayEl.textContent = days[today] + (isWeekend ? ' (주말)' : ' (평일)');
}
