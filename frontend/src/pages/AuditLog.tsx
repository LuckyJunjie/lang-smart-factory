import { useEffect, useState } from 'react'
import { api, AuditLog as AuditLogType } from '../api'

export default function AuditLog() {
  const [logs, setLogs] = useState<AuditLogType[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getAuditLogs()
      .then(setLogs)
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="text-gray-500">加载中...</div>
  }

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return '-'
    return new Date(dateStr).toLocaleString('zh-CN')
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">审计日志</h2>

      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left">时间</th>
              <th className="px-4 py-3 text-left">操作人</th>
              <th className="px-4 py-3 text-left">操作</th>
              <th className="px-4 py-3 text-left">对象类型</th>
              <th className="px-4 py-3 text-left">对象ID</th>
              <th className="px-4 py-3 text-left">状态</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 ? (
              <tr>
                <td colSpan={6} className="px-4 py-8 text-center text-gray-500">
                  暂无审计日志
                </td>
              </tr>
            ) : (
              logs.slice(0, 100).map((log) => (
                <tr key={log.id} className="border-t hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {formatDate(log.created_at)}
                  </td>
                  <td className="px-4 py-3">
                    <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded">
                      {log.agent_name}
                    </span>
                  </td>
                  <td className="px-4 py-3 font-medium">{log.operation}</td>
                  <td className="px-4 py-3 text-gray-600">{log.target_type || '-'}</td>
                  <td className="px-4 py-3 font-mono text-sm">{log.target_id || '-'}</td>
                  <td className="px-4 py-3">
                    <span className={`text-xs px-2 py-1 rounded ${
                      log.status === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {log.status}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
