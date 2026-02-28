document.addEventListener('alpine:init', () => {
    Alpine.data('transactionsApp', () => ({
        transactions: [],
        isLoading: false,
        error: null,
        searchQuery: '',

        init() {
            this.fetchTransactions();
        },

        async fetchTransactions() {
            this.isLoading = true;
            this.error = null;
            try {
                const url = `http://localhost:8000/api/transactions`;
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                this.transactions = await response.json();
            } catch (err) {
                console.error("Failed to fetch transactions:", err);
                this.error = "Failed to load transactions data. Make sure the backend Server is running on port 8000.";
            } finally {
                this.isLoading = false;
            }
        },

        get filteredTransactions() {
            if (this.searchQuery === '') return this.transactions;

            const q = this.searchQuery.toLowerCase();
            return this.transactions.filter(t => {
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
