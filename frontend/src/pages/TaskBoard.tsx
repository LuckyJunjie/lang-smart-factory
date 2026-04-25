import { useEffect, useState } from 'react'
import { api } from '../api'

interface Task {
  id: number
  title: string
  status: string
  executor: string
  risk: string
  blocker: string
  next_step_task_id: number | null
  assigned_agent: string
  assigned_team: string
}

export default function TaskBoard() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch('/api/tasks')
      .then(r => r.json())
      .then(data => {
        if (Array.isArray(data)) setTasks(data)
        else if (data.tasks) setTasks(data.tasks)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const statusGroups = {
    new: tasks.filter(t => t.status === 'new'),
    in_progress: tasks.filter(t => t.status === 'in_progress'),
    done: tasks.filter(t => t.status === 'done'),
  }

  if (loading) return <div className="p-4">加载中...</div>

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">📋 任务看板</h2>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {(['new', 'in_progress', 'done'] as const).map(status => (
          <div key={status} className="bg-white rounded-lg shadow">
            <div className={`px-4 py-3 border-b font-semibold ${
              status === 'new' ? 'bg-gray-50' :
              status === 'in_progress' ? 'bg-blue-50' : 'bg-green-50'
            }`}>
              {status === 'new' ? '🆕 待办' : status === 'in_progress' ? '🔄 进行中' : '✅ 已完成'}
              <span className="ml-2 text-sm text-gray-500">({statusGroups[status].length})</span>
            </div>
            <div className="p-4 space-y-3">
              {statusGroups[status].length === 0 ? (
                <p className="text-gray-400 text-sm text-center">暂无</p>
              ) : (
                statusGroups[status].map(task => (
                  <div key={task.id} className={`border rounded p-3 ${
                    task.risk === 'high' ? 'border-red-300 bg-red-50' : ''
                  }`}>
                    <h4 className="font-medium mb-2">{task.title}</h4>
                    <div className="text-xs text-gray-500 space-y-1">
                      <p>执行者: {task.assigned_agent || task.executor || '-'}</p>
                      <p>团队: {task.assigned_team || '-'}</p>
                      {task.blocker && (
                        <p className="text-red-600">⛔ 阻塞: {task.blocker}</p>
                      )}
                      {task.next_step_task_id && (
                        <p className="text-blue-600">→ 下一步: #{task.next_step_task_id}</p>
                      )}
                    </div>
                    {task.risk === 'high' && (
                      <span className="mt-2 inline-block px-2 py-1 bg-red-100 text-red-700 text-xs rounded">
                        ⚠️ 高风险
                      </span>
                    )}
                  </div>
                ))
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}