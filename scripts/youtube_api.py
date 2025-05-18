"""
app.py

Streamlit dashboard for displaying YouTube trending sentiment analysis:
- Region and sentiment filtering
- Pie charts and word clouds
- Global and regional views
- CSV export of filtered results
"""

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
from deep_translator import GoogleTranslator

# Streamlit page setup
st.set_page_config(page_title="YouTube Sentiment Dashboard", layout="wide")
st.title("📊 YouTube Trending Sentiment Dashboard")

# --- Load comment sentiment results ---
def load_comments():
    path = Path(__file__).resolve().parent / "comment_sentiment.json"
    if not path.exists():
        return pd.DataFrame()
    with open(path, "r", encoding="utf-8") as f:
        return pd.DataFrame([json.loads(line) for line in f])

# --- Load video metadata ---
def load_metadata():
    path = Path(__file__).resolve().parent / "video_metadata.json"
    if not path.exists():
        return pd.DataFrame()
    with open(path, "r", encoding="utf-8") as f:
        return pd.DataFrame([json.loads(line) for line in f])

df_comments = load_comments()
df_meta = load_metadata()

# If no data, warn user
if df_comments.empty or df_meta.empty:
    st.warning("⚠️ No data found. Please run the producer and sentiment processor.")
    st.stop()

# === GLOBAL SENTIMENT OVERVIEW ===
st.header("🌍 Global Sentiment Overview")

# Count total sentiments across all comments
sentiment_counts = df_comments["sentiment"].value_counts().to_dict()
total = sentiment_counts.get("POSITIVE", 0) + sentiment_counts.get("NEGATIVE", 0)

# Show summary metrics
col1, col2, col3 = st.columns(3)
col1.metric("✅ Positive", sentiment_counts.get("POSITIVE", 0))
col2.metric("⚠️ Negative", sentiment_counts.get("NEGATIVE", 0))
col3.metric("🧮 Total Comments", total)

# Global pie chart
global_pie = pd.DataFrame({
    "Sentiment": ["Positive", "Negative"],
    "Count": [
        sentiment_counts.get("POSITIVE", 0),
        sentiment_counts.get("NEGATIVE", 0)
    ]
})
fig_global = px.pie(
    global_pie,
    names='Sentiment',
    values='Count',
    title="🌐 Global Sentiment Distribution",
    color='Sentiment',
    color_discrete_map={'Positive': 'green', 'Negative': 'red'}
)
st.plotly_chart(fig_global, key="global-pie")

# === SENTIMENT BY REGION (Bar Chart) ===
st.subheader("📊 Sentiment Volume by Region")

# Group sentiments per region
region_sentiment = df_comments.groupby(["region", "sentiment"]).size().unstack(fill_value=0).reset_index()
region_sentiment["Total"] = region_sentiment["POSITIVE"] + region_sentiment["NEGATIVE"]

# Display bar chart
bar_fig = px.bar(
    region_sentiment.sort_values("Total", ascending=False),
    x="region",
    y=["POSITIVE", "NEGATIVE"],
    title="Total Comments by Region and Sentiment",
    labels={"value": "Comment Count", "region": "Region", "variable": "Sentiment"},
    color_discrete_map={"POSITIVE": "green", "NEGATIVE": "red"}
)
st.plotly_chart(bar_fig, use_container_width=True)

# === REGION-BASED VIDEO DISPLAY ===
st.header("📍 Regional Sentiment Viewer")

# Select region and sentiment filters
region = st.selectbox("Choose a region:", sorted(df_meta["region"].dropna().unique()))
filter_sentiment = st.selectbox("Filter videos by sentiment:", ["All", "Positive only", "Negative only"])
search_query = st.text_input("🔎 Search video titles (optional):").lower()

# Filter metadata and comments for selected region
meta_region = df_meta[df_meta["region"] == region]
comments_region = df_comments[df_comments["region"] == region]

# Summarize sentiment by video
sentiment_summary = (
    comments_region.groupby(["video_id", "sentiment"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

# Merge video metadata with comment sentiment
merged = meta_region.merge(sentiment_summary, on="video_id", how="left").fillna(0)

# Apply sentiment filters
if filter_sentiment == "Positive only":
    merged = merged[merged["POSITIVE"] > merged["NEGATIVE"]]
elif filter_sentiment == "Negative only":
    merged = merged[merged["NEGATIVE"] > merged["POSITIVE"]]

# Apply search filter
if search_query:
    merged = merged[merged["title"].str.lower().str.contains(search_query)]

# If empty, stop and notify
if merged.empty:
    st.info("ℹ️ No videos with matching sentiment data for this region.")
    st.stop()

# === EXPORT CSV BUTTON ===
csv = merged.to_csv(index=False).encode("utf-8")
st.download_button(
    label="💾 Download Regional Sentiment Data as CSV",
    data=csv,
    file_name=f"{region.lower()}_sentiment.csv",
    mime="text/csv"
)

# === DISPLAY VIDEOS + CHARTS ===
for idx, row in merged.iterrows():
    st.subheader(row["title"])
    video_id = row["video_id"]
    pos = int(row.get("POSITIVE", 0))
    neg = int(row.get("NEGATIVE", 0))
    total = pos + neg

    st.markdown(f"**✅ Positive:** {pos}  **⚠️ Negative:** {neg}  **🗣 Total:** {total}")
    st.markdown(f"[▶ Watch on YouTube]({row['video_url']})")

    # Per-video pie chart
    if total > 0:
        pie_df = pd.DataFrame({
            "Sentiment": ["Positive", "Negative"],
            "Count": [pos, neg]
        })
        fig = px.pie(
            pie_df,
            names='Sentiment',
            values='Count',
            title='Sentiment Distribution',
            color='Sentiment',
            color_discrete_map={'Positive': 'green', 'Negative': 'red'}
        )
        st.plotly_chart(fig, key=f"pie-{idx}")

    # Word cloud of translated comment text
    video_comments = comments_region[comments_region["video_id"] == video_id]
    all_text = " ".join(video_comments["text"].dropna().astype(str).tolist())

    if all_text.strip():
        try:
            # Translate all comments to English
            translated_text = GoogleTranslator(source='auto', target='en').translate(all_text)
        except Exception as e:
            translated_text = all_text
            st.warning(f"Translation failed: {e}")

        # Generate and render word cloud
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(translated_text)
        fig, ax = plt.subplots()
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig, clear_figure=True)

    st.markdown("---")
