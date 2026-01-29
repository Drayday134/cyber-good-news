"""Main application - Cyber Good News: Positive cybersecurity stories for Discord."""

import asyncio
import sys
from datetime import datetime
from src.config import Config, validate_config
from src.collectors import RSSCollector
from src.processors import PositiveScorer
from src.notifiers import DiscordNotifier
from src.database import StoryDatabase


class CyberGoodNews:
    """Main application orchestrator."""

    def __init__(self):
        self.db = StoryDatabase()
        self.processor = PositiveScorer()
        self.notifier = DiscordNotifier()
        self.collectors = []
        self._init_collectors()

    def _init_collectors(self):
        rss = RSSCollector()
        if rss.is_available():
            self.collectors.append(rss)

    async def collect_and_alert(self):
        """Collect stories, score them, and send positive ones to Discord."""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Starting collection cycle...")

        total_collected = 0
        new_stories = 0

        for collector in self.collectors:
            print(f"\nCollecting from {collector.name}...")
            try:
                stories = collector.collect()
                total_collected += len(stories)

                if stories:
                    print(f"Scoring {len(stories)} stories for positive impact...")
                    positive_stories = self.processor.process_stories(stories)

                    new_count = self.db.save_stories(positive_stories)
                    new_stories += new_count

                    if new_count > 0:
                        print(f"{new_count} new positive stories saved")

                        unsent = [s for s in positive_stories
                                 if not s.is_sent and s.impact_score >= Config.MIN_IMPACT_SCORE]

                        if unsent:
                            await self.notifier.send_story_batch(unsent, max_alerts=Config.MAX_ALERTS_PER_HOUR)

                            for story in unsent:
                                if story.is_sent:
                                    self.db.mark_as_sent(story.id)
                    else:
                        print("No new positive stories (all duplicates)")

            except Exception as e:
                print(f"Error collecting from {collector.name}: {e}")

        print(f"\n{'='*60}")
        print(f"Collection cycle complete")
        print(f"  Total items scanned: {total_collected}")
        print(f"  New positive stories: {new_stories}")

        stats = self.db.get_stats()
        print(f"\nDatabase Stats:")
        print(f"  Total stories: {stats['total_stories']}")
        print(f"  Sent to Discord: {stats['sent_alerts']}")
        print(f"  Pending: {stats['pending_alerts']}")
        print(f"  Avg impact score: {stats['avg_impact']}/10")
        print(f"{'='*60}\n")

    async def run_continuous(self):
        """Run continuous monitoring."""
        print("Starting Cyber Good News Feed")
        print(f"Collection interval: {Config.COLLECTION_INTERVAL_MINUTES} minutes")
        print(f"Impact threshold: {Config.MIN_IMPACT_SCORE}/10")
        print(f"Active collectors: {len(self.collectors)}")
        for collector in self.collectors:
            print(f"   - {collector.name}")
        print()

        discord_task = asyncio.create_task(self.notifier.start())
        await asyncio.sleep(3)

        try:
            while True:
                await self.collect_and_alert()
                interval_seconds = Config.COLLECTION_INTERVAL_MINUTES * 60
                print(f"Sleeping for {Config.COLLECTION_INTERVAL_MINUTES} minutes...")
                await asyncio.sleep(interval_seconds)

        except KeyboardInterrupt:
            print("\n\nShutting down...")
            await self.notifier.close()
            discord_task.cancel()

    async def run_once(self):
        """Run a single collection cycle (for testing)."""
        print("Running single collection cycle (test mode)\n")

        discord_task = asyncio.create_task(self.notifier.start())
        await asyncio.sleep(3)

        await self.collect_and_alert()

        await self.notifier.close()
        discord_task.cancel()

        print("\nTest complete!")


async def main():
    print("=" * 60)
    print("      Cyber Good News Feed")
    print("  Positive cybersecurity stories for Discord")
    print("=" * 60)
    print()

    try:
        validate_config()
        print("Configuration validated\n")
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nSetup required:")
        print("   1. Copy .env.example to .env")
        print("   2. Add your DISCORD_WEBHOOK_URL")
        print()
        sys.exit(1)

    app = CyberGoodNews()

    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        await app.run_once()
    else:
        await app.run_continuous()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
