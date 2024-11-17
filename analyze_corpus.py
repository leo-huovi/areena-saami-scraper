import re
from collections import Counter
from typing import List, Dict, Tuple
import numpy as np
from langdetect import detect
import pandas as pd

class CorpusAnalyzer:
    def __init__(self, text: str):
        self.raw_text = text
        self.sentences = self._split_into_sentences()
        self.words = self._tokenize()

    def _split_into_sentences(self) -> List[str]:
        """Split text into sentences based on punctuation marks."""
        # Basic sentence splitting - can be improved with more sophisticated rules
        sentences = re.split(r'[.!?]+', self.raw_text)
        # Remove empty sentences and strip whitespace
        return [s.strip() for s in sentences if s.strip()]

    def _tokenize(self) -> List[str]:
        """Tokenize text into words."""
        # Split on whitespace and punctuation, lowercase all words
        words = re.findall(r'\b\w+\b', self.raw_text.lower())
        return words

    def basic_stats(self) -> Dict:
        """Calculate basic corpus statistics."""
        # Count total words, unique words, and sentences
        total_words = len(self.words)
        unique_words = len(set(self.words))
        total_sentences = len(self.sentences)

        # Calculate average sentence length
        sentence_lengths = [len(re.findall(r'\b\w+\b', s)) for s in self.sentences]
        avg_sentence_length = np.mean(sentence_lengths)
        median_sentence_length = np.median(sentence_lengths)

        # Calculate type-token ratio
        ttr = unique_words / total_words if total_words > 0 else 0

        return {
            "total_words": total_words,
            "unique_words": unique_words,
            "total_sentences": total_sentences,
            "average_sentence_length": round(avg_sentence_length, 2),
            "median_sentence_length": round(median_sentence_length, 2),
            "type_token_ratio": round(ttr, 4),
            "sentence_length_std": round(np.std(sentence_lengths), 2)
        }

    def word_frequency(self, top_n: int = 20) -> List[Tuple[str, int]]:
        """Calculate word frequencies."""
        return Counter(self.words).most_common(top_n)

    def sentence_length_distribution(self) -> Dict[int, int]:
        """Calculate distribution of sentence lengths."""
        lengths = [len(re.findall(r'\b\w+\b', s)) for s in self.sentences]
        return dict(Counter(lengths))

    def detect_languages(self) -> Dict[str, int]:
        """Attempt to detect languages in the corpus."""
        language_counts = Counter()

        # Try to detect language for each sentence
        for sentence in self.sentences:
            try:
                lang = detect(sentence)
                language_counts[lang] += 1
            except:
                language_counts['unknown'] += 1

        return dict(language_counts)

    def generate_report(self) -> str:
        """Generate a formatted report of corpus statistics."""
        stats = self.basic_stats()
        freq = self.word_frequency(10)
        length_dist = self.sentence_length_distribution()

        report = [
            "=== Sami Corpus Analysis Report ===\n",
            "\n=== Basic Statistics ===",
            f"Total Words: {stats['total_words']}",
            f"Unique Words: {stats['unique_words']}",
            f"Total Sentences: {stats['total_sentences']}",
            f"Average Sentence Length: {stats['average_sentence_length']} words",
            f"Median Sentence Length: {stats['median_sentence_length']} words",
            f"Type-Token Ratio: {stats['type_token_ratio']}",
            f"Sentence Length Std Dev: {stats['sentence_length_std']}",

            "\n=== Top 10 Most Frequent Words ===",
            *[f"{word}: {count}" for word, count in freq],

            "\n=== Sentence Length Distribution ===",
            *[f"{length} words: {count} sentences"
              for length, count in sorted(length_dist.items())]
        ]

        return "\n".join(report)

# Example usage
def analyze_corpus(text_content: str):
    analyzer = CorpusAnalyzer(text_content)
    print(analyzer.generate_report())

    # Additional analysis: create visualizations using pandas
    stats = analyzer.basic_stats()
    length_dist = analyzer.sentence_length_distribution()

    # Convert sentence length distribution to DataFrame for easier analysis
    df_lengths = pd.DataFrame.from_dict(length_dist,
                                      orient='index',
                                      columns=['count'])

    print("\nSentence Length Statistics:")
    print(df_lengths.describe())

    return analyzer

# Main execution
if __name__ == "__main__":
    # Sample usage with a text file
    with open("combined_subtitles.txt", "r", encoding="utf-8") as f:
        corpus_text = f.read()

    analyzer = analyze_corpus(corpus_text)
