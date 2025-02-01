# Define Enums and Analysis Schema
import enum
from typing_extensions import TypedDict


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

class FeedbackIntent(enum.Enum):
    ARTSTYLE = "Artstyle"
    EMOTION = "Emotion"
    SPECIFIC_OBJECT = "Specific Object" 