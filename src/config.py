"""Configuration management for Cyber Good News feed."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    # Discord
    DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL')

    # News API (optional)
    NEWS_API_KEY = os.getenv('NEWS_API_KEY')

    # Collection settings
    COLLECTION_INTERVAL_MINUTES = int(os.getenv('COLLECTION_INTERVAL_MINUTES', '60'))
    MIN_IMPACT_SCORE = int(os.getenv('MIN_IMPACT_SCORE', '5'))
    MAX_ALERTS_PER_HOUR = int(os.getenv('MAX_ALERTS_PER_HOUR', '5'))

    # Data storage
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'stories.db')

    # Categories for positive cyber news
    CATEGORIES = [
        'Security Wins',
        'Threat Takedowns',
        'Privacy Advances',
        'Community & Education',
        'Innovation & Research',
        'Policy & Regulation',
        'Open Source & Tools',
        'People & Lives Improved',
        'Other'
    ]

    # RSS Feeds - sources that cover positive cybersecurity stories
    RSS_FEEDS = [
        # Major cybersecurity outlets (also cover takedowns, patches, wins)
        {'name': 'Krebs on Security', 'url': 'https://krebsonsecurity.com/feed/'},
        {'name': 'The Hacker News', 'url': 'https://feeds.feedburner.com/TheHackersNews'},
        {'name': 'Bleeping Computer', 'url': 'https://www.bleepingcomputer.com/feed/'},
        {'name': 'Dark Reading', 'url': 'https://www.darkreading.com/rss.xml'},
        {'name': 'SecurityWeek', 'url': 'https://www.securityweek.com/feed/'},
        # EFF - digital rights and privacy wins
        {'name': 'EFF Deeplinks', 'url': 'https://www.eff.org/rss/updates.xml'},
        # NIST - standards and frameworks
        {'name': 'NIST Cybersecurity', 'url': 'https://www.nist.gov/blogs/cybersecurity-insights/rss.xml'},
        # CISA - government defense successes
        {'name': 'CISA Alerts', 'url': 'https://www.cisa.gov/news.xml'},
        # Schneier on Security - thoughtful security commentary
        {'name': 'Schneier on Security', 'url': 'https://www.schneier.com/feed/'},
        # The Record - Recorded Future news
        {'name': 'The Record', 'url': 'https://therecord.media/feed'},
    ]


def validate_config():
    """Validate required configuration."""
    required = {
        'DISCORD_WEBHOOK_URL': Config.DISCORD_WEBHOOK_URL,
    }

    missing = [key for key, value in required.items() if not value]

    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")

    return True
