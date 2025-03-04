from flask import Flask, render_template, request, jsonify
import json
import os
from vertexai.preview.generative_models import GenerativeModel
from google.cloud import aiplatform

app = Flask(__name__)

# Initialize Vertex AI

@app.route('/debug')
def debug():
    import sys
    return {
        'cwd': os.getcwd(),
        'listdir': os.listdir('.'),
        'templates_exists': os.path.exists('templates'),
        'templates_content': os.listdir('templates') if os.path.exists('templates') else [],
        'python_version': sys.version,
        'env': dict(os.environ)
    }
    
aiplatform.init(
    project=os.environ.get("GOOGLE_CLOUD_PROJECT", "steel-wall-403114"),
    location=os.environ.get("GOOGLE_CLOUD_REGION", "us-central1")
)

def analyze_config(config_data):
    """Analyze cloud configuration using Vertex AI Gemini"""
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
    
    [CONCLUSION]
    {{list of final recommendations, one per line}}
    """
    
    try:
        # Use Vertex AI Gemini model
        model = GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(prompt)
        print(f"Raw AI Response: {response.text}")
        return response.text
    except Exception as e:
        print(f"Error in AI analysis: {str(e)}")
        raise

def parse_ai_response(response_text):
    """Parse the AI response into structured data"""
    parsed = {
        "summary": "Analysis could not be completed.",
        "issues": [],
        "recommendations": []
    }
    
    try:
        # Split into sections
        sections = response_text.split('[')
        for section in sections:
            if 'SUMMARY]' in section:
                parsed['summary'] = section.split(']', 1)[-1].strip()
            elif 'ISSUES]' in section:
                issues_text = section.split(']', 1)[-1].strip()
                # Split individual issues
                issue_blocks = issues_text.split('---')
                for issue_block in issue_blocks:
                    if not issue_block.strip():
                        continue
                        
                    issue_data = {
                        "title": "Unnamed Issue",
                        "severity": "MEDIUM",
                        "description": "",
                        "recommendation": ""
                    }
                    
                    for line in issue_block.split('\n'):
                        line = line.strip()
                        if not line:
                            continue
                            
                        if line.startswith('Issue:'):
                            issue_data['title'] = line.split(':', 1)[1].strip()
                        elif line.startswith('Severity:'):
                            issue_data['severity'] = line.split(':', 1)[1].strip().upper()
                        elif line.startswith('Description:'):
                            issue_data['description'] = line.split(':', 1)[1].strip()
                        elif line.startswith('Recommendation:'):
                            issue_data['recommendation'] = line.split(':', 1)[1].strip()
                    
                    if any(issue_data.values()):
                        parsed['issues'].append(issue_data)
                        
            elif 'CONCLUSION]' in section:
                conclusion = section.split(']', 1)[-1].strip()
                parsed['recommendations'] = [line.strip() for line in conclusion.split('\n') if line.strip()]
        
        # Fallbacks for empty sections
        if not parsed['issues']:
            parsed['issues'] = [{"title": "No issues found", "severity": "LOW", 
                                "description": "No security issues were identified in the configuration.",
                                "recommendation": "Continue monitoring your configuration regularly."}]
                                
        if not parsed['recommendations']:
            parsed['recommendations'] = ["Keep your cloud configurations up to date with security best practices."]
            
        return parsed
    except Exception as e:
        print(f"Error parsing AI response: {str(e)}")
        return parsed

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main route handling both form display and file upload"""
    if request.method == 'POST':
        # Check if file part exists
        if 'config_file' not in request.files:
            return render_template('upload.html', error="No file part")
            
        file = request.files['config_file']
        if file.filename == '':
            return render_template('upload.html', error="No selected file")
            
        if not file.filename.endswith('.json'):
            return render_template('upload.html', error="File must be JSON format")
            
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
        except Exception as e:
            return render_template('upload.html', error=f"Error analyzing configuration: {str(e)}")
    
    # GET request - show upload form
    return render_template('upload.html')

if __name__ == '__main__':
    # This is used when running locally only
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)), debug=True)
    
    