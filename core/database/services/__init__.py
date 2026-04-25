"""
Smart Factory Database Services
核心业务逻辑服务层
"""

from .id_generator import generate_code, get_entity_by_code
from .audit_logger import log_audit, get_audit_logs
from .dependency_manager import (
    add_dependency,
    get_dependencies,
    delete_dependency,
    detect_priority_inversion,
    would_create_cycle,
)
from .document_generator import (
    generate_project_document,
    generate_dependency_graph,
)

__all__ = [
    # ID Generator
    'generate_code',
    'get_entity_by_code',
    # Audit
    'log_audit',
    'get_audit_logs',
    # Dependency
    'add_dependency',
    'get_dependencies',
    'delete_dependency',
    'detect_priority_inversion',
    'would_create_cycle',
    # Document
    'generate_project_document',
    'generate_dependency_graph',
]
