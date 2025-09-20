import eel
import requests
import json
import time
from datetime import datetime

# Web klasörünü ayarla
eel.init('web')

# Global değişkenler - API URL'nizi buraya yazın
api_url = "https://jsonplaceholder.typicode.com/posts/1"  # Buraya kendi API adresinizi yazın

# Test verisi - API'niz bu formatta veri döndürmeli
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
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()

        data = response.json()

        # Eğer API test API'si ise (JSONPlaceholder), test verisi döndür
        if "jsonplaceholder.typicode.com" in api_url:
            data = test_data

        # Veri tiplerini kontrol et ve düzelt
        processed_data = process_data_types(data)
        last_data = processed_data

        return {
            "status": "success",
            "data": processed_data,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"API hatası: {str(e)}"}

    except json.JSONDecodeError:
        return {"status": "error", "message": "API'den geçersiz JSON verisi geldi"}


@eel.expose
def process_data_types(data):
    """Veri tiplerini beklenen formatlara dönüştür"""
    processed = {}

    # Beklenen veri tipleri
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
                    # Boolean dönüşümü
                    if isinstance(value, bool):
                        processed[key] = value
                    elif isinstance(value, (int, float)):
                        processed[key] = bool(value)
                    elif isinstance(value, str):
                        processed[key] = value.lower() in ['true', '1', 'yes', 'on', 'açık']
                    else:
                        processed[key] = False
                elif expected_type == int:
                    # Integer dönüşümü
                    processed[key] = int(float(value))
                else:
                    processed[key] = expected_type(value)
            except (ValueError, TypeError):
                # Hatalı veri durumunda varsayılan değer
                if expected_type == bool:
                    processed[key] = False
                elif expected_type == int:
                    processed[key] = 0
        else:
            # Eksik veri durumunda varsayılan değer
            if expected_type == bool:
                processed[key] = False
            elif expected_type == int:
                processed[key] = 0

    return processed


@eel.expose
def get_current_api_url():
    """Mevcut API URL'sini döndür"""
    global api_url
    return api_url


if __name__ == '__main__':
    print("Dashboard başlatılıyor...")
    eel.start('index.html',
              size=(1200, 800),
              port=8080,
              host='localhost')