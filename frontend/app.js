// Initialize Lucide Icons
lucide.createIcons();

// Chart.js Contexts
const metricsCtx = document.getElementById('metricsChart').getContext('2d');
const riskGaugeCtx = document.getElementById('riskGauge').getContext('2d');

let metricsChart;
let historyData = {
    labels: Array(20).fill(''),
    latency: Array(20).fill(0),
    errors: Array(20).fill(0)
};

// Autonomous Monitor State
let scanCountdown = 45;
setInterval(() => {
    const el = document.getElementById('scan-countdown');
    if (el) {
        scanCountdown--;
        if (scanCountdown < 0) scanCountdown = 45;
        el.innerText = scanCountdown;
    }
}, 1000);

// Initialize Metrics Chart
function initCharts() {
    metricsChart = new Chart(metricsCtx, {
        type: 'line',
        data: {
            labels: historyData.labels,
            datasets: [
                {
                    label: 'Latency (ms)',
                    data: historyData.latency,
                    borderColor: '#00f2ff',
                    backgroundColor: 'rgba(0, 242, 255, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 0
                },
                {
                    label: 'Error Rate (%)',
                    data: historyData.errors,
                    borderColor: '#ff0055',
                    backgroundColor: 'rgba(255, 0, 85, 0.1)',
                    fill: true,
                    tension: 0.4,
                    borderWidth: 2,
                    pointRadius: 0
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: '#a0a6b1', font: { size: 10 } }
                },
                x: { display: false }
            }
        }
    });
}

// WebSocket Connection
let socket;
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    socket = new WebSocket(`${protocol}//${window.location.host}/ws/stats`);

    socket.onopen = () => {
        console.log('Successfully connected to AI Engine WebSocket');
        document.getElementById('connection-status').className = 'status-badge status-healthy';
        document.getElementById('connection-status').innerHTML = '<i data-lucide="radio" style="width: 14px; margin-right: 4px;"></i> Live Monitoring (WS)';
        lucide.createIcons();
    };

    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        renderDashboard(data);
    };

    socket.onclose = () => {
        console.warn('WebSocket connection closed. Falling back to HTTP polling.');
        document.getElementById('connection-status').className = 'status-badge status-warning';
        document.getElementById('connection-status').innerHTML = '<i data-lucide="alert-triangle" style="width: 14px; margin-right: 4px;"></i> Polling Fallback';
        lucide.createIcons();
        setTimeout(connectWebSocket, 5000); // Try to reconnect every 5s
    };

    socket.onerror = (err) => {
        console.error('WebSocket Error:', err);
        socket.close();
    };
}

function renderDashboard(data) {
    const { metrics, assessment } = data;

    // Update UI Values
    document.getElementById('riskValue').innerText = assessment.risk_score;
    document.getElementById('latency-val').innerText = `${Math.round(metrics.latency_ms)} ms`;
    document.getElementById('error-val').innerText = `${metrics.error_rate.toFixed(2)} %`;
    document.getElementById('throughput-val').innerText = `${metrics.active_connections} req/s`;

    // Update Status Badge
    const statusEl = document.getElementById('riskStatus');
    statusEl.innerText = assessment.status;
    statusEl.className = `status-badge status-${assessment.status.toLowerCase()}`;

    // Update Autonomous Stats
    if (data.monitoring_stats) {
        document.getElementById('autonomous-intervention-count').innerText = `${data.monitoring_stats.total_remediations} Fixes Applied`;
        document.getElementById('stats-active').innerText = data.monitoring_stats.active_pipelines;
        document.getElementById('stats-failed').innerText = data.monitoring_stats.failed_pipelines;
        document.getElementById('stats-success-rate').innerText = `${data.monitoring_stats.success_rate.toFixed(1)}%`;
        document.getElementById('stats-remediations').innerText = data.monitoring_stats.total_remediations;
    }

    // Update Recommendation Badge
    const recBadge = document.getElementById('recommendation-badge');
    recBadge.innerText = assessment.recommendation;
    recBadge.className = `status-badge status-${assessment.status.toLowerCase()}`;

    // Auto-log Critical or Warning status
    if (assessment.status !== 'HEALTHY' && !lastLoggedIncident) {
        logIncident(assessment.status, assessment.reasons[0] || "Anomaly detected");
    } else if (assessment.status === 'HEALTHY') {
        lastLoggedIncident = null;
    }

    // Update Insights List
    const insightsList = document.getElementById('riskInsights');
    insightsList.innerHTML = assessment.reasons.length > 0 
        ? assessment.reasons.map(r => `<li style="display: flex; align-items: start; gap: 8px; color: ${r.includes('Security') ? 'var(--danger-neon)' : 'var(--warning-neon)'}; margin-bottom: 4px;">
            <i data-lucide="${r.includes('Security') ? 'shield-alert' : 'zap'}" style="width: 16px; flex-shrink: 0; margin-top: 2px;"></i> 
            <span>${r}</span></li>`).join('')
        : `<li style="display: flex; align-items: center; gap: 8px; color: var(--success-neon);">
            <i data-lucide="check-circle" style="width: 16px;"></i> Systems operating within safety parameters</li>`;
    
    // Update Vulnerability List
    const vulnList = document.getElementById('vulnerability-list');
    const vulns = metrics.vulnerabilities || [];
    if (vulns.length > 0) {
        vulnList.innerHTML = vulns.map(v => `
            <div style="background: rgba(255,255,255,0.03); padding: 0.6rem; border-radius: 8px; border: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <p style="font-size: 0.8rem; font-weight: 600; color: ${v.level === 'CRITICAL' ? 'var(--danger-neon)' : 'var(--warning-neon)'}">${v.id}</p>
                    <p style="font-size: 0.7rem; color: var(--text-secondary);">${v.desc}</p>
                </div>
                <span class="status-badge" style="font-size: 0.6rem; padding: 1px 6px; background: rgba(0,0,0,0.3); border: 1px solid ${v.level === 'CRITICAL' ? 'var(--danger-neon)' : 'var(--warning-neon)'}; color: ${v.level === 'CRITICAL' ? 'var(--danger-neon)' : 'var(--warning-neon)'}">${v.level}</span>
            </div>
        `).join('');
    } else {
        vulnList.innerHTML = `
            <div style="font-size: 0.8rem; color: var(--text-secondary); text-align: center; padding: 1rem; border: 1px dashed var(--border-color); border-radius: 12px;">
                No active threats detected.
            </div>
        `;
    }

    // Update Drift Status
    const driftContainer = document.getElementById('drift-status');
    const drifts = metrics.drifts || [];
    if (drifts.length > 0) {
        driftContainer.innerHTML = `
            <span style="font-size: 0.8rem; color: ${drifts[0].severity === 'HIGH' ? 'var(--danger-neon)' : 'var(--warning-neon)'}">${drifts[0].config} Drifted</span>
            <i data-lucide="alert-triangle" style="width: 16px; color: ${drifts[0].severity === 'HIGH' ? 'var(--danger-neon)' : 'var(--warning-neon)'};"></i>
        `;
    } else {
        driftContainer.innerHTML = `
            <span style="font-size: 0.8rem; color: var(--success-neon);">No drift detected</span>
            <i data-lucide="check-circle" style="width: 16px; color: var(--success-neon);"></i>
        `;
    }

    // Update Cost Suggestions
    const costContainer = document.getElementById('cost-suggestions');
    const suggest = assessment.cost_suggestions || [];
    if (suggest.length > 0) {
        costContainer.innerHTML = suggest.map(s => `
            <div style="background: rgba(0, 255, 136, 0.05); padding: 0.6rem; border-radius: 8px; border: 1px solid rgba(0, 255, 136, 0.2); display: flex; justify-content: space-between; align-items: center;">
                <div style="display: flex; gap: 10px; align-items: center;">
                    <i data-lucide="trending-down" style="width: 14px; color: var(--success-neon);"></i>
                    <span style="font-size: 0.75rem; color: var(--text-secondary);">${s.name}</span>
                </div>
                <span style="font-size: 0.75rem; font-weight: 700; color: var(--success-neon);">${s.saving}</span>
            </div>
        `).join('');
    } else {
        costContainer.innerHTML = `
            <div style="font-size: 0.8rem; color: var(--text-secondary); text-align: center; padding: 1rem; border: 1px dashed var(--border-color); border-radius: 12px;">
                No savings identified.
            </div>
        `;
    }

    // Only create icons for elements that might have new ones, not the whole body
    // This prevents UI stuttering and high CPU in the browser
    const containers = ['riskInsights', 'vulnerability-list', 'drift-status', 'cost-suggestions', 'recommendation-badge'];
    containers.forEach(id => {
        const el = document.getElementById(id);
        if (el) lucide.createIcons({ props: {}, attrs: {}, nameAttr: 'data-lucide', root: el });
    });

    // Update Chart
    historyData.latency.shift();
    historyData.latency.push(metrics.latency_ms);
    historyData.errors.shift();
    historyData.errors.push(metrics.error_rate);
    
    metricsChart.update('none');
}

let lastLoggedIncident = null;
function logIncident(type, message) {
    const logContainer = document.getElementById('alert-log');
    if (logContainer.querySelector('div[style*="italic"]')) {
        logContainer.innerHTML = ''; // Clear the "No incidents" message
    }

    const time = new Date().toLocaleTimeString();
    const entry = document.createElement('div');
    entry.style = `
        background: rgba(255,255,255,0.03); 
        padding: 0.8rem 1rem; 
        border-radius: 10px; 
        border-left: 4px solid ${type === 'CRITICAL' ? 'var(--danger-neon)' : 'var(--warning-neon)'};
        display: flex;
        justify-content: space-between;
        align-items: center;
        animation: slideIn 0.3s ease-out;
    `;
    
    entry.innerHTML = `
        <div>
            <span style="font-weight: 600; color: ${type === 'CRITICAL' ? 'var(--danger-neon)' : 'var(--warning-neon)'}">${type} Alert:</span>
            <span style="color: var(--text-primary); margin-left: 8px;">${message}</span>
        </div>
        <span style="font-size: 0.75rem; color: var(--text-secondary);">${time}</span>
    `;
    
    logContainer.prepend(entry);
    lastLoggedIncident = type;

    // Trigger Notification Feedback
    triggerNotificationFeedback(type, message);
}

// History DB Sync
async function updateHistory() {
    try {
        const response = await fetch('/api/history?limit=10');
        if (!response.ok) return;
        const data = await response.json();
        
        const historyContainer = document.getElementById('history-log');
        if (data.length === 0) {
            historyContainer.innerHTML = '<div style="color: var(--text-secondary); font-style: italic; font-size: 0.8rem; text-align: center; padding: 1rem;">No historical data yet.</div>';
            return;
        }

        historyContainer.innerHTML = data.map(record => `
            <div style="background: rgba(255,255,255,0.02); padding: 0.6rem 0.8rem; border-radius: 8px; border: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem;">
                <div style="display: flex; gap: 10px; align-items: center;">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: ${record.status === 'CRITICAL' ? 'var(--danger-neon)' : (record.status === 'WARNING' ? 'var(--warning-neon)' : 'var(--success-neon)')};"></span>
                    <span style="font-weight: 600; color: var(--text-primary);">Score: ${record.risk_score.toFixed(2)}</span>
                </div>
                <span style="color: var(--text-secondary); font-size: 0.7rem;">${new Date(record.timestamp).toLocaleTimeString()}</span>
            </div>
        `).join('');
    } catch (err) {
        console.warn('Failed to fetch history:', err);
    }
}

function triggerNotificationFeedback(type, message) {
    const center = document.getElementById('notification-center');
    const items = center.querySelectorAll('div');
    
    items.forEach(item => {
        item.style.opacity = '1';
        item.style.borderColor = type === 'CRITICAL' ? 'var(--danger-neon)' : 'var(--warning-neon)';
        item.style.boxShadow = `0 0 15px ${type === 'CRITICAL' ? 'var(--danger-neon)' : 'var(--warning-neon)'}`;
        
        setTimeout(() => {
            item.style.opacity = '0.5';
            item.style.borderColor = 'var(--border-color)';
            item.style.boxShadow = 'none';
        }, 3000);
    });
}

// Keep Polling as Fallback only if WS is not active
async function updateDashboard() {
    if (socket && socket.readyState === WebSocket.OPEN) return;

    try {
        const response = await fetch('/api/health');
        if (!response.ok) throw new Error('Backend unreachable');
        const data = await response.json();
        renderDashboard(data);
    } catch (err) {
        simulateLocalData();
    }
}

// Local simulation if backend is not running
function simulateLocalData() {
    const lat = 50 + Math.random() * 200;
    const err = Math.random() * 2;
    
    document.getElementById('latency-val').innerText = `${Math.round(lat)} ms`;
    document.getElementById('error-val').innerText = `${err.toFixed(2)} %`;
    document.getElementById('throughput-val').innerText = `${Math.floor(1000 + Math.random() * 500)} req/s`;
    
    historyData.latency.shift();
    historyData.latency.push(lat);
    historyData.errors.shift();
    historyData.errors.push(err);
    metricsChart.update('none');
}

// Pipeline Simulation Logic
async function startSimulation() {
    const steps = ['Build', 'Security Scan', 'Unit Tests', 'Integration Tests'];
    const stepIds = {
        'Build': 'step-build',
        'Security Scan': 'step-scan',
        'Unit Tests': 'step-test',
        'Integration Tests': 'step-deploy'
    };
    
    // UI Reset
    Object.values(stepIds).forEach(id => {
        document.getElementById(id).classList.remove('step-success', 'step-active', 'step-failed');
    });
    
    const deployBtn = document.getElementById('deploy-btn');
    deployBtn.disabled = true;
    
    // Get Auto-Heal Mode status
    const autoHealEnabled = document.getElementById('auto-heal-toggle').checked;
    
    try {
        // Start backend simulation
        const response = await fetch(`/api/pipeline/simulate?auto_fix=${autoHealEnabled}`);
        if (!response.ok) throw new Error("Simulation request failed");
        
        const results = await response.json();
        
        for (let i = 0; i < results.length; i++) {
            const res = results[i];
            const elId = stepIds[res.step];
            const el = document.getElementById(elId);
            
            // Mark as active
            el.classList.add('step-active');
            await new Promise(r => setTimeout(r, 800)); // Visual delay
            el.classList.remove('step-active');
            
            if (res.status === 'SUCCESS') {
                el.classList.add('step-success');
            } else {
                el.classList.add('step-failed');
                
                if (res.remediation) {
                    const fix = res.remediation;
                    logIncident('WARNING', `Pipeline failed at ${res.step}. AI Auto-Fix Triggered...`);
                    
                    // Show self-healing feedback
                    await new Promise(r => setTimeout(r, 1000));
                    
                    if (fix.execution_status === 'Fix Applied Successfully') {
                        logIncident('HEALTHY', `AI applied fix: ${fix.auto_fix_command}. Retrying step...`);
                        el.classList.remove('step-failed');
                        el.classList.add('step-success');
                        
                        // Switch to Analyzer tab to show details
                        switchTab('analyzer');
                        displayAutoFixResult(fix);
                        
                        // Briefly pulse to show "healed"
                        el.parentElement.classList.add('pulse');
                        setTimeout(() => el.parentElement.classList.remove('pulse'), 2000);
                        
                        continue; // Proceed to next steps in the loop
                    } else {
                        logIncident('CRITICAL', `Auto-Fix failed for ${res.step}. Manual intervention required.`);
                    }
                } else {
                    logIncident('CRITICAL', `Pipeline failed at ${res.step}. Deployment halted.`);
                }
                
                deployBtn.disabled = false;
                return; // Stop simulation on failure
            }
        }
        
        // If all steps (including potential fixes) succeeded
        await startCanaryRollout();
        
    } catch (err) {
        console.error("Simulation Error:", err);
        logIncident('CRITICAL', "Failed to connect to AI Simulation Engine.");
    } finally {
        deployBtn.disabled = false;
    }
}

async function startCanaryRollout() {
    const strategyLabel = document.getElementById('strategy-label');
    const bluePctLabel = document.getElementById('blue-pct');
    const greenPctLabel = document.getElementById('green-pct');
    const flowBar = document.getElementById('traffic-flow-bar');
    const greenEnv = document.getElementById('green-env');
    const greenStatus = document.getElementById('green-status');

    strategyLabel.innerText = "CANARY ROLLOUT (ACTIVE)";
    strategyLabel.style.color = 'var(--secondary-neon)';
    
    // Preparation
    greenEnv.style.borderColor = 'var(--secondary-neon)';
    greenEnv.querySelector('i').style.color = 'var(--secondary-neon)';
    greenStatus.innerText = "HEALTHY";
    greenStatus.style.color = 'var(--secondary-neon)';

    // Traffic Shifting Steps
    const configResponse = await fetch('/api/admin/config');
    const activeConfig = await configResponse.json();
    const rolloutSteps = activeConfig.canary_steps || [10, 25, 50, 75, 100];
    const stepDelay = activeConfig.step_delay_ms || 500;

    for (let pct of rolloutSteps) {
        // Check if AI risk is too high during rollout
        const currentRisk = parseFloat(document.getElementById('riskValue').innerText);
        const threshold = activeConfig.risk_threshold || 0.6;

        if (currentRisk > threshold) {
            logIncident('CRITICAL', `Canary Rollout ABORTED: Risk (${currentRisk}) exceeded sensitivity threshold (${threshold}).`);
            resetCanary();
            return;
        }

        bluePctLabel.innerText = `${100 - pct}%`;
        greenPctLabel.innerText = `${pct}%`;
        flowBar.style.width = `${pct}%`;
        
        await new Promise(r => setTimeout(r, stepDelay));
    }

    // Finalize
    strategyLabel.innerText = "ROLLOUT COMPLETE";
    strategyLabel.style.color = 'var(--success-neon)';
    greenEnv.classList.add('pulse');
    document.getElementById('blue-env').classList.remove('pulse');
    document.getElementById('blue-env').style.opacity = '0.5';
    
    logIncident('HEALTHY', 'Canary Rollout successful. Traffic fully shifted to Green environment.');
}

function resetCanary() {
    document.getElementById('blue-pct').innerText = '100%';
    document.getElementById('green-pct').innerText = '0%';
    document.getElementById('traffic-flow-bar').style.width = '0%';
    document.getElementById('strategy-label').innerText = "ROLLING UPDATE";
    document.getElementById('strategy-label').style.color = 'var(--primary-neon)';
    
    const greenEnv = document.getElementById('green-env');
    greenEnv.style.borderColor = 'var(--border-color)';
    greenEnv.querySelector('i').style.color = 'var(--text-secondary)';
    document.getElementById('green-status').innerText = "INACTIVE";
    document.getElementById('green-status').style.color = 'var(--text-secondary)';
    greenEnv.classList.remove('pulse');
    document.getElementById('blue-env').classList.add('pulse');
    document.getElementById('blue-env').style.opacity = '1';
}

async function triggerStress(mode) {
    try {
        const response = await fetch(`/api/admin/stress?mode=${mode}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        const statusDot = document.getElementById('network-dot');
        if (mode === 'RECOVERY') {
            statusDot.style.background = 'var(--success-neon)';
            statusDot.style.boxShadow = '0 0 8px var(--success-neon)';
            logIncident('HEALTHY', 'System Stress relieved. Initiating automated recovery protocol.');
        } else {
            statusDot.style.background = 'var(--danger-neon)';
            statusDot.style.boxShadow = '0 0 12px var(--danger-neon)';
            logIncident('WARNING', `External Stress Test initiated: ${mode} scenario.`);
        }
    } catch (err) {
        console.error('Failed to trigger stress on backend:', err);
        // Fallback for visual only if backend is down
        alert(`Simulating ${mode} stress mode locally.`);
    }
}

// Configuration Management
async function loadConfiguration() {
    try {
        const response = await fetch('/api/admin/config');
        const config = await response.json();
        
        document.getElementById('risk-threshold-input').value = config.risk_threshold;
        document.getElementById('threshold-val').innerText = config.risk_threshold.toFixed(2);
        document.getElementById('canary-steps-input').value = config.canary_steps.join(', ');
        document.getElementById('step-delay-input').value = config.step_delay_ms;
        
        // Also load Jenkins config
        await loadJenkinsConfig();
    } catch (err) {
        console.warn('Failed to load config:', err);
    }
}

async function saveConfiguration() {
    const threshold = parseFloat(document.getElementById('risk-threshold-input').value);
    const stepsStr = document.getElementById('canary-steps-input').value;
    const steps = stepsStr.split(',').map(s => parseInt(s.trim())).filter(s => !isNaN(s));
    const delay = parseInt(document.getElementById('step-delay-input').value);

    try {
        const response = await fetch('/api/admin/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                risk_threshold: threshold,
                canary_steps: steps,
                step_delay_ms: delay
            })
        });
        
        if (response.ok) {
            logIncident('HEALTHY', 'AI Security Protocols Updated: New sensitivity thresholds active.');
            const btn = document.querySelector('button[onclick="saveConfiguration()"]');
            btn.innerText = "Saved!";
            btn.style.borderColor = "var(--success-neon)";
            btn.style.color = "var(--success-neon)";
            setTimeout(() => {
                btn.innerText = "Save Settings";
                btn.style.borderColor = "var(--primary-neon)";
                btn.style.color = "var(--primary-neon)";
            }, 2000);
        }
    } catch (err) {
        console.error('Failed to save config:', err);
    }
}

// UI Event Listeners
document.getElementById('risk-threshold-input').addEventListener('input', (e) => {
    document.getElementById('threshold-val').innerText = parseFloat(e.target.value).toFixed(2);
});

// Tab Management
function switchTab(tabId) {
    // Update Tab UI
    document.querySelectorAll('.nav-tab').forEach(tab => {
        tab.classList.remove('active');
        if (tab.innerText.toLowerCase().includes(tabId)) {
            tab.classList.add('active');
        }
    });

    // Update Sections
    document.querySelectorAll('.view-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(`${tabId}-section`).classList.add('active');

    // Refresh lucide icons for new section
    lucide.createIcons();
}

// Log Analyzer Logic
async function analyzePipelineLog() {
    const logText = document.getElementById('log-input').value;
    if (!logText.trim()) {
        alert("Please paste some log content first.");
        return;
    }

    const btn = document.getElementById('analyze-btn');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="pulse" data-lucide="brain"></i> Analyzing CI/CD pipeline failure using Azure OpenAI...';
    lucide.createIcons();

    try {
        const response = await fetch('/api/analyze-log', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ log_text: logText })
        });

        if (!response.ok) throw new Error("Failed to analyze log");

        const data = await response.json();
        renderAnalysisResults(data, logText);
    } catch (err) {
        console.error(err);
        alert("Analysis failed. Please ensure the backend is running.");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
        lucide.createIcons();
    }
}

function renderAnalysisResults(results, originalLog) {
    document.getElementById('analysis-placeholder').style.display = 'none';
    document.getElementById('analysis-results').style.display = 'flex';

    document.getElementById('res-category').innerText = results.category;
    document.getElementById('res-tool').innerText = results.tool;
    document.getElementById('res-root-cause').innerText = results.root_cause;
    document.getElementById('res-source-platform').innerText = results.pipeline_source || "AI Detected";
    document.getElementById('res-source').innerText = results.analysis_source || "Rule Engine";
    document.getElementById('res-manual-steps').innerText = results.manual_fix_steps || "N/A";

    const conf = results.confidence || 0;
    document.getElementById('res-confidence').innerText = `${(conf * 100).toFixed(0)}%`;
    document.getElementById('res-conf-bar').style.width = `${conf * 100}%`;

    // AI Insight display
    const aiInsightSec = document.getElementById('res-ai-insight-section');
    if (results.analysis_source && results.analysis_source.includes("AI Engine")) {
        aiInsightSec.style.display = 'block';
        document.getElementById('res-ai-insight').innerText = results.root_cause;
    } else {
        aiInsightSec.style.display = 'none';
    }
    
    const hasAutoFix = results.strategies && results.strategies.length > 0;
    document.getElementById('res-autofix').innerText = hasAutoFix ? 'Available' : 'Not Available';
    document.getElementById('res-autofix').style.color = hasAutoFix ? 'var(--success-neon)' : 'var(--text-secondary)';

    // Handle Corrections
    const correctionSec = document.getElementById('res-correction-section');
    if (results.correction && results.correction.suggestion) {
        correctionSec.style.display = 'block';
        document.getElementById('res-suggested-pkg').innerText = results.correction.suggestion;
        document.getElementById('res-correction-conf').innerText = `${(results.correction.confidence * 100).toFixed(0)}% AI Match`;
    } else {
        correctionSec.style.display = 'none';
    }

    // Render Commands
    const cmdContainer = document.getElementById('res-commands');
    cmdContainer.innerHTML = results.commands.map(cmd => `
        <div class="ai-command-box">
            <span>$ ${cmd}</span>
            <button class="copy-btn" onclick="copyToClipboard('${cmd.replace(/'/g, "\\'")}')">
                <i data-lucide="copy" style="width: 14px;"></i>
            </button>
        </div>
    `).join('');

    // Render Tips
    const tipsList = document.getElementById('res-tips');
    tipsList.innerHTML = results.prevention_tips.map(tip => `<li>${tip}</li>`).join('');

    // Highlight Important Lines in UI
    highlightLogLines(results.highlighted_lines, originalLog);
    
    lucide.createIcons();
}

function highlightLogLines(indices, logText) {
    const lines = logText.split('\n');
    const overlay = document.getElementById('highlight-overlay');
    
    // Create a version of the text with highlighted lines
    const highlightedHtml = lines.map((line, idx) => {
        if (indices.includes(idx)) {
            return `<span class="highlight-error">${line || ' '}</span>`;
        }
        return `<span>${line || ' '}</span>`;
    }).join('\n');

    overlay.innerHTML = highlightedHtml;
    
    // Sync scroll
    const textarea = document.getElementById('log-input');
    textarea.onscroll = () => {
        overlay.scrollTop = textarea.scrollTop;
    };
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text);
    // Simple toast or button feedback could go here
    const btn = event.currentTarget;
    const original = btn.innerHTML;
    btn.innerHTML = '<i data-lucide="check" style="width: 14px; color: var(--success-neon);"></i>';
    lucide.createIcons();
    setTimeout(() => {
        btn.innerHTML = original;
        lucide.createIcons();
    }, 2000);
}

// Jenkins Auto-Remediation Logic
async function remediateJenkinsJob() {
    const jobName = document.getElementById('jenkins-job-name').value;
    if (!jobName.trim()) {
        alert("Please enter a Jenkins job name first.");
        return;
    }

    const btn = document.getElementById('pull-btn');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="pulse" data-lucide="loader-2"></i> Connecting to Jenkins...';
    lucide.createIcons();

    try {
        const response = await fetch('/api/remediate-job', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ source: 'Jenkins', job_id: jobName })
        });

        if (!response.ok) throw new Error("Failed to remediate Jenkins job");

        const data = await response.json();
        
        // Show the Auto-Fix results panel directly
        document.getElementById('analysis-placeholder').style.display = 'none';
        document.getElementById('analysis-results').style.display = 'none';
        document.getElementById('autofix-results').style.display = 'flex';
        
        // Populate the log textarea so the user can see what was pulled
        if (data.original_log) {
            const logTextarea = document.getElementById('log-input');
            logTextarea.value = data.original_log;
            // Trigger overlay refresh with highlighted lines if any
            highlightLogLines(data.highlighted_lines || [], data.original_log);
        }

        displayAutoFixResult(data);
        
    } catch (err) {
        console.error(err);
        alert("Remediation failed. Check backend logs for API errors.");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
        lucide.createIcons();
    }
}

function displayAutoFixResult(data) {
    document.getElementById('autofix-results').style.display = 'flex';
    document.getElementById('autofix-category').innerText = data.category;
    document.getElementById('autofix-tool').innerText = data.detected_tool || "Unknown";
    document.getElementById('autofix-source').innerText = data.analysis_source || "Rule Engine";
    document.getElementById('autofix-source-platform').innerText = data.pipeline_source || "AI Detected";
    document.getElementById('autofix-root-cause').innerText = data.root_cause;
    document.getElementById('autofix-confidence').innerText = data.confidence_score ? `${(data.confidence_score * 100).toFixed(0)}%` : 'N/A';
    
    // Handle Corrections in AutoFix UI
    const correctionSec = document.getElementById('autofix-correction-section');
    if (data.correction && data.correction.suggestion) {
        correctionSec.style.display = 'block';
        document.getElementById('autofix-orig-pkg').innerText = data.correction.original;
        document.getElementById('autofix-sugg-pkg').innerText = data.correction.suggestion;
    } else {
        correctionSec.style.display = 'none';
    }
    
    if (data.auto_fix_available && data.auto_fix_command) {
        document.getElementById('autofix-command-section').style.display = 'block';
        document.getElementById('autofix-command').innerHTML = `
            <div class="ai-command-box">
                <span>$ ${data.auto_fix_command}</span>
            </div>
        `;
    } else {
        document.getElementById('autofix-command-section').style.display = 'none';
    }

    document.getElementById('autofix-manual-steps').innerText = data.manual_fix_steps || 'Manual intervention required.';
    document.getElementById('autofix-execution-status').innerText = data.execution_status;
    document.getElementById('autofix-retry-status').innerText = data.retry_status;

    // Visual feedback for execution status
    const execStatus = document.getElementById('autofix-execution-status');
    if (data.execution_status === "Fix Applied Successfully") {
        execStatus.style.color = "var(--success-neon)";
    } else if (data.execution_status === "Fix Failed") {
        execStatus.style.color = "var(--danger-neon)";
    } else {
        execStatus.style.color = "var(--warning-neon)";
    }
    
    const badge = document.getElementById('autofix-badge');
    if (data.auto_fix_available) {
        badge.innerText = 'AUTO-FIX READY';
        badge.style.background = 'rgba(0, 255, 136, 0.1)';
        badge.style.color = 'var(--success-neon)';
        badge.style.borderColor = 'var(--success-neon)';
    } else {
        badge.innerText = 'MANUAL FIX REQUIRED';
        badge.style.background = 'rgba(255, 0, 85, 0.1)';
        badge.style.color = 'var(--danger-neon)';
        badge.style.borderColor = 'var(--danger-neon)';
    }
}

// Auto Fix Logic
async function autoFixPipeline() {
    const logText = document.getElementById('log-input').value;
    if (!logText.trim()) {
        alert("Please paste some log content first.");
        return;
    }

    const btn = document.getElementById('autofix-btn');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="pulse" data-lucide="loader-2"></i> Executing Auto Fix...';
    lucide.createIcons();
    
    // Clear previous results and show progress
    document.getElementById('analysis-placeholder').style.display = 'none';
    document.getElementById('analysis-results').style.display = 'none';
    document.getElementById('autofix-results').style.display = 'flex';
    document.getElementById('autofix-badge').innerText = 'PLANNING';
    document.getElementById('autofix-badge').style.background = 'rgba(0, 150, 255, 0.2)';
    document.getElementById('autofix-badge').style.color = '#00f2ff';
    document.getElementById('autofix-badge').style.borderColor = '#00f2ff';
    
    document.getElementById('autofix-category').innerText = "Generating Fix Plan...";
    document.getElementById('autofix-tool').innerText = "--";
    document.getElementById('autofix-root-cause').innerText = "--";
    document.getElementById('autofix-confidence').innerText = "--";
    document.getElementById('autofix-manual-steps').innerText = "Calculating safe remediation path...";
    document.getElementById('autofix-execution-status').innerText = "Awaiting Execution...";
    document.getElementById('autofix-execution-status').style.color = "white";
    document.getElementById('autofix-retry-status').innerText = "--";

    const jobName = document.getElementById('jenkins-job-name').value;

    console.log(`[AUTONOMOUS] Triggering Auto-Fix for job: ${jobName || 'manual'}`);

    try {
        const response = await fetch('/api/autofix', {
            method: 'POST',
            cache: 'no-store', // Aggressive no-cache
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                log_text: logText,
                job_id: jobName
            })
        });

        if (!response.ok) throw new Error("Failed to auto fix log");

        const data = await response.json();
        displayAutoFixResult(data);

    } catch (err) {
        console.error(err);
        alert("Auto Fix failed. Please ensure the backend is running.");
        document.getElementById('autofix-badge').innerText = 'ERROR';
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
        lucide.createIcons();
    }
}


// Monitoring Stats
async function fetchMonitoringStats() {
    try {
        const response = await fetch('/api/monitoring');
        if (!response.ok) return;
        const stats = await response.json();
        
        document.getElementById('stats-active').innerText = stats.active_pipelines;
        document.getElementById('stats-failed').innerText = stats.failed_pipelines;
        document.getElementById('stats-success-rate').innerText = stats.success_rate + '%';
        document.getElementById('stats-remediations').innerText = stats.total_remediations;
    } catch (err) {
        console.error("Monitoring stats error:", err);
    }
}

// Start
initCharts();
loadConfiguration();
connectWebSocket();
setInterval(updateDashboard, 2000);
setInterval(updateHistory, 5000); 
setInterval(fetchMonitoringStats, 5000);
updateDashboard();
updateHistory();
fetchMonitoringStats();

// Jenkins Connection Functions
async function testJenkinsConnection() {
    const url = document.getElementById('jenkins-url-input').value;
    const user = document.getElementById('jenkins-user-input').value;
    const token = document.getElementById('jenkins-token-input').value;

    if (!url || !user || !token) {
        alert("Please fill in all Jenkins connection fields.");
        return;
    }

    const btn = document.querySelector('button[onclick="testJenkinsConnection()"]');
    const originalText = btn.innerHTML;
    btn.disabled = true;
    btn.innerHTML = '<i class="pulse" data-lucide="refresh-cw"></i> Testing...';
    lucide.createIcons();

    try {
        const response = await fetch('/api/jenkins/test', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, user, token })
        });
        const result = await response.json();
        
        const indicator = document.getElementById('jenkins-connection-indicator');
        if (result.success) {
            indicator.innerText = "Verified";
            indicator.className = "status-badge status-healthy";
            indicator.style.color = "var(--success-neon)";
            logIncident('HEALTHY', 'Jenkins connection verified successfully.');
        } else {
            indicator.innerText = "Failed";
            indicator.className = "status-badge status-critical";
            indicator.style.color = "var(--danger-neon)";
            alert(`Connection Failed: ${result.message}`);
        }
    } catch (err) {
        alert("Failed to reach the backend to test connection.");
    } finally {
        btn.disabled = false;
        btn.innerHTML = originalText;
        lucide.createIcons();
    }
}

async function saveJenkinsConfig() {
    const url = document.getElementById('jenkins-url-input').value;
    const user = document.getElementById('jenkins-user-input').value;
    const token = document.getElementById('jenkins-token-input').value;

    try {
        const response = await fetch('/api/jenkins/config', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url, user, token })
        });
        
        if (response.ok) {
            logIncident('HEALTHY', 'Jenkins credentials updated in memory.');
            const btn = document.querySelector('button[onclick="saveJenkinsConfig()"]');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i data-lucide="check" style="width: 14px;"></i> Saved!';
            btn.style.background = "var(--success-neon)";
            btn.style.color = "black";
            lucide.createIcons();
            
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.style.background = "var(--primary-neon)";
                btn.style.color = "black";
                lucide.createIcons();
            }, 2000);
        }
    } catch (err) {
        console.error('Failed to save Jenkins config:', err);
    }
}

async function loadJenkinsConfig() {
    try {
        const response = await fetch('/api/jenkins/config');
        const config = await response.json();
        if (config) {
            document.getElementById('jenkins-url-input').value = config.url || '';
            document.getElementById('jenkins-user-input').value = config.user || '';
            // We don't populate the token for security reasons, or just show placeholders
            if (config.token) {
                document.getElementById('jenkins-token-input').placeholder = "•••••••••••••••• (Saved)";
                document.getElementById('jenkins-connection-indicator').innerText = "Configured";
                document.getElementById('jenkins-connection-indicator').className = "status-badge status-warning";
            }
        }
    } catch (err) {
        console.warn('Failed to load Jenkins config:', err);
    }
}
