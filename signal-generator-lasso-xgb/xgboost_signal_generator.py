from xgboost import XGBClassifier
import numpy as np
import pandas as pd

# ------------------ #
# Step 1: Define 3-class Target
# ------------------ #

# Calculate future return (10-bar forward, adjust if needed)
future_return = df['Close'].shift(-6) / df['Close'] - 1

# Assign classes:
# 0 = Down, 1 = Flat, 2 = Up
df['Target'] = np.select(
    [future_return < -0.01, future_return > 0.01],
    [0, 2],
    default=1
)

# ------------------ #
# Step 2: Feature Setup
# ------------------ #

XGB_WINDOW = 1000
retrain_freq = 10

feature_cols = [
    'Return_1', 'Return_2', 'Return_3',
    'Log_Return',
    'Vol_6', 'Vol_20', 'Vol_50', 'Vol_Ratio', 'Vol_6_Z',
    'Momentum_3', 'Momentum_10', 'MA_slope_10', 'Price_MA_20_ratio',
    'SignedVol', 'SignedVol_EMA10',
    'Vol_Imbalance', 'Vol_Imbalance_MA',
    'ZVolume', 'GARCH_vol_1_clipped', 'GARCH_vs_Realized', 'GARCH_Z',
    'RSI_scaled', 'RSI_Overbought', 'RSI_Oversold',
    'MACD_Clipped', 'MACD_Z'
]

# Drop previous prediction columns if any
df.drop(columns=[
    'XGB_Prediction', 'XGB_Confidence', 'XGB_Long_Conf',
    'XGB_Short_Conf', 'XGB_Flat_Conf', 'Confidence_Gap'
], inplace=True, errors='ignore')

# Initialize columns
df['XGB_Prediction'] = np.nan
df['XGB_Long_Conf'] = np.nan
df['XGB_Short_Conf'] = np.nan
df['XGB_Flat_Conf'] = np.nan
df['XGB_Confidence'] = np.nan
df['Confidence_Gap'] = np.nan

# Clean dataframe for training
df_clean = df.dropna(subset=feature_cols + ['Target']).copy()
model = None

# Rolling window training and prediction
for i in range(XGB_WINDOW, len(df_clean)):
    if (i - XGB_WINDOW) % retrain_freq == 0:
        train_df = df_clean.iloc[i - XGB_WINDOW:i-6].copy()

        if train_df[feature_cols + ['Target']].isnull().any().any():
            continue

        X_train = train_df[feature_cols]
        y_train = train_df['Target']

        model = XGBClassifier(
            n_estimators=100,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='multi:softprob',
            num_class=3,
            eval_metric='mlogloss',
            n_jobs=3,
            random_state=42
        )
        model.fit(X_train, y_train)

    if model is not None:
        X_test = df_clean.iloc[[i]][feature_cols]
        if X_test.isnull().any().any():
            continue

        probs = model.predict_proba(X_test)[0]
        predicted_class = int(np.argmax(probs))
        idx = df_clean.index[i]

        df.loc[idx, 'XGB_Prediction'] = predicted_class
        df.loc[idx, 'XGB_Short_Conf'] = probs[0]
        df.loc[idx, 'XGB_Flat_Conf'] = probs[1]
        df.loc[idx, 'XGB_Long_Conf'] = probs[2]
        df.loc[idx, 'XGB_Confidence'] = max(probs)
        df.loc[idx, 'Confidence_Gap'] = abs(probs[2] - probs[0])


# ------------------ #
# Step 3: Evaluation
# ------------------ #

# evaluation for 3 class xgboost
from sklearn.metrics import classification_report, confusion_matrix, f1_score, precision_score, recall_score, mean_squared_error
import numpy as np

# Only evaluate on rows where prediction exists
valid = df['XGB_Prediction'].notna()

y_true = df.loc[valid, 'Target'].astype(int)
y_pred = df.loc[valid, 'XGB_Prediction'].astype(int)
y_prob = df.loc[valid, ['XGB_Short_Conf', 'XGB_Flat_Conf', 'XGB_Long_Conf']].values

# Overall MDA (how often predicted class matches true class)
mda = (y_true == y_pred).mean()

# RMSE using argmax of predicted probs
rmse = mean_squared_error(y_true, y_prob.argmax(axis=1)) ** 0.5

# Classification report for per-class precision/recall/f1
report = classification_report(y_true, y_pred, target_names=["Down", "Flat", "Up"])

# Confusion matrix (optional)
conf_mat = confusion_matrix(y_true, y_pred)

# Print results
print("📊 XGBoost 3-Class Evaluation")
print(f"Mean Directional Accuracy (MDA): {mda:.2%}")
print(f"RMSE (class argmax):             {rmse:.4f}")
print("\nClassification Report:\n", report)
print("Confusion Matrix:\n", conf_mat)

