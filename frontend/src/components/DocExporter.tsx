import { useState, useEffect } from 'react'
import { api } from '../api'

export default function DocExporter() {
  const [projects, setProjects] = useState<any[]>([])
  const [selectedProject, setSelectedProject] = useState<number | null>(null)
  const [format, setFormat] = useState<'markdown' | 'json'>('markdown')
  const [document, setDocument] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    api.getProjects().then(setProjects).catch(console.error)
  }, [])

  const handleExport = async () => {
    if (!selectedProject) return
    
    setLoading(true)
    try {
      const response = await fetch(`/api/projects/${selectedProject}/document?format=${format}`)
      const text = await response.text()
      setDocument(text)
    } catch (err) {
      console.error('Export failed:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = () => {
    if (!document) return
    
    const blob = new Blob([document], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `project-${selectedProject}-document.${format === 'json' ? 'json' : 'md'}`
    a.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="max-w-4xl">
      <h2 className="text-2xl font-bold mb-6">📄 文档导出器</h2>
      
      <div className="bg-white rounded-lg shadow p-6 mb-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              选择项目
            </label>
            <select
              value={selectedProject || ''}
              onChange={(e) => setSelectedProject(Number(e.target.value))}
              className="w-full border rounded px-3 py-2"
            >
              <option value="">-- 选择项目 --</option>
              {projects.map((p) => (
                <option key={p.id} value={p.id}>
                  {p.name} ({p.code || `P${p.id}`})
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              文档格式
            </label>
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value as typeof format)}
              className="w-full border rounded px-3 py-2"
            >
              <option value="markdown">Markdown (.md)</option>
              <option value="json">JSON (.json)</option>
            </select>
          </div>
        </div>
        
        <button
          onClick={handleExport}
          disabled={!selectedProject || loading}
          className="mt-4 bg-blue-600 text-white py-2 px-6 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '导出中...' : '导出文档'}
        </button>
      </div>

      {document && (
        <div className="bg-white rounded-lg shadow">
          <div className="p-4 border-b flex justify-between items-center">
            <h3 className="font-semibold">预览</h3>
            <button
              onClick={handleDownload}
              className="bg-green-600 text-white py-1 px-4 rounded hover:bg-green-700"
            >
              ⬇️ 下载
            </button>
          </div>
          <pre className="p-4 text-sm overflow-auto max-h-96 bg-gray-50 whitespace-pre-wrap">
            {document}
          </pre>
        </div>
      )}
    </div>
  )
}