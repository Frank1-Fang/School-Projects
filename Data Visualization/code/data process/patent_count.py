import pandas as pd
import os

# 输入文件夹路径和输出文件路径
input_folder = "reduced_cleaned_data"
output_file = "patent_yearly_counts.csv"

# 指定需要保留的列（用于合并时）
columns_to_keep = ["filing_date", "patent_id"]

# 初始化一个空的 DataFrame，用于存储所有文件数据
all_data = pd.DataFrame()

# 获取所有CSV文件的列表
file_list = [f for f in os.listdir(input_folder) if f.endswith('.csv')]

# 读取每个文件并合并数据
for file_name in file_list:
    input_file_path = os.path.join(input_folder, file_name)
    
    # 读取数据并保留指定列
    data = pd.read_csv(input_file_path, usecols=columns_to_keep)
    
    # 将数据追加到总数据框
    all_data = pd.concat([all_data, data], ignore_index=True)

# 确保 filing_date 转为日期格式
all_data['filing_date'] = pd.to_datetime(all_data['filing_date'], errors='coerce')

# 提取年份
all_data['year'] = all_data['filing_date'].dt.year

# 去重处理，仅保留唯一的 patent_id
unique_patents = all_data.drop_duplicates(subset='patent_id')

# 按年份统计专利总数
patent_counts = unique_patents.groupby('year').size().reset_index(name='patent_count')

# 按年份排序
patent_counts = patent_counts.sort_values('year')

# 保存最终统计结果
patent_counts.to_csv(output_file, index=False)

print(f"所有文件的专利数量统计已完成，结果保存到 {output_file}")

