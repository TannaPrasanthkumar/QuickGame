import streamlit as st
from streamlit_drawable_canvas import st_canvas
import google.generativeai as genai
import random
from PIL import Image
import numpy as np
import time

# Read the API key
with open('key.txt', 'r') as file:
    key = file.read().strip()

genai.configure(api_key=key)
model = genai.GenerativeModel('gemini-1.5-flash')

words = []

with open('words.txt', 'r') as file:
    for line in file:
        word = line.strip()  
        words.append(word)
        
easy_words = words[:36]
medium_words = words[36:56]
difficulty_words = words[56:]

words = {
    'easy': easy_words,
    'medium': medium_words,
    'hard': difficulty_words
}

st.set_page_config(
    page_title="Google QuickDraw Clone", page_icon="🎨", layout="wide"
)

st.title("QuickDraw Clone powered by Gemini")
st.markdown(
"""
Welcome to QuickDraw!
Unleash your inner artist and challenge our AI to guess your doodles. Draw, test, and see if our AI can keep up with your creativity. Let the fun begin! 
"""
)

# Left sidebar for game controls and drawing tools
left_sidebar = st.sidebar

# Add difficulty selection in left sidebar
difficulty = left_sidebar.selectbox("Select difficulty:", ['easy', 'medium', 'hard'])

# Initialize session state variables
if 'current_word' not in st.session_state or st.session_state.difficulty != difficulty:
    st.session_state.current_word = random.choice(words[difficulty])
    st.session_state.difficulty = difficulty
    st.session_state.score = 0
    st.session_state.round = 1
    st.session_state.start_time = time.time()
    st.session_state.response = None
    st.session_state.result_message = None

# Display the current word to draw
left_sidebar.write(f"Draw a: {st.session_state.current_word}")

# Display timer
elapsed_time = int(time.time() - st.session_state.start_time)
left_sidebar.write(f"Time: {elapsed_time} seconds")

MAX_ROUNDS = 10

# Left sidebar for game stats
left_sidebar.write(f"Score: {st.session_state.score}")
left_sidebar.write(f"Round: {st.session_state.round} / {MAX_ROUNDS}")

# Drawing tool controls in left sidebar
drawing_mode = left_sidebar.selectbox(
    "Drawing tool:",
    ("freedraw", "line", "rect", "circle", "transform", "polygon", "point"),
)

stroke_width = left_sidebar.slider("Stroke width: ", 1, 25, 3)
if drawing_mode == "point":
    point_display_radius = left_sidebar.slider("Point display radius: ", 1, 25, 3)
stroke_color = left_sidebar.color_picker("Stroke color hex: ")
bg_color = left_sidebar.color_picker("Background color hex: ", "#fff")

# Main content area
main_col, right_sidebar = st.columns([0.7, 0.3])

with main_col:
    # Canvas for drawing
    canvas_result = st_canvas(
        stroke_width=stroke_width,
        stroke_color=stroke_color,
        background_color=bg_color,
        update_streamlit=True,
        width=480,
        height=480,
        drawing_mode=drawing_mode,
        point_display_radius=point_display_radius if drawing_mode == "point" else 0,
        key="full_app",
    )

    if st.button("Guess My Drawing"):
        if canvas_result.image_data is not None:
            # Convert the image data to a format Gemini can use
            image = Image.fromarray((canvas_result.image_data * 255).astype(np.uint8), 'RGBA')
            image = image.convert('RGB')

            # Send image to Gemini
            prompt = f"""
            Analyze the image and determine what object is drawn.
            The drawing is meant to represent one of the following: {', '.join(words[difficulty])}.
            Respond with a single word that best matches the drawn object from the given list.
            """
            response = model.generate_content([prompt, image])
            
            st.session_state.response = response

            # Check Gemini's response
            if response and response.text.strip().lower() == st.session_state.current_word.strip().lower():
                st.session_state.score += 1
                st.session_state.result_message = f"Correct! The answer was {st.session_state.current_word}."
                st.session_state.current_word = random.choice(words[difficulty])
                st.session_state.start_time = time.time()  # Reset timer for next word
            else:
                st.session_state.result_message = f"Wrong. The correct answer was {st.session_state.current_word}."
                st.session_state.current_word = random.choice(words[difficulty])
                st.session_state.start_time = time.time()  # Reset timer for next word
            
            st.session_state.round += 1
            st.rerun()

    if st.button("Clear Canvas"):
        st.session_state.response = None
        st.session_state.result_message = None
        st.rerun()

# Right sidebar for responses
with right_sidebar:
    st.write("Gemini's Response:")
    if st.session_state.response:
        st.write(f"Gemini's guess: {st.session_state.response.text}")
    
    if st.session_state.result_message:
        st.write(st.session_state.result_message)

if st.session_state.round > MAX_ROUNDS:
    right_sidebar.success(f"Game Over! Your final score is {st.session_state.score} out of {MAX_ROUNDS}.")
    if right_sidebar.button("Play Again"):
        st.session_state.score = 0
        st.session_state.round = 1
        st.session_state.current_word = random.choice(words[difficulty])
        st.session_state.start_time = time.time()
        st.session_state.response = None
        st.session_state.result_message = None
        st.rerun()