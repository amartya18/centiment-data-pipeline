import re
import nltk
import pickle

class TweetPreprocess:
    def __init__(self):
        # required
        nltk.download("wordnet")
        nltk.download("omw-1.4")
        nltk.download("words")

        self.lemmatizer = nltk.stem.WordNetLemmatizer()
        self.tokenizer = nltk.tokenize.TweetTokenizer()
        self.detokenizer = nltk.tokenize.treebank.TreebankWordDetokenizer()

        words = nltk.corpus.words
        self.word_set = set(words.words())

        self.stop_words = ["the", "with", "in", "a", "is"]

    def lemmatize_text(self, text):
        return [(self.lemmatizer.lemmatize(w)) for w in self.tokenizer.tokenize((text))]

    def get_hashtag_text(self, word):
        #if not a hahstag return the word
        if (not word.startswith("#")):
            return word
        
        word = word[1:] # remove hashtag
        return word if (word in self.word_set) else ""

    def remove_hashtag_text(self, tokens):
        cleaned_tokens = []
        for word in tokens:
            cleaned_word = self.get_hashtag_text(word)
            if cleaned_word != "":
                cleaned_tokens.append(cleaned_word)

        return cleaned_tokens

    def remove_stop_words(self, tokens):
        return [word for word in tokens if word not in self.stop_words] 

    # replace username mentions e.g. '@elonmusk' to 'USER'
    def replace_user_mentions(self, tokens):
        for i, word in enumerate(tokens):
            if (word.startswith("@")):
                tokens[i] = "USER"

        return tokens

    def remove_punctuation(self, tokens):
        cleaned_tokens = []
        for word in tokens:
            cleaned_word = re.sub(r'[^\w\s]', '', (word))
            if cleaned_word != '':
                cleaned_tokens.append(cleaned_word)

        return cleaned_tokens

    def tokens_detokenizer(self, tokens):
        return self.detokenizer.detokenize(tokens)

    def process_data(self, data):
        tokens = self.lemmatize_text(data)
        tokens = self.remove_hashtag_text(tokens)
        tokens = self.remove_stop_words(tokens)
        tokens = self.replace_user_mentions(tokens)
        tokens = self.remove_punctuation(tokens)
        result = self.tokens_detokenizer(tokens)

        return result
