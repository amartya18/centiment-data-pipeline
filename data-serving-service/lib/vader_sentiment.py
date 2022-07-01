from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk import download

class VaderSentiment:
    def __init__(self):
        download('vader_lexicon')
        self.analyzer = SentimentIntensityAnalyzer()
        # basic crypto lexicon
        additional_words = {
            "bullish": 2.9,
            "bearish": -2.9,
            "hodl": 2.7,
            "hodling": 2.7,
        }
        self.analyzer.lexicon.update(additional_words)

    def get_polarity(self, data):
        polarity = self.analyzer.polarity_scores(data)
        return self.convert_polarity_percentage(polarity)
    

    def convert_polarity_percentage(self, polarity):
        compound = polarity["compound"]
        percentage = (compound + 1) / 2 * 100
        return round(percentage, 1)