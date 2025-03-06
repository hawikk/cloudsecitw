from flask import Flask, render_template, request
import json
import os
from vertexai.preview.generative_models import GenerativeModel
from google.cloud import aiplatform

app = Flask(__name__)

# Initialize Vertex AI
# Requires GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_REGION environment variables
aiplatform.init(
    project=os.environ.get("GOOGLE_CLOUD_PROJECT"),
    location=os.environ.get("GOOGLE_CLOUD_REGION")
)


def analyze_config(config_data):
    """Analyze cloud configuration using Vertex AI Gemini"""
    # Structured prompt to enforce consistent response format
    prompt = f"""
    You are a cloud security expert. Analyze this cloud configuration JSON for security issues.
    
    CONFIGURATION:
    {json.dumps(config_data, indent=2)}
    
    Provide response in EXACTLY this format:
    
    [SUMMARY]
    {{insert concise 2-3 sentence summary here}}
    
    [ISSUES]
    Issue: {{issue title}}
    Severity: (HIGH|MEDIUM|LOW)
    Description: {{detailed issue description}}
    Recommendation: {{specific mitigation steps}}
    ---
    Issue: {{next issue title}}
    Severity: (HIGH|MEDIUM|LOW)
    Description: {{detailed issue description}}
    Recommendation: {{specific mitigation steps}}
    """
    # Use Vertex AI Gemini model
    model = GenerativeModel("gemini-2.0-flash-001")
    response = model.generate_content(prompt)
    return response.text
def parse_ai_response(response_text):
    """Parse the AI response into structured data"""
    # Initialize with default values in case parsing fails
    parsed = {
        "summary": "Analysis could not be completed.",
        "issues": [],
        "recommendations": []
    }
    # Split response into sections using bracket notation
    sections = response_text.split('[')
    for section in sections:
        # Handle summary section
        if 'SUMMARY]' in section:
            # Extract text after SUMMARY] marker
            parsed['summary'] = section.split(']', 1)[-1].strip()
        # Handle issues section 
        elif 'ISSUES]' in section:
            issues_text = section.split(']', 1)[-1].strip()
            # Split individual issues separated by horizontal rule
            issue_blocks = issues_text.split('---')
            for issue_block in issue_blocks:
                # Skip empty blocks from accidental splits
                if not issue_block.strip():
                    continue
                
                # Initialize with default values
                issue_data = {
                    "title": "Unnamed Issue",
                    "severity": "MEDIUM", # Default to medium if missing
                    "description": "",
                    "recommendation": ""
                }
                # Parse each line of the issue block
                for line in issue_block.split('\n'):
                    line = line.strip()
                    if not line:
                        continue # Skip empty lines
                    
                    # Extract each field using startswith matching
                    # This is safer than split in case of colons in values
                    if line.startswith('Issue:'):
                        issue_data['title'] = line.split(':', 1)[1].strip()
                    elif line.startswith('Severity:'):
                        # Force uppercase to maintain consistency
                        issue_data['severity'] = line.split(':', 1)[1].strip().upper()
                    elif line.startswith('Description:'):
                        issue_data['description'] = line.split(':', 1)[1].strip()
                    elif line.startswith('Recommendation:'):
                        issue_data['recommendation'] = line.split(':', 1)[1].strip()
                # Only add issue if at least one field has content
                if any(issue_data.values()):
                    parsed['issues'].append(issue_data)
    return parsed

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route handling both form display and file upload"""
    if request.method == 'POST':
        file = request.files['config_file']
        try:
            # Parse JSON file
            config_data = json.load(file)
            
            # Analyze configuration
            analysis_result = analyze_config(config_data)
            
            # Parse the AI response
            parsed_result = parse_ai_response(analysis_result)
            
            # Render report
            return render_template('report.html', result=parsed_result)
        except json.JSONDecodeError:
            return render_template('upload.html', error="Invalid JSON file format")
        
    # GET request - show upload form
    return render_template('upload.html')
    
    