import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_absolute_error
import os

df = pd.read_csv('results/geometry_performance.csv')
os.makedirs('results/figures', exist_ok=True)

print(f"Dataset: {len(df)} airfoils\n")

# ── Features and targets ───────────────────────────────────────────────────
features = ['max_camber', 'max_camber_loc', 'max_thickness',
            'max_thickness_loc', 'le_thickness', 'camber_at_25', 'camber_area']

targets = {
    'max_CL_CD': 'Maximum CL/CD',
    'max_CL':    'Maximum CL',
    'min_CD':    'Minimum CD',
}

X = df[features].values
print(f"Features: {features}")
print(f"Samples: {len(X)}\n")

# ── Train and evaluate models ──────────────────────────────────────────────
results = {}

for target_col, target_name in targets.items():
    y = df[target_col].values
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)
    
    scaler = StandardScaler()
    X_train_sc = scaler.fit_transform(X_train)
    X_test_sc = scaler.transform(X_test)
    
    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest':     RandomForestRegressor(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
    }
    
    print(f"Target: {target_name}")
    print("-" * 50)
    
    best_model = None
    best_r2 = -999
    
    for model_name, model in models.items():
        if model_name == 'Linear Regression':
            model.fit(X_train_sc, y_train)
            y_pred = model.predict(X_test_sc)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
        
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        
        # Cross validation
        if model_name == 'Linear Regression':
            cv_scores = cross_val_score(model, 
                scaler.fit_transform(X), y, cv=5, scoring='r2')
        else:
            cv_scores = cross_val_score(model, X, y, cv=5, scoring='r2')
        
        print(f"  {model_name}:")
        print(f"    Test R²={r2:.3f}  MAE={mae:.3f}  CV R²={cv_scores.mean():.3f}±{cv_scores.std():.3f}")
        
        if r2 > best_r2:
            best_r2 = r2
            best_model = (model_name, model, y_pred, y_test)
    
    results[target_col] = best_model
    print()

# ── Feature importance from Random Forest ─────────────────────────────────
print("\nFeature Importance (Random Forest — CL/CD prediction):")
print("-" * 50)

rf_model = RandomForestRegressor(n_estimators=200, random_state=42)
y_clcd = df['max_CL_CD'].values
rf_model.fit(X, y_clcd)

importance_df = pd.DataFrame({
    'feature': features,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print(importance_df.round(4).to_string(index=False))

# Plot feature importance
fig, ax = plt.subplots(figsize=(10, 5))
colors = ['steelblue' if i < 3 else 'lightsteelblue' 
          for i in range(len(importance_df))]
ax.barh(importance_df['feature'], importance_df['importance'],
        color=colors, edgecolor='white')
ax.set_title('Feature Importance for CL/CD Prediction\n(Random Forest, Re=200,000)',
             fontsize=13, fontweight='bold')
ax.set_xlabel('Importance Score')
ax.grid(True, alpha=0.3, axis='x')
plt.tight_layout()
plt.savefig('results/figures/feature_importance.png', dpi=150)
plt.close()
print("\nSaved: feature_importance.png")

# ── Predicted vs actual plots ──────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

for ax, (target_col, target_name) in zip(axes, targets.items()):
    model_name, model, y_pred, y_test = results[target_col]
    r2 = r2_score(y_test, y_pred)
    
    ax.scatter(y_test, y_pred, alpha=0.7, edgecolors='gray',
               linewidth=0.5, s=60, color='steelblue')
    
    # Perfect prediction line
    lims = [min(y_test.min(), y_pred.min()),
            max(y_test.max(), y_pred.max())]
    ax.plot(lims, lims, 'r--', linewidth=2, label='Perfect prediction')
    
    ax.set_xlabel(f'Actual {target_name}')
    ax.set_ylabel(f'Predicted {target_name}')
    ax.set_title(f'{target_name}\n{model_name} | R²={r2:.3f}',
                 fontweight='bold')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

plt.suptitle('ML Model Predictions vs Actual Values',
             fontsize=13, fontweight='bold')
plt.tight_layout()
plt.savefig('results/figures/ml_predictions.png', dpi=150)
plt.close()
print("Saved: ml_predictions.png")

# ── Save importance results ────────────────────────────────────────────────
importance_df.to_csv('results/feature_importance.csv', index=False)
print("Saved: feature_importance.csv")
print("\nML analysis complete.")