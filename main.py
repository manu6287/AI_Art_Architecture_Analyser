from __future__ import print_function
import sys
import os
from flask import Flask, jsonify, render_template, request, url_for, session
import google.generativeai as genai
from dotenv import load_dotenv
import uuid
import base64
import json
import enum
from typing_extensions import TypedDict
from structures import *


load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24) # Needed for sessions to work

# Set up authentication
api_key = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=api_key)

if not api_key:
    raise ValueError("Please make sure to define your GOOGLE_API_KEY in your .env file")
    
def json_response(prompt, instruction, schema):
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
    
def json_response_with_image(prompt, instruction, schema, image_path):
    
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
    
def feedback_intent_resolution(prompt: str):
    try:
        instruction = "Please evaluate carefully whether the given image is of a painting(made with paint) or a sketch(made with pencil) and return the enum value that matches according to the specified response schema."
        # Generate Response
        result = json_response(prompt=prompt, instruction=instruction, schema=FeedbackType)
        
        if "error" in result:
            print(f"Error in LLM response: {result['error']}", file=sys.stderr)
            return None, None
        
        try:
            response_text = result.candidates[0].content.parts[0].text.strip()
            
            response_dict = json.loads(response_text)
            intent = FeedbackType(response_dict)
            print(f"Feedback Type: {intent}", file=sys.stderr)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            print(f"Error parsing JSON: {e}", file=sys.stderr)
            return None, None
        

        schema = ''
        instruction = "You are an app which compares how similar questions are. Compare the prompt to all the enum values and return the most similar one while following the response schema."
        if intent == FeedbackType.PAINTING:
            result = json_response(prompt=prompt, instruction=instruction, schema=PaintingIntent)
            response_text = result.candidates[0].content.parts[0].text.strip()
            response_dict = json.loads(response_text)
            intent = PaintingIntent(response_dict)
            instruction = 'You are a chatbot that provides detailed feedback on the user\'s painting for each field in the json response schema. The tone should be soft and educational, providing concrete suggestions for improvement.'
        elif intent == FeedbackType.SKETCH:
            result = json_response(prompt=prompt, instruction=instruction, schema=SketchIntent)
            response_text = result.candidates[0].content.parts[0].text.strip()
            response_dict = json.loads(response_text)
            intent = SketchIntent(response_dict)
            instruction = 'You are a chatbot that provides detailed feedback on the user\'s sketch for each field in the json response schema. The tone should be soft and educational, providing concrete suggestions for improvement.'

        else:
            return {"error": "Please specify whether you are asking for feedback on a sketch or a painting."}
        print(f"Feedback Intent: {intent}", file=sys.stderr)
        schema = resolve_schema(intent)

        return instruction, schema

    except Exception as e:
        print(f"Error in feedback_intent_resolution: {e}", file=sys.stderr)
        return None, None
    
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

        result = json_response_with_image(prompt=prompt, instruction=instruction, schema=Analysis, image_path=image_path)
        
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
def generate_chatbot_response(image_path, prompt, schema, instruction):
     try:
         # Load the image using Pillow
         if image_path:
             with open(image_path, "rb") as image_file:
                 image_data = image_file.read()
             base64_image = base64.b64encode(image_data).decode('utf-8')
         else:
             base64_image = None

         chat_history = session.get('chat_history', [])

         if base64_image:
             response = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instruction).generate_content(
                 [{'mime_type': 'image/jpeg', 'data': base64_image}, prompt] + chat_history,
                 generation_config=genai.GenerationConfig(
                 response_mime_type="application/json",
                 response_schema=schema)
                 )
         else:
             response = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instruction).generate_content(
                 [prompt] + chat_history,
                 generation_config=genai.GenerationConfig(
                 response_mime_type="application/json",
                 response_schema=schema)
                 )
         chat_history.append(f'User: {prompt} Bot: {response.text}')
         session['chat_history'] = chat_history
         return response
     except Exception as e:
         return {"error": str(e)}
    
def chatbot_response_process(prompt, image_path):
    try:
        chat_history = session.get('chat_history', [])
        instruction = None
        schema = None
        if chat_history.__len__() < 1:
            instruction, schema = feedback_intent_resolution(prompt)

        if instruction is None or schema is None:
            instruction = 'You are a chatbot that provides detailed feedback only on the requested specific factor of the user\'s art. The tone should be soft and educational, providing concrete suggestions for improvement. Use 200 words or less.'
            schema=Reply

        if image_path:
            result = generate_chatbot_response(prompt=prompt, instruction=instruction, schema=schema, image_path=image_path)
        else:
            result = generate_chatbot_response(prompt=prompt, instruction=instruction, schema=schema)

        if "error" in result:
             print(f"ERROR: LLM Response Error: {result['error']}", file=sys.stderr)
             return {"error": "ERROR: Failed to generate chatbot response"}
        try:
             response_text = result.candidates[0].content.parts[0].text.strip()
             response_dict = json.loads(response_text)
        except (json.JSONDecodeError, KeyError, IndexError) as e:
             print(f"ERROR: JSON Parsing Error: {e}", file=sys.stderr)
             return {"error": "ERROR: Failed to parse JSON response"}

        return response_dict
    except Exception as e:
        print(f"ERROR: chatbot_response_process failed: {e}", file=sys.stderr)
        return {"error": "ERROR: chatbot_response_process failed"}
     
def resolve_schema(intent):
    intent_to_template = {
        PaintingIntent.A: ResponseTemplateA,
        PaintingIntent.B: ResponseTemplateB,
        PaintingIntent.C: ResponseTemplateC,
        PaintingIntent.D: ResponseTemplateD,
        PaintingIntent.E: ResponseTemplateE,
        PaintingIntent.F: ResponseTemplateF,
        PaintingIntent.G: ResponseTemplateG,
        PaintingIntent.H: ResponseTemplateH,
        PaintingIntent.I: ResponseTemplateI,
        PaintingIntent.J: ResponseTemplateJ,
        SketchIntent.K: ResponseTemplate1,
        SketchIntent.L: ResponseTemplate2,
        SketchIntent.M: ResponseTemplate3,
        SketchIntent.N: ResponseTemplate4,
        SketchIntent.O: ResponseTemplate5,
        SketchIntent.P: ResponseTemplate6,
        SketchIntent.Q: ResponseTemplate7,
        SketchIntent.R: ResponseTemplate8,
        SketchIntent.S: ResponseTemplate9,
        SketchIntent.T: ResponseTemplate10,
        SketchIntent.U: ResponseTemplate11,
    }
    
    return intent_to_template.get(intent, None)
     
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
        
        chat_response = jsonify(chatbot_response_process(prompt=user_prompt, image_path=None))
        return chat_response

    file = request.files['file']
    user_prompt = request.form.get('msg')

    if file.filename == '':
        chat_response = jsonify(chatbot_response_process(prompt=user_prompt, image_path=None))
        return chat_response

    if file:
        filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]
        filepath = os.path.join('static', 'uploads', filename)
        file.save(filepath)
        chat_response = jsonify(chatbot_response_process(image_path=filepath, prompt=user_prompt))
        return chat_response


@app.route('/chatbot', methods=['GET'], endpoint="ChatBot")
def chatbot():
    chat_history = session.get('chat_history', [])
    return render_template('ChatBot.html', chat_history=chat_history)



if __name__ == '__main__':
    os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)
    app.run(debug=False)