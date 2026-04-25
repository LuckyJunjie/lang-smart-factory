import { useState } from 'react'

interface Props {
  requirementId: number
  onAction?: () => void
}

const TEAMS = ['einstein', 'curie', 'galileo', 'darwin', 'hawking']

export default function RequirementActions({ requirementId, onAction }: Props) {
  const [showModal, setShowModal] = useState(false)
  const [action, setAction] = useState<'take' | 'assign' | 'auto-split' | null>(null)
  const [loading, setLoading] = useState(false)

  const handleAction = async () => {
    setLoading(true)
    try {
      const endpoint = action === 'take' 
        ? `/api/requirements/${requirementId}/take`
        : action === 'assign'
        ? `/api/requirements/${requirementId}/assign`
        : `/api/requirements/${requirementId}/auto-split`
      
      const body = action === 'auto-split' 
        ? {} 
        : { assigned_team: TEAMS[0], assigned_agent: TEAMS[0] }
      
      await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
      })
      
      setShowModal(false)
      onAction?.()
    } catch (err) {
      alert('操作失败: ' + (err as Error).message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="flex gap-2">
        <button
          onClick={() => { setAction('take'); setShowModal(true) }}
          className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
        >
          接取
        </button>
        <button
          onClick={() => { setAction('assign'); setShowModal(true) }}
          className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded hover:bg-purple-200"
        >
          分配
        </button>
        <button
          onClick={() => { setAction('auto-split'); setShowModal(true) }}
          className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded hover:bg-green-200"
        >
          自动拆分
        </button>
      </div>

      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-sm">
            <h3 className="font-semibold mb-4">
              {action === 'take' ? '接取需求' : action === 'assign' ? '分配需求' : '自动拆分'}
            </h3>
            
            {action !== 'auto-split' && (
              <div className="mb-4">
                <label className="block text-sm mb-2">选择团队</label>
                <select className="w-full border rounded px-3 py-2">
                  {TEAMS.map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
              </div>
            )}

            <div className="flex gap-2 justify-end">
              <button
                onClick={() => setShowModal(false)}
                className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded"
              >
                取消
              </button>
              <button
                onClick={handleAction}
                disabled={loading}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
              >
                {loading ? '处理中...' : '确认'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}