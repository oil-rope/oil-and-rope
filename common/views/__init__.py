"""
List of views that are generic and can be used all around the project.
"""

from .auth import StaffRequiredMixin
from .list import MultiplePaginatorListView

__all__ = [
    'MultiplePaginatorListView', 'StaffRequiredMixin'
]
