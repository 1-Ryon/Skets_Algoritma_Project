from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel
from typing import Optional
from backend_logic import DatabaseManager, UserManager

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Inisialisasi Dua Manager
db = DatabaseManager()
user_db = UserManager()

# --- Auth Logic ---
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme)):
    # Cari user di file data_users.json
    user = next((u for u in user_db.users if u['username'] == token), None)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

# --- Pydantic Models ---
class MahasiswaInput(BaseModel):
    nama: str
    jurusan: str
    ipk: float

# --- Routes Frontend (HTML) ---
@app.get("/")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard")
def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

# --- API Endpoints ---

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = user_db.authenticate(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Username atau Password salah")
    
    # Return username sebagai token sederhana
    return {"access_token": user['username'], "token_type": "bearer", "role": user['role']}

@app.get("/api/mahasiswa")
def get_all(sort_by: Optional[str] = None, search: Optional[str] = None):
    data = db.data
    if search:
        if search.isdigit():
            found = db.binary_search_nim(search)
            data = [found] if found else []
        else:
            data = [m for m in data if search.lower() in m['nama'].lower()]

    if sort_by == "ipk_desc": data = db.bubble_sort_by_ipk(ascending=False)
    elif sort_by == "ipk_asc": data = db.bubble_sort_by_ipk(ascending=True)
            
    return data

@app.post("/api/mahasiswa")
def add_mhs(mhs: MahasiswaInput, current_user: dict = Depends(get_current_user)):
    # 1. Cek Authorization: Hanya Admin
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Hanya Admin yang boleh menambah data")
    
    try:
        # 2. Tambah Data Mahasiswa (Generate NIM terjadi di sini)
        new_mhs = db.add_mahasiswa_data(mhs.nama, mhs.jurusan, mhs.ipk)
        generated_nim = new_mhs['nim']
        
        # 3. Generate Password Otomatis: "maha#" + 4 digit terakhir NIM
        # Contoh NIM: 251208000001 -> Password: maha#0001
        last_4_digits = generated_nim[-4:]
        generated_password = f"maha#{last_4_digits}"
        
        # 4. Buat Akun Login untuk Mahasiswa tersebut
        user_db.create_user(username=generated_nim, password=generated_password, role="mahasiswa")
        
        return {
            "message": "Data & Akun Berhasil Dibuat",
            "data": new_mhs,
            "account_info": {
                "username": generated_nim,
                "initial_password": generated_password
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/api/mahasiswa/{nim}")
def delete_mhs(nim: str, current_user: dict = Depends(get_current_user)):
    if current_user['role'] != 'admin':
        raise HTTPException(status_code=403, detail="Hanya Admin yang boleh menghapus")
    
    # Hapus Data Profil DAN Akun Login
    deleted_data = db.delete_mahasiswa_data(nim)
    if deleted_data:
        user_db.delete_user(nim) # Hapus akun user juga agar tidak jadi sampah
        return {"message": "Data & Akun Berhasil Dihapus"}
        
    raise HTTPException(status_code=404, detail="Data tidak ditemukan")