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
passwords = {
    "name": os.getenv("PASSWORD_NAME"),
    "password": os.getenv("PASSWORD_VALUE")
}

sender_email = os.getenv("SENDER_EMAIL")
receiver_email = os.getenv("RECEIVER_EMAIL")
app_password = os.getenv("APP_PASSWORD")

app = Flask(__name__)

# ---- İzinli input değişkenleri ----
allowed_input_variables = {
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
home_input_variables = {
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

password_allowed_variables = {
    "name":"str",
    "password":"str",
}

users_codes_list=[]
characters = string.ascii_letters + string.digits
input_excel_file = "input.xlsx"
output_excel_file = "output.xlsx"
image_file = "image.png"
email_site=""
email_confirmed_codes=[]
now = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

mail_html = f"""
<div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
  <h2 style="color: #4F46E5;">Akıllı Ev Kontrol Sistemi</h2>
  <p>Merhaba herdemitumtal</p>
  <p>Akıllı ev sisteminize giriş için linke tıklayın:</p>
  <div style="background-color: #F3F4F6; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center;">
    <a href="{email_site}" 
       style="color: #4F46E5; font-size: 24px; text-decoration: none; font-weight: bold;">
       {email_site}
    </a>
  </div>
  <p style="color: #6B7280;">Bu kod 5 dakika geçerlidir.</p>
  <p style="color: #6B7280; font-size: 12px;">Tarih: {now}</p>
</div>
"""
@app.route('/app-input', methods=['POST'])
def app_input():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400

    filtered_data = {}
    for key, val_type in home_input_variables.items():
        if key in data:
            try:
                filtered_data[key] = val_type(data[key])
            except (ValueError, TypeError):
                return jsonify({"error": "wrong format data"}), 400

    passwordin = data.get("password")
    if passwordin == password:
        try:
            if os.path.exists(input_excel_file):
                df = pd.read_excel(input_excel_file, sheet_name="input")
                df = pd.concat([df, pd.DataFrame([filtered_data])], ignore_index=True)
            else:
                df = pd.DataFrame([filtered_data])

            with pd.ExcelWriter(input_excel_file, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="input")

            return jsonify({"success": "successful"}), 200
        except Exception as e:
            return jsonify({"error": "internal server error", "details": str(e)}), 500

    return jsonify({"error": "unauthorized"}), 401

@app.route('/server-input', methods=['POST'])
def server_input():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400

    filtered_data = {}
    for key, val_type in allowed_input_variables.items():
        if key in data:
            try:
                filtered_data[key] = val_type(data[key])
            except (ValueError, TypeError):
                return jsonify({"error": "wrong format data"}), 400

    confirmed_code = data.get("confirmed_code")
    if confirmed_code in email_confirmed_codes:
        try:
            if os.path.exists(input_excel_file):
                df = pd.read_excel(input_excel_file, sheet_name="input")
                df = pd.concat([df, pd.DataFrame([filtered_data])], ignore_index=True)
            else:
                df = pd.DataFrame([filtered_data])

            with pd.ExcelWriter(input_excel_file, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="input")

            return jsonify({"success": "successful"}), 200
        except Exception as e:
            return jsonify({"error": "internal server error", "details": str(e)}), 500

    return jsonify({"error": "unauthorized"}), 401


@app.route('/server-output', methods=['GET'])
def server_output():
    data = request.get_json()

    if not data:
        return jsonify({"error": "no data"}), 400

    confirmed_code = data.get("confirmed_code")

    if confirmed_code in email_confirmed_codes:
        if not os.path.exists(output_excel_file):
            return jsonify({"error": "no available data"}), 404

        try:
            df = pd.read_excel(output_excel_file, sheet_name="output")
            if df.empty:
                return jsonify({"error": "no available data"}), 404

            # Son satırı döndür
            last_data = df.iloc[-1].to_dict()
            return jsonify({"success": "successful", "data": last_data}), 200
        except Exception as e:
            return jsonify({"error": "internal server error", "details": str(e)}), 500

    return jsonify({"error": "unauthorized"}), 401



@app.route('/image-input', methods=['POST'])
def image_input():
    if 'file' not in request.files:
        return jsonify({"error": "no data"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "wrong format data"}), 400

    try:
        file.save(image_file)
        return jsonify({"success": "successful"}), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500


@app.route('/image-output', methods=['GET'])
def image_output():
    data = request.get_json()

    if not os.path.exists(image_file):
        return jsonify({"error": "file not found"}), 404

    if not data:
        return jsonify({"error": "no data"}), 400

    confirmed_code = data.get("confirmed_code")

    if confirmed_code in email_confirmed_codes:
        try:
            return send_file(image_file, mimetype='image/png')
        except Exception as e:
            return jsonify({"error": "internal server error", "details": str(e)}), 500

    return jsonify({"error": "unauthorized"}), 401


@app.route('/password-confirmation', methods=['GET'])
def password_confirmation():
    password_data = request.get_json()
    if not password_data:
        return jsonify({"error": "no data"}), 400

    # Yalnızca izinli değişkenleri filtrele
    filtered_data = {}
    for key, val_type in password_allowed_variables.items():
        if key in password_data:
            try:
                filtered_data[key] = str(password_data[key])  # string olarak alıyoruz
            except (ValueError, TypeError):
                return jsonify({"error": "wrong format data"}), 400

    if filtered_data == passwords:
        try:
            random_code = ''.join(random.choice(characters) for _ in range(16))
            global users_codes_list
            users_codes_list.append(random_code)
            return jsonify({"success": "successful", "random_code": random_code}), 200
        except Exception as e:
            return jsonify({"error": "internal server error", "details": str(e)}), 500

    return jsonify({"error": "unauthorized"}), 401


@app.route('/sign-out', methods=['GET'])
def sign_out():
    data = request.get_json()
    if not data:
        return jsonify({"error": "no data"}), 400

    confirmed_code = data.get("confirmed_code")
    if confirmed_code in email_confirmed_codes:
        try:
            global users_codes_list
            if confirmed_code in users_codes_list:
                users_codes_list.remove(confirmed_code)
            return jsonify({"success": "successful", "message": "signed out"}), 200
        except Exception as e:
            return jsonify({"error": "internal server error", "details": str(e)}), 500

    return jsonify({"error": "unauthorized"}), 401


@app.route('/email', methods=['GET'])
def email():
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
        message["From"] = sender_email
        message["To"] = receiver_email
        part = MIMEText(html_content, "html")
        message.attach(part)

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, message.as_string())

        return jsonify({"success": "successful", "message": "mail sent"}), 200

    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500



def email_confirm():
    try:
        confirmed_code = random.randint(100000, 999999)
        global email_confirmed_codes
        email_confirmed_codes.append(confirmed_code)
        return jsonify({"success": "successful", "email_confirmed_code": confirmed_code}), 200
    except Exception as e:
        return jsonify({"error": "internal server error", "details": str(e)}), 500

# URL aynen korunuyor
app.add_url_rule(f'/email-confirm{email_site}', view_func=email_confirm, methods=['GET'])


if __name__ == '__main__':
    app.run(debug=True)
