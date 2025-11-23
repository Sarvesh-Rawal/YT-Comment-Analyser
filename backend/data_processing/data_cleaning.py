import pandas as pd
import emoji
import re
from .hinglish_dict import hinglish_to_english
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
import nltk

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')
nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

# Read comments
# df = pd.read_csv("comments.csv", encoding='utf-8-sig')

def normalize_hinglish(text):
    text = text.lower()
    words = text.split()
    normalized_words = []
    
    for word in words:
        if word in hinglish_to_english:
            normalized_words.append(hinglish_to_english[word])
        else:
            normalized_words.append(word)
    
    return " ".join(normalized_words)

def clean_comment(comment: str) -> str:
    # Replacing mentions with <mention>
    comment = re.sub(r'@\w+', '<mention>', comment)
   
    # Replacing URLs with <link>
    comment = re.sub(r'http\S+|www\S+', '<link>', comment)
    
    # Removing hashtags symbol
    comment = re.sub(r'#', '', comment)
    
     # Converting emojis to text
    comment = emoji.demojize(comment, language='en')
    
    # Converting to lowercase
    comment = comment.lower()
    
    # Removing extra spaces
    comment = re.sub(r'\s+', ' ', comment).strip()
    
    # Normalize Hinglish words
    comment = normalize_hinglish(comment)
    
    # Tokenization
    tokens = word_tokenize(comment)

    # Removing stopwords
    filtered_tokens = []
    for w in tokens:
        if w in ["<mention>", "<link>"]:
            filtered_tokens.append(w)
        elif w not in stop_words:
            filtered_tokens.append(w)

    # Lemmatization
    processed_tokens = []
    for w in filtered_tokens:
        lemma = lemmatizer.lemmatize(w)
        processed_tokens.append(lemma)

    # Joining back into single string
    return " ".join(processed_tokens)

def clean_comments_df(df: pd.DataFrame) -> pd.DataFrame:
    df["cleaned_comment"] = df["comment"].apply(clean_comment)
    return df
