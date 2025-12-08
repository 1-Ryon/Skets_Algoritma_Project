import os
from abc import ABC, abstractmethod

# --- OOP: Abstract Base Class ---
class Person(ABC):
    def __init__(self, nama):
        self._nama = nama

# --- OOP: Inheritance & Encapsulation ---
class Mahasiswa(Person):
    def __init__(self, nama, nim, jurusan, ipk):
        super().__init__(nama)
        self._nim = nim
        self._jurusan = jurusan
        self._ipk = ipk

    # Dictionary untuk konversi ke JSON
    def to_dict(self):
        return {
            "nim": self._nim,
            "nama": self._nama,
            "jurusan": self._jurusan,
            "ipk": self._ipk
        }

    def to_csv(self):
        return f"{self._nim};{self._nama};{self._jurusan};{self._ipk}"

class Database:
    def __init__(self):
        self.filename = "data_mahasiswa.txt"
        self.data = []
        self.muat_file()

    def muat_file(self):
        self.data = []
        if os.path.exists(self.filename):
            with open(self.filename, 'r') as f:
                for line in f:
                    parts = line.strip().split(';')
                    if len(parts) == 4:
                        self.data.append(Mahasiswa(parts[1], parts[0], parts[2], float(parts[3])))

    def simpan_file(self):
        with open(self.filename, 'w') as f:
            for mhs in self.data:
                f.write(mhs.to_csv() + "\n")

    def get_all(self):
        return [mhs.to_dict() for mhs in self.data]

    def tambah(self, nama, nim, jurusan, ipk):
        # Cek duplikat
        if any(m._nim == nim for m in self.data):
            return False
        self.data.append(Mahasiswa(nama, nim, jurusan, ipk))
        self.simpan_file()
        return True

    def hapus(self, nim):
        awal = len(self.data)
        self.data = [m for m in self.data if m._nim != nim]
        if len(self.data) < awal:
            self.simpan_file()
            return True
        return False