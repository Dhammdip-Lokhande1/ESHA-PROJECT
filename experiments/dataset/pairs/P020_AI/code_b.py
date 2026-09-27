from collections import Counter
from typing import Dict

def word_freq(text: str) -> Dict[str, int]:
    """Count word frequencies using collections.Counter."""
    return dict(Counter(text.split()))
