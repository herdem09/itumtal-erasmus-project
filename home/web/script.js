let refreshInterval = null;
let isAutoRefresh = true;
let controlStates = {}; // Kontrol durumlarını saklayacak

// Sayfa yüklendiğinde otomatik veri çekmeyi başlat
window.onload = async function() {
    addLog('Dashboard başlatıldı');

    // İlk veri çekme denemesi
    setTimeout(fetchData, 500);

    // 3 saniyede bir otomatik veri çekme
    startAutoRefresh();
};

// Kontrol toggle fonksiyonu
async function toggleControl(controlId, newState) {
    const card = document.getElementById(`${controlId}_toggle`).closest('.control-card');
    const statusElement = document.getElementById(`${controlId}_status`);

    // Loading animasyonu başlat
    card.classList.add('loading');

    try {
        // API'ye değişikliği gönder
        const result = await eel.send_control_command(controlId, newState)();

        if (result.status === 'success') {
            // Başarılı ise durumu güncelle
            controlStates[controlId] = newState;
            updateControlDisplay(controlId, newState);
            updateDependentControls();
            addLog(`✅ ${controlId}: ${newState ? 'Açıldı' : 'Kapandı'}`, 'success');
        } else {
            // Hata durumunda toggle'ı geri çevir
            document.getElementById(`// Boolean durumları güncelle
function updateBooleanStatus(elementId, value, trueText = 'Açık', falseText = 'Kapalı') {
    const statusElement = document.getElementById(elementId);
    const card = statusElement.closest('.card');
    const dot = statusElement.querySelector('.status-dot');
    const span = statusElement.querySelector('span:last-child');

    if (value !== undefined && value !== null) {
        if (value === true || value === 'true' || value === 1) {
            dot.className = 'status-dot online';
            span.textContent = trueText;
            card.classList.remove('inactive');
            card.classList.add('active');
        } else {
            dot.className = 'status-dot offline';
            span.textContent = falseText;
            card.classList.remove('active');
            card.classList.add('inactive');
        }
    } else {
        dot.className = 'status-dot warning';
        span.textContent = 'Veri yok';
        card.classList.remove('active', // Veri al
async function fetchData() {
    try {
        const result = await eel.get_api_data()();

        if (result.status === 'success') {
            displayData(resultlet refreshInterval = null;
let isAutoRefresh = true; // Otomatik başlat

// Sayfa yüklendiğinde otomatik veri çekmeyi başlat
window.onload = async function() {
    addLog('Dashboard başlatıldı');

    // İlk veri çekme denemesi
    setTimeout(fetchData, 500);

    // 3 saniyede bir otomatik veri çekme
    startAutoRefresh();
};

// Veri al
async function fetchData() {
    try {
        const result = await eel.get_api_data()();

        if (result.status === 'success') {
            displayData(result.data, result.timestamp);
            updateStatus('online', 'Güncellendi');
            addLog('✅ Veri başarıyla alındı', 'success');
        } else {
            addLog(`❌ ${result.message}`, 'error');
            updateStatus('offline', 'Hata');
        }
    } catch (error) {
        addLog(`❌ Veri alınırken hata: ${error}`, 'error');
        updateStatus('offline', 'Hata');
    }
}

// Bağlantıyı test et (artık kullanılmıyor ama uyumluluk için bırakıldı)
async function testConnection() {
    await fetchData();
}

// Otomatik yenilemeyi başlat (3 saniyede bir)
function startAutoRefresh() {
    if (isAutoRefresh && refreshInterval) {
        return; // Zaten aktif
    }

    const interval = 3000; // 3 saniye

    refreshInterval = setInterval(fetchData, interval);
    isAutoRefresh = true;

    addLog(`🔄 Otomatik yenileme başlatıldı (3s)`, 'success');
    updateStatus('online', 'Otomatik yenileme aktif');
}

// Otomatik yenilemeyi durdur
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
        isAutoRefresh = false;

        addLog('⏹️ Otomatik yenileme durduruldu', 'success');
        updateStatus('online', 'Manuel mod');
    }
}

// Veriyi göster
function displayData(data, timestamp) {
    // Özel değişkenleri işle
    updateTemperature(data.temperature);
    updateWeatherStatus('brightness', data.brightness); // Özel hava durumu fonksiyonu
    updateBooleanStatus('open_door', data.open_door, 'Açık', 'Kapalı');
    updateBooleanStatus('temperature_auto', data.temperature_auto);
    updateBooleanStatus('brightness_auto', data.brightness_auto);
    updateBooleanStatus('fan', data.fan);
    updateBooleanStatus('window', data.window, 'Açık', 'Kapalı');
    updateBooleanStatus('heater', data.heater);
    updateBooleanStatus('light', data.light);
    updateBooleanStatus('curtain', data.curtain, 'Açık', 'Kapalı');

    // Ham veri
    document.getElementById('rawData').textContent =
        `Son Güncelleme: ${timestamp}\n\n${JSON.stringify(data, null, 2)}`;
}

// Sıcaklık değerini güncelle
function updateTemperature(temperature) {
    const tempElement = document.getElementById('temperature');
    const tempCard = tempElement.closest('.card');

    if (temperature !== undefined && temperature !== null) {
        tempElement.textContent = temperature;

        // Sıcaklığa göre renk değiştir
        tempCard.classList.remove('hot', 'cold', 'normal');
        if (temperature > 25) {
            tempCard.classList.add('hot');
        } else if (temperature < 18) {
            tempCard.classList.add('cold');
        } else {
            tempCard.classList.add('normal');
        }
    } else {
        tempElement.textContent = '-';
        tempCard.classList.remove('hot', 'cold', 'normal');
    }
}

// Boolean durumları güncelle
function updateBooleanStatus(elementId, value, trueText = 'Açık', falseText = 'Kapalı') {
    const statusElement = document.getElementById(elementId);
    const card = statusElement.closest('.card');
    const dot = statusElement.querySelector('.status-dot');
    const span = statusElement.querySelector('span:last-child');

    if (value !== undefined && value !== null) {
        if (value === true || value === 'true' || value === 1) {
            dot.className = 'status-dot online';
            span.textContent = trueText;
            card.classList.remove('inactive');
            card.classList.add('active');
        } else {
            dot.className = 'status-dot offline';
            span.textContent = falseText;
            card.classList.remove('active');
            card.classList.add('inactive');
        }
    } else {
        dot.className = 'status-dot warning';
        span.textContent = 'Veri yok';
        card.classList.remove('active', 'inactive');
    }
}

// Özel hava durumu güncelleme fonksiyonu
function updateWeatherStatus(elementId, value) {
    const statusElement = document.getElementById(elementId);
    const card = statusElement.closest('.card');
    const dot = statusElement.querySelector('.status-dot');
    const span = statusElement.querySelector('span:last-child');

    if (value !== undefined && value !== null) {
        if (value === true || value === 'true' || value === 1) {
            dot.className = 'status-dot online';
            span.textContent = 'Aydınlık';
            card.classList.remove('inactive');
            card.classList.add('active');
        } else {
            dot.className = 'status-dot offline';
            span.textContent = 'Karanlık';
            card.classList.remove('active');
            card.classList.add('inactive');
        }
    } else {
        dot.className = 'status-dot warning';
        span.textContent = 'Veri yok';
        card.classList.remove('active', 'inactive');
    }
}

// Değeri formatla (artık kullanılmıyor ama uyumluluk için bırakıldı)
function formatValue(value) {
    if (typeof value === 'number') {
        if (Number.isInteger(value)) {
            return value.toLocaleString();
        } else {
            return value.toFixed(2);
        }
    } else if (typeof value === 'string') {
        return value.length > 20 ? value.substring(0, 20) + '...' : value;
    } else if (typeof value === 'object' && value !== null) {
        return 'Object';
    } else {
        return String(value);
    }
}

// Durum göstergesini güncelle
function updateStatus(status, text) {
    const statusElement = document.getElementById('status');
    const dot = statusElement.querySelector('.status-dot');
    const span = statusElement.querySelector('span:last-child');

    dot.className = `status-dot ${status}`;
    span.textContent = text;
}

// Log ekle
function addLog(message, type = 'info') {
    const logArea = document.getElementById('logArea');
    const timestamp = new Date().toLocaleTimeString();

    const logEntry = document.createElement('div');
    logEntry.className = `log-entry log-${type}`;
    logEntry.textContent = `[${timestamp}] ${message}`;

    logArea.appendChild(logEntry);
    logArea.scrollTop = logArea.scrollHeight;

    // Maximum 100 log tutmak için eski logları sil
    const logs = logArea.querySelectorAll('.log-entry');
    if (logs.length > 100) {
        logs[0].remove();
    }
}

// Sayfa kapatılırken otomatik yenilemeyi durdur
window.addEventListener('beforeunload', function() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});