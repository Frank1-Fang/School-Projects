import os
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

# 输入文件夹路径
folder_path = "reduced_cleaned_data"  # 替换为你的文件夹路径

# 特征提取函数
def extract_features(data):
    # 转换 beCited 列为列表长度
    data['beCited'] = data['beCited'].apply(lambda x: len(eval(x)) if pd.notnull(x) else 0)

    # 按机构分组
    grouped = data.groupby('original_organization')

    # 计算特征
    patent_count = grouped['patent_id'].nunique()  # 专利数
    total_citations = grouped['beCited'].sum()  # 被引用总数
    avg_citations_per_patent = total_citations / patent_count  # 平均被引用次数
    field_diversity = grouped['cpc_class'].nunique()  # 领域广度
    field_focus = grouped['cpc_class'].apply(lambda x: x.value_counts().max() / len(x))  # 主领域专注度
    
    data['filing_year'] = pd.to_datetime(data['filing_date'], errors='coerce').dt.year
    grouped_year = grouped['filing_year']
    
    active_years = grouped_year.apply(lambda x: x.max() - x.min() + 1)  # 活跃年限
    avg_patents_per_year = patent_count / active_years  # 年均专利数
    inventor_count = grouped['inventor_id'].nunique()  # 发明人数

    # 返回特征表
    return pd.DataFrame({
        'patent_count': patent_count,
        'total_citations': total_citations,
        'avg_citations_per_patent': avg_citations_per_patent,
        'field_diversity': field_diversity,
        'field_focus': field_focus,
        'active_years': active_years,
        'avg_patents_per_year': avg_patents_per_year,
        'inventor_count': inventor_count
    }).reset_index()

# 合并文件夹中的所有 .csv 文件
data_list = []
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        file_path = os.path.join(folder_path, file_name)
        print(f"读取文件: {file_path}")
        data = pd.read_csv(file_path)
        data_list.append(data)

# 合并所有数据
all_data = pd.concat(data_list, ignore_index=True)

# 提取特征
features = extract_features(all_data)

# 数据标准化
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features.iloc[:, 1:])

# 使用肘部法确定最佳聚类数
distortions = []
for k in range(2, 10):
    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(features_scaled)
    distortions.append(kmeans.inertia_)

# 绘制肘部法图像
plt.figure(figsize=(8, 5))
plt.plot(range(2, 10), distortions, marker='o')
plt.xlabel('Number of clusters')
plt.ylabel('Distortion')
plt.title('Elbow Method')
plt.show()

# 选择最佳聚类数（例如 4）
optimal_k = 4
kmeans = KMeans(n_clusters=optimal_k, random_state=42)
features['cluster'] = kmeans.fit_predict(features_scaled)

# 只保留数值类型列
numeric_features = features.select_dtypes(include=[float, int])

# 执行聚合操作
cluster_summary = numeric_features.groupby(features['cluster']).mean()

# 可视化聚类结果（PCA 降维）
pca = PCA(n_components=2)
pca_result = pca.fit_transform(features_scaled)
features['pca1'] = pca_result[:, 0]
features['pca2'] = pca_result[:, 1]

pca_data = features[['original_organization', 'pca1', 'pca2', 'cluster']]
pca_data.to_csv('pca_clustered_data.csv', index=False)
print("降维后的数据和聚类结果已保存为 pca_clustered_data.csv")

plt.figure(figsize=(10, 7))
sns.scatterplot(data=features, x='pca1', y='pca2', hue='cluster', palette='Set2')
plt.title('Cluster Visualization')
plt.xlabel('PCA Component 1')
plt.ylabel('PCA Component 2')
plt.xlim(-10, 50)  # 设置x轴范围
plt.ylim(-10, 50)  # 设置y轴范围
plt.legend(title='Cluster')
plt.show()

# 保存聚类结果
features.to_csv('clustered_features.csv', index=False)
print("聚类结果已保存为 clustered_features.csv")