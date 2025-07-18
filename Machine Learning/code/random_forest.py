# # 读取之前储存的特征
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score
from sklearn.model_selection import train_test_split

data = pd.read_csv("features_mine.csv")

# 部分列存在许多没有匹配的空值，将空值填充为0
data.replace([np.inf, -np.inf], np.nan, inplace=True)
data.fillna(0, inplace=True)
# 拆分train、test数据集
train = data[data["origin"]=="train"].drop(["origin"],axis = 1)
test = data[data["origin"]=="test"].drop(["origin","label"],axis = 1)
X,Y = train.drop(['label'],axis=1),train['label']

L = []

def run():
    # 拆分训练集与验证集

    train_x,valid_x,train_y,valid_y = train_test_split(X,Y,test_size=0.2)

    # 对特征进行标准化
    scaler = StandardScaler()

    # 训练标准化器，并对训练集进行标准化
    train_x = scaler.fit_transform(train_x)
    valid_x = scaler.transform(valid_x)
    test_x = scaler.transform(test)



    # 使用随机森林模型进行训练
    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(train_x, train_y)

    # 评估模型
    rf_train_accuracy = accuracy_score(train_y, rf_model.predict(train_x))
    rf_valid_accuracy = accuracy_score(valid_y, rf_model.predict(valid_x))
    rf_roc_auc = roc_auc_score(valid_y, rf_model.predict_proba(valid_x)[:, 1])

    # 输出结果
    print("Random Forest Train Accuracy:", rf_train_accuracy)
    print("Random Forest Valid Accuracy:", rf_valid_accuracy)
    print("Random Forest ROC AUC:", rf_roc_auc)
    L.append(rf_roc_auc)

    # 比较正负样本比例
    print(f"正样本比例：{train_y.mean():.4f}")
    print(f"负样本比例：{1 - train_y.mean():.4f}")

for i in range(10):
    run()

print(L)