import argparse
import pandas as pd
import sys

def parse_barcodes(bc_str):
    """
    解析 Barcode number 列。
    如果是 '45~48'，解析为 ['45', '46', '47', '48']
    """
    bc_str = str(bc_str).strip()
    if '~' in bc_str:
        start, end = bc_str.split('~')
        # 考虑到有时候 barcode 可能有前导零（如 045~048），使用 zfill 保持长度一致
        length = len(start)
        return [str(i).zfill(length) for i in range(int(start), int(end) + 1)]
    elif '-' in bc_str: # 兼容有些人习惯用减号表示范围
        start, end = bc_str.split('-')
        length = len(start)
        return [str(i).zfill(length) for i in range(int(start), int(end) + 1)]
    else:
        return [bc_str]

def main():
    parser = argparse.ArgumentParser(description="从表格 A 提取并拆解数据填入表格 B")
    
    # 必需的文件路径参数
    parser.add_argument('-i', '--input', required=True, help="输入文件 A 的路径 (CSV格式)")
    parser.add_argument('-o', '--output', required=True, help="输出文件 B 的路径 (支持 .csv 或 .xlsx)")
    
    # 筛选条件的参数
    parser.add_argument('--filter_species', required=True, help="用于筛选表 A 中 '物种' 列的值")
    
    # 需要填入表 B 的固定参数
    parser.add_argument('--sample_name', required=True, help="填入 B 表的 SampleName")
    parser.add_argument('--species', required=True, help="填入 B 表的 Species")
    parser.add_argument('--tissue', required=True, help="填入 B 表的 Tissue")

    args = parser.parse_args()

    print("[*] 正在读取表格 A...")
    try:
        # 如果你的 CSV 包含中文，可能需要根据实际情况加上 encoding='utf-8' 或 'gbk'
        df_a = pd.read_csv(args.input)
    except Exception as e:
        print(f"[!] 读取文件 A 失败: {e}")
        sys.exit(1)

    # 1. 执行筛选：物种匹配 且 status 为 delivered
    filtered_a = df_a[(df_a['物种'] == args.filter_species) & (df_a['status'] == 'delivered')]

    if filtered_a.empty:
        print("[!] 警告：筛选后没有符合条件的数据！请检查输入的 --filter_species 参数和表格内容。")
        sys.exit(0)

    print(f"✔︎ 筛选出 {len(filtered_a)} 行基础数据，正在进行 Barcode 拆解和路径拼接...")
    
    # 存储 B 表的行数据
    b_rows = []

    # 2. 遍历筛选后的每一行并提取/拆解信息
    for _, row in filtered_a.iterrows():
        # 安全获取字段并转为字符串
        sec_path = str(row.get('secondary path', '')).rstrip('/')  # 去掉路径末尾多余的 / 防止拼接出双斜杠
        chip_num = str(row.get('chip number', ''))
        lane = str(row.get('Lane', ''))
        sn = str(row.get('SC芯片号(时空芯片SN号)', ''))
        sample_id = str(row.get('Production sample number', ''))
        bc_str = str(row.get('Barcode number', ''))
        orig_sample_name = str(row.get('样本名称', ''))

        # 解析 Barcode，例如将 '45~48' 变为 ['45', '46', '47', '48']
        barcodes = parse_barcodes(bc_str)

        # 为每一个 barcode 生成一行数据
        for bc in barcodes:
            # 拼接 FastQ 路径: secondary path/chip number_LaneBarcode_1.fq.gz
            # 注意：在 sec_path 和文件名之间加上了 '/' 保证路径格式正确
            base_name = f"{chip_num}_{lane}_{bc}"
            fastq1 = f"{sec_path}/{base_name}_1.fq.gz"
            fastq2 = f"{sec_path}/{base_name}_2.fq.gz"

            # 组装 B 表单行数据
            b_rows.append({
                '*FastQ1': fastq1,
                'FastQ2': fastq2,
                'SN': sn,
                'SampleID': sample_id,
                'SampleName': args.sample_name,
                'Species': args.species,
                'Tissue': args.tissue,
                '样本名称': orig_sample_name
            })

    # 3. 生成 B 表并导出
    b_columns = ['*FastQ1', 'FastQ2', 'SN', 'SampleID', 'SampleName', 'Species', 'Tissue', '样本名称']
    df_b = pd.DataFrame(b_rows, columns=b_columns)

    print(f"[*] 正在保存结果至: {args.output}")
    # 根据文件后缀自动决定保存为 CSV 还是 Excel
    if args.output.endswith('.xlsx'):
        df_b.to_excel(args.output, index=False)
    elif args.output.endswith('.tsv'):
        df_b.to_csv(args.output, sep='\t', index=False)
    else:
        df_b.to_csv(args.output, index=False)

    print(f"✔︎ 处理完成！共生成 {len(df_b)} 行目标数据。")

if __name__ == '__main__':
    main()