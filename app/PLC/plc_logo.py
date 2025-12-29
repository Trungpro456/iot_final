# plc_logo.py
# Dành cho pymodbus 2.5.3 (Raspberry Pi / IOT2050)

from pymodbus.client.sync import ModbusTcpClient


class LogoPLC:
    def __init__(self, host="192.168.137.3", port=502):
        self.host = host
        self.port = port

        # Kết nối test 1 lần để báo trạng thái
        test_client = ModbusTcpClient(self.host, self.port)
        ok = test_client.connect()
        print("🔌 PLC LOGO connect =", ok)
        test_client.close()

    # ---------- GHI M1–M7 và M9 (bỏ M8) ----------
    def write_relay(self, relay_id, state):
        client = ModbusTcpClient(self.host, self.port)

        print(f"→ Ghi relay M{relay_id} = {state}")

        if not client.connect():
            print("❌ Không kết nối được PLC khi ghi relay")
            return None

        relay_id = int(relay_id)

        # ❌ Không cho phép ghi M8
        if relay_id == 8:
            print("⚠️ M8 là biến đặc biệt – bỏ qua")
            client.close()
            return None

        base_addr = 8256  # M1
        coil_addr = base_addr + (relay_id - 1)

        value = True if state == "ON" else False
        result = client.write_coil(coil_addr, value, unit=1)
        print("→ Ghi relay result:", result)
        client.close()
        return result

    # ---------- ĐỌC Q1–Q8, fallback M1–M9 (bỏ M8) ----------
    def read_outputs(self):
        client = ModbusTcpClient(self.host, self.port)

        if not client.connect():
            print("❌ Không kết nối được PLC khi đọc outputs")
            return None

        # ----- Đọc Q1..Q8 -----
        r = client.read_coils(8192, 8, unit=1)

        if r and hasattr(r, "bits") and len(r.bits) >= 8:
            result = {str(i + 1): int(r.bits[i]) for i in range(8)}
            client.close()
            return result

        print("❌ Không đọc được Q → thử đọc M")

        # ----- Đọc M1..M9 -----
        r = client.read_coils(8256, 9, unit=1)

        if not r or not hasattr(r, "bits") or len(r.bits) < 9:
            print("❌ Không đọc được cả Q và M")
            client.close()
            return None

        # Bỏ M8
        result = {}
        for i in range(9):
            m_index = i + 1
            if m_index == 8:
                continue
            result[str(m_index)] = int(r.bits[i])

        client.close()
        return result


# ---- Test nhanh ----
if __name__ == "__main__":
    plc = LogoPLC()

    print("→ Ghi M1 = ON")
    plc.write_relay(1, "on")

    print("→ Đọc Q1..Q8 / fallback M")
    print(plc.read_outputs())


# ---- Tạo đối tượng PLC dùng chung cho app.py ----
plc = LogoPLC()
