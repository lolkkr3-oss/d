from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import traceback

app = Flask(__name__)
CORS(app)

@app.route('/redeem', methods=['POST'])
def redeem_mystrix():
    try:
        # 1. รับข้อมูลจาก Roblox
        data = request.json
        if not data:
            return jsonify({"status": "error", "message": "ไม่มีข้อมูลส่งมา"}), 400

        full_url = data.get('url', '').strip()
        target_phone = data.get('phone', '').strip()

        # 2. ตรวจสอบเงื่อนไขเบื้องต้น
        print(f"[*] รับคำขอเติมเงิน: เบอร์ {target_phone} | ลิงก์: {full_url}")

        if not target_phone or len(target_phone) < 10:
            print("[FAIL] เบอร์โทรศัพท์ไม่ถูกต้อง")
            return jsonify({"status": "error", "message": "เบอร์โทรศัพท์เจ้าของแมพไม่ถูกต้อง"}), 400
        
        if not full_url.startswith("https://gift.truemoney.com"):
            print("[FAIL] ลิงก์ซองไม่ถูกต้อง")
            return jsonify({"status": "error", "message": "รูปแบบลิงก์ซองไม่ถูกต้อง"}), 400

        # 3. ส่งคำขอไปที่ Mystrix API
        api_url = "https://api.mystrix2.me/truemoney"
        payload = {
            "phone": target_phone,
            "gift": full_url 
        }
        
        # ตั้งค่า timeout ไว้ 20 วินาทีกันค้าง
        response = requests.post(api_url, data=payload, timeout=20)
        
        # ตรวจสอบว่า API ตอบกลับมาเป็น JSON หรือไม่
        try:
            res_json = response.json()
        except:
            print(f"[DEBUG] Raw Response (Not JSON): {response.text}")
            return jsonify({"status": "error", "message": "API ภายนอกไม่ตอบกลับเป็น JSON"}), 500

        # 4. พิมพ์คำตอบจาก Mystrix ออกมาดูเพื่อ Debug (สำคัญมาก)
        print(f"[DEBUG] Mystrix Response: {res_json}")

        # 5. ตรวจสอบผลลัพธ์ตามโครงสร้าง API
        # กรณีสำเร็จ
        if res_json.get("data") and res_json["data"].get("voucher"):
            amount = res_json["data"]["voucher"]["amount_baht"]
            print(f">>> [OK] สำเร็จ! ยอดเงิน: {amount} บาท")
            return jsonify({"status": "success", "amount": amount})
        
        # กรณีไม่สำเร็จ (ดึงข้อความ Error จาก API มาโชว์)
        err_msg = res_json.get('msg') or res_json.get('message') or "ซองไม่ถูกต้องหรือถูกใช้ไปแล้ว"
        print(f"[FAIL] ปฏิเสธการเติมเงิน: {err_msg}")
        return jsonify({"status": "error", "message": err_msg}), 400

    except Exception as e:
        print(f"[CRASH] เกิดข้อผิดพลาดที่ Server: {str(e)}")
        traceback.print_exc() # พิมพ์ Error เต็มๆ ใน Terminal
        return jsonify({"status": "error", "message": f"Internal Server Error: {str(e)}"}), 500

if __name__ == '__main__':
    # รองรับทั้งรันในคอม (Local) และรันบน Render
port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)
