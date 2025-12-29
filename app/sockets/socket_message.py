from flask_socketio import SocketIO, emit
from app.database.execute import HandleDB
from app.PLC.plc_logo import LogoPLC

plc = LogoPLC()

class SocketMessage:
    def __init__(self, app, async_mode="threading", cors_allowed_origins="*"):
        self.socketio = SocketIO(
            app,
            async_mode=async_mode,
            cors_allowed_origins=cors_allowed_origins,
        )
        self.plc = plc
        self.register_events()
        self.socketio.start_background_task(self.plc_status_worker)

    # ================= EVENTS =================

    def register_events(self):

        @self.socketio.on("connect")
        def handle_connect():
            print("✅ Client connected")

            db = HandleDB()
            states = db.get_all_relay_state_db()

            emit("relay_status_all", states)

        @self.socketio.on("disconnect")
        def handle_disconnect():
            print("❌ Client disconnected")


        @self.socketio.on("toggle_relay")
        def handle_toggle_relay(data):
            relay_id = str(data.get("relay_id"))
            state = data.get("state")
            print(f"🔄 Yêu cầu đổi trạng thái relay {relay_id} → {state}")
            try:
                # 1. Ghi PLC
                plc.write_relay(relay_id, state)

                # 2. Cập nhật DB
                db = HandleDB()
                db.update_relay_state_db(relay_id, state)

                # 3. Emit cho tất cả client
                self.socketio.emit(
                    "relay_status",
                    {"relay_id": relay_id, "state": state}
                )

            except Exception as e:
                emit(
                    "relay_error",
                    {"relay_id": relay_id, "message": str(e)}
                )

    # ================= PLC WORKER =================

    def plc_status_worker(self):
        last_states = {}

        while True:
            try:
                states = plc.read_outputs()
                if not states:
                # nếu read fail tạm thời → wait lâu hơn
                    self.socketio.sleep(2)
                    continue

                for r, v in states.items():
                    state = "on" if v else "off"

                    if last_states.get(r) != state:
                        last_states[r] = state
                        self.socketio.emit(
                            "relay_status",
                            {"relay_id": str(r), "state": state}
                        )

            except Exception as e:
            # Chỉ log, không disconnect toàn bộ PLC
                print("PLC worker error:", e)

            self.socketio.sleep(1)