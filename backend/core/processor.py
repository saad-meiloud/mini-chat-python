import re
import unicodedata
import nltk

# Ensurepunkt and stopwords are downloaded (or handle in startup)
# nltk.download('punkt') # Consider doing this in main app startup to avoid reloading

class TextProcessor:
    def __init__(self):
        pass

    def normalize(self, text: str) -> str:
        """
        Converts text to lowercase, removes accents, punctuation, and extra spaces.
        """
        # Convert to lowercase
        text = text.lower()

        # Remove accents
        text = unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode('utf-8')

        # Remove punctuation (keep only alphanumeric and spaces)
        text = re.sub(r'[^\w\s]', '', text)

        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def tokenize(self, text: str) -> list[str]:
        """
        Splits text into tokens.
        """
        # Simple tokenization by splitting on space if NLTK is too heavy for simple requirement
        # But using nltk is better for robustness
        # return nltk.word_tokenize(text)
        return text.split()

processor = TextProcessor()
