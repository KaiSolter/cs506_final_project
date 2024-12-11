import pandas as pd
import numpy
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score

data = pd.read_csv('final_report/cleaned.csv')

# our features
X = data.drop(columns=['game_result', 'user_id', 'op_id'])

#our label
y = data['game_result']   # the last column

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)


# Train the Random Forest model with predefined parameters
rf = RandomForestClassifier(n_estimators=300, max_depth=12, random_state=42)
rf.fit(X_train, y_train)


# Make predictions
y_pred = rf.predict(X_test)


# Evaluate accuracy
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy with Selected Parameters:", accuracy)