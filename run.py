import app   # ⚠️ import module, KHÔNG import biến

flask_app = app.create_app()

if __name__ == "__main__":
    app.socket_manager.socketio.run(
        flask_app,
        host="0.0.0.0",
        port=8000,
        debug=True
    )
