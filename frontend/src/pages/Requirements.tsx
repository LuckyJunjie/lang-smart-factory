import { useEffect, useState } from 'react'
import { api, Requirement, Project } from '../api'
import RequirementActions from '../components/RequirementActions'

export default function Requirements() {
  const [requirements, setRequirements] = useState<Requirement[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [filterProject, setFilterProject] = useState<number | ''>('')

  const [formData, setFormData] = useState({
    project_id: 1,
    title: '',
    description: '',
    priority: 1,
  })

  const loadData = () => {
    setLoading(true)
    Promise.all([
      filterProject ? api.getRequirements(filterProject) : api.getRequirements(),
      api.getProjects(),
    ])
      .then(([r, p]) => {
        setRequirements(r)
        setProjects(p)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    loadData()
  }, [filterProject])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await api.createRequirement(formData)
      setFormData({ project_id: 1, title: '', description: '', priority: 1 })
      setShowForm(false)
      loadData()
    } catch (err) {
      console.error(err)
      alert('创建失败')
    }
  }

  if (loading) {
    return <div className="text-gray-500">加载中...</div>
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold">📋 需求管理</h2>
        <button
          onClick={() => setShowForm(!showForm)}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
        >
          {showForm ? '取消' : '+ 新建需求'}
        </button>
      </div>

      <div className="mb-4">
        <select
          value={filterProject}
          onChange={(e) => setFilterProject(e.target.value ? Number(e.target.value) : '')}
          className="border rounded px-3 py-2"
        >
          <option value="">全部项目</option>
          {projects.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="bg-white rounded-lg shadow p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <select
              value={formData.project_id}
              onChange={(e) => setFormData({ ...formData, project_id: Number(e.target.value) })}
              className="border rounded px-3 py-2"
              required
            >
              {projects.map((p) => (
                <option key={p.id} value={p.id}>{p.name}</option>
              ))}
            </select>
            <input
              type="number"
              min="0"
              max="5"
              placeholder="优先级 (0-5)"
              value={formData.priority}
              onChange={(e) => setFormData({ ...formData, priority: Number(e.target.value) })}
              className="border rounded px-3 py-2"
            />
            <input
              type="text"
              placeholder="需求标题"
              value={formData.title}
              onChange={(e) => setFormData({ ...formData, title: e.target.value })}
              className="border rounded px-3 py-2 md:col-span-2"
              required
            />
            <textarea
              placeholder="需求描述"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="border rounded px-3 py-2 md:col-span-2"
              rows={3}
            />
          </div>
          <button type="submit" className="mt-4 bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700">
            创建
          </button>
        </form>
      )}

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left">编码</th>
              <th className="px-4 py-3 text-left">标题</th>
              <th className="px-4 py-3 text-left">优先级</th>
              <th className="px-4 py-3 text-left">状态</th>
              <th className="px-4 py-3 text-left">操作</th>
            </tr>
          </thead>
          <tbody>
            {requirements.map((r) => (
              <tr key={r.id} className="border-t hover:bg-gray-50">
                <td className="px-4 py-3 font-mono text-sm">{r.code || `REQ${r.id}`}</td>
                <td className="px-4 py-3">
                  <p className="font-medium">{r.title}</p>
                  {r.description && <p className="text-sm text-gray-500 truncate">{r.description}</p>}
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-2 py-1 rounded ${
                    r.priority >= 3 ? 'bg-red-100 text-red-800' : 'bg-gray-100 text-gray-800'
                  }`}>
                    P{r.priority}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span className={`text-xs px-2 py-1 rounded ${
                    r.status === 'active' ? 'bg-green-100 text-green-800' :
                    r.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                    'bg-gray-100 text-gray-800'
                  }`}>
                    {r.status}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <RequirementActions 
                    requirementId={r.id} 
                    onAction={loadData} 
                  />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}