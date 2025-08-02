import os
import json
from flask import Flask, render_template, jsonify, send_from_directory
from datetime import datetime

app = Flask(__name__)

def get_result_files():
    """Get all JSON result files from outputs directory"""
    outputs_dir = "outputs"
    if not os.path.exists(outputs_dir):
        return []
    
    files = []
    for filename in os.listdir(outputs_dir):
        if filename.endswith('.json') and filename.startswith('results-'):
            filepath = os.path.join(outputs_dir, filename)
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    files.append({
                        'filename': filename,
                        'timestamp': data.get('timestamp', 'Unknown'),
                        'models_count': len(data.get('results', [])),
                        'filepath': filepath
                    })
            except Exception as e:
                print(f"Error reading {filename}: {e}")
                continue
    
    # Sort by timestamp descending
    files.sort(key=lambda x: x['timestamp'], reverse=True)
    return files

@app.route('/')
def index():
    """Main page"""
    files = get_result_files()
    return render_template('index.html', files=files)

@app.route('/api/files')
def api_files():
    """API endpoint to get all result files"""
    return jsonify(get_result_files())

@app.route('/api/file/<path:filename>')
def api_file(filename):
    """API endpoint to get specific file content"""
    filepath = os.path.join("outputs", filename)
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
        return jsonify(data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)