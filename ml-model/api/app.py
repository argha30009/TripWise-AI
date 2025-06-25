from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import numpy as np
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# Load model and encoder
model_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(model_dir, '..', 'budget_model.pkl')
encoder_path = os.path.join(model_dir, '..', 'label_encoder.pkl')

try:
    model = joblib.load(model_path)
    label_encoder = joblib.load(encoder_path)
    print("Model and encoder loaded successfully")
except:
    print("Model files not found. Please train the model first.")
    model = None
    label_encoder = None

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        expenses = data.get('expenses', [])
        budget = data.get('budget', 1000)
        trip_duration = data.get('trip_duration', 7)
        
        if not expenses:
            return jsonify({
                'predicted_spending': budget * 0.8,
                'budget_status': 'on_track',
                'recommendations': ['Start tracking expenses for better predictions']
            })
        
        # Calculate current spending
        total_spent = sum(expense['amount'] for expense in expenses)
        days_elapsed = len(set(expense['date'][:10] for expense in expenses))
        
        # Simple prediction if model not available
        if model is None:
            daily_average = total_spent / max(1, days_elapsed)
            predicted_total = daily_average * trip_duration
            
            status = 'on_track'
            if predicted_total > budget:
                status = 'over_budget'
            elif predicted_total < budget * 0.7:
                status = 'under_budget'
            
            recommendations = [
                f"Based on current spending, you might spend ${predicted_total:.2f} total",
                f"Your daily average is ${daily_average:.2f}",
                "Consider setting daily spending limits" if status == 'over_budget' else "You're doing great with your budget!"
            ]
            
            return jsonify({
                'predicted_spending': predicted_total,
                'budget_status': status,
                'recommendations': recommendations
            })
        
        # Use ML model for prediction
        # ... (ML prediction logic would go here)
        
        return jsonify({
            'predicted_spending': total_spent * 1.2,
            'budget_status': 'on_track',
            'recommendations': ['Keep tracking your expenses!']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ML service is running'})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
