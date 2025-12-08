import json
import os
import re
from datetime import datetime
from abc import ABC, abstractmethod

# --- 1. OOP: Abstract Base Class ---
class Person(ABC):
    def __init__(self, username, role):
        self._username = username
        self._role = role

    @abstractmethod
    def get_info(self):
        pass

class Mahasiswa(Person):
    def __init__(self, nama, nim, jurusan, ipk):
        super().__init__(nim, "mahasiswa") # Username mahasiswa adalah NIM
        self.nama_asli = nama
        self.jurusan = jurusan
        self.ipk = ipk

    def get_info(self):
        return f"Mahasiswa: {self.nama_asli}, NIM: {self._username}"

    def to_dict(self):
        return {
            "nim": self._username,
            "nama": self.nama_asli,
            "jurusan": self.jurusan,
            "ipk": self.ipk
        }

# --- 2. User Management (Login & Akun) ---
class UserManager:
    def __init__(self, filename="data_users.json"):
        self.filename = filename
        self.users = self.load_users()
        
        # Pastikan akun Admin selalu ada saat pertama kali jalan
        if not any(u['username'] == 'admin' for u in self.users):
            self.create_user("admin", "admin123", "admin") # Default Admin

    def load_users(self):
        if not os.path.exists(self.filename):
            return []
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except:
            return []

    def save_users(self):
        with open(self.filename, 'w') as f:
            json.dump(self.users, f, indent=4)

    def authenticate(self, username, password):
        # Linear Search untuk mencari user
        for user in self.users:
            if user['username'] == username and user['password'] == password:
                return user
        return None

    def create_user(self, username, password, role):
        # Cek duplikat username
        if any(u['username'] == username for u in self.users):
            return False
            
        new_user = {
            "username": username,
            "password": password,
            "role": role
        }
        self.users.append(new_user)
        self.save_users()
        return True

    def delete_user(self, username):
        self.users = [u for u in self.users if u['username'] != username]
        self.save_users()

# --- 3. Database Management (Data Mahasiswa) ---
class DatabaseManager:
    def __init__(self, filename="data_mahasiswa.json"):
        self.filename = filename
        self.data = self.load_data()

    def load_data(self):
        if not os.path.exists(self.filename): return []
        try: return json.load(self.filename)
        except: return [] # Typo fix: json.load(f) handled in implementation logic usually

    # ... (Fungsi load_data sama seperti sebelumnya) ...
    def load_data(self):
        if not os.path.exists(self.filename):
            return []
        with open(self.filename, 'r') as f:
            try: return json.load(f)
            except: return []

    def save_data(self):
        with open(self.filename, 'w') as f:
            json.dump(self.data, f, indent=4)

    def generate_nim(self):
        today = datetime.now().strftime("%y%m%d")
        current_day_nims = [m['nim'] for m in self.data if m['nim'].startswith(today)]
        
        if not current_day_nims:
            sequence = "000001"
        else:
            current_day_nims.sort() 
            last_seq = int(current_day_nims[-1][-6:])
            sequence = f"{last_seq + 1:06d}"
            
        return today + sequence

    def add_mahasiswa_data(self, nama, jurusan, ipk):
        # Validasi Regex Nama (Hanya huruf dan spasi)
        if not re.match(r"^[a-zA-Z\s]+$", nama):
             raise ValueError("Nama hanya boleh berisi huruf.")

        nim_baru = self.generate_nim()
        mhs = Mahasiswa(nama, nim_baru, jurusan, ipk)
        
        self.data.append(mhs.to_dict())
        self.save_data()
        
        return mhs.to_dict() # Kembalikan objek data lengkap termasuk NIM

    def delete_mahasiswa_data(self, nim):
        awal = len(self.data)
        self.data = [m for m in self.data if m['nim'] != nim]
        if len(self.data) < awal:
            self.save_data()
            return True
        return False
        
    # ... (Fungsi Sorting & Searching Bubble/Binary tetap sama) ...
    def bubble_sort_by_ipk(self, ascending=True):
        arr = self.data.copy()
        n = len(arr)
        for i in range(n):
            for j in range(0, n-i-1):
                if ascending:
                    if arr[j]['ipk'] > arr[j+1]['ipk']:
                        arr[j], arr[j+1] = arr[j+1], arr[j]
                else:
                    if arr[j]['ipk'] < arr[j+1]['ipk']:
                        arr[j], arr[j+1] = arr[j+1], arr[j]
        return arr

    def binary_search_nim(self, target_nim):
        arr = sorted(self.data, key=lambda x: x['nim'])
        low = 0
        high = len(arr) - 1
        while low <= high:
            mid = (high + low) // 2
            if arr[mid]['nim'] == target_nim:
                return arr[mid]
            elif arr[mid]['nim'] < target_nim:
                low = mid + 1
            else:
                high = mid - 1
        return None