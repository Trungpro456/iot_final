#!/usr/bin/env python3
from pymodbus.client.sync import ModbusSerialClient
import sqlite3
import time
import sys

# ================== CẤU HÌNH ==================
PORT_NAME = '/dev/ttyUSB0'
SLAVE_ID  = 1
DB_NAME   = "app/database/main.db"
READ_INTERVAL = 1.0
# ==============================================

client = ModbusSerialClient(
    method='rtu',
    port=PORT_NAME,
    baudrate=9600,
    parity='E',
    stopbits=1,
    bytesize=8,
    timeout=1
)

# ================== ĐỊA CHỈ MODBUS ==================
ADDR_READ_FREQ    = 12288    # Hz (*100)
ADDR_READ_CURRENT = 12291    # A (*10)

# ================== DATABASE ==================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS INVTG20 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            TanSo INTEGER NOT NULL,
            DongDien DECIMAL NOT NULL,
            ThoiGian DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def insert_data(conn, freq, current):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO INVTG20 (TanSo, DongDien)
        VALUES (?, ?)
    """, (int(freq), current))
    conn.commit()

# ================== MAIN ==================
def main():
    if not client.connect():
        print("❌ Không kết nối được Modbus RTU")
        sys.exit(1)

    print(f"✅ Đã kết nối Modbus RTU tại {PORT_NAME}")

    conn = init_db()

    try:
        while True:
            rr = client.read_holding_registers(ADDR_READ_FREQ, 4, unit=SLAVE_ID)
            if rr.isError():
                print("❌ Lỗi đọc Modbus")
                time.sleep(READ_INTERVAL)
                continue

            freq = rr.registers[0] / 100.0   # 12288
            current = rr.registers[3] / 10.0  # 12291

            print(f"📊 F={freq:.2f} Hz | I={current:.2f} A")

            # ---- GHI DATABASE ----
            insert_data(conn, freq, current)

            time.sleep(READ_INTERVAL)

    except KeyboardInterrupt:
        print("\n⛔ Dừng chương trình")

    finally:
        conn.close()
        client.close()
        print("🔌 Đã đóng kết nối Modbus")

if __name__ == "__main__":
    main()
