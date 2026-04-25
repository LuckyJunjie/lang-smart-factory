import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api'

export default function RequirementDetail() {
  const { id } = useParams<{ id: string }>()
  const [requirement, setRequirement] = useState<any>(null)
  const [project, setProject] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    const rid = parseInt(id)
    
    Promise.all([
      api.getRequirement(rid),
      api.getProjects()
    ])
      .then(([r, projects]) => {
        setRequirement(r)
        // Find parent project
        const parentProject = projects.find((p: any) => p.id === r.project_id)
        setProject(parentProject)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div className="p-4">加载中...</div>
  if (!requirement) return <div className="p-4">需求未找到</div>

  return (
    <div>
      <div className="mb-6">
        <Link to="/requirements" className="text-blue-600 hover:underline">← 返回需求列表</Link>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-2xl font-bold">{requirement.title}</h2>
            <p className="text-gray-500 font-mono text-sm">
              编码: {requirement.code || `REQ${requirement.id}`}
            </p>
          </div>
          <span className={`px-3 py-1 rounded ${
            requirement.status === 'active' ? 'bg-green-100 text-green-800' :
            requirement.status === 'completed' ? 'bg-blue-100 text-blue-800' :
            'bg-gray-100'
          }`}>
            {requirement.status}
          </span>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div>
            <p className="text-gray-500 text-sm">优先级</p>
            <span className={`px-2 py-1 rounded text-sm ${
              requirement.priority >= 3 ? 'bg-red-100 text-red-800' : 'bg-gray-100'
            }`}>
              P{requirement.priority}
            </span>
          </div>
          <div>
            <p className="text-gray-500 text-sm">所属项目</p>
            <Link to={`/projects/${requirement.project_id}`} className="text-blue-600 hover:underline">
              {project?.name || `P${requirement.project_id}`}
            </Link>
          </div>
          <div>
            <p className="text-gray-500 text-sm">创建时间</p>
            <p>{requirement.created_at ? new Date(requirement.created_at).toLocaleDateString() : '-'}</p>
          </div>
          <div>
            <p className="text-gray-500 text-sm">进度</p>
            <p>{requirement.progress_percent || 0}%</p>
          </div>
        </div>

        {requirement.description && (
          <div className="mt-4">
            <p className="text-gray-500 text-sm mb-1">描述</p>
            <p className="text-gray-700">{requirement.description}</p>
          </div>
        )}

        {requirement.acceptance_criteria && (
          <div className="mt-4">
            <p className="text-gray-500 text-sm mb-1">验收标准</p>
            <p className="text-gray-700">{requirement.acceptance_criteria}</p>
          </div>
        )}

        {requirement.depends_on && (
          <div className="mt-4">
            <p className="text-gray-500 text-sm mb-1">依赖</p>
            <p className="text-gray-700 font-mono text-sm">{requirement.depends_on}</p>
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">✨ 关联特性</h3>
        <p className="text-gray-500 text-sm">（特性数据将显示在这里）</p>
        {/* Features would be loaded from origin_features table */}
      </div>
    </div>
  )
}