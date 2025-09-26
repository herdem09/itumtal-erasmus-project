import eel
import requests
import json
import logging
import os
from datetime import datetime

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Web klasörünü ayarla
WEB_DIR = os.path.join(os.path.dirname(__file__), 'web')
eel.init(WEB_DIR)

# Global değişkenler
api_url = "http://127.0.0.1:5001/get-data"
control_api_url = "http://127.0.0.1:5001/set-data"

# Test verisi
test_data = {
    "temperature": 23,
    "brightness": True,
    "open_door": False,
    "temperature_auto": True,
    "brightness_auto": False,
    "fan": True,
    "window": False,
    "heater": False,
    "light": True,
    "curtain": False
}

last_data = {}

# Authentication API configuration
AUTH_API_BASE_URL = "http://127.0.0.1:5000"  # api/api.py'nin çalıştığı port
confirmed_code_token = None


@eel.expose
def password_confirmation_api(name, password):
    """Kullanıcı adı/parola ile /password-confirmation çağrısı yapar."""
    try:
        payload = {"name": name, "password": password}
        logging.info(f"/password-confirmation istek: {payload}")
        resp = requests.get(f"{AUTH_API_BASE_URL}/password-confirmation", json=payload, timeout=10)
        try:
            data = resp.json()
        except Exception:
            return {"status": "error", "message": "Geçersiz API yanıtı"}

        if resp.status_code == 200 and data.get("success") == "successful" and "random_code" in data:
            logging.info("Parola doğrulama başarılı, random_code alındı")
            return {"status": "success", "random_code": data["random_code"]}
        else:
            msg = data.get("error") or data.get("message") or f"HTTP {resp.status_code}"
            logging.warning(f"Parola doğrulama başarısız: {msg}")
            return {"status": "error", "message": msg}
    except requests.exceptions.RequestException as e:
        logging.error(f"Parola doğrulama isteği hatası: {e}")
        return {"status": "error", "message": str(e)}


@eel.expose
def request_email_api(random_code):
    """Random code ile /email çağrısı yapar, doğrulama bağlantısını e-posta ile gönderir."""
    try:
        payload = {"random_code": random_code}
        logging.info(f"/email istek: {payload}")
        resp = requests.get(f"{AUTH_API_BASE_URL}/email", json=payload, timeout=10)
        try:
            data = resp.json()
        except Exception:
            return {"status": "error", "message": "Geçersiz API yanıtı"}

        if resp.status_code == 200 and data.get("success") == "successful":
            logging.info("E-posta gönderimi başarılı")
            return {"status": "success", "message": "E-posta gönderildi"}
        else:
            msg = data.get("error") or data.get("message") or f"HTTP {resp.status_code}"
            logging.warning(f"E-posta gönderimi başarısız: {msg}")
            return {"status": "error", "message": msg}
    except requests.exceptions.RequestException as e:
        logging.error(f"E-posta isteği hatası: {e}")
        return {"status": "error", "message": str(e)}


@eel.expose
def save_confirmed_code(code):
    """Kullanıcının e-posta ile aldığı confirmed_code'u saklar."""
    global confirmed_code_token
    confirmed_code_token = code
    logging.info("Confirmed code kaydedildi")
    return {"status": "success"}


@eel.expose
def get_api_data():
    """API'den veri al (fallback: /get-data -> /get_data)"""
    global last_data, api_url

    last_error = None
    for url in [api_url, "http://127.0.0.1:5000/get_data"]:
        try:
            logging.info(f"API'den veri çekiliyor: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            data = response.json()

            if "jsonplaceholder.typicode.com" in url:
                logging.debug("Test API kullanılıyor, sahte veriler döndürülecek.")
                data = test_data

            processed_data = process_data_types(data)
            last_data = processed_data

            # Kullanılan URL'yi kalıcı yap
            if api_url != url:
                logging.info(f"API URL fallback kullanıldı: {url}")
                api_url = url

            logging.info(f"Gelen veri: {processed_data}")
            return {
                "status": "success",
                "data": processed_data,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except requests.exceptions.RequestException as e:
            last_error = e
            continue
        except json.JSONDecodeError:
            logging.error("API'den geçersiz JSON verisi geldi")
            return {"status": "error", "message": "API'den geçersiz JSON verisi geldi"}

    logging.error(f"API hatası: {str(last_error)}")
    return {"status": "error", "message": f"API hatası: {str(last_error)}"}


@eel.expose
def send_control_command(control_id, value):
    """Kontrol komutunu API'ye gönder (fallback: /set-data -> /set_data)"""
    global control_api_url, test_data

    payload = {
        "control": control_id,
        "value": value,
        "timestamp": datetime.now().isoformat()
    }

    last_error = None
    for url in [control_api_url, "http://127.0.0.1:5000/set_data"]:
        try:
            logging.info(f"Kontrol komutu gönderiliyor ({url}): {payload}")
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()

            if "jsonplaceholder.typicode.com" in url:
                test_data[control_id] = value
                logging.debug(f"Test modu güncellemesi: {control_id} = {value}")

            # Kullanılan URL'yi kalıcı yap
            if control_api_url != url:
                logging.info(f"Kontrol API URL fallback kullanıldı: {url}")
                control_api_url = url

            logging.info(f"Kontrol komutu sonucu: {control_id} başarıyla {value} olarak ayarlandı")
            return {
                "status": "success",
                "message": f"{control_id} başarıyla {value} olarak ayarlandı",
                "data": payload
            }
        except requests.exceptions.RequestException as e:
            last_error = e
            continue
        except Exception as e:
            logging.critical(f"Beklenmeyen hata: {str(e)}")
            return {"status": "error", "message": f"Beklenmeyen hata: {str(e)}"}

    logging.error(f"Kontrol API hatası: {str(last_error)}")
    return {"status": "error", "message": f"Kontrol API hatası: {str(last_error)}"}


@eel.expose
def process_data_types(data):
    """Veri tiplerini beklenen formatlara dönüştür"""
    processed = {}

    expected_types = {
        "temperature": int,
        "brightness": bool,
        "open_door": bool,
        "temperature_auto": bool,
        "brightness_auto": bool,
        "fan": bool,
        "window": bool,
        "heater": bool,
        "light": bool,
        "curtain": bool
    }

    for key, expected_type in expected_types.items():
        if key in data:
            value = data[key]
            try:
                if expected_type == bool:
                    if isinstance(value, bool):
                        processed[key] = value
                    elif isinstance(value, (int, float)):
                        processed[key] = bool(value)
                    elif isinstance(value, str):
                        processed[key] = value.lower() in ['true', '1', 'yes', 'on', 'açık']
                    else:
                        processed[key] = False
                elif expected_type == int:
                    processed[key] = int(float(value))
                else:
                    processed[key] = expected_type(value)
            except (ValueError, TypeError):
                processed[key] = False if expected_type == bool else 0
                logging.warning(f"Tip dönüşüm hatası: {key} için varsayılan değer atandı")
        else:
            processed[key] = False if expected_type == bool else 0
            logging.warning(f"Veri eksik: {key}, varsayılan değer atandı")

    logging.debug(f"İşlenen veri: {processed}")
    return processed


@eel.expose
def get_current_api_url():
    """Mevcut API URL'sini döndür"""
    logging.info(f"Mevcut API URL'si istendi: {api_url}")
    return api_url


if __name__ == '__main__':
    logging.info("Smart Home Dashboard başlatılıyor...")
    logging.info(f"Veri API: {api_url}")
    logging.info(f"Kontrol API: {control_api_url}")
    logging.info("Test modu aktif - gerçek API'lerinizi main.py'da ayarlayın")

    eel.start('login.html',
              size=(1200, 800),
              port=8080,
              host='localhost')
