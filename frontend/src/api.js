const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8011'
).replace(/\/+$/, '')

export async function request(path, options = {}) {
  let response
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        ...(options.body ? { 'Content-Type': 'application/json' } : {}),
        ...options.headers,
      },
    })
  } catch {
    throw new Error('Cannot reach the API. Start the FastAPI server and retry.')
  }

  if (response.status === 204) return null

  let data
  try {
    data = await response.json()
  } catch {
    throw new Error(`The API returned an unreadable response (${response.status}).`)
  }

  if (!response.ok) {
    const detail = typeof data.detail === 'string'
      ? data.detail
      : `Request failed (${response.status}).`
    throw new Error(detail)
  }
  return data
}

export const api = {
  health: () => request('/api/health'),
  stats: () => request('/api/stats'),
  papers: ({ search = '', limit = 50, offset = 0, sort = 'title' } = {}) => {
    const params = new URLSearchParams({ search, limit: String(limit), offset: String(offset), sort })
    return request(`/api/papers?${params}`)
  },
  paper: (id) => request(`/api/papers/${encodeURIComponent(id)}`),
  search: (query) => request(`/api/search?q=${encodeURIComponent(query)}`),
  graph: (limit = 100) => request(`/api/graph?limit=${limit}`),
  node: (id) => request(`/api/nodes/${encodeURIComponent(id)}`),
  connections: (id) => request(`/api/nodes/${encodeURIComponent(id)}/connections`),
  assistant: (question) => request('/api/assistant/query', {
    method: 'POST',
    body: JSON.stringify({ question }),
  }),
  compare: (paperIds) => request('/api/compare', {
    method: 'POST',
    body: JSON.stringify({ paper_ids: paperIds }),
  }),
  gaps: () => request('/api/gaps'),
  collections: () => request('/api/collections'),
  createCollection: (name) => request('/api/collections', {
    method: 'POST',
    body: JSON.stringify({ name }),
  }),
  renameCollection: (id, name) => request(`/api/collections/${encodeURIComponent(id)}`, {
    method: 'PATCH',
    body: JSON.stringify({ name }),
  }),
  deleteCollection: (id) => request(`/api/collections/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  }),
  addToCollection: (collectionId, paperId) => request(
    `/api/collections/${encodeURIComponent(collectionId)}/papers?paper_id=${encodeURIComponent(paperId)}`,
    { method: 'POST' },
  ),
  removeFromCollection: (collectionId, paperId) => request(
    `/api/collections/${encodeURIComponent(collectionId)}/papers?paper_id=${encodeURIComponent(paperId)}`,
    { method: 'DELETE' },
  ),
  importPreview: (filename, content) => request('/api/import/preview', {
    method: 'POST',
    body: JSON.stringify({ filename, content }),
  }),
}
