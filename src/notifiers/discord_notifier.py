"""Discord notification handler for positive cyber news via webhooks."""

import requests
import time
from typing import List, Dict, Any
from ..models import CyberGoodNews
from ..config import Config


class DiscordNotifier:
    """Send positive cybersecurity news to Discord via webhook."""

    def __init__(self):
        self.webhook_url = Config.DISCORD_WEBHOOK_URL

    async def start(self):
        pass

    async def send_story_alert(self, story: CyberGoodNews):
        """Send a single positive news story to Discord."""
        embed = self._create_story_embed(story)
        payload = {"embeds": [embed]}

        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            story.is_sent = True
            print(f"  Sent: {story.title[:60]}...")
        except Exception as e:
            print(f"Error sending to Discord: {e}")

    async def send_story_batch(self, stories: List[CyberGoodNews], max_alerts: int = 5):
        """Send top positive stories with rate limiting."""
        eligible = [s for s in stories if s.impact_score >= Config.MIN_IMPACT_SCORE]

        top_stories = sorted(
            eligible,
            key=lambda s: s.impact_score,
            reverse=True
        )[:max_alerts]

        if not top_stories:
            print("No positive stories to send (none above impact threshold)")
            return

        print(f"Sending top {len(top_stories)} positive stories (out of {len(eligible)} eligible)...")

        sent_count = 0
        for story in top_stories:
            await self.send_story_alert(story)
            sent_count += 1
            if sent_count < len(top_stories):
                time.sleep(2)

    def _create_story_embed(self, story: CyberGoodNews) -> Dict[str, Any]:
        """Create a Discord embed for a positive news story."""
        color = self._impact_to_color(story.impact_score)
        icon = self._category_icon(story.category)

        fields = [
            {
                "name": "Impact Score",
                "value": f"{story.impact_score:.1f}/10 - {self._impact_label(story.impact_score)}",
                "inline": True
            },
            {
                "name": f"{icon} Category",
                "value": story.category,
                "inline": True
            },
            {
                "name": "Source",
                "value": story.source,
                "inline": True
            }
        ]

        if story.tags:
            tags_text = ', '.join(f"`{tag}`" for tag in story.tags[:5])
            fields.append({
                "name": "Tags",
                "value": tags_text,
                "inline": False
            })

        embed = {
            "title": f"{self._impact_emoji(story.impact_score)} {story.title[:250]}",
            "description": story.summary or story.description[:500] if story.description else "No description available",
            "url": story.source_url,
            "color": color,
            "fields": fields,
            "footer": {
                "text": f"Cyber Good News | Published: {story.published_date.strftime('%Y-%m-%d %H:%M UTC')}"
            }
        }

        return embed

    def _impact_to_color(self, score: float) -> int:
        """Green-themed colors based on impact score."""
        if score >= 8.0:
            return 0x00FF00  # Bright Green - Outstanding
        elif score >= 6.0:
            return 0x2ECC71  # Emerald - High
        elif score >= 4.0:
            return 0x3498DB  # Blue - Moderate
        else:
            return 0x9B59B6  # Purple - Notable

    def _impact_label(self, score: float) -> str:
        if score >= 8.0:
            return "Outstanding"
        elif score >= 6.0:
            return "High Impact"
        elif score >= 4.0:
            return "Moderate"
        else:
            return "Notable"

    def _impact_emoji(self, score: float) -> str:
        if score >= 8.0:
            return "\U0001f31f"  # star
        elif score >= 6.0:
            return "\u2705"  # check
        elif score >= 4.0:
            return "\U0001f4a1"  # lightbulb
        else:
            return "\U0001f4f0"  # newspaper

    def _category_icon(self, category: str) -> str:
        icons = {
            'Security Wins': '\U0001f3c6',
            'Threat Takedowns': '\U0001f6a8',
            'Privacy Advances': '\U0001f512',
            'Community & Education': '\U0001f393',
            'Innovation & Research': '\U0001f52c',
            'Policy & Regulation': '\U0001f3db\ufe0f',
            'Open Source & Tools': '\U0001f527',
            'People & Lives Improved': '\u2764\ufe0f',
        }
        return icons.get(category, '\U0001f4f0')

    async def close(self):
        pass
