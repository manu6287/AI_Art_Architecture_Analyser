import os
from flask import Flask, render_template, request, url_for, jsonify
import google.generativeai as genai
import uuid
import base64
import json
import enum
from typing_extensions import TypedDict
from dotenv import load_dotenv
from main import response, response_with_image
from structures import Type, Analysis, FeedbackArtStyle, FeedbackEmotionEval, FeedbackIntent, FeedbackSthSpecific

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