// Main JavaScript untuk Sistem Akademik

// ========== GLOBAL VARIABLES ==========
const API_BASE = window.location.origin;
let currentUser = null;

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication
    checkAuth();
    
    // Initialize components
    initTheme();
    initWhatsAppLink();
    initSearch();
    initModals();
    
    // Load user data
    loadUserData();
    
    // Update time every minute
    updateCurrentTime();
    setInterval(updateCurrentTime, 60000);
});

// ========== AUTH FUNCTIONS ==========
function checkAuth() {
    const token = localStorage.getItem('token');
    if (!token && !window.location.pathname.includes('/login')) {
        window.location.href = '/';
    }
}

async function login(username, password) {
    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch('/api/login', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Login failed');
        }
        
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        
        window.location.href = '/dashboard';
    } catch (error) {
        showAlert('error', 'Login gagal: ' + error.message);
    }
}

function logout() {
    localStorage.clear();
    window.location.href = '/';
}

// ========== THEME MANAGEMENT ==========
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
    
    // Theme toggle button
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
        themeToggle.innerHTML = savedTheme === 'dark' 
            ? '<i class="fas fa-sun"></i>' 
            : '<i class="fas fa-moon"></i>';
    }
}

function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    
    // Update toggle button icon
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.innerHTML = newTheme === 'dark' 
            ? '<i class="fas fa-sun"></i>' 
            : '<i class="fas fa-moon"></i>';
    }
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
}

// ========== USER FUNCTIONS ==========
async function loadUserData() {
    const token = localStorage.getItem('token');
    if (!token) return;
    
    try {
        const response = await fetch('/api/user/me', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (response.ok) {
            currentUser = await response.json();
            updateUIWithUserData();
        }
    } catch (error) {
        console.error('Failed to load user data:', error);
    }
}

function updateUIWithUserData() {
    if (!currentUser) return;
    
    // Update avatar
    const avatar = document.getElementById('userAvatar');
    if (avatar && currentUser.foto_profil) {
        avatar.src = currentUser.foto_profil;
    }
    
    // Update username
    const usernameElement = document.getElementById('usernameDisplay');
    if (usernameElement) {
        usernameElement.textContent = currentUser.nama;
    }
    
    // Update role badge
    const roleBadge = document.getElementById('userRole');
    if (roleBadge) {
        roleBadge.textContent = currentUser.role.toUpperCase();
        roleBadge.className = `role-badge ${currentUser.role}`;
    }
}

// ========== SEARCH FUNCTIONALITY ==========
function initSearch() {
    const searchInput = document.getElementById('globalSearch');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                performSearch(this.value);
            }
        });
        
        // Debounce untuk performa
        let timeout;
        searchInput.addEventListener('input', function() {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                if (this.value.length > 2) {
                    performSearch(this.value);
                }
            }, 500);
        });
    }
}

async function performSearch(query) {
    try {
        const response = await fetch(`/api/search?q=${encodeURIComponent(query)}`);
        const results = await response.json();
        displaySearchResults(results);
    } catch (error) {
        console.error('Search failed:', error);
    }
}

function displaySearchResults(results) {
    // Implementasi display search results
    // Bisa berupa modal atau update table
    console.log('Search results:', results);
}

// ========== MODAL FUNCTIONS ==========
function initModals() {
    // Close modal when clicking outside
    document.addEventListener('click', function(event) {
        if (event.target.classList.contains('modal')) {
            closeAllModals();
        }
    });
    
    // Close modal with Escape key
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            closeAllModals();
        }
    });
}

function showModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

function closeAllModals() {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.style.display = 'none';
    });
    document.body.style.overflow = 'auto';
}

// ========== ALGORITHM DEMO ==========
async function demoSorting(algorithm, key = 'nama') {
    try {
        const response = await fetch(`/api/sort?algorithm=${algorithm}&key=${key}`);
        const result = await response.json();
        
        showAlert('info', 
            `Algoritma: ${result.algorithm.toUpperCase()}\n` +
            `Waktu eksekusi: ${result.execution_time_ms?.toFixed(2)}ms\n` +
            `Time Complexity: ${result.time_complexity}`
        );
        
        return result.sorted_data;
    } catch (error) {
        showAlert('error', 'Demo sorting gagal: ' + error.message);
    }
}

async function demoSearching(algorithm, value) {
    try {
        const response = await fetch(`/api/search?algorithm=${algorithm}&q=${value}`);
        const result = await response.json();
        
        showAlert('info',
            `Algoritma: ${result.algorithm.toUpperCase()}\n` +
            `Hasil ditemukan: ${result.count || (result.found ? 'Ya' : 'Tidak')}\n` +
            `Waktu eksekusi: ${result.execution_time_ms?.toFixed(2)}ms`
        );
        
        return result.results || result.result;
    } catch (error) {
        showAlert('error', 'Demo searching gagal: ' + error.message);
    }
}

// ========== DATA TABLE FUNCTIONS ==========
function renderDataTable(data, containerId, columns) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    let html = `
        <div class="table-responsive">
            <table class="data-table">
                <thead>
                    <tr>
                        ${columns.map(col => `<th>${col.label}</th>`).join('')}
                        <th>Aksi</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    data.forEach(item => {
        html += '<tr>';
        columns.forEach(col => {
            html += `<td>${item[col.key] || ''}</td>`;
        });
        html += `
            <td>
                <button class="btn-icon" onclick="editItem('${item.id}')">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon btn-danger" onclick="deleteItem('${item.id}')">
                    <i class="fas fa-trash"></i>
                </button>
            </td>
        </tr>`;
    });
    
    html += `
                </tbody>
            </table>
        </div>
    `;
    
    container.innerHTML = html;
}

// ========== FORM HANDLING ==========
async function submitForm(formId, endpoint, method = 'POST') {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const formData = new FormData(form);
    
    try {
        const response = await fetch(endpoint, {
            method: method,
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: formData
        });
        
        const result = await response.json();
        
        if (response.ok) {
            showAlert('success', result.message || 'Operasi berhasil');
            form.reset();
            closeAllModals();
            // Refresh data jika perlu
            if (typeof refreshData === 'function') {
                refreshData();
            }
        } else {
            showAlert('error', result.detail || 'Operasi gagal');
        }
    } catch (error) {
        showAlert('error', 'Terjadi kesalahan: ' + error.message);
    }
}

// ========== FILE UPLOAD ==========
async function uploadFile(file, endpoint) {
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: formData
        });
        
        return await response.json();
    } catch (error) {
        throw error;
    }
}

// ========== NOTIFICATION SYSTEM ==========
function showAlert(type, message) {
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `
        <span>${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;
    
    // Add to alert container
    let container = document.getElementById('alertContainer');
    if (!container) {
        container = document.createElement('div');
        container.id = 'alertContainer';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(container);
    }
    
    container.appendChild(alert);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 5000);
}

// ========== UTILITY FUNCTIONS ==========
function updateCurrentTime() {
    const now = new Date();
    const timeElement = document.getElementById('currentTime');
    if (timeElement) {
        timeElement.textContent = now.toLocaleString('id-ID', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID');
}

function formatNumber(num, decimals = 2) {
    return num.toFixed(decimals);
}

function initWhatsAppLink() {
    const whatsappBtn = document.getElementById('whatsappBtn');
    if (whatsappBtn) {
        whatsappBtn.addEventListener('click', function() {
            const phone = '6282213407223';
            const message = 'Halo, saya butuh bantuan terkait Sistem Manajemen Akademik';
            window.open(`https://wa.me/${phone}?text=${encodeURIComponent(message)}`, '_blank');
        });
    }
}

function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    sidebar.classList.toggle('collapsed');
    mainContent.classList.toggle('expanded');
}

// ========== DATA VISUALIZATION ==========
function createChart(ctx, type, data, options) {
    return new Chart(ctx, {
        type: type,
        data: data,
        options: options
    });
}

// ========== EXPORT FUNCTIONS ==========
function exportToCSV(data, filename) {
    if (!data.length) return;
    
    const headers = Object.keys(data[0]);
    const csvRows = [
        headers.join(','),
        ...data.map(row => 
            headers.map(header => 
                JSON.stringify(row[header] || '')
            ).join(',')
        )
    ];
    
    const csvString = csvRows.join('\n');
    const blob = new Blob([csvString], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.csv`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// ========== VALIDATION FUNCTIONS ==========
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validateNIM(nim) {
    const re = /^\d{10}$/;
    return re.test(nim);
}

function validatePhone(phone) {
    const re = /^08[1-9][0-9]{7,10}$/;
    return re.test(phone);
}

// ========== EVENT LISTENERS ==========
// Global event listener untuk aksi umum
document.addEventListener('click', function(event) {
    // Handle delete buttons
    if (event.target.closest('.btn-delete')) {
        const button = event.target.closest('.btn-delete');
        const id = button.dataset.id;
        const type = button.dataset.type;
        
        if (id && type) {
            if (confirm(`Apakah Anda yakin ingin menghapus ${type} ini?`)) {
                deleteItem(id, type);
            }
        }
    }
    
    // Handle edit buttons
    if (event.target.closest('.btn-edit')) {
        const button = event.target.closest('.btn-edit');
        const id = button.dataset.id;
        const type = button.dataset.type;
        
        if (id && type) {
            editItem(id, type);
        }
    }
});

// ========== ERROR HANDLING ==========
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    showAlert('error', 'Terjadi kesalahan: ' + event.error.message);
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showAlert('error', 'Kesalahan sistem: ' + event.reason.message);
});

// ========== WEBSOCKET FOR REAL-TIME UPDATES ==========
let socket = null;

function connectWebSocket() {
    if (socket) return;
    
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    socket = new WebSocket(wsUrl);
    
    socket.onopen = function() {
        console.log('WebSocket connected');
    };
    
    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };
    
    socket.onclose = function() {
        console.log('WebSocket disconnected');
        socket = null;
        // Reconnect after 5 seconds
        setTimeout(connectWebSocket, 5000);
    };
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case 'notification':
            showAlert('info', data.message);
            break;
        case 'data_update':
            // Refresh data jika ada perubahan
            if (typeof refreshData === 'function') {
                refreshData();
            }
            break;
    }
}

// ========== INITIALIZE WEBSOCKET ==========
if (window.location.pathname !== '/') {
    connectWebSocket();
}

// ========== PWA SUPPORT ==========
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/service-worker.js')
            .then(function(registration) {
                console.log('ServiceWorker registered with scope:', registration.scope);
            })
            .catch(function(error) {
                console.log('ServiceWorker registration failed:', error);
            });
    });
}

// ========== OFFLINE SUPPORT ==========
window.addEventListener('online', function() {
    showAlert('success', 'Anda kembali online');
});

window.addEventListener('offline', function() {
    showAlert('warning', 'Anda sedang offline. Beberapa fitur mungkin tidak tersedia.');
});