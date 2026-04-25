import { Link, useLocation } from 'react-router-dom'

interface LayoutProps {
  children: React.ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/projects', label: '项目管理', icon: '📁' },
    { path: '/requirements', label: '需求管理', icon: '📋' },
    { path: '/tasks', label: '任务看板', icon: '📋' },
    { path: '/dependencies', label: '依赖关系', icon: '🔗' },
    { path: '/audit', label: '审计日志', icon: '📝' },
    { path: '/knowledge-base', label: '知识库', icon: '📚' },
    { path: '/knowledge', label: '知识收集', icon: '🔄' },
  ]

  const toolItems = [
    { path: '/tools/code-generator', label: '代码生成', icon: '🔧' },
    { path: '/tools/feature-tree', label: '特性树', icon: '🌳' },
    { path: '/tools/doc-exporter', label: '文档导出', icon: '📄' },
  ]

  return (
    <div className="min-h-screen flex">
      {/* Sidebar */}
      <aside className="w-64 bg-gray-800 text-white flex-shrink-0">
        <div className="p-4 border-b border-gray-700">
          <h1 className="text-xl font-bold">Smart Factory</h1>
          <p className="text-sm text-gray-400">项目管理平台</p>
        </div>
        <nav className="p-4">
          <p className="text-xs text-gray-500 uppercase mb-2">导航</p>
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg mb-1 transition-colors ${
                location.pathname === item.path
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}
          
          <p className="text-xs text-gray-500 uppercase mt-4 mb-2">工具</p>
          {toolItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg mb-1 transition-colors ${
                location.pathname === item.path
                  ? 'bg-purple-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </Link>
          ))}

          <div className="mt-4 pt-4 border-t border-gray-700">
            <Link
              to="/settings"
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                location.pathname === '/settings'
                  ? 'bg-gray-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              <span>⚙️</span>
              <span>设置</span>
            </Link>
          </div>
        </nav>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-auto bg-gray-50">
        {children}
      </main>
    </div>
  )
}