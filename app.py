from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a strong secret key

# Configure upload folder and allowed file extensions
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def compare_images(image1_path, image2_path):
    # Load images
    img1 = cv2.imread(image1_path)
    img2 = cv2.imread(image2_path)

    # Resize images to the same size
    img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

    # Convert to grayscale for SSIM
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

    # Compute SSIM (ensuring it's within [0,1])
    ssim_score = max(0, ssim(gray1, gray2))

    # Compute color histograms
    hist1 = cv2.calcHist([img1], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
    hist2 = cv2.calcHist([img2], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])

    # Normalize histograms
    hist1 = cv2.normalize(hist1, hist1).flatten()
    hist2 = cv2.normalize(hist2, hist2).flatten()

    # Compute histogram similarity using Bhattacharyya distance
    hist_score = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
    hist_score = 1 - hist_score  # Closer to 1 means more similar

    # Adjust weights (SSIM 40%, Histogram 60%)
    final_score = (ssim_score * 40) + (hist_score * 60)  

    # Normalize to [0,100]
    # final_score = max(0, min(100, final_score * 100))

    # # Mild leniency boost for moderate changes
    if final_score < 80:
        final_score += (100 - final_score) * 0.10  

    return round(final_score, 2)


@app.route('/')
def index():
    """
    Homepage that displays:
      - Simple rules for the game.
      - Three prompt images as clickable cards (each shows its score or '--/100').
      - The navbar shows the average score only if all three have been scored.
    """
    images = [
        {'id': '1', 'filename': 'image1.png'},
        {'id': '2', 'filename': 'image2.png'},
        {'id': '3', 'filename': 'image3.png'}
    ]
    scores = session.get('scores', {})
    average_score = None
    if len(scores) == 3:
        average_score = sum(scores.values()) / 3

    return render_template('index.html', images=images, scores=scores, average_score=average_score)

@app.route('/play/<image_id>', methods=['GET', 'POST'])
def play(image_id):
    mapping = {
        '1': 'image1.png',
        '2': 'image2.png',
        '3': 'image3.png'
    }
    if image_id not in mapping:
        flash("Invalid image selected.")
        return redirect(url_for('index'))

    original_image = mapping[image_id]
    original_image_path = os.path.join('static', 'images', original_image)

    if request.method == 'POST':
        if 'uploaded_image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['uploaded_image']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            uploaded_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(uploaded_path)

            try:
                score = compare_images(original_image_path, uploaded_path)
            except ValueError as e:
                flash(str(e))
                return redirect(request.url)

            scores = session.get('scores', {})
            scores[image_id] = score
            session['scores'] = scores

            average_score = None
            if len(scores) == 3:
                average_score = sum(scores.values()) / 3

            return render_template('result.html',
                                   original_image=url_for('static', filename='images/' + original_image),
                                   uploaded_image=url_for('static', filename='uploads/' + filename),
                                   score=score,
                                   average_score=average_score)
        else:
            flash('Allowed file types are png, jpg, jpeg')
            return redirect(request.url)

    return render_template('play.html',
                           image_id=image_id,
                           original_image=url_for('static', filename='images/' + original_image),
                           average_score=None)

if __name__ == '__main__':
    app.run(debug=True)
