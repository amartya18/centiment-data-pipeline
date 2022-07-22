from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import download

class VaderSentiment:
    def __init__(self):
        download('vader_lexicon')
        self.analyzer = SentimentIntensityAnalyzer()
        # basic crypto lexicon
        additional_words = {
            "bullish": 2.9,
            "bull":2.5,
            "bear":-2.5,
            "bearish": -2.9,
            "hodl": 2.7,
            "hodling": 2.7,
            "sell":-1,
            "buy":1,
            "mooning":2,
            "moon":2,
            "rocket":1.5,
            "correction":-1,
            "distribution":-2,
            "accumulation":2,
            "pump":2,
            "dump":-2,
            "fraud":-3,
            "future":1,
            "scam":-2,
            "hold":2.7,
            "discount":1,
            "long":2,
            "short":-2,
            "fomo":-1,
            "fud":-1,
            "ath":1.5,
        }
        self.analyzer.lexicon.update(additional_words)

    def get_polarity(self, data):
        polarity = self.analyzer.polarity_scores(data)
        return self.convert_polarity_percentage(polarity)
    

    def convert_polarity_percentage(self, polarity):
        compound = polarity["compound"]
        percentage = (compound + 1) / 2 * 100
        return round(percentage, 1)