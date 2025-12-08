document.addEventListener('DOMContentLoaded', loadData);

// --- Fungsi 1: Ambil Data dari API (GET) ---
function loadData() {
    fetch('/api/mahasiswa')
        .then(response => response.json())
        .then(data => {
            const tbody = document.querySelector('#tabelMahasiswa tbody');
            tbody.innerHTML = ''; // Bersihkan tabel

            if(data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" style="text-align:center">Belum ada data</td></tr>';
                return;
            }

            data.forEach(mhs => {
                const row = `
                    <tr>
                        <td>${mhs.nim}</td>
                        <td>${mhs.nama}</td>
                        <td>${mhs.jurusan}</td>
                        <td>${mhs.ipk}</td>
                        <td>
                            <button onclick="hapusData('${mhs.nim}')" class="btn-delete">Hapus</button>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        });
}

// --- Fungsi 2: Kirim Data ke API (POST) ---
document.getElementById('formMahasiswa').addEventListener('submit', function(e) {
    e.preventDefault(); // Cegah reload halaman

    const data = {
        nim: document.getElementById('nim').value,
        nama: document.getElementById('nama').value,
        jurusan: document.getElementById('jurusan').value,
        ipk: document.getElementById('ipk').value
    };

    fetch('/api/mahasiswa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) throw new Error("Gagal menyimpan / NIM Duplikat");
        return response.json();
    })
    .then(result => {
        alert('Sukses: ' + result.message);
        document.getElementById('formMahasiswa').reset(); // Bersihkan form
        loadData(); // Refresh tabel otomatis
    })
    .catch(error => {
        alert('Error: ' + error.message);
    });
});

// --- Fungsi 3: Hapus Data via API (DELETE) ---
function hapusData(nim) {
    if(!confirm('Yakin ingin menghapus NIM ' + nim + '?')) return;

    fetch(`/api/mahasiswa/${nim}`, {
        method: 'DELETE'
    })
    .then(response => response.json())
    .then(result => {
        loadData(); // Refresh tabel
    });
}