"use strict";

let refreshInterval = null;
let isAutoRefresh = true;
let controlStates = {}; // (gelecekteki) kontrol durumları için

// Sayfa yüklendiğinde otomatik veri çekmeyi başlat
window.onload = async function () {
    addLog("Dashboard başlatıldı");

    // İlk veri çekme denemesi
    setTimeout(fetchData, 500);

    // 3 saniyede bir otomatik veri çekme
    startAutoRefresh();
};

// Veri al
async function fetchData() {
    try {
        const result = await eel.get_api_data()();

        if (result && result.status === "success") {
            displayData(result.data, result.timestamp);
            updateStatus("online", "Güncellendi");
            addLog("✅ Veri başarıyla alındı", "success");
        } else {
            const msg = result && result.message ? result.message : "Bilinmeyen hata";
            addLog(`❌ ${msg}`, "error");
            updateStatus("offline", "Hata");
        }
    } catch (error) {
        addLog(`❌ Veri alınırken hata: ${error}`, "error");
        updateStatus("offline", "Hata");
    }
}

// Otomatik yenilemeyi başlat (3 saniyede bir)
function startAutoRefresh() {
    if (isAutoRefresh && refreshInterval) {
        return; // Zaten aktif
    }

    const interval = 3000; // 3 saniye

    refreshInterval = setInterval(fetchData, interval);
    isAutoRefresh = true;

    addLog(`🔄 Otomatik yenileme başlatıldı (3s)`, "success");
    updateStatus("online", "Otomatik yenileme aktif");
}

// Otomatik yenilemeyi durdur
function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
        refreshInterval = null;
        isAutoRefresh = false;

        addLog("⏹️ Otomatik yenileme durduruldu", "success");
        updateStatus("online", "Manuel mod");
    }
}

// (Opsiyonel) kontrol gönderme — şimdilik UI'da kullanılmıyor ama hatasız dursun
async function toggleControl(controlId, newState) {
    try {
        const result = await eel.send_control_command(controlId, newState)();
        if (result && result.status === "success") {
            controlStates[controlId] = newState;
            addLog(`✅ ${controlId}: ${newState ? "Açıldı" : "Kapandı"}`, "success");
        } else {
            const msg = result && result.message ? result.message : "Komut gönderilemedi";
            addLog(`❌ ${controlId}: ${msg}` , "error");
        }
    } catch (error) {
        addLog(`❌ ${controlId} komutu hata verdi: ${error}`, "error");
    }
}

// Veriyi göster
function displayData(data, timestamp) {
    if (!data || typeof data !== "object") {
        addLog("❌ Geçersiz veri formatı", "error");
        return;
    }

    // Özel değişkenleri işle
    updateTemperature(data.temperature);
    updateWeatherStatus("brightness", data.brightness); // Özel hava durumu fonksiyonu
    updateBooleanStatus("open_door", data.open_door, "Açık", "Kapalı");
    updateBooleanStatus("temperature_auto", data.temperature_auto);
    updateBooleanStatus("brightness_auto", data.brightness_auto);
    updateBooleanStatus("fan", data.fan);
    updateBooleanStatus("window", data.window, "Açık", "Kapalı");
    updateBooleanStatus("heater", data.heater);
    updateBooleanStatus("light", data.light);
    updateBooleanStatus("curtain", data.curtain, "Açık", "Kapalı");

    // Ham veri
    const raw = document.getElementById("rawData");
    if (raw) {
        raw.textContent = `Son Güncelleme: ${timestamp || "-"}\n\n${JSON.stringify(data, null, 2)}`;
    }
}

// Sıcaklık değerini güncelle
function updateTemperature(temperature) {
    const tempElement = document.getElementById("temperature");
    if (!tempElement) return;

    const tempCard = tempElement.closest(".card");

    if (temperature !== undefined && temperature !== null) {
        tempElement.textContent = temperature;

        // Sıcaklığa göre renk değiştir
        tempCard && tempCard.classList.remove("hot", "cold", "normal");
        if (tempCard) {
            if (Number(temperature) > 25) {
                tempCard.classList.add("hot");
            } else if (Number(temperature) < 18) {
                tempCard.classList.add("cold");
            } else {
                tempCard.classList.add("normal");
            }
        }
    } else {
        tempElement.textContent = "-";
        tempCard && tempCard.classList.remove("hot", "cold", "normal");
    }
}

// Boolean durumları güncelle
function updateBooleanStatus(elementId, value, trueText = "Açık", falseText = "Kapalı") {
    const statusElement = document.getElementById(elementId);
    if (!statusElement) return;

    const card = statusElement.closest(".card");
    const dot = statusElement.querySelector(".status-dot");
    const span = statusElement.querySelector("span:last-child");

    if (value !== undefined && value !== null) {
        if (value === true || value === "true" || value === 1) {
            dot && (dot.className = "status-dot online");
            span && (span.textContent = trueText);
            card && card.classList.remove("inactive");
            card && card.classList.add("active");
        } else {
            dot && (dot.className = "status-dot offline");
            span && (span.textContent = falseText);
            card && card.classList.remove("active");
            card && card.classList.add("inactive");
        }
    } else {
        dot && (dot.className = "status-dot warning");
        span && (span.textContent = "Veri yok");
        card && card.classList.remove("active", "inactive");
    }
}

// Özel hava durumu güncelleme fonksiyonu
function updateWeatherStatus(elementId, value) {
    const statusElement = document.getElementById(elementId);
    if (!statusElement) return;

    const card = statusElement.closest(".card");
    const dot = statusElement.querySelector(".status-dot");
    const span = statusElement.querySelector("span:last-child");

    if (value !== undefined && value !== null) {
        if (value === true || value === "true" || value === 1) {
            dot && (dot.className = "status-dot online");
            span && (span.textContent = "Aydınlık");
            card && card.classList.remove("inactive");
            card && card.classList.add("active");
        } else {
            dot && (dot.className = "status-dot offline");
            span && (span.textContent = "Karanlık");
            card && card.classList.remove("active");
            card && card.classList.add("inactive");
        }
    } else {
        dot && (dot.className = "status-dot warning");
        span && (span.textContent = "Veri yok");
        card && card.classList.remove("active", "inactive");
    }
}

// Durum göstergesini güncelle
function updateStatus(status, text) {
    const statusElement = document.getElementById("status");
    if (!statusElement) return;
    const dot = statusElement.querySelector(".status-dot");
    const span = statusElement.querySelector("span:last-child");

    if (dot) dot.className = `status-dot ${status}`;
    if (span) span.textContent = text;
}

// Log ekle
function addLog(message, type = "info") {
    const logArea = document.getElementById("logArea");
    if (!logArea) return;

    const timestamp = new Date().toLocaleTimeString();

    const logEntry = document.createElement("div");
    logEntry.className = `log-entry log-${type}`;
    logEntry.textContent = `[${timestamp}] ${message}`;

    logArea.appendChild(logEntry);
    logArea.scrollTop = logArea.scrollHeight;

    // Maximum 100 log tutmak için eski logları sil
    const logs = logArea.querySelectorAll(".log-entry");
    if (logs.length > 100) {
        logs[0].remove();
    }
}

// Sayfa kapatılırken otomatik yenilemeyi durdur
window.addEventListener("beforeunload", function () {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});
