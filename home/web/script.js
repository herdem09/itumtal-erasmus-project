let refreshInterval = null;
let isAutoRefresh = true;

// Son bilinen durumlar (sunucudan gelenler ile güncellenir)
let state = {
    temperature: null,
    brightness: null,
    open_door: null,
    temperature_auto: null,
    brightness_auto: null,
    fan: null,
    window: null,
    heater: null,
    light: null,
    curtain: null,
};

// Kart ID eşleştirmeleri (UI'da kilit göstermek için)
const CARD_IDS = {
    fan: "fan_card",
    window: "window_card",
    heater: "heater_card",
    light: "light_card",
    curtain: "curtain_card",
};

// Birbirini kilitleyen kontroller
const INTERLOCKS = {
    temperature_auto: ["fan", "window", "heater"],
    brightness_auto: ["light", "curtain"],
};

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

// Kullanıcı etkile��imi ile tetiklenen toggle işlemleri
async function handleToggle(controlId, newState) {
    // Sunucudan gelen son duruma göre interlock kontrolü
    if (state.temperature_auto && ["fan", "window", "heater"].includes(controlId)) {
        // İzin verme ve geri al
        addLog("🔒 Oto Sıcaklık açıkken fan/pencere/ısıtıcı kullanılmaz", "error");
        setToggleUI(controlId, state[controlId]);
        return;
    }
    if (state.brightness_auto && ["light", "curtain"].includes(controlId)) {
        addLog("🔒 Oto Aydınlık açıkken perde/ışık kullanılmaz", "error");
        setToggleUI(controlId, state[controlId]);
        return;
    }

    // Değişim yoksa gönderme
    if (state.hasOwnProperty(controlId) && state[controlId] === newState) {
        addLog(`ℹ️ ${controlId} zaten ${newState ? "Açık" : "Kapalı"}`);
        return;
    }

    // UI'da yükleniyor hali
    setCardLoading(controlId, true);

    try {
        const result = await eel.send_control_command(controlId, newState)();
        if (result && result.status === "success") {
            // Lokal durumu güncelle
            state[controlId] = newState;
            setToggleUI(controlId, newState);
            addLog(`✅ ${controlId} ${newState ? "Açıldı" : "Kapandı"}`, "success");

            // Interlock gerektiriyorsa uygula
            if (controlId === "temperature_auto" || controlId === "brightness_auto") {
                applyInterlocks();
            }
        } else {
            const msg = result && result.message ? result.message : "Komut gönderilemedi";
            addLog(`❌ ${controlId}: ${msg}`, "error");
            // Eski haline dön
            setToggleUI(controlId, state[controlId]);
        }
    } catch (error) {
        addLog(`❌ ${controlId} komutu hata verdi: ${error}`, "error");
        // Eski haline dön
        setToggleUI(controlId, state[controlId]);
    } finally {
        setCardLoading(controlId, false);
    }
}

// Veriyi UI'da göster ve durumları uygula
function displayData(data, timestamp) {
    if (!data || typeof data !== "object") {
        addLog("❌ Geçersiz veri formatı", "error");
        return;
    }

    // Lokal state'i güncelle
    state = { ...state, ...data };

    // Sıcaklık ve hava durumu
    updateTemperature(data.temperature);
    updateWeatherStatus("brightness", data.brightness);

    // Toggle'ları ve metinleri güncelle
    setToggleUI("temperature_auto", data.temperature_auto, "Açık", "Kapalı");
    setToggleUI("brightness_auto", data.brightness_auto, "Açık", "Kapalı");

    setToggleUI("open_door", data.open_door, "Açık", "Kapalı");
    setToggleUI("window", data.window, "Açık", "Kapalı");
    setToggleUI("fan", data.fan, "Açık", "Kapalı");
    setToggleUI("heater", data.heater, "Açık", "Kapalı");
    setToggleUI("light", data.light, "Açık", "Kapalı");
    setToggleUI("curtain", data.curtain, "Açık", "Kapalı");

    // Interlock'ları uygula
    applyInterlocks();

    // Ham veri
    const raw = document.getElementById("rawData");
    if (raw) {
        raw.textContent = `Son Güncelleme: ${timestamp || "-"}\n\n${JSON.stringify(data, null, 2)}`;
    }
}

// Bir toggle'ın UI'ını güncelle (checkbox + durum metni)
function setToggleUI(controlId, value, trueText = "Açık", falseText = "Kapalı") {
    const input = document.getElementById(`${controlId}_toggle`);
    const status = document.getElementById(`${controlId}_status`);

    if (input) input.checked = !!value;
    if (status) status.textContent = value ? trueText : falseText;
}

// Bir toggle'ı kilitle/aç
function setToggleDisabled(controlId, disabled) {
    const input = document.getElementById(`${controlId}_toggle`);
    if (input) input.disabled = !!disabled;

    const cardId = CARD_IDS[controlId];
    if (cardId) {
        const card = document.getElementById(cardId);
        if (card) card.classList.toggle("disabled", !!disabled);
    }
}

// Interlock'ları UI'a uygula
function applyInterlocks() {
    const tempAuto = !!state.temperature_auto;
    const brightAuto = !!state.brightness_auto;

    INTERLOCKS.temperature_auto.forEach(id => setToggleDisabled(id, tempAuto));
    INTERLOCKS.brightness_auto.forEach(id => setToggleDisabled(id, brightAuto));
}

// Kartı "yükleniyor" durumuna al/çıkar
function setCardLoading(controlId, isLoading) {
    const cardId = CARD_IDS[controlId];
    if (!cardId) return;
    const card = document.getElementById(cardId);
    if (!card) return;

    card.classList.toggle("loading", !!isLoading);
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

// Özel hava durumu güncelleme fonksiyonu (aydınlık/karanlık)
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

// Durum göstergesini güncelle (üstteki küçük online/offline)
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
