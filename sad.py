from flask import Flask, request, render_template_string, redirect
from werkzeug.utils import secure_filename
import os
import PyPDF2
import re
import spacy
from PyPDF2 import PdfReader

with open('so.pdf', 'rb') as file:
    reader = PdfReader(file)
    num_pages = len(reader.pages)  # Use len(reader.pages) to get the number of pages
    print(num_pages)



# Initialize Flask app
app = Flask(__name__)

# Initialize the SpaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Folder where files will be saved
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create the upload folder if it doesn't exist
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file types
ALLOWED_EXTENSIONS = {'pdf'}

# Check if the file extension is allowed (PDF only)
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Function to extract text from PDF
def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfFileReader(file)
        text = ""
        for page_num in range(reader.numPages):
            text += reader.getPage(page_num).extract_text()
        return text
    



# Function to extract contact info (phone, email)
def extract_contact_info(text):
    # Phone number regex: match 10 digit numbers
    phone = re.search(r'\b\d{10}\b', text)
    # Email address regex
    email = re.search(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
    # Return the found values or None if not found
    return phone.group() if phone else None, email.group() if email else None

# Function to extract entities (Education and Work Experience) using SpaCy
def extract_entities(text):
    doc = nlp(text)
    education = []
    work_exp = []
    for ent in doc.ents:
        if ent.label_ == "ORG":  # Organizations could be universities or companies
            education.append(ent.text)
        elif ent.label_ == "DATE":  # Dates for employment or education periods
            work_exp.append(ent.text)
    return education, work_exp

# Home route (Upload form)
@app.route('/')
def upload_form():
    return '''
    <h1>Resume Parser</h1>
    <form action="/upload" method="POST" enctype="multipart/form-data">
        <input type="file" name="file" accept="application/pdf">
        <input type="submit" value="Upload Resume">
    </form>
    '''

# Upload and processing route
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if a file is uploaded
    if 'file' not in request.files:
        return "No file uploaded", 400
    
    file = request.files['file']
    
    # Validate the file
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)  # Save the uploaded file
        
        # Extract text from PDF
        text = extract_text_from_pdf(file_path)
        
        # Extract contact info (phone and email)
        phone, email = extract_contact_info(text)
        
        # Extract education and work experience using NLP
        education, work_exp = extract_entities(text)
        
        # Render the results in an HTML template
        return render_template_string('''
        <h1>Extracted Information</h1>
        <p><strong>Name:</strong> Could not extract (requires advanced NLP)</p>
        <p><strong>Email:</strong> {{ email }}</p>
        <p><strong>Phone:</strong> {{ phone }}</p>
        
        <h2>Education</h2>
        <ul>
          {% for edu in education %}
          <li>{{ edu }}</li>
          {% endfor %}
        </ul>
        
        <h2>Work Experience</h2>
        <ul>
          {% for work in work_exp %}
          <li>{{ work }}</li>
          {% endfor %}
        </ul>

        <a href="/">Upload Another Resume</a>
        ''', phone=phone, email=email, education=education, work_exp=work_exp)
    
    return "Invalid file type. Only PDFs are allowed.", 400

if __name__ == '__main__':
    app.run(debug=True)

import os
print(os.getcwd())



