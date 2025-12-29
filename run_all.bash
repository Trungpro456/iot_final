#!/bin/bash

# Kích hoạt môi trường ảo nếu cần
# source /path/to/venv/bin/activate

# echo "Chạy test_bt220.py..."
# python3 devices/test_bt220.py &

echo "Chạy test_cbas.py..."
python3 devices/test_cbas.py &

echo "Chạy test_cbll.py..."
python3 devices/test_cbll.py &

echo "Chạy test_EC.py..."
python3 devices/test_EC.py &

echo "Chạy test_PH.py..."
python3 devices/test_PH.py &

wait
echo "Tất cả các script đã chạy xong."
