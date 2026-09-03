import os
from fastapi import FastAPI, UploadFile, File, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from ultralytics import YOLO

import models
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API Deteksi Kerusakan Bodi Mobil",
    description="Backend untuk mendeteksi kerusakan mobil menggunakan YOLO dan PostgreSQL",
    version="1.0.0"
)

app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = "yolov8n.pt" 
model = YOLO(MODEL_PATH)

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"status": "Aman", "message": "Backend Deteksi Bodi Mobil Berjalan Lancar!"}

@app.post("/detect/")
async def detect_damage(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
        raise HTTPException(status_code=400, detail="Format file harus berupa JPG, JPEG, atau PNG.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    try:
        results = model(file_path)
        detected_damages = []
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                label = model.names[class_id]
                confidence = float(box.conf[0])
                detected_damages.append({
                    "label": label,
                    "confidence": round(confidence, 2)
                })

        if not detected_damages:
            summary_label = "Normal / Tidak Ada Kerusakan"
            severity = "Aman"
        else:
            summary_label = ", ".join(list(set([d['label'] for d in detected_damages])))
            severity = "Parah" if len(detected_damages) > 3 else "Sedang" if len(detected_damages) > 1 else "Ringan"

        db_log = models.DamageLog(
            image_path=file_path,
            damage_type=summary_label,
            severity_level=severity,
            confidence_score=float(results[0].boxes.conf[0]) if detected_damages else 0.0
        )
        db.add(db_log)
        db.commit()
        db.refresh(db_log)

        return {
            "id": db_log.id,
            "status": "Sukses",
            "filename": file.filename,
            "detections": detected_damages,
            "summary": {
                "damage_type": summary_label,
                "severity_level": severity
            },
            "saved_at": db_log.created_at
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Terjadi kesalahan saat pemrosesan: {str(e)}")

@app.get("/logs")
def get_all_logs(db: Session = Depends(get_db)):
    logs = db.query(models.DamageLog).order_by(models.DamageLog.created_at.desc()).all()
    return {
        "status": "Sukses",
        "total_data": len(logs),
        "data": logs
    }

@app.get("/logs/{log_id}")
def get_log_detail(log_id: int, db: Session = Depends(get_db)):
    log = db.query(models.DamageLog).filter(models.DamageLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Data log tidak ditemukan.")
    return {
        "status": "Sukses",
        "data": log
    }

@app.delete("/logs/{log_id}")
def delete_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(models.DamageLog).filter(models.DamageLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Data log tidak ditemukan.")
    
    # Hapus file gambar jika ada di direktori
    if os.path.exists(log.image_path):
        os.remove(log.image_path)
        
    db.delete(log)
    db.commit()
    return {
        "status": "Sukses",
        "message": f"Log dengan ID {log_id} beserta gambarnya berhasil dihapus."
    }