"""RSS feed collector for positive cyber news."""

import feedparser
import hashlib
from datetime import datetime
from typing import List
from .base import BaseCollector
from ..models import CyberGoodNews
from ..config import Config


class RSSCollector(BaseCollector):
    """Collects positive cybersecurity news from RSS feeds."""

    def __init__(self):
        super().__init__("RSS Feeds")
        self.feeds = Config.RSS_FEEDS

    def collect(self) -> List[CyberGoodNews]:
        """Collect from all configured RSS feeds."""
        all_stories = []

        for feed_info in self.feeds:
            try:
                stories = self._collect_from_feed(feed_info)
                all_stories.extend(stories)
                print(f"  Collected {len(stories)} items from {feed_info['name']}")
            except Exception as e:
                print(f"  Error collecting from {feed_info['name']}: {str(e)}")

        return all_stories

    def _collect_from_feed(self, feed_info: dict) -> List[CyberGoodNews]:
        """Collect from a single RSS feed."""
        feed = feedparser.parse(feed_info['url'])
        stories = []

        for entry in feed.entries:
            story_id = hashlib.md5(entry.link.encode()).hexdigest()

            published_date = datetime.now()
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published_date = datetime(*entry.published_parsed[:6])

            description = ''
            if hasattr(entry, 'summary'):
                description = entry.summary
            elif hasattr(entry, 'description'):
                description = entry.description

            story = CyberGoodNews(
                id=story_id,
                title=entry.title,
                description=description,
                source=feed_info['name'],
                source_url=entry.link,
                published_date=published_date,
                collected_date=datetime.now(),
                category='Uncategorized',
                impact_score=0.0,
            )

            stories.append(story)

        return stories

    def is_available(self) -> bool:
        return True
