/**
 * LeaderboardModule — Page Leaderboard complète
 * Table triable, filtres par monde, pagination
 */
class LeaderboardModule {
    constructor() {
        this.currentPage = 1;
        this.limit = 50;
        this.worldFilter = '';
        this.levelFilter = '';
        this.data = [];
        this.loading = false;
        this.init();
    }

    init() {
        // Bind DOM elements
        this.tableEl = document.getElementById('leaderboard-table');
        this.paginationEl = document.getElementById('leaderboard-pagination');
        this.worldSelect = document.getElementById('leaderboard-world-filter');
        this.levelSelect = document.getElementById('leaderboard-level-filter');
        this.limitSelect = document.getElementById('leaderboard-limit-filter');
        this.refreshBtn = document.getElementById('leaderboard-refresh');
        this.prevBtn = document.getElementById('lb-prev');
        this.nextBtn = document.getElementById('lb-next');
        this.pageInfo = document.getElementById('lb-page-info');

        // Event listeners
        if (this.worldSelect) {
            this.worldSelect.addEventListener('change', () => {
                this.worldFilter = this.worldSelect.value;
                this.currentPage = 1;
                this.loadData();
            });
        }

        if (this.levelSelect) {
            this.levelSelect.addEventListener('change', () => {
                this.levelFilter = this.levelSelect.value;
                this.currentPage = 1;
                this.loadData();
            });
        }

        if (this.limitSelect) {
            this.limitSelect.addEventListener('change', () => {
                this.limit = parseInt(this.limitSelect.value, 10) || 50;
                this.currentPage = 1;
                this.loadData();
            });
        }

        if (this.refreshBtn) {
            this.refreshBtn.addEventListener('click', () => {
                this.currentPage = 1;
                this.loadData();
            });
        }

        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => {
                if (this.currentPage > 1) {
                    this.currentPage--;
                    this.renderTable();
                    this.updatePagination();
                }
            });
        }

        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => {
                const maxPage = Math.ceil(this.data.length / this.limit) || 1;
                if (this.currentPage < maxPage) {
                    this.currentPage++;
                    this.renderTable();
                    this.updatePagination();
                }
            });
        }
    }

    async loadData() {
        if (this.loading) return;
        this.loading = true;
        this.showLoading();

        try {
            const api = window.facade || window.api;
            if (!api) {
                throw new Error('API not available');
            }

            const worldId = this.worldFilter !== '' ? parseInt(this.worldFilter, 10) : null;

            // Try new persistent leaderboard first
            let entries = [];
            try {
                const result = await api.getLeaderboardGlobal(worldId, this.limit * 5);
                if (Array.isArray(result)) {
                    entries = result;
                } else if (result && Array.isArray(result.entries)) {
                    entries = result.entries;
                }
            } catch (_) { /* fall through to legacy */ }

            // Fall back to legacy endpoint (GameSession-based) when no v2 entries
            if (entries.length === 0) {
                try {
                    const raw = window.api;
                    const legacy = await raw.request(`/game/leaderboard?limit=${this.limit * 5}`);
                    const arr = Array.isArray(legacy) ? legacy : [];
                    entries = arr.map((e, i) => ({
                        player_username: e.player_username || e.player_name || 'Unknown',
                        player_name: e.player_username || e.player_name || 'Unknown',
                        score: e.score || 0,
                        level_reached: e.level_reached || 1,
                        level_id: e.level_reached || 1,
                        world_id: e.world_id || null,
                        character_used: e.character_used || '',
                        duration_sec: e.duration_sec || 0,
                        accuracy_pct: e.accuracy_pct || null,
                        enemies_killed: e.enemies_killed || 0,
                        created_at: e.created_at || null,
                        rank: i + 1,
                    }));
                } catch (_) { /* ignore */ }
            }

            // Filter by world if needed
            if (worldId !== null) {
                entries = entries.filter(e => e.world_id === worldId);
            }

            // Filter by level if needed
            const levelId = this.levelFilter !== '' ? parseInt(this.levelFilter, 10) : null;
            if (levelId !== null) {
                entries = entries.filter(e => (e.level_id || e.level_reached) === levelId);
            }

            this.data = entries;
            this.renderTable();
            this.updatePagination();
        } catch (error) {
            this.showError(error.message || 'Failed to load leaderboard');
        } finally {
            this.loading = false;
        }
    }

    renderTable() {
        if (!this.tableEl) return;

        if (!this.data || this.data.length === 0) {
            this.tableEl.innerHTML = `
                <div class="lb-empty">
                    <span class="lb-empty-icon">🏆</span>
                    <span>${window.i18n ? window.i18n.t('leaderboard.noScores') : 'No scores yet. Be the first to play!'}</span>
                </div>
            `;
            return;
        }

        const offset = (this.currentPage - 1) * this.limit;
        const pageData = this.data.slice(offset, offset + this.limit);

        const rows = pageData.map((entry, i) => {
            const rank = offset + i + 1;
            const rankClass = rank <= 3 ? `lb-rank-${rank}` : '';
            const rankDisplay = rank <= 3 ? this.getMedalEmoji(rank) : `#${rank}`;
            const username = this.escapeHtml(entry.player_username || entry.player_name || 'Unknown');
            const score = this.formatNumber(entry.score || 0);
            const level = entry.level_reached || entry.level_id || '—';
            const char = this.getCharEmoji(entry.character_used);
            const duration = this.formatDuration(entry.duration_sec);
            const accuracy = entry.accuracy_pct != null ? `${Math.round(entry.accuracy_pct)}%` : '—';
            const date = this.formatDate(entry.created_at);

            return `
                <tr>
                    <td class="lb-rank ${rankClass}">${rankDisplay}</td>
                    <td><span class="lb-player">${username}</span></td>
                    <td class="lb-score">${score}</td>
                    <td class="lb-level">${level}</td>
                    <td class="lb-char">${char}</td>
                    <td class="lb-time">${duration}</td>
                    <td class="lb-acc">${accuracy}</td>
                    <td class="lb-date">${date}</td>
                </tr>
            `;
        }).join('');

        this.tableEl.innerHTML = `
            <table class="lb-table">
                <thead>
                    <tr>
                        <th class="lb-rank-col">#</th>
                        <th>Player</th>
                        <th class="lb-score-col">Score</th>
                        <th class="lb-level-col">Lvl</th>
                        <th class="lb-char-col">Char</th>
                        <th class="lb-time-col">Time</th>
                        <th class="lb-acc-col">Acc</th>
                        <th class="lb-date-col">Date</th>
                    </tr>
                </thead>
                <tbody>${rows}</tbody>
            </table>
        `;
    }

    updatePagination() {
        if (!this.paginationEl || !this.pageInfo) return;

        const maxPage = Math.max(1, Math.ceil(this.data.length / this.limit));

        if (this.prevBtn) this.prevBtn.disabled = this.currentPage <= 1;
        if (this.nextBtn) this.nextBtn.disabled = this.currentPage >= maxPage;

        this.pageInfo.textContent = `${this.currentPage} / ${maxPage}`;
    }

    showLoading() {
        if (this.tableEl) {
            this.tableEl.innerHTML = `
                <div class="lb-loading">
                    <div class="lb-spinner"></div>
                    <div>${window.i18n ? window.i18n.t('leaderboard.loading') : 'Loading...'}</div>
                </div>
            `;
        }
    }

    showError(message) {
        if (this.tableEl) {
            this.tableEl.innerHTML = `
                <div class="lb-error">
                    <span class="lb-empty-icon">⚠️</span>
                    <span>${this.escapeHtml(message)}</span>
                </div>
            `;
        }
    }

    // ── Helpers ────────────────────────────────────────────

    getMedalEmoji(rank) {
        if (rank === 1) return '🥇';
        if (rank === 2) return '🥈';
        if (rank === 3) return '🥉';
        return `#${rank}`;
    }

    getCharEmoji(char) {
        if (!char) return '🎮';
        const c = String(char).toLowerCase();
        if (c.includes('fox') || c.includes('renard')) return '🦊';
        if (c.includes('cat') || c.includes('chat')) return '🐱';
        if (c.includes('knight') || c.includes('chevalier')) return '⚔️';
        if (c.includes('mage') || c.includes('wizard')) return '🧙';
        if (c.includes('ninja')) return '🥷';
        if (c.includes('robot')) return '🤖';
        if (c.includes('ghost')) return '👻';
        if (c.includes('dragon')) return '🐉';
        return '🎮';
    }

    formatNumber(n) {
        if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
        if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
        return String(n);
    }

    formatDuration(seconds) {
        if (!seconds || seconds <= 0) return '—';
        const m = Math.floor(seconds / 60);
        const s = seconds % 60;
        return `${m}:${String(s).padStart(2, '0')}`;
    }

    formatDate(dateStr) {
        if (!dateStr) return '—';
        try {
            const d = new Date(dateStr);
            const now = new Date();
            const diff = now - d;
            // If less than 24h, show relative time
            if (diff < 86400000) {
                const h = Math.floor(diff / 3600000);
                if (h < 1) return 'now';
                if (h < 24) return `${h}h ago`;
            }
            return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
        } catch {
            return '—';
        }
    }

    escapeHtml(str) {
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    }
}

// Initialize when DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.leaderboardModule = new LeaderboardModule();
});
