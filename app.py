from flask import Flask, render_template, request, jsonify
from database import Database

app = Flask(__name__)
db = Database()

# --- Halaman Utama (Frontend) ---
@app.route('/')
def index():
    return render_template('index.html')

# --- API ENDPOINTS (Backend JSON) ---

@app.route('/api/mahasiswa', methods=['GET'])
def get_mahasiswa():
    # Fitur Search & Sort bisa ditambahkan logic-nya di sini
    return jsonify(db.get_all())

@app.route('/api/mahasiswa', methods=['POST'])
def add_mahasiswa():
    data = request.json
    sukses = db.tambah(data['nama'], data['nim'], data['jurusan'], float(data['ipk']))
    if sukses:
        return jsonify({"message": "Berhasil tambah data"}), 201
    return jsonify({"message": "NIM Sudah ada!"}), 400

@app.route('/api/mahasiswa/<nim>', methods=['DELETE'])
def delete_mahasiswa(nim):
    if db.hapus(nim):
        return jsonify({"message": "Data dihapus"}), 200
    return jsonify({"message": "Data tidak ditemukan"}), 404

if __name__ == '__main__':
    app.run(debug=True)