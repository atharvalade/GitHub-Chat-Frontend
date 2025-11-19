// Centralized API configuration
// Change this URL to match your backend deployment
export const API_BASE_URL = 'https://americas-smallest-listing-laid.trycloudflare.com';

// API endpoints
export const API_ENDPOINTS = {
  healthCheck: `${API_BASE_URL}/healthcheck`,
  initializeRepo: `${API_BASE_URL}/api/repository/initialize`,
  chat: `${API_BASE_URL}/api/chat`,
} as const;

// API types matching backend responses
export interface InitializeRepoRequest {
  owner: string;
  repo: string;
}

export interface InitializeRepoResponse {
  status: string;
  message: string;
  summary: string;
  tree: string;
}

export interface ChatRequest {
  owner: string;
  repo: string;
  query: string;
  history: [string, string][];
}

export interface ChatResponse {
  response: string;
  history: [string, string][];
}

// API helper functions
export async function initializeRepository(
  owner: string,
  repo: string
): Promise<InitializeRepoResponse> {
  const response = await fetch(API_ENDPOINTS.initializeRepo, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ owner, repo }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `Failed to initialize repository: ${response.statusText}`);
  }

  return response.json();
}

export async function sendChatMessage(
  owner: string,
  repo: string,
  query: string,
  history: [string, string][] = []
): Promise<ChatResponse> {
  const response = await fetch(API_ENDPOINTS.chat, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ owner, repo, query, history }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `Failed to get chat response: ${response.statusText}`);
  }

  return response.json();
}

export async function checkHealth(): Promise<{ status: string }> {
  const response = await fetch(API_ENDPOINTS.healthCheck);
  if (!response.ok) {
    throw new Error('Backend health check failed');
  }
  return response.json();
}

