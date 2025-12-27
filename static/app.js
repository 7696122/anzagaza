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
        
        document.getElementById('mainRecommendation').innerHTML = formatMainRecommendation(data.simple_recommendation);
        document.getElementById('quietTimesInfo').innerHTML = formatQuietTimesInfo(data.detailed_recommendations);
    } catch (e) {
        document.getElementById('mainRecommendation').innerHTML = '오류: ' + e.message;
        document.getElementById('quietTimesInfo').innerHTML = '오류: ' + e.message;
    }
}

function formatMainRecommendation(simple) {
    return `
        <div style="background: ${simple.color}; color: white; padding: 16px; border-radius: 12px; text-align: center;">
            <strong style="font-size: 1.4em;">${simple.action}</strong><br>
            <span style="font-size: 1.1em;">${simple.reason}</span>
        </div>
    `;
}

function formatQuietTimesInfo(rec) {
    let html = `
        <div style="display: grid; gap: 16px;">
            <div style="background: ${rec.current_status.color}; color: white; padding: 12px; border-radius: 8px;">
                <strong>📍 현재: ${rec.current_status.status}</strong><br>
                ${rec.current_status.reason} (${rec.current_status.passengers})
            </div>
            
            <div style="background: #f0f9ff; padding: 12px; border-radius: 8px;">
                <strong>⏰ 다음 한적한 시간: ${rec.next_quiet_time.time}</strong><br>
                ${rec.next_quiet_time.reason}`;
    
    if (rec.next_quiet_time.wait_minutes > 0) {
        html += `<br><small>대기시간: ${rec.next_quiet_time.wait_minutes}분</small>`;
    }
    html += '</div>';
    
    html += '<div><strong>✅ 오늘의 최적 시간:</strong><br>';
    rec.best_times_today.forEach(time => {
        const color = time.status === '매우한적' ? '#22c55e' : time.status === '한적' ? '#eab308' : '#f97316';
        html += `<div style="margin: 4px 0; padding: 8px; background: ${color}; color: white; border-radius: 6px; font-size: 0.9em;">
            ${time.time}: ${time.status} (${time.passengers})
        </div>`;
    });
    html += '</div>';
    
    html += '<div><strong>❌ 피해야 할 시간:</strong><br>';
    rec.avoid_times.forEach(avoid => {
        html += `<div style="margin: 4px 0; padding: 8px; background: #ef4444; color: white; border-radius: 6px; font-size: 0.9em;">
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
    if (data.error) return `❌ ${data.error}`;
    
    const tempIcon = data.temperature < 0 ? '🥶' : data.temperature > 25 ? '🔥' : '🌡️';
    const weatherIcon = data.is_raining ? '🌧️' : data.is_snowing ? '❄️' : '☀️';
    
    return `
        <div style="display: grid; gap: 8px;">
            <div><strong>${weatherIcon} ${data.weather}</strong></div>
            <div>${tempIcon} 기온: ${data.temperature}°C | 💧 습도: ${data.humidity}%</div>
            <div style="background: ${data.impact_factor > 1.2 ? '#fef3c7' : '#dcfce7'}; padding: 12px; border-radius: 8px; margin-top: 8px;">
                <strong>📊 혼잡도 예상: ${data.impact_factor}배</strong><br>
                ${data.recommendation}
            </div>
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
    if (Object.keys(data).length === 0) return '📍 배차간격 정보 없음';
    
    let html = '<div style="display: grid; gap: 12px;">';
    
    for (const [route, info] of Object.entries(data)) {
        if (info.error) continue;
        
        const frequency = info.frequency_per_hour;
        const headway = info.estimated_headway;
        const nextBus = info.next_bus;
        
        // 배차간격에 따른 색상
        const headwayColor = headway <= 8 ? '#22c55e' : headway <= 12 ? '#eab308' : '#ef4444';
        
        html += `
            <div style="border: 1px solid #e5e7eb; border-radius: 8px; padding: 12px; background: #f9fafb;">
                <div style="font-weight: bold; color: #1f2937;">${route}번</div>
                <div style="font-size: 0.9em; color: #6b7280; margin: 4px 0;">
                    🚌 다음 버스: ${nextBus}분 후
                </div>
                <div style="background: ${headwayColor}; color: white; padding: 4px 8px; border-radius: 4px; font-size: 0.8em; display: inline-block;">
                    배차간격: ${headway}분 | 시간당 ${frequency}대
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
    if (data.error) return `<div class="bus-item">❌ ${data.error}</div>`;
    if (!data.buses || data.buses.length === 0) return '<div class="bus-item">📍 버스 정보 없음</div>';
    
    let html = '<div class="bus-info">';
    
    // 전체 편안함 통계
    if (data.comfort_stats && !data.comfort_stats.error) {
        const stats = data.comfort_stats.comfort_distribution;
        html += `
            <div style="background: #f0f9ff; padding: 12px; border-radius: 8px; margin-bottom: 12px;">
                <strong>📊 현재 시간대 편안함</strong><br>
                <small>매우편안 ${stats.very_comfortable}% | 편안 ${stats.comfortable}% | 혼잡 ${stats.crowded}% | 매우혼잡 ${stats.very_crowded}%</small><br>
                ${data.comfort_stats.recommendation}
            </div>
        `;
    }
    
    data.buses.forEach(bus => {
        const getOccupancyColor = (passengers) => {
            if (passengers <= 20) return '#22c55e';
            if (passengers <= 40) return '#eab308';
            if (passengers <= 60) return '#f97316';
            return '#ef4444';
        };
        
        const passengers1 = bus.bus1_passengers;
        const passengers2 = bus.bus2_passengers;
        
        html += `
            <div class="bus-item">
                <div class="bus-route">${bus.route}번</div>
                <div class="bus-direction">→ ${bus.direction}</div>
                
                <div style="margin: 8px 0; padding: 8px; background: ${getOccupancyColor(passengers1)}; color: white; border-radius: 6px;">
                    🚌 ${bus.arrival1}<br>
                    <strong>👥 ${passengers1}명 탑승 (${bus.bus1_occupancy_rate}%)</strong><br>
                    <small>${bus.bus1_comfort}</small>
                </div>
                
                <div style="margin: 8px 0; padding: 8px; background: ${getOccupancyColor(passengers2)}; color: white; border-radius: 6px;">
                    🚌 ${bus.arrival2}<br>
                    <strong>👥 ${passengers2}명 탑승 (${bus.bus2_occupancy_rate}%)</strong><br>
                    <small>${bus.bus2_comfort}</small>
                </div>
                
                <div style="background: #f9fafb; padding: 8px; border-radius: 6px; font-size: 0.9em;">
                    💡 ${bus.recommendation}
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    return html;
}

// 페이지 로드시 정보 가져오기
refreshQuietTimes();
refreshBus();
refreshPrediction();
refreshWeather();
refreshTraffic();

// 현재 요일 표시
const days = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'];
const today = new Date().getDay();
const isWeekend = today === 0 || today === 6;
document.getElementById('currentDay').textContent = days[today] + (isWeekend ? ' (주말)' : ' (평일)');
