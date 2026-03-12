from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
CORS(app)

@app.route('/redeem', methods=['POST'])
def redeem_mystrix():
    try:
        data = request.json
        full_url = data.get('url', '')
        target_phone = data.get('phone', '') # รับเบอร์โทรจาก Roblox

        # ตรวจสอบข้อมูลเบื้องต้น
        if not target_phone or len(target_phone) < 10:
            return jsonify({"status": "error", "message": "เบอร์โทรศัพท์เจ้าของไม่ถูกต้อง"}), 400
        
        if not full_url.startswith("https://gift.truemoney.com"):
            return jsonify({"status": "error", "message": "ลิงก์ซองไม่ถูกต้อง"}), 400

        # ส่งคำขอไปที่ Mystrix API
        api_url = "https://api.mystrix2.me/truemoney"
        payload = {
            "phone": target_phone,
            "gift": full_url 
        }
        
        print(f"[*] Processing: {target_phone} with gift link")
        
        response = requests.post(api_url, data=payload, timeout=20)
        
        try:
            res_json = response.json()
        except:
            return jsonify({"status": "error", "message": "API Mystrix ไม่ตอบกลับเป็น JSON"}), 500

        # ตรวจสอบผลลัพธ์
        if res_json.get("data") and res_json["data"].get("voucher"):
            amount = res_json["data"]["voucher"]["amount_baht"]
            return jsonify({"status": "success", "amount": amount})

        # กรณี Error จาก API ภายนอก
        err_msg = res_json.get('msg') or res_json.get('message') or "ซองของขวัญใช้ไม่ได้"
        return jsonify({"status": "error", "message": err_msg}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": f"Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    # สำหรับ Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
