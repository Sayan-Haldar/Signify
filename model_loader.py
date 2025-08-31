from tensorflow.keras.applications import ResNet50
from tensorflow.keras.models import Model

def load_model():
    base_model = ResNet50(weights='imagenet', include_top=False, pooling='avg')
    model = Model(inputs=base_model.input, outputs=base_model.output)
    return model

# Load globally once
model = load_model()
