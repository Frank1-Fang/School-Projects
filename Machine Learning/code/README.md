Code for the final project.

# Feature Engineering Overview
This document describes the core feature engineering pipeline implemented for our project: **Repeat Buyer Prediction for E-Commerce (Tmall Dataset)**.

We designed and extracted features from three perspectives to capture complex behaviors and interactions within the data:

## Data Sources

The features were generated from the following CSV files:

- `user_info_format1.csv`: demographic info (age, gender)
- `user_log_format1.csv`: full behavioral logs (click, cart, purchase, favorite)
- `train_format1.csv` / `test_format1.csv`: training & prediction targets

## 1. User-level Features

We extracted personalized user-level behavioral features to capture shopping tendencies and loyalty signals.

### Basic Aggregations
- Total number of actions (`click`, `cart`, `purchase`, `favorite`)
- Number of unique interacted items, categories, brands, and merchants
- Total number of active days

### Action Ratio Features
- `purchase_to_click_ratio`
- `cart_to_click_ratio`
- `favorite_to_click_ratio`

### Active Days Ratios
- For each action type, compute:
  - Number of active days
  - Ratio of action-specific active days over total active days

### User Repurchase Rate
- Fraction of merchants with whom the user made purchases on multiple days
- Captures user loyalty tendency

## 2. Merchant-level Features

These features describe the merchants' ability to attract and retain users.

### Basic Aggregations
- Total number of interactions
- Unique users, categories, items, active days

### Behavior Ratios
- `merchant_purchase_to_click_ratio`
- `merchant_cart_to_click_ratio`
- `merchant_favorite_to_click_ratio`

### Activity Spread
- Merchant active days by action type
- Ratio of active days per behavior over total active days

### Merchant Repurchase Rate
- Proportion of users who made repeat purchases with the merchant

## 3. User-Merchant Interaction Features

These features capture the fine-grained relationship between individual users and merchants.

### Interaction Statistics
- Total number of user-merchant interactions
- Number of active days, unique items/categories/brands involved

### Behavior Ratios
- `um_purchase_to_click_ratio`
- `um_cart_to_click_ratio`
- `um_favorite_to_click_ratio`

### Activity Analysis
- Number of active days for each action type (0-3)
- Ratio of active days per behavior over total active days

### User-Merchant Repurchase Flag
- Binary indicator: whether the user made purchases on multiple days with this merchant

## Additional Notes

- **Demographics**: Age and gender are one-hot encoded (with missing values imputed).
- **Missing Data**: Handled via imputation for `gender`, `age_range`, and `brand_id`.
- **Join Strategy**: All features are merged back into a unified table using `user_id` and `merchant_id`.

## Output

The final merged feature set was saved as: `./features_mine.csv`. It includes all engineered features for both train and test samples, ready for modeling.
