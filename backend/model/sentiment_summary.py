import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64

def summarize_sentiments(video_id: str) -> dict:

    # Connect to database
    con = sqlite3.connect("backend/database/minor_project.db")
    
    # Fetch all comments for the given post_ID
    query = "SELECT sentiment FROM post WHERE post_ID = ?"
    df = pd.read_sql_query(query, con, params=(video_id,))
    
    # Handle case: no comments found
    if df.empty:
        return {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "total_comments": 0
        }

    # Count each sentiment type safely
    sentiment_counts = df["sentiment"].value_counts()

    # Extract values, default to 0 if not found
    positive = int(sentiment_counts.get("Positive", 0))
    negative = int(sentiment_counts.get("Negative", 0))
    neutral = int(sentiment_counts.get("Neutral", 0))
    total = int(len(df))

    # Prepare summary dictionary
    summary = {
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "total_comments": total
    }
    
    query = "SELECT * FROM post WHERE post_ID = ?"
    df = pd.read_sql_query(query, con, params=(video_id,))
    con.close()

    # Fetch negative comments
    negative_comments_df = df[df['sentiment'] == 'Negative']
    negative_comments = negative_comments_df['comment'].tolist()
    
    # Bar Chart
    sen_num_df = sentiment_counts.reset_index()
    sen_num_df.columns = ["sentiment", "count"]

    plt.figure(figsize=(5, 4))
    sns.barplot(x="sentiment", y="count", data=sen_num_df, palette="coolwarm", hue="sentiment")
    plt.title("Total Comments per Sentiment")
    plt.tight_layout()
    bar_img = io.BytesIO()
    plt.savefig(bar_img, format="png", bbox_inches="tight")
    plt.close()
    bar_img.seek(0)
    bar_base64 = base64.b64encode(bar_img.getvalue()).decode("utf-8")

    # Line Chart (comments over time)
    df["time"] = pd.to_datetime(df["time"].str.replace("Z", "+00:00"), errors="coerce")
    grouped = (
        df.groupby([pd.Grouper(key="time", freq="h"), "sentiment"])
        .size()
        .reset_index(name="count")
    )

    plt.figure(figsize=(6, 4))
    sns.lineplot(
        data=grouped,
        x="time",
        y="count",
        hue="sentiment",
        marker="o",
        palette={"Positive": "limegreen", "Neutral": "gold", "Negative": "crimson"}
    )
    plt.xticks(rotation=45)
    plt.title("Comment Activity Over Time")
    plt.tight_layout()
    line_img = io.BytesIO()
    plt.savefig(line_img, format="png", bbox_inches="tight")
    plt.close()
    line_img.seek(0)
    line_base64 = base64.b64encode(line_img.getvalue()).decode("utf-8")

    # Pie Chart
    plt.figure(figsize=(4, 4))
    plt.pie(
        sentiment_counts.values,
        labels=sentiment_counts.index,
        autopct="%1.1f%%",
        shadow=True,
        explode=[0.05] * len(sentiment_counts),
        colors=sns.color_palette("coolwarm", len(sentiment_counts))
    )
    plt.title("Sentiment Distribution")
    plt.tight_layout()
    pie_img = io.BytesIO()
    plt.savefig(pie_img, format="png", bbox_inches="tight")
    plt.close()
    pie_img.seek(0)
    pie_base64 = base64.b64encode(pie_img.getvalue()).decode("utf-8")

    # Return all data
    summary.update({
        "positive": positive,
        "negative": negative,
        "neutral": neutral,
        "total_comments": total,
        "bar_chart": bar_base64,
        "line_chart": line_base64,
        "pie_chart": pie_base64,
        "negative_comments": negative_comments
    })

    return summary
