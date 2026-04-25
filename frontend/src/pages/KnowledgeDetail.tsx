import { useEffect, useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'

interface KnowledgeItem {
  id: number
  title: string
  content: string
  category: string
  tags: string
  source: string
  created_by: string
  created_at: string
  updated_at: string
  status: string
  project_id?: number
  requirement_id?: number
}

interface Project {
  id: number
  name: string
}

export default function KnowledgeDetail() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [item, setItem] = useState<KnowledgeItem | null>(null)
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState(false)
  const [editData, setEditData] = useState<Partial<KnowledgeItem>>({})

  useEffect(() => {
    loadData()
  }, [id])

  const loadData = async () => {
    if (!id) return
    setLoading(true)
    try {
      const [itemRes, projectsRes] = await Promise.all([
        fetch(`/api/knowledge/items/${id}`),
        fetch('/api/projects')
      ])
      const itemData = await itemRes.json()
      const projectsData = await projectsRes.json()
      setItem(itemData)
      setProjects(Array.isArray(projectsData) ? projectsData : [])
      setEditData(itemData)
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!id) return
    try {
      await fetch(`/api/knowledge/items/${id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editData)
      })
      setEditing(false)
      loadData()
    } catch (err) {
      console.error(err)
      alert('保存失败')
    }
  }

  const handleDelete = async () => {
    if (!id || !confirm('确定删除这条知识？')) return
    try {
      await fetch(`/api/knowledge/items/${id}`, { method: 'DELETE' })
      navigate('/knowledge-base')
    } catch (err) {
      console.error(err)
      alert('删除失败')
    }
  }

  if (loading) return <div className="p-4">加载中...</div>
  if (!item) return <div className="p-4">知识未找到</div>

  const project = projects.find(p => p.id === item.project_id)

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link to="/knowledge-base" className="text-blue-600 hover:underline">
          ← 返回知识库
        </Link>
      </div>

      <div className="bg-white rounded-lg shadow">
        {editing ? (
          <div className="p-6">
            <h2 className="text-xl font-bold mb-4">编辑知识</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">标题</label>
                <input
                  type="text"
                  value={editData.title || ''}
                  onChange={e => setEditData({...editData, title: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-1">内容</label>
                <textarea
                  value={editData.content || ''}
                  onChange={e => setEditData({...editData, content: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                  rows={8}
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium mb-1">分类</label>
                  <input
                    type="text"
                    value={editData.category || ''}
                    onChange={e => setEditData({...editData, category: e.target.value})}
                    className="w-full border rounded px-3 py-2"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium mb-1">标签</label>
                  <input
                    type="text"
                    value={editData.tags || ''}
                    onChange={e => setEditData({...editData, tags: e.target.value})}
                    className="w-full border rounded px-3 py-2"
                    placeholder="逗号分隔"
                  />
                </div>
              </div>
              <div className="flex justify-end gap-2">
                <button onClick={() => setEditing(false)} className="px-4 py-2 text-gray-600">取消</button>
                <button onClick={handleSave} className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">保存</button>
              </div>
            </div>
          </div>
        ) : (
          <div className="p-6">
            {/* Meta */}
            <div className="flex justify-between items-start mb-4">
              <div>
                <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-sm mr-2">
                  {item.category || '未分类'}
                </span>
                <span className={`px-2 py-1 rounded text-sm ${
                  item.status === 'pinned' ? 'bg-yellow-100 text-yellow-700' : 'bg-gray-100 text-gray-600'
                }`}>
                  {item.status}
                </span>
              </div>
              <div className="flex gap-2">
                <button onClick={() => setEditing(true)} className="px-3 py-1 text-blue-600 border border-blue-600 rounded hover:bg-blue-50">
                  编辑
                </button>
                <button onClick={handleDelete} className="px-3 py-1 text-red-600 border border-red-600 rounded hover:bg-red-50">
                  删除
                </button>
              </div>
            </div>

            {/* Title */}
            <h1 className="text-2xl font-bold mb-4">{item.title}</h1>

            {/* Content */}
            <div className="prose max-w-none mb-6">
              <p className="whitespace-pre-wrap text-gray-700">{item.content}</p>
            </div>

            {/* Tags */}
            {item.tags && (
              <div className="flex flex-wrap gap-2 mb-6">
                {item.tags.split(',').map(tag => (
                  <span key={tag} className="px-3 py-1 bg-gray-100 rounded-full text-sm">
                    #{tag.trim()}
                  </span>
                ))}
              </div>
            )}

            {/* Meta Info */}
            <div className="border-t pt-4 text-sm text-gray-500">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <span className="font-medium">来源:</span> {item.source}
                </div>
                <div>
                  <span className="font-medium">创建者:</span> {item.created_by}
                </div>
                <div>
                  <span className="font-medium">创建时间:</span> {item.created_at?.slice(0, 16)}
                </div>
                <div>
                  <span className="font-medium">更新时间:</span> {item.updated_at?.slice(0, 16)}
                </div>
                {project && (
                  <div>
                    <span className="font-medium">关联项目:</span>{' '}
                    <Link to={`/projects/${project.id}`} className="text-blue-600 hover:underline">
                      {project.name}
                    </Link>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}