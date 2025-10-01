# app.py (Production version for Render)

import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import json
from werkzeug.utils import secure_filename
import random
import time

app = Flask(**name**)
CORS(app)

# Configuration

app.config[‘MAX_CONTENT_LENGTH’] = 50 * 1024 * 1024  # 50MB max file size
app.config[‘UPLOAD_FOLDER’] = ‘static/uploads’
ALLOWED_EXTENSIONS = {‘png’, ‘jpg’, ‘jpeg’, ‘gif’, ‘heic’, ‘webp’}

# Create upload folder if it doesn’t exist

os.makedirs(app.config[‘UPLOAD_FOLDER’], exist_ok=True)
os.makedirs(‘templates’, exist_ok=True)

# Data storage

DATA_FILE = ‘wardrobe_data.json’

def allowed_file(filename):
return ‘.’ in filename and filename.rsplit(’.’, 1)[1].lower() in ALLOWED_EXTENSIONS

def load_data():
“”“Load data from JSON file”””
if os.path.exists(DATA_FILE):
try:
with open(DATA_FILE, ‘r’) as f:
return json.load(f)
except (json.JSONDecodeError, FileNotFoundError):
pass
return {
‘shirts’: [],
‘pants’: [],
‘combinations’: [],
‘preferences’: {},
‘weekly_outfits’: []
}

def save_data(data):
“”“Save data to JSON file”””
try:
with open(DATA_FILE, ‘w’) as f:
json.dump(data, f, indent=2)
except Exception as e:
print(f”Error saving data: {e}”)

@app.route(’/’)
def index():
“”“Serve the HTML file”””
return render_template(‘index.html’)

@app.route(’/manifest.json’)
def manifest():
“”“Serve PWA manifest”””
return jsonify({
“name”: “Wardrobe Manager”,
“short_name”: “Wardrobe”,
“description”: “Personal outfit combination manager”,
“start_url”: “/”,
“display”: “standalone”,
“background_color”: “#f8f9fa”,
“theme_color”: “#2c3e50”,
“icons”: [
{
“src”: “data:image/svg+xml,%3Csvg xmlns=‘http://www.w3.org/2000/svg’ viewBox=‘0 0 192 192’%3E%3Crect fill=’%232c3e50’ width=‘192’ height=‘192’/%3E%3Ctext y=‘130’ font-size=‘100’ fill=‘white’%3E👔%3C/text%3E%3C/svg%3E”,
“sizes”: “192x192”,
“type”: “image/svg+xml”
}
]
})

@app.route(’/api/data’, methods=[‘GET’])
def get_data():
“”“Get all wardrobe data”””
return jsonify(load_data())

@app.route(’/api/upload/<clothing_type>’, methods=[‘POST’])
def upload_clothing(clothing_type):
“”“Upload clothing images”””
try:
if clothing_type not in [‘shirts’, ‘pants’]:
return jsonify({‘error’: ‘Invalid clothing type’}), 400

```
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400
    
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No files selected'}), 400
    
    # Ensure upload directory exists
    upload_dir = app.config['UPLOAD_FOLDER']
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    
    data = load_data()
    uploaded_items = []
    
    for file in files:
        if file and file.filename and allowed_file(file.filename):
            try:
                # Generate unique filename
                filename = secure_filename(file.filename)
                if not filename:
                    filename = f"image_{random.randint(1000, 9999)}.jpg"
                
                timestamp = str(int(time.time() * 1000))
                unique_filename = f"{timestamp}_{filename}"
                filepath = os.path.join(upload_dir, unique_filename)
                
                # Save file
                file.save(filepath)
                
                # Verify file was saved
                if not os.path.exists(filepath):
                    continue
                
                # Add to data
                item = {
                    'id': f"{timestamp}_{random.randint(1000, 9999)}",
                    'filename': unique_filename,
                    'url': f"/static/uploads/{unique_filename}",
                    'original_name': file.filename
                }
                data[clothing_type].append(item)
                uploaded_items.append(item)
                
            except Exception as file_error:
                print(f"Error saving file {file.filename}: {file_error}")
                continue
    
    if not uploaded_items:
        return jsonify({'error': 'No valid files could be uploaded'}), 400
    
    save_data(data)
    return jsonify({
        'success': True,
        'items': uploaded_items,
        'total': len(data[clothing_type])
    })
    
except Exception as e:
    print(f"Upload error: {e}")
    return jsonify({'error': f'Upload failed: {str(e)}'}), 500
```

@app.route(’/api/remove/<clothing_type>/<item_id>’, methods=[‘DELETE’])
def remove_clothing(clothing_type, item_id):
“”“Remove a clothing item”””
if clothing_type not in [‘shirts’, ‘pants’]:
return jsonify({‘error’: ‘Invalid clothing type’}), 400

```
data = load_data()

# Find and remove item
items = data[clothing_type]
data[clothing_type] = [item for item in items if item['id'] != item_id]

# Remove file
for item in items:
    if item['id'] == item_id:
        try:
            filepath = os.path.join('static', 'uploads', item['filename'])
            if os.path.exists(filepath):
                os.remove(filepath)
        except:
            pass
        break

save_data(data)
return jsonify({'success': True})
```

@app.route(’/api/clear/<clothing_type>’, methods=[‘DELETE’])
def clear_clothing(clothing_type):
“”“Clear all items of a type”””
if clothing_type not in [‘shirts’, ‘pants’]:
return jsonify({‘error’: ‘Invalid clothing type’}), 400

```
data = load_data()

# Remove files
for item in data[clothing_type]:
    try:
        filepath = os.path.join('static', 'uploads', item['filename'])
        if os.path.exists(filepath):
            os.remove(filepath)
    except:
        pass

# Clear data
data[clothing_type] = []
save_data(data)

return jsonify({'success': True})
```

@app.route(’/api/generate_combinations’, methods=[‘POST’])
def generate_combinations():
“”“Generate all combinations”””
data = load_data()

```
if not data['shirts'] or not data['pants']:
    return jsonify({'error': 'Need at least one shirt and one pair of pants'}), 400

# Generate combinations
combinations = []
for shirt in data['shirts']:
    for pants in data['pants']:
        combinations.append({
            'id': f"{shirt['id']}_{pants['id']}",
            'shirt': shirt,
            'pants': pants
        })

data['combinations'] = combinations
save_data(data)

return jsonify({
    'success': True,
    'count': len(combinations),
    'combinations': combinations
})
```

@app.route(’/api/rate’, methods=[‘POST’])
def rate_combination():
“”“Rate a combination”””
rating_data = request.json
combo_id = rating_data.get(‘combination_id’)
liked = rating_data.get(‘liked’)

```
if combo_id is None or liked is None:
    return jsonify({'error': 'Invalid data'}), 400

data = load_data()
if 'preferences' not in data:
    data['preferences'] = {}

data['preferences'][combo_id] = liked
save_data(data)

return jsonify({'success': True})
```

@app.route(’/api/generate_weekly’, methods=[‘POST’])
def generate_weekly():
“”“Generate weekly plan using backtracking algorithm”””
data = load_data()
preferences = data.get(‘preferences’, {})
combinations = data.get(‘combinations’, [])

```
# Get liked combinations
liked_combos = [
    combo for combo in combinations
    if preferences.get(combo['id']) == True
]

if len(liked_combos) < 7:
    return jsonify({'error': f'Need at least 7 liked combinations (have {len(liked_combos)})'}), 400

# Backtracking algorithm to find 7 non-repeating outfits
def find_weekly_outfits(liked_combos, max_attempts=1000):
    best_solution = []
    
    for attempt in range(max_attempts):
        shuffled = liked_combos.copy()
        random.shuffle(shuffled)
        
        solution = []
        used_shirts = set()
        used_pants = set()
        
        def backtrack(index):
            nonlocal solution, used_shirts, used_pants
            
            if len(solution) == 7:
                return True
            
            for i in range(index, len(shuffled)):
                combo = shuffled[i]
                shirt_id = combo['shirt']['id']
                pants_id = combo['pants']['id']
                
                if shirt_id not in used_shirts and pants_id not in used_pants:
                    solution.append(combo)
                    used_shirts.add(shirt_id)
                    used_pants.add(pants_id)
                    
                    if backtrack(i + 1):
                        return True
                    
                    solution.pop()
                    used_shirts.remove(shirt_id)
                    used_pants.remove(pants_id)
            
            return False
        
        if backtrack(0):
            return solution
        
        if len(solution) > len(best_solution):
            best_solution = solution
    
    return best_solution

weekly_outfits = find_weekly_outfits(liked_combos)

if len(weekly_outfits) < 7:
    return jsonify({'error': 'Could not generate 7 unique outfits'}), 400

data['weekly_outfits'] = weekly_outfits
save_data(data)

return jsonify({
    'success': True,
    'outfits': weekly_outfits
})
```

@app.route(’/api/analytics’, methods=[‘GET’])
def get_analytics():
“”“Get analytics data”””
data = load_data()
preferences = data.get(‘preferences’, {})

```
# Calculate statistics
liked_count = sum(1 for v in preferences.values() if v == True)
disliked_count = sum(1 for v in preferences.values() if v == False)

# Calculate performance for each item
shirt_performance = []
for shirt in data['shirts']:
    liked = 0
    total = len(data['pants'])
    for pants in data['pants']:
        combo_id = f"{shirt['id']}_{pants['id']}"
        if preferences.get(combo_id) == True:
            liked += 1
    
    shirt_performance.append({
        'item': shirt,
        'liked': liked,
        'total': total,
        'performance': (liked / total * 100) if total > 0 else 0
    })

pants_performance = []
for pants in data['pants']:
    liked = 0
    total = len(data['shirts'])
    for shirt in data['shirts']:
        combo_id = f"{shirt['id']}_{pants['id']}"
        if preferences.get(combo_id) == True:
            liked += 1
    
    pants_performance.append({
        'item': pants,
        'liked': liked,
        'total': total,
        'performance': (liked / total * 100) if total > 0 else 0
    })

# Sort by performance (worst first)
shirt_performance.sort(key=lambda x: x['performance'])
pants_performance.sort(key=lambda x: x['performance'])

return jsonify({
    'stats': {
        'shirts': len(data['shirts']),
        'pants': len(data['pants']),
        'combinations': len(data['shirts']) * len(data['pants']),
        'liked': liked_count,
        'disliked': disliked_count
    },
    'shirt_performance': shirt_performance,
    'pants_performance': pants_performance
})
```

@app.route(’/static/uploads/<filename>’)
def uploaded_file(filename):
“”“Serve uploaded files”””
return send_from_directory(app.config[‘UPLOAD_FOLDER’], filename)

if **name** == ‘**main**’:
port = int(os.environ.get(‘PORT’, 5000))
app.run(host=‘0.0.0.0’, port=port)
