# 🎭 EmotiDetect AI - Face Emotion Detection App

A comprehensive real-time emotion detection application built with Streamlit, OpenCV, Keras, and Gemini AI integration.

## 🌟 Features

- **🔐 User Authentication**: Secure login and signup system
- **📊 Interactive Dashboard**: Real-time analytics and emotion statistics
- **📷 Real-Time Detection**: Live camera feed emotion recognition
- **🖼️ Image Upload Analysis**: Batch processing of uploaded images
- **🤖 AI Chatbot**: Gemini 1.5 Flash powered emotional wellness assistant
- **📈 Data Visualization**: Beautiful charts and graphs using Plotly
- **🎨 Modern UI**: Responsive design with gradient themes and animations

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Computer Vision**: OpenCV
- **Deep Learning**: TensorFlow/Keras
- **AI Chatbot**: Google Gemini 1.5 Flash
- **Data Visualization**: Plotly
- **Database**: SQLite
- **Authentication**: bcrypt
- **Image Processing**: PIL/Pillow

## 📁 Project Structure

```
emotion_detection_app/
├── 📁 assets/
│   ├── 📁 images/
│   │   ├── logo.svg
│   │   └── background.svg
│   └── 📁 models/
│       └── emotion_model.h5
├── 📁 components/
│   ├── __init__.py
│   ├── auth.py
│   ├── database.py
│   ├── emotion_detector.py
│   └── chatbot.py
├── 📁 pages/
│   ├── __init__.py
│   ├── 1_🔐_Login.py
│   ├── 2_📊_Dashboard.py
│   ├── 3_📷_Real_Time_Detection.py
│   ├── 4_🖼️_Image_Upload.py
│   └── 5_🤖_Chatbot.py
├── 📁 data/
│   ├── users.db
│   └── emotions_data.json
├── 📁 styles/
│   └── style.css
├── requirements.txt
├── main.py
├── config.py
└── README.md
```

## 🚀 Installation & Setup

### Prerequisites

- Python 3.8 or higher
- Webcam (for real-time detection)
- Google Gemini API key

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/emotion-detection-app.git
cd emotion-detection-app
```

### Step 2: Create Virtual Environment

```bash
python -m venv emotion_env
source emotion_env/bin/activate  # On Windows: emotion_env\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Download Emotion Model

You'll need to download a pre-trained emotion detection model or train your own:

```python
# Example using fer2013 dataset
# Place the trained model as: assets/models/emotion_model.h5
```

### Step 5: Configure Environment

1. Create a `.env` file in the root directory:
```
GEMINI_API_KEY=your_gemini_api_key_here
```

2. Update the API key in `components/chatbot.py`:
```python
API_KEY = "AIzaSyD8YsGR1zzgNaTiu65ziFzB97YNt8DIh4M"  # Replace with your key
```

### Step 6: Run the Application

```bash
streamlit run main.py
```

The app will be available at `http://localhost:8501`

## 🎯 Usage Guide

### 1. Authentication
- Create a new account on the login page
- Login with your credentials
- Your session will be maintained across app restarts

### 2. Dashboard
- View overall emotion statistics
- See recent detection history
- Monitor app usage metrics

### 3. Real-Time Detection
- Click "Start Camera" to begin live detection
- Position your face in the camera frame
- View real-time emotion classification
- See confidence scores and analytics

### 4. Image Upload
- Upload PNG, JPG, or JPEG images
- Support for multiple faces in one image
- Detailed emotion analysis with confidence scores
- Historical analysis of uploaded images

### 5. AI Chatbot
- Chat about emotions and mental wellness
- Get personalized advice based on your emotion history
- Use quick action buttons for common queries
- Context-aware responses using your detection data

## 📊 Supported Emotions

- 😊 **Happy**: Joy, contentment, satisfaction
- 😢 **Sad**: Sorrow, melancholy, disappointment
- 😠 **Angry**: Rage, frustration, irritation
- 😲 **Surprise**: Shock, amazement, wonder
- 😨 **Fear**: Anxiety, worry, apprehension
- 🤢 **Disgust**: Aversion, repulsion, distaste
- 😐 **Neutral**: Calm, composed, balanced

## 🔧 Configuration

### Model Configuration
- Model path: `assets/models/emotion_model.h5`
- Input size: 48x48 grayscale images
- Architecture: CNN (Convolutional Neural Network)

### Camera Settings
- Default resolution: 640x480
- Frame rate: 30 FPS
- Face detection: Haar Cascade

### Database Schema
```sql
-- Users table
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT,
    created_at TIMESTAMP
);
```

## 🚨 Troubleshooting

### Common Issues

1. **Camera not working**
   - Ensure camera permissions are granted
   - Check if other apps are using the camera
   - Try changing camera index in code (0, 1, 2, etc.)

2. **Model loading errors**
   - Verify model file exists in `assets/models/`
   - Check TensorFlow/Keras compatibility
   - Ensure sufficient memory available

3. **Gemini API errors**
   - Verify API key is correct and active
   - Check internet connection
   - Ensure API quota isn't exceeded

4. **Streamlit issues**
   - Clear browser cache
   - Restart the application
   - Check Python version compatibility

### Performance Optimization

- **CPU Usage**: Reduce camera resolution for better performance
- **Memory**: Close other applications when running
- **Model**: Use quantized models for faster inference
- **Browser**: Use Chrome/Firefox for best Streamlit experience

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenCV** for computer vision capabilities
- **TensorFlow/Keras** for deep learning framework
- **Streamlit** for the amazing web app framework
- **Google Gemini** for AI chatbot integration
- **Plotly** for beautiful data visualizations
- **FER2013 Dataset** for emotion recognition training data

## 📞 Support

For support, email support@emotidetect.ai or join our Discord community.

## 🔮 Future Enhancements

- [ ] Mobile app version
- [ ] Voice emotion detection
- [ ] Multi-language support
- [ ] Advanced analytics dashboard
- [ ] Export emotion reports
- [ ] Integration with wearable devices
- [ ] Cloud deployment options
- [ ] Real-time emotion tracking API

---

Made with ❤️ by the EmotiDetect AI Team