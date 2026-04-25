import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import ProjectDetail from './pages/ProjectDetail'
import Requirements from './pages/Requirements'
import RequirementDetail from './pages/RequirementDetail'
import TaskBoard from './pages/TaskBoard'
import KnowledgeBase from './pages/KnowledgeBase'
import KnowledgeDetail from './pages/KnowledgeDetail'
import KnowledgeCollection from './pages/KnowledgeCollection'
import Dependencies from './pages/Dependencies'
import AuditLog from './pages/AuditLog'
import Settings from './pages/Settings'
import CodeGenerator from './components/CodeGenerator'
import FeatureTree from './components/FeatureTree'
import DocExporter from './components/DocExporter'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/projects" element={<Projects />} />
        <Route path="/projects/:id" element={<ProjectDetail />} />
        <Route path="/requirements" element={<Requirements />} />
        <Route path="/requirements/:id" element={<RequirementDetail />} />
        <Route path="/tasks" element={<TaskBoard />} />
        <Route path="/knowledge-base" element={<KnowledgeBase />} />
        <Route path="/knowledge-base/:id" element={<KnowledgeDetail />} />
        <Route path="/knowledge" element={<KnowledgeCollection />} />
        <Route path="/dependencies" element={<Dependencies />} />
        <Route path="/audit" element={<AuditLog />} />
        <Route path="/settings" element={<Settings />} />
        <Route path="/tools/code-generator" element={<CodeGenerator />} />
        <Route path="/tools/feature-tree" element={<FeatureTree />} />
        <Route path="/tools/doc-exporter" element={<DocExporter />} />
      </Routes>
    </Layout>
  )
}

export default App