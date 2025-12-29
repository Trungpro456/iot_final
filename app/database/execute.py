import sqlite3
import os

DB_PATH = os.path.abspath("app/database/main.db")

'''
Lớp thực thi các hàm truy vấn cơ sở dữ liệu
'''
class HandleDB:
    def get_conn(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    # ================= RELAY =================
# Lấy trạng thái tất cả relay
    def get_all_relay_state_db(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM relay_states")
            return [dict(row) for row in cursor.fetchall()]

# Lấy trạng thái và chế độ của 1 relay
    def get_relay_state_db(self, relay_id):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT state, mode FROM relay_states WHERE relay_id = ?",
                (relay_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else {"state": "off", "mode": "manual"}

# Cập nhật trạng thái relay
    def update_relay_state_db(self, relay_id, state):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE relay_states SET state = ? WHERE relay_id = ?",
                (state, relay_id),
            )
            conn.commit()

# Cập nhật chế độ relay (auto/manual)
    def update_relay_mode_db(self, relay_id, mode):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE relay_states SET mode = ? WHERE relay_id = ?",
                (mode, relay_id),
            )
            conn.commit()

    # ================= SENSOR =================
# Lấy ra lưu lượng 1, 2 và tổng lưu lượng mới nhất
    def get_latest_luuluong_1_2_and_total(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT LuuLuongID, TongLuuLuong
                FROM LuuLuong
                WHERE LuuLuongID IN (1, 2)
                ORDER BY ThoiGian DESC
                """
            )
            rows = cursor.fetchall()

        luuluong_1 = None
        luuluong_2 = None

        for row in rows:
            if row["LuuLuongID"] == 1 and not luuluong_1:
                luuluong_1 = dict(row)
            elif row["LuuLuongID"] == 2 and not luuluong_2:
                luuluong_2 = dict(row)
            if luuluong_1 and luuluong_2:
                break

        tong = sum(
            float(x["TongLuuLuong"]) for x in (luuluong_1, luuluong_2) if x
        )

        return {
            "luu_luong_1": luuluong_1,
            "luu_luong_2": luuluong_2,
            "tong_luu_luong": tong,
        }

# Lấy ra áp suất mới nhất
    def get_latest_apxuat(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT ApXuat FROM ApXuat ORDER BY ThoiGian DESC LIMIT 1"
            )
            row = cursor.fetchone()
            return row["ApXuat"] if row else None

# Lấy ra EC mới nhất và làm tròn 2 chữ số thập phân
    def get_latest_ec(self, decimals=2):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT EC FROM EC ORDER BY ThoiGian DESC LIMIT 1")
            row = cursor.fetchone()
            if row and row["EC"] is not None:
                return round(row["EC"], decimals)
            return None

# Lấy ra PH mới nhất 
    def get_latest_ph(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT PH FROM PH ORDER BY ThoiGian DESC LIMIT 1")
            row = cursor.fetchone()
            return row["PH"] if row else None
# Kiểm tra tài khoản đăng nhập
    def check_login(self, username, password):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM USER WHERE mssv = ? AND password = ?",
                (username, password),
            )
            row = cursor.fetchone()
            return dict(row) if row else None
# Lấy dữ liệu lưu lượng
    def get_data_luu_luong(self, luongluong_id):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM LuuLuong WHERE LuuLuongID = ? ORDER BY ThoiGian DESC",
                (luongluong_id,),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

# Lấy dữ liệu áp suất
    def get_data_apxuat(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM ApXuat ORDER BY ThoiGian DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

# Lấy dữ liệu EC
    def get_data_ec(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM EC ORDER BY ThoiGian DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
# Lấy dữ liệu PH
    def get_data_ph(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM PH ORDER BY ThoiGian DESC")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]


# Lấy dữ liệu lịch sử và vẽ biểu đồ 
    def get_history_data(self, start_time=None, end_time=None, limit=20):
        # Base query helper
        def get_query(table, value_col, time_col="ThoiGian", where_clause=""):
            base = f"SELECT {value_col} as value, {time_col} as time FROM {table}"
            if start_time and end_time:
                extra_condition = f"AND {where_clause}" if where_clause else ""
                return f"{base} WHERE {time_col} BETWEEN ? AND ? {extra_condition} ORDER BY {time_col} ASC"
            return f"{base} {('WHERE ' + where_clause) if where_clause else ''} ORDER BY {time_col} DESC LIMIT ?"

        params = (start_time, end_time) if start_time and end_time else (limit,)
        cursor = self.get_conn().cursor()
        # Fetch Flow 1
        cursor.execute(
            get_query("LuuLuong", "TongLuuLuong", where_clause="LuuLuongID=1"), params
        )
        flow1 = [dict(row) for row in cursor.fetchall()]

        # Fetch Flow 2
        cursor.execute(
            get_query("LuuLuong", "TongLuuLuong", where_clause="LuuLuongID=2"), params
        )
        flow2 = [dict(row) for row in cursor.fetchall()]

        # Fetch Pressure
        cursor.execute(get_query("ApXuat", "ApXuat"), params)
        pressure = [dict(row) for row in cursor.fetchall()]
        # Fetch EC
        cursor.execute(get_query("EC", "EC"), params)
        ec = [dict(row) for row in cursor.fetchall()]

        # Fetch pH
        cursor.execute(get_query("PH", "PH"), params)
        ph = [dict(row) for row in cursor.fetchall()]
        # If data was fetched with DESC + LIMIT, reverse it for charts
        if not (start_time and end_time):
            flow1 = flow1[::-1]
            flow2 = flow2[::-1]
            pressure = pressure[::-1]
            ec = ec[::-1]
            ph = ph[::-1]

        return {
            "flow1": flow1,
            "flow2": flow2,
            "pressure": pressure,
            "ec": ec,
            "ph": ph,
        }
