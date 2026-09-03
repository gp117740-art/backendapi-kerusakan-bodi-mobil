import urllib.request

# URL model YOLOv8 custom khusus car damage detection (Public Mirror)
MODEL_URL = "https://huggingface.co/fefefelix/yolov8n-car-damage/resolve/main/best.pt"
MODEL_PATH = "car_damage_best.pt"

print("Sedang mengunduh model deteksi kerusakan mobil...")

# Menggunakan User-Agent agar tidak dianggap bot oleh server HuggingFace
req = urllib.request.Request(
    MODEL_URL, 
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
)

try:
    with urllib.request.urlopen(req) as response, open(MODEL_PATH, 'wb') as out_file:
        out_file.write(response.read())
    print(f"Berhasil! Model tersimpan sebagai '{MODEL_PATH}'.")
except Exception as e:
    print(f"Gagal mengunduh model: {e}")