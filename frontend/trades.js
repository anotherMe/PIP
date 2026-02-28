document.addEventListener('alpine:init', () => {
    Alpine.data('tradesApp', () => ({
        trades: [],
        isLoading: false,
        error: null,
        searchQuery: '',

        init() {
            this.fetchTrades();
        },

        async fetchTrades() {
            this.isLoading = true;
            this.error = null;
            try {
                const url = `http://localhost:8000/api/trades`;
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                this.trades = await response.json();
            } catch (err) {
                console.error("Failed to fetch trades:", err);
                this.error = "Failed to load trades data. Make sure the backend Server is running on port 8000.";
            } finally {
                this.isLoading = false;
            }
        },

        get filteredTrades() {
            if (this.searchQuery === '') return this.trades;

            const q = this.searchQuery.toLowerCase();
            return this.trades.filter(t => {
                const typeMatch = (t.type || '').toLowerCase().includes(q);
                const descMatch = (t.description || '').toLowerCase().includes(q);
                return typeMatch || descMatch;
            });
        },

        // Formatters mapping (using shared utils)
        formatMoney: window.utils.formatMoney,
        formatDate: window.utils.formatDate,
        getColorClass: window.utils.getColorClass
    }));
});
