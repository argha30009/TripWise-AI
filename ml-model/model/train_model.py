import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import os

def generate_sample_data():
    """Generate sample training data for the budget prediction model"""
    np.random.seed(42)
    
    categories = ['food', 'accommodation', 'transportation', 'entertainment', 'shopping', 'other']
    
    # Generate 1000 sample expense records
    data = []
    for _ in range(1000):
        category = np.random.choice(categories)
        
        # Different spending patterns based on category
        if category == 'accommodation':
            amount = np.random.normal(150, 50)
        elif category == 'transportation':
            amount = np.random.normal(80, 30)
        elif category == 'food':
            amount = np.random.normal(45, 20)
        elif category == 'entertainment':
            amount = np.random.normal(60, 25)
        elif category == 'shopping':
            amount = np.random.normal(70, 35)
        else:  # other
            amount = np.random.normal(40, 20)
        
        amount = max(5, amount)  # Ensure positive amounts
        
        trip_duration = np.random.randint(1, 15)
        budget = np.random.randint(500, 3000)
        days_elapsed = np.random.randint(1, trip_duration + 1)
        
        data.append({
            'category': category,
            'amount': amount,
            'trip_duration': trip_duration,
            'budget': budget,
            'days_elapsed': days_elapsed,
            'total_spent_so_far': amount * np.random.uniform(0.5, 2.0)
        })
    
    return pd.DataFrame(data)

def train_model():
    """Train the budget prediction model"""
    print("Generating sample data...")
    df = generate_sample_data()
    
    # Encode categorical variables
    le_category = LabelEncoder()
    df['category_encoded'] = le_category.fit_transform(df['category'])
    
    # Features for prediction
    features = ['category_encoded', 'trip_duration', 'budget', 'days_elapsed', 'total_spent_so_far']
    X = df[features]
    
    # Target: predict remaining spending
    y = df['budget'] - df['total_spent_so_far']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    print("Training model...")
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # Evaluate
    score = model.score(X_test, y_test)
    print(f"Model R² score: {score:.3f}")
    
    # Save model and encoder

    model_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(model_dir, '..', 'budget_model.pkl')
    encoder_path = os.path.join(model_dir, '..', 'label_encoder.pkl')
    
    joblib.dump(model, model_path)
    joblib.dump(le_category, encoder_path)
    
    print(f"Model saved to {model_path}")
    print(f"Label encoder saved to {encoder_path}")
    
    return model, le_category

if __name__ == "__main__":
    train_model()
