from flask import Flask, render_template, request, redirect, url_for, flash
import os
import cv2
import numpy as np

app = Flask(__name__)
app.secret_key = "your_secret_key"

UPLOAD_FOLDER = 'static/uploads'
PREDEFINED_IMAGES_FOLDER = 'images'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Predefined images for comparison
PREDEFINED_IMAGES = [
    os.path.join(PREDEFINED_IMAGES_FOLDER, "image1.jpg"),
    os.path.join(PREDEFINED_IMAGES_FOLDER, "image2.jpg"),
    os.path.join(PREDEFINED_IMAGES_FOLDER, "image3.jpg"),
]

# Initialize scores and attempts
scores = [{"highest_score": 0, "attempts": 0} for _ in PREDEFINED_IMAGES]
MAX_ATTEMPTS = 5


def calculate_similarity(image1_path, image2_path):
    """Calculate similarity score between two images."""
    img1 = cv2.imread(image1_path, cv2.IMREAD_GRAYSCALE)
    img2 = cv2.imread(image2_path, cv2.IMREAD_GRAYSCALE)

    # Resize images to match
    img1 = cv2.resize(img1, (200, 200))
    img2 = cv2.resize(img2, (200, 200))

    # Calculate similarity using Mean Squared Error (MSE)
    mse = np.mean((img1 - img2) ** 2)
    if mse == 0:
        return 100  # Perfect match
    score = max(0, 100 - int(mse / 10))  # Scale score to 0-100
    return score


@app.route('/')
def home():
    """Home page to display highest scores and average score."""
    average_score = sum([entry['highest_score'] for entry in scores]) / len(scores)
    return render_template('home.html', scores=scores, average_score=average_score)


@app.route('/upload/<int:image_index>', methods=['GET', 'POST'])
def upload(image_index):
    """Upload and compare images."""
    if image_index < 0 or image_index >= len(PREDEFINED_IMAGES):
        flash("Invalid image index!")
        return redirect(url_for('home'))

    if request.method == 'POST':
        # Check if maximum attempts exceeded
        if scores[image_index]["attempts"] >= MAX_ATTEMPTS:
            flash("Maximum attempts reached for this image!")
            return redirect(url_for('home'))

        # Check if the file exists
        if 'image' not in request.files:
            flash("No file part!")
            return redirect(request.url)

        file = request.files['image']
        if file.filename == '':
            flash("No selected file!")
            return redirect(request.url)

        # Save uploaded file
        filename = f"image_{image_index}_attempt_{scores[image_index]['attempts'] + 1}.jpg"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(upload_path)

        # Calculate similarity score
        predefined_image = PREDEFINED_IMAGES[image_index]
        score = calculate_similarity(predefined_image, upload_path)
        scores[image_index]["attempts"] += 1
        scores[image_index]["highest_score"] = max(scores[image_index]["highest_score"], score)

        flash(f"Your score is {score}/100")
        return redirect(url_for('result', image_index=image_index, uploaded_image=filename, score=score))

    return render_template('upload.html', image_index=image_index, PREDEFINED_IMAGES=PREDEFINED_IMAGES)



@app.route('/result/<int:image_index>')
def result(image_index):
    """Display the result page with comparison between predefined and uploaded images."""
    if image_index < 0 or image_index >= len(PREDEFINED_IMAGES):
        flash("Invalid image index!")
        return redirect(url_for('home'))

    uploaded_image = request.args.get('uploaded_image')
    score = request.args.get('score', type=int)
    predefined_image = PREDEFINED_IMAGES[image_index]

    return render_template('result.html', 
                           predefined_image=predefined_image,
                           uploaded_image=uploaded_image,
                           score=score,
                           image_index=image_index)


if __name__ == '__main__':
    app.run(debug=True)