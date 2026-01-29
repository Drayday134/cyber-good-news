"""Database layer for positive cyber news storage."""

import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from .models import CyberGoodNews
from .config import Config
import os


class StoryDatabase:
    """SQLite database for storing positive cyber news stories."""

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or Config.DATABASE_PATH
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS stories (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT,
                    source TEXT NOT NULL,
                    source_url TEXT NOT NULL,
                    published_date TEXT NOT NULL,
                    collected_date TEXT NOT NULL,
                    category TEXT,
                    impact_score REAL,
                    summary TEXT,
                    tags TEXT,
                    is_processed INTEGER DEFAULT 0,
                    is_sent INTEGER DEFAULT 0
                )
            ''')

            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_impact_sent
                ON stories(impact_score, is_sent)
            ''')

            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_collected_date
                ON stories(collected_date DESC)
            ''')

            conn.commit()

    def save_story(self, story: CyberGoodNews) -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM stories WHERE id = ?', (story.id,))
            if cursor.fetchone():
                return False

            cursor.execute('''
                INSERT INTO stories (
                    id, title, description, source, source_url,
                    published_date, collected_date, category, impact_score,
                    summary, tags, is_processed, is_sent
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                story.id,
                story.title,
                story.description,
                story.source,
                story.source_url,
                story.published_date.isoformat(),
                story.collected_date.isoformat(),
                story.category,
                story.impact_score,
                story.summary,
                json.dumps(story.tags) if story.tags else None,
                1 if story.is_processed else 0,
                1 if story.is_sent else 0,
            ))
            conn.commit()
            return True

    def save_stories(self, stories: List[CyberGoodNews]) -> int:
        new_count = 0
        for story in stories:
            if self.save_story(story):
                new_count += 1
        return new_count

    def mark_as_sent(self, story_id: str):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('UPDATE stories SET is_sent = 1 WHERE id = ?', (story_id,))
            conn.commit()

    def get_stats(self) -> dict:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM stories')
            total = cursor.fetchone()[0]

            cursor.execute('SELECT COUNT(*) FROM stories WHERE is_sent = 1')
            sent = cursor.fetchone()[0]

            cursor.execute('SELECT AVG(impact_score) FROM stories WHERE impact_score > 0')
            avg_impact = cursor.fetchone()[0] or 0.0

            return {
                'total_stories': total,
                'sent_alerts': sent,
                'pending_alerts': total - sent,
                'avg_impact': round(avg_impact, 2),
            }
