// script.js - JavaScript untuk dashboard RKS NET

// Konfigurasi
const CONFIG = {
    dataUrl: './data/status.json',
    refreshInterval: 60000, // 60 detik
    countdownStart: 60,
    enableNotifications: true,
    enableSound: true,
    filter: 'all' // all, online, offline
};

// State management
let appState = {
    customers: [],
    filteredCustomers: [],
    lastUpdate: null,
    summary: { total_customers: 0, online_customers: 0, offline_customers: 0 },
    countdown: CONFIG.countdownStart,
    countdownInterval: null,
    refreshInterval: null,
    searchTerm: '',
    currentFilter: 'all'
};

// DOM Elements
const elements = {
    totalCount: document.getElementById('total'),
    onlineCount: document.getElementById('online'),
    offlineCount: document.getElementById('offline'),
    lastUpdate: document.getElementById('lastUpdate'),
    countdown: document.getElementById('countdown'),
    tableBody: document.getElementById('tableBody'),
    searchInput: document.getElementById('searchInput'),
    filterAll: document.getElementById('filterAll'),
    filterOnline: document.getElementById('filterOnline'),
    filterOffline: document.getElementById('filterOffline'),
    refreshButton: document.querySelector('.refresh-btn'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    notificationBadge: document.getElementById('notificationBadge')
};

// Format waktu
function formatDateTime(isoString) {
    if (!isoString) return '-';
    
    const date = new Date(isoString);
    return date.toLocaleString('id-ID', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
}

function formatTimeOnly(isoString) {
    if (!isoString) return '-';
    
    const date = new Date(isoString);
    return date.toLocaleTimeString('id-ID', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
}

// Load data dari JSON
async function loadData(showLoading = true) {
    try {
        if (showLoading) showLoadingOverlay();
        
        // Tambah timestamp untuk bypass cache
        const timestamp = new Date().getTime();
        const url = `${CONFIG.dataUrl}?t=${timestamp}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Update state
        appState.customers = data.customers || [];
        appState.lastUpdate = data.last_updated;
        appState.summary = data.summary || {
            total_customers: 0,
            online_customers: 0,
            offline_customers: 0
        };
        
        // Apply filter dan search
        applyFilters();
        
        // Update UI
        updateDashboard();
        
        // Check untuk notifications
        checkForAlerts();
        
        // Reset countdown
        resetCountdown();
        
        if (showLoading) hideLoadingOverlay();
        
        console.log('Data loaded successfully:', data.summary);
        
    } catch (error) {
        console.error('Error loading data:', error);
        showError('Gagal memuat data. Silakan refresh halaman.');
        hideLoadingOverlay();
    }
}

// Update dashboard UI
function updateDashboard() {
    // Update summary statistics
    elements.totalCount.textContent = appState.summary.total_customers;
    elements.onlineCount.textContent = appState.summary.online_customers;
    elements.offlineCount.textContent = appState.summary.offline_customers;
    
    // Update last update time
    elements.lastUpdate.textContent = formatDateTime(appState.lastUpdate);
    
    // Update table
    updateTable();
    
    // Update filter buttons
    updateFilterButtons();
}

// Update tabel dengan data
function updateTable() {
    const customers = appState.filteredCustomers;
    
    if (customers.length === 0) {
        elements.tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="no-data">
                    <div style="text-align: center; padding: 40px; color: #64748b;">
                        <i class="fas fa-database" style="font-size: 48px; margin-bottom: 15px; opacity: 0.5;"></i>
                        <p>Tidak ada data yang sesuai dengan filter</p>
                    </div>
                </td>
            </tr>
        `;
        return;
    }
    
    let tableHTML = '';
    
    customers.forEach(customer => {
        const statusClass = customer.status.toLowerCase();
        const statusText = customer.status === 'UP' ? 'ONLINE' : 'OFFLINE';
        const statusIcon = customer.status === 'UP' ? 'fa-check-circle' : 'fa-times-circle';
        
        tableHTML += `
            <tr class="customer-row" data-status="${statusClass}" data-name="${customer.name.toLowerCase()}">
                <td class="customer-number">${customer.no}</td>
                <td class="customer-name">
                    <div style="display: flex; align-items: center; gap: 10px;">
                        <div class="avatar" style="
                            width: 36px;
                            height: 36px;
                            border-radius: 50%;
                            background: ${getCustomerColor(customer.no)};
                            color: white;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-weight: bold;
                            font-size: 14px;
                        ">
                            ${customer.no}
                        </div>
                        <div>
                            <strong>${customer.name}</strong>
                            ${customer.comment ? `<br><small style="color: #64748b;">${customer.comment}</small>` : ''}
                        </div>
                    </div>
                </td>
                <td class="customer-ip">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <i class="fas fa-network-wired" style="color: #64748b;"></i>
                        <code style="background: #f1f5f9; padding: 4px 8px; border-radius: 4px; font-family: 'Courier New', monospace;">
                            ${customer.ip}
                        </code>
                    </div>
                </td>
                <td class="customer-status">
                    <div class="status-badge ${statusClass}">
                        <i class="fas ${statusIcon}"></i> ${statusText}
                    </div>
                    ${customer.last_down ? `<br><small style="color: #64748b; font-size: 12px;">Down: ${customer.last_down}</small>` : ''}
                </td>
                <td class="customer-update">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <i class="far fa-clock" style="color: #64748b;"></i>
                        <span>${formatTimeOnly(appState.lastUpdate)}</span>
                    </div>
                </td>
            </tr>
        `;
    });
    
    elements.tableBody.innerHTML = tableHTML;
}

// Warna avatar berdasarkan nomor
function getCustomerColor(number) {
    const colors = [
        '#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
        '#ec4899', '#14b8a6', '#f97316', '#6366f1', '#84cc16'
    ];
    return colors[number % colors.length];
}

// Filter dan search
function applyFilters() {
    let filtered = [...appState.customers];
    
    // Apply status filter
    if (appState.currentFilter === 'online') {
        filtered = filtered.filter(c => c.status === 'UP');
    } else if (appState.currentFilter === 'offline') {
        filtered = filtered.filter(c => c.status === 'DOWN');
    }
    
    // Apply search filter
    if (appState.searchTerm.trim()) {
        const term = appState.searchTerm.toLowerCase();
        filtered = filtered.filter(c => 
            c.name.toLowerCase().includes(term) || 
            c.ip.includes(term) ||
            (c.comment && c.comment.toLowerCase().includes(term))
        );
    }
    
    appState.filteredCustomers = filtered;
}

// Update filter buttons state
function updateFilterButtons() {
    // Reset semua button
    elements.filterAll?.classList.remove('active');
    elements.filterOnline?.classList.remove('active');
    elements.filterOffline?.classList.remove('active');
    
    // Aktifkan button yang sesuai
    switch (appState.currentFilter) {
        case 'all':
            elements.filterAll?.classList.add('active');
            break;
        case 'online':
            elements.filterOnline?.classList.add('active');
            break;
        case 'offline':
            elements.filterOffline?.classList.add('active');
            break;
    }
}

// Set filter
function setFilter(filter) {
    appState.currentFilter = filter;
    applyFilters();
    updateDashboard();
}

// Search function
function handleSearch() {
    appState.searchTerm = elements.searchInput.value;
    applyFilters();
    updateDashboard();
}

// Check untuk alerts dan notifications
function checkForAlerts() {
    const offlineCount = appState.summary.offline_customers;
    
    if (offlineCount > 0) {
        // Show notification badge
        if (elements.notificationBadge) {
            elements.notificationBadge.innerHTML = `
                <i class="fas fa-exclamation-triangle"></i>
                ${offlineCount} Pelanggan OFFLINE
            `;
            elements.notificationBadge.style.display = 'block';
            
            // Auto hide setelah 5 detik
            setTimeout(() => {
                elements.notificationBadge.style.display = 'none';
            }, 5000);
        }
        
        // Play alert sound
        if (CONFIG.enableSound) {
            playAlertSound();
        }
        
        // Browser notification
        if (CONFIG.enableNotifications && Notification.permission === 'granted') {
            showBrowserNotification(offlineCount);
        }
    } else {
        // Hide notification badge jika semua online
        if (elements.notificationBadge) {
            elements.notificationBadge.style.display = 'none';
        }
    }
}

// Browser notification
function showBrowserNotification(offlineCount) {
    const notification = new Notification('⚠️ RKS NET Alert', {
        body: `${offlineCount} pelanggan OFFLINE terdeteksi`,
        icon: 'https://cdn-icons-png.flaticon.com/512/2991/2991148.png',
        tag: 'rks-net-alert'
    });
    
    notification.onclick = () => {
        window.focus();
        notification.close();
    };
    
    setTimeout(() => notification.close(), 5000);
}

// Alert sound
function playAlertSound() {
    try {
        const audioContext = new (window.AudioContext || window.webkitAudioContext)();
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        oscillator.frequency.value = 600;
        oscillator.type = 'sine';
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.8);
        
        oscillator.start(audioContext.currentTime);
        oscillator.stop(audioContext.currentTime + 0.8);
    } catch (e) {
        console.log('Audio not supported');
    }
}

// Request notification permission
function requestNotificationPermission() {
    if ('Notification' in window && Notification.permission === 'default') {
        Notification.requestPermission().then(permission => {
            if (permission === 'granted') {
                console.log('Notification permission granted');
            }
        });
    }
}

// Countdown functions
function startCountdown() {
    clearInterval(appState.countdownInterval);
    
    appState.countdownInterval = setInterval(() => {
        appState.countdown--;
        if (elements.countdown) {
            elements.countdown.textContent = appState.countdown;
        }
        
        if (appState.countdown <= 0) {
            appState.countdown = CONFIG.countdownStart;
            loadData();
        }
    }, 1000);
}

function resetCountdown() {
    appState.countdown = CONFIG.countdownStart;
    if (elements.countdown) {
        elements.countdown.textContent = appState.countdown;
    }
    startCountdown();
}

// Auto refresh
function startAutoRefresh() {
    clearInterval(appState.refreshInterval);
    
    appState.refreshInterval = setInterval(() => {
        loadData(false); // Load tanpa loading overlay
    }, CONFIG.refreshInterval);
}

// Loading overlay
function showLoadingOverlay() {
    if (elements.loadingOverlay) {
        elements.loadingOverlay.style.display = 'flex';
    }
}

function hideLoadingOverlay() {
    if (elements.loadingOverlay) {
        elements.loadingOverlay.style.display = 'none';
    }
}

// Error handling
function showError(message) {
    elements.tableBody.innerHTML = `
        <tr>
            <td colspan="5" style="text-align: center; padding: 40px; color: #ef4444;">
                <i class="fas fa-exclamation-circle" style="font-size: 48px; margin-bottom: 15px;"></i>
                <h3 style="margin-bottom: 10px;">Error</h3>
                <p style="margin-bottom: 20px;">${message}</p>
                <button onclick="loadData()" style="
                    padding: 10px 20px;
                    background: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    cursor: pointer;
                    font-size: 14px;
                ">
                    <i class="fas fa-redo"></i> Coba Lagi
                </button>
            </td>
        </tr>
    `;
}

// Export data ke CSV
function exportToCSV() {
    const customers = appState.customers;
    
    if (customers.length === 0) {
        alert('Tidak ada data untuk diexport');
        return;
    }
    
    // Header CSV
    let csv = 'No,Nama Pemilik Router,IP Address,Status,Last Update\n';
    
    // Data
    customers.forEach(customer => {
        csv += `${customer.no},"${customer.name}",${customer.ip},${customer.status},"${formatDateTime(appState.lastUpdate)}"\n`;
    });
    
    // Create blob dan download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `rks-net-monitoring-${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Initialize dashboard
function initDashboard() {
    console.log('Initializing RKS NET Dashboard...');
    
    // Request notification permission
    requestNotificationPermission();
    
    // Setup event listeners
    setupEventListeners();
    
    // Start countdown
    startCountdown();
    
    // Start auto refresh
    startAutoRefresh();
    
    // Load initial data
    loadData();
    
    console.log('Dashboard initialized successfully');
}

// Setup event listeners
function setupEventListeners() {
    // Search input
    if (elements.searchInput) {
        elements.searchInput.addEventListener('input', handleSearch);
    }
    
    // Filter buttons
    if (elements.filterAll) {
        elements.filterAll.addEventListener('click', () => setFilter('all'));
    }
    
    if (elements.filterOnline) {
        elements.filterOnline.addEventListener('click', () => setFilter('online'));
    }
    
    if (elements.filterOffline) {
        elements.filterOffline.addEventListener('click', () => setFilter('offline'));
    }
    
    // Refresh button
    if (elements.refreshButton) {
        elements.refreshButton.addEventListener('click', () => {
            loadData();
            if (elements.refreshButton) {
                elements.refreshButton.style.transform = 'rotate(360deg)';
                setTimeout(() => {
                    if (elements.refreshButton) {
                        elements.refreshButton.style.transform = '';
                    }
                }, 300);
            }
        });
    }
    
    // Export button (jika ada)
    const exportBtn = document.getElementById('exportBtn');
    if (exportBtn) {
        exportBtn.addEventListener('click', exportToCSV);
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl+R atau F5 untuk refresh
        if ((e.ctrlKey && e.key === 'r') || e.key === 'F5') {
            e.preventDefault();
            loadData();
        }
        
        // Ctrl+F untuk focus search
        if (e.ctrlKey && e.key === 'f') {
            e.preventDefault();
            if (elements.searchInput) {
                elements.searchInput.focus();
            }
        }
        
        // Escape untuk clear search
        if (e.key === 'Escape') {
            if (elements.searchInput) {
                elements.searchInput.value = '';
                handleSearch();
            }
        }
    });
}

// Initialize saat page load
document.addEventListener('DOMContentLoaded', initDashboard);

// Global functions untuk dipanggil dari HTML
window.loadData = loadData;
window.setFilter = setFilter;
window.exportToCSV = exportToCSV;
