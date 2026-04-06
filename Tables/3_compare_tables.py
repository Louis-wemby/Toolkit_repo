import argparse
import pandas as pd
import sys
import os

def load_table(file_path):
    """根据文件后缀自动读取 CSV 或 Excel"""
    try:
        if file_path.endswith('.csv'):
            return pd.read_csv(file_path)
        elif file_path.endswith(('.xls', '.xlsx')):
            return pd.read_excel(file_path)
        else:
            print(f"[✕] 不支持的文件格式: {file_path} (仅支持 .csv 或 .xlsx)")
            sys.exit(1)
    except Exception as e:
        print(f"[✕] 读取文件 {file_path} 失败: {e}")
        sys.exit(1)

def save_table(df, file_path):
    """根据文件后缀自动保存为 CSV 或 Excel"""
    if file_path.endswith('.xlsx'):
        df.to_excel(file_path, index=False)
    else:
        df.to_csv(file_path, index=False)

def main():
    parser = argparse.ArgumentParser(description="比对旧表与新表，提取新增的行导出为新表")
    
    parser.add_argument('-a', '--old_table', required=True, help="旧的表格 A (已处理过的数据)")
    parser.add_argument('-b', '--new_table', required=True, help="新的表格 B (包含最新产出的数据)")
    parser.add_argument('-o', '--output', required=True, help="输出表格 C 的路径 (差异/增量数据)")
    
    # 强烈建议使用 unique key 进行比对
    parser.add_argument('-k', '--key_column', help="用于比对的唯一标识列名 (如 'SC芯片号(时空芯片SN号)' 或 'Barcode')。如果不指定，则进行全行严格匹配比对。")

    args = parser.parse_args()

    print("[*] 正在加载表格数据...")
    df_old = load_table(args.old_table)
    df_new = load_table(args.new_table)

    print(f"[*] 旧表 A 共 {len(df_old)} 行，新表 B 共 {len(df_new)} 行。")

    if args.key_column:
        # 【策略 1】基于唯一 ID 列提取增量数据 (推荐，最稳定)
        if args.key_column not in df_old.columns or args.key_column not in df_new.columns:
            print(f"[✕] 错误: 指定的比对列 '{args.key_column}' 在表格中不存在，请检查表头！")
            sys.exit(1)
            
        # 找出在 B 中但不在 A 中的 ID
        new_keys = ~df_new[args.key_column].isin(df_old[args.key_column])
        df_diff = df_new[new_keys]
        print(f"[*] 使用 '{args.key_column}' 作为主键进行比对...")
        
    else:
        # 【策略 2】全行比对提取增量数据
        # 使用 merge 将新表和旧表合并，保留仅存在于左侧(新表)的行
        print("[*] 未指定主键，正在进行全列内容比对...")
        # 为了防止 NaN 导致比对失败，先填充空值
        df_old_filled = df_old.fillna("NaN_PLACEHOLDER")
        df_new_filled = df_new.fillna("NaN_PLACEHOLDER")
        
        merged = df_new_filled.merge(df_old_filled, how='left', indicator=True)
        # 筛选出只在 B 表里的行，并去掉辅助列 '_merge'
        df_diff_filled = merged[merged['_merge'] == 'left_only'].drop(columns=['_merge'])
        
        # 还原回原始的 NaN，匹配原始数据的索引
        df_diff = df_new.loc[df_diff_filled.index]

    if df_diff.empty:
        print("[!] 提示：新表 B 中没有发现任何新增数据。未生成输出文件。")
        sys.exit(0)

    print(f"[✓] 提取成功！共发现 {len(df_diff)} 行新增数据。")
    save_table(df_diff, args.output)
    print(f"[✓] 增量数据已保存至: {args.output}")

if __name__ == '__main__':
    main()