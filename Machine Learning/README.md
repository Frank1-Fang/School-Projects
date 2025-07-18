# Repeat Buyer Prediction for E-Commerce (Tmall Dataset)
This repository contains our final project for the *CS182 - Introduction to Machine Learning* course at ShanghaiTech University (Fall 2024-2025).  
We selected the real-world topic: **Tmall Repeat Buyer Prediction**, a problem from Alibaba Tianchi platform.

## Project Overview
Predicting whether a customer will make a repeat purchase with a specific merchant is crucial for e-commerce platforms aiming to improve customer retention and long-term revenue. In this project, we developed a machine learning pipeline to forecast repeat buyers based on user behaviors, merchant performance, and user-merchant interactions.

We used four datasets containing user demographics, user logs, historical purchases, and merchant data to construct rich features. We then compared multiple models—**Logistic Regression**, **Support Vector Machines (SVM)**, **Random Forest**, and **XGBoost**—on their predictive performance and computational efficiency.

## Key Methods
- **Feature Engineering**:  
  We extracted features from:
  - User behavior: clicks, add-to-cart, purchase ratio, active days
  - Merchant statistics: CTR, purchase rate, unique user count
  - User-merchant interactions: repurchase ratio, interaction diversity
  - Demographics: age range, gender (one-hot encoded)

- **Model Comparison**:  
  We trained and evaluated four models:
  - `Logistic Regression`: strong baseline with fast convergence and interpretability
  - `SVM`: poor scalability on large dataset
  - `Random Forest`: low variance but suboptimal AUC
  - `XGBoost`: highest AUC, best accuracy, but required parameter tuning

- **Feature Importance Analysis**:
  We masked different feature blocks to identify their contribution to AUC:
  - Demographics (age/gender): minimal impact
  - User behavior: moderate impact
  - Merchant features and user-merchant interactions: **most critical**

 ## Results Summary

| Model               | Train Accuracy | Test Accuracy | ROC AUC   |
|--------------------|----------------|----------------|-----------|
| Logistic Regression | 0.93857        | 0.93832        | 0.66821   |
| SVM                 | 0.93918        | 0.93976        | 0.54404   |

- XGBoost achieved the best performance (highest mean AUC), though not shown in table due to multi-run variance analysis.
- Logistic Regression offers consistent and interpretable performance.
- SVM is inefficient and unsuitable for this dataset.

## File Structure
```plaintext
Machine Learning/
├── code/                   # Model training, feature generation, evaluation
├── report/                 # Final report in PDF
├── PPT/                    # Project presentation slides
└── README.md               # Project overview
