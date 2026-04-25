#!/usr/bin/env python3
"""
Seed Smart Factory DB: 假想项目「OpenClaw 协作平台」— 15 个迭代需求，用于测试开发团队协调能力。

项目目标：轻量级分布式团队协作工具，验证 OpenClaw 集群的协作流程（需求发现、任务分配、风险上报、汇总上报）。

Usage:
  cd smart-factory && python3 scripts/seed_openclaw_collab_platform.py [--db PATH] [--init]
  --init: 若 DB 不存在则创建并执行 schema。
"""

import argparse
import os
import sqlite3
import sys
from datetime import datetime

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
_CORE_DB = os.path.join(_REPO_ROOT, "core", "db")

PROJECT_NAME = "OpenClaw 协作平台"
PROJECT_DESC = """轻量级分布式团队协作工具，用于验证 OpenClaw 集群的协作流程。
包含：用户管理、任务看板、风险跟踪、飞书集成等核心模块。
15 个迭代（每迭代 1 周），全面测试需求发现、任务分配、风险上报与汇总上报闭环。
团队：前端、后端、数据库、运维、测试；协调角色：项目管理 Agent、Program Manager Agent。"""

# 15 个迭代：每项 (迭代号, 需求标题, 需求描述含任务分解与风险, 任务列表 [(标题, 执行方)])
ITERATIONS = [
    (
        1,
        "迭代1：用户认证基础",
        """需求：实现用户注册、登录、JWT 鉴权。
任务分解：
- 后端：设计用户表，编写注册/登录 API（数据库团队 + 后端团队）
- 前端：开发登录/注册页面，接入 API（前端团队）
风险：数据库选型（MySQL vs PostgreSQL）需评估团队熟悉度 → 数据库团队上报风险，Program Manager 协调技术调研。""",
        [
            ("设计用户表，编写注册/登录 API", "数据库团队+后端团队"),
            ("开发登录/注册页面，接入 API", "前端团队"),
        ],
    ),
    (
        2,
        "迭代2：项目与看板模型",
        """需求：支持创建项目，每个项目包含默认看板列（待办、进行中、完成）。
任务分解：
- 数据库：项目表、看板列表（数据库团队）
- 后端：项目 CRUD API，看板列初始化逻辑（后端团队）
- 前端：项目列表页、项目创建表单（前端团队）
风险：项目与用户关联的权限设计复杂，可能影响进度 → 后端架构师上报风险，Program Manager 组织设计评审。""",
        [
            ("项目表、看板列表设计与迁移", "数据库团队"),
            ("项目 CRUD API，看板列初始化逻辑", "后端团队"),
            ("项目列表页、项目创建表单", "前端团队"),
        ],
    ),
    (
        3,
        "迭代3：任务卡片基础功能",
        """需求：在看板中创建、编辑、删除任务卡片。
任务分解：
- 数据库：任务表，关联看板列（数据库团队）
- 后端：任务 CRUD API（后端团队）
- 前端：看板视图，卡片拖拽排序（前端团队）
风险：前端拖拽库选择（如 dnd-kit 兼容性） → 前端架构师上报风险，Program Manager 安排技术预研。""",
        [
            ("任务表、关联看板列", "数据库团队"),
            ("任务 CRUD API", "后端团队"),
            ("看板视图，卡片拖拽排序", "前端团队"),
        ],
    ),
    (
        4,
        "迭代4：任务分配与成员管理",
        """需求：支持将任务分配给项目成员，项目成员可加入/退出项目。
任务分解：
- 后端：项目成员关系 API，任务分配接口（后端团队）
- 前端：成员选择器，任务卡片显示指派人（前端团队）
- 测试：编写成员管理场景测试（测试团队）
风险：无预设风险，用于测试正常流程。""",
        [
            ("项目成员关系 API，任务分配接口", "后端团队"),
            ("成员选择器，任务卡片显示指派人", "前端团队"),
            ("成员管理场景测试", "测试团队"),
        ],
    ),
    (
        5,
        "迭代5：实时协作（WebSocket）",
        """需求：实现看板多人实时更新（如任务拖拽时其他用户立即看到变化）。
任务分解：
- 后端：WebSocket 服务，房间管理（后端团队）
- 前端：WebSocket 客户端，同步状态（前端团队）
- 运维：配置负载均衡支持 WebSocket 长连接（运维团队）
风险：后端团队对 WebSocket 不熟悉，学习成本高 → 后端 Scrum Master 上报风险，Program Manager 协调内部培训或引入库。""",
        [
            ("WebSocket 服务，房间管理", "后端团队"),
            ("WebSocket 客户端，同步状态", "前端团队"),
            ("负载均衡支持 WebSocket 长连接", "运维团队"),
        ],
    ),
    (
        6,
        "迭代6：风险跟踪模块",
        """需求：支持创建风险、指派负责人、跟踪状态（待处理、处理中、已关闭）。
任务分解：
- 数据库：风险表（数据库团队）
- 后端：风险 CRUD API，风险上报接口（后端团队）
- 前端：风险列表页、风险详情表单（前端团队）
风险：风险状态流转逻辑复杂，需与现有任务系统关联 → 后端架构师上报风险，Program Manager 协调产品确认。""",
        [
            ("风险表设计与迁移", "数据库团队"),
            ("风险 CRUD API，风险上报接口", "后端团队"),
            ("风险列表页、风险详情表单", "前端团队"),
        ],
    ),
    (
        7,
        "迭代7：飞书集成基础",
        """需求：通过飞书机器人发送项目动态通知（如任务创建、风险上报）。
任务分解：
- 后端：飞书 API 对接，消息模板（后端团队）
- 运维：配置飞书机器人 Webhook 环境变量（运维团队）
风险：飞书 API 限频策略不明，可能导致通知延迟 → 后端团队上报风险，Program Manager 联系飞书技术支持。""",
        [
            ("飞书 API 对接，消息模板", "后端团队"),
            ("飞书机器人 Webhook 环境变量配置", "运维团队"),
        ],
    ),
    (
        8,
        "迭代8：迭代报表生成",
        """需求：生成迭代燃尽图、任务统计图表（按状态、成员）。
任务分解：
- 后端：统计数据 API（后端团队）
- 前端：图表库集成（ECharts），报表页面（前端团队）
- 测试：验证数据准确性（测试团队）
风险：大数据量下统计性能问题 → 数据库团队上报风险，Program Manager 安排索引优化迭代。""",
        [
            ("统计数据 API", "后端团队"),
            ("图表库集成（ECharts），报表页面", "前端团队"),
            ("验证数据准确性", "测试团队"),
        ],
    ),
    (
        9,
        "迭代9：搜索功能",
        """需求：支持全局搜索任务、项目、风险。
任务分解：
- 数据库：全文索引（数据库团队）
- 后端：搜索 API（后端团队）
- 前端：搜索框、结果展示（前端团队）
风险：Elasticsearch 引入会增加运维复杂度 → 运维团队上报风险，Program Manager 决定是否采用简单 LIKE 查询。""",
        [
            ("全文索引设计与实现", "数据库团队"),
            ("搜索 API", "后端团队"),
            ("搜索框、结果展示", "前端团队"),
        ],
    ),
    (
        10,
        "迭代10：通知中心",
        """需求：站内通知和邮件通知，用户可配置接收规则。
任务分解：
- 数据库：通知表、用户设置表（数据库团队）
- 后端：通知发送队列（后端团队）
- 前端：通知中心 UI（前端团队）
风险：邮件服务商 SMTP 不稳定 → 后端团队上报风险，Program Manager 协调备用服务。""",
        [
            ("通知表、用户设置表", "数据库团队"),
            ("通知发送队列", "后端团队"),
            ("通知中心 UI", "前端团队"),
        ],
    ),
    (
        11,
        "迭代11：性能优化（缓存）",
        """需求：引入 Redis 缓存热点数据（用户信息、看板数据）。
任务分解：
- 后端：集成 Redis，缓存策略实现（后端团队）
- 运维：部署 Redis 集群（运维团队）
- 测试：压测验证缓存效果（测试团队）
风险：缓存一致性问题可能导致脏数据 → 后端架构师上报风险，Program Manager 组织设计评审。""",
        [
            ("集成 Redis，缓存策略实现", "后端团队"),
            ("部署 Redis 集群", "运维团队"),
            ("压测验证缓存效果", "测试团队"),
        ],
    ),
    (
        12,
        "迭代12：安全性增强",
        """需求：XSS 过滤、CSRF 防护、接口限流。
任务分解：
- 后端：添加安全中间件（后端团队）
- 前端：输入过滤（前端团队）
- 运维：配置 WAF 规则（运维团队）
风险：限流策略可能误伤正常用户 → 测试团队上报风险，Program Manager 协调灰度发布。""",
        [
            ("安全中间件（XSS/CSRF/限流）", "后端团队"),
            ("输入过滤", "前端团队"),
            ("WAF 规则配置", "运维团队"),
        ],
    ),
    (
        13,
        "迭代13：移动端适配",
        """需求：实现响应式布局，支持手机浏览器访问。
任务分解：
- 前端：CSS 媒体查询，组件适配（前端团队）
- 测试：移动端兼容性测试（测试团队）
风险：部分组件库移动端样式异常 → 前端架构师上报风险，Program Manager 安排修复计划。""",
        [
            ("CSS 媒体查询，组件适配", "前端团队"),
            ("移动端兼容性测试", "测试团队"),
        ],
    ),
    (
        14,
        "迭代14：多语言支持（i18n）",
        """需求：支持中英文切换。
任务分解：
- 前端：国际化框架集成，语言文件（前端团队）
- 后端：多语言错误码（后端团队）
风险：翻译资源缺失，需协调外部资源 → 前端 Scrum Master 上报风险，Program Manager 联系翻译团队。""",
        [
            ("国际化框架集成，语言文件", "前端团队"),
            ("多语言错误码", "后端团队"),
        ],
    ),
    (
        15,
        "迭代15：插件系统原型",
        """需求：支持简单的插件机制，允许第三方扩展看板组件。
任务分解：
- 后端：插件注册 API，钩子机制（后端团队）
- 前端：插件加载沙箱（前端团队）
- 测试：插件安全性测试（测试团队）
风险：沙箱隔离不完善可能导致安全漏洞 → 测试团队上报风险，Program Manager 组织安全评审。""",
        [
            ("插件注册 API，钩子机制", "后端团队"),
            ("插件加载沙箱", "前端团队"),
            ("插件安全性测试", "测试团队"),
        ],
    ),
]


def get_db_path(db_path: str) -> str:
    if os.path.isabs(db_path):
        return db_path
    if not db_path or db_path == "factory.db":
        return os.path.join(_CORE_DB, "factory.db")
    return os.path.normpath(os.path.join(_REPO_ROOT, db_path))


def init_schema(conn: sqlite3.Connection) -> None:
    schema_path = os.path.join(_CORE_DB, "schema.sql")
    migrations_dir = os.path.join(_CORE_DB, "migrations")
    with open(schema_path) as f:
        conn.executescript(f.read())
    if os.path.isdir(migrations_dir):
        for f in sorted(os.listdir(migrations_dir)):
            if f.endswith(".sql"):
                path = os.path.join(migrations_dir, f)
                with open(path) as fp:
                    script = fp.read()
                try:
                    conn.executescript(script)
                except sqlite3.OperationalError as e:
                    err = str(e).lower()
                    if "duplicate column" not in err and "already exists" not in err:
                        raise
    conn.commit()


def ensure_project(conn: sqlite3.Connection) -> int:
    c = conn.cursor()
    c.execute("SELECT id FROM projects WHERE name = ?", (PROJECT_NAME,))
    row = c.fetchone()
    if row:
        c.execute(
            "UPDATE projects SET description=?, type=?, status=?, updated_at=? WHERE id=?",
            (PROJECT_DESC, "tool", "active", datetime.utcnow().isoformat(), row[0]),
        )
        conn.commit()
        return row[0]
    c.execute(
        """INSERT INTO projects (name, description, type, status, repo_url)
           VALUES (?, ?, ?, ?, ?)""",
        (PROJECT_NAME, PROJECT_DESC, "tool", "active", ""),
    )
    conn.commit()
    return c.lastrowid


def insert_requirement(conn: sqlite3.Connection, project_id: int, iteration_num: int, title: str, description: str) -> int:
    c = conn.cursor()
    plan_step_id = str(iteration_num)
    c.execute(
        """INSERT INTO requirements (
             project_id, title, description, priority, type, status,
             plan_step_id, plan_phase, step, progress_percent
           ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'not start', 0)""",
        (project_id, title, description, "P2", "feature", "new", plan_step_id, "iteration"),
    )
    conn.commit()
    return c.lastrowid


def insert_tasks(conn: sqlite3.Connection, req_id: int, tasks: list) -> None:
    c = conn.cursor()
    for title, executor in tasks:
        c.execute(
            """INSERT INTO tasks (req_id, title, description, status, executor)
               VALUES (?, ?, ?, 'todo', ?)""",
            (req_id, title, "", executor),
        )
    conn.commit()


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed OpenClaw 协作平台 15 迭代需求到 Smart Factory DB")
    parser.add_argument("--db", default=None, help="Path to factory.db")
    parser.add_argument("--init", action="store_true", help="Create DB and run schema if missing")
    args = parser.parse_args()
    db_path = get_db_path(args.db or "factory.db")

    if not os.path.isfile(db_path):
        if args.init:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = sqlite3.connect(db_path)
            init_schema(conn)
            conn.close()
            print("Created DB and ran schema at", db_path)
        else:
            print("DB not found:", db_path, file=sys.stderr)
            print("Run with --init to create and initialize it.", file=sys.stderr)
            return 1

    conn = sqlite3.connect(db_path)
    try:
        project_id = ensure_project(conn)
        print("Project:", PROJECT_NAME, "(id=%s)" % project_id)

        c = conn.cursor()
        c.execute("SELECT id FROM requirements WHERE project_id = ? AND plan_phase = ?", (project_id, "iteration"))
        existing = c.fetchall()
        if existing:
            print("Already have", len(existing), "iteration requirements for this project. Skip insert.")
            return 0

        for iteration_num, title, description, tasks in ITERATIONS:
            req_id = insert_requirement(conn, project_id, iteration_num, title, description)
            insert_tasks(conn, req_id, tasks)
            print("  Iteration %2d (req_id=%s): %s" % (iteration_num, req_id, title[:50]))

        print("Done: 15 iterations (requirements + tasks) inserted. Use GET /api/requirements?project_id=%s to list." % project_id)
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
