# Dealing with Tables

Scripts in this repo handle table-related issues. Supported formats include `.csv`, `.tsv`, `.txt`, `.xlsx`, etc.

## Navi

- [Dealing with Tables](#dealing-with-tables)
  - [Navi](#navi)
  - [0.测序数据表格转换](#0测序数据表格转换)
    - [Usage](#usage)

---

## 0.测序数据表格转换

下机的测序数据需要我们手动挂载上传到云平台对应项目的数据管理下，挂载时选择“批量上传”，上传提前整理好的表格（表格 A）即可一次性传输下机数据。在投递流程分析（`SAW_spatial_scRNA`或`SAW-ST`）时，同样可以“表格数据输入”（表格 B）的方式入参。然而尽管表格 A 与表格 B 的表头有部分重叠之处，由于文件路径的变动，重新填写表格 B 显得较为繁琐。可通过脚本 `0_process_inputExcel.py`读取表格 A 的各列内容，自动填写进表格 B，同时实现特殊路径的修改与添加。表格 B 的模板可以在数据管理-表格下导出。

### Usage

查看`0_process_inputExcel.py`的用法与参数说明：

``` bash
python 0_process_inputExcel.py -h
```

使用示例:

``` bash
python 0_process_inputExcel.py \
  -a Sp2-fovea.xlsx Sp2-peri2.xlsx \
  -b template.xlsx \
  -o Sp2_SAW_spatial_scRNA_V2_batch2.xlsx \
  -p "/Files/snRNA-seq_Data/Species_name" \
  -r "/Files/Species_name/STAR" \
  --mem 120 \
  --sc_mem 80 \
  --organism "Species_name" \
  --tissue "Tissue_name" 
```

<div align="right"><a href="#navi">⬆ Back to top</a></div>
