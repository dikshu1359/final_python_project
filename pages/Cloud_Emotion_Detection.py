import streamlit as st
import requests
import tempfile
from PIL import Image

st.set_page_config(page_title="Cloud Emotion Detection (Azure)", page_icon="☁️", layout="centered")
st.title("Cloud Emotion Detection (Microsoft Azure Face API)")

st.markdown("""
This demo uses the Microsoft Azure Face API for highly accurate emotion detection.<br>
You need an Azure Face API key and endpoint. [Get one here.](https://portal.azure.com/)
""", unsafe_allow_html=True)

api_key = st.text_input("Azure Face API Key", type="password")
endpoint = st.text_input("Azure Face API Endpoint (e.g. https://<your-region>.api.cognitive.microsoft.com)")

uploaded_file = st.file_uploader("Upload an image for emotion detection", type=["jpg", "jpeg", "png"])

if uploaded_file and api_key and endpoint:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp_file:
        image.save(tmp_file.name)
        tmp_file.flush()
        with open(tmp_file.name, "rb") as image_data:
            face_api_url = endpoint.rstrip("/") + "/face/v1.0/detect"
            headers = {
                "Ocp-Apim-Subscription-Key": api_key,
                "Content-Type": "application/octet-stream"
            }
            params = {
                "returnFaceAttributes": "emotion"
            }
            with st.spinner("Detecting emotion via Azure API..."):
                response = requests.post(
                    face_api_url, headers=headers, params=params, data=image_data
                )
            if response.status_code == 200:
                faces = response.json()
                if not faces:
                    st.warning("No face detected in the image.")
                else:
                    emotions = faces[0]['faceAttributes']['emotion']
                    top_emotion = max(emotions, key=emotions.get)
                    confidence = emotions[top_emotion]
                    st.success(f"Detected Emotion: {top_emotion.title()} (Confidence: {confidence:.1%})")
                    st.write("All emotion scores:")
                    st.json(emotions)
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
else:
    st.info("Please upload an image and enter your Azure API credentials.") 