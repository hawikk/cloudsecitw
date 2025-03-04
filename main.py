from flask import Flask, render_template, request
from google.cloud import aiplatform
from vertexai.preview.generative_models import GenerativeModel
import json
import tempfile

app = Flask(__name__)

def analyze_config(config_data):
    aiplatform.init(project="steel-wall-403114", location="us-central1")
    
    prompt = f"""
    Analyze this cloud configuration JSON for security issues. 
    Provide response in EXACTLY this format:
    
    [SUMMARY]
    {{insert concise 2-3 sentence summary here}}
    
    [ISSUES]
    Issue: {{issue title}}
    Severity: (HIGH/MEDIUM/LOW)
    Description: {{issue description}}
    Recommendation: {{mitigation steps}}
    ---
    Issue: {{next issue}}
    Severity: 
    Description: 
    Recommendation: 
    
    [CONCLUSION]
    {{final recommendations}}
    """
    
    model = GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'config_file' not in request.files:
            return 'No file uploaded', 400
        file = request.files['config_file']
        if file.filename == '':
            return 'No selected file', 400
        try:
            config_data = json.load(file)
            analysis_result = analyze_config(config_data)
            return render_template('report.html', result=analysis_result)
        except json.JSONDecodeError:
            return 'Invalid JSON file', 400
    return render_template('upload.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)