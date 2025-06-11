# Predicting Food Delivery Time using Machine Learning

This project aims to develop a predictive model that accurately estimates food delivery time using the **Zomato Delivery Operations Analytics Dataset**. With over 45,000 records and 20 features—including weather conditions, traffic density, vehicle details, and geographic coordinates—this project uses machine learning techniques to improve delivery route optimization and enhance customer satisfaction.

---

## 📌 **Objective**

- Build a predictive model to estimate food delivery times.
- Identify key factors influencing delivery time (e.g., weather, traffic, vehicle condition).
- Help restaurants and delivery platforms optimize logistics and improve efficiency.
- Provide insights into how external factors impact delivery durations.

---

## 📊 **Dataset Overview**

**Dataset Source:** Kaggle  
**Dataset Name:** Zomato Delivery Dataset  
**Size:** 45,584 rows × 20 columns

**Features include:**

- Delivery person details (age, ratings)
- Order & delivery timestamps
- Weather and traffic conditions
- Vehicle and order type
- Location coordinates (restaurant and delivery point)
- Time taken for delivery (target variable)

---

## 🧹 **Phase 1: Data Cleaning & Preprocessing**

- Dropped irrelevant columns: `ID`, `Delivery_person_ID`, `Order_Date`, `Time_Ordered`, `Time_Order_Picked`
- Removed rows with missing values
- Created a new column: `Haversine_Distance_km` to represent delivery distance
- Removed the 4 raw coordinate columns after calculating distance
- Detected and removed outliers using:
  - Distance threshold (>25 km)
  - Speed thresholds by city type
  - Rare rating values (e.g., 2.5–3.4)
- Performed sampling to reduce dataset to 5,000 rows while retaining key minority cases (`Festival=Yes`, `City=Semi-Urban`, `Multiple_deliveries=3.0`)

---

## 🧠 **Phase 2: Feature Engineering & Modeling**

### 🔸 **Encoding**
- OneHotEncoder: `weather_conditions`, `type_of_order`, `type_of_vehicle`, `city`
- LabelEncoder: `festival`

### 🔸 **Feature Selection**
Used two techniques to identify the top predictive features:
- Random Forest Feature Importances
- Permutation Feature Importances

**Top Features Selected:**
- `haversine_Distance_km`, `festival`, `road_traffic_density`, `delivery_person_ratings`, `delivery_person_age`, `vehicle_condition`, `multiple_deliveries`, and selected one-hot encoded weather/city columns

### 🔸 **Model Building**
Models tested:
- Linear Regression
- SVR
- Decision Tree
- Random Forest
- Gradient Boosting
- XGBoost

**Evaluation Metrics Used:**
- MAE (Mean Absolute Error)
- RMSE (Root Mean Squared Error)
- R² Score

**Best Performing Models (Pre-Tuning):**
1. Random Forest – R²: 0.8999
2. XGBoost – R²: 0.8888
3. Gradient Boosting – R²: 0.8774

### 🔸 **Hyperparameter Tuning**
Used `GridSearchCV` with 5-fold CV to tune top 3 models.

**Final Results (Post-Tuning):**
- **Random Forest:** MAE = 2.86, RMSE = 3.60, R² = 0.9045
- **XGBoost:** MAE = 2.91, R² = 0.9036
- **Gradient Boosting:** MAE = 2.93, R² = 0.9032

---

## ⚖️ **Model Comparison**

Performed **paired t-tests** on cross-validated MAEs to compare models:

- Random Forest vs Gradient Boosting: *Significant* (p = 0.0057)
- Random Forest vs XGBoost: *Not significant* (p = 0.5385)
- Gradient Boosting vs XGBoost: *Not significant* (p = 0.3946)

**Conclusion:**  
Random Forest statistically outperformed Gradient Boosting and slightly outperformed XGBoost, making it the most reliable choice.

---

## ✅ **Conclusion**

This project successfully developed a highly accurate predictive model to estimate food delivery time. The insights derived from the data (e.g., importance of distance, traffic, festivals) provide actionable intelligence for optimizing delivery operations in the food industry. The final Random Forest model achieved over **90% accuracy**, indicating strong performance and generalizability.

---

## 📂 **Technologies Used**

- Python (Pandas, NumPy, Scikit-learn, XGBoost)
- Jupyter Notebook
- Matplotlib, Seaborn (for visualization)
- Haversine Formula (for geo-distance calculation)
- GridSearchCV for hyperparameter tuning

---

## 📌 **Author**

Developed by [Mohamed Sahad M]  
Connect with me on [LinkedIn](https://www.linkedin.com/in/mohamed-sahad-m-96b038200/)  
