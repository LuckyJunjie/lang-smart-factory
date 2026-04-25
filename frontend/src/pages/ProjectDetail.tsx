import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api, Project, Requirement } from '../api'

export default function ProjectDetail() {
  const { id } = useParams<{ id: string }>()
  const [project, setProject] = useState<Project | null>(null)
  const [requirements, setRequirements] = useState<Requirement[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return
    const pid = parseInt(id)
    
    Promise.all([
      api.getProject(pid),
      api.getRequirements(pid)
    ])
      .then(([p, r]) => {
        setProject(p)
        setRequirements(r)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [id])

  if (loading) return <div>加载中...</div>
  if (!project) return <div>项目未找到</div>

  return (
    <div>
      <div className="mb-6">
        <Link to="/projects" className="text-blue-600 hover:underline">← 返回项目列表</Link>
      </div>

      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <h2 className="text-2xl font-bold mb-4">{project.name}</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div>
            <p className="text-gray-500 text-sm">编码</p>
            <p className="font-mono">{project.code || `P${project.id}`}</p>
          </div>
          <div>
            <p className="text-gray-500 text-sm">状态</p>
            <span className={`px-2 py-1 rounded text-sm ${
              project.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100'
            }`}>
              {project.status}
            </span>
          </div>
          <div>
            <p className="text-gray-500 text-sm">创建时间</p>
            <p>{project.created_at ? new Date(project.created_at).toLocaleDateString() : '-'}</p>
          </div>
          <div>
            <p className="text-gray-500 text-sm">需求数量</p>
            <p className="text-2xl font-bold">{requirements.length}</p>
          </div>
        </div>
        {project.desc_alias && (
          <div className="mt-4">
            <p className="text-gray-500 text-sm">描述</p>
            <p>{project.desc_alias}</p>
          </div>
        )}
        {project.repo_url && (
          <div className="mt-4">
            <p className="text-gray-500 text-sm">仓库</p>
            <a href={project.repo_url} className="text-blue-600 hover:underline font-mono text-sm">
              {project.repo_url}
            </a>
          </div>
        )}
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="p-4 border-b flex justify-between items-center">
          <h3 className="text-lg font-semibold">需求列表</h3>
          <Link
            to="/requirements"
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            + 新建需求
          </Link>
        </div>
        
        {requirements.length === 0 ? (
          <div className="p-8 text-center text-gray-500">暂无需求</div>
        ) : (
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left">编码</th>
                <th className="px-4 py-3 text-left">标题</th>
                <th className="px-4 py-3 text-left">优先级</th>
                <th className="px-4 py-3 text-left">状态</th>
              </tr>
            </thead>
            <tbody>
              {requirements.map((r) => (
                <tr key={r.id} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-3 font-mono text-sm">{r.code || `REQ${r.id}`}</td>
                  <td className="px-4 py-3">{r.title}</td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-sm ${
                      r.priority >= 3 ? 'bg-red-100 text-red-800' : 'bg-gray-100'
                    }`}>
                      P{r.priority}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded text-sm ${
                      r.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100'
                    }`}>
                      {r.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}
