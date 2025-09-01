import numpy as np
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.resnet50 import preprocess_input
from sklearn.metrics.pairwise import cosine_similarity
from model_loader import model
from sklearn.preprocessing import normalize

def extract_features(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    features = model.predict(x)
    return features

def verify_signatures(original_path, test_path):
    features1 = extract_features(original_path)
    features2 = extract_features(test_path)
    f1 = normalize(features1)
    f2 = normalize(features2)
    similarity = cosine_similarity(f1, f2)[0][0]
    threshold = 0.75
    match = similarity >= threshold

    return float(similarity), bool(match)
