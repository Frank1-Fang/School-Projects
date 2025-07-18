# # 读取之前储存的特征
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt

data = pd.read_csv("features_mine.csv")

# 部分列存在许多没有匹配的空值，将空值填充为0
data.replace([np.inf, -np.inf], np.nan, inplace=True)
data.fillna(0, inplace=True)
# 拆分train、test数据集
train = data[data["origin"]=="train"].drop(["origin"],axis = 1)
test = data[data["origin"]=="test"].drop(["origin","label"],axis = 1)
X,Y = train.drop(['label'],axis=1),train['label']

# 拆分训练集与验证集

train_x,valid_x,train_y,valid_y = train_test_split(X,Y,test_size=0.2)

# 对特征进行标准化
scaler = StandardScaler()

# 训练标准化器，并对训练集进行标准化
train_x = scaler.fit_transform(train_x)
valid_x = scaler.transform(valid_x)
test_x = scaler.transform(test)

# 计算train、valid集里正样本比例
print("Ratio of positive samples in train dataset:",train_y.mean())
print("Ratio of positive samples in valid dataset:",valid_y.mean())

L = []
index = [1,2,3,4,5,6,7,8,9,10]

def run():
        # 拆分训练集与验证集

    train_x,valid_x,train_y,valid_y = train_test_split(X,Y,test_size=0.2)

    # 对特征进行标准化
    scaler = StandardScaler()

    # 训练标准化器，并对训练集进行标准化
    train_x = scaler.fit_transform(train_x)
    valid_x = scaler.transform(valid_x)
    test_x = scaler.transform(test)

    # 使用默认参数建模
    model = LogisticRegression(max_iter=1000)
    model.fit(train_x,train_y)

    # evaluate the model 
    print('train accuracy:',model.score(train_x,train_y))
    print('accuracy:',model.score(valid_x,valid_y))
    print('roc_auc:',roc_auc_score(valid_y,model.predict_proba(valid_x)[:,1]))
    L.append(roc_auc_score(valid_y,model.predict_proba(valid_x)[:,1]))

    print(f"正样本比例：{train_y.mean():.4f}")
    print(f"负样本比例：{1 - train_y.mean():.4f}")

for i in range(10):
    run()
print(L)
plt.plot(index, L)
plt.show()
