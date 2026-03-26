import os
import re
import argparse
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

# 定义需要提取的所有指标
TARGET_METRICS = [
    "Correction",
    "Estimated Number of Raw cells",
    "Mean MID of Raw Cells",
    "Mean Gene of Raw Cells",
    "Median MID of Raw Cells",
    "Median Gene of Raw Cells",
    "Doublet number",
    "Doublet rate",
    "Estimated Number of Filtered cells",
    "Mean MID of Filtered Cells",
    "Mean Gene of Filtered Cells",
    "Median MID of Filtered Cells",
    "Median Gene of Filtered Cells",
    "Mean cell area of Filtered cells",
    "Median cell area of Filtered cells",
    "Mapped reads",
    "Reads number per cell",
    "Reads in cell / Mapped reads",
    "Unique reads in cell / Unique reads",
    "Unique reads / Total reads"
]

def clean_text(text):
    """辅助函数：清理HTML文本中的多余空格并转为小写，以便于精确匹配"""
    return re.sub(r'\s+', ' ', text).strip().lower()

def extract_metrics_from_html(file_path):
    """
    解析 HTML 文件并提取指定的质控指标
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # 初始化结果字典，默认值为 NA
    results = {k: "NA" for k in TARGET_METRICS}
    
    # 遍历所有的 HTML 表格行
    for tr in soup.find_all('tr'):
        cells = tr.find_all(['td', 'th'])
        # 确保该行至少有两列（标签列和数值列）
        if len(cells) >= 2:
            raw_label = cells[0].get_text(strip=True)
            val = cells[1].get_text(strip=True)
            
            label_cleaned = clean_text(raw_label)
            
            # 匹配目标指标
            for key in TARGET_METRICS:
                if results[key] == "NA":
                    key_cleaned = clean_text(key)
                    # 采用完全相等或包含关系进行匹配
                    if key_cleaned == label_cleaned or label_cleaned.startswith(key_cleaned):
                        results[key] = val
                        break
                        
    return results

def main():
    parser = argparse.ArgumentParser(description="从特定的 scRNA-seq 目录结构中提取 HTML 报告指标并汇总为 Excel。")
    parser.add_argument("-i", "--input_dir", required=True, 
                        help="大路径，例如: /Files/ResultData/.../Larus_argentatus/")
    parser.add_argument("-o", "--output_file", required=True, 
                        help="输出的 Excel 文件路径，例如: summary_metrics.xlsx")
    
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    if not input_dir.is_dir():
        print(f"[!] 错误: 指定的输入目录不存在 '{input_dir}'")
        return

    data = []
    print(f"[...] 正在扫描路径: {input_dir}")
    
    # 1. 遍历大路径下的所有子级文件夹 (即 Wxxxx 文件夹)
    for w_dir in input_dir.iterdir():
        if w_dir.is_dir():
            sample_name = w_dir.name # 取值为 W2026...
            
            # 2. 定位到目标 report 文件夹
            report_dir = w_dir / "scRNA_result" / "report"
            
            if report_dir.exists() and report_dir.is_dir():
                # 3. 提取该目录下的 .html 文件
                for html_file in report_dir.glob("*.html"):
                    if ".report.html" in html_file.name:
                        continue # 跳过 .report.html 文件
                    
                    sn_number = html_file.stem # 获取文件名 Y40241A1 作为 SN number
                    
                    try:
                        # 提取网页内的指标
                        metrics = extract_metrics_from_html(html_file)
                        
                        # 组装最终的数据字典（保证列的顺序）
                        row_data = {
                            "Sample Name": sample_name,
                            "SN number": sn_number
                        }
                        row_data.update(metrics) # 合并抓取到的具体指标
                        
                        data.append(row_data)
                        print(f"[✔︎] 成功解析: [{sample_name}] -> {html_file.name}")
                    except Exception as e:
                        print(f"[!] 解析失败 {html_file.name}: {e}")

    # 4. 导出到 Excel
    if data:
        df = pd.DataFrame(data)
        df.to_excel(args.output_file, index=False)
        print(f"[✓] 提取完成！共处理了 {len(data)} 个 HTML 报告。")
        print(f"结果已保存至: {Path(args.output_file).resolve()}")
    else:
        print("[!] 未找到符合要求的 HTML 文件，请检查路径层级是否完全符合: 大路径/task_ID/scRNA_result/report/*.html")

if __name__ == "__main__":
    main()
