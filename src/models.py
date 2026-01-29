"""Data models for positive cyber news stories."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class CyberGoodNews:
    """Represents a single positive cybersecurity news story."""

    id: Optional[str]
    title: str
    description: str
    source: str
    source_url: str
    published_date: datetime
    collected_date: datetime
    category: str
    impact_score: float  # 0-10 scale (how positive/impactful)
    summary: Optional[str] = None
    tags: Optional[List[str]] = None
    is_processed: bool = False
    is_sent: bool = False

    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'source': self.source,
            'source_url': self.source_url,
            'published_date': self.published_date.isoformat(),
            'collected_date': self.collected_date.isoformat(),
            'category': self.category,
            'impact_score': self.impact_score,
            'summary': self.summary,
            'tags': self.tags,
            'is_processed': self.is_processed,
            'is_sent': self.is_sent,
        }
