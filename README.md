# Flask Image Comparison Game

This is a Flask-based web application where users upload an image to compare with a predefined reference image. The system calculates a similarity score based on Structural Similarity Index (SSIM) and color histogram comparison.

## Features
- Upload an image and compare it to a predefined reference image.
- Uses SSIM and histogram similarity for comparison.
- Displays an average score if all three images have been compared.
- Flask-based web interface with session handling.

## Installation
### Prerequisites
Ensure you have Python installed on your system.

### Clone the Repository
```sh
git clone <repository-url>
cd <repository-folder>
```

### Install Dependencies
```sh
pip install -r requirements.txt
```

## Usage
### Run the Application
```sh
python app.py
```

### Access the Web App
Open a browser and go to:
```
http://127.0.0.1:5000/
```

## File Structure
```
/
|-- app.py                  # Main Flask application
|-- requirements.txt        # Dependencies list
|-- README.md               # Documentation
|-- static/
|   |-- images/             # Predefined images
|   |-- uploads/            # Uploaded images
|-- templates/
    |-- index.html          # Homepage
    |-- play.html           # Image upload page
    |-- result.html         # Display results
```

## Technologies Used
- **Flask** - Web framework
- **OpenCV** - Image processing
- **NumPy** - Numerical operations
- **scikit-image** - Structural similarity (SSIM)
- **Werkzeug** - Secure file handling
