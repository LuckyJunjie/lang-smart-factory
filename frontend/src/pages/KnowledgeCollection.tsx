import { useState } from 'react'

export default function KnowledgeCollection() {
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<any>(null)
  const [error, setError] = useState<string | null>(null)

  const triggerCollection = async () => {
    setLoading(true)
    setError(null)
    setResult(null)
    
    try {
      const response = await fetch('/api/knowledge/collect', { method: 'POST' })
      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError((err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl">
      <h2 className="text-2xl font-bold mb-6">📚 知识收集</h2>
      
      <div className="bg-white rounded-lg shadow p-6">
        <p className="text-gray-600 mb-4">
          手动触发知识收集过程，从项目文档、代码注释等来源收集结构化知识。
        </p>
        
        <button
          onClick={triggerCollection}
          disabled={loading}
          className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? '收集中...' : '触发知识收集'}
        </button>

        {error && (
          <div className="mt-4 p-3 bg-red-100 text-red-700 rounded">
            错误: {error}
          </div>
        )}

        {result && (
          <div className="mt-4 p-4 bg-green-50 rounded">
            <h3 className="font-semibold mb-2">✅ 收集完成</h3>
            <pre className="text-sm overflow-auto">
              {typeof result === 'object' ? JSON.stringify(result, null, 2) : String(result)}
            </pre>
          </div>
        )}
      </div>

      <div className="mt-6 bg-white rounded-lg shadow p-6">
        <h3 className="font-semibold mb-4">自动知识收集</h3>
        <p className="text-gray-600 text-sm">
          知识收集会自动按计划运行。上次运行状态可通过检查日志查看。
        </p>
      </div>
    </div>
  )
}