"""
Smart Factory Database Models (from Origin)
These are SQLAlchemy model definitions for documentation.
Actual database uses SQLite with Smart Factory schema.
"""

# Model definitions for reference
# These match the SQLite tables: projects, requirements, origin_features, origin_test_cases, dependencies, audit_logs

class ProjectModel:
    """Project model - matches projects table"""
    fields = {
        'id': 'INTEGER PRIMARY KEY',
        'code': 'TEXT UNIQUE NOT NULL',
        'name': 'TEXT NOT NULL',
        'desc_alias': 'TEXT',
        'status': "TEXT DEFAULT 'active'",
        'repo_url': 'TEXT',
        'created_at': 'TEXT',
        'updated_at': 'TEXT'
    }

class RequirementModel:
    """Requirement model - matches requirements table"""
    fields = {
        'id': 'INTEGER PRIMARY KEY',
        'project_id': 'INTEGER NOT NULL',
        'code': 'TEXT UNIQUE NOT NULL',
        'title': 'TEXT NOT NULL',
        'description': 'TEXT',
        'priority': 'INTEGER DEFAULT 0',
        'status': "TEXT DEFAULT 'active'",
        'created_at': 'TEXT',
        'updated_at': 'TEXT'
    }

class FeatureModel:
    """Feature model - matches origin_features table"""
    fields = {
        'id': 'INTEGER PRIMARY KEY',
        'requirement_id': 'INTEGER NOT NULL',
        'code': 'TEXT UNIQUE NOT NULL',
        'name': 'TEXT NOT NULL',
        'tech_notes': 'TEXT',
        'art_asset_required': 'TEXT',
        'priority': 'INTEGER DEFAULT 0',
        'status': "TEXT DEFAULT 'active'",
        'created_at': 'TEXT',
        'updated_at': 'TEXT'
    }

class TestCaseModel:
    """TestCase model - matches origin_test_cases table"""
    fields = {
        'id': 'INTEGER PRIMARY KEY',
        'feature_id': 'INTEGER NOT NULL',
        'code': 'TEXT UNIQUE NOT NULL',
        'precondition': 'TEXT',
        'steps': 'TEXT',
        'expected_result': 'TEXT',
        'priority': 'INTEGER DEFAULT 0',
        'status': "TEXT DEFAULT 'active'",
        'created_at': 'TEXT',
        'updated_at': 'TEXT'
    }

class DependencyModel:
    """Dependency model - matches dependencies table"""
    fields = {
        'id': 'INTEGER PRIMARY KEY',
        'source_type': 'TEXT NOT NULL',
        'source_id': 'INTEGER NOT NULL',
        'target_type': 'TEXT NOT NULL',
        'target_id': 'INTEGER NOT NULL',
        'dep_type': 'TEXT',
        'created_at': 'TEXT'
    }

class AuditLogModel:
    """AuditLog model - matches audit_logs table"""
    fields = {
        'id': 'INTEGER PRIMARY KEY',
        'agent_name': 'TEXT NOT NULL',
        'operation': 'TEXT NOT NULL',
        'target_type': 'TEXT',
        'target_id': 'TEXT',
        'details': 'TEXT',
        'status': "TEXT DEFAULT 'success'",
        'created_at': 'TEXT'
    }

# Export model schemas
__all__ = [
    'ProjectModel',
    'RequirementModel',
    'FeatureModel',
    'TestCaseModel',
    'DependencyModel',
    'AuditLogModel'
]
