"""
FastAPI Server untuk Sistem Manajemen Akademik Lengkap
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

from database import db_manager, Role, StatusAbsen
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
security = HTTPBearer()

# ========== MIDDLEWARE ==========
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response

# ========== ROUTES UTAMA ==========

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, current_user: dict = Depends(get_current_user)):
    context = {
        "request": request,
        "user": current_user,
        "role": current_user.get("role"),
        "stats": get_dashboard_stats(current_user)
    }
    return templates.TemplateResponse("dashboard.html", context)

@app.get("/mahasiswa", response_class=HTMLResponse)
async def page_mahasiswa(request: Request, current_user: dict = Depends(get_current_user)):
    mahasiswa_data = db_manager.mahasiswa_data
    
    # Apply sorting jika ada parameter
    sort_by = request.query_params.get("sort_by", "")
    if sort_by:
        if "ipk" in sort_by:
            ascending = "asc" in sort_by
            mahasiswa_data = algo_manager.sort_data(
                mahasiswa_data, 
                algorithm="bubble",
                key="ipk",
                ascending=ascending
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
    context = {
        "request": request,
        "user": current_user,
        "dosen": db_manager.dosen_data
    }
    return templates.TemplateResponse("dosen.html", context)

@app.get("/nilai", response_class=HTMLResponse)
async def page_nilai(request: Request, current_user: dict = Depends(get_current_user)):
    context = {
        "request": request,
        "user": current_user,
        "mahasiswa": db_manager.mahasiswa_data[:20]  # Batasi untuk performa
    }
    return templates.TemplateResponse("nilai.html", context)

@app.get("/profile", response_class=HTMLResponse)
async def page_profile(request: Request, current_user: dict = Depends(get_current_user)):
    context = {
        "request": request,
        "user": current_user,
        "mahasiswa": db_manager.mahasiswa_data  # Tambahkan ini
    }
    return templates.TemplateResponse("profile.html", context)

@app.get("/users", response_class=HTMLResponse)
async def page_users(request: Request, current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != Role.ADMIN.value:
        raise HTTPException(status_code=403, detail="Forbidden")
    
    context = {
        "request": request,
        "user": current_user,
        "all_users": db_manager.users
    }
    return templates.TemplateResponse("users.html", context)

# ========== API ENDPOINTS ==========
# ========== ENDPOINT BARU ==========

@app.get("/api/mahasiswa/{nim}")
async def get_mahasiswa_detail(nim: str, current_user: dict = Depends(get_current_user)):
    """Get mahasiswa detail by NIM"""
    mahasiswa = next((m for m in db_manager.mahasiswa_data if m["nim"] == nim), None)
    if not mahasiswa:
        raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")
    
    return mahasiswa

@app.put("/api/profile")
async def update_profile(
    nama: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    jurusan: Optional[str] = Form(None),
    angkatan: Optional[str] = Form(None),
    bidang: Optional[str] = Form(None),
    bio: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """Update user profile"""
    updates = {}
    
    if nama:
        updates["nama"] = nama
    if email:
        updates["email"] = email
    if bio:
        updates["bio"] = bio
    
    # Update role-specific fields
    if current_user.get("role") == "mahasiswa":
        if jurusan:
            updates["jurusan"] = jurusan
        if angkatan:
            updates["angkatan"] = angkatan
    elif current_user.get("role") == "dosen":
        if bidang:
            updates["bidang"] = bidang
    
    # Update in database
    try:
        # Simulate update
        user_index = next((i for i, u in enumerate(db_manager.users) 
                          if u["username"] == current_user["username"]), -1)
        
        if user_index >= 0:
            for key, value in updates.items():
                db_manager.users[user_index][key] = value
            db_manager.save_all()
        
        return {"success": True, "message": "Profil berhasil diperbarui"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/change-password")
async def change_password(
    old_password: str = Form(...),
    new_password: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    """Change user password"""
    # In a real app, verify old password and update
    # For now, just simulate success
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password baru minimal 6 karakter")
    
    return {"success": True, "message": "Password berhasil diubah"}

@app.delete("/api/mahasiswa/{nim}")
async def delete_mahasiswa(nim: str, current_user: dict = Depends(get_current_user)):
    """Delete mahasiswa by NIM (admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Hanya admin yang bisa menghapus mahasiswa")
    
    try:
        # Remove from mahasiswa data
        initial_length = len(db_manager.mahasiswa_data)
        db_manager.mahasiswa_data = [m for m in db_manager.mahasiswa_data if m["nim"] != nim]
        
        # Remove from users
        db_manager.users = [u for u in db_manager.users if u["username"] != nim]
        
        if len(db_manager.mahasiswa_data) < initial_length:
            db_manager.save_all()
            return {"success": True, "message": "Mahasiswa berhasil dihapus"}
        else:
            raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/dosen/{nidn}")
async def delete_dosen(nidn: str, current_user: dict = Depends(get_current_user)):
    """Delete dosen by NIDN (admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Hanya admin yang bisa menghapus dosen")
    
    try:
        # Remove from dosen data
        initial_length = len(db_manager.dosen_data)
        db_manager.dosen_data = [d for d in db_manager.dosen_data if d["nidn"] != nidn]
        
        # Remove from users
        db_manager.users = [u for u in db_manager.users if u["username"] != nidn]
        
        if len(db_manager.dosen_data) < initial_length:
            db_manager.save_all()
            return {"success": True, "message": "Dosen berhasil dihapus"}
        else:
            raise HTTPException(status_code=404, detail="Dosen tidak ditemukan")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/login")
async def login(username: str = Form(...), password: str = Form(...)):
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

@app.post("/api/dosen")
async def create_dosen(
    nama: str = Form(...),
    bidang: str = Form(...),
    current_user: dict = Depends(get_current_user)
):
    if current_user.get("role") != Role.ADMIN.value:
        raise HTTPException(status_code=403, detail="Hanya admin yang bisa membuat dosen")
    
    try:
        # Generate NIDN (8 digit)
        import random
        nidn = str(random.randint(10000000, 99999999))
        
        # Buat user dosen
        from database import Dosen
        dosen = Dosen(nidn, nama, bidang)
        dosen_dict = dosen.to_dict()
        
        # Tambah ke database
        db_manager.dosen_data.append(dosen_dict)
        
        # Tambah ke users juga
        from database import User, Role
        user_dosen = User(nidn, Role.DOSEN, nama)
        user_dosen.set_password(f"dosen#{nidn[-4:]}")
        db_manager.users.append(user_dosen.to_dict())
        
        db_manager.save_all()
        
        return {
            "success": True,
            "message": "Dosen berhasil dibuat",
            "data": dosen_dict,
            "login_info": {
                "username": nidn,
                "password": f"dosen#{nidn[-4:]}"
            }
        }
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
    if current_user.get("role") != Role.DOSEN.value:
        raise HTTPException(status_code=403, detail="Hanya dosen yang bisa memberi nilai")
    
    # Hitung nilai akhir
    nilai_akhir = (nilai_tugas * 0.3 + nilai_uts * 0.3 + nilai_uas * 0.4)
    
    return {
        "success": True,
        "message": "Nilai berhasil diupdate",
        "data": {
            "nim": nim,
            "kode_matkul": kode_matkul,
            "nilai_tugas": nilai_tugas,
            "nilai_uts": nilai_uts,
            "nilai_uas": nilai_uas,
            "nilai_akhir": nilai_akhir,
            "dosen": current_user.get("username")
        }
    }

@app.post("/api/upload-photo")
async def upload_photo(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File harus gambar")
    
    # Generate unique filename
    import uuid
    file_ext = file.filename.split(".")[-1]
    filename = f"{current_user['username']}_{uuid.uuid4().hex[:8]}.{file_ext}"
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
    if algorithm == "binary":
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

@app.get("/api/whatsapp")
async def get_whatsapp_link():
    phone = "6282213407223"
    message = "Halo, saya butuh bantuan terkait Sistem Manajemen Akademik"
    whatsapp_url = f"https://wa.me/{phone}?text={message}"
    
    return {
        "phone": phone,
        "whatsapp_url": whatsapp_url,
        "message": "Customer Service tersedia via WhatsApp"
    }

@app.get("/api/algorithm-info")
async def get_algorithm_info():
    return algo_manager.get_time_complexity_info()

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/api/user/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return current_user

# ========== HELPER FUNCTIONS ==========
def get_dashboard_stats(user: dict) -> dict:
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
            "matkul_diampu": 3,
            "nilai_diberikan": 45,
            "absensi_diinput": 120
        }
    else:  # Mahasiswa
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

# ========== RUN APPLICATION ==========
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )