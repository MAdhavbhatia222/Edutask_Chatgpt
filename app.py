from flask import Flask, request, render_template, redirect, url_for
import os,shutil
import subprocess
import pandas as pd
from io import StringIO

app = Flask(__name__)
UPLOAD_FOLDER = 'source_documents'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT'] = "<p>Start by uploading a file to generate tasks.</p>"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def clear_directory(directory):
    """
    Removes all files and subdirectories within the specified directory.

    Parameters:
    - directory (str): The path to the directory to clear.
    """
    if os.path.exists(directory):
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)  # Remove the file
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)  # Remove the directory
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')



def run_script(filepaths):
    db_path = os.getcwd()
    script_path = os.path.join(db_path, 'OpenAI_Template.py')
    # Prepare the command with multiple file paths
    command = ['python', script_path] + filepaths
    result = subprocess.run(command, capture_output=True, text=True)
    print("###########result.stdout#############")
    print(result.stdout)
    print("###########result.stderr#############")  # Check for errors
    print(result.stderr)
    return result.stdout
    
def attempt_to_parse_csv(output):
    try:
        df_output = output.split('###############################')[-1].strip()
        print("###########df_output#############")
        print(df_output)
        if df_output:
            df = pd.read_csv(StringIO(df_output))
            print("###########df#############")
            print(df)
            html_table = df.to_html(index=False, border=0, classes='table table-striped')
            print("###########html_table#############")
            print(html_table)
            return html_table
    except pd.errors.EmptyDataError:
        pass
    return None

@app.route('/')
def home():
    return redirect(url_for('generate'))

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if request.method == 'POST':
        if 'files[]' not in request.files:
            print("No file part.")
            return redirect(request.url)
        
        files = request.files.getlist('files[]')

        if not files or files[0].filename == '':
            print("No selected file")
            return redirect(request.url)

        # Clear the directories before saving new files
        clear_directory(os.path.join(os.getcwd(), 'db'))
        clear_directory(app.config['UPLOAD_FOLDER'])

        filepaths = []  # Store file paths
        for file in files:
            if file and allowed_file(file.filename):
                filename = file.filename
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                print(f"Saving file to {filepath}")
                file.save(filepath)
                filepaths.append(filepath)

        if filepaths:
            output = run_script(filepaths)
            try:
                html_table_parsed = attempt_to_parse_csv(output)
            except Exception as e:
                print(e)
                html_table_parsed = "<p>Could not process files. Please check the formats and try again.</p>"
            app.config['OUTPUT'] = html_table_parsed

        return redirect(url_for('output'))
    return render_template('upload_form.html')

@app.route('/output')
def output():
    html_table = app.config['OUTPUT']
    if html_table:
        return render_template('output_display.html', html_table=html_table)
    else:
        html_table = "<p>Uh-oh! Seems like an issue. Try Refresh or Please try again. I support following formats: txt, pdf, 'doc', 'docx'.</p>"
        return render_template('output_display.html', html_table=html_table)

if __name__ == '__main__':
   app.run(debug=True, port=3000)