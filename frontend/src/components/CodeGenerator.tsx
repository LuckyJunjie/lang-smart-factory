import { useState } from 'react'
import { api } from '../api'

export default function CodeGenerator() {
  const [entityType, setEntityType] = useState<'project' | 'requirement' | 'feature' | 'test_case'>('project')
  const [generatedCode, setGeneratedCode] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleGenerate = async () => {
    setLoading(true)
    setError(null)
    setGeneratedCode(null)
    
    try {
      const response = await fetch('/api/mcp/project/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: `Auto-${entityType}-${Date.now()}`,
          agent: 'GUI'
        })
      })
      
      if (!response.ok) {
        // Fallback: 直接调用后端生成
        const res = await fetch('/api/projects', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name: `Temp-${entityType}` })
        })
        const data = await res.json()
        setGeneratedCode(data.code || `Generated ID: ${data.id}`) 
      } else {
        const data = await response.json()
        setGeneratedCode(data.code)
      }
    } catch (err) {
      setError('生成失败: ' + (err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-xl">
      <h2 className="text-2xl font-bold mb-6">📝 代码生成器</h2>
      
      <div className="bg-white rounded-lg shadow p-6">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            实体类型
          </label>
          <select
            value={entityType}
            onChange={(e) => setEntityType(e.target.value as typeof entityType)}
            className="w-full border rounded px-3 py-2"
          >
            <option value="project">Project (P001)</option>
            <option value="requirement">Requirement (REQ001)</option>
            <option value="feature">Feature (F001)</option>
            <option value="test_case">Test Case (TC001)</option>
          </select>
        </div>

        <button
          onClick={handleGenerate}
          disabled={loading}
          className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '生成中...' : '生成编码'}
        </button>

        {error && (
          <div className="mt-4 p-3 bg-red-100 text-red-700 rounded">
            {error}
          </div>
        )}

        {generatedCode && (
          <div className="mt-4 p-4 bg-green-100 rounded">
            <p className="text-sm text-gray-600">生成的编码:</p>
            <p className="text-2xl font-mono font-bold text-green-800">{generatedCode}</p>
          </div>
        )}
      </div>
    </div>
  )
}