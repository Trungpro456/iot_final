from flask import Blueprint, jsonify, request , session
from app.services.api import API
# Khai báo blue print API cho backend 
api_bp = Blueprint("api_bp", __name__)

# Test API 
@api_bp.route("/test")
def test():
    return jsonify("Hello world")

# XỬ LÝ ĐĂNG NHẬP TÀI KHOẢN 
@api_bp.route("/login", methods=["POST"])
def login():
    body = request.get_json() or {}
    username = body.get("username")
    password = body.get("password")

    if API().login(username, password):
        session["user"] = username   # 👈 BẮT BUỘC
        return jsonify({
            "success": True,
            "user": username
        })
    else:
        return jsonify({
            "success": False,
            "message": "Tên đăng nhập hoặc mật khẩu không đúng"
        }), 401

# Lấy trạng thái relay từ PLC
@api_bp.route("/relay_state")
def relay_state():
    return jsonify(API().get_relay_state())

# Lấy trạng thái relay từ DB
@api_bp.route("/relay_state_db")
def relay_state_db():
    return jsonify(API().get_relay_state_db())

# Cập nhật trạng thái relay vào DB
@api_bp.route("/update_relay_state_db", methods=["POST"])
def update_relay_state_db():
    body = request.get_json()
    relay_id = body.get("relay_id")
    state = body.get("state")
    return jsonify(API().update_relay_state_db(relay_id, state))

# Cập nhật mode relay vào DB
@api_bp.route("/update_relay_mode_db", methods=["POST"])
def update_relay_mode_db():
    body = request.get_json()
    relay_id = body.get("relay_id")
    mode = body.get("mode")
    return jsonify(API().update_relay_mode_db(relay_id, mode))

# Lấy dữ liệu lưu lượng
@api_bp.route("/latest_luuluong_1_2_and_total")
def latest_luuluong_1_2_and_total():
    return jsonify(API().get_latest_luuluong_1_2_and_total())

# Lấy dữ liệu áp suất
@api_bp.route("/latest_apxuat")
def latest_apxuat():
    return jsonify(API().get_latest_apxuat())

# Lấy dữ liệu EC
@api_bp.route("/latest_ec")
def latest_ec():
    return jsonify(API().get_latest_ec())

# Lấy dữ liệu pH
@api_bp.route("/latest_ph")
def latest_ph():
    return jsonify(API().get_latest_ph())

# Lấy dữ liệu lịch sử
@api_bp.route("/history_data")
def history_data():
    start_time = request.args.get("start_time")
    end_time = request.args.get("end_time")
    return jsonify(API().get_history_data(start_time, end_time))

# Lấy dữ liệu lưu lượng
@api_bp.route("/data_luu_luong")
def data_luu_luong():
    id = request.args.get("id")
    return jsonify(API().get_data_luu_luong(id))

# Lấy dữ liệu áp suất
@api_bp.route("/data_apxuat")
def data_apxuat():
    return jsonify(API().get_data_apxuat())

# Lấy dữ liệu EC
@api_bp.route("/data_ec")
def data_ec():
    return jsonify(API().get_data_ec())

# Lấy dữ liệu pH
@api_bp.route("/data_ph")
def data_ph():
    return jsonify(API().get_data_ph())
