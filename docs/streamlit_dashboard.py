#!/usr/bin/env python3
"""
Smart Factory Dashboard - Streamlit Web UI
智慧工厂项目管理看板
"""

import streamlit as st
import os
import requests
import json
from datetime import datetime

# Configuration
API_BASE = os.environ.get("SMART_FACTORY_API", "http://192.168.3.75:5000/api").rstrip("/")

st.set_page_config(
    page_title="智慧工厂控制台",
    page_icon="🏭",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .status-active { color: #28a745; }
    .status-in_progress { color: #ffc107; }
    .status-done { color: #17a2b8; }
    .status-blocked { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

def get_projects():
    try:
        r = requests.get(f"{API_BASE}/projects", timeout=5)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def get_requirements(status=None):
    try:
        url = f"{API_BASE}/requirements"
        if status:
            url += f"?status={status}"
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def get_tasks(req_id=None):
    try:
        url = f"{API_BASE}/requirements/{req_id}/tasks" if req_id else f"{API_BASE}/tasks"
        r = requests.get(url, timeout=5)
        return r.json() if r.status_code == 200 else []
    except:
        return []

def get_dashboard_stats():
    try:
        r = requests.get(f"{API_BASE}/dashboard/stats", timeout=5)
        return r.json() if r.status_code == 200 else {}
    except:
        return {}

def get_pipelines():
    try:
        r = requests.get(f"{API_BASE}/pipelines", timeout=5)
        return r.json() if r.status_code == 200 else []
    except:
        return []

# Sidebar
st.sidebar.title("🏭 智慧工厂")
st.sidebar.markdown("---")

page = st.sidebar.radio("导航", ["Dashboard", "项目管理", "需求管理", "任务管理", "CI/CD", "Pipeline"])

# Main content
if page == "Dashboard":
    st.title("📊 智慧工厂仪表盘")
    
    # Stats
    stats = get_dashboard_stats()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        projects = stats.get('projects', [])
        total = sum(p.get('count', 0) for p in projects)
        st.metric("项目总数", total)
    with col2:
        reqs = stats.get('requirements', [])
        total = sum(p.get('count', 0) for p in reqs)
        st.metric("需求总数", total)
    with col3:
        tasks = stats.get('tasks', [])
        total = sum(p.get('count', 0) for p in tasks)
        st.metric("任务总数", total)
    with col4:
        machines = stats.get('machines', [])
        total = sum(p.get('count', 0) for p in machines)
        st.metric("机器总数", total)
    
    # Recent projects
    st.subheader("📁 项目概览")
    projects = get_projects()
    if projects:
        for p in projects[:10]:
            status_color = "🟢" if p.get('status') == 'active' else "🟡" if p.get('status') == 'in_progress' else "🔵"
            st.markdown(f"{status_color} **{p.get('name')}** - {p.get('description', 'N/A')} (进度: {p.get('progress_percent', 0)}%)")
    else:
        st.info("无法连接到API服务")

elif page == "项目管理":
    st.title("📁 项目管理")
    
    projects = get_projects()
    
    # New project form
    with st.expander("➕ 新建项目"):
        with st.form("new_project"):
            name = st.text_input("项目名称")
            desc = st.text_area("描述")
            repo = st.text_input("GitHub仓库")
            submitted = st.form_submit_button("创建")
            if submitted and name:
                # API call would go here
                st.success(f"项目 {name} 创建成功!")
    
    # Project list
    for p in projects:
        with st.expander(f"{p.get('name')} ({p.get('status')})"):
            st.write(f"**描述:** {p.get('description', 'N/A')}")
            st.write(f"**仓库:** {p.get('github_repo', 'N/A')}")
            st.write(f"**进度:** {p.get('progress_percent', 0)}%")
            st.write(f"**问题状态:** {p.get('issue_status', 'N/A')}")

elif page == "需求管理":
    st.title("📋 需求管理")
    
    # Filter
    status_filter = st.selectbox("状态筛选", ["all", "new", "in_progress", "done", "blocked"])
    
    requirements = get_requirements(status_filter if status_filter != "all" else None)
    
    for req in requirements:
        priority_emoji = "🔴" if req.get('priority') == 'P0' else "🟠" if req.get('priority') == 'P1' else "🟡"
        st.markdown(f"{priority_emoji} **{req.get('title')}** ({req.get('status')})")
        st.write(f"项目ID: {req.get('project_id')} | 类型: {req.get('type')} | 进度: {req.get('progress_percent', 0)}%")
        st.markdown("---")

elif page == "任务管理":
    st.title("✅ 任务管理")
    
    # Select requirement
    requirements = get_requirements()
    req_options = {f"{r.get('title')} (ID: {r.get('id')})": r.get('id') for r in requirements}
    selected_req = st.selectbox("选择需求", list(req_options.keys()))
    
    if selected_req:
        req_id = req_options[selected_req]
        tasks = get_tasks(req_id)
        
        st.subheader(f"需求 {req_id} 的任务")
        
        # Auto-split button
        if st.button("🤖 自动生成任务"):
            # API call would go here
            st.info("自动任务拆分功能")
        
        for task in tasks:
            status_icon = "⬜" if task.get('status') == 'todo' else "🔄" if task.get('status') == 'in_progress' else "✅" if task.get('status') == 'done' else "⏸️"
            st.markdown(f"{status_icon} {task.get('title')} - {task.get('status')}")

elif page == "CI/CD":
    st.title("⚙️ CI/CD 构建")
    
    # List builds
    builds_url = f"{API_BASE}/cicd/builds"
    try:
        r = requests.get(builds_url, timeout=5)
        builds = r.json() if r.status_code == 200 else []
        
        for build in builds[:20]:
            status_icon = "🔴" if build.get('status') == 'failed' else "🟢" if build.get('status') == 'success' else "🟡"
            st.markdown(f"{status_icon} **Build #{build.get('id')}** - {build.get('pipeline_name')} - {build.get('status')}")
            st.write(f"Commit: {build.get('commit_sha', 'N/A')[:8]} | Branch: {build.get('branch')}")
            st.markdown("---")
    except Exception as e:
        st.error(f"无法连接到API: {e}")

elif page == "Pipeline":
    st.title("🔄 Pipeline 工作流")
    
    pipelines = get_pipelines()
    
    for p in pipelines:
        with st.expander(f"📦 {p.get('name')}"):
            st.write(f"**描述:** {p.get('description', 'N/A')}")
            st.write(f"**触发类型:** {p.get('trigger_type')}")
            st.write(f"**状态:** {p.get('status')}")
            st.write(f"**最后运行:** {p.get('last_run_at', '从未')}")
            
            if st.button(f"▶️ 触发运行 #{p.get('id')}"):
                # API call would go here
                st.success("Pipeline已触发!")

# Footer
st.markdown("---")
st.markdown(f"🕐 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    # Run with: streamlit run docs/streamlit_dashboard.py
    st.info("运行命令: streamlit run docs/streamlit_dashboard.py")
