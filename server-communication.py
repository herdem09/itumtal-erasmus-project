from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# İzinli input değişkenleri ve tipleri
allowed_input_variables = {
    "communication_password_input": str,
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

input_excel_file = "input.xlsx"
output_excel_file = "output.xlsx"


@app.route('/server-input', methods=['POST'])
def server_input():
    veri = request.get_json()
    if not veri:
        return jsonify({"hata": "JSON verisi bulunamadı"}), 400

    # Yalnızca izinli değişkenleri filtrele
    filtered_data = {}
    for key, val_type in allowed_input_variables.items():
        if key in veri:
            try:
                filtered_data[key] = val_type(veri[key])
            except (ValueError, TypeError):
                return jsonify({"hata": f"{key} tipi hatalı"}), 400

    # Excel dosyasına kaydet
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


@app.route('/server-output', methods=['GET'])
def server_output():
    # Eğer output.xlsx yoksa örnek veri oluştur
    if not os.path.exists(output_excel_file):
        output_data = {
            "temperature": 24,
            "brightness": True,
            "open_door": False,
            "temperature_auto": True,
            "brightness_auto": True,
            "fan": False,
            "window": False,
            "heater": False,
            "light": False,
            "curtain": True,
            "timer": 0.0
        }
        df = pd.DataFrame([output_data])
        with pd.ExcelWriter(output_excel_file, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name="output")

    df = pd.read_excel(output_excel_file, sheet_name="output")
    # Sadece son satırı döndür
    data = df.iloc[-1].to_dict()
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)
