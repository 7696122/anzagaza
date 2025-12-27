// 실제 서울시 OpenAPI 데이터 (2024년 11월)
const morning421 = {
    labels: ['06:00', '06:10', '06:20', '06:30', '06:40', '06:50', '07:00', '07:10', '07:20', '07:30', '07:40', '07:50', '08:00', '08:10', '08:20', '08:30', '08:40', '08:50', '09:00', '09:10', '09:20', '09:30', '09:40', '09:50'],
    datasets: [{
        label: '421번 10분당 승차 추정',
        data: [2, 2, 3, 3, 4, 4, 15, 16, 17, 18, 19, 20, 20, 20, 21, 22, 23, 24, 18, 18, 19, 20, 20, 21],
        backgroundColor: function(context) {
            const value = context.parsed.y;
            if (value < 5) return '#22c55e';
            if (value < 15) return '#eab308';
            if (value < 20) return '#f97316';
            return '#ef4444';
        },
        borderRadius: 4
    }]
};

const morning400 = {
    labels: ['06:00', '06:10', '06:20', '06:30', '06:40', '06:50', '07:00', '07:10', '07:20', '07:30', '07:40', '07:50', '08:00', '08:10', '08:20', '08:30', '08:40', '08:50', '09:00', '09:10', '09:20', '09:30', '09:40', '09:50'],
    datasets: [{
        label: '400번 10분당 승차 추정',
        data: [3, 3, 4, 5, 5, 6, 6, 7, 8, 9, 10, 11, 6, 6, 7, 8, 9, 10, 6, 6, 7, 8, 8, 9],
        backgroundColor: function(context) {
            const value = context.parsed.y;
            if (value < 5) return '#22c55e';
            if (value < 8) return '#eab308';
            if (value < 10) return '#f97316';
            return '#ef4444';
        },
        borderRadius: 4
    }]
};

const evening421 = {
    labels: ['17:00', '17:10', '17:20', '17:30', '17:40', '17:50', '18:00', '18:10', '18:20', '18:30', '18:40', '18:50', '19:00', '19:10', '19:20', '19:30', '19:40', '19:50', '20:00', '20:10', '20:20', '20:30', '20:40', '20:50'],
    datasets: [{
        label: '421번 10분당 하차 추정',
        data: [10, 11, 12, 13, 13, 14, 13, 14, 15, 16, 16, 15, 12, 12, 11, 11, 10, 10, 8, 8, 7, 7, 6, 6],
        backgroundColor: function(context) {
            const value = context.parsed.y;
            if (value < 8) return '#22c55e';
            if (value < 12) return '#eab308';
            if (value < 15) return '#f97316';
            return '#ef4444';
        },
        borderRadius: 4
    }]
};

const evening400 = {
    labels: ['17:00', '17:10', '17:20', '17:30', '17:40', '17:50', '18:00', '18:10', '18:20', '18:30', '18:40', '18:50', '19:00', '19:10', '19:20', '19:30', '19:40', '19:50', '20:00', '20:10', '20:20', '20:30', '20:40', '20:50'],
    datasets: [{
        label: '400번 10분당 하차 추정',
        data: [3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, 2, 2, 2, 2, 1],
        backgroundColor: function(context) {
            const value = context.parsed.y;
            if (value < 3) return '#22c55e';
            if (value < 4) return '#eab308';
            if (value < 5) return '#f97316';
            return '#ef4444';
        },
        borderRadius: 4
    }]
};

const opts = { 
    responsive: true, 
    plugins: { legend: { display: false } }, 
    scales: { 
        y: { beginAtZero: true },
        x: { 
            ticks: { 
                maxTicksLimit: 12,
                callback: function(value, index) {
                    return index % 2 === 0 ? this.getLabelForValue(value) : '';
                }
            }
        }
    }
};

new Chart(document.getElementById('morningChart421'), { type: 'bar', data: morning421, options: opts });
new Chart(document.getElementById('morningChart400'), { type: 'bar', data: morning400, options: opts });
new Chart(document.getElementById('eveningChart421'), { type: 'bar', data: evening421, options: opts });
new Chart(document.getElementById('eveningChart400'), { type: 'bar', data: evening400, options: opts });

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
    if (!data.buses) return '<div class="bus-item">📍 버스 정보 없음</div>';
    
    let html = '<div class="bus-info">';
    data.buses.forEach(bus => {
        const congestionIcon = ['🟢', '🟡', '🟠', '🔴', '⚫'][bus.congestion1] || '❓';
        const congestionIcon2 = ['🟢', '🟡', '🟠', '🔴', '⚫'][bus.congestion2] || '❓';
        html += `
            <div class="bus-item">
                <div class="bus-route">${bus.route}번</div>
                <div class="bus-direction">→ ${bus.direction}</div>
                <div class="bus-arrival">🚌 ${bus.arrival1} ${congestionIcon}</div>
                <div class="bus-arrival">🚌 ${bus.arrival2} ${congestionIcon2}</div>
            </div>
        `;
    });
    html += '</div>';
    return html;
}

// 페이지 로드시 정보 가져오기
refreshBus();
refreshWeather();

// 현재 요일 표시
const days = ['일요일', '월요일', '화요일', '수요일', '목요일', '금요일', '토요일'];
const today = new Date().getDay();
const isWeekend = today === 0 || today === 6;
document.getElementById('currentDay').textContent = days[today] + (isWeekend ? ' (주말)' : ' (평일)');
