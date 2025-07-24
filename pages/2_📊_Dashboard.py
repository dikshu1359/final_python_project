import streamlit as st
import sqlite3
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Dashboard - Face Emotion Detection",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dashboard
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .dashboard-header {
        text-align: center;
        padding: 20px 0;
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        margin-bottom: 30px;
    }
    
    .emotion-stat {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        margin: 5px;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #2C3E50, #34495E);
    }
    
    .stSelectbox > div > div {
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<link rel="stylesheet" href="/styles/style1.css">', unsafe_allow_html=True)
st.markdown('<div class="background-container"><div class="background-image"></div></div>', unsafe_allow_html=True)

def load_user_data():
    """Load user data from database"""
    try:
        conn = sqlite3.connect('data/users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        conn.close()
        return total_users
    except:
        return 0

def load_emotions_data():
    """Load emotions data from JSON file"""
    try:
        with open('data/emotions_data.json', 'r') as f:
            data = json.load(f)
        return data
    except:
        # Return sample data if file doesn't exist
        return {
            "sessions": [
                {
                    "date": "2024-07-24",
                    "emotions": {"Happy": 45, "Sad": 12, "Angry": 8, "Surprise": 15, "Fear": 5, "Disgust": 3, "Neutral": 35},
                    "session_type": "real_time"
                },
                {
                    "date": "2024-07-23", 
                    "emotions": {"Happy": 38, "Sad": 18, "Angry": 12, "Surprise": 10, "Fear": 8, "Disgust": 4, "Neutral": 42},
                    "session_type": "image_upload"
                }
            ]
        }

def create_emotion_pie_chart(emotions_data):
    """Create pie chart for emotion distribution"""
    if not emotions_data["sessions"]:
        return None
    
    # Aggregate all emotions
    total_emotions = {}
    for session in emotions_data["sessions"]:
        for emotion, count in session["emotions"].items():
            total_emotions[emotion] = total_emotions.get(emotion, 0) + count
    
    fig = px.pie(
        values=list(total_emotions.values()),
        names=list(total_emotions.keys()),
        title="Overall Emotion Distribution",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_size=20,
        title_x=0.5
    )
    
    return fig

def create_emotion_bar_chart(emotions_data):
    """Create bar chart for emotion trends"""
    if not emotions_data["sessions"]:
        return None
    
    # Prepare data for bar chart
    dates = []
    emotions_list = []
    counts = []
    
    for session in emotions_data["sessions"]:
        date = session["date"]
        for emotion, count in session["emotions"].items():
            dates.append(date)
            emotions_list.append(emotion)
            counts.append(count)
    
    df = pd.DataFrame({
        'Date': dates,
        'Emotion': emotions_list,
        'Count': counts
    })
    
    fig = px.bar(
        df, 
        x='Date', 
        y='Count', 
        color='Emotion',
        title="Emotion Detection Over Time",
        barmode='group'
    )
    
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_size=20,
        title_x=0.5
    )
    
    return fig

def create_emotion_line_chart(emotions_data):
    """Create line chart for emotion trends"""
    if not emotions_data["sessions"]:
        return None
    
    # Prepare data for line chart
    dates = []
    happy_counts = []
    sad_counts = []
    angry_counts = []
    
    for session in emotions_data["sessions"]:
        dates.append(session["date"])
        happy_counts.append(session["emotions"].get("Happy", 0))
        sad_counts.append(session["emotions"].get("Sad", 0))
        angry_counts.append(session["emotions"].get("Angry", 0))
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(x=dates, y=happy_counts, mode='lines+markers', name='Happy', line=dict(color='#FFD700')))
    fig.add_trace(go.Scatter(x=dates, y=sad_counts, mode='lines+markers', name='Sad', line=dict(color='#4169E1')))
    fig.add_trace(go.Scatter(x=dates, y=angry_counts, mode='lines+markers', name='Angry', line=dict(color='#FF6347')))
    
    fig.update_layout(
        title="Primary Emotions Trend",
        xaxis_title="Date",
        yaxis_title="Detection Count",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font_color='white',
        title_font_size=20,
        title_x=0.5
    )
    
    return fig

def main():
    # Check if user is logged in
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        st.error("🔒 Please login first!")
        st.stop()
    
    # Dashboard Header
    st.sidebar.image('assets/images/logo.png', width=80)
    st.sidebar.markdown('<h2 style="text-align:center; color:#667eea; margin-bottom:1rem;">EmotiVision</h2>', unsafe_allow_html=True)
    st.markdown('<div class="app-header fade-in"><h1>Dashboard</h1><p>See your emotion analytics and trends at a glance.</p></div>', unsafe_allow_html=True)
    
    # Load data
    total_users = load_user_data()
    emotions_data = load_emotions_data()
    
    # Sidebar filters
    st.sidebar.title("📊 Dashboard Controls")
    
    # Date range selector
    date_range = st.sidebar.selectbox(
        "Select Time Range",
        ["Last 7 Days", "Last 30 Days", "All Time"]
    )
    
    # Chart type selector
    chart_type = st.sidebar.selectbox(
        "Select Visualization",
        ["Overview", "Pie Chart", "Bar Chart", "Line Chart", "All Charts"]
    )
    
    # Main dashboard content
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate total sessions and emotions
    total_sessions = len(emotions_data["sessions"])
    total_detections = sum(sum(session["emotions"].values()) for session in emotions_data["sessions"])
    
    # Most detected emotion
    all_emotions = {}
    for session in emotions_data["sessions"]:
        for emotion, count in session["emotions"].items():
            all_emotions[emotion] = all_emotions.get(emotion, 0) + count
    
    most_detected = max(all_emotions, key=all_emotions.get) if all_emotions else "None"
    
    # Metrics cards
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>👥 Total Users</h3>
            <h2>{}</h2>
        </div>
        """.format(total_users), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📸 Sessions</h3>
            <h2>{}</h2>
        </div>
        """.format(total_sessions), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Total Detections</h3>
            <h2>{}</h2>
        </div>
        """.format(total_detections), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>😊 Top Emotion</h3>
            <h2>{}</h2>
        </div>
        """.format(most_detected), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts section
    if chart_type == "Overview" or chart_type == "All Charts":
        col1, col2 = st.columns(2)
        
        with col1:
            pie_fig = create_emotion_pie_chart(emotions_data)
            if pie_fig:
                st.plotly_chart(pie_fig, use_container_width=True)
        
        with col2:
            line_fig = create_emotion_line_chart(emotions_data)
            if line_fig:
                st.plotly_chart(line_fig, use_container_width=True)
    
    if chart_type == "Pie Chart" or chart_type == "All Charts":
        pie_fig = create_emotion_pie_chart(emotions_data)
        if pie_fig:
            st.plotly_chart(pie_fig, use_container_width=True)
    
    if chart_type == "Bar Chart" or chart_type == "All Charts":
        bar_fig = create_emotion_bar_chart(emotions_data)
        if bar_fig:
            st.plotly_chart(bar_fig, use_container_width=True)
    
    if chart_type == "Line Chart" or chart_type == "All Charts":
        line_fig = create_emotion_line_chart(emotions_data)
        if line_fig:
            st.plotly_chart(line_fig, use_container_width=True)
    
    # Recent sessions table
    st.subheader("📋 Recent Detection Sessions")
    
    if emotions_data["sessions"]:
        sessions_df = pd.DataFrame([
            {
                "Date": session["date"],
                "Session Type": session["session_type"].replace("_", " ").title(),
                "Total Detections": sum(session["emotions"].values()),
                "Dominant Emotion": max(session["emotions"], key=session["emotions"].get)
            }
            for session in emotions_data["sessions"][-10:]  # Last 10 sessions
        ])
        
        st.dataframe(sessions_df, use_container_width=True)
    else:
        st.info("No detection sessions found. Start using the app to see data here!")
    
    # Emotion statistics
    st.subheader("📈 Detailed Emotion Statistics")
    
    if all_emotions:
        emotion_cols = st.columns(len(all_emotions))
        
        for i, (emotion, count) in enumerate(all_emotions.items()):
            with emotion_cols[i]:
                percentage = (count / total_detections * 100) if total_detections > 0 else 0
                st.markdown(f"""
                <div class="emotion-stat">
                    <h4>{emotion}</h4>
                    <h3>{count}</h3>
                    <p>{percentage:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()