import pandas as pd
import os

# 输入文件夹路径和输出文件路径
input_folder = "reduced_cleaned_data"
patent_output_file = "institution_patent_counts.csv"
citation_output_file = "institution_citation_counts.csv"

# 指定需要保留的列
columns_to_keep = ["filing_date", "original_organization", "patent_id", "beCited"]

# 初始化一个空的 DataFrame
all_data = pd.DataFrame()

# 获取所有CSV文件的列表
file_list = [f for f in os.listdir(input_folder) if f.endswith('.csv')]

# 读取和合并数据
for file_name in file_list:
    input_file_path = os.path.join(input_folder, file_name)
    data = pd.read_csv(input_file_path, usecols=columns_to_keep)
    all_data = pd.concat([all_data, data], ignore_index=True)

# 转换 filing_date 为日期格式并提取年份
all_data['filing_date'] = pd.to_datetime(all_data['filing_date'], errors='coerce')
all_data['year'] = all_data['filing_date'].dt.year

# 去重专利记录
unique_patents = all_data.drop_duplicates(subset='patent_id')

# =========== 统计专利数 ============
# 按机构和年份统计专利数
patent_counts = (
    unique_patents
    .groupby(['original_organization', 'year'])
    .agg(patent_count=('patent_id', 'count'))
    .reset_index()
)

# 创建透视表，按机构和年份展开
patent_pivot = patent_counts.pivot(index='original_organization', columns='year', values='patent_count').fillna(0)
patent_pivot.to_csv(patent_output_file)
print(f"专利数量统计已保存到 {patent_output_file}")

# =========== 快速统计引用数 ============
# 处理 beCited 列，将引用 ID 展开为独立行
citation_data = unique_patents[['original_organization', 'year', 'beCited']].dropna()
citation_data = citation_data.assign(beCited=citation_data['beCited'].str.split(',')).explode('beCited')

# 按机构和年份统计引用数
citation_counts = (
    citation_data
    .groupby(['original_organization', 'year'])
    .size()
    .reset_index(name='total_citations')
)

# 创建透视表，按机构和年份展开
citation_pivot = citation_counts.pivot(index='original_organization', columns='year', values='total_citations').fillna(0)
citation_pivot.to_csv(citation_output_file)
print(f"引用数量统计已保存到 {citation_output_file}")
