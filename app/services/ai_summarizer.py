import logging
import re
from typing import List, Optional

import nltk
from nltk.tokenize import sent_tokenize

logger = logging.getLogger(__name__)

# Download required NLTK data (would be done at setup time)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)


class AISummarizer:
    """Service for generating AI-powered summaries of webpage content."""

    def generate_summary(
        self,
        text_content: str,
        max_sentences: int = 3,
        max_length: int = 200
    ) -> Optional[str]:
        """
        Generate a summary of webpage content using extractive summarization.

        Args:
            text_content: The text content to summarize
            max_sentences: Maximum number of sentences in summary
            max_length: Maximum length of summary in characters

        Returns:
            Summary text or None if unable to generate
        """
        try:
            if not text_content or len(text_content.strip()) < 100:
                return None

            # Tokenize into sentences
            sentences = sent_tokenize(text_content)

            if len(sentences) < 2:
                # If only one sentence, return a truncated version
                return text_content.strip()[:max_length].strip()

            # Score sentences based on various heuristics
            scored_sentences = []
            for i, sentence in enumerate(sentences):
                score = self._score_sentence(sentence, i, len(sentences))
                scored_sentences.append((score, sentence))

            # Sort by score (highest first)
            scored_sentences.sort(key=lambda x: x[0], reverse=True)

            # Select top sentences
            selected_sentences = []
            total_length = 0

            for score, sentence in scored_sentences:
                if len(selected_sentences) >= max_sentences:
                    break

                # Check if adding this sentence would exceed max length
                if total_length + len(sentence) > max_length and selected_sentences:
                    break

                selected_sentences.append(sentence)
                total_length += len(sentence)

            # Sort selected sentences by original order
            # This is a simplified approach - in practice, we'd need to track original positions
            summary = ' '.join(selected_sentences[:max_sentences])

            return summary.strip()

        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return None

    def _score_sentence(self, sentence: str, position: int, total_sentences: int) -> float:
        """
        Score a sentence based on various heuristics.

        Args:
            sentence: The sentence to score
            position: Position in the document (0-based)
            total_sentences: Total number of sentences

        Returns:
            Score (higher is better)
        """
        score = 0.0
        sentence_lower = sentence.lower()

        # Length score (prefer medium-length sentences)
        word_count = len(sentence.split())
        if 10 <= word_count <= 30:
            score += 2.0
        elif word_count < 5:
            score -= 1.0

        # Position score (prefer sentences near the beginning)
        if position < total_sentences * 0.3:  # Top 30%
            score += 1.5
        elif position > total_sentences * 0.7:  # Bottom 30%
            score -= 0.5

        # Keyword score (sentences with important words)
        important_words = [
            'company', 'business', 'provides', 'offers', 'services', 'products',
            'leading', 'innovative', 'technology', 'solutions', 'platform',
            'customers', 'users', 'mission', 'vision', 'about', 'contact'
        ]

        for word in important_words:
            if word in sentence_lower:
                score += 0.5

        # Capitalization score (prefer sentences starting with capital letters after punctuation)
        if re.match(r'^[A-Z]', sentence.strip()):
            score += 0.3

        # Numeric content score (sentences with numbers might be important)
        if re.search(r'\d', sentence):
            score += 0.2

        return score


# Global instance
ai_summarizer = AISummarizer()