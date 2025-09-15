from flask import Flask, request, jsonify, send_file
import pandas as pd
import os
import random
import string

app = Flask(__name__)

# İzinli input değişkenleri ve tipleri
allowed_input_variables = {
    "random_code": str,
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

passwords = {
    "name":"herdemitumtal",
    "password":"2019itumtalherdem1907",
}

users_codes_list=[]

characters = string.ascii_letters + string.digits
input_excel_file = "input.xlsx"
output_excel_file = "output.xlsx"
image_file = "image.png"

@app.route('/server-user-input', methods=['POST'])
def server_user_input():
    data = request.get_json()
    if not data:
        return jsonify({"hata": "JSON verisi bulunamadı"}), 400

    # Yalnızca izinli değişkenleri filtrele
    filtered_data = {}
    for key, val_type in allowed_input_variables.items():
        if key in data:
            try:
                filtered_data[key] = val_type(data[key])
            except (ValueError, TypeError):
                return jsonify({"hata": f"{key} tipi hatalı"}), 400

    random_code = data.get("random_code")  # Sadece random_code al
    if random_code in users_codes_list:
        if os.path.exists(input_excel_file):
            df = pd.read_excel(input_excel_file, sheet_name="input")
            df = pd.concat([df, pd.DataFrame([filtered_data])], ignore_index=True)
        else:
            df = pd.DataFrame([filtered_data])

        with pd.ExcelWriter(input_excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="input")

        return jsonify({
            "mesaj": "İzinli değişkenler başarıyla alındı ve kaydedildi",
            "alinan_veri": filtered_data
        })
    return jsonify({"hata":"Sayfayı yenileyip tekrar deneyin"})


@app.route('/server-output', methods=['GET'])
def server_output():
    data = request.get_json()

    if not data:
        return jsonify({"hata": "JSON verisi bulunamadı"}), 400

    random_code = data.get("random_code")  # Sadece random_code al

    if random_code in users_codes_list:

        if not os.path.exists(output_excel_file):
            return jsonify({"hata":"henüz veri yok"})

        df = pd.read_excel(output_excel_file, sheet_name="output")
        # Sadece son satırı döndür
        data = df.iloc[-1].to_dict()
        return jsonify(data)

    return jsonify({"hata":"sayfayı yenileyip tekrar deneyin"})


@app.route('/image-input', methods=['POST'])
def image_input():
    if 'file' not in request.files:
        return jsonify({"hata": "Dosya bulunamadı"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"hata": "Dosya adı boş"}), 400

    # Her zaman image.png olarak kaydet (üstüne yazar)
    file.save(image_file)
    return jsonify({"mesaj": "Görsel alındı ve image.png olarak kaydedildi"})


@app.route('/image-output', methods=['GET'])
def image_output():
    data=request.get_json()
    if not os.path.exists(image_file):
        return jsonify({"hata": "Henüz image.png yüklenmedi"}), 404

    if not data:
        return jsonify({"hata": "JSON verisi bulunamadı"}), 400

    random_code = data.get("random_code")  # Sadece random_code al

    if random_code in users_codes_list:
        return send_file(image_file, mimetype='image/png')

    return jsonify({"hata":"sayfayı yenileyip tekrar deneyin"})

@app.route('/password-confirmation',methods=['GET'])
def password_confirmation():
    password_data = request.get_json()
    if not password_data:
        return jsonify({"hata": "JSON verisi bulunamadı"}), 400

    # Yalnızca izinli değişkenleri filtrele
    filtered_data = {}
    for key, val_type in allowed_input_variables.items():
        if key in password_data:
            try:
                filtered_data[key] = val_type(password_data[key])
            except (ValueError, TypeError):
                return jsonify({"hata": f"{key} tipi hatalı"}), 400
    if passwords==filtered_data:
        random_code = ''.join(random.choice(characters) for _ in range(16))
        global users_codes_list
        users_codes_list.append(random_code)
        return jsonify({"random_code": random_code})

@app.route('/sign-out',methods=['GET'])
def sign_out():
    data=request.get_json()
    if not data:
        return jsonify({"hata": "JSON verisi bulunamadı"}), 400

    random_code=data.get("random_code")
    if random_code in users_codes_list:
        global users_codes_list
        users_codes_list.remove(random_code)
        return jsonify({"200":"Cıkış yapıldı"})
    return None

if __name__ == '__main__':
    app.run(debug=True)
