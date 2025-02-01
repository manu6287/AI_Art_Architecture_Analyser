import os
from flask import Flask, render_template, request, url_for, session
import google.generativeai as genai
from dotenv import load_dotenv
import uuid
import base64
import json
import enum
from typing_extensions import TypedDict
from structures import Type, Analysis, FeedbackArtStyle, FeedbackEmotionEval, FeedbackIntent, FeedbackSthSpecific

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24) # Needed for sessions to work

# Set up authentication
api_key = "AIzaSyCNfoz9ynNBUPlomIRwAhf5B8g5NcWAwmg"
#os.getenv('GOOGLE_API_KEY')
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
    
def feedback_intent_resolution (prompt: str):
    try:

        instruction = "Determine which aspect of their art the user intends to work on based on the given prompt. Reply only with one of the following enums for FeedbackIntent: 'Artstyle', 'Emotion', or 'Specific Object'."

        # Generate Response
        result = response(prompt=prompt, instruction=instruction, schema=Type) 
        
        # Extract JSON response (assuming the response is inside `candidates[0]['content']['parts'][0]['text']`)
        response_text = result.candidates[0].content.parts[0].text.strip()
        response_dict = json.loads(response_text)

        # Extract the FeedbackIntent value
        intent_value = response_dict.get("FeedbackIntent")

        # Convert to Enum
        intent = FeedbackIntent(intent_value)

        # Map the response to the Enum (Ensure it matches exactly)
        schema = ''
        # Execute Different Code Based on the Intent
        if intent == FeedbackIntent.ARTSTYLE:
            instruction = 'Give feedback on how to improve the given artwork for the desired artstyle for each category in the schema. Reply with the specified json schema.'
            schema = FeedbackArtStyle

            print("User wants to improve their art style. Suggesting relevant techniques...")
            # Execute Code for Art Style Enhancement
        elif intent == FeedbackIntent.EMOTION:
            instruction = 'Give feedback on how to convey or better convey the desired emotion in the given artwork for each category in the schema. Reply with the specified json schema.'
            schema = FeedbackEmotionEval
            print("User wants to convey emotions better in their art. Suggesting emotional expression techniques...")
            # Execute Code for Enhancing Emotion in Art
        elif intent == FeedbackIntent.SPECIFIC_OBJECT:
            instruction = 'Give feedback on how to add or better include the specific desired object(s) into the given artwork for each category in the schema. Reply with the specified json schema.'
            schema = FeedbackSthSpecific
            print("User wants to focus on a specific object. Providing detailed object-based suggestions...")
            # Execute Code for Improving Specific Object Representation
        else:
            print("Unknown intent detected.")

        return instruction, schema

    except Exception as e:
        return {"error": str(e)}

def analyze_image(image_path):
    try:
        instruction = (
            "You are an app that analyses art in artwork, buildings, and sculptures. "
            "You will identify the type of art, the title of the work, which style was used to create it, "
            "who the creator is, the year it was created, the name of the era when it was created, "
            "the provenance, the cultural geographic origin, the meaning and/or the context of the work, "
            "If you don't know the answer to some field use value 'unknown', "
            "and then output in the specified JSON format."
        )

        prompt = "What can you tell me about this work of art?"

        result = response_with_image(prompt=prompt, instruction=instruction, schema=Analysis, image_path=image_path)
        
        # Extract the content from the result
        if result and hasattr(result, 'candidates') and result.candidates:
            # Get the JSON string from the model's response
            json_text = result.candidates[0].content.parts[0].text

            # Parse the JSON string into a Python dictionary
            analysis_data = json.loads(json_text)

            return analysis_data
        else:
             return {"error": "Invalid data in the response."}

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