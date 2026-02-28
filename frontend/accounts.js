document.addEventListener('alpine:init', () => {
    Alpine.data('accountsApp', () => ({
        accounts: [],
        isLoading: false,
        error: null,
        searchQuery: '',

        init() {
            this.fetchAccounts();
        },

        async fetchAccounts() {
            this.isLoading = true;
            this.error = null;
            try {
                const url = `http://localhost:8000/api/accounts`;
                const response = await fetch(url);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                this.accounts = await response.json();
            } catch (err) {
                console.error("Failed to fetch accounts:", err);
                this.error = "Failed to load accounts data. Make sure the backend Server is running on port 8000.";
            } finally {
                this.isLoading = false;
            }
        },

        get filteredAccounts() {
            if (this.searchQuery === '') return this.accounts;

            const q = this.searchQuery.toLowerCase();
            return this.accounts.filter(a => {
                const nameMatch = (a.name || '').toLowerCase().includes(q);
                const descMatch = (a.description || '').toLowerCase().includes(q);
                return nameMatch || descMatch;
            });
        }
    }));
});
