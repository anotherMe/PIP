document.addEventListener('alpine:init', () => {
    Alpine.data('instrumentsApp', () => ({
        instruments: [],
        isLoading: false,
        error: null,
        searchQuery: '',

        init() {
            this.fetchInstruments();
        },

        async fetchInstruments() {
            this.isLoading = true;
            this.error = null;
            try {
                const url = `http://localhost:8000/api/instruments`;
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                this.instruments = await response.json();
            } catch (err) {
                console.error("Failed to fetch instruments:", err);
                this.error = "Failed to load instruments data. Make sure the backend Server is running on port 8000.";
            } finally {
                this.isLoading = false;
            }
        },

        get filteredInstruments() {
            if (this.searchQuery === '') return this.instruments;

            const q = this.searchQuery.toLowerCase();
            return this.instruments.filter(inst => {
                const nameMatch = (inst.name || '').toLowerCase().includes(q);
                const tickerMatch = (inst.ticker || '').toLowerCase().includes(q);
                const isinMatch = (inst.isin || '').toLowerCase().includes(q);
                return nameMatch || tickerMatch || isinMatch;
            });
        },

        // Exposing shared formatters just in case we need them in the template
        formatMoney: window.utils.formatMoney,
        formatPercent: window.utils.formatPercent,
        formatDate: window.utils.formatDate,
        getColorClass: window.utils.getColorClass
    }));
});
