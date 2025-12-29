#!/usr/bin/env python3
import mraa
import time
import sys
import sqlite3

# --- CẤU HÌNH ---
PIN_A1 = 1
MAX_BAR = 10.0
R_SHUNT = 165.0
READ_INTERVAL = 1.0
DB_NAME   = "app/database/main.db"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ApXuat (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ApXuat DECIMAL NOT NULL,
            TrangThai TEXT NOT NULL,
            DienAp DECIMAL NOT NULL,
            ThoiGian DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def insert_pressure(conn, pressure, status, voltage):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO ApXuat (ApXuat, TrangThai, DienAp)
        VALUES (?, ?, ?)
    """, (pressure, status, voltage))
    conn.commit()

# ---------- MAIN ----------
def main():
    try:
        ai = mraa.Aio(PIN_A1)
        ai.setBit(10)
    except ValueError as e:
        print(f"❌ Lỗi MRAA: {e}")
        sys.exit(1)

    conn = init_db()

    print("--- PRESSURE SENSOR SERVICE STARTED ---")
    print("Nhấn Ctrl+C để dừng.\n")

    try:
        while True:
            raw_val = ai.read()
            voltage = (raw_val / 1023.0) * 5.0

            v_zero = 0.66
            v_span = 2.64

            pressure = ((voltage - v_zero) / v_span) * MAX_BAR

            # --- Trạng thái ---
            if pressure < 0:
                if voltage < 0.5:
                    status = "DUT_DAY"
                    pressure = 0.0
                else:
                    status = "OK"
                    pressure = 0.0
            elif pressure > MAX_BAR:
                status = "QUA_AP"
                pressure = MAX_BAR
            else:
                status = "OK"

            print(
                f"Raw: {raw_val:4d} | "
                f"Volt: {voltage:.2f} V | "
                f"Ap suat: {pressure:.2f} Bar | "
                f"Trang thai: {status}"
            )

            # ---- GHI DATABASE ----
            insert_pressure(conn, pressure, status, voltage)

            time.sleep(READ_INTERVAL)

    except KeyboardInterrupt:
        conn.close()
        print("\n⛔ Pressure service stopped.")
    except Exception as e:
        print(f"❌ Lỗi khi đọc áp suất: {e}")

if __name__ == "__main__":
    main()
