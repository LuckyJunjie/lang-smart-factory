import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'

interface KnowledgeItem {
  id: number
  title: string
  content: string
  category: string
  tags: string
  source: string
  created_by: string
  created_at: string
  status: string
  project_id?: number
}

interface Category {
  id: number
  name: string
  description: string
  color: string
  icon: string
}

interface Project {
  id: number
  name: string
}

export default function KnowledgeBase() {
  const [items, setItems] = useState<KnowledgeItem[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [projects, setProjects] = useState<Project[]>([])
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [selectedProject, setSelectedProject] = useState<number | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState<'recent' | 'title'>('recent')
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [viewMode, setViewMode] = useState<'cards' | 'list'>('cards')
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set())
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: '',
    tags: '',
    source: 'manual',
    project_id: null as number | null,
  })

  useEffect(() => {
    loadData()
  }, [selectedCategory, selectedProject])

  const loadData = async () => {
    setLoading(true)
    try {
      let url = '/api/knowledge/items?'
      if (selectedCategory) url += `category=${encodeURIComponent(selectedCategory)}&`
      const [itemsRes, catsRes, projectsRes] = await Promise.all([
        fetch(url),
        fetch('/api/knowledge/categories'),
        fetch('/api/projects')
      ])
      const itemsData = await itemsRes.json()
      const catsData = await catsRes.json()
      const projectsData = await projectsRes.json()
      setItems(Array.isArray(itemsData) ? itemsData : [])
      setCategories(Array.isArray(catsData) ? catsData : [])
      setProjects(Array.isArray(projectsData) ? projectsData : [])
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      const payload = { ...formData }
      if (!payload.project_id) delete payload.project_id
      await fetch('/api/knowledge/items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      })
      setFormData({ title: '', content: '', category: '', tags: '', source: 'manual', project_id: null })
      setShowForm(false)
      loadData()
    } catch (err) {
      console.error(err)
      alert('创建失败')
    }
  }

  const handleSearch = async () => {
    if (!searchTerm.trim()) {
      loadData()
      return
    }
    setLoading(true)
    try {
      const res = await fetch(`/api/knowledge/search?q=${encodeURIComponent(searchTerm)}`)
      const data = await res.json()
      setItems(Array.isArray(data) ? data : [])
    } catch (err) {
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const handleBulkDelete = async () => {
    if (selectedIds.size === 0 || !confirm(`删除 ${selectedIds.size} 条知识？`)) return
    try {
      await Promise.all(
        Array.from(selectedIds).map(id =>
          fetch(`/api/knowledge/items/${id}`, { method: 'DELETE' })
        )
      )
      setSelectedIds(new Set())
      loadData()
    } catch (err) {
      console.error(err)
      alert('删除失败')
    }
  }

  const filteredItems = selectedProject
    ? items.filter(item => item.project_id === selectedProject)
    : items

  const sortedItems = [...filteredItems].sort((a, b) => {
    if (sortBy === 'recent') {
      return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    }
    return a.title.localeCompare(b.title)
  })

  const toggleSelect = (id: number) => {
    const newSet = new Set(selectedIds)
    if (newSet.has(id)) newSet.delete(id)
    else newSet.add(id)
    setSelectedIds(newSet)
  }

  const stats = {
    total: sortedItems.length,
    byCategory: categories.reduce((acc, cat) => {
      acc[cat.name] = items.filter(i => i.category === cat.name).length
      return acc
    }, {} as Record<string, number>)
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-2xl font-bold">📚 知识库</h2>
          <p className="text-sm text-gray-500">{stats.total} 条知识</p>
        </div>
        <div className="flex gap-2">
          <button onClick={() => setViewMode('cards')} className={`px-3 py-1 rounded ${viewMode === 'cards' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100'}`}>📰</button>
          <button onClick={() => setViewMode('list')} className={`px-3 py-1 rounded ${viewMode === 'list' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100'}`}>📋</button>
          {selectedIds.size > 0 && (
            <button onClick={handleBulkDelete} className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200">
              删除 ({selectedIds.size})
            </button>
          )}
          <button onClick={() => setShowForm(!showForm)} className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
            {showForm ? '取消' : '+ 新建'}
          </button>
        </div>
      </div>

      {/* New Form */}
      {showForm && (
        <div className="bg-white rounded-lg shadow p-4 mb-4">
          <h3 className="font-semibold mb-3">新建知识条目</h3>
          <form onSubmit={handleCreate} className="grid grid-cols-2 gap-4">
            <input type="text" placeholder="标题 *" value={formData.title} onChange={e => setFormData({...formData, title: e.target.value})} className="col-span-2 border rounded px-3 py-2" required />
            <textarea placeholder="内容" value={formData.content} onChange={e => setFormData({...formData, content: e.target.value})} className="col-span-2 border rounded px-3 py-2" rows={3} />
            <select value={formData.category} onChange={e => setFormData({...formData, category: e.target.value})} className="border rounded px-3 py-2">
              <option value="">选择分类</option>
              {categories.map(cat => <option key={cat.id} value={cat.name}>{cat.icon} {cat.name}</option>)}
            </select>
            <select value={formData.project_id || ''} onChange={e => setFormData({...formData, project_id: e.target.value ? Number(e.target.value) : null})} className="border rounded px-3 py-2">
              <option value="">关联项目</option>
              {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
            </select>
            <input type="text" placeholder="标签 (逗号分隔)" value={formData.tags} onChange={e => setFormData({...formData, tags: e.target.value})} className="border rounded px-3 py-2" />
            <div className="col-span-2 flex justify-end gap-2">
              <button type="button" onClick={() => setShowForm(false)} className="px-4 py-2 text-gray-600">取消</button>
              <button type="submit" className="bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700">保存</button>
            </div>
          </form>
        </div>
      )}

      <div className="flex flex-1 gap-4 overflow-hidden">
        {/* Sidebar */}
        <div className="w-56 flex-shrink-0 bg-white rounded-lg shadow p-4 overflow-auto">
          <div className="mb-4">
            <div className="flex gap-1">
              <input type="text" placeholder="搜索..." value={searchTerm} onChange={e => setSearchTerm(e.target.value)} className="flex-1 border rounded px-2 py-1 text-sm" onKeyDown={e => e.key === 'Enter' && handleSearch()} />
              <button onClick={handleSearch} className="bg-blue-100 px-2 py-1 rounded text-sm">🔍</button>
            </div>
          </div>

          {/* Project Filter */}
          <h3 className="font-semibold mb-2">关联项目</h3>
          <select value={selectedProject || ''} onChange={e => setSelectedProject(e.target.value ? Number(e.target.value) : null)} className="w-full border rounded px-2 py-1 text-sm mb-4">
            <option value="">全部项目</option>
            {projects.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
          </select>

          {/* Sort */}
          <h3 className="font-semibold mb-2">排序</h3>
          <div className="space-y-1 mb-4">
            <button onClick={() => setSortBy('recent')} className={`w-full text-left px-3 py-1 rounded text-sm ${sortBy === 'recent' ? 'bg-blue-100' : 'hover:bg-gray-100'}`}>最近</button>
            <button onClick={() => setSortBy('title')} className={`w-full text-left px-3 py-1 rounded text-sm ${sortBy === 'title' ? 'bg-blue-100' : 'hover:bg-gray-100'}`}>标题</button>
          </div>

          <h3 className="font-semibold mb-2">分类</h3>
          <div className="space-y-1">
            <button onClick={() => { setSelectedCategory(''); setSelectedProject(null); loadData(); }} className={`w-full text-left px-3 py-2 rounded flex justify-between items-center ${!selectedCategory ? 'bg-blue-100 font-medium' : 'hover:bg-gray-100'}`}>
              <span>📋 全部</span><span className="text-xs text-gray-500">{items.length}</span>
            </button>
            {categories.map(cat => (
              <button key={cat.id} onClick={() => { setSelectedCategory(cat.name); setSelectedProject(null); loadData(); }} className={`w-full text-left px-3 py-2 rounded flex justify-between items-center ${selectedCategory === cat.name ? 'bg-blue-100 font-medium' : 'hover:bg-gray-100'}`} style={{ borderLeft: `3px solid ${cat.color}` }}>
                <span>{cat.icon} {cat.name}</span><span className="text-xs text-gray-500">{stats.byCategory[cat.name] || 0}</span>
              </button>
            ))}
          </div>

          <h3 className="font-semibold mt-4 mb-2">热门标签</h3>
          <div className="flex flex-wrap gap-1">
            {['godot', 'python', 'react', 'api', '游戏'].map(tag => (
              <button key={tag} onClick={() => { setSearchTerm(tag); handleSearch(); }} className="px-2 py-1 bg-gray-100 rounded text-xs hover:bg-blue-100">#{tag}</button>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-auto">
          {loading ? (
            <div className="flex items-center justify-center h-64"><div className="text-gray-500">加载中...</div></div>
          ) : viewMode === 'cards' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {sortedItems.map(item => (
                <div key={item.id} className="bg-white rounded-lg shadow p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start mb-2">
                    <input type="checkbox" checked={selectedIds.has(item.id)} onChange={() => toggleSelect(item.id)} className="mr-2" />
                    <Link to={`/knowledge-base/${item.id}`} className="flex-1">
                      <h3 className="font-semibold line-clamp-2 hover:text-blue-600">{item.title}</h3>
                    </Link>
                  </div>
                  <p className="text-gray-600 text-sm line-clamp-3 mb-3">{item.content}</p>
                  {item.tags && (
                    <div className="flex flex-wrap gap-1 mb-3">
                      {item.tags.split(',').slice(0, 3).map(tag => <span key={tag} className="px-2 py-0.5 bg-gray-100 rounded text-xs">#{tag.trim()}</span>)}
                    </div>
                  )}
                  <div className="flex justify-between text-xs text-gray-400 pt-2 border-t">
                    <span>{item.source}</span>
                    <span>{item.created_at?.slice(0, 10)}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow">
              {sortedItems.map((item, idx) => (
                <div key={item.id} className={`p-4 hover:bg-gray-50 flex items-start gap-3 ${idx !== 0 ? 'border-t' : ''}`}>
                  <input type="checkbox" checked={selectedIds.has(item.id)} onChange={() => toggleSelect(item.id)} className="mt-1" />
                  <Link to={`/knowledge-base/${item.id}`} className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">{item.category || '未分类'}</span>
                      <h3 className="font-medium">{item.title}</h3>
                    </div>
                    <p className="text-gray-600 text-sm line-clamp-2">{item.content}</p>
                  </Link>
                  <div className="text-xs text-gray-400 text-right">
                    <div>{item.source}</div>
                    <div>{item.created_at?.slice(0, 10)}</div>
                  </div>
                </div>
              ))}
            </div>
          )}
          {sortedItems.length === 0 && !loading && (
            <div className="flex flex-col items-center justify-center h-64 text-gray-500">
              <div className="text-4xl mb-2">📭</div>
              <div>{searchTerm ? '未找到' : '暂无知识'}</div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}