import os
from flask import Flask, render_template, request, url_for, session
import google.generativeai as genai
from dotenv import load_dotenv
import uuid
import base64
import json
import enum
from typing_extensions import TypedDict
from methods import feedback_intent_resolution, analyze_image
from structures import Type, Analysis, FeedbackArtStyle, FeedbackEmotionEval, FeedbackIntent, FeedbackSthSpecific

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24) # Needed for sessions to work

# Set up authentication
api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

if not api_key:
    raise ValueError("Please make sure to define your GOOGLE_API_KEY in your .env file")
    
def response(prompt, instruction, schema):
    try:
        result = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instruction).generate_content(
            [prompt],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=schema
            ),
        )
        
        return result
    except Exception as e:
        return {"error": str(e)}
    
def response_with_image(prompt, instruction, schema, image_path):
    
    try:
        # Load the image using Pillow
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        base64_image = base64.b64encode(image_data).decode('utf-8')
        
        result = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instruction).generate_content(
            [{'mime_type': 'image/jpeg', 'data': base64_image}, prompt],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=schema
            ),
        )
        
        return result
    except Exception as e:
        return {"error": str(e)}
            

# Function to Generate Chatbot Response
def generate_chatbot_response(image_path, user_prompt):
    try:
        # Load the image using Pillow
        if image_path:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()
            base64_image = base64.b64encode(image_data).decode('utf-8')
        else:
            base64_image = None

        chat_history = session.get('chat_history', [])
        prompt = f"""
           You are a chatbot designed to give feedback on drawings and paintings.
           Your goal is to provide constructive and helpful suggestions that will help improve user artwork.

           Your tone should be positive and encouraging. 
           If no image is provided in the prompt then just respond to the prompt alone.
           If an image is provided respond to the prompt based on the image.

           User Prompt: {user_prompt}

           Chat History: {chat_history}
       """

        if base64_image:
            response = genai.GenerativeModel("gemini-1.5-flash").generate_content(
                [{'mime_type': 'image/jpeg', 'data': base64_image}, prompt]
            )
        else:
            response = genai.GenerativeModel("gemini-1.5-flash").generate_content(prompt)

        chat_history.append(f'User: {user_prompt} Bot: {response.text}')
        session['chat_history'] = chat_history
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file part')

        file = request.files['file']

        if file.filename == '':
            return render_template('index.html', error='No selected file')

        if file:
            filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
            filepath = os.path.join('static', 'uploads', filename)
            file.save(filepath)

            analysis = analyze_image(filepath)

            return render_template('result.html', image_url=url_for('static', filename=f'uploads/{filename}'),
                                   analysis=analysis)

    return render_template('index.html')


@app.route("/get", methods=["POST"])
def chat():
    if 'file' not in request.files:
        user_prompt = request.form.get('msg')
        chat_response = generate_chatbot_response(None, user_prompt)
        return chat_response

    file = request.files['file']
    user_prompt = request.form.get('msg')

    if file.filename == '':
        chat_response = generate_chatbot_response(None, user_prompt)
        return chat_response

    if file:
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        filepath = os.path.join('static', 'uploads', filename)
        file.save(filepath)
        chat_response = generate_chatbot_response(filepath, user_prompt)
        return chat_response


@app.route('/chatbot', methods=['GET'], endpoint="ChatBot")
def chatbot():
    chat_history = session.get('chat_history', [])
    return render_template('ChatBot.html', chat_history=chat_history)



if __name__ == '__main__':
    os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)
    app.run(debug=False)