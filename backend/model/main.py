from fetch_data.yt_comments import fetch_youtube_comments
from cleaning.data_cleaning import clean_comments_df
from models.model_use import analyze_comments
from models.sentiment_summary import summarize_sentiments

def main():
    # Step 1: Fetch comments from YouTube
    video_url = "https://www.youtube.com/watch?v=mbOO0Z6ryO0"
    df = fetch_youtube_comments(video_url)
    print(f"\nFetched {len(df)} comments \n")

    # Step 2: Clean comments
    df = clean_comments_df(df)
    print("Comments cleaned and new column added \n")

    # Step 3: Analyze comments using the pre-trained model
    df = analyze_comments(df)
    print("Sentiment analysis completed and new column added \n")

    print(df[["comment", "cleaned_comment", "sentiment"]].head())
    df.to_csv('final_df.csv', index=False)

    # Step 4: Summarize sentiments
    summary = summarize_sentiments(df)
    print("\nSentiment summary:")
    for key, value in summary.items():
        print(f"{key}: {value}")    

if __name__ == "__main__":
    main()