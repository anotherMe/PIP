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

        // Formatters mapping (using shared utils)
        formatMoney: window.utils.formatMoney,
        formatPercent: window.utils.formatPercent,
        formatDate: window.utils.formatDate,
        getColorClass: window.utils.getColorClass
    }));
});
