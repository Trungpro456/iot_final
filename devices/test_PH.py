#!/usr/bin/env python3
import mraa
import time
import sys
import sqlite3

# --- CẤU HÌNH ---
ANALOG_PIN = 4
V_REF = 5.0
ADC_RES = 1024.0
READ_INTERVAL = 1.0
DB_NAME   = "app/database/main.db"

# --- HIỆU CHUẨN ---
OFFSET = 0.00
PH_STEP = 3.5

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS PH (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Raw INTEGER NOT NULL,
            Voltage DECIMAL NOT NULL,
            PH DECIMAL NOT NULL,
            ThoiGian DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def insert_ph(conn, raw, voltage, ph):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO PH (Raw, Voltage, PH)
        VALUES (?, ?, ?)
    """, (int(raw), voltage, ph))
    conn.commit()

# ---------- MAIN ----------
def main():
    try:
        ph_sensor = mraa.Aio(ANALOG_PIN)
    except ValueError:
        print("❌ Không thể khởi tạo chân Analog A0.")
        sys.exit(1)

    conn = init_db()

    print("--- pH SENSOR SERVICE STARTED ---")
    print("Nhấn Ctrl+C để dừng.\n")

    try:
        while True:
            raw_sum = 0
            for _ in range(10):
                raw_sum += ph_sensor.read()
                time.sleep(0.02)

            raw_avg = raw_sum / 10.0
            voltage = raw_avg * (V_REF / ADC_RES)

            # --- Công thức pH ---
            ph_value = 7.0 + ((voltage - 2.5) / 0.18)
            # hoặc:
            # ph_value = PH_STEP * voltage + OFFSET

            print(
                f"Raw: {raw_avg:6.1f} | "
                f"Volt: {voltage:.2f} V | "
                f"pH: {ph_value:.2f}"
            )

            # ---- GHI DATABASE ----
            insert_ph(conn, raw_avg, voltage, ph_value)

            time.sleep(READ_INTERVAL)

    except KeyboardInterrupt:
        conn.close()
        print("\n⛔ pH service stopped.")
    except Exception as e:
        print(f"❌ Lỗi khi đọc pH: {e}")

if __name__ == "__main__":
    main()
