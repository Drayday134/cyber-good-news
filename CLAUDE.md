# Cyber Good News

Positive cybersecurity news aggregator with Discord alerts. Runs as a systemd service. Same architecture as threat-intel-aggregator but scores for positive impact instead of threat severity.

## Quick Reference

- **Service**: `sudo systemctl status cyber-good-news` / `restart` / `stop`
- **Logs**: `journalctl -u cyber-good-news -n 50` or `./logs/service.log`
- **Test run**: `source venv/bin/activate && python app.py --test`
- **DB**: `./data/` (SQLite)
- **Config**: `.env`

## Architecture

```
app.py (entry point, CyberGoodNews orchestrator)
  -> src/collectors/   (RSSCollector)
  -> src/processors/   (PositiveScorer - scores stories for positive impact)
  -> src/notifiers/    (DiscordNotifier)
  -> src/database.py   (StoryDatabase - SQLite dedup)
  -> src/config.py     (reads .env)
  -> src/models.py     (Story dataclass)
```

## Key .env Settings

- `DISCORD_WEBHOOK_URL` - required (same webhook as threat-intel)
- `MIN_IMPACT_SCORE=5`
- `MAX_ALERTS_PER_HOUR=5`
- `COLLECTION_INTERVAL_MINUTES=60`

## Don't Touch

- `.env` (live Discord webhook)
- `data/` while service is running
