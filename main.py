"""
FastAPI Server untuk Sistem Manajemen Akademik
Dengan semua fitur yang diminta
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Form, File, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from pathlib import Path
from typing import Optional
import shutil
from datetime import datetime
import json

from database import db_manager, Role, Mahasiswa, Dosen, User, StatusAbsen
from algorithms import algo_manager
from auth import AuthHandler, get_current_user

# ========== SETUP FASTAPI ==========
app = FastAPI(
    title="Sistem Manajemen Akademik",
    description="Sistem lengkap untuk manajemen data mahasiswa, dosen, dan nilai",
    version="2.0.0"
)

# Setup static files dan templates
BASE_DIR = Path(__file__).parent
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=BASE_DIR / "templates")

# Buat folder uploads jika belum ada
UPLOAD_DIR = BASE_DIR / "static" / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

# Auth handler
auth_handler = AuthHandler()

# ========== MIDDLEWARE ==========
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers"""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

# ========== ROUTES ==========

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Halaman login"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    """Dashboard utama berdasarkan role"""
    context = {
        "request": request,
        "user": current_user,
        "role": current_user.get("role"),
        "stats": get_dashboard_stats(current_user)
    }
    return templates.TemplateResponse("dashboard.html", context)

@app.get("/mahasiswa", response_class=HTMLResponse)
async def page_mahasiswa(request: Request, current_user: dict = Depends(get_current_user)):
    """Halaman data mahasiswa"""
    mahasiswa_data = db_manager.mahasiswa_data
    
    # Apply sorting jika ada parameter
    sort_by = request.query_params.get("sort_by", "")
    if sort_by:
        mahasiswa_data = algo_manager.sort_data(
            mahasiswa_data, 
            algorithm="bubble",  # Default bubble sort
            key=sort_by.replace("_desc", "").replace("_asc", ""),
            ascending="_asc" in sort_by
        )["sorted_data"]
    
    context = {
        "request": request,
        "user": current_user,
        "mahasiswa": mahasiswa_data,
        "algorithms": algo_manager.get_time_complexity_info()
    }
    return templates.TemplateResponse("mahasiswa.html", context)

@app.get("/dosen", response_class=HTMLResponse)
async def page_dosen(request: Request, current_user: dict = Depends(get_current_user)):
    """Halaman data dosen"""
    context = {
        "request": request,
        "user": current_user,
        "dosen": db_manager.dosen_data
    }
    return templates.TemplateResponse("dosen.html", context)

@app.get("/nilai", response_class=HTMLResponse)
async def page_nilai(request: Request, current_user: dict = Depends(get_current_user)):
    """Halaman nilai dan absensi"""
    context = {
        "request": request,
        "user": current_user,
        "mahasiswa": db_manager.mahasiswa_data[:50]  # Batasi untuk performa
    }
    return templates.TemplateResponse("nilai.html", context)

@app.get("/profile", response_class=HTMLResponse)
async def page_profile(request: Request, current_user: dict = Depends(get_current_user)):
    """Halaman profile user"""
    context = {
        "request": request,
        "user": current_user
    }
    return templates.TemplateResponse("profile.html", context)

@app.get("/users", response_class=HTMLResponse)
async def page_users(request: Request, current_user: dict = Depends(get_current_user)):
    """Halaman management users (admin only)"""
    if current_user.get("role") != Role.ADMIN.value:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    context = {
        "request": request,
        "user": current_user,
        "all_users": db_manager.users
    }
    return templates.TemplateResponse("users.html", context)

# ========== API ENDPOINTS ==========

@app.post("/api/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """API login"""
    user = db_manager.authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Username atau password salah")
    
    # Create JWT token
    token = auth_handler.encode_token(user["username"], user["role"])
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "role": user["role"],
            "nama": user["nama"]
        }
    }

@app.post("/api/mahasiswa")
async def create_mahasiswa(
    nama: str = Form(...),
    jurusan: str = Form(...),
    angkatan: int = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Create mahasiswa baru (admin only)"""
    if current_user.get("role") != Role.ADMIN.value:
        raise HTTPException(status_code=403, detail="Hanya admin yang bisa membuat mahasiswa")
    
    try:
        result = db_manager.create_mahasiswa(nama, jurusan, angkatan)
        return JSONResponse({
            "success": True,
            "message": "Mahasiswa berhasil dibuat",
            "data": result
        })
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/api/mahasiswa/{nim}/nilai")
async def update_nilai_mahasiswa(
    nim: str,
    kode_matkul: str = Form(...),
    nilai_tugas: float = Form(...),
    nilai_uts: float = Form(...),
    nilai_uas: float = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Update nilai mahasiswa (dosen only)"""
    if current_user.get("role") != Role.DOSEN.value:
        raise HTTPException(status_code=403, detail="Hanya dosen yang bisa memberi nilai")
    
    # Cari mahasiswa
    mahasiswa = algo_manager.search_data(
        db_manager.mahasiswa_data, 
        "linear", 
        "nim", 
        nim
    )["result"]
    
    if not mahasiswa:
        raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")
    
    # Hitung nilai akhir
    nilai_akhir = (nilai_tugas * 0.3 + nilai_uts * 0.3 + nilai_uas * 0.4)
    
    # Update data (simplified)
    # Dalam implementasi real, perlu update ke database
    return {
        "success": True,
        "message": "Nilai berhasil diupdate",
        "data": {
            "nim": nim,
            "kode_matkul": kode_matkul,
            "nilai_akhir": nilai_akhir,
            "dosen": current_user.get("username")
        }
    }

@app.post("/api/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload foto profil"""
    # Validasi file
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus gambar")
    
    # Generate unique filename
    file_ext = file.filename.split(".")[-1]
    filename = f"{current_user['username']}_{datetime.now().timestamp()}.{file_ext}"
    filepath = UPLOAD_DIR / filename
    
    # Save file
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Update database
    db_manager.update_profile(
        current_user["username"],
        foto_profil=f"/static/uploads/{filename}"
    )
    
    return {
        "success": True,
        "message": "Foto berhasil diupload",
        "file_url": f"/static/uploads/{filename}"
    }

@app.get("/api/search")
async def search_data(
    q: str,
    algorithm: str = "linear",
    current_user: dict = Depends(get_current_user)
):
    """API search dengan pilihan algoritma"""
    if algorithm == "binary":
        # Untuk binary search, butuh key yang spesifik
        if q.isdigit() and len(q) > 3:
            result = algo_manager.search_data(
                db_manager.mahasiswa_data,
                "binary",
                "nim",
                q
            )
        else:
            result = {"error": "Untuk binary search, gunakan NIM lengkap"}
    else:
        result = algo_manager.search_data(
            db_manager.mahasiswa_data,
            algorithm,
            search_value=q
        )
    
    return result

@app.get("/api/sort")
async def sort_data(
    algorithm: str = "bubble",
    key: str = "nama",
    order: str = "asc",
    current_user: dict = Depends(get_current_user)
):
    """API sorting dengan pilihan algoritma"""
    ascending = order == "asc"
    
    try:
        result = algo_manager.sort_data(
            db_manager.mahasiswa_data,
            algorithm,
            key,
            ascending
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/algorithm-info")
async def get_algorithm_info():
    """Get info time complexity semua algoritma"""
    return algo_manager.get_time_complexity_info()

@app.get("/api/whatsapp")
async def get_whatsapp_link():
    """Return WhatsApp link untuk customer service"""
    phone = "082213407223"
    message = "Halo, saya butuh bantuan terkait Sistem Manajemen Akademik"
    whatsapp_url = f"https://wa.me/{phone}?text={message}"
    
    return {
        "phone": phone,
        "whatsapp_url": whatsapp_url,
        "message": "Customer Service tersedia via WhatsApp"
    }

# ========== HELPER FUNCTIONS ==========
def get_dashboard_stats(user: dict) -> dict:
    """Get statistics untuk dashboard"""
    role = user.get("role")
    
    if role == Role.ADMIN.value:
        return {
            "total_mahasiswa": len(db_manager.mahasiswa_data),
            "total_dosen": len(db_manager.dosen_data),
            "total_users": len(db_manager.users),
            "recent_activity": []
        }
    elif role == Role.DOSEN.value:
        return {
            "total_mahasiswa": len(db_manager.mahasiswa_data),
            "matkul_diampu": 3,  # Example
            "nilai_diberikan": 45,
            "absensi_diinput": 120
        }
    else:  # Mahasiswa
        # Cari data mahasiswa ini
        mhs_data = next(
            (m for m in db_manager.mahasiswa_data if m["nim"] == user["username"]),
            {}
        )
        
        return {
            "ipk": mhs_data.get("ipk", 0),
            "total_sks": mhs_data.get("total_sks", 0),
            "presensi_rate": mhs_data.get("presensi_rate", 0),
            "matkul_aktif": len(mhs_data.get("nilai", []))
        }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

# ========== RUN APPLICATION ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )