import os
import pandas as pd
import ast

# 指定输入文件夹路径
folder_path = "reduced_cleaned_data"  # 请替换为你的文件夹路径
output_file = "institution_analysis_unique.csv"

# 初始化一个空的 DataFrame 列表
data_list = []

# 遍历文件夹中的所有 CSV 文件并读取
for file_name in os.listdir(folder_path):
    if file_name.endswith('.csv'):
        file_path = os.path.join(folder_path, file_name)
        print(f"正在读取文件: {file_path}")
        df = pd.read_csv(file_path)
        data_list.append(df)

# 合并所有 DataFrame
data = pd.concat(data_list, ignore_index=True)

# 转换 'beCited' 列，将字符串列表转换为实际引用数量
def count_citations(cited_list):
    try:
        return len(ast.literal_eval(cited_list))
    except (ValueError, SyntaxError):
        return 0

data['beCited'] = data['beCited'].apply(count_citations)

# 去重：以 'patent_id' 为唯一标识，保留每个专利的第一条记录
data_unique = data.drop_duplicates(subset=['patent_id'])

# **过滤掉 cpc_sub_class 为 0 的记录**
data_unique = data_unique[data_unique['cpc_sub_class'] != '0']

# 按机构和领域分组，计算引用数总和
citation_group = data_unique.groupby(['original_organization', 'cpc_sub_class']).agg({
    'beCited': 'sum'
}).reset_index()

# 找到每个机构引用数最多的领域
max_citation_class = citation_group.loc[citation_group.groupby('original_organization')['beCited'].idxmax()]
max_citation_class = max_citation_class.rename(columns={
    'cpc_sub_class': 'max_cited_cpc_sub_class',
    'beCited': 'max_cited_count'
})

# 按机构和领域分组，计算专利数
patent_group = data_unique.groupby(['original_organization', 'cpc_sub_class']).size().reset_index(name='patent_count')

# 找到每个机构专利数最多的领域
max_patent_class = patent_group.loc[patent_group.groupby('original_organization')['patent_count'].idxmax()]
max_patent_class = max_patent_class.rename(columns={
    'cpc_sub_class': 'max_patent_cpc_sub_class',
    'patent_count': 'max_patent_count'
})

# 合并引用数最多和专利数最多的领域信息
result = pd.merge(
    max_citation_class[['original_organization', 'max_cited_cpc_sub_class', 'max_cited_count']],
    max_patent_class[['original_organization', 'max_patent_cpc_sub_class', 'max_patent_count']],
    on='original_organization', how='outer'
)

# 输出为 CSV 文件
result.to_csv(output_file, index=False)

print("处理完成，结果已保存为:", output_file)
