// Centralized frontend API configuration
// Reads from Vite environment variable VITE_API_BASE_URL if set,
// otherwise defaults to local development backend at http://localhost:8000/api/v1
export const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';
