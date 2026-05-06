from flask import Flask, request, jsonify, send_from_directory
from PIL import Image
import numpy as np
import pandas as pd
import io
import os
import cv2
from datetime import datetime

app = Flask(__name__, static_folder='.', static_url_path='')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATASET_DIR = os.path.join(BASE_DIR, "fashion-dataset")
IMAGES_DIR = os.path.join(DATASET_DIR, "images")
STYLES_CSV = os.path.join(DATASET_DIR, "styles.csv")

HISTORY_DIR = os.path.join(BASE_DIR, "history")
os.makedirs(HISTORY_DIR, exist_ok=True)

MAX_ITEMS = 2000
THUMB = (64, 64)

DATASET_META = []
DATASET_FEATURES = {}

def extract_features(image):
    img = image.convert("RGB").resize(THUMB)
    arr = np.array(img, dtype=np.float32)

    feat = []

    ch, cw = THUMB[1] // 4, THUMB[0] // 4

    for r in range(4):
        for c in range(4):
            cell = arr[r*ch:(r+1)*ch, c*cw:(c+1)*cw, :]
            feat.extend(cell.mean(axis=(0, 1)).tolist())

    feat.extend(arr.mean(axis=(0, 1)).tolist())

    return np.array(feat, dtype=np.float32)

def detect_texture(image):

    img = image.convert("L").resize((128, 128))
    arr = np.array(img)

    edges = cv2.Canny(arr, 80, 150)
    edge_density = np.mean(edges)

    if edge_density < 10:
        return "plain"
    elif edge_density < 25:
        return "striped"
    else:
        return "checked/patterned"

def detect_category(image):

    width, height = image.size
    ratio = height / width

    if ratio > 1.4:
        return "dress"
    elif ratio > 1.1:
        return "topwear"
    else:
        return "bottomwear"

def cosine_similarity(a, b):

    denom = np.linalg.norm(a) * np.linalg.norm(b)

    return float(np.dot(a, b) / denom) if denom > 0 else 0.0

def load_dataset():

    global DATASET_META, DATASET_FEATURES

    print("Loading dataset...")

    df = pd.read_csv(STYLES_CSV, on_bad_lines='skip')

    df.columns = df.columns.str.strip()

    df = df[df['id'].apply(lambda x:
        os.path.isfile(os.path.join(IMAGES_DIR, f"{int(x)}.jpg"))
    )]

    df = df.sample(n=min(MAX_ITEMS, len(df)), random_state=42)

    meta = []
    feats = {}

    for _, row in df.iterrows():

        item_id = int(row['id'])

        img_path = os.path.join(IMAGES_DIR, f"{item_id}.jpg")

        try:
            img = Image.open(img_path).convert("RGB")
            feat = extract_features(img)
            texture = detect_texture(img)

        except:
            continue

        category = str(row.get('subCategory', 'unknown')).lower()

        meta.append({
            "id": item_id,
            "name": str(row.get('productDisplayName', 'Item'))[:50],
            "category": category,
            "color": str(row.get('baseColour', 'unknown')),
            "texture": texture,
            "description": f"{row.get('usage','')} · {row.get('season','')}",
            "image_file": f"{item_id}.jpg"
        })

        feats[item_id] = feat

    DATASET_META = meta
    DATASET_FEATURES = feats

    print(f"Loaded {len(DATASET_META)} items")

load_dataset()

@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

@app.route('/images/<filename>')
def images(filename):
    return send_from_directory(IMAGES_DIR, filename)

@app.route('/history/<filename>')
def history(filename):
    return send_from_directory(HISTORY_DIR, filename)

@app.route('/dataset')
def dataset():
    return jsonify(DATASET_META[:60])

@app.route('/recommend', methods=['POST'])
def recommend():

    if 'image' not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files['image']

    try:
        image = Image.open(io.BytesIO(file.read())).convert("RGB")

    except:
        return jsonify({"error": "Invalid image"}), 400

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    history_name = f"upload_{timestamp}.jpg"

    history_path = os.path.join(HISTORY_DIR, history_name)

    image.save(history_path)

    query_feat = extract_features(image)

    detected_category = detect_category(image)

    detected_texture = detect_texture(image)

    scored = []

    for item in DATASET_META:

        item_id = item['id']

        feat = DATASET_FEATURES[item_id]

        sim = cosine_similarity(query_feat, feat)

        if detected_category in item['category']:
            sim += 0.15

        if detected_texture == item['texture']:
            sim += 0.10

        scored.append({
            **item,
            "similarity": int(sim * 100),
            "image_url": f"/images/{item['image_file']}"
        })

    scored.sort(key=lambda x: x['similarity'], reverse=True)

    return jsonify({
        "detected_category": detected_category,
        "detected_texture": detected_texture,
        "history_image": f"/history/{history_name}",
        "recommendations": scored[:8]
    })

if __name__ == '__main__':
    app.run(debug=True)