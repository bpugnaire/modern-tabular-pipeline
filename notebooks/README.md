# Jupyter Notebooks

This directory contains exploratory and analysis notebooks for the churn prediction project.

## Notebooks

### 1. `01_exploratory_data_analysis.ipynb`
**Purpose**: Comprehensive EDA of the telco churn dataset

**Contents**:
- Data quality checks and statistics
- Target variable distribution
- Demographic analysis (gender, age, dependents)
- Tenure analysis and customer lifecycle
- Financial metrics (charges, revenue)
- Contract and billing patterns
- Service usage patterns
- Feature engineering validation
- Correlation analysis
- Key insights and recommendations

**Key Findings**:
- 26.5% overall churn rate
- Month-to-month contracts have highest churn risk
- New customers (<12 months) churn significantly more
- Fiber optic customers show higher churn despite premium pricing
- Service bundle adoption inversely correlates with churn

### 2. `02_model_training_optimization.ipynb`
**Purpose**: Model training, evaluation, and optimization strategies

**Contents**:
- Baseline model training with default parameters
- Comprehensive evaluation metrics (accuracy, precision, recall, F1, ROC-AUC)
- Confusion matrix and classification report
- ROC and Precision-Recall curves
- Feature importance analysis
- SHAP values for model interpretability
- Error analysis (false positives/negatives)
- Hyperparameter tuning examples
- Optimization recommendations

**Key Results**:
- Baseline: 79.99% accuracy, 0.8441 ROC-AUC
- Top features: tenure_years, contract_type, monthly_charges
- Optimization opportunities identified:
  - Hyperparameter tuning (iterations, depth, learning_rate)
  - Class imbalance handling
  - Feature engineering enhancements
  - Ensemble methods

## Running the Notebooks

### Setup
```bash
# Install Jupyter and dependencies (already included)
make install

# Launch Jupyter
jupyter lab

# Or use VS Code Jupyter extension
code notebooks/
```

### Environment
Notebooks automatically load environment variables from `.env`:
- GCS credentials for data access
- Validated feature loading via Pandera schemas
- Access to project modules (`src/`)

### Dependencies
All required packages are in `pyproject.toml`:
- Data: `pandas`, `polars`, `numpy`
- Visualization: `plotly`, `seaborn`, `matplotlib`
- ML: `catboost`, `scikit-learn`, `shap`
- Project: `src` modules for data loading and models

## Best Practices

1. **Run cells in order** - Dependencies between cells
2. **Check .env file** - Ensure GCS credentials are set
3. **Clear outputs before committing** - Keep notebooks clean in git
4. **Document findings** - Add markdown cells with insights
5. **Version experiments** - Use MLflow for tracking runs

## Output
- Visualizations are interactive (Plotly)
- Charts saved automatically to `outputs/` when generated
- Model artifacts tracked in MLflow (not in notebooks)
