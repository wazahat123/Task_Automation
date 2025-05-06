from flask import Flask, render_template, request, redirect, url_for, flash
import os
import subprocess

app = Flask(__name__)
app.secret_key = 'your_secret_key'

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index'))

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # Running the automation script and passing the uploaded file path as argument
        result = subprocess.run(
            ["python", "automation.py", filepath], check=True, capture_output=True, text=True
        )
        flash("✅ Task automation completed successfully!")
        print(result.stdout)  # Print output of automation script to console (for debugging)
    except subprocess.CalledProcessError as e:
        flash(f"❌ Automation failed: {e.stderr}")  # Provide the error message from the subprocess
        print(e.stderr)  # Print error output of automation script to console (for debugging)

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
