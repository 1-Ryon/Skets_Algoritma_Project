from flask import Flask, render_template, request, jsonify
from backend_logic import DatabaseManager, UserManager
from functools import wraps

app = Flask(__name__)

# Inisialisasi Logic
db = DatabaseManager()
user_db = UserManager()

# --- Custom Auth Decorator (Pengganti Depends FastAPI) ---
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Ambil token dari Header: "Authorization: Bearer <token>"
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            if " " in auth_header:
                token = auth_header.split(" ")[1]
        
        if not token:
            return jsonify({'detail': 'Token is missing!'}), 401
        
        # Validasi Token (Disini token = username agar simpel)
        user = next((u for u in user_db.users if u['username'] == token), None)
        if not user:
            return jsonify({'detail': 'Token invalid / User not found'}), 401
            
        return f(current_user=user, *args, **kwargs)
    return decorated

# --- Routes Tampilan (HTML) ---
@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard_page():
    return render_template('dashboard.html')

# --- API Endpoints ---

@app.route('/token', methods=['POST'])
def login():
    # Menerima Form Data (seperti dari script.js lama)
    username = request.form.get('username')
    password = request.form.get('password')
    
    user = user_db.authenticate(username, password)
    if not user:
        return jsonify({"detail": "Username/Password salah"}), 400
    
    return jsonify({
        "access_token": user['username'], 
        "role": user['role']
    })

@app.route('/api/mahasiswa', methods=['GET'])
def get_all():
    sort_by = request.args.get('sort_by')
    search = request.args.get('search')
    
    data = db.data
    
    # Searching Manual (Binary/Linear)
    if search:
        if search.isdigit():
            found = db.binary_search_nim(search)
            data = [found] if found else []
        else:
            data = [m for m in data if search.lower() in m['nama'].lower()]

    # Sorting Manual (Bubble Sort)
    if sort_by == "ipk_desc":
        data = db.bubble_sort_by_ipk(ascending=False)
    elif sort_by == "ipk_asc":
        data = db.bubble_sort_by_ipk(ascending=True)
            
    return jsonify(data)

@app.route('/api/mahasiswa', methods=['POST'])
@token_required
def add_mhs(current_user):
    # Cek Role
    if current_user['role'] != 'admin':
        return jsonify({"detail": "Hanya Admin boleh menambah data"}), 403
    
    data = request.get_json()
    try:
        # Tambah Data & Generate NIM
        new_mhs = db.add_mahasiswa_data(data['nama'], data['jurusan'], float(data['ipk']))
        
        # Auto Generate Akun Login
        generated_nim = new_mhs['nim']
        generated_pass = f"maha#{generated_nim[-4:]}"
        user_db.create_user(generated_nim, generated_pass, "mahasiswa")
        
        return jsonify({
            "message": "Sukses",
            "data": new_mhs,
            "account_info": {"initial_password": generated_pass}
        })
    except ValueError as e:
        return jsonify({"detail": str(e)}), 400

@app.route('/api/mahasiswa/<nim>', methods=['DELETE'])
@token_required
def delete_mhs(current_user, nim):
    if current_user['role'] != 'admin':
        return jsonify({"detail": "Hanya Admin boleh menghapus"}), 403
    
    if db.delete_mahasiswa_data(nim):
        user_db.delete_user(nim) # Hapus akun juga
        return jsonify({"message": "Terhapus"})
        
    return jsonify({"detail": "Data tidak ditemukan"}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)