"""
Smart Factory API Routes
Flask Blueprint routes for project management
"""

from .project_routes import project_bp
from .requirement_routes import requirement_bp
from .dependencies import dependencies_bp

__all__ = [
    'project_bp',
    'requirement_bp',
    'dependencies_bp',
]
