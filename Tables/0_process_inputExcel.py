import argparse
import pandas as pd
import os
import sys

def update_path(old_path, new_base):
    """替换路径中最后一个 '/' 之前的内容.因为下机数据路径以/zfssz8开头,而数据管理路径以/Files开头"""
    if pd.isna(old_path) or not isinstance(old_path, str):
        return old_path
    filename = old_path.split('/')[-1]
    # 使用 / 拼接
    return f"{new_base.rstrip('/')}/{filename}"

def main():
    parser = argparse.ArgumentParser(description="处理测序数据集群挂载表格A,合并为流程分析批量导入表格B")
    
    # --- 必需参数 ---
    parser.add_argument('-a', '--input_a', nargs='+', required=True, help="输入表格 A 的路径 (支持多个文件，空格隔开)")
    parser.add_argument('-b', '--input_b', required=True, help="输入表格 B (作为表头模板)")
    parser.add_argument('-o', '--output', required=True, help="输出的结果表格路径")
    parser.add_argument('-p', '--new_path', required=True, help="FastQ 文件的新路径 (替换最后一个 / 前的内容)")
    parser.add_argument('-r', '--ref_index', required=True, help="ReferenceIndex 参数")
    parser.add_argument('--mem', type=int, required=True, help="Mem 参数 (整数)")
    parser.add_argument('--sc_mem', type=int, required=True, help="ScMem 参数 (整数)")
    
    # --- 可选参数 ---
    parser.add_argument('-k', '--kit_version', default='Stereo-seq T FF V1.3', help="KitVersion (默认: Stereo-seq T FF V1.3)")
    parser.add_argument('--organism', type=str, default='', help="Organism 参数 (可选)")
    parser.add_argument('--tissue', type=str, default='', help="Tissue 参数 (可选)")

    args = parser.parse_args()

    print("[*] 正在读取并合并表格 A...")
    try:
        # 读取一个或多个 A 表并合并
        df_a_list = [pd.read_excel(f) for f in args.input_a]
        df_a = pd.concat(df_a_list, ignore_index=True)
    except Exception as e:
        print(f"[!] 读取 A 表失败: {e}")
        sys.exit(1)

    # 【关键处理】检查并按照 SN 排列，确保相同的 SN 挨在一起
    df_a.sort_values(by='SN', inplace=True)
    df_a.reset_index(drop=True, inplace=True)

    print("[*] 正在读取表格 B 获取表头...")
    try:
        # 读取 B 表，仅为了获取它的表头顺序
        df_b_template = pd.read_excel(args.input_b, nrows=0)
        b_cols = list(df_b_template.columns)
    except Exception as e:
        print(f"[!] 读取 B 表失败: {e}")
        sys.exit(1)

    # 替换 B 表头中的 Fastqs 为 FastQ1 和 FastQ2，保持其他顺序不变
    if 'Fastqs' in b_cols:
        idx = b_cols.index('Fastqs')
        b_cols = b_cols[:idx] + ['FastQ1', 'FastQ2'] + b_cols[idx+1:]
    else:
        # 兜底：如果 B 表里没有 Fastqs 列，就加在末尾
        b_cols.extend(['FastQ1', 'FastQ2'])

    # 创建目标空表
    df_b = pd.DataFrame(columns=b_cols)

    print("[*] 正在执行数据映射和处理逻辑...")
    # 1. 基础对应关系
    df_b['EntityID'] = df_a['SampleID']
    df_b['ID'] = df_a['SN']
    df_b['SN'] = df_a['SN']

    # 2. 处理 FastQ 路径替换
    if '*FastQ1' in df_a.columns:
        df_b['FastQ1'] = df_a['*FastQ1'].apply(lambda x: update_path(x, args.new_path))
    else:
        print("[!] 警告：A 表中未找到 '*FastQ1' 列！")
        
    if 'FastQ2' in df_a.columns:
        df_b['FastQ2'] = df_a['FastQ2'].apply(lambda x: update_path(x, args.new_path))
    else:
        print("[!] 警告：A 表中未找到 'FastQ2' 列！")

    # 3. 拼接 ChipMask 路径
    df_b['ChipMask'] = df_a['SN'].apply(lambda sn: f"/Files/RawData/{sn}.barcodeToPos.h5")

    # 4. ReferenceIndex: 仅在首个出现的 Unique SN 处填入，其余保持空 (NaN)
    df_b['ReferenceIndex'] = None
    first_sn_mask = ~df_b['SN'].duplicated(keep='first')
    df_b.loc[first_sn_mask, 'ReferenceIndex'] = args.ref_index

    # 5. 填入 User 参数传入的内容
    df_b['KitVersion'] = args.kit_version
    if args.organism:
        df_b['Organism'] = args.organism
    if args.tissue:
        df_b['Tissue'] = args.tissue
        
    df_b['Mem'] = args.mem
    df_b['ScMem'] = args.sc_mem

    # 6. 填入固定硬编码的值
    df_b['UniquelyMappedOnly'] = 'false'
    df_b['rRNARemove'] = 'false'
    df_b['LargeChip'] = 'false'
    df_b['CellSpecies'] = 'mouse'
    df_b['CellSample'] = 'pbmc'
    df_b['Correction'] = 0

    # 其余未提及的列由于我们在创建 pd.DataFrame(columns=b_cols) 时已经定义，会自动保持为空 (NaN)

    print(f"[*] 正在保存结果至: {args.output}")
    # 存出结果，取消索引
    df_b.to_excel(args.output, index=False)
    print("[✔︎] 处理完成！")

if __name__ == '__main__':
    main()
