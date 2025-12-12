// Main JavaScript untuk Sistem Akademik Lengkap

// ========== GLOBAL VARIABLES ==========
const API_BASE = window.location.origin;
let currentUser = null;

// ========== INITIALIZATION ==========
document.addEventListener('DOMContentLoaded', function() {
    checkAuth();
    loadUserData();
    initTheme();
    initWhatsApp();
    updateCurrentTime();
    setInterval(updateCurrentTime, 60000);
});

// ========== AUTH FUNCTIONS ==========
function checkAuth() {
    const token = localStorage.getItem('token');
    const currentPath = window.location.pathname;
    
    if (!token && !currentPath.includes('/login') && currentPath !== '/') {
        window.location.href = '/';
        return false;
    }
    
    if (token && (currentPath === '/' || currentPath.includes('/login'))) {
        window.location.href = '/dashboard';
        return false;
    }
    
    return true;
}

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
        } else if (response.status === 401) {
            logout();
        }
    } catch (error) {
        console.error('Failed to load user data:', error);
    }
}

function updateUIWithUserData() {
    if (!currentUser) return;
    
    // Update avatar
    const avatars = document.querySelectorAll('#userAvatar, .avatar');
    avatars.forEach(avatar => {
        if (currentUser.foto_profil) {
            avatar.src = currentUser.foto_profil;
        }
    });
    
    // Update username display
    const usernameElements = document.querySelectorAll('#usernameDisplay');
    usernameElements.forEach(el => {
        if (el) el.textContent = currentUser.nama;
    });
    
    // Update role badge
    const roleBadges = document.querySelectorAll('#userRole');
    roleBadges.forEach(badge => {
        if (badge) {
            badge.textContent = currentUser.role.toUpperCase();
            badge.className = `role-badge ${currentUser.role}`;
        }
    });
}

function logout() {
    if (confirm('Apakah Anda yakin ingin logout?')) {
        localStorage.clear();
        window.location.href = '/';
    }
}

// ========== THEME MANAGEMENT ==========
function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
}

function toggleDarkMode() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
    
    // Update toggle button if exists
    const themeToggle = document.getElementById('themeToggle');
    if (themeToggle) {
        themeToggle.innerHTML = theme === 'dark' 
            ? '<i class="fas fa-sun"></i>' 
            : '<i class="fas fa-moon"></i>';
    }
}

// ========== WHATSAPP INTEGRATION ==========
function initWhatsApp() {
    const whatsappBtns = document.querySelectorAll('#whatsappBtn, .whatsapp-link');
    whatsappBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            const phone = '6282213407223';
            const message = 'Halo, saya butuh bantuan terkait Sistem Manajemen Akademik';
            const whatsappUrl = `https://wa.me/${phone}?text=${encodeURIComponent(message)}`;
            window.open(whatsappUrl, '_blank');
        });
    });
}

// ========== SIDEBAR FUNCTIONS ==========
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
        sidebar.classList.toggle('collapsed');
    }
}

// ========== UTILITY FUNCTIONS ==========
function updateCurrentTime() {
    const now = new Date();
    const timeElements = document.querySelectorAll('#currentTime');
    
    timeElements.forEach(el => {
        if (el) {
            el.textContent = now.toLocaleDateString('id-ID', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
            });
        }
    });
}

function showAlert(type, message, duration = 5000) {
    // Create alert container if not exists
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
    
    // Create alert element
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.style.cssText = `
        background-color: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
        color: white;
        padding: 1rem;
        margin-bottom: 0.5rem;
        border-radius: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        animation: slideIn 0.3s ease;
    `;
    
    alert.innerHTML = `
        <span>${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()" style="
            background: none;
            border: none;
            color: white;
            font-size: 1.2rem;
            cursor: pointer;
            margin-left: 1rem;
        ">&times;</button>
    `;
    
    container.appendChild(alert);
    
    // Auto remove after duration
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, duration);
    
    // Add CSS animation
    if (!document.querySelector('#alertAnimations')) {
        const style = document.createElement('style');
        style.id = 'alertAnimations';
        style.textContent = `
            @keyframes slideIn {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// ========== FORM VALIDATION ==========
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validateNIM(nim) {
    const re = /^\d{10}$/;
    return re.test(nim);
}

function validateNIDN(nidn) {
    const re = /^\d{8}$/;
    return re.test(nidn);
}

function validatePhone(phone) {
    const re = /^08[1-9][0-9]{7,10}$/;
    return re.test(phone);
}

// ========== DATA EXPORT ==========
function exportToCSV(data, filename = 'data') {
    if (!data || data.length === 0) {
        showAlert('warning', 'Tidak ada data untuk diexport');
        return;
    }
    
    try {
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
        const blob = new Blob([csvString], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        
        const link = document.createElement('a');
        link.href = url;
        link.download = `${filename}_${new Date().toISOString().slice(0,10)}.csv`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        showAlert('success', 'Data berhasil diexport');
    } catch (error) {
        showAlert('error', 'Gagal export data: ' + error.message);
    }
}

// ========== PAGINATION ==========
function createPagination(totalItems, itemsPerPage, currentPage, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const totalPages = Math.ceil(totalItems / itemsPerPage);
    let html = '<div class="pagination">';
    
    // Previous button
    html += `<button class="page-link ${currentPage === 1 ? 'disabled' : ''}" 
              onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>
                &laquo; Prev
            </button>`;
    
    // Page numbers
    for (let i = 1; i <= totalPages; i++) {
        if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
            html += `<button class="page-link ${i === currentPage ? 'active' : ''}" 
                      onclick="changePage(${i})">${i}</button>`;
        } else if (i === currentPage - 3 || i === currentPage + 3) {
            html += '<span class="page-dots">...</span>';
        }
    }
    
    // Next button
    html += `<button class="page-link ${currentPage === totalPages ? 'disabled' : ''}" 
              onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>
                Next &raquo;
            </button>`;
    
    html += '</div>';
    container.innerHTML = html;
}

// ========== MODAL MANAGEMENT ==========
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

// Close modal when clicking outside
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
});

// Close modal with Escape key
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
        document.body.style.overflow = 'auto';
    }
});

// ========== API CALL WRAPPER ==========
async function apiCall(endpoint, method = 'GET', data = null) {
    const token = localStorage.getItem('token');
    const headers = {
        'Authorization': `Bearer ${token}`
    };
    
    let options = {
        method: method,
        headers: headers
    };
    
    if (data) {
        if (data instanceof FormData) {
            options.body = data;
        } else {
            headers['Content-Type'] = 'application/json';
            options.body = JSON.stringify(data);
        }
    }
    
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        
        if (response.status === 401) {
            logout();
            throw new Error('Session expired. Please login again.');
        }
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.detail || `HTTP ${response.status}`);
        }
        
        return result;
    } catch (error) {
        console.error('API Error:', error);
        showAlert('error', error.message);
        throw error;
    }
}

// ========== ERROR HANDLING ==========
window.addEventListener('error', function(event) {
    console.error('Global error:', event.error);
    showAlert('error', 'Terjadi kesalahan: ' + event.error.message);
});

window.addEventListener('unhandledrejection', function(event) {
    console.error('Unhandled promise rejection:', event.reason);
    showAlert('error', 'Kesalahan sistem: ' + event.reason.message);
});

// ========== OFFLINE DETECTION ==========
window.addEventListener('online', function() {
    showAlert('success', 'Anda kembali online');
});

window.addEventListener('offline', function() {
    showAlert('warning', 'Anda sedang offline. Beberapa fitur mungkin tidak tersedia.');
});

// ========== LOADING INDICATOR ==========
function showLoading(show = true) {
    let loader = document.getElementById('loadingIndicator');
    
    if (show) {
        if (!loader) {
            loader = document.createElement('div');
            loader.id = 'loadingIndicator';
            loader.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.5);
                display: flex;
                justify-content: center;
                align-items: center;
                z-index: 9999;
            `;
            loader.innerHTML = `
                <div class="spinner" style="
                    width: 50px;
                    height: 50px;
                    border: 5px solid #f3f3f3;
                    border-top: 5px solid #4f46e5;
                    border-radius: 50%;
                    animation: spin 1s linear infinite;
                "></div>
            `;
            document.body.appendChild(loader);
            
            // Add animation
            const style = document.createElement('style');
            style.textContent = `
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `;
            document.head.appendChild(style);
        }
        loader.style.display = 'flex';
    } else if (loader) {
        loader.style.display = 'none';
    }
}

// ========== DEBOUNCE FUNCTION ==========
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ========== FORMAT FUNCTIONS ==========
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
}

function formatDateTime(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('id-ID', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatNumber(num, decimals = 2) {
    if (num === null || num === undefined) return '-';
    return Number(num).toFixed(decimals);
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR'
    }).format(amount);
}

// ========== INITIALIZE ON LOAD ==========
// Auto-check auth on page changes
window.addEventListener('pageshow', function(event) {
    if (event.persisted) {
        checkAuth();
    }
});

// Initialize service worker for PWA
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