Report for the final project.

# Final Report: Repeat Buyer Prediction for E-Commerce

This directory contains the final report for the course project of **CS182 - Introduction to Machine Learning** at ShanghaiTech University.  
The project focuses on predicting repeat purchase behavior on the Tmall e-commerce platform using various machine learning models and custom-designed features.

## Problem Background

Repeat purchase behavior is vital for e-commerce platforms due to its impact on customer retention and lifetime value.  
This project aims to predict the probability that a user will return to a merchant and make another purchase, leveraging Tmall's user interaction logs and merchant data.

## Methodology

### Datasets Used:
- `train_format1.csv` and `test_format1.csv`: user-merchant pairs with labels
- `user_info_format1.csv`: user demographic data (age, gender)
- `user_log_format1.csv`: user activity logs (click, cart, purchase, favorite)

### Feature Engineering:
- **User features**: interaction counts, action ratios, activity days, repurchase rate
- **Merchant features**: CTR, purchase ratios, user diversity, repurchase rate
- **User-merchant interaction**: personalized ratios and repeat patterns
- **Demographics**: one-hot encoded age and gender

### Models Applied:
- Logistic Regression (baseline, interpretable)
- Support Vector Machine (RBF kernel, slow convergence)
- Random Forest (robust but underperformed)
- XGBoost (best performance but higher variance and complexity)

## Results Summary

| Model               | Train Accuracy | Test Accuracy | ROC AUC   |
|--------------------|----------------|----------------|-----------|
| Logistic Regression | 0.93857        | 0.93832        | 0.66821   |
| SVM                 | 0.93918        | 0.93976        | 0.54404   |

- **XGBoost** achieved the highest AUC across multiple runs, despite variance.
- **Feature importance analysis** showed:
  - Merchant and user-merchant interaction features are **most critical**.
  - Demographics (age, gender) had **minimal influence**.

## Conclusions

- XGBoost is the most effective model for this task.
- Logistic Regression remains a fast and stable baseline.
- SVM is not practical for large-scale behavioral data.
- Targeted feature design is more impactful than adding general demographic data.

This study provides a strong pipeline for customer retention prediction in real-world e-commerce platforms.

## Reference

Liu, G., Nguyen, T. T., Zhao, G., et al. (2016).  
*Repeat Buyer Prediction for E-Commerce.*  
Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining.  
[DOI: 10.1145/2939672.2939674](https://doi.org/10.1145/2939672.2939674)
