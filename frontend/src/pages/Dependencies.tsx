import { useEffect, useState } from 'react'
import { api, Dependency } from '../api'

export default function Dependencies() {
  const [dependencies, setDependencies] = useState<Dependency[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getDependencies()
      .then(setDependencies)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="text-gray-500">加载中...</div>
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">依赖关系</h2>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left">来源类型</th>
              <th className="px-4 py-3 text-left">来源ID</th>
              <th className="px-4 py-3 text-left">目标类型</th>
              <th className="px-4 py-3 text-left">目标ID</th>
              <th className="px-4 py-3 text-left">依赖类型</th>
            </tr>
          </thead>
          <tbody>
            {dependencies.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-gray-500">
                  暂无依赖关系
                </td>
              </tr>
            ) : (
              dependencies.map((d) => (
                <tr key={d.id} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                      {d.source_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono">{d.source_id}</td>
                  <td className="px-4 py-3">
                    <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded">
                      {d.target_type}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-mono">{d.target_id}</td>
                  <td className="px-4 py-3 text-gray-600">{d.dep_type || '-'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-6 bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">依赖关系说明</h3>
        <ul className="list-disc list-inside text-gray-600 space-y-2">
          <li>依赖类型可以是: <code className="bg-gray-100 px-1 rounded">blocks</code>, <code className="bg-gray-100 px-1 rounded">requires</code>, <code className="bg-gray-100 px-1 rounded">relates_to</code></li>
          <li>来源和目标可以是: <code className="bg-gray-100 px-1 rounded">project</code>, <code className="bg-gray-100 px-1 rounded">requirement</code>, <code className="bg-gray-100 px-1 rounded">feature</code></li>
        </ul>
      </div>
    </div>
  )
}
