document.addEventListener('alpine:init', () => {
    Alpine.data('portfolioApp', () => ({
        positions: [],
        isLoading: false,
        error: null,
        statusFilter: 'all',
        searchQuery: '',

        init() {
            this.fetchPositions();
        },

        async fetchPositions() {
            this.isLoading = true;
            this.error = null;
            try {
                // Ensure the backend URL matches where Uvicorn is running
                const url = `http://localhost:8000/api/positions?status_filter=${this.statusFilter}`;
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                this.positions = await response.json();
            } catch (err) {
                console.error("Failed to fetch positions:", err);
                this.error = "Failed to load portfolio data. Make sure the backend Server is running on port 8000.";
            } finally {
                this.isLoading = false;
            }
        },

        get filteredPositions() {
            if (this.searchQuery === '') return this.positions;

            const q = this.searchQuery.toLowerCase();
            return this.positions.filter(pos => {
                const nameMatch = (pos.instrument_name || '').toLowerCase().includes(q);
                const tickerMatch = (pos.instrument_ticker || '').toLowerCase().includes(q);
                const isinMatch = (pos.instrument_isin || '').toLowerCase().includes(q);
                return nameMatch || tickerMatch || isinMatch;
            });
        },

        get totalInvested() {
            return this.filteredPositions.reduce((sum, pos) => sum + (pos.total_invested || 0), 0);
        },

        get totalPnl() {
            return this.filteredPositions.reduce((sum, pos) => sum + (pos.pnl || 0), 0);
        },

        // Formatters
        formatMoney(value, symbol = '') {
            if (value === null || value === undefined) return '-';
            const formatter = new Intl.NumberFormat('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            return `${formatter.format(value)} ${symbol}`;
        },

        formatPercent(value) {
            if (value === null || value === undefined) return '-';
            const formatter = new Intl.NumberFormat('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
            return `${formatter.format(value * 100)} %`;
        },

        formatDate(dateString) {
            if (!dateString) return '';
            const date = new Date(dateString);
            if (isNaN(date.getTime())) return '';

            // Format to YYYY-MM-DD HH:MM:SS
            const y = date.getFullYear();
            const m = String(date.getMonth() + 1).padStart(2, '0');
            const d = String(date.getDate()).padStart(2, '0');
            const hh = String(date.getHours()).padStart(2, '0');
            const mm = String(date.getMinutes()).padStart(2, '0');
            const ss = String(date.getSeconds()).padStart(2, '0');

            return `${y}-${m}-${d} ${hh}:${mm}:${ss}`;
        },

        getColorClass(value) {
            if (value > 0) return 'positive';
            if (value < 0) return 'negative';
            return 'neutral';
        }
    }));
});
