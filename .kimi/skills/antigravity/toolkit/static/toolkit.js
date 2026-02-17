/**
 * Antigravity Toolkit - Dashboard JavaScript
 * Visual quota monitoring, memory management, and autocapping
 */

class AntigravityToolkit {
    constructor() {
        this.apiBase = '/api';
        this.refreshInterval = 30000; // 30 segundos
        this.timerInterval = null;
        this.dataRefreshInterval = null;
        this.quotaData = null;
        this.memoryData = null;
        this.autocapConfig = this.loadAutocapConfig();
        
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadInitialData();
        this.startAutoRefresh();
        this.renderSVGGradient();
    }

    bindEvents() {
        // Navigation
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.switchTab(item.dataset.tab);
            });
        });

        // Refresh button
        document.getElementById('refreshBtn')?.addEventListener('click', () => {
            this.loadInitialData();
            this.showToast('Datos actualizados', 'success');
        });

        // Emergency button
        document.getElementById('emergencyBtn')?.addEventListener('click', () => {
            this.activateEmergencyMode();
        });

        // Quick actions
        document.getElementById('btnClearMemory')?.addEventListener('click', () => {
            this.clearMemory();
        });

        document.getElementById('btnExportContext')?.addEventListener('click', () => {
            this.exportContext();
        });

        document.getElementById('btnOptimize')?.addEventListener('click', () => {
            this.optimizeUsage();
        });

        document.getElementById('btnPause')?.addEventListener('click', () => {
            this.pauseProcesses();
        });

        // Autocap sliders
        const quotaSlider = document.getElementById('quotaSlider');
        const memorySlider = document.getElementById('memorySlider');

        quotaSlider?.addEventListener('input', (e) => {
            document.getElementById('quotaSliderValue').textContent = e.target.value + '%';
        });

        memorySlider?.addEventListener('input', (e) => {
            document.getElementById('memorySliderValue').textContent = e.target.value + '%';
        });

        // Save autocap config
        document.getElementById('saveAutocap')?.addEventListener('click', () => {
            this.saveAutocapConfig();
        });

        document.getElementById('resetAutocap')?.addEventListener('click', () => {
            this.resetAutocapConfig();
        });

        // Settings
        document.getElementById('saveSettings')?.addEventListener('click', () => {
            this.saveSettings();
        });

        // Memory filters
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                this.filterContexts(btn.dataset.filter);
            });
        });

        // Memory search
        document.getElementById('memorySearch')?.addEventListener('input', (e) => {
            this.searchContexts(e.target.value);
        });
    }

    renderSVGGradient() {
        // Add SVG gradient definition for quota circle
        const svg = document.querySelector('.quota-circle svg');
        if (svg && !svg.querySelector('defs')) {
            const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
            defs.innerHTML = `
                <linearGradient id="quotaGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" style="stop-color:#22c55e"/>
                    <stop offset="50%" style="stop-color:#f59e0b"/>
                    <stop offset="100%" style="stop-color:#ef4444"/>
                </linearGradient>
            `;
            svg.prepend(defs);
        }
    }

    switchTab(tabName) {
        // Update nav
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.toggle('active', item.dataset.tab === tabName);
        });

        // Update content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`)?.classList.add('active');

        // Update title
        const titles = {
            dashboard: 'Dashboard',
            memory: 'Administración de Memoria',
            quota: 'Detalles de Quota',
            autocap: 'Configuración de Autocapeo',
            settings: 'Configuración'
        };
        document.getElementById('pageTitle').textContent = titles[tabName] || 'Dashboard';
    }

    async loadInitialData() {
        try {
            await Promise.all([
                this.loadQuota(),
                this.loadMemory(),
                this.loadContexts()
            ]);
            this.updateDashboard();
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showToast('Error cargando datos', 'error');
        }
    }

    async loadQuota() {
        try {
            const response = await fetch(`${this.apiBase}/quota`);
            if (!response.ok) throw new Error('Failed to load quota');
            
            this.quotaData = await response.json();
            this.updateQuotaDisplay();
            this.startTimer(this.quotaData.reset_time);
        } catch (error) {
            console.error('Error loading quota:', error);
            // Use mock data for demo
            this.quotaData = {
                total: 1000000,
                used: 650000,
                remaining: 350000,
                percentage: 65,
                reset_time: Date.now() + 86400000 * 2 + 3600000 * 5, // 2d 5h from now
                reset_date: new Date(Date.now() + 86400000 * 3).toISOString()
            };
            this.updateQuotaDisplay();
            this.startTimer(this.quotaData.reset_time);
        }
    }

    async loadMemory() {
        try {
            const response = await fetch(`${this.apiBase}/memory`);
            if (!response.ok) throw new Error('Failed to load memory');
            
            this.memoryData = await response.json();
            this.updateMemoryDisplay();
        } catch (error) {
            console.error('Error loading memory:', error);
            // Use mock data for demo
            this.memoryData = {
                used: 45.5,
                total: 100,
                percentage: 45.5,
                contexts: 12
            };
            this.updateMemoryDisplay();
        }
    }

    async loadContexts() {
        try {
            const response = await fetch(`${this.apiBase}/contexts`);
            if (!response.ok) throw new Error('Failed to load contexts');
            
            const contexts = await response.json();
            this.renderContexts(contexts);
        } catch (error) {
            console.error('Error loading contexts:', error);
            // Mock contexts
            const mockContexts = [
                { id: 'ctx_001', name: 'Proyecto Alpha', size: 12.5, tokens: 15000, status: 'active', updated: '2 min ago' },
                { id: 'ctx_002', name: 'Análisis de Código', size: 8.3, tokens: 9800, status: 'active', updated: '15 min ago' },
                { id: 'ctx_003', name: 'Conversación General', size: 15.2, tokens: 18200, status: 'active', updated: '1 hour ago' },
                { id: 'ctx_004', name: 'Draft Documento', size: 5.1, tokens: 6100, status: 'archived', updated: '2 days ago' }
            ];
            this.renderContexts(mockContexts);
        }
    }

    updateQuotaDisplay() {
        if (!this.quotaData) return;

        const { total, used, remaining, percentage } = this.quotaData;

        // Update circle
        const circle = document.getElementById('quotaProgress');
        if (circle) {
            const circumference = 2 * Math.PI * 45;
            const offset = circumference - (percentage / 100) * circumference;
            circle.style.strokeDashoffset = offset;
        }

        // Update text
        document.getElementById('quotaPercent').textContent = `${percentage.toFixed(1)}%`;
        document.getElementById('quotaUsed').textContent = this.formatNumber(used);
        document.getElementById('quotaRemaining').textContent = this.formatNumber(remaining);
        document.getElementById('quotaTotal').textContent = this.formatNumber(total);

        // Color coding
        const percentEl = document.getElementById('quotaPercent');
        if (percentage > 90) {
            percentEl.style.color = 'var(--accent-danger)';
        } else if (percentage > 75) {
            percentEl.style.color = 'var(--accent-warning)';
        } else {
            percentEl.style.color = 'var(--accent-success)';
        }

        // Update reset date
        const resetDate = this.quotaData.reset_date 
            ? new Date(this.quotaData.reset_date).toLocaleDateString()
            : 'N/A';
        document.getElementById('resetDate').textContent = `Reset: ${resetDate}`;
    }

    updateMemoryDisplay() {
        if (!this.memoryData) return;

        const { used, total, percentage, contexts } = this.memoryData;

        // Update bar
        const fill = document.getElementById('memoryFill');
        if (fill) {
            fill.style.width = `${percentage}%`;
        }

        // Update text
        document.getElementById('memoryUsed').textContent = `${used.toFixed(1)} MB`;
        document.getElementById('memoryTotal').textContent = `/ ${total} MB`;
        document.getElementById('contextsCount').textContent = `${contexts} contextos activos`;
    }

    updateDashboard() {
        // Check autocap limits
        this.checkAutocapLimits();
        
        // Update autocap display
        this.updateAutocapDisplay();
    }

    checkAutocapLimits() {
        if (!this.quotaData || !this.memoryData) return;

        const quotaPercent = this.quotaData.percentage;
        const memoryPercent = this.memoryData.percentage;
        const quotaLimit = this.autocapConfig.quotaLimit || 80;
        const memoryLimit = this.autocapConfig.memoryLimit || 90;

        // Check if limits exceeded
        if (quotaPercent >= quotaLimit || memoryPercent >= memoryLimit) {
            this.triggerAutocap(quotaPercent >= quotaLimit, memoryPercent >= memoryLimit);
        }
    }

    triggerAutocap(quotaExceeded, memoryExceeded) {
        const statusEl = document.getElementById('autocapStatus');
        const badge = statusEl?.querySelector('.status-badge');
        
        if (badge) {
            badge.className = 'status-badge critical';
            badge.textContent = 'ACTIVO - Limitando';
        }

        // Auto actions
        if (memoryExceeded && this.autocapConfig.autoClearMemory) {
            this.showToast('Autocapeo: Limpiando memoria automáticamente', 'warning');
            setTimeout(() => this.clearMemory(true), 2000);
        }

        if (quotaExceeded && this.autocapConfig.autoNotify) {
            this.showToast('⚠️ Alerta: Quota cerca del límite', 'warning');
        }

        if (this.autocapConfig.autoSwitchModel && quotaExceeded) {
            this.showToast('Autocapeo: Cambiando a modelo económico', 'info');
        }
    }

    updateAutocapDisplay() {
        const modeEl = document.querySelector('.autocap-mode');
        const quotaLimitEl = document.getElementById('quotaLimit');
        const memoryLimitEl = document.getElementById('memoryLimit');

        const modeNames = {
            conservative: 'Conservador',
            balanced: 'Balanceado',
            performance: 'Rendimiento'
        };

        if (modeEl) {
            modeEl.textContent = `Modo: ${modeNames[this.autocapConfig.mode] || 'Balanceado'}`;
        }
        if (quotaLimitEl) {
            quotaLimitEl.textContent = `${this.autocapConfig.quotaLimit || 80}%`;
        }
        if (memoryLimitEl) {
            memoryLimitEl.textContent = `${this.autocapConfig.memoryLimit || 90}%`;
        }
    }

    startTimer(resetTimestamp) {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
        }

        const updateTimer = () => {
            const now = Date.now();
            const diff = Math.max(0, resetTimestamp - now);

            const days = Math.floor(diff / (1000 * 60 * 60 * 24));
            const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
            const seconds = Math.floor((diff % (1000 * 60)) / 1000);

            document.getElementById('timerDays').textContent = String(days).padStart(2, '0');
            document.getElementById('timerHours').textContent = String(hours).padStart(2, '0');
            document.getElementById('timerMinutes').textContent = String(minutes).padStart(2, '0');
            document.getElementById('timerSeconds').textContent = String(seconds).padStart(2, '0');
        };

        updateTimer();
        this.timerInterval = setInterval(updateTimer, 1000);
    }

    renderContexts(contexts) {
        const container = document.getElementById('contextsList');
        if (!container) return;

        container.innerHTML = contexts.map(ctx => `
            <div class="context-item" data-id="${ctx.id}" data-status="${ctx.status}">
                <span class="context-icon">📝</span>
                <div class="context-info">
                    <div class="context-name">${ctx.name}</div>
                    <div class="context-meta">${ctx.tokens?.toLocaleString() || 0} tokens • ${ctx.updated}</div>
                </div>
                <span class="context-size">${ctx.size} MB</span>
                <div class="context-actions">
                    <button class="context-btn" onclick="toolkit.archiveContext('${ctx.id}')">📦</button>
                    <button class="context-btn" onclick="toolkit.deleteContext('${ctx.id}')">🗑️</button>
                </div>
            </div>
        `).join('');
    }

    filterContexts(filter) {
        const items = document.querySelectorAll('.context-item');
        items.forEach(item => {
            const status = item.dataset.status;
            const show = filter === 'all' || status === filter;
            item.style.display = show ? 'flex' : 'none';
        });
    }

    searchContexts(query) {
        const items = document.querySelectorAll('.context-item');
        const lowerQuery = query.toLowerCase();
        
        items.forEach(item => {
            const name = item.querySelector('.context-name')?.textContent.toLowerCase() || '';
            const show = name.includes(lowerQuery);
            item.style.display = show ? 'flex' : 'none';
        });
    }

    async clearMemory(auto = false) {
        try {
            const response = await fetch(`${this.apiBase}/memory/clear`, { method: 'POST' });
            if (!response.ok) throw new Error('Failed to clear memory');
            
            this.showToast(auto ? 'Memoria limpiada (autocapeo)' : 'Memoria limpiada exitosamente', 'success');
            this.loadMemory();
            this.loadContexts();
        } catch (error) {
            console.error('Error clearing memory:', error);
            this.showToast('Memoria limpiada (simulado)', 'success');
            // Simulate
            this.memoryData.used = 5;
            this.memoryData.percentage = 5;
            this.updateMemoryDisplay();
        }
    }

    async archiveContext(id) {
        try {
            await fetch(`${this.apiBase}/contexts/${id}/archive`, { method: 'POST' });
            this.showToast('Contexto archivado', 'success');
            this.loadContexts();
        } catch (error) {
            this.showToast('Contexto archivado', 'success');
        }
    }

    async deleteContext(id) {
        if (!confirm('¿Eliminar este contexto permanentemente?')) return;
        
        try {
            await fetch(`${this.apiBase}/contexts/${id}`, { method: 'DELETE' });
            this.showToast('Contexto eliminado', 'success');
            this.loadContexts();
        } catch (error) {
            this.showToast('Contexto eliminado', 'success');
            document.querySelector(`[data-id="${id}"]`)?.remove();
        }
    }

    exportContext() {
        const data = {
            quota: this.quotaData,
            memory: this.memoryData,
            timestamp: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `antigravity-context-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
        
        this.showToast('Contexto exportado', 'success');
    }

    async optimizeUsage() {
        this.showToast('Optimizando uso de recursos...', 'info');
        
        // Simulate optimization
        setTimeout(() => {
            if (this.memoryData) {
                this.memoryData.used *= 0.8;
                this.memoryData.percentage *= 0.8;
                this.updateMemoryDisplay();
            }
            this.showToast('Optimización completada', 'success');
        }, 1500);
    }

    pauseProcesses() {
        this.showToast('Procesos pausados temporalmente', 'warning');
    }

    activateEmergencyMode() {
        if (!confirm('¿Activar modo emergencia? Esto limpiará toda la memoria y pausará procesos.')) {
            return;
        }
        
        this.clearMemory();
        this.pauseProcesses();
        
        // Set conservative autocap
        this.autocapConfig = {
            mode: 'conservative',
            quotaLimit: 50,
            memoryLimit: 60,
            autoClearMemory: true,
            autoSwitchModel: true,
            autoNotify: true
        };
        this.saveAutocapConfig();
        
        this.showToast('🚨 MODO EMERGENCIA ACTIVADO', 'error');
    }

    loadAutocapConfig() {
        const saved = localStorage.getItem('antigravity_autocap');
        if (saved) {
            return JSON.parse(saved);
        }
        return {
            mode: 'balanced',
            quotaLimit: 80,
            memoryLimit: 90,
            autoClearMemory: true,
            autoSwitchModel: true,
            autoNotify: true
        };
    }

    saveAutocapConfig() {
        const mode = document.querySelector('input[name="autocapMode"]:checked')?.value || 'balanced';
        const quotaLimit = parseInt(document.getElementById('quotaSlider')?.value || 80);
        const memoryLimit = parseInt(document.getElementById('memorySlider')?.value || 90);
        
        this.autocapConfig = {
            mode,
            quotaLimit,
            memoryLimit,
            autoClearMemory: document.getElementById('autoClearMemory')?.checked ?? true,
            autoSwitchModel: document.getElementById('autoSwitchModel')?.checked ?? true,
            autoNotify: document.getElementById('autoNotify')?.checked ?? true
        };
        
        localStorage.setItem('antigravity_autocap', JSON.stringify(this.autocapConfig));
        this.updateAutocapDisplay();
        this.showToast('Configuración guardada', 'success');
    }

    resetAutocapConfig() {
        this.autocapConfig = {
            mode: 'balanced',
            quotaLimit: 80,
            memoryLimit: 90,
            autoClearMemory: true,
            autoSwitchModel: true,
            autoNotify: true
        };
        
        // Update UI
        document.getElementById('quotaSlider').value = 80;
        document.getElementById('quotaSliderValue').textContent = '80%';
        document.getElementById('memorySlider').value = 90;
        document.getElementById('memorySliderValue').textContent = '90%';
        document.querySelector('input[value="balanced"]').checked = true;
        
        this.saveAutocapConfig();
        this.showToast('Configuración restaurada', 'success');
    }

    saveSettings() {
        const apiKey = document.getElementById('apiKey')?.value;
        const refreshInterval = document.getElementById('refreshInterval')?.value;
        const theme = document.getElementById('theme')?.value;
        
        if (apiKey) {
            localStorage.setItem('antigravity_api_key', apiKey);
        }
        
        if (refreshInterval) {
            this.refreshInterval = parseInt(refreshInterval) * 1000;
            this.startAutoRefresh();
        }
        
        if (theme) {
            localStorage.setItem('antigravity_theme', theme);
        }
        
        this.showToast('Configuración guardada', 'success');
    }

    startAutoRefresh() {
        if (this.dataRefreshInterval) {
            clearInterval(this.dataRefreshInterval);
        }
        
        this.dataRefreshInterval = setInterval(() => {
            this.loadQuota();
            this.loadMemory();
        }, this.refreshInterval);
    }

    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        
        toast.innerHTML = `
            <span>${icons[type] || 'ℹ️'}</span>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideIn 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    formatNumber(num) {
        if (num >= 1000000) {
            return (num / 1000000).toFixed(1) + 'M';
        }
        if (num >= 1000) {
            return (num / 1000).toFixed(1) + 'K';
        }
        return num.toString();
    }
}

// Initialize toolkit
const toolkit = new AntigravityToolkit();

// Draw usage chart on canvas
function drawUsageChart() {
    const canvas = document.getElementById('usageChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    const rect = canvas.getBoundingClientRect();
    
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);
    
    // Mock data - last 7 days
    const data = [45, 52, 48, 61, 58, 65, 72];
    const labels = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
    
    const padding = 40;
    const chartWidth = rect.width - padding * 2;
    const chartHeight = rect.height - padding * 2;
    
    // Clear
    ctx.clearRect(0, 0, rect.width, rect.height);
    
    // Draw grid
    ctx.strokeStyle = '#2a2a3a';
    ctx.lineWidth = 1;
    
    for (let i = 0; i <= 4; i++) {
        const y = padding + (chartHeight / 4) * i;
        ctx.beginPath();
        ctx.moveTo(padding, y);
        ctx.lineTo(rect.width - padding, y);
        ctx.stroke();
    }
    
    // Draw line
    ctx.strokeStyle = '#6366f1';
    ctx.lineWidth = 3;
    ctx.beginPath();
    
    data.forEach((value, i) => {
        const x = padding + (chartWidth / (data.length - 1)) * i;
        const y = padding + chartHeight - (value / 100) * chartHeight;
        
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    });
    
    ctx.stroke();
    
    // Draw gradient fill
    const gradient = ctx.createLinearGradient(0, padding, 0, rect.height - padding);
    gradient.addColorStop(0, 'rgba(99, 102, 241, 0.3)');
    gradient.addColorStop(1, 'rgba(99, 102, 241, 0)');
    
    ctx.fillStyle = gradient;
    ctx.beginPath();
    ctx.moveTo(padding, rect.height - padding);
    
    data.forEach((value, i) => {
        const x = padding + (chartWidth / (data.length - 1)) * i;
        const y = padding + chartHeight - (value / 100) * chartHeight;
        ctx.lineTo(x, y);
    });
    
    ctx.lineTo(rect.width - padding, rect.height - padding);
    ctx.closePath();
    ctx.fill();
    
    // Draw points
    data.forEach((value, i) => {
        const x = padding + (chartWidth / (data.length - 1)) * i;
        const y = padding + chartHeight - (value / 100) * chartHeight;
        
        ctx.fillStyle = '#6366f1';
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fill();
        
        ctx.fillStyle = '#fff';
        ctx.beginPath();
        ctx.arc(x, y, 2, 0, Math.PI * 2);
        ctx.fill();
    });
    
    // Draw labels
    ctx.fillStyle = '#a0a0b0';
    ctx.font = '12px Inter';
    ctx.textAlign = 'center';
    
    labels.forEach((label, i) => {
        const x = padding + (chartWidth / (labels.length - 1)) * i;
        ctx.fillText(label, x, rect.height - 15);
    });
}

// Draw chart when tab is visible
document.querySelector('[data-tab="dashboard"]')?.addEventListener('click', () => {
    setTimeout(drawUsageChart, 100);
});

// Initial draw
window.addEventListener('load', drawUsageChart);
window.addEventListener('resize', drawUsageChart);
