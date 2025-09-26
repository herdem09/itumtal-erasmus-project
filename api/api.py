from flask import Flask, request, jsonify, send_file
import pandas as pd
import os
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import datetime
from dotenv import load_dotenv


# ---- ENV LOAD ----
load_dotenv()  # .env dosyasındaki değerleri yükle

PASSWORD = os.getenv("PASSWORD")
PASSWORDS = {
    "name": os.getenv("PASSWORD_NAME"),
    "password": os.getenv("PASSWORD_VALUE")
}

SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")

app = Flask(__name__)

# ---- İzinli input değişkenleri ----
ALLOWED_INPUT_VARIABLES = {
    "confirmed_code": str,
    "open_door_input": bool,
    "close_door": bool,
    "temperature_auto_input": bool,
    "brightness_auto_input": bool,
    "fan_input": bool,
    "window_input": bool,
    "heater_input": bool,
    "light_input": bool,
    "curtain_input": bool
}

HOME_INPUT_VARIABLES = {
    "password": str,
    "temperature": int,
    "brightness": bool,
    "password_input": int,
    "card_input": str,
    "open_door_input": bool,
    "close_door": bool,
    "face_recognition": bool,
    "temperature_auto_input": bool,
    "brightness_auto_input": bool,
    "fan_input": bool,
    "window_input": bool,
    "heater_input": bool,
    "light_input": bool,
    "curtain_input": bool
}

PASSWORD_ALLOWED_VARIABLES = {
    "name": "str",
    "password": "str",
}

# Global variables
users_codes_list = []
characters = string.ascii_letters + string.digits
INPUT_EXCEL_FILE = "input.xlsx"
OUTPUT_EXCEL_FILE = "output.xlsx"
IMAGE_FILE = "image.png"
email_site = ""
email_confirmed_codes = []
now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

MAIL_HTML = f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <h2 style="color: #4F46E5;">Akıllı Ev Kontrol Sistemi</h2>
  <p>Merhaba herdemitumtal</p>
  <p>Akıllı ev sisteminize giriş için linke tıklayın:</p>
  <div style="background-color: #F3F4F6; padding: 20px; border-radius: 8px; 
       margin: 20px 0; text-align: center;">
    <a href="{email_site}" 
       style="color: #4F46E5; font-size: 24px; text-decoration: none; 
              font-weight: bold;">
       {email_site}
    </a>
  </div>
  <p style="color: #6B7280;">Bu kod 5 dakika geçerlidir.</p>
  <p style="color: #6B7280; font-size: 12px;">Tarih: {now}</p>
</div>
"""


def filter_data(data, allowed_variables):
    """Veriyi izinli değişkenlere göre filtreler."""
    filtered_data = {}
    for key, val_type in allowed_variables.items():
        if key in data:
            try:
                filtered_data[key] = val_type(data[key])
            except (ValueError, TypeError):
                return None
    return filtered_data


def save_to_excel(data, filename, sheet_name="input"):
    """Veriyi Excel dosyasına kaydeder."""
    try:
        if os.path.exists(filename):
            df = pd.read_excel(filename, sheet_name=sheet_name)
            df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
        else:
            df = pd.DataFrame([data])

        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name=sheet_name)
        return True
    except Exception:
        return False


@app.route('/app-input', methods=['POST'])
def app_input():
    """Uygulama giriş endpoint'i."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400

    filtered_data = filter_data(data, HOME_INPUT_VARIABLES)
    if filtered_data is None:
        return jsonify({"error": "wrong format data"}), 400

    password_input = data.get("password")
    if password_input == PASSWORD:
        if save_to_excel(filtered_data, INPUT_EXCEL_FILE):
            return jsonify({"success": "successful"}), 200
        else:
            return jsonify({
                "error": "internal server error"
            }), 500

    return jsonify({"error": "unauthorized"}), 401


@app.route('/server-input', methods=['POST'])
def server_input():
    """Sunucu giriş endpoint'i."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400

    filtered_data = filter_data(data, ALLOWED_INPUT_VARIABLES)
    if filtered_data is None:
        return jsonify({"error": "wrong format data"}), 400

    confirmed_code = data.get("confirmed_code")
    if confirmed_code in email_confirmed_codes:
        if save_to_excel(filtered_data, INPUT_EXCEL_FILE):
            return jsonify({"success": "successful"}), 200
        else:
            return jsonify({
                "error": "internal server error"
            }), 500

    return jsonify({"error": "unauthorized"}), 401


@app.route('/server-output', methods=['GET'])
def server_output():
    """Sunucu çıkış endpoint'i."""
    data = request.get_json()

    if not data:
        return jsonify({"error": "no data"}), 400

    confirmed_code = data.get("confirmed_code")

    if confirmed_code in email_confirmed_codes:
        if not os.path.exists(OUTPUT_EXCEL_FILE):
            return jsonify({"error": "no available data"}), 404

        try:
            df = pd.read_excel(OUTPUT_EXCEL_FILE, sheet_name="output")
            if df.empty:
                return jsonify({"error": "no available data"}), 404

            # Son satırı döndür
            last_data = df.iloc[-1].to_dict()
            return jsonify({"success": "successful", "data": last_data}), 200
        except Exception as e:
            return jsonify({
                "error": "internal server error",
                "details": str(e)
            }), 500

    return jsonify({"error": "unauthorized"}), 401


@app.route('/image-input', methods=['POST'])
def image_input():
    """Resim yükleme endpoint'i."""
    if 'file' not in request.files:
        return jsonify({"error": "no data"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "wrong format data"}), 400

    try:
        file.save(IMAGE_FILE)
        return jsonify({"success": "successful"}), 200
    except Exception as e:
        return jsonify({
            "error": "internal server error",
            "details": str(e)
        }), 500


@app.route('/image-output', methods=['GET'])
def image_output():
    """Resim çıkış endpoint'i."""
    data = request.get_json()

    if not os.path.exists(IMAGE_FILE):
        return jsonify({"error": "file not found"}), 404

    if not data:
        return jsonify({"error": "no data"}), 400

    confirmed_code = data.get("confirmed_code")

    if confirmed_code in email_confirmed_codes:
        try:
            return send_file(IMAGE_FILE, mimetype='image/png')
        except Exception as e:
            return jsonify({
                "error": "internal server error",
                "details": str(e)
            }), 500

    return jsonify({"error": "unauthorized"}), 401


@app.route('/password-confirmation', methods=['GET'])
def password_confirmation():
    """Şifre doğrulama endpoint'i."""
    password_data = request.get_json()
    if not password_data:
        return jsonify({"error": "no data"}), 400

    # Yalnızca izinli değişkenleri filtrele
    filtered_data = {}
    for key, val_type in PASSWORD_ALLOWED_VARIABLES.items():
        if key in password_data:
            try:
                filtered_data[key] = str(password_data[key])
            except (ValueError, TypeError):
                return jsonify({"error": "wrong format data"}), 400

    if filtered_data == PASSWORDS:
        try:
            random_code = ''.join(random.choice(characters) for _ in range(16))
            global users_codes_list
            users_codes_list.append(random_code)
            return jsonify({
                "success": "successful",
                "random_code": random_code
            }), 200
        except Exception as e:
            return jsonify({
                "error": "internal server error",
                "details": str(e)
            }), 500

    return jsonify({"error": "unauthorized"}), 401


@app.route('/sign-out', methods=['GET'])
def sign_out():
    """Çıkış yapma endpoint'i."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400

    confirmed_code = data.get("confirmed_code")
    if confirmed_code in email_confirmed_codes:
        try:
            global users_codes_list
            if confirmed_code in users_codes_list:
                users_codes_list.remove(confirmed_code)
            return jsonify({
                "success": "successful",
                "message": "signed out"
            }), 200
        except Exception as e:
            return jsonify({
                "error": "internal server error",
                "details": str(e)
            }), 500

    return jsonify({"error": "unauthorized"}), 401


@app.route('/email', methods=['GET'])
def email():
    """E-posta gönderme endpoint'i."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400

    random_code = data.get("random_code")
    if not random_code:
        return jsonify({"error": "wrong format data"}), 400

    if random_code not in users_codes_list:
        return jsonify({"error": "unauthorized"}), 401

    try:
        users_codes_list.remove(random_code)

        global email_site
        global email_confirmed_codes
        email_site = ''.join(random.choice(characters) for _ in range(128))
        email_confirmed_codes.append(email_site)

        message = MIMEMultipart("alternative")
        message["Subject"] = "Akıllı Ev Doğrulama Kodu"
        message["From"] = SENDER_EMAIL
        message["To"] = RECEIVER_EMAIL
        part = MIMEText(MAIL_HTML, "html")
        message.attach(part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(SENDER_EMAIL, APP_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, message.as_string())

        return jsonify({
            "success": "successful",
            "message": "mail sent"
        }), 200

    except Exception as e:
        return jsonify({
            "error": "internal server error",
            "details": str(e)
        }), 500


def email_confirm():
    """E-posta doğrulama fonksiyonu."""
    try:
        confirmed_code = random.randint(100000, 999999)
        global email_confirmed_codes
        email_confirmed_codes.append(confirmed_code)
        return jsonify({
            "success": "successful",
            "email_confirmed_code": confirmed_code
        }), 200
    except Exception as e:
        return jsonify({
            "error": "internal server error",
            "details": str(e)
        }), 500


# URL aynen korunuyor
app.add_url_rule(f'/email-confirm{email_site}',
                 view_func=email_confirm,
                 methods=['GET'])


if __name__ == '__main__':
    app.run(debug=True)
