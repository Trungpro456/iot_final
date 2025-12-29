from flask import Blueprint, render_template, session, redirect, url_for, flash
from functools import wraps

web_bp = Blueprint("web_bp", __name__)

# 1. Decorator để bảo vệ các trang yêu cầu đăng nhập
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            # Nếu chưa đăng nhập, đá về trang login và thông báo
            return redirect(url_for("web_bp.login_page"))
        return f(*args, **kwargs)
    return decorated_function

# --- ROUTES ---

@web_bp.route("/")
@login_required # Chỉ cho xem trang chủ khi đã login
def home():
    return render_template("index.html")

@web_bp.route("/login")
def login(): # Đổi login_page thành login
    if "user" in session:
        return redirect(url_for("web_bp.home"))
    return render_template("login.html")
    
@web_bp.route("/logout")
def logout():
    session.pop("user", None)
    flash("Bạn đã đăng xuất thành công", "info")
    return redirect(url_for("web_bp.login")) # Sửa thành login_page theo tên hàm bên dưới

@web_bp.route("/history")
@login_required
def history():
    return render_template("history.html")

@web_bp.route("/data")
@login_required
def data():
    return render_template("data.html")

@web_bp.route("/device")
@login_required
def device():
    return render_template("device.html")

@web_bp.route("/contact")
def contact():
    # Trang contact có thể cho phép xem công khai
    return render_template("contact.html")