"""Positive cyber news collectors."""

from .base import BaseCollector
from .rss_collector import RSSCollector

__all__ = [
    'BaseCollector',
    'RSSCollector',
]
