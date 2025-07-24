import google.generativeai as genai
import streamlit as st
from datetime import datetime
import json
import os

class GeminiChatbot:
    def __init__(self, api_key="AIzaSyD8YsGR1zzgNaTiu65ziFzB97YNt8DIh4M"):
        """Initialize Gemini chatbot with API key"""
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        
        # System prompt for emotion-focused conversations
        self.system_prompt = """
        You are EmotiBot, an AI assistant specialized in emotional intelligence and mental wellness. 
        You help users understand emotions, provide emotional support, and give advice on emotional well-being.
        
        Key characteristics:
        - Empathetic and understanding
        - Knowledgeable about emotions and psychology
        - Supportive and encouraging
        - Provide practical advice for emotional situations
        - Help users interpret facial emotion detection results
        
        Always respond in a warm, caring tone and focus on emotional wellness.
        """
        
        # Initialize chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
    
    def get_response(self, user_message, emotion_context=None):
        """Get response from Gemini model"""
        try:
            # Prepare the prompt with context
            if emotion_context:
                context_prompt = f"""
                Context: The user's recent emotion detection showed: {emotion_context}
                
                User message: {user_message}
                
                Please provide a helpful response considering their emotional state.
                """
            else:
                context_prompt = f"{self.system_prompt}\n\nUser: {user_message}"
            
            # Generate response
            response = self.model.generate_content(context_prompt)
            return response.text
            
        except Exception as e:
            st.error(f"Error generating response: {str(e)}")
            return "I'm sorry, I'm having trouble connecting right now. Please try again later."
    
    def add_to_history(self, user_message, bot_response):
        """Add conversation to history"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conversation = {
            'timestamp': timestamp,
            'user': user_message,
            'bot': bot_response
        }
        
        st.session_state.chat_history.append(conversation)
        
        # Keep only last 50 conversations to manage memory
        if len(st.session_state.chat_history) > 50:
            st.session_state.chat_history = st.session_state.chat_history[-50:]
    
    def get_emotion_advice(self, detected_emotion):
        """Get specific advice based on detected emotion"""
        emotion_prompts = {
            'happy': "The user seems happy! Give them positive reinforcement and suggest ways to maintain this positive mood.",
            'sad': "The user appears sad. Provide gentle, supportive advice and coping strategies.",
            'angry': "The user looks angry. Offer calming techniques and anger management advice.",
            'fear': "The user seems fearful or anxious. Provide reassurance and anxiety management tips.",
            'surprise': "The user appears surprised. Help them process unexpected situations positively.",
            'disgust': "The user shows signs of disgust or discomfort. Offer supportive guidance.",
            'neutral': "The user has a neutral expression. Offer general wellness and mood-boosting tips."
        }
        
        prompt = emotion_prompts.get(detected_emotion.lower(), 
                                   "Provide general emotional wellness advice.")
        
        return self.get_response("", emotion_context=f"Detected emotion: {detected_emotion}")
    
    def clear_history(self):
        """Clear chat history"""
        st.session_state.chat_history = []
    
    def export_chat_history(self):
        """Export chat history as JSON"""
        return json.dumps(st.session_state.chat_history, indent=2)
    
    def get_emotional_insights(self, emotions_data):
        """Analyze emotion patterns and provide insights"""
        if not emotions_data:
            return "No emotion data available for analysis."
        
        # Create analysis prompt
        analysis_prompt = f"""
        Analyze this emotion detection data and provide insights:
        {json.dumps(emotions_data, indent=2)}
        
        Please provide:
        1. Overall emotional patterns
        2. Recommendations for emotional well-being
        3. Any concerning trends
        4. Positive observations
        """
        
        return self.get_response(analysis_prompt)
    
    def suggest_mood_activities(self, current_emotion):
        """Suggest activities based on current emotion"""
        activity_prompt = f"""
        The user is currently feeling {current_emotion}. 
        Suggest 5 specific activities or techniques that could help them:
        1. Maintain positive emotions if they're feeling good
        2. Improve their mood if they're feeling negative emotions
        3. Manage stress or anxiety
        
        Make the suggestions practical and actionable.
        """
        
        return self.get_response(activity_prompt)