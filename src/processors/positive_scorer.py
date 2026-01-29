"""Rule-based processor that scores stories for positive cybersecurity impact."""

import re
import yaml
import os
from typing import List, Tuple
from ..models import CyberGoodNews
from ..config import Config


class PositiveScorer:
    """Score and filter news stories for positive cybersecurity impact."""

    def __init__(self, scoring_file: str = None):
        if scoring_file is None:
            scoring_file = os.path.join(
                os.path.dirname(__file__), '..', '..', 'config', 'positive_scoring.yaml'
            )
        self.scoring_file = scoring_file
        self.rules = self._load_scoring_rules()

    def _load_scoring_rules(self) -> dict:
        try:
            with open(self.scoring_file, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load scoring rules: {e}")
            return self._get_default_rules()

    def _get_default_rules(self) -> dict:
        return {
            'positive_categories': {
                'Security Wins': {
                    'keywords': ['arrested', 'takedown', 'dismantled', 'seized'],
                    'base_score': 7.0
                },
                'Innovation & Research': {
                    'keywords': ['new tool', 'open source', 'research'],
                    'base_score': 6.0
                }
            }
        }

    def process_stories(self, stories: List[CyberGoodNews]) -> List[CyberGoodNews]:
        """Process stories: categorize, score, and filter to only positive ones."""
        processed = []

        for story in stories:
            try:
                if not story.is_processed:
                    self._analyze_story(story)
                    story.is_processed = True

                # Only keep stories that score positively
                if story.impact_score >= Config.MIN_IMPACT_SCORE:
                    processed.append(story)

            except Exception as e:
                print(f"Error processing story {story.id}: {e}")

        return processed

    def _analyze_story(self, story: CyberGoodNews):
        """Analyze a single story for positive impact."""
        text = f"{story.title} {story.description}".lower()

        title_text = story.title.lower()

        # Count positive signals - require at least one in the TITLE
        positive_signals = self.rules.get('positive_signals', {}).get('keywords', [])
        title_pos = sum(1 for kw in positive_signals if kw.lower() in title_text)
        body_pos = sum(1 for kw in positive_signals if kw.lower() in text)

        # Count negative indicators in title
        negative_keywords = self.rules.get('negative_indicators', {}).get('keywords', [])
        title_neg = sum(1 for kw in negative_keywords if kw.lower() in title_text)
        neg_count = sum(1 for kw in negative_keywords if kw.lower() in text)

        # Must have at least 1 positive signal in the title
        if title_pos == 0:
            story.impact_score = 0.0
            story.category = 'Neutral'
            return

        # If title has more negative than positive indicators, skip
        if title_neg > title_pos:
            story.impact_score = 0.0
            story.category = 'Negative'
            return

        # Categorize into positive categories
        category, base_score = self._categorize(text)
        story.category = category
        story.impact_score = self._calculate_impact(text, base_score)

        # Penalize stories that still have negative indicators
        if neg_count > 0:
            story.impact_score -= neg_count * 0.5

        story.impact_score = min(10.0, max(0.0, story.impact_score))
        story.tags = self._extract_tags(text)
        story.summary = self._generate_summary(story)

    def _is_purely_negative(self, text: str) -> bool:
        """Check if a story is purely about bad news with no positive angle."""
        negative_only = self.rules.get('negative_indicators', {})
        negative_keywords = negative_only.get('keywords', [])
        positive_signals = self.rules.get('positive_signals', {}).get('keywords', [])

        neg_count = sum(1 for kw in negative_keywords if kw.lower() in text)
        pos_count = sum(1 for kw in positive_signals if kw.lower() in text)

        # If heavily negative and no positive signals, it's purely negative
        return neg_count >= 2 and pos_count == 0

    def _categorize(self, text: str) -> Tuple[str, float]:
        """Categorize story into positive categories."""
        categories = self.rules.get('positive_categories', {})

        best_match = None
        best_score = 0
        best_base = 3.0

        for cat_name, cat_data in categories.items():
            keywords = cat_data.get('keywords', [])
            matches = sum(1 for kw in keywords if kw.lower() in text)
            if matches > best_score:
                best_score = matches
                best_match = cat_name
                best_base = cat_data.get('base_score', 5.0)

        if best_match is None:
            return 'Other', 3.0

        return best_match, best_base

    def _calculate_impact(self, text: str, base_score: float) -> float:
        """Calculate positive impact score with modifiers."""
        score = base_score

        # Apply positive modifiers
        modifiers = self.rules.get('impact_modifiers', {})
        for mod_name, mod_data in modifiers.items():
            keywords = mod_data.get('keywords', [])
            modifier = mod_data.get('modifier', 0.0)
            if any(kw.lower() in text for kw in keywords):
                score += modifier

        return score

    def _extract_tags(self, text: str) -> List[str]:
        """Extract relevant tags."""
        tags = set(['cyber-good-news', 'security-positive'])

        categories = self.rules.get('positive_categories', {})
        for cat_name, cat_data in categories.items():
            for kw in cat_data.get('keywords', []):
                if kw.lower() in text:
                    tags.add(kw)
                    if len(tags) >= 8:
                        return list(tags)[:8]

        return list(tags)[:8]

    def _generate_summary(self, story: CyberGoodNews) -> str:
        """Generate a brief summary."""
        if len(story.description) <= 200:
            return story.description

        label = self._get_impact_label(story.impact_score)
        summary = f"{label} impact story in '{story.category}'. "
        summary += f"Source: {story.source}. "

        if story.description:
            first_sentence = story.description.split('.')[0][:150]
            summary += f"{first_sentence}."

        return summary

    def _get_impact_label(self, score: float) -> str:
        if score >= 8.0:
            return "Outstanding"
        elif score >= 6.0:
            return "High"
        elif score >= 4.0:
            return "Moderate"
        else:
            return "Notable"

    def reload_rules(self):
        self.rules = self._load_scoring_rules()
        print("Scoring rules reloaded")
