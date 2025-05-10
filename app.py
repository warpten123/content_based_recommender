from flask import Flask, request, jsonify
from flask import Flask
from flask_cors import CORS
from content_based_filtering import ContentBasedFiltering
import os

app = Flask(__name__)
CORS(app) 


@app.route('/')
def hello():
    return "Hello, Flask!"

@app.route('/api/upload_csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not file.filename.endswith('.csv'):
        return jsonify({"error": "Invalid file type. Only CSV allowed."}), 400

    # Save to the root directory of your project
    filepath = os.path.join(os.getcwd(), file.filename)
    print("filepath",filepath)
    file.save(filepath)

    return jsonify({"message": f"File '{file.filename}' uploaded successfully!"})

@app.route('/api/read_csv', methods=['GET'])
def read_csv():
    filepath = os.path.join(os.getcwd(), 'pc_builds_with_prices.csv') 
    

    if not os.path.exists(filepath):
        return jsonify({"error": "pc_builds_with_prices.csv not found in the root directory."}), 404

    try:
        cb = ContentBasedFiltering(filepath)
        cb.read_csv_file()
        cb.generate_build_matrix()
        return jsonify({"message": "Build Matrix Successfully Created"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/load_csv', methods=['GET'])
def load_csv():
    loadPath = os.path.join(os.getcwd(), 'build_matrix.csv')
    if not os.path.exists(loadPath):
        return jsonify({"error": "build_matrix.csv not found in the root directory."}), 404
    try:
        cb = ContentBasedFiltering(loadPath)
        load_csv = cb.load_csv(loadPath)
        return jsonify({"data": load_csv})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/generate_recom', methods=['POST'])
def generate_recom():
    try:
        # Get user vector from JSON request
        user_input = request.get_json()
        user_vector = user_input.get('user_vector')

        if not user_vector or not isinstance(user_vector, list):
            return jsonify({"error": "Invalid or missing 'user_vector' in request body."}), 400

        # Initialize recommender and get recommendations
        cb = ContentBasedFiltering('build_matrix.csv')  # assumes it handles loading internally
        recommendations = cb.generate_recommendations(user_vector)

        return jsonify({"recommendations": recommendations})

    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == '__main__':
    app.run(debug=True)