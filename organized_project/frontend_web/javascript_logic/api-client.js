/**
 * H.C. Lombardo App - API Client
 * JavaScript API client for interacting with H.C. Lombardo endpoints
 */

class HCLombardoAPIClient {
    constructor(baseUrl = window.location.origin) {
        this.baseUrl = baseUrl;
        this.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
    }

    // Generic API request method
    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        const config = {
            headers: this.headers,
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || `HTTP ${response.status}: ${response.statusText}`);
            }
            
            return data;
        } catch (error) {
            console.error(`API Request Failed [${endpoint}]:`, error);
            throw error;
        }
    }

    // Health check
    async getHealth() {
        return await this.request('/health');
    }

    // NFL Betting API methods
    nfl = {
        // Get NFL predictions
        getPredictions: async () => {
            return await this.request('/predict');
        },

        // Get team statistics
        getTeams: async () => {
            return await this.request('/teams');
        },

        // Get specific team data
        getTeam: async (teamId) => {
            return await this.request(`/teams/${teamId}`);
        },

        // Get betting lines
        getBettingLines: async (gameId = null) => {
            const endpoint = gameId ? `/betting-lines/${gameId}` : '/betting-lines';
            return await this.request(endpoint);
        },

        // Get game predictions with details
        getGamePrediction: async (homeTeam, awayTeam) => {
            return await this.request(`/predict-game?home=${homeTeam}&away=${awayTeam}`);
        }
    };

    // Text Classification API methods
    text = {
        // Classify text
        classify: async (text) => {
            return await this.request('/classify', {
                method: 'POST',
                body: JSON.stringify({ text })
            });
        },

        // Analyze sentiment
        analyzeSentiment: async (text) => {
            return await this.request('/sentiment', {
                method: 'POST', 
                body: JSON.stringify({ text })
            });
        },

        // Batch text analysis
        batchAnalyze: async (texts) => {
            return await this.request('/batch-analyze', {
                method: 'POST',
                body: JSON.stringify({ texts })
            });
        }
    };

    // API status and info methods
    info = {
        // Get OpenAPI schema
        getOpenAPI: async () => {
            return await this.request('/openapi.json');
        },

        // Get API version info
        getVersion: async () => {
            return await this.request('/version');
        },

        // Get system metrics
        getMetrics: async () => {
            return await this.request('/metrics');
        }
    };
}

// Interactive API Testing Functions
const APITester = {
    client: new HCLombardoAPIClient(),
    resultsContainer: null,

    init() {
        this.resultsContainer = document.getElementById('api-results');
        this.setupTestButtons();
    },

    setupTestButtons() {
        // Add test buttons to the page
        const testContainer = document.createElement('div');
        testContainer.className = 'api-test-container';
        testContainer.innerHTML = `
            <h3>🧪 API Testing Panel</h3>
            <div class="test-buttons">
                <button onclick="APITester.testHealth()" class="test-btn">Test Health</button>
                <button onclick="APITester.testNFLPredictions()" class="test-btn">Test NFL API</button>
                <button onclick="APITester.testTextClassification()" class="test-btn">Test Text API</button>
                <button onclick="APITester.testAll()" class="test-btn primary">Test All APIs</button>
            </div>
            <div id="api-results" class="api-results"></div>
        `;

        // Insert after nav-grid or at end of container
        const container = document.querySelector('.container');
        if (container) {
            container.appendChild(testContainer);
        }
    },

    async testHealth() {
        this.showLoading('Testing API health...');
        try {
            const result = await this.client.getHealth();
            this.showResult('Health Check', result, 'success');
        } catch (error) {
            this.showResult('Health Check', error.message, 'error');
        }
    },

    async testNFLPredictions() {
        this.showLoading('Testing NFL predictions...');
        try {
            const result = await this.client.nfl.getPredictions();
            this.showResult('NFL Predictions', result, 'success');
        } catch (error) {
            this.showResult('NFL Predictions', error.message, 'error');
        }
    },

    async testTextClassification() {
        this.showLoading('Testing text classification...');
        try {
            const result = await this.client.text.classify('This is a great product!');
            this.showResult('Text Classification', result, 'success');
        } catch (error) {
            this.showResult('Text Classification', error.message, 'error');
        }
    },

    async testAll() {
        this.showLoading('Running comprehensive API tests...');
        const results = {};

        // Test health
        try {
            results.health = await this.client.getHealth();
        } catch (error) {
            results.health = { error: error.message };
        }

        // Test NFL API
        try {
            results.nfl = await this.client.nfl.getPredictions();
        } catch (error) {
            results.nfl = { error: error.message };
        }

        // Test text API  
        try {
            results.text = await this.client.text.classify('Testing H.C. Lombardo APIs');
        } catch (error) {
            results.text = { error: error.message };
        }

        this.showResult('Comprehensive Test', results, 'info');
    },

    showLoading(message) {
        if (this.resultsContainer) {
            this.resultsContainer.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>${message}</p>
                </div>
            `;
        }
    },

    showResult(title, data, type) {
        if (!this.resultsContainer) return;

        const resultHtml = `
            <div class="result-item ${type}">
                <h4>${title}</h4>
                <pre>${JSON.stringify(data, null, 2)}</pre>
                <small>Tested at: ${new Date().toLocaleTimeString()}</small>
            </div>
        `;

        this.resultsContainer.innerHTML = resultHtml;
    }
};

// Initialize API tester when page loads
document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're on a page that wants API testing
    if (document.querySelector('.container')) {
        APITester.init();
    }
});

// Export for global use
window.HCLombardoAPIClient = HCLombardoAPIClient;
window.APITester = APITester;