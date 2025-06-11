import os
import cv2
import pytesseract
from PIL import Image
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from reportlab.pdfgen import canvas

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OVERLAY_FOLDER = 'overlays'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OVERLAY_FOLDER, exist_ok=True)

# --- Admin Credentials (example only, use hashed passwords in production) ---
ADMIN_USER = "Karthik Gunda"
ADMIN_PASS = "VaastuGeniusAdmin2025!"

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    if data['username'] == ADMIN_USER and data['password'] == ADMIN_PASS:
        return jsonify({"status": "success", "message": "Welcome Karthik Gunda"})
    return jsonify({"status": "fail", "message": "Unauthorized"}), 401

@app.route('/analyze', methods=['POST'])
def analyze():
    file = request.files['image']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    result, image_name, pdf_file = analyze_floorplan(filepath, filename)
    return jsonify({"result": result, "image": image_name, "pdf": pdf_file})

@app.route('/chakra/remedies', methods=['GET'])
def chakra_remedies():
    tips = {
        "NE": "Ideal for meditation/yoga. Keep space clean.",
        "SE": "Best for kitchen. Avoid clutter.",
        "SW": "Use for master bedroom. Add stability colors.",
        "NW": "Good for guest rooms or storage."
    }
    return jsonify(tips)

@app.route('/report/<filename>', methods=['GET'])
def get_report(filename):
    return send_file(os.path.join(OVERLAY_FOLDER, filename), as_attachment=True)

# --- Analyze Floorplan Function ---
def analyze_floorplan(image_path, filename):
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)

    detected_rooms = []
    keywords = ['kitchen', 'bedroom', 'toilet', 'hall', 'living']
    for word in text.lower().split():
        if word in keywords:
            detected_rooms.append(word)

    zones = list(set(detected_rooms)) or ['Unknown']
    overlay_filename = f"overlay_{filename}"
    overlay_path = os.path.join(OVERLAY_FOLDER, overlay_filename)

    # Draw dummy labels on image
    for i, zone in enumerate(zones):
        cv2.putText(image, zone, (50, 50 + i*30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imwrite(overlay_path, image)

    # Create PDF report
    pdf_name = filename.replace('.', '_') + '.pdf'
    pdf_path = os.path.join(OVERLAY_FOLDER, pdf_name)
    c = canvas.Canvas(pdf_path)
    c.drawString(100, 800, f"Vaastu Genius Report for {filename}")
    c.drawString(100, 770, f"Detected Zones: {', '.join(zones)}")
    c.drawString(100, 740, f"Chakra Suggestion: SW = Bedroom, NE = Meditation")
    c.save()

    return zones, overlay_filename, pdf_name

if __name__ == '__main__':
    app.run(debug=True)
@app.route('/')
def home():
    return "✅ Vaastu Genius AI Backend is Live!"
