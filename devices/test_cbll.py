import mraa
import time
import sys
import sqlite3

# ================= CẤU HÌNH =================
PIN_FLOW_1 = 2          # D2
PIN_FLOW_2 = 3          # D3
K_FACTOR_1 = 10.0
K_FACTOR_2 = 10.0
UPDATE_INTERVAL = 1.0
DB_NAME = "main.db"
# ============================================

pulse_1 = 0
pulse_2 = 0

total_1 = 0.0   # tổng lưu lượng sensor 1 (L)
total_2 = 0.0   # tổng lưu lượng sensor 2 (L)

# ---------- ISR ----------
def isr_flow_1(args):
    global pulse_1
    pulse_1 += 1

def isr_flow_2(args):
    global pulse_2
    pulse_2 += 1

def format_time(seconds):
    m, s = divmod(seconds, 60)
    return f"{int(m):02d}:{int(s):02d}"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS LuuLuong (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            LuuLuongID INTEGER NOT NULL,
            SoXung INTEGER NOT NULL,
            LP DECIMAL NOT NULL,
            LS DECIMAL NOT NULL,
            TongLuuLuong DECIMAL NOT NULL,
            ThoiGian DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def insert_flow(conn, sensor_id, so_xung, lp, ls, tong):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO LuuLuong (LuuLuongID, SoXung, LP, LS, TongLuuLuong)
        VALUES (?, ?, ?, ?, ?)
    """, (sensor_id, so_xung, lp, ls, tong))
    conn.commit()

# ---------- MAIN ----------
def main():
    global pulse_1, pulse_2, total_1, total_2

    conn = init_db()

    try:
        flow1 = mraa.Gpio(PIN_FLOW_1)
        flow1.dir(mraa.DIR_IN)
        flow1.mode(mraa.MODE_PULLUP)
        flow1.isr(mraa.EDGE_FALLING, isr_flow_1, None)

        flow2 = mraa.Gpio(PIN_FLOW_2)
        flow2.dir(mraa.DIR_IN)
        flow2.mode(mraa.MODE_PULLUP)
        flow2.isr(mraa.EDGE_FALLING, isr_flow_2, None)

    except ValueError:
        print("❌ Lỗi khởi tạo GPIO")
        sys.exit(1)

    print("-" * 105)
    print(f"| {'TGIAN':^7} | {'XUNG 1':^8} | {'LƯU LƯỢNG 1':^14} | {'XUNG 2':^8} | {'LƯU LƯỢNG 2':^14} |")
    print("-" * 105)

    last_time = time.time()
    start_time = time.time()
    last_pulse_1 = 0
    last_pulse_2 = 0

    try:
        while True:
            time.sleep(UPDATE_INTERVAL)
            current_time = time.time()
            dt = current_time - last_time

            # ---- SENSOR 1 ----
            current_1 = pulse_1
            delta_1 = current_1 - last_pulse_1
            hz_1 = delta_1 / dt
            flow_lpm_1 = hz_1 / K_FACTOR_1
            flow_ls_1 = flow_lpm_1 / 60.0
            total_1 += flow_ls_1 * dt

            # ---- SENSOR 2 ----
            current_2 = pulse_2
            delta_2 = current_2 - last_pulse_2
            hz_2 = delta_2 / dt
            flow_lpm_2 = hz_2 / K_FACTOR_2
            flow_ls_2 = flow_lpm_2 / 60.0
            total_2 += flow_ls_2 * dt

            elapsed = format_time(current_time - start_time)

            print(
                f"| {elapsed:^7} | "
                f"{delta_1:^8} | {flow_lpm_1:10.2f} L/p | "
                f"{delta_2:^8} | {flow_lpm_2:10.2f} L/p |"
            )

            # ---- GHI DATABASE ----
            insert_flow(conn, 1, delta_1, flow_lpm_1, flow_ls_1, total_1)
            insert_flow(conn, 2, delta_2, flow_lpm_2, flow_ls_2, total_2)

            last_time = current_time
            last_pulse_1 = current_1
            last_pulse_2 = current_2

    except KeyboardInterrupt:
        try:
            flow1.isrExit()
            flow2.isrExit()
        except:
            pass
        conn.close()
        print("\n⛔ Đã dừng chương trình")

if __name__ == "__main__":
    main()
import mraa
import time
import sys
import sqlite3

# ================= CẤU HÌNH =================
PIN_FLOW_1 = 2          # D2
PIN_FLOW_2 = 3          # D3
K_FACTOR_1 = 10.0
K_FACTOR_2 = 10.0
UPDATE_INTERVAL = 1.0
DB_NAME   = "app/database/main.db"
# ============================================

pulse_1 = 0
pulse_2 = 0

total_1 = 0.0   # tổng lưu lượng sensor 1 (L)
total_2 = 0.0   # tổng lưu lượng sensor 2 (L)

# ---------- ISR ----------
def isr_flow_1(args):
    global pulse_1
    pulse_1 += 1

def isr_flow_2(args):
    global pulse_2
    pulse_2 += 1

def format_time(seconds):
    m, s = divmod(seconds, 60)
    return f"{int(m):02d}:{int(s):02d}"

# ---------- DATABASE ----------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS LuuLuong (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            LuuLuongID INTEGER NOT NULL,
            SoXung INTEGER NOT NULL,
            LP DECIMAL NOT NULL,
            LS DECIMAL NOT NULL,
            TongLuuLuong DECIMAL NOT NULL,
            ThoiGian DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn

def insert_flow(conn, sensor_id, so_xung, lp, ls, tong):
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO LuuLuong (LuuLuongID, SoXung, LP, LS, TongLuuLuong)
        VALUES (?, ?, ?, ?, ?)
    """, (sensor_id, so_xung, lp, ls, tong))
    conn.commit()

# ---------- MAIN ----------
def main():
    global pulse_1, pulse_2, total_1, total_2

    conn = init_db()

    try:
        flow1 = mraa.Gpio(PIN_FLOW_1)
        flow1.dir(mraa.DIR_IN)
        flow1.mode(mraa.MODE_PULLUP)
        flow1.isr(mraa.EDGE_FALLING, isr_flow_1, None)

        flow2 = mraa.Gpio(PIN_FLOW_2)
        flow2.dir(mraa.DIR_IN)
        flow2.mode(mraa.MODE_PULLUP)
        flow2.isr(mraa.EDGE_FALLING, isr_flow_2, None)

    except ValueError:
        print("❌ Lỗi khởi tạo GPIO")
        sys.exit(1)

    print("-" * 105)
    print(f"| {'TGIAN':^7} | {'XUNG 1':^8} | {'LƯU LƯỢNG 1':^14} | {'XUNG 2':^8} | {'LƯU LƯỢNG 2':^14} |")
    print("-" * 105)

    last_time = time.time()
    start_time = time.time()
    last_pulse_1 = 0
    last_pulse_2 = 0

    try:
        while True:
            time.sleep(UPDATE_INTERVAL)
            current_time = time.time()
            dt = current_time - last_time

            # ---- SENSOR 1 ----
            current_1 = pulse_1
            delta_1 = current_1 - last_pulse_1
            hz_1 = delta_1 / dt
            flow_lpm_1 = hz_1 / K_FACTOR_1
            flow_ls_1 = flow_lpm_1 / 60.0
            total_1 += flow_ls_1 * dt

            # ---- SENSOR 2 ----
            current_2 = pulse_2
            delta_2 = current_2 - last_pulse_2
            hz_2 = delta_2 / dt
            flow_lpm_2 = hz_2 / K_FACTOR_2
            flow_ls_2 = flow_lpm_2 / 60.0
            total_2 += flow_ls_2 * dt

            elapsed = format_time(current_time - start_time)

            print(
                f"| {elapsed:^7} | "
                f"{delta_1:^8} | {flow_lpm_1:10.2f} L/p | "
                f"{delta_2:^8} | {flow_lpm_2:10.2f} L/p |"
            )

            # ---- GHI DATABASE ----
            insert_flow(conn, 1, delta_1, flow_lpm_1, flow_ls_1, total_1)
            insert_flow(conn, 2, delta_2, flow_lpm_2, flow_ls_2, total_2)

            last_time = current_time
            last_pulse_1 = current_1
            last_pulse_2 = current_2

    except KeyboardInterrupt:
        try:
            flow1.isrExit()
            flow2.isrExit()
        except:
            pass
        conn.close()
        print("\n⛔ Đã dừng chương trình")

if __name__ == "__main__":
    main()
