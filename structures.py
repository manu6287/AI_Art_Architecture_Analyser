# Define Enums and Analysis Schema
import enum
from typing_extensions import TypedDict


class Type(enum.Enum):
    BUILDING = "Building"
    SCULPTURE = "Sculpture"
    ARTWORK = "Artwork"
    
class FeedbackType(enum.Enum):
    PAINTING = "Painting"
    SKETCH = "Sketch"


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

class FeedbackSthSpecific(TypedDict):
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

class FeedbackIntent(enum.Enum):
    ARTSTYLE = "Artstyle"
    EMOTION = "Emotion"
    SPECIFIC_OBJECT = "Specific Object" 
    
class Reply(TypedDict):
    response: str
    
import enum

class SketchIntent(enum.Enum):
    K = "How to improve a sketch?"
    L = "How to make a sketch more in a particular style?"
    M = "How to express particular emotions in a sketch?"
    N = "What’s the story behind my sketch?"
    O = "How to improve the proportions of a sketch?"
    P = "How to add more detail to a sketch?"
    Q = "How to enhance depth in a sketch?"
    R = "How to simplify a sketch for clarity?"
    S = "How to improve the fluidity of my sketch?"
    T = "How to make a sketch feel more energetic?"
    U = "How to balance light and dark in a sketch?"
class PaintingIntent(enum.Enum):
    A = "How to improve this artwork?"
    B = "How to make a painting more in a particular style?"
    C = "How to express particular emotions in a painting?"
    D = "What’s the story behind my painting?"
    E = "How to enhance the depth of a painting?"
    F = "How can I add more movement to my painting?"
    G = "How to simplify a complex painting?"
    H = "How do I make my painting more dynamic?"
    I = "How to make a painting look more realistic?"
    J = "How to adjust a painting’s composition for balance?"
    
class ResponseTemplate1(TypedDict):
    line_work: str
    shading_and_value: str
    proportions_and_anatomy: str
    composition: str
    texture_and_detail: str
    perspective: str
    light_and_shadow: str
    final_polish: str

class ResponseTemplate2(TypedDict):
    line_work: str
    shading_and_value: str
    proportions_and_anatomy: str
    composition: str
    emotion_and_expression: str
    gesture_and_body_language: str
    style: str

class ResponseTemplate3(TypedDict):
    line_work: str
    shading_and_value: str
    composition: str
    emotion_and_expression: str
    body_language_and_gesture: str
    light_and_shadow: str

class ResponseTemplate4(TypedDict):
    subject_matter: str
    line_work: str
    body_language_and_gesture: str
    composition: str
    emotion_and_expression: str
    symbolism: str
    light_and_shadow: str
    context_and_background: str

class ResponseTemplate5(TypedDict):
    proportions_and_anatomy: str
    line_work: str
    perspective: str
    composition: str
    proportional_adjustments: str

class ResponseTemplate6(TypedDict):
    texture_and_detail: str
    shading_and_value: str
    line_work: str
    emotion_and_expression: str

class ResponseTemplate7(TypedDict):
    shading_and_value: str
    perspective: str
    light_and_shadow: str
    proportions_and_anatomy: str
    composition: str

class ResponseTemplate8(TypedDict):
    line_work: str
    negative_space: str
    composition: str
    shading_and_value: str
    clarity_and_cleanliness: str

class ResponseTemplate9(TypedDict):
    line_work: str
    gesture_and_body_language: str
    composition: str
    emotion_and_expression: str

class ResponseTemplate10(TypedDict):
    line_work: str
    movement_and_gesture: str
    composition: str
    emotion_and_expression: str
        
class ResponseTemplate11(TypedDict):
    shading_and_value: str
    light_and_shadow: str
    contrast: str
    composition: str
class ResponseTemplateA(TypedDict): 
    color_palette: str 
    shading_and_contrast: str 
    line_quality: str 
    texture: str 
    composition: str 
    light_and_shadow: str
    subject_matter: str
    proportions_and_anatomy: str
    final_polish: str

class ResponseTemplateB(TypedDict): 
    brushwork: str
    color_palette: str
    line_quality: str
    texture: str
    composition: str
    subject_matter: str
    emotion_and_expression: str
    light_and_shadow: str
    style: str

class ResponseTemplateC(TypedDict): 
    color_palette: str
    brushwork: str
    composition: str
    light_and_shadow: str
    texture: str
    line_quality: str
    emotion_and_expression: str
    proportions_and_anatomy: str

class ResponseTemplateD(TypedDict): 
    subject_matter: str
    composition: str
    line_work: str
    symbolism: str
    color_palette: str
    light_and_shadow: str
    emotion_and_expression: str
    context_and_background: str
    proportions_and_anatomy: str

class ResponseTemplateE(TypedDict): 
    shading_and_contrast: str
    light_and_shadow: str
    proportions_and_anatomy: str
    composition: str
    texture: str

class ResponseTemplateF(TypedDict): 
    brushwork: str
    composition: str
    emotion_and_expression: str
    line_quality: str
    subject_matter: str

class ResponseTemplateG(TypedDict): 
    composition: str
    negative_space: str
    proportions_and_anatomy: str
    final_polish: str
    subject_matter: str

class ResponseTemplateH(TypedDict): 
    brushwork: str
    color_palette: str
    line_quality: str
    light_and_shadow: str
    composition: str
    movement_and_gesture: str

class ResponseTemplateI(TypedDict): 
    shading_and_contrast: str
    proportions_and_anatomy: str
    texture: str
    light_and_shadow: str
    composition: str

class ResponseTemplateJ(TypedDict): 
    composition: str
    negative_space: str
    proportions_and_anatomy: str
    subject_matter: str
    light_and_shadow: str
