from flask import Flask, render_template, request, jsonify
from backend.scrapper.yt_comments import fetch_youtube_comments
from backend.data_processing.data_cleaning import clean_comments_df
from backend.model.model_use import analyze_comments
from backend.database.store_data import update_database
from backend.model.sentiment_summary import summarize_sentiments

# Initialize Flask app
app = Flask(__name__)

# renders index.html 
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze_video', methods=['POST'])
def analyze_video():
    """Handle YouTube sentiment analysis."""
    try:
        # Get video URL from form input
        data=request.get_json()
        print(data)
        video_url = data.get('video_url')
        print(video_url)
        if not video_url:
            return jsonify({"error": "No video URL provided"}), 400
        
        # Step 1: Fetch comments from YouTube
        df, uplaod_date, video_title, video_id = fetch_youtube_comments(video_url)
        print(f"\nFetched {len(df)} comments \n")
        
        # Step 2: Clean comments
        df = clean_comments_df(df)
        print("Comments cleaned and new column added \n")

        # Step 3: Analyze comments using the pre-trained model
        df = analyze_comments(df)
        print("Sentiment analysis completed and new column added \n")
        # print(df.head())

        #Saving data to database
        db_response = update_database(df, video_id, video_title, uplaod_date)
        print(db_response)

        # Step 4: Summarize sentiments
        summary = summarize_sentiments(video_id)
        print("\nSentiment summary sent to frontend \n")
        

        # Return a valid JSON response always
        return jsonify({
            "upload_date": uplaod_date,
            "video_title": video_title,
            "summary": summary
        }), 200


    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)
