// SmartClean API Utilities
const API_BASE = '/api';

// Debounce function
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

// Throttle function
function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// API request helper
async function apiRequest(endpoint, options = {}) {
  const token = localStorage.getItem('token');
  
  const config = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { 'Authorization': `Bearer ${token}` }),
      ...options.headers
    }
  };
  
  const response = await fetch(`${API_BASE}${endpoint}`, config);
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new Error(error.detail || 'Request failed');
  }
  
  return response.json();
}

// Get all cleaners
async function getCleaners() {
  return apiRequest('/cleaners');
}

// Get all orders
async function getOrders(status, page = 1, limit = 20) {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  params.append('page', page);
  params.append('limit', limit);
  return apiRequest(`/orders?${params}`);
}

// Get order by ID
async function getOrder(id) {
  return apiRequest(`/orders/${id}`);
}

// Create order
async function createOrder(data) {
  return apiRequest('/orders', {
    method: 'POST',
    body: JSON.stringify(data)
  });
}

// Accept order
async function acceptOrder(orderId, cleanerId) {
  return apiRequest(`/orders/${orderId}/accept`, {
    method: 'POST',
    body: JSON.stringify({ cleaner_id: cleanerId })
  });
}

// Complete order
async function completeOrder(orderId, photos) {
  return apiRequest(`/orders/${orderId}/complete`, {
    method: 'POST',
    body: JSON.stringify({ photos })
  });
}

// Verify order
async function verifyOrder(orderId) {
  return apiRequest(`/orders/${orderId}/verify-accept`, {
    method: 'POST'
  });
}

// Get stats
async function getStats() {
  return apiRequest('/stats');
}

// Upload image
async function uploadImage(file) {
  const formData = new FormData();
  formData.append('file', file);
  
  const token = localStorage.getItem('token');
  const response = await fetch(`${API_BASE}/upload/image`, {
    method: 'POST',
    headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    body: formData
  });
  
  if (!response.ok) throw new Error('Upload failed');
  return response.json();
}

// Host login
async function hostLogin(phone, name = '') {
  return apiRequest('/hosts/login', {
    method: 'POST',
    body: JSON.stringify({ phone, name })
  });
}

// Cleaner login
async function cleanerLogin(phone) {
  return apiRequest('/cleaners/login', {
    method: 'POST',
    body: JSON.stringify({ phone })
  });
}

// Sanitize HTML (prevent XSS)
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Show toast notification
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;
  
  const container = document.getElementById('toast-container') || createToastContainer();
  container.appendChild(toast);
  
  setTimeout(() => toast.remove(), 3000);
}

function createToastContainer() {
  const container = document.createElement('div');
  container.id = 'toast-container';
  container.style.cssText = 'position:fixed;top:20px;right:20px;z-index:9999;';
  document.body.appendChild(container);
  return container;
}

// Format date
function formatDate(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  return date.toLocaleDateString('zh-TW', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
}

// Format price
function formatPrice(price) {
  return new Intl.NumberFormat('zh-TW', {
    style: 'currency',
    currency: 'CAD'
  }).format(price);
}

// Safe innerHTML (XSS protection)
function safeInnerHTML(element, html) {
  element.innerHTML = html;
}

// Skeleton Screen Helpers
function showSkeleton(containerId, type = 'card') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    let skeleton = '';
    
    if (type === 'card') {
        skeleton = `
            <div class="skeleton-card">
                <div class="skeleton-order-header">
                    <div class="skeleton skeleton-avatar"></div>
                    <div class="skeleton skeleton-text-sm"></div>
                </div>
                <div class="skeleton-order-body">
                    <div class="skeleton skeleton-text-lg"></div>
                    <div class="skeleton skeleton-text"></div>
                    <div class="skeleton skeleton-text-sm"></div>
                </div>
                <div class="skeleton skeleton-button"></div>
            </div>
        `;
    } else if (type === 'list') {
        skeleton = Array(5).fill(`
            <div class="skeleton-card">
                <div class="skeleton skeleton-text-lg" style="margin-bottom: 12px;"></div>
                <div class="skeleton skeleton-text"></div>
            </div>
        `).join('');
    } else if (type === 'stats') {
        skeleton = `
            <div class="skeleton-stats">
                <div class="skeleton-stat">
                    <div class="skeleton skeleton-stat-number"></div>
                    <div class="skeleton skeleton-stat-label"></div>
                </div>
                <div class="skeleton-stat">
                    <div class="skeleton skeleton-stat-number"></div>
                    <div class="skeleton skeleton-stat-label"></div>
                </div>
                <div class="skeleton-stat">
                    <div class="skeleton skeleton-stat-number"></div>
                    <div class="skeleton skeleton-stat-label"></div>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = skeleton;
}

function hideSkeleton(containerId) {
    // Skeleton will be replaced by actual content
}

// Lazy load with skeleton
async function loadWithSkeleton(containerId, loadFunction, type = 'card') {
    showSkeleton(containerId, type);
    
    try {
        const data = await loadFunction();
        return data;
    } catch (error) {
        console.error('Load failed:', error);
        return null;
    }
}
