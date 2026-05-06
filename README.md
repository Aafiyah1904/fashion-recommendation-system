<<<<<<< HEAD
# Fashion Recommendation System

A simple web-based fashion recommendation system that takes an uploaded image and recommends similar outfits from a dataset using color analysis.

---

## Project Structure

```
fashion_system/
├── index.html     ← Frontend structure
├── style.css      ← All styling
├── script.js      ← Frontend logic (upload, fetch, render)
├── app.py         ← Python Flask backend (recommendation engine)
└── README.md
```

---

## How to Run

### Step 1 — Install Python dependencies

```bash
pip install flask flask-cors Pillow numpy
```

### Step 2 — Start the backend

```bash
python app.py
```

You should see:
```
Running on http://127.0.0.1:5000
```

### Step 3 — Open the frontend

Open `index.html` in your browser (double-click it).

---

## How It Works

1. User uploads a fashion image via the browser
2. The image is sent to the Python Flask backend (`/recommend`)
3. Backend extracts the **dominant color** from the image using PIL + NumPy
4. It **detects the category** (casual, formal, ethnic, party, sport, western) from the color range
5. Each dataset item is **scored** by combining color distance + category match
6. Top 8 most similar outfits are returned as JSON
7. Frontend renders the results with similarity percentage bars

---

## Dataset

25 fashion items covering categories:
- Casual, Formal, Ethnic, Party, Sport, Western

Each item has: name, category, description, dominant color (RGB), and style tags.

---

## Technologies Used

| Layer    | Technology          |
|----------|---------------------|
| Frontend | HTML, CSS           |
| Logic    | JavaScript (fetch)  |
| Backend  | Python, Flask       |
| Image    | Pillow, NumPy       |
=======
# fashion-recommendation-system
>>>>>>> bb05b1842a148eec4880dbf12586727ba1198605
