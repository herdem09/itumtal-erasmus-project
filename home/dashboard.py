import eel
import requests
import json
import logging
from datetime import datetime

# Logging ayarları
logging.basicConfig(
    level=logging.INFO,  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Web klasörünü ayarla
eel.init('web')

# Global değişkenler
api_url = "http://192.168.1.200:5000/api/data"
control_api_url = "https://jsonplaceholder.typicode.com/posts"

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


@eel.expose
def get_api_data():
    """API'den veri al"""
    global last_data

    try:
        logging.info(f"API'den veri çekiliyor: {api_url}")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if "jsonplaceholder.typicode.com" in api_url:
            logging.debug("Test API kullanılıyor, sahte veriler döndürülecek.")
            data = test_data

        processed_data = process_data_types(data)
        last_data = processed_data

        # Gelen veriyi terminale yaz
        logging.info(f"Gelen veri: {processed_data}")

        return {
            "status": "success",
            "data": processed_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"API hatası: {str(e)}")
        return {"status": "error", "message": f"API hatası: {str(e)}"}

    except json.JSONDecodeError:
        logging.error("API'den geçersiz JSON verisi geldi")
        return {"status": "error", "message": "API'den geçersiz JSON verisi geldi"}


@eel.expose
def send_control_command(control_id, value):
    """Kontrol komutunu API'ye gönder"""
    global control_api_url, test_data

    try:
        payload = {
            "control": control_id,
            "value": value,
            "timestamp": datetime.now().isoformat()
        }

        logging.info(f"Kontrol komutu gönderiliyor: {payload}")
        response = requests.post(control_api_url, json=payload, timeout=10)
        response.raise_for_status()

        if "jsonplaceholder.typicode.com" in control_api_url:
            test_data[control_id] = value
            logging.debug(f"Test modu güncellemesi: {control_id} = {value}")

        logging.info(f"Kontrol komutu sonucu: {control_id} başarıyla {value} olarak ayarlandı")

        return {
            "status": "success",
            "message": f"{control_id} başarıyla {value} olarak ayarlandı",
            "data": payload
        }

    except requests.exceptions.RequestException as e:
        logging.error(f"Kontrol API hatası: {str(e)}")
        return {"status": "error", "message": f"Kontrol API hatası: {str(e)}"}

    except Exception as e:
        logging.critical(f"Beklenmeyen hata: {str(e)}")
        return {"status": "error", "message": f"Beklenmeyen hata: {str(e)}"}


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

    eel.start('index.html',
              size=(1200, 800),
              port=8080,
              host='localhost')
