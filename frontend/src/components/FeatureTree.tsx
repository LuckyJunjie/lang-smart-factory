import { useState, useEffect } from 'react'
import { api } from '../api'

interface TreeNode {
  id: number
  type: 'project' | 'requirement' | 'feature' | 'test_case'
  name: string
  code: string
  children?: TreeNode[]
  expanded?: boolean
}

export default function FeatureTree() {
  const [projects, setProjects] = useState<any[]>([])
  const [treeData, setTreeData] = useState<TreeNode[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      const data = await api.getProjects()
      setProjects(data)
      
      // Build tree
      const tree = await Promise.all(
        data.map(async (p) => {
          const requirements = await api.getRequirements(p.id)
          const children = requirements.map((r: any) => ({
            id: r.id,
            type: 'requirement' as const,
            name: r.title,
            code: r.code || `REQ${r.id}`,
            children: [],
          }))
          return {
            id: p.id,
            type: 'project' as const,
            name: p.name,
            code: p.code || `P${p.id}`,
            children,
            expanded: false,
          }
        })
      )
      
      setTreeData(tree)
    } catch (err) {
      console.error('Failed to load:', err)
    } finally {
      setLoading(false)
    }
  }

  const toggleExpand = (nodeId: number) => {
    const toggle = (nodes: TreeNode[]): TreeNode[] =>
      nodes.map((n) => {
        if (n.id === nodeId) {
          return { ...n, expanded: !n.expanded }
        }
        if (n.children) {
          return { ...n, children: toggle(n.children) }
        }
        return n
      })
    setTreeData(toggle(treeData))
  }

  const TypeIcon = ({ type }: { type: string }) => {
    const icons: Record<string, string> = {
      project: '📁',
      requirement: '📋',
      feature: '✨',
      test_case: '🧪',
    }
    return <span className="mr-2">{icons[type] || '📄'}</span>
  }

  const renderNode = (node: TreeNode, depth: number = 0) => (
    <div key={`${node.type}-${node.id}`} style={{ marginLeft: depth * 20 }}>
      <div
        className="flex items-center py-1 px-2 hover:bg-gray-100 rounded cursor-pointer"
        onClick={() => node.children && node.children.length > 0 && toggleExpand(node.id)}
      >
        {node.children && node.children.length > 0 && (
          <span className="mr-1 text-xs">{node.expanded ? '▼' : '▶'}</span>
        )}
        <TypeIcon type={node.type} />
        <span className="font-medium">{node.name}</span>
        <span className="ml-2 text-xs text-gray-500 font-mono">{node.code}</span>
      </div>
      {node.expanded && node.children && (
        <div>
          {node.children.map((child) => renderNode(child, depth + 1))}
        </div>
      )}
    </div>
  )

  if (loading) {
    return <div className="p-4">加载中...</div>
  }

  return (
    <div className="max-w-3xl">
      <h2 className="text-2xl font-bold mb-6">🌳 特性树</h2>
      
      <div className="bg-white rounded-lg shadow p-6">
        {treeData.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            暂无项目数据
          </div>
        ) : (
          <div className="space-y-2">
            {treeData.map((node) => renderNode(node))}
          </div>
        )}
      </div>
    </div>
  )
}