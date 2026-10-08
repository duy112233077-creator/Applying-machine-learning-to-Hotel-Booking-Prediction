import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings
warnings.filterwarnings('ignore')

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, confusion_matrix, roc_auc_score, roc_curve)

# Setup directories
OUTPUT_DIR = "outputs"
PLOTS_DIR = os.path.join(OUTPUT_DIR, "plots")
MODELS_DIR = os.path.join(OUTPUT_DIR, "models")
os.makedirs(PLOTS_DIR, exist_ok=True)
os.makedirs(MODELS_DIR, exist_ok=True)

def find_dataset():
    candidates = [
        os.path.join("hotel_bookings.csv", "hotel_bookings.csv"),
        "hotel_bookings.csv",
        os.path.join("files", "hotel_bookings.csv")
    ]
    for c in candidates:
        if os.path.isfile(c):
            return c
    raise FileNotFoundError("Could not find hotel_bookings.csv dataset")

def main():
    print("=" * 70)
    print("ENHANCED HOTEL BOOKING CANCELLATION PREDICTION PIPELINE")
    print("=" * 70)
    
    # 1. LOAD DATASET
    data_path = find_dataset()
    print(f"[1/8] Loading dataset from: {data_path}")
    df = pd.read_csv(data_path)
    print(f"      Dataset Shape: {df.shape[0]} rows x {df.shape[1]} columns")
    
    # Save raw EDA summary log
    with open(os.path.join(OUTPUT_DIR, "eda_summary.txt"), "w", encoding="utf-8") as f:
        f.write("=== DATASET INFORMATION ===\n")
        f.write(f"Shape: {df.shape}\n\n")
        f.write("Column Names & Types:\n")
        for col, dtype in zip(df.columns, df.dtypes):
            f.write(f" - {col}: {dtype}\n")
        f.write("\n=== MISSING VALUES ===\n")
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        f.write(missing.to_string())
        f.write("\n\n=== DESCRIPTIVE STATISTICS ===\n")
        f.write(df.describe().to_string())
        f.write("\n\n=== TARGET DISTRIBUTION ===\n")
        f.write(df['is_canceled'].value_counts().to_string())
        f.write("\n" + df['is_canceled'].value_counts(normalize=True).to_string())

    sns.set_theme(style="whitegrid")

    # 2. MISSING VALUES VISUALIZATION
    print("[2/8] Generating Missing Values & Target Distribution Visualizations...")
    missing = df.isnull().sum()
    missing = missing[missing > 0].sort_values(ascending=False)
    
    if len(missing) > 0:
        plt.figure(figsize=(8, 5))
        missing_perc = (missing / len(df)) * 100
        ax = sns.barplot(x=missing_perc.values, y=missing_perc.index, palette="Reds_r")
        plt.title("Percentage of Missing Values by Feature", fontsize=12, fontweight="bold")
        plt.xlabel("Missing Percentage (%)")
        for p in ax.patches:
            width = p.get_width()
            ax.annotate(f'{width:.2f}%', (width + 0.5, p.get_y() + p.get_height() / 2.),
                        ha='left', va='center', fontsize=10)
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, "eda_missing_values.png"), dpi=300)
        plt.close()

    # Target Distribution Pie & Bar Combo Plot
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    
    # Bar Chart
    ax1 = sns.countplot(data=df, x='is_canceled', palette='Set2', ax=axes[0])
    axes[0].set_title('Target Count Distribution', fontsize=12, fontweight='bold')
    axes[0].set_xticklabels(['Not Canceled (0)', 'Canceled (1)'])
    for p in ax1.patches:
        height = p.get_height()
        ax1.annotate(f'{height:,}', (p.get_x() + p.get_width() / 2., height / 2),
                     ha='center', va='center', fontsize=11, color='white', fontweight='bold')
        
    # Pie Chart
    target_counts = df['is_canceled'].value_counts()
    axes[1].pie(target_counts, labels=['Not Canceled (0)', 'Canceled (1)'], autopct='%1.1f%%',
                colors=['#66b3ff','#ff9999'], explode=(0.05, 0), startangle=90, textprops={'fontsize': 11, 'weight': 'bold'})
    axes[1].set_title('Target Percentage Distribution', fontsize=12, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "eda_target_distribution_pie_bar.png"), dpi=300)
    plt.close()

    # Categorical Features Pie Charts (Hotel Type, Deposit Type, Market Segment)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    df['hotel'].value_counts().plot.pie(ax=axes[0], autopct='%1.1f%%', colors=['#ff9999','#66b3ff'], startangle=90)
    axes[0].set_title('Hotel Type Distribution', fontweight='bold')
    axes[0].set_ylabel('')

    df['deposit_type'].value_counts().plot.pie(ax=axes[1], autopct='%1.1f%%', colors=['#99ff99','#ffcc99','#c2c2f0'], startangle=90)
    axes[1].set_title('Deposit Type Distribution', fontweight='bold')
    axes[1].set_ylabel('')

    df['market_segment'].value_counts().plot.pie(ax=axes[2], autopct='%1.1f%%', startangle=90)
    axes[2].set_title('Market Segment Distribution', fontweight='bold')
    axes[2].set_ylabel('')

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "eda_categorical_pies.png"), dpi=300)
    plt.close()

    # 3. OUTLIER ANALYSIS (IQR METHOD)
    print("[3/8] Performing Outlier Analysis (IQR Method)...")
    
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    
    # Lead time before IQR
    sns.boxplot(data=df, y='lead_time', ax=axes[0, 0], color='lightskyblue')
    axes[0, 0].set_title('Lead Time (Before IQR Cleaning)', fontweight='bold')
    
    # ADR before IQR
    sns.boxplot(data=df, y='adr', ax=axes[0, 1], color='lightcoral')
    axes[0, 1].set_title('ADR (Before IQR Cleaning)', fontweight='bold')

    # Compute IQR bounds
    Q1_lt, Q3_lt = df['lead_time'].quantile(0.25), df['lead_time'].quantile(0.75)
    IQR_lt = Q3_lt - Q1_lt
    upper_lt = Q3_lt + 1.5 * IQR_lt

    Q1_adr, Q3_adr = df['adr'].quantile(0.25), df['adr'].quantile(0.75)
    IQR_adr = Q3_adr - Q1_adr
    upper_adr = Q3_adr + 1.5 * IQR_adr
    lower_adr = max(0, Q1_adr - 1.5 * IQR_adr)

    df_filtered_iqr = df[(df['lead_time'] <= upper_lt) & (df['adr'] >= lower_adr) & (df['adr'] <= upper_adr)]

    # Lead time after IQR
    sns.boxplot(data=df_filtered_iqr, y='lead_time', ax=axes[1, 0], color='deepskyblue')
    axes[1, 0].set_title(f'Lead Time (After IQR Cleaning: <= {upper_lt:.0f} days)', fontweight='bold')
    
    # ADR after IQR
    sns.boxplot(data=df_filtered_iqr, y='adr', ax=axes[1, 1], color='crimson')
    axes[1, 1].set_title(f'ADR (After IQR Cleaning: {lower_adr:.0f} - {upper_adr:.0f})', fontweight='bold')

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "eda_outliers_before_after.png"), dpi=300)
    plt.close()

    print(f"      Raw Rows: {len(df):,} | IQR Filtered Rows: {len(df_filtered_iqr):,}")

    # Plot 2D Distribution: Lead Time vs ADR
    plt.figure(figsize=(9, 6))
    sns.scatterplot(data=df_filtered_iqr.sample(5000, random_state=42), x='lead_time', y='adr', hue='is_canceled', alpha=0.6, palette='coolwarm')
    plt.title('2D Distribution: Lead Time vs ADR (Colored by Cancellation)', fontsize=12, fontweight='bold')
    plt.xlabel('Lead Time (Days)')
    plt.ylabel('Average Daily Rate (ADR)')
    plt.legend(title='Is Canceled', labels=['No', 'Yes'])
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "eda_leadtime_vs_adr_scatter.png"), dpi=300)
    plt.close()

    # Correlation Matrix
    plt.figure(figsize=(12, 10))
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    sns.heatmap(corr, annot=False, cmap='coolwarm', linewidths=0.5)
    plt.title('Correlation Matrix of Numerical Features', fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "eda_correlation_matrix.png"), dpi=300)
    plt.close()

    # 4. PREPROCESSING & FEATURE ENGINEERING
    print("[4/8] Preprocessing Data & Encoding Features...")
    df_clean = df.copy()

    # Drop leakage columns
    leakage_cols = ['reservation_status', 'reservation_status_date']
    df_clean.drop(columns=[c for c in leakage_cols if c in df_clean.columns], inplace=True)

    # Missing value imputation
    df_clean['agent'] = df_clean['agent'].fillna(0)
    df_clean['company'] = df_clean['company'].fillna(0)
    df_clean['country'] = df_clean['country'].fillna('Unknown')
    df_clean['children'] = df_clean['children'].fillna(0)
    
    # Feature Engineering
    df_clean['total_stay'] = df_clean['stays_in_weekend_nights'] + df_clean['stays_in_week_nights']
    df_clean['total_guests'] = df_clean['children'] + df_clean['babies'] + df_clean['adults']
    df_clean['is_family'] = ((df_clean['children'] > 0) | (df_clean['babies'] > 0)).astype(int)
    df_clean['has_special_requests'] = (df_clean['total_of_special_requests'] > 0).astype(int)

    # Top countries bucketing
    top_countries = df_clean['country'].value_counts().head(10).index
    df_clean['country_group'] = df_clean['country'].apply(lambda c: c if c in top_countries else 'Other')
    df_clean.drop(columns=['country'], inplace=True)
    
    # One-Hot Encoding
    categorical_cols = df_clean.select_dtypes(include=['object']).columns.tolist()
    df_encoded = pd.get_dummies(df_clean, columns=categorical_cols, drop_first=True)

    print(f"      Encoded Dataset Shape: {df_encoded.shape[0]} rows x {df_encoded.shape[1]} features")

    # 5. TRAIN / TEST SPLIT & SCALING
    print("[5/8] Splitting and Scaling Data...")
    X = df_encoded.drop(columns=['is_canceled'])
    y = df_encoded['is_canceled']

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    joblib.dump(scaler, os.path.join(MODELS_DIR, "scaler.pkl"))
    joblib.dump(X.columns.tolist(), os.path.join(MODELS_DIR, "feature_names.pkl"))

    print(f"      Train Set: {X_train_scaled.shape[0]} samples | Test Set: {X_test_scaled.shape[0]} samples")

    # 6. SMOTE BALANCING EXPERIMENT
    print("[6/8] Running SMOTE Oversampling Experiment...")
    smote = SMOTE(random_state=42)
    X_train_smote, y_train_smote = smote.fit_resample(X_train_scaled, y_train)

    print(f"      Original Train Target Distribution: {dict(pd.Series(y_train).value_counts())}")
    print(f"      After SMOTE Target Distribution:    {dict(pd.Series(y_train_smote).value_counts())}")

    # Evaluate Random Forest with SMOTE vs Original
    rf_orig = RandomForestClassifier(n_estimators=100, max_depth=16, random_state=42, n_jobs=-1)
    rf_orig.fit(X_train_scaled, y_train)
    y_pred_orig = rf_orig.predict(X_test_scaled)
    y_proba_orig = rf_orig.predict_proba(X_test_scaled)[:, 1]

    rf_smote = RandomForestClassifier(n_estimators=100, max_depth=16, random_state=42, n_jobs=-1)
    rf_smote.fit(X_train_smote, y_train_smote)
    y_pred_smote = rf_smote.predict(X_test_scaled)
    y_proba_smote = rf_smote.predict_proba(X_test_scaled)[:, 1]

    smote_res = [
        {
            'Experiment': 'Without SMOTE (Original)',
            'Accuracy': accuracy_score(y_test, y_pred_orig),
            'Precision': precision_score(y_test, y_pred_orig),
            'Recall': recall_score(y_test, y_pred_orig),
            'F1-Score': f1_score(y_test, y_pred_orig),
            'ROC-AUC': roc_auc_score(y_test, y_proba_orig)
        },
        {
            'Experiment': 'With SMOTE',
            'Accuracy': accuracy_score(y_test, y_pred_smote),
            'Precision': precision_score(y_test, y_pred_smote),
            'Recall': recall_score(y_test, y_pred_smote),
            'F1-Score': f1_score(y_test, y_pred_smote),
            'ROC-AUC': roc_auc_score(y_test, y_proba_smote)
        }
    ]
    smote_df = pd.DataFrame(smote_res)
    smote_df.to_csv(os.path.join(OUTPUT_DIR, "smote_comparison_results.csv"), index=False)
    
    # SMOTE Bar Chart
    plt.figure(figsize=(8, 5))
    smote_melted = smote_df.melt(id_vars=['Experiment'], value_vars=['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC'], var_name='Metric', value_name='Score')
    sns.barplot(data=smote_melted, x='Metric', y='Score', hue='Experiment', palette='Set1')
    plt.title('SMOTE Oversampling Performance Impact (Random Forest)', fontweight='bold')
    plt.ylim(0.6, 1.0)
    plt.legend(title='')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "smote_comparison_chart.png"), dpi=300)
    plt.close()

    # 7. MODEL TRAINING & GRIDSEARCHCV
    print("[7/8] Training All Models & Hyperparameter Tuning...")
    
    models = {
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42),
        'Decision Tree': DecisionTreeClassifier(max_depth=12, random_state=42),
        'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=16, random_state=42, n_jobs=-1),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, max_depth=6, random_state=42),
        'XGBoost': XGBClassifier(n_estimators=100, max_depth=6, learning_rate=0.1, random_state=42, eval_metric='logloss')
    }

    trained_models = {}
    results = []
    predictions = {}
    probabilities = {}

    for name, model in models.items():
        print(f"      Training {name}...")
        model.fit(X_train_scaled, y_train)
        trained_models[name] = model
        
        joblib.dump(model, os.path.join(MODELS_DIR, f"{name.lower().replace(' ', '_')}.pkl"))

        y_pred = model.predict(X_test_scaled)
        y_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        predictions[name] = y_pred
        probabilities[name] = y_proba

        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        auc = roc_auc_score(y_test, y_proba)

        results.append({
            'Model': name,
            'Accuracy': acc,
            'Precision': prec,
            'Recall': rec,
            'F1-Score': f1,
            'ROC-AUC': auc
        })

    results_df = pd.DataFrame(results)
    results_df.to_csv(os.path.join(OUTPUT_DIR, "model_comparison_results.csv"), index=False)
    
    # GridSearchCV for Random Forest Optimization
    print("      Performing GridSearchCV Hyperparameter Tuning for Random Forest...")
    param_grid = {
        'n_estimators': [100, 150],
        'max_depth': [14, 18],
        'min_samples_split': [2, 5]
    }
    grid_search = GridSearchCV(RandomForestClassifier(random_state=42, n_jobs=-1), param_grid, cv=3, scoring='f1', n_jobs=-1)
    grid_search.fit(X_train_scaled, y_train)
    
    best_rf = grid_search.best_estimator_
    joblib.dump(best_rf, os.path.join(MODELS_DIR, "best_rf_gridsearch.pkl"))
    
    with open(os.path.join(OUTPUT_DIR, "grid_search_summary.txt"), "w", encoding="utf-8") as f:
        f.write("=== GRIDSEARCHCV HYPERPARAMETER TUNING ===\n")
        f.write(f"Best Parameters: {grid_search.best_params_}\n")
        f.write(f"Best CV F1-Score: {grid_search.best_score_:.4f}\n")

    print("\n" + "=" * 70)
    print("MODEL EVALUATION SUMMARY:")
    print("=" * 70)
    print(results_df.to_string(index=False))

    # 8. EVALUATION PLOTS
    print("\n[8/8] Generating Final Comparison Plots...")

    # Plot 1: Model Comparison Bar Chart
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    sns.barplot(data=results_df, x='Model', y='Accuracy', ax=axes[0, 0], palette='Blues_d')
    axes[0, 0].set_title('Accuracy Comparison', fontweight='bold')
    axes[0, 0].set_ylim(0.6, 1.0)
    for p in axes[0, 0].patches:
        axes[0, 0].annotate(f'{p.get_height():.4f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center', va='bottom', fontsize=9)

    sns.barplot(data=results_df, x='Model', y='F1-Score', ax=axes[0, 1], palette='Greens_d')
    axes[0, 1].set_title('F1-Score Comparison', fontweight='bold')
    axes[0, 1].set_ylim(0.5, 1.0)
    for p in axes[0, 1].patches:
        axes[0, 1].annotate(f'{p.get_height():.4f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center', va='bottom', fontsize=9)

    df_melted = results_df.melt(id_vars=['Model'], value_vars=['Precision', 'Recall'], var_name='Metric', value_name='Score')
    sns.barplot(data=df_melted, x='Model', y='Score', hue='Metric', ax=axes[1, 0], palette='Set2')
    axes[1, 0].set_title('Precision vs Recall Comparison', fontweight='bold')
    axes[1, 0].set_ylim(0.5, 1.0)

    sns.barplot(data=results_df, x='Model', y='ROC-AUC', ax=axes[1, 1], palette='Purples_d')
    axes[1, 1].set_title('ROC-AUC Comparison', fontweight='bold')
    axes[1, 1].set_ylim(0.6, 1.0)
    for p in axes[1, 1].patches:
        axes[1, 1].annotate(f'{p.get_height():.4f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                            ha='center', va='bottom', fontsize=9)

    for ax in axes.flatten():
        ax.set_xticklabels(ax.get_xticklabels(), rotation=25, ha='right')

    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "model_metrics_comparison.png"), dpi=300)
    plt.close()

    # Plot 2: Combined ROC Curves
    plt.figure(figsize=(10, 7))
    for name in models.keys():
        fpr, tpr, _ = roc_curve(y_test, probabilities[name])
        auc_val = results_df.loc[results_df['Model'] == name, 'ROC-AUC'].values[0]
        plt.plot(fpr, tpr, label=f"{name} (AUC = {auc_val:.4f})", linewidth=2)

    plt.plot([0, 1], [0, 1], 'k--', label='Random Chance (AUC = 0.5000)')
    plt.xlabel('False Positive Rate (1 - Specificity)', fontsize=11)
    plt.ylabel('True Positive Rate (Sensitivity / Recall)', fontsize=11)
    plt.title('Receiver Operating Characteristic (ROC) Curves', fontsize=13, fontweight='bold')
    plt.legend(loc='lower right', fontsize=10)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "roc_curves_comparison.png"), dpi=300)
    plt.close()

    # Plot 3: Confusion Matrices
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    axes_flat = axes.flatten()

    for idx, (name, y_pred) in enumerate(predictions.items()):
        cm = confusion_matrix(y_test, y_pred)
        sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=axes_flat[idx],
                    xticklabels=['Not Canceled', 'Canceled'],
                    yticklabels=['Not Canceled', 'Canceled'],
                    cbar=False)
        axes_flat[idx].set_title(f'Confusion Matrix: {name}', fontweight='bold')
        axes_flat[idx].set_ylabel('Actual Label')
        axes_flat[idx].set_xlabel('Predicted Label')

    fig.delaxes(axes_flat[5])
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "confusion_matrices.png"), dpi=300)
    plt.close()

    # Plot 4: Feature Importance
    rf_model = trained_models['Random Forest']
    importances = rf_model.feature_importances_
    feat_imp = pd.DataFrame({
        'Feature': X.columns,
        'Importance': importances
    }).sort_values('Importance', ascending=False)

    feat_imp.to_csv(os.path.join(OUTPUT_DIR, "rf_feature_importances.csv"), index=False)

    plt.figure(figsize=(10, 8))
    sns.barplot(data=feat_imp.head(15), x='Importance', y='Feature', palette='viridis')
    plt.title('Top 15 Most Important Features (Random Forest)', fontsize=13, fontweight='bold')
    plt.xlabel('Feature Importance Score')
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "feature_importance_rf.png"), dpi=300)
    plt.close()

    print("\n[OK] Pipeline execution complete!")
    print(f"[OK] All enhanced plots saved to: {PLOTS_DIR}")
    print(f"[OK] Trained models saved to: {MODELS_DIR}")

if __name__ == "__main__":
    main()
