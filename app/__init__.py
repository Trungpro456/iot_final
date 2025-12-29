from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.sockets.socket_message import SocketMessage

db = SQLAlchemy()
socket_manager = None   # chỉ khai báo

def create_app():
    global socket_manager

    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    app.secret_key = "super-secret-key"

    db.init_app(app)

    socket_manager = SocketMessage(app)


    from .routes.frontend import web_bp
    from .routes.api import api_bp

    app.register_blueprint(web_bp)
    app.register_blueprint(api_bp, url_prefix="/api")

    return app
