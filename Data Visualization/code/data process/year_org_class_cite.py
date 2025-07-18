import os
import pandas as pd

def preprocess_patent_data(input_folder, output_file):
    all_data = []
    
    # 遍历输入文件夹中的所有 CSV 文件
    for file in os.listdir(input_folder):
        if file.endswith(".csv"):
            file_path = os.path.join(input_folder, file)
            data = pd.read_csv(file_path)
            
            # 保留所需的列
            data = data[['filing_date', 'original_organization', 'patent_id', 'cpc_sub_class', 'beCited']]
            
            # 提取 filing_date 中的年份
            data['filing_date'] = pd.to_datetime(data['filing_date'], errors='coerce').dt.year
            
            # 将 beCited 转换为数字
            data['beCited'] = data['beCited'].apply(lambda x: len(eval(x)) if isinstance(x, str) else 0)
            
            # 删除重复行
            data = data.drop_duplicates(subset=['filing_date', 'original_organization', 'patent_id', 'cpc_sub_class'])
            
            # 过滤掉 cpc_sub_class 为 0 的记录
            data = data[data['cpc_sub_class'] != '0']
            
            # 将处理后的数据添加到列表
            all_data.append(data)
    
    # 合并所有文件的数据
    result_data = pd.concat(all_data, ignore_index=True)
    
    # 保存到输出文件
    result_data.to_csv(output_file, index=False)
    print(f"预处理完成，结果已保存到 {output_file}")

# 修改为你本地的输入文件夹路径和输出文件路径
input_folder = 'reduced_cleaned_data'  # 输入文件夹路径
output_file = 'year_org_class_cite.csv'  # 输出文件路径

# 运行预处理函数
preprocess_patent_data(input_folder, output_file)
