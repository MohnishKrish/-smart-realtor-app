from flask import Flask, render_template, request, redirect, session, url_for, jsonify
import mysql.connector
from datetime import timedelta, datetime
import os
import joblib
import json
import pandas as pd

# ------------ CONFIG ------------
app = Flask(__name__)
app.secret_key = 'change_this_to_a_random_secret_!!!'
app.permanent_session_lifetime = timedelta(days=30)

# MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="moni1612",
    database="login_system"
)
cursor = db.cursor(dictionary=True)

# Load model
MODEL_PATH = os.path.join("model", "model.pkl")
COLUMNS_PATH = os.path.join("model", "columns.json")
model = None
model_columns = None

if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)

if os.path.exists(COLUMNS_PATH):
    with open(COLUMNS_PATH, "r") as f:
        model_columns = json.load(f)

# Location coords
LOCATION_COORDS = {
    "Mumbai": [19.0760, 72.8777],
    "Delhi": [28.7041, 77.1025],
    "Bangalore": [12.9716, 77.5946],
    "Chennai": [13.0827, 80.2707],
    "Kolkata": [22.5726, 88.3639]
}



# ------------ ROUTES ------------

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        u = request.form['username']
        p = request.form['password']

        cursor.execute("SELECT * FROM users WHERE username=%s", (u,))
        if cursor.fetchone():
            return render_template('signup.html', error="Username exists")

        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (u, p))
        db.commit()
        return redirect(url_for('home'))

    return render_template('signup.html')



@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()

    if user:
        session['user_id'] = user['id']
        session['username'] = user['username']
        return redirect(url_for('dashboard'))

    return render_template('login.html', error="Invalid Login")



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))



@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    uid = session['user_id']

    # Only recent (unsaved) predictions
    cursor.execute("""
        SELECT * FROM predictions 
        WHERE user_id=%s AND is_saved=0
        ORDER BY created_at DESC
        LIMIT 10
    """, (uid,))
    recent = cursor.fetchall()

    # Trend graph
    cursor.execute("""
        SELECT DATE_FORMAT(created_at, '%Y-%m') AS month, AVG(predicted_price) AS avg_price
        FROM predictions
        WHERE user_id=%s
        GROUP BY month
        ORDER BY month
        LIMIT 12
    """, (uid,))
    rows = cursor.fetchall()

    trend_months = [r['month'] for r in rows]
    trend_prices = [round(r['avg_price'], 2) for r in rows]

    return render_template(
        'dashboard.html',
        username=session['username'],
        recent=recent,
        trend_months=trend_months,
        trend_prices=trend_prices,
        coords=[20.5937, 78.9629],
        locations=list(LOCATION_COORDS.keys())
    )



@app.route('/predict', methods=['POST'])
def predict():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    data = request.form

    location = data.get('location')
    sqft = int(data.get('sqft') or 0)
    bedrooms = int(data.get('bedrooms') or 0)
    bathrooms = int(data.get('bathrooms') or 0)
    property_type = data.get('property_type')
    age_years = int(data.get('age_years') or 0)

    # MODEL PREDICTION
    predicted_price = None

    if model and model_columns:
        X = pd.DataFrame(columns=model_columns)
        X.loc[0] = 0

        if 'sqft' in X.columns: X.at[0, 'sqft'] = sqft
        if 'bedrooms' in X.columns: X.at[0, 'bedrooms'] = bedrooms
        if 'bathrooms' in X.columns: X.at[0, 'bathrooms'] = bathrooms
        if 'age_years' in X.columns: X.at[0, 'age_years'] = age_years

        loc_col = f"loc_{location}"
        if loc_col in X.columns: X.at[0, loc_col] = 1

        type_col = f"ptype_{property_type}"
        if type_col in X.columns: X.at[0, type_col] = 1

        try:
            predicted_price = float(model.predict(X)[0])
        except:
            predicted_price = None

    # FALLBACK FORMULA
    if predicted_price is None:
        base = {'Mumbai':40000,'Delhi':30000,'Bangalore':25000,'Chennai':18000,'Kolkata':15000}
        ppsq = base.get(location,15000)
        predicted_price = sqft * ppsq

    predicted_price = round(predicted_price, 2)

    # INSERT INTO DB
    cursor2 = db.cursor()
    cursor2.execute("""
        INSERT INTO predictions
        (user_id, location, sqft, bedrooms, bathrooms, property_type, age_years, predicted_price, is_saved)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,0)
    """, (
        session['user_id'],
        location, sqft, bedrooms, bathrooms, property_type, age_years, predicted_price
    ))
    db.commit()

    # FETCH UPDATED RECENT PREDICTIONS
    cursor.execute("""
        SELECT * FROM predictions
        WHERE user_id=%s AND is_saved=0
        ORDER BY created_at DESC
        LIMIT 10
    """, (session['user_id'],))
    recent = cursor.fetchall()

    # RENDER DASHBOARD WITH PREDICTED PRICE
    return render_template(
        'dashboard.html',
        username=session['username'],
        recent=recent,
        predicted_price=predicted_price,
        trend_months=[],
        trend_prices=[],
        coords=LOCATION_COORDS.get(location, [20.5937, 78.9629]),
        locations=list(LOCATION_COORDS.keys())
    )


@app.route('/save_prediction', methods=['POST'])
def save_prediction():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    prediction_id = request.form.get("id")

    cursor2 = db.cursor()
    cursor2.execute("""
        UPDATE predictions
        SET is_saved = 1
        WHERE id=%s AND user_id=%s
    """, (prediction_id, session['user_id']))
    db.commit()

    return redirect(url_for('saved'))



@app.route('/saved')
def saved():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    cursor.execute("""
        SELECT * FROM predictions
        WHERE user_id=%s AND is_saved=1
        ORDER BY created_at DESC
    """, (session['user_id'],))
    saved_rows = cursor.fetchall()

    return render_template('saved.html', saved=saved_rows, username=session['username'])



if __name__ == "__main__":
    app.run(debug=True)