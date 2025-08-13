"""
Configuration Package

This package contains configuration settings and environment management
for the healthcare web application backend.
"""

from .settings import settings, get_settings

__all__ = ["settings", "get_settings"]
