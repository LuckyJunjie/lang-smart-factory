const API_BASE = '/api'

export interface Project {
  id: number
  code: string
  name: string
  desc_alias?: string
  status: string
  repo_url?: string
  created_at?: string
  updated_at?: string
  owner?: string
  expected_revenue?: number
  progress_percent?: number
}

export interface Requirement {
  id: number
  project_id: number
  code: string
  title: string
  description?: string
  priority: number
  status: string
  created_at?: string
  updated_at?: string
}

export interface Dependency {
  id: number
  source_type: string
  source_id: number
  target_type: string
  target_id: number
  dep_type?: string
  created_at?: string
}

export interface AuditLog {
  id: number
  agent_name: string
  operation: string
  target_type?: string
  target_id?: string
  details?: string
  status: string
  created_at?: string
}

async function fetchJSON<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })
  if (!response.ok) {
    throw new Error(`API Error: ${response.status}`)
  }
  return response.json()
}

export const api = {
  // Projects
  getProjects: () => fetchJSON<Project[]>('/projects'),
  getProject: (id: number) => fetchJSON<Project>(`/projects/${id}`),
  createProject: (data: Partial<Project>) =>
    fetchJSON<{ id: number; code: string }>('/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateProject: (id: number, data: Partial<Project>) =>
    fetchJSON<{ status: string }>(`/projects/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  deleteProject: (id: number) =>
    fetchJSON<{ status: string }>(`/projects/${id}`, { method: 'DELETE' }),

  // Requirements
  getRequirements: (projectId?: number) =>
    fetchJSON<Requirement[]>(
      projectId ? `/requirements?project_id=${projectId}` : '/requirements'
    ),
  getRequirement: (id: number) => fetchJSON<Requirement>(`/requirements/${id}`),
  createRequirement: (data: Partial<Requirement>) =>
    fetchJSON<{ id: number; code: string }>('/requirements', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  updateRequirement: (id: number, data: Partial<Requirement>) =>
    fetchJSON<{ status: string }>(`/requirements/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
  deleteRequirement: (id: number) =>
    fetchJSON<{ status: string }>(`/requirements/${id}`, { method: 'DELETE' }),

  // Dependencies
  getDependencies: () => fetchJSON<Dependency[]>('/dependencies'),
  createDependency: (data: Partial<Dependency>) =>
    fetchJSON<{ id: number }>('/dependencies', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  // Audit Logs
  getAuditLogs: () => fetchJSON<AuditLog[]>('/audit_logs'),
}
