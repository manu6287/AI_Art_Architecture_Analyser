import os
from flask import Flask, render_template, request, url_for, session
import google.generativeai as genai
from dotenv import load_dotenv
import uuid
import base64
import json
import enum
from typing_extensions import TypedDict


load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24) # Needed for sessions to work


# Set up authentication
api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

if not api_key:
    raise ValueError("Please make sure to define your GOOGLE_API_KEY in your .env file")


# Define Enums and Analysis Schema
class Type(enum.Enum):
    BUILDING = "Building"
    SCULPTURE = "Sculpture"
    ARTWORK = "Artwork"


class Analysis(TypedDict):
    type: Type
    title: str
    creator: str
    style: str
    year: int
    era: str
    culturalOrigin: str
    provenance: str
    contextualMeaning: str


# Function to Analyze the Image
def analyze_image(image_path):
    try:
        # Load the image using Pillow
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        base64_image = base64.b64encode(image_data).decode('utf-8')

        instruction = (
            "You are an app that analyses art in artwork, buildings, and sculptures. "
            "You will identify the type of art, the title of the work, which style was used to create it, "
            "who the creator is, the year it was created, the name of the era when it was created, "
            "the provenance, the cultural geographic origin, the meaning and/or the context of the work, "
            "If you don't know the answer to some field use value 'unknown', "
            "and then output in the specified JSON format."
        )

        prompt = "What can you tell me about this work of art?"

        result = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instruction).generate_content(
            [{'mime_type': 'image/jpeg', 'data': base64_image}, prompt],
             generation_config=genai.GenerationConfig(
                response_mime_type="application/json", response_schema=Analysis
            ),
        )

        # Extract the content from the result
        if result and hasattr(result, 'candidates') and result.candidates:
            # Get the JSON string from the model's response
            json_text = result.candidates[0].content.parts[0].text

            # Parse the JSON string into a Python dictionary
            analysis_data = json.loads(json_text)

            return analysis_data
        else:
             return {"error": "No valid candidates in the response."}

    except Exception as e:
        return {"error": str(e)}


@app.route('/', methods=['GET', 'POST'], endpoint='home')
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