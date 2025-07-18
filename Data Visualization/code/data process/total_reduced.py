import pandas as pd
import os

# 输入文件夹路径和输出文件夹路径
input_folder = "cleaned_data"
output_folder = "reduced_cleaned_data"

# 确保输出文件夹存在
os.makedirs(output_folder, exist_ok=True)

# 指定需要保留的列
columns_to_keep = [
    "filing_date",
    "original_organization",
    "inventor_id",
    "male_flag",
    "patent_id",
    "cpc_class",
    "cpc_sub_class",
    "cpc_class_title",
    "beCited"
]

# 获取所有CSV文件的列表
file_list = [f for f in os.listdir(input_folder) if f.endswith('.csv')]

# 批量处理文件
for file_name in file_list:
    input_file_path = os.path.join(input_folder, file_name)
    
    # 读取数据
    data = pd.read_csv(input_file_path)
    
    # 筛选指定的列
    data_filtered = data[columns_to_keep]
    
    # 删除含有缺失值的行
    cleaned_data = data_filtered.dropna()
    
    # 保存清理后的文件
    output_file_path = os.path.join(output_folder, f"reduced_cleaned_{file_name}")
    cleaned_data.to_csv(output_file_path, index=False)
    
    print(f"文件 {file_name} 已处理，清理后的文件保存为 {output_file_path}")

print("所有文件已处理完成！")
