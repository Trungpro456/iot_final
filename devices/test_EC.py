#!/usr/bin/env python3
import mraa
import time
import sqlite3
from datetime import datetime

# ================= CẤU HÌNH =================
PIN_INDEX = 3        # Chân analog EC
V_REF = 5.0
ADC_RES = 1023.0
K_VALUE = 0.007633
READ_INTERVAL = 1.0
DB_NAME   = "app/database/main.db"
# ============================================

def calc_ec(raw_val):
    """Chuyển ADC raw -> EC (uS/cm)"""
    voltage = (raw_val / ADC_RES) * V_REF

    if voltage <= 0.05:
        ec_mS = 0.0
    else:
        ec_mS = (
            133.42 * (voltage ** 3)
            - 255.86 * (voltage ** 2)
            + 857.39 * voltage
        ) * K_VALUE

    ec_uS = ec_mS * 1000
    return voltage, ec_uS

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS EC (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            Raw INTEGER NOT NULL,
            Voltage DECIMAL NOT NULL,
            EC DECIMAL NOT NULL,
            ThoiGian DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def insert_ec(conn, raw, voltage, ec):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO EC (Raw, Voltage, EC)
        VALUES (?, ?, ?)
    """, (raw, voltage, ec))
    conn.commit()

# ---------- MAIN ----------
def main():
    try:
        ai = mraa.Aio(PIN_INDEX)
        ai.setBit(10)
    except ValueError as e:
        print(f"❌ Lỗi khởi tạo ADC: {e}")
        return

    conn = init_db()

    print("=== EC SENSOR SERVICE STARTED ===")
    print("Nhấn Ctrl+C để dừng\n")

    try:
        while True:
            raw = ai.read()
            voltage, ec = calc_ec(raw)

            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(
                f"[{ts}] RAW={raw:4d} | "
                f"V={voltage:.3f} V | "
                f"EC={ec:.0f} uS/cm"
            )

            # ---- GHI DATABASE ----
            insert_ec(conn, raw, voltage, ec)

            time.sleep(READ_INTERVAL)

    except KeyboardInterrupt:
        conn.close()
        print("\n⛔ EC service stopped.")

if __name__ == "__main__":
    main()
