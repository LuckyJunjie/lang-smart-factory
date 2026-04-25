import { useEffect, useState } from 'react'
import { api, Project, Requirement } from '../api'

export default function Dashboard() {
  const [projects, setProjects] = useState<Project[]>([])
  const [requirements, setRequirements] = useState<Requirement[]>([])
  const [auditCount, setAuditCount] = useState(0)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([
      api.getProjects(),
      api.getRequirements(),
    ])
      .then(([p, r]) => {
        setProjects(p)
        setRequirements(r)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
    
    // 加载审计日志数量
    fetch('/api/audit_logs?limit=1')
      .then(r => r.json())
      .then(data => setAuditCount(Array.isArray(data) ? data.length : 0))
      .catch(() => {})
  }, [])

  if (loading) {
    return <div className="text-gray-500">加载中...</div>
  }

  const activeProjects = projects.filter((p) => p.status === 'active').length
  const totalRevenue = projects.reduce((sum, p) => sum + (p.expected_revenue || 0), 0)
  const avgProgress = projects.length > 0 
    ? Math.round(projects.reduce((sum, p) => sum + (p.progress_percent || 0), 0) / projects.length)
    : 0

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">📊 Dashboard</h2>

      <div className="grid grid-cols-1 md:grid-cols-6 gap-4 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-sm">总项目数</p>
          <p className="text-3xl font-bold text-blue-600">{projects.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-sm">活跃项目</p>
          <p className="text-3xl font-bold text-green-600">{activeProjects}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-sm">总需求数</p>
          <p className="text-3xl font-bold text-purple-600">{requirements.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-sm">审计日志</p>
          <p className="text-3xl font-bold text-orange-600">{auditCount}+</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-sm">预期总收益</p>
          <p className="text-2xl font-bold text-yellow-600">{(totalRevenue/1000).toFixed(0)}k</p>
        </div>
        <div className="bg-white rounded-lg shadow p-6">
          <p className="text-gray-500 text-sm">平均进度</p>
          <p className="text-3xl font-bold text-teal-600">{avgProgress}%</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">📁 最近项目</h3>
          <ul className="space-y-2">
            {projects.slice(0, 5).map((p) => (
              <li key={p.id} className="flex justify-between items-center p-2 hover:bg-gray-50 rounded">
                <div>
                  <span className="font-medium">{p.name}</span>
                  {p.owner && <span className="ml-2 text-xs text-gray-500">👤 {p.owner}</span>}
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-xs">{p.progress_percent || 0}%</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    p.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    {p.status}
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">📋 最近需求</h3>
          <ul className="space-y-2">
            {requirements.slice(0, 5).map((r) => (
              <li key={r.id} className="p-2 hover:bg-gray-50 rounded">
                <div className="flex justify-between">
                  <span className="font-medium">{r.code || `REQ${r.id}`}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    r.priority >= 3 ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    P{r.priority}
                  </span>
                </div>
                <p className="text-sm text-gray-600 truncate">{r.title}</p>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  )
}