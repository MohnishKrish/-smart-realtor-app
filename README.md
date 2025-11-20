# -smart-realtor-app
Smart Realtor is an AI-powered real estate price prediction app built with Flask and machine learning. Users can predict house prices based on location, size, BHK, and property features, view recent predictions, and save favorites. Includes interactive charts, maps, and a clean dashboard UI.
# 🏡 Smart Realtor – AI House Price Prediction App

Smart Realtor is an AI-powered real estate price prediction web application built using **Flask**, **Machine Learning**, and **MySQL**.  
It predicts house prices based on key property features such as **location**, **square feet**, **BHK**, **bathrooms**, **property type**, and **age of the property**.

The app features an interactive dashboard, recent predictions history, saved predictions (favorites), and visual trend charts.  
Designed for fast, accurate, and user-friendly real estate insights.

---

## 🚀 Features

### 🔹 **AI-Powered Price Prediction**
- ML model predicts house prices accurately.
- Supports multiple cities and property configurations.

### 🔹 **Interactive Dashboard**
- Clean UI with charts (Chart.js)
- Map integration (Leaflet.js)
- Latest prediction displayed instantly

### 🔹 **Recent Predictions**
- Every prediction is stored automatically in the database  
- Shows **only unsaved** predictions on the dashboard

### 🔹 **Saved Predictions (Favorites)**
- Users can save important predictions  
- Saved predictions remain **permanently**, even after logout  
- Clean separation between recent and saved items

### 🔹 **User Authentication**
- Signup, Login, Logout  
- Session-based authentication

---

## 🛠️ Tech Stack

### **Backend**
- Python (Flask)
- MySQL
- Joblib (ML model loading)
- Pandas

### **Frontend**
- HTML / CSS
- Chart.js (Graphs)
- Leaflet.js (Maps)
- Vanilla JS

### **Machine Learning**
- Scikit-learn regression model
- Encoded categorical features
- Trained using housing dataset

---

## 📂 Project Structure
smart-realtor/
│
├── app.py                 # Main Flask backend
├── model/
│   ├── model.pkl          # Trained ML model
│   └── columns.json       # Model feature names
│
├── templates/
│   ├── dashboard.html     # Dashboard page
│   ├── saved.html         # Saved predictions
│   ├── login.html
│   └── signup.html
│
├── static/
│   ├── dashboard.css      # Stylesheet
│   └── dashboard.js       # JS for charts & maps



