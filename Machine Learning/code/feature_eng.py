import pandas as pd
from sklearn.preprocessing import OneHotEncoder

# 加载数据
user_info = pd.read_csv('./data_format1/user_info_format1.csv')
user_log = pd.read_csv('./data_format1/user_log_format1.csv')
data_train = pd.read_csv('./data_format1/train_format1.csv')
data_test = pd.read_csv('./data_format1/test_format1.csv')

# 合并训练集和测试集，添加来源标记
data_train["origin"] = "train"
data_test["origin"] = "test"
data = pd.concat([data_train, data_test], sort=False)
data = data.drop(["prob"], axis=1)

user_log.rename(columns = {"seller_id":"merchant_id"}, inplace=True)
# 填充缺失值
user_info['gender'] = user_info['gender'].fillna(2)
user_info['age_range'] = user_info['age_range'].fillna(0)
user_log['brand_id'] = user_log['brand_id'].fillna(0)

# 独热编码处理年龄和性别
def one_hot_encode_user_info(user_info):
    encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')  # 修改为 sparse_output=False
    encoded_features = encoder.fit_transform(user_info[['age_range', 'gender']])
    encoded_feature_names = encoder.get_feature_names_out(['age_range', 'gender'])
    encoded_df = pd.DataFrame(encoded_features, columns=encoded_feature_names, index=user_info.index)
    return pd.concat([user_info, encoded_df], axis=1)

user_info_encoded = one_hot_encode_user_info(user_info)

# 删除原始的年龄和性别列
user_info_encoded = user_info_encoded.drop(columns=['age_range', 'gender'])

# 计算交互特征
def calculate_interaction_features(user_log):
    # 按 user_id 分组
    user_features = user_log.groupby('user_id').agg(
        total_interactions=('time_stamp', 'size'),
        unique_items=('item_id', 'nunique'),
        unique_categories=('cat_id', 'nunique'),
        unique_brands=('brand_id', 'nunique'),
        unique_merchants=('merchant_id', 'nunique'),
        total_active_days=('time_stamp', 'nunique')
    ).reset_index()

    # 统计行为次数
    action_counts = user_log.groupby(['user_id', 'action_type']).size().unstack(fill_value=0).reset_index()
    action_counts.columns = ['user_id', 'action_0_count', 'action_1_count', 'action_2_count', 'action_3_count']

    user_features = user_features.merge(action_counts, on='user_id', how='left')

    # 计算行为比例
    user_features['purchase_to_click_ratio'] = user_features['action_2_count'] / user_features['action_0_count']
    user_features['favorite_to_click_ratio'] = user_features['action_3_count'] / user_features['action_0_count']
    user_features['cart_to_click_ratio'] = user_features['action_1_count'] / user_features['action_0_count']

    # 每种行为类型的活跃天数
    action_active_days = user_log.groupby(['user_id', 'action_type'])['time_stamp'].nunique().unstack(fill_value=0).reset_index()
    action_active_days.columns = ['user_id', 'active_days_0', 'active_days_1', 'active_days_2', 'active_days_3']
    user_features = user_features.merge(action_active_days, on='user_id', how='left')

    # 每种行为类型的活跃天数占总活跃天数的比例
    for col in ['active_days_0', 'active_days_1', 'active_days_2', 'active_days_3']:
        user_features[f'{col}_ratio'] = user_features[col] / user_features['total_active_days']

    # 计算复购率
    user_merchant_purchases = user_log[user_log['action_type'] == 2].groupby(['user_id', 'merchant_id'])['time_stamp'].nunique()
    user_merchant_repurchase = (user_merchant_purchases > 1).astype(int).rename('repurchase_flag')
    user_repurchase_rate = user_merchant_repurchase.groupby('user_id').mean().rename('user_repurchase_rate').reset_index()
    user_features = user_features.merge(user_repurchase_rate, on='user_id', how='left')

    # 商家特征
    merchant_features = user_log.groupby('merchant_id').agg(
        merchant_total_interactions=('time_stamp', 'size'),
        merchant_unique_items=('item_id', 'nunique'),
        merchant_unique_categories=('cat_id', 'nunique'),
        merchant_unique_users=('user_id', 'nunique'),
        merchant_total_active_days=('time_stamp', 'nunique')
    ).reset_index()

    # 统计商家行为次数
    merchant_action_counts = user_log.groupby(['merchant_id', 'action_type']).size().unstack(fill_value=0).reset_index()
    merchant_action_counts.columns = ['merchant_id', 'merchant_action_0_count', 'merchant_action_1_count', 'merchant_action_2_count', 'merchant_action_3_count']

    merchant_features = merchant_features.merge(merchant_action_counts, on='merchant_id', how='left')

    # 计算商家行为比例
    merchant_features['merchant_purchase_to_click_ratio'] = merchant_features['merchant_action_2_count'] / merchant_features['merchant_action_0_count']
    merchant_features['merchant_favorite_to_click_ratio'] = merchant_features['merchant_action_3_count'] / merchant_features['merchant_action_0_count']
    merchant_features['merchant_cart_to_click_ratio'] = merchant_features['merchant_action_1_count'] / merchant_features['merchant_action_0_count']

    # 每种行为类型的活跃天数
    merchant_active_days = user_log.groupby(['merchant_id', 'action_type'])['time_stamp'].nunique().unstack(fill_value=0).reset_index()
    merchant_active_days.columns = ['merchant_id', 'merchant_active_days_0', 'merchant_active_days_1', 'merchant_active_days_2', 'merchant_active_days_3']
    merchant_features = merchant_features.merge(merchant_active_days, on='merchant_id', how='left')

# 每种行为类型的活跃天数占总活跃天数的比例
    for col in ['merchant_active_days_0', 'merchant_active_days_1', 'merchant_active_days_2', 'merchant_active_days_3']:
        merchant_features[f'{col}_ratio'] = merchant_features[col] / merchant_features['merchant_total_active_days']

    
    # 计算商家复购率
    merchant_repurchase_rate = user_merchant_repurchase.groupby('merchant_id').mean().rename('merchant_repurchase_rate').reset_index()
    merchant_features = merchant_features.merge(merchant_repurchase_rate, on='merchant_id', how='left')

    # 用户-商家交互特征
    user_merchant_features = user_log.groupby(['user_id', 'merchant_id']).agg(
        um_total_interactions=('time_stamp', 'size'),
        um_total_active_days=('time_stamp', 'nunique'),
        um_unique_items=('item_id', 'nunique'),
        um_unique_categories=('cat_id', 'nunique'),
        um_unique_brands=('brand_id', 'nunique')
    ).reset_index()

    # 统计用户-商家行为次数
    user_merchant_action_counts = user_log.groupby(['user_id', 'merchant_id', 'action_type']).size().unstack(fill_value=0).reset_index()
    user_merchant_action_counts.columns = ['user_id', 'merchant_id', 'um_action_0_count', 'um_action_1_count', 'um_action_2_count', 'um_action_3_count']

    user_merchant_features = user_merchant_features.merge(user_merchant_action_counts, on=['user_id', 'merchant_id'], how='left')

    # 计算用户-商家购买点击比
    user_merchant_features['um_purchase_to_click_ratio'] = user_merchant_features['um_action_2_count'] / user_merchant_features['um_action_0_count']
    user_merchant_features['um_favorite_to_click_ratio'] = user_merchant_features['um_action_3_count'] / user_merchant_features['um_action_0_count']
    user_merchant_features['um_cart_to_click_ratio'] = user_merchant_features['um_action_1_count'] / user_merchant_features['um_action_0_count']
    
    # 每种行为类型的活跃天数
    um_active_days = user_log.groupby(['user_id', 'merchant_id', 'action_type'])['time_stamp'].nunique().unstack(fill_value=0).reset_index()
    um_active_days.columns = ['user_id', 'merchant_id', 'um_active_days_0', 'um_active_days_1', 'um_active_days_2', 'um_active_days_3']
    user_merchant_features = user_merchant_features.merge(um_active_days, on=['user_id', 'merchant_id'], how='left')

    # 每种行为类型的活跃天数占总活跃天数的比例
    for col in ['um_active_days_0', 'um_active_days_1', 'um_active_days_2', 'um_active_days_3']:
        user_merchant_features[f'{col}_ratio'] = user_merchant_features[col] / user_merchant_features['um_total_active_days']
    
    # 计算用户-商家复购率
    user_merchant_features = user_merchant_features.merge(user_merchant_repurchase.reset_index(), on=['user_id', 'merchant_id'], how='left')

    return user_features, merchant_features, user_merchant_features

user_features, merchant_features, user_merchant_features = calculate_interaction_features(user_log)

# 合并特征
def merge_features(data, user_info_encoded, user_features, merchant_features, user_merchant_features):
    data = data.merge(user_features, on='user_id', how='left')
    data = data.merge(user_info_encoded, on='user_id', how='left')
    data = data.merge(merchant_features, on='merchant_id', how='left')
    data = data.merge(user_merchant_features, on=['user_id', 'merchant_id'], how='left')
    return data

data = merge_features(data, user_info_encoded, user_features, merchant_features, user_merchant_features)

# 输出结果
print(data.head())

# 保存处理后的数据
data.to_csv('./features_mine.csv', index=False)
