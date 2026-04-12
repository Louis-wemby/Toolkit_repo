import json
import pandas as pd
import argparse
import sys

def extract_saw_metrics(json_file_path, output_name):
    # 读取 JSON 文件
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"错误: 找不到文件 '{json_file_path}'")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"错误: 文件 '{json_file_path}' 不是有效的 JSON 格式")
        sys.exit(1)
    
    # --- 1. 数据定位 ---
    # 使用 .get() 配合默认空字典/列表，提高代码鲁棒性
    report_gene = data.get("7.Report summary", {}).get("7.1.Gene", [{}])[0]
    anno_dist = data.get("2.Annotation", {}).get("2.3.Annotation", [{}])[0]
    tissue_summary = data.get("3.TissueCut", {}).get("3.1.Summary", [{}])[0]
    
    # 寻找 Bin 20 的统计数据
    bin_stats_list = data.get("3.TissueCut", {}).get("3.2.Gene square bin statistics", [])
    bin20_data = next((item for item in bin_stats_list if str(item.get("Bin size")) == "20"), None)

    # --- 2. 指标整理 ---
    metrics = []

    # Sequencing & Quality
    metrics.append(["Sequencing", "Total Reads", report_gene.get("Total Reads (Gene)")])
    metrics.append(["Sequencing", "Total Q30", report_gene.get("Total Q30")])
    metrics.append(["Sequencing", "Sequencing Saturation", report_gene.get("% of Sequencing Saturation")])
    
    # Alignment
    metrics.append(["Mapping", "Confidently Mapped Rate", report_gene.get("% of Confidently Mapped Reads")])
    metrics.append(["Mapping", "Exonic Region Rate", anno_dist.get("% of reads mapped to exonic regions")])
    metrics.append(["Mapping", "Intronic Region Rate", anno_dist.get("% of reads mapped to intronic regions")])

    # Tissue Area (换算为 mm^2)
    area_nm2_str = tissue_summary.get("Tissue area in square nanometers")
    if area_nm2_str:
        area_mm2 = round(float(area_nm2_str) / 1e12, 4)
    else:
        area_mm2 = None
    metrics.append(["Tissue", "Tissue Area (mm^2)", area_mm2])
    metrics.append(["Tissue", "Total Gene Types", tissue_summary.get("Total gene type under tissue")])

    # Bin 20 Statistics
    if bin20_data:
        # metrics.append(["Square Bin 20", "Mean Reads per Spot", bin20_data.get("Mean reads per spot")])
        metrics.append(["Square Bin 20", "Mean MID count per Spot", bin20_data.get("Mean MID per spot")])
        metrics.append(["Square Bin 20", "Mean Gene types per Spot", bin20_data.get("Mean gene type per spot")])
        # metrics.append(["Square Bin 20", "Median Gene types per Spot", bin20_data.get("Median gene type per spot")])
    else:
        print("警告: JSON 中未找到 Bin 20 的数据，输出表格中将缺失此部分。")

    # --- 3. 生成 DataFrame 并导出 ---
    df = pd.DataFrame(metrics, columns=["Category", "Metric Name", "Value"])
    
    try:
        df.to_excel(output_name, index=False, engine='openpyxl')
        print(f"成功！指标已提取并保存至: {output_name}")
    except Exception as e:
        print(f"导出 Excel 失败: {e}")
        print("请检查是否安装了 openpyxl 库: pip install openpyxl")
        sys.exit(1)

def main():
    # 使用 argparse 配置命令行参数
    parser = argparse.ArgumentParser(
        description="从 SAW 分析报告 (JSON) 中提取关键空间转录组指标，并导出为 Excel 表格。"
    )
    
    # 添加 -i/--input 和 -o/--output 参数
    parser.add_argument("-i", "--input", required=True, 
                        help="输入的 JSON 文件路径 (必须提供，例如: report.json)")
    parser.add_argument("-o", "--output", default="SAW_Appendix_Metrics.xlsx", 
                        help="输出的 Excel 文件路径 (可选，默认: SAW_Appendix_Metrics.xlsx)")
    
    args = parser.parse_args()
    
    # 执行提取
    extract_saw_metrics(args.input, args.output)

if __name__ == "__main__":
    main()