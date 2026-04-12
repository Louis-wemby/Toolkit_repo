import json
import pandas as pd

def export_saw_to_excel(json_file_path, output_name):
    with open(json_file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # --- 1. 数据定位 ---
    report_gene = data["7.1.Gene"][0]
    anno_dist = data["2.Annotation"]["2.3.Annotation"][0]
    tissue_summary = data["3.TissueCut"]["3.1.Summary"][0]
    
    # 寻找 Bin 20 的统计数据
    bin_stats_list = data["3.TissueCut"]["3.2.Gene square bin statistics"]
    bin20_data = next((item for item in bin_stats_list if str(item["Bin size"]) == "20"), None)

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

    # Tissue Area
    area_nm2 = float(tissue_summary.get("Tissue area in square nanometers", 0))
    # 单位换算为 mm^2
    area_mm2 = round(area_nm2 / 1e12, 4)
    metrics.append(["Tissue", "Tissue Area (mm^2)", area_mm2])
    metrics.append(["Tissue", "Total Gene Types", tissue_summary.get("Total gene type under tissue")])

    # Bin 20 Statistics
    if bin20_data:
        metrics.append(["Square Bin 20", "Mean MID count per Spot", bin20_data.get("Mean MID per spot")])
        metrics.append(["Square Bin 20", "Mean Gene types per Spot", bin20_data.get("Mean gene type per spot")])
        # metrics.append(["Square Bin 20", "Median Gene types per Spot", bin20_data.get("Median gene type per spot")])

    # --- 3. 生成 DataFrame 并导出 ---
    df = pd.DataFrame(metrics, columns=["Category", "Metric Name", "Value"])
    
    # 导出为 Excel
    df.to_excel(output_name, index=False, engine='openpyxl')
    print(f"Excel文件已生成: {output_name}")

# Example
# export_saw_to_excel('report.json', 'ST_metrics.xlsx')