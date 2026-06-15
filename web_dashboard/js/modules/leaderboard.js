// leaderboard.js — Leaderboard widgets for ARCAD3X Dashboard
// ==========================================================
// Widgets:
//   - Global Top 10 (live, auto-refresh every 30s)
//   - Personal Best Tracker (trend line over last 30 days)
//   - World Records per World (hall of fame)
//   - Rival comparison (pick a player, side-by-side stats)

'use strict';

class LeaderboardManager {
    constructor(api) {
        this.api = api;
        this.facade = window.facade;
        this.refreshInterval = null;
        this.autoRefreshMs = 30000; // 30 seconds
    }

    init() {
        this.initGlobalTop10();
        this.initPersonalBestTracker();
        this.initWorldRecords();
        this.initRivalComparison();
        this.startAutoRefresh();
    }

    // ── Global Top 10 Widget ───────────────────────────────────────────────

    initGlobalTop10() {
        const container = document.getElementById('leaderboard-global-top10');
        if (!container) return;
        this.loadGlobalTop10();
    }

    async loadGlobalTop10(worldId = null) {
        const container = document.getElementById('leaderboard-global-top10');
        if (!container) return;

        try {
            const client = this.facade || this.api;
            let data;
            if (client.getLeaderboardGlobal) {
                data = await client.getLeaderboardGlobal(worldId, 10);
            } else {
                // Fallback to raw API
                const params = worldId ? `?world=${worldId}&limit=10` : '?limit=10';
                const resp = await this.api.request(`/game/leaderboard/global${params}`);
                data = resp?.entries || [];
            }

            if (!Array.isArray(data) || data.length === 0) {
                container.innerHTML = '<p class="lb-empty">No scores yet. Be the first!</p>';
                return;
            }

            const medals = ['🥇', '🥈', '🥉'];
            const rows = data.map((entry, i) => {
                const medal = i < 3 ? `<span class="lb-medal">${medals[i]}</span>` : `<span class="lb-rank">#${i + 1}</span>`;
                const worldName = entry.world_name || 'Any';
                const pbBadge = entry.is_pb ? '<span class="lb-pb">PB</span>' : '';
                return `
                    <div class="lb-row ${i < 3 ? 'lb-top3' : ''}">
                        ${medal}
                        <span class="lb-name">${this._escapeHtml(entry.player_name || entry.player_username || 'Unknown')}</span>
                        <span class="lb-score">${entry.score.toLocaleString()} pts</span>
                        <span class="lb-meta">Lv${entry.level_id} • ${this._escapeHtml(worldName)} ${pbBadge}</span>
                    </div>
                `;
            }).join('');

            container.innerHTML = `
                <div class="lb-header">
                    <h3>🏆 Global Top 10</h3>
                    <span class="lb-live-indicator">● LIVE</span>
                </div>
                <div class="lb-list">${rows}</div>
                <div class="lb-footer">
                    <button class="lb-refresh-btn" onclick="window.leaderboardManager.loadGlobalTop10()">↻ Refresh</button>
                    <span class="lb-last-updated">Updated ${new Date().toLocaleTimeString()}</span>
                </div>
            `;
        } catch (err) {
            container.innerHTML = '<p class="lb-error">Failed to load leaderboard.</p>';
        }
    }

    // ── Personal Best Tracker ──────────────────────────────────────────────

    initPersonalBestTracker() {
        const container = document.getElementById('leaderboard-personal-best');
        if (!container) return;
        this.loadPersonalBestTracker();
    }

    async loadPersonalBestTracker() {
        const container = document.getElementById('leaderboard-personal-best');
        if (!container) return;

        const playerId = this._getPlayerId();
        if (!playerId) {
            container.innerHTML = '<p class="lb-empty">Login to see your personal bests!</p>';
            return;
        }

        try {
            const client = this.facade || this.api;
            let data;
            if (client.getPlayerLeaderboardHistory) {
                data = await client.getPlayerLeaderboardHistory(playerId);
            } else {
                data = await this.api.request(`/game/leaderboard/player/${playerId}`);
            }

            if (!data || !data.recent_runs || data.recent_runs.length === 0) {
                container.innerHTML = '<p class="lb-empty">No runs recorded yet. Start playing!</p>';
                return;
            }

            // Filter last 30 days
            const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
            const recentEntries = data.recent_runs.filter(e => new Date(e.created_at) >= thirtyDaysAgo);

            // Build trend data (group by day, take max score)
            const dailyScores = {};
            recentEntries.forEach(e => {
                const day = e.created_at.split('T')[0];
                if (!dailyScores[day] || e.score > dailyScores[day]) {
                    dailyScores[day] = e.score;
                }
            });

            const sortedDays = Object.keys(dailyScores).sort();
            const chartData = sortedDays.map(d => ({ day: d, score: dailyScores[d] }));

            // Build simple SVG sparkline
            const svg = this._buildSparkline(chartData, 300, 120);

            const pbEntries = data.personal_bests?.slice(0, 5) || [];
            const pbList = pbEntries.map(e => `
                <div class="lb-pb-row">
                    <span class="lb-pb-score">${e.score.toLocaleString()} pts</span>
                    <span class="lb-pb-meta">Lv${e.level_id} • ${this._escapeHtml(e.world_name || 'Any')}</span>
                    <span class="lb-pb-date">${new Date(e.created_at).toLocaleDateString()}</span>
                </div>
            `).join('');

            container.innerHTML = `
                <div class="lb-header">
                    <h3>📈 Personal Best Tracker</h3>
                    <span class="lb-stat">Best: ${(data.best_score || 0).toLocaleString()} pts</span>
                </div>
                <div class="lb-chart">${svg}</div>
                <div class="lb-pb-list">
                    <h4>Recent PBs</h4>
                    ${pbList || '<p class="lb-empty">No personal bests yet.</p>'}
                </div>
            `;
        } catch (err) {
            container.innerHTML = '<p class="lb-error">Failed to load personal bests.</p>';
        }
    }

    _buildSparkline(data, width, height) {
        if (data.length < 2) return '<p class="lb-empty">Not enough data for chart.</p>';

        const scores = data.map(d => d.score);
        const min = Math.min(...scores);
        const max = Math.max(...scores);
        const range = max - min || 1;

        const padX = 30, padY = 20;
        const chartW = width - padX * 2;
        const chartH = height - padY * 2;

        const points = data.map((d, i) => {
            const x = padX + (i / (data.length - 1)) * chartW;
            const y = padY + chartH - ((d.score - min) / range) * chartH;
            return `${x},${y}`;
        }).join(' ');

        const labels = data.map((d, i) => {
            if (i % Math.ceil(data.length / 5) !== 0 && i !== data.length - 1) return '';
            const x = padX + (i / (data.length - 1)) * chartW;
            return `<text x="${x}" y="${height - 5}" font-size="10" fill="#888" text-anchor="middle">${d.day.slice(5)}</text>`;
        }).join('');

        return `
            <svg width="${width}" height="${height}" class="lb-sparkline">
                <polyline points="${points}" fill="none" stroke="#00ff88" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                <circle cx="${padX + chartW}" cy="${padY + chartH - ((scores[scores.length - 1] - min) / range) * chartH}" r="4" fill="#00ff88"/>
                ${labels}
            </svg>
        `;
    }

    // ── World Records Widget ───────────────────────────────────────────────

    initWorldRecords() {
        const container = document.getElementById('leaderboard-world-records');
        if (!container) return;
        this.loadWorldRecords();
    }

    async loadWorldRecords() {
        const container = document.getElementById('leaderboard-world-records');
        if (!container) return;

        try {
            const data = await this.api.request('/game/leaderboard/world-records');
            if (!Array.isArray(data) || data.length === 0) {
                container.innerHTML = '<p class="lb-empty">No world records yet.</p>';
                return;
            }

            const rows = data.map(r => `
                <div class="lb-wr-row">
                    <span class="lb-wr-world">${this._escapeHtml(r.world_name)}</span>
                    <span class="lb-wr-holder">${this._escapeHtml(r.record_holder)}</span>
                    <span class="lb-wr-score">${r.best_score.toLocaleString()} pts</span>
                    <span class="lb-wr-date">${r.achieved_at ? new Date(r.achieved_at).toLocaleDateString() : ''}</span>
                </div>
            `).join('');

            container.innerHTML = `
                <div class="lb-header">
                    <h3>🌍 World Records</h3>
                </div>
                <div class="lb-wr-list">${rows}</div>
            `;
        } catch (err) {
            container.innerHTML = '<p class="lb-error">Failed to load world records.</p>';
        }
    }

    // ── Rival Comparison Widget ──────────────────────────────────────────────

    initRivalComparison() {
        const container = document.getElementById('leaderboard-rival-comparison');
        if (!container) return;

        // Build the UI with a player picker
        container.innerHTML = `
            <div class="lb-header">
                <h3>⚔️ Rival Comparison</h3>
            </div>
            <div class="lb-rival-picker">
                <input type="text" id="rivalInput" placeholder="Enter player username..." class="lb-rival-input">
                <button id="rivalCompareBtn" class="lb-rival-btn">Compare</button>
            </div>
            <div id="rivalResult" class="lb-rival-result"></div>
        `;

        const btn = document.getElementById('rivalCompareBtn');
        const input = document.getElementById('rivalInput');
        if (btn && input) {
            btn.addEventListener('click', () => this.compareRival(input.value.trim()));
            input.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') this.compareRival(input.value.trim());
            });
        }
    }

    async compareRival(rivalUsername) {
        const resultDiv = document.getElementById('rivalResult');
        if (!resultDiv || !rivalUsername) return;

        const myId = this._getPlayerId();
        if (!myId) {
            resultDiv.innerHTML = '<p class="lb-empty">Login to compare with rivals.</p>';
            return;
        }

        resultDiv.innerHTML = '<p class="lb-loading">Loading comparison...</p>';

        try {
            // First find rival player ID by username
            const players = await this.api.request('/game/players?limit=200');
            const rival = players?.find(p => p.username.toLowerCase() === rivalUsername.toLowerCase());
            if (!rival) {
                resultDiv.innerHTML = '<p class="lb-error">Player not found.</p>';
                return;
            }

            const data = await this.api.request(`/game/leaderboard/rival-comparison?player_a=${myId}&player_b=${rival.id}`);
            if (!data) {
                resultDiv.innerHTML = '<p class="lb-error">Failed to load comparison.</p>';
                return;
            }

            const { player_a_name, player_a_stats, player_b_name, player_b_stats, comparison } = data;

            const makeStatRow = (label, a, b) => {
                const winner = a > b ? 'A' : a < b ? 'B' : 'tie';
                const aClass = winner === 'A' ? 'lb-win' : winner === 'tie' ? 'lb-tie' : '';
                const bClass = winner === 'B' ? 'lb-win' : winner === 'tie' ? 'lb-tie' : '';
                return `
                    <div class="lb-stat-row">
                        <span class="lb-stat-label">${label}</span>
                        <span class="lb-stat-a ${aClass}">${a.toLocaleString()}</span>
                        <span class="lb-stat-b ${bClass}">${b.toLocaleString()}</span>
                    </div>
                `;
            };

            resultDiv.innerHTML = `
                <div class="lb-rival-table">
                    <div class="lb-rival-header">
                        <span class="lb-rival-name">${this._escapeHtml(player_a_name)}</span>
                        <span class="lb-rival-vs">VS</span>
                        <span class="lb-rival-name">${this._escapeHtml(player_b_name)}</span>
                    </div>
                    ${makeStatRow('Best Score', player_a_stats.best_score, player_b_stats.best_score)}
                    ${makeStatRow('Avg Score', player_a_stats.avg_score, player_b_stats.avg_score)}
                    ${makeStatRow('Total Runs', player_a_stats.total_runs, player_b_stats.total_runs)}
                    ${makeStatRow('Total Kills', player_a_stats.total_kills, player_b_stats.total_kills)}
                    ${makeStatRow('Avg Accuracy', player_a_stats.avg_accuracy + '%', player_b_stats.avg_accuracy + '%')}
                    <div class="lb-rival-winner">
                        🏆 Winner: <strong>${this._escapeHtml(comparison.winner)}</strong>
                    </div>
                </div>
            `;
        } catch (err) {
            resultDiv.innerHTML = '<p class="lb-error">Failed to compare.</p>';
        }
    }

    // ── Auto Refresh ─────────────────────────────────────────────────────────

    startAutoRefresh() {
        if (this.refreshInterval) clearInterval(this.refreshInterval);
        this.refreshInterval = setInterval(() => {
            this.loadGlobalTop10();
        }, this.autoRefreshMs);
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    // ── Helpers ────────────────────────────────────────────────────────────

    _getPlayerId() {
        const token = this._getToken();
        if (!token) return null;
        try {
            return JSON.parse(atob(token.split('.')[1])).player_id ?? null;
        } catch (_) { return null; }
    }

    _getToken() {
        return localStorage.getItem(window.APP_CONFIG?.TOKEN_KEY || 'SI3LN_SESSION')
            || localStorage.getItem('access_token');
    }

    _escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Export globally
window.LeaderboardManager = LeaderboardManager;
