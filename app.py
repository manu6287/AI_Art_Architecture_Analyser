import os
from flask import Flask, render_template, request, url_for, jsonify
import google.generativeai as genai
import uuid
import base64
import json
import enum
from typing_extensions import TypedDict


app = Flask(__name__)

# Set up authentication
api_key = "..."
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

class FeedbackArtStyle(TypedDict):
    brushwork: str
    palette: str
    comp_struct: str
    light_shadow: str
    lines_shapes : str
    scale_proportion: str

class FeedbackEmotionEval(TypedDict):
    color_palette : str
    Brushwork_texture : str
    Compositon_framing: str
    Lighting_shadow: str
    Lines_shapes : str    
    scale_proportions: str
    brushstroke_mov: str

class FeedbackSthSpecific:
    prop_anatomy: str
    persp_depth: str
    line_quality: str
    lighting_shadows: str
    texture_detail: str
    comp_framing: str
    color: str #if applicable
    mood_emotion: str
    flow_gesture: str
    overall_concept: str    


def provide_feedback(image_path, prompt:str):
    try:
        instruction = ''
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()

        base64_image = base64.b64encode(image_data).decode('utf-8')

        result = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instruction).generate_content(
            [{'mime_type': 'image/jpeg', 'data': base64_image}, prompt],
             generation_config=genai.GenerationConfig(
                response_mime_type="application/json", response_schema=FeedbackArtStyle
            ),
        )


    except Exception as e:
        return {"error": str(e)}

def provide_feedback(prompt:str):
    try:
        instruction = ''
        result = genai.GenerativeModel("gemini-1.5-flash", system_instruction=instruction).generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json", response_schema=Analysis
            ),
        )

    except Exception as e:
        return {"error": str(e)}

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


if __name__ == '__main__':
    os.makedirs(os.path.join('static', 'uploads'), exist_ok=True)
    app.run(debug=False)