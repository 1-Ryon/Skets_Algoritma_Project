const API_URL = "/api/mahasiswa";

// --- AUTHENTICATION HELPER ---
function getToken() {
    return localStorage.getItem('token');
}

function getRole() {
    return localStorage.getItem('role');
}

function checkAuth() {
    // Jika tidak ada token, tendang ke halaman login
    if (!getToken()) {
        window.location.href = '/'; 
        return;
    }

    // Tampilkan info user
    const userInfo = document.getElementById('userInfo');
    if (userInfo) {
        userInfo.innerText = `User: ${getToken()} | Role: ${getRole()}`;
    }

    // Authorization Frontend: Sembunyikan form input jika bukan admin
    if (getRole() === 'admin') {
        const adminSec = document.getElementById('adminSection');
        if (adminSec) adminSec.style.display = 'block';
    } else {
        // Jika mahasiswa, sembunyikan kolom aksi (delete) di header tabel jika perlu
        // (Opsional, tergantung desain tabel)
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('role');
    window.location.href = '/';
}

// --- DATA MANAGEMENT ---

// 1. Load Data (GET)
async function loadData() {
    // Ambil elemen filter jika ada
    const sortEl = document.getElementById('sortSelect');
    const searchEl = document.getElementById('searchInput');
    
    const sort = sortEl ? sortEl.value : '';
    const search = searchEl ? searchEl.value : '';

    try {
        const res = await fetch(`${API_URL}?sort_by=${sort}&search=${search}`, {
            headers: {
                'Authorization': `Bearer ${getToken()}` // Kirim Token
            }
        });

        if (res.status === 401) { logout(); return; } // Token expired

        const data = await res.json();
        const tbody = document.getElementById('tableBody');
        tbody.innerHTML = '';

        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5" style="text-align:center;">Data tidak ditemukan</td></tr>';
            return;
        }

        data.forEach(mhs => {
            let btnDelete = '';
            // Tombol Hapus hanya muncul untuk Admin
            if (getRole() === 'admin') {
                btnDelete = `<button onclick="deleteData('${mhs.nim}')" class="btn-delete">Hapus</button>`;
            }

            tbody.innerHTML += `
                <tr>
                    <td>${mhs.nim}</td>
                    <td>${mhs.nama}</td>
                    <td>${mhs.jurusan}</td>
                    <td>${mhs.ipk}</td>
                    <td>${btnDelete}</td>
                </tr>
            `;
        });
    } catch (error) {
        console.error("Gagal load data:", error);
    }
}

// 2. Add Data (POST) - Khusus Admin
async function addData() {
    const namaVal = document.getElementById('nama').value;
    const jurusanVal = document.getElementById('jurusan').value;
    const ipkVal = document.getElementById('ipk').value;

    if (!namaVal || !jurusanVal || !ipkVal) {
        alert("Semua field harus diisi!");
        return;
    }

    const data = {
        nama: namaVal,
        jurusan: jurusanVal,
        ipk: parseFloat(ipkVal)
    };

    try {
        const res = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${getToken()}`
            },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (res.ok) {
            // --- INI BAGIAN PENTING ---
            // Menampilkan Alert berisi NIM & Password Otomatis
            alert(`✅ SUKSES TAMBAH DATA!\n\nNIM Baru: ${result.data.nim}\nPassword Awal: ${result.account_info.initial_password}\n\n(Harap catat password ini untuk mahasiswa ybs)`);
            
            // Bersihkan Form
            document.getElementById('nama').value = '';
            document.getElementById('jurusan').value = '';
            document.getElementById('ipk').value = '';
            
            loadData(); // Refresh tabel
        } else {
            alert("Gagal: " + result.detail);
        }
    } catch (error) {
        alert("Terjadi kesalahan sistem");
    }
}

// 3. Delete Data (DELETE) - Khusus Admin
async function deleteData(nim) {
    if (!confirm(`Yakin ingin menghapus data NIM ${nim}?\nAkun login mahasiswa ini juga akan dihapus.`)) return;

    try {
        const res = await fetch(`${API_URL}/${nim}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${getToken()}`
            }
        });

        if (res.ok) {
            loadData();
        } else {
            const result = await res.json();
            alert("Gagal menghapus: " + result.detail);
        }
    } catch (error) {
        alert("Terjadi kesalahan saat menghapus");
    }
}