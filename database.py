import json
import os
import re
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Optional
import uuid
from dataclasses import dataclass, field
from enum import Enum

# ========== ENUMS ==========
class Role(Enum):
    ADMIN = "admin"
    DOSEN = "dosen"
    MAHASISWA = "mahasiswa"

class Semester(Enum):
    GANJIL = "ganjil"
    GENAP = "genap"

class StatusAbsen(Enum):
    HADIR = "hadir"
    IZIN = "izin"
    SAKIT = "sakit"
    ALPHA = "alpha"

# ========== ABSTRACT CLASSES ==========
class Person(ABC):
    """Abstract Base Class untuk semua orang dalam sistem"""
    def __init__(self, username: str, role: Role):
        self._username = username
        self._role = role
        self._created_at = datetime.now()
        
    @abstractmethod
    def get_info(self) -> str:
        pass
    
    @property
    def username(self):
        return self._username
    
    @property
    def role(self):
        return self._role

# ========== INHERITANCE ==========
class User(Person):
    """Class untuk user sistem dengan enkapsulasi lengkap"""
    def __init__(self, username: str, role: Role, nama: str, email: str = ""):
        super().__init__(username, role)
        self.__nama = nama
        self.__email = email
        self.__password = self._generate_initial_password()
        self.__foto_profil = ""
        self.__is_active = True
        self.__last_login = None
        self.__profile_complete = False
        
    def _generate_initial_password(self) -> str:
        """Generate password otomatis berdasarkan role"""
        if self._role == Role.ADMIN:
            return "admin123"
        elif self._role == Role.DOSEN:
            return f"dosen#{self._username[-4:]}"
        else:  # Mahasiswa
            return f"maha#{self._username[-4:]}"
    
    def get_info(self) -> str:
        return f"{self._role.value.capitalize()}: {self.__nama} ({self._username})"
    
    # === ENCAPSULATION dengan property ===
    @property
    def nama(self):
        return self.__nama
    
    @nama.setter
    def nama(self, value):
        if not re.match(r"^[a-zA-Z\s.,']+$", value):
            raise ValueError("Nama hanya boleh huruf dan spasi")
        self.__nama = value
    
    @property
    def email(self):
        return self.__email
    
    @email.setter
    def email(self, value):
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
            raise ValueError("Email tidak valid")
        self.__email = value
    
    @property
    def password(self):
        return "********"  # Hide password
    
    def set_password(self, new_password):
        if len(new_password) < 6:
            raise ValueError("Password minimal 6 karakter")
        self.__password = new_password
    
    def check_password(self, password):
        return self.__password == password
    
    @property
    def foto_profil(self):
        return self.__foto_profil
    
    @foto_profil.setter
    def foto_profil(self, path):
        self.__foto_profil = path
    
    def to_dict(self):
        return {
            "username": self._username,
            "role": self._role.value,
            "nama": self.__nama,
            "email": self.__email,
            "foto_profil": self.__foto_profil,
            "is_active": self.__is_active,
            "created_at": self._created_at.isoformat(),
            "profile_complete": self.__profile_complete
        }

class Mahasiswa(User):
    """Class khusus untuk mahasiswa dengan inheritance"""
    def __init__(self, nim: str, nama: str, jurusan: str, angkatan: int):
        super().__init__(nim, Role.MAHASISWA, nama)
        self.__nim = nim
        self.__jurusan = jurusan
        self.__angkatan = angkatan
        self.__ipk = 0.0
        self.__total_sks = 0
        self.__nilai_list = []
        self.__absensi_list = []
    
    def hitung_ipk(self) -> float:
        """Hitung IPK dari semua nilai"""
        if not self.__nilai_list:
            return 0.0
        
        total_bobot = 0
        total_sks = 0
        
        for nilai in self.__nilai_list:
            bobot = self._konversi_nilai_ke_bobot(nilai['nilai_akhir'])
            total_bobot += bobot * nilai['sks']
            total_sks += nilai['sks']
        
        self.__ipk = total_bobot / total_sks if total_sks > 0 else 0.0
        self.__total_sks = total_sks
        return self.__ipk
    
    def _konversi_nilai_ke_bobot(self, nilai: float) -> float:
        """Konversi nilai angka ke bobot"""
        if nilai >= 85: return 4.0
        elif nilai >= 80: return 3.7
        elif nilai >= 75: return 3.3
        elif nilai >= 70: return 3.0
        elif nilai >= 65: return 2.7
        elif nilai >= 60: return 2.3
        elif nilai >= 55: return 2.0
        elif nilai >= 50: return 1.7
        else: return 0.0
    
    def hitung_ips(self, semester: str, tahun: int) -> float:
        """Hitung IPS per semester"""
        nilai_semester = [n for n in self.__nilai_list 
                         if n['semester'] == semester and n['tahun'] == tahun]
        
        if not nilai_semester:
            return 0.0
        
        total_bobot = 0
        total_sks = 0
        
        for nilai in nilai_semester:
            bobot = self._konversi_nilai_ke_bobot(nilai['nilai_akhir'])
            total_bobot += bobot * nilai['sks']
            total_sks += nilai['sks']
        
        return total_bobot / total_sks if total_sks > 0 else 0.0
    
    def tambah_nilai(self, kode_matkul: str, nama_matkul: str, 
                    sks: int, nilai_akhir: float, semester: str, tahun: int):
        """Tambah nilai untuk mahasiswa"""
        nilai_data = {
            'kode_matkul': kode_matkul,
            'nama_matkul': nama_matkul,
            'sks': sks,
            'nilai_akhir': nilai_akhir,
            'semester': semester,
            'tahun': tahun,
            'timestamp': datetime.now().isoformat()
        }
        self.__nilai_list.append(nilai_data)
        self.hitung_ipk()  # Update IPK
    
    def tambah_absensi(self, kode_matkul: str, tanggal: str, status: StatusAbsen):
        """Tambah data absensi"""
        absensi_data = {
            'kode_matkul': kode_matkul,
            'tanggal': tanggal,
            'status': status.value,
            'timestamp': datetime.now().isoformat()
        }
        self.__absensi_list.append(absensi_data)
    
    def get_presensi_rate(self, kode_matkul: str = None) -> float:
        """Hitung persentase kehadiran"""
        if not self.__absensi_list:
            return 0.0
        
        filtered = self.__absensi_list
        if kode_matkul:
            filtered = [a for a in self.__absensi_list if a['kode_matkul'] == kode_matkul]
        
        total = len(filtered)
        hadir = len([a for a in filtered if a['status'] == StatusAbsen.HADIR.value])
        
        return (hadir / total * 100) if total > 0 else 0.0
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "nim": self.__nim,
            "jurusan": self.__jurusan,
            "angkatan": self.__angkatan,
            "ipk": self.__ipk,
            "total_sks": self.__total_sks,
            "nilai": self.__nilai_list[-10:],  # 10 nilai terakhir
            "absensi": self.__absensi_list[-20:],  # 20 absensi terakhir
            "presensi_rate": self.get_presensi_rate()
        })
        return base_dict

class Dosen(User):
    """Class khusus untuk dosen"""
    def __init__(self, nidn: str, nama: str, bidang: str):
        super().__init__(nidn, Role.DOSEN, nama)
        self.__nidn = nidn
        self.__bidang = bidang
        self.__mata_kuliah = []
    
    def tambah_matkul(self, kode: str, nama: str, sks: int, semester: str):
        """Tambah mata kuliah yang diampu"""
        matkul = {
            'kode': kode,
            'nama': nama,
            'sks': sks,
            'semester': semester,
            'mahasiswa_terdaftar': []
        }
        self.__mata_kuliah.append(matkul)
    
    def beri_nilai(self, nim_mahasiswa: str, kode_matkul: str, 
                  nilai_tugas: float, nilai_uts: float, nilai_uas: float):
        """Beri nilai ke mahasiswa"""
        # Hitung nilai akhir (bisa disesuaikan bobot)
        nilai_akhir = (nilai_tugas * 0.3 + nilai_uts * 0.3 + nilai_uas * 0.4)
        
        return {
            'nim': nim_mahasiswa,
            'kode_matkul': kode_matkul,
            'nilai_tugas': nilai_tugas,
            'nilai_uts': nilai_uts,
            'nilai_uas': nilai_uas,
            'nilai_akhir': nilai_akhir,
            'dosen': self.__nidn
        }
    
    def absensi_mahasiswa(self, nim_mahasiswa: str, kode_matkul: str, 
                         tanggal: str, status: StatusAbsen):
        """Input absensi mahasiswa"""
        return {
            'nim': nim_mahasiswa,
            'kode_matkul': kode_matkul,
            'tanggal': tanggal,
            'status': status.value,
            'dosen': self.__nidn
        }
    
    def to_dict(self):
        base_dict = super().to_dict()
        base_dict.update({
            "nidn": self.__nidn,
            "bidang": self.__bidang,
            "mata_kuliah": self.__mata_kuliah
        })
        return base_dict

# ========== DATABASE MANAGER ==========
class DatabaseManager:
    """Manager untuk semua operasi database dengan error handling"""
    def __init__(self):
        self.users_file = "data_users.json"
        self.mahasiswa_file = "data_mahasiswa.json"
        self.dosen_file = "data_dosen.json"
        self.mata_kuliah_file = "data_matkul.json"
        
        # In-memory storage
        self.users = self._load_json(self.users_file)
        self.mahasiswa_data = self._load_json(self.mahasiswa_file)
        self.dosen_data = self._load_json(self.dosen_file)
        self.mata_kuliah = self._load_json(self.mata_kuliah_file)
        
        # Auto create admin jika belum ada
        self._initialize_default_data()
    
    def _load_json(self, filename: str):
        """Load data dari file JSON dengan error handling"""
        try:
            if os.path.exists(filename):
                with open(filename, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return []
    
    def _save_json(self, filename: str, data):
        """Save data ke file JSON dengan error handling"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving {filename}: {e}")
            return False
    
    def _initialize_default_data(self):
        """Inisialisasi data default untuk pertama kali"""
        # Cek apakah admin sudah ada
        admin_exists = any(user.get('username') == 'admin' for user in self.users)
        
        if not admin_exists:
            admin = User("admin", Role.ADMIN, "Administrator", "admin@univ.ac.id")
            self.users.append(admin.to_dict())
            self._save_json(self.users_file, self.users)
        
        # Buat beberapa data dummy untuk testing
        if not self.mahasiswa_data:
            self._generate_sample_data()
    
    def _generate_sample_data(self):
        """Generate sample data untuk testing"""
        # Sample mahasiswa
        mhs1 = Mahasiswa("2023123001", "Budi Santoso", "Teknik Informatika", 2023)
        mhs2 = Mahasiswa("2023123002", "Siti Aminah", "Sistem Informasi", 2023)
        
        # Sample dosen
        dosen1 = Dosen("12345678", "Dr. Ahmad Wijaya, M.Kom", "Data Science")
        dosen1.tambah_matkul("TI101", "Pemrograman Dasar", 3, "ganjil")
        
        # Sample nilai
        mhs1.tambah_nilai("TI101", "Pemrograman Dasar", 3, 85.5, "ganjil", 2023)
        mhs1.tambah_absensi("TI101", "2023-09-01", StatusAbsen.HADIR)
        
        # Save to memory
        self.mahasiswa_data.append(mhs1.to_dict())
        self.mahasiswa_data.append(mhs2.to_dict())
        self.dosen_data.append(dosen1.to_dict())
        
        # Save to files
        self._save_json(self.mahasiswa_file, self.mahasiswa_data)
        self._save_json(self.dosen_file, self.dosen_data)
    
    def save_all(self):
        """Save semua data ke file"""
        self._save_json(self.users_file, self.users)
        self._save_json(self.mahasiswa_file, self.mahasiswa_data)
        self._save_json(self.dosen_file, self.dosen_data)
        self._save_json(self.mata_kuliah_file, self.mata_kuliah)
    
    # === CRUD Operations ===
    
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Autentikasi user dengan linear search"""
        # Time Complexity: O(n) - Linear Search
        for user in self.users:
            if user.get('username') == username:
                # In real app, password should be hashed
                if user.get('password', '').startswith('********'):
                    # Check from actual User object if exists
                    pass
                return user
        return None
    
    def create_mahasiswa(self, nama: str, jurusan: str, angkatan: int) -> dict:
        """Buat mahasiswa baru dengan NIM otomatis"""
        # Generate NIM: tahun + jurusan code + sequence
        jurusan_code = self._get_jurusan_code(jurusan)
        year_code = str(angkatan)[-2:]
        
        # Cari sequence terakhir
        existing_nims = [m['nim'] for m in self.mahasiswa_data 
                        if m['nim'].startswith(year_code + jurusan_code)]
        
        if existing_nims:
            last_seq = max(int(nim[-3:]) for nim in existing_nims)
            sequence = f"{last_seq + 1:03d}"
        else:
            sequence = "001"
        
        nim = f"{year_code}{jurusan_code}{sequence}"
        
        # Buat objek mahasiswa
        mahasiswa = Mahasiswa(nim, nama, jurusan, angkatan)
        mhs_dict = mahasiswa.to_dict()
        
        # Tambah ke users juga
        user_mhs = User(nim, Role.MAHASISWA, nama)
        user_mhs.set_password(f"maha#{nim[-4:]}")
        self.users.append(user_mhs.to_dict())
        
        self.mahasiswa_data.append(mhs_dict)
        self.save_all()
        
        return {
            "mahasiswa": mhs_dict,
            "login_info": {
                "username": nim,
                "password": f"maha#{nim[-4:]}"
            }
        }
    
    def _get_jurusan_code(self, jurusan: str) -> str:
        """Konversi nama jurusan ke kode"""
        codes = {
            "teknik informatika": "01",
            "sistem informasi": "02",
            "ilmu komputer": "03",
            "teknik elektro": "04",
            "manajemen": "05"
        }
        return codes.get(jurusan.lower(), "00")
    
    def get_user_by_username(self, username: str) -> Optional[dict]:
        """Cari user by username dengan binary search"""
        # Time Complexity: O(log n) setelah sorting
        sorted_users = sorted(self.users, key=lambda x: x['username'])
        
        low, high = 0, len(sorted_users) - 1
        while low <= high:
            mid = (low + high) // 2
            if sorted_users[mid]['username'] == username:
                return sorted_users[mid]
            elif sorted_users[mid]['username'] < username:
                low = mid + 1
            else:
                high = mid - 1
        return None
    
    def update_profile(self, username: str, **kwargs) -> bool:
        """Update profile user"""
        user = self.get_user_by_username(username)
        if not user:
            return False
        
        allowed_fields = ['nama', 'email', 'foto_profil']
        for field, value in kwargs.items():
            if field in allowed_fields:
                user[field] = value
        
        user['profile_complete'] = True
        self.save_all()
        return True
    
    def get_all_users_by_role(self, role: Role) -> list:
        """Get semua user berdasarkan role"""
        return [user for user in self.users if user.get('role') == role.value]

# Singleton instance
db_manager = DatabaseManager()