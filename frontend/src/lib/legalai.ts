import apiClient from './api';

export const legalaiApi = {
  // Search
  searchChunks: (q: string, domains?: string, limit = 10) =>
    apiClient.get('/legalai/search/chunks', { params: { q, domains, limit } }),
  searchLaws: (q: string, domains?: string, limit = 20) =>
    apiClient.get('/legalai/search/laws', { params: { q, domains, limit } }),

  // Chat
  createSession: (title?: string) =>
    apiClient.post('/legalai/chat/sessions', { title }),
  listSessions: () =>
    apiClient.get('/legalai/chat/sessions'),
  getMessages: (sessionId: string) =>
    apiClient.get(`/legalai/chat/sessions/${sessionId}/messages`),
  askQuestion: (question: string, sessionId?: string, domains?: string[]) =>
    apiClient.post('/legalai/chat/ask', { question, session_id: sessionId, domains }),

  // Laws
  listLaws: (params?: { law_type?: string; domain?: string; status?: string; limit?: number }) =>
    apiClient.get('/legalai/laws', { params }),
  getLaw: (id: string) =>
    apiClient.get(`/legalai/laws/${id}`),

  // Documents
  uploadDocument: (file: File) => {
    const form = new FormData();
    form.append('file', file);
    return apiClient.post('/legalai/documents/upload', form, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },
  listDocuments: () =>
    apiClient.get('/legalai/documents'),
  deleteDocument: (id: string) =>
    apiClient.delete(`/legalai/documents/${id}`),

  // Crawler (admin)
  getCrawlerStats: () =>
    apiClient.get('/legalai/crawler/stats'),
  getCrawlerSources: () =>
    apiClient.get('/legalai/crawler/sources'),
  crawlUrl: (url: string) =>
    apiClient.post('/legalai/crawler/crawl', { url }),
  crawlPriority: () =>
    apiClient.post('/legalai/crawler/crawl-priority'),
  listCrawlJobs: () =>
    apiClient.get('/legalai/crawler/jobs'),
};
