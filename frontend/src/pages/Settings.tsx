import { useState } from 'react'

export default function Settings() {
  const [settings, setSettings] = useState({
    apiUrl: '/api',
    theme: 'light',
    language: 'zh-CN',
    autoRefresh: true,
    refreshInterval: 30,
  })

  const handleSave = () => {
    localStorage.setItem('smart_factory_settings', JSON.stringify(settings))
    alert('设置已保存')
  }

  return (
    <div className="max-w-2xl">
      <h2 className="text-2xl font-bold mb-6">设置</h2>

      <div className="bg-white rounded-lg shadow p-6">
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              API 地址
            </label>
            <input
              type="text"
              value={settings.apiUrl}
              onChange={(e) => setSettings({ ...settings, apiUrl: e.target.value })}
              className="w-full border rounded px-3 py-2"
              placeholder="/api"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              主题
            </label>
            <select
              value={settings.theme}
              onChange={(e) => setSettings({ ...settings, theme: e.target.value })}
              className="w-full border rounded px-3 py-2"
            >
              <option value="light">浅色</option>
              <option value="dark">深色</option>
              <option value="auto">自动</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              语言
            </label>
            <select
              value={settings.language}
              onChange={(e) => setSettings({ ...settings, language: e.target.value })}
              className="w-full border rounded px-3 py-2"
            >
              <option value="zh-CN">简体中文</option>
              <option value="en-US">English</option>
            </select>
          </div>

          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.autoRefresh}
                onChange={(e) => setSettings({ ...settings, autoRefresh: e.target.checked })}
                className="mr-2"
              />
              <span className="text-sm font-medium text-gray-700">自动刷新数据</span>
            </label>
          </div>

          {settings.autoRefresh && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                刷新间隔（秒）
              </label>
              <input
                type="number"
                min="10"
                max="300"
                value={settings.refreshInterval}
                onChange={(e) => setSettings({ ...settings, refreshInterval: parseInt(e.target.value) })}
                className="w-full border rounded px-3 py-2"
              />
            </div>
          )}

          <div className="pt-4 border-t">
            <button
              onClick={handleSave}
              className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700"
            >
              保存设置
            </button>
          </div>
        </div>
      </div>

      <div className="mt-6 bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">系统信息</h3>
        <dl className="space-y-2 text-sm">
          <div className="flex justify-between">
            <dt className="text-gray-500">版本</dt>
            <dd className="font-mono">1.0.0</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-gray-500">构建时间</dt>
            <dd className="font-mono">{new Date().toLocaleString()}</dd>
          </div>
          <div className="flex justify-between">
            <dt className="text-gray-500">API</dt>
            <dd className="font-mono">{settings.apiUrl}</dd>
          </div>
        </dl>
      </div>
    </div>
  )
}
