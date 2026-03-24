# Dealing with Tables

Scripts in this repo handle table-related issues. Supported formats include `.csv`, `.tsv`, `.txt`, `.xlsx`, etc.

## Navi

- [Dealing with Tables](#dealing-with-tables)
  - [Navi](#navi)
  - [0.测序数据统计表格的生成](#0测序数据统计表格的生成)
    - [Usage](#usage)
  - [1.测序数据表格转换为输入表格](#1测序数据表格转换为输入表格)
    - [Usage](#usage-1)
  - [2.单细胞流程分析结果指标提取](#2单细胞流程分析结果指标提取)
    - [Usage](#usage-2)

---

## 0.测序数据统计表格的生成

根据芯片号与物种的对应关系和下机交付的`Sequencing data.xlsx`表格，可以利用脚本`0_seqStats_gen.py`从中提取某一物种的全部下机数据，整理为可直接通过“数据管理-添加文件-集群上传”挂载到相应文件夹下存储的表格（可能需要复制到`fastqImport.xlsx`模板表格中）.关键列名：二级路径（`Secondary Path`），时空芯片号（`SN`），芯片号（`chip number`），Barcode 号（`Barcode number`），泳道（`Lane`）等等.

### Usage

查看`0_seqStats_gen.py`的用法与参数说明：

```bash
python 0_seqStats_gen.py -h
```

使用示例：

```bash
python 0_seqStats_gen.py \
  -i ../SeqStats.csv \
  -o SpeciesName_delivered.xlsx \
  --filter_species "SpeciesName" \
  --sample_name "Species_Tissue_" \
  --species "SpeciesName" \
  --tissue "TissueName"
```

**代码亮点：**

- 可根据“物种”列筛选出对应物种的下机数据.
- 仅筛选状态为 "delivered"，即已交付的下机数据.
- 对于`Barcode number`为诸如`45~48`格式的，自动拆分为多条数据.

## 1.测序数据表格转换为输入表格

下机的测序数据需要我们手动挂载上传到云平台对应项目的数据管理下，挂载时选择“批量上传”，上传提前整理好的表格（表格 A）即可一次性传输下机数据。在投递流程分析（`SAW_spatial_scRNA`或`SAW-ST`）时，同样可以“表格数据输入”（表格 B）的方式入参.然而尽管表格 A 与表格 B 的表头有部分重叠之处，由于文件路径的变动，重新填写表格 B 显得较为繁琐.可通过脚本 `1_process_inputExcel.py`读取表格 A 的各列内容，自动填写进表格 B，同时实现特殊路径的修改与添加.表格 B 的模板可以在数据管理-表格下导出.

### Usage

查看`1_process_inputExcel.py`的用法与参数说明：

``` bash
python 1_process_inputExcel.py -h
```

使用示例:

``` bash
python 1_process_inputExcel.py \
  -a Sp2-fovea.xlsx Sp2-peri2.xlsx \
  -b template.xlsx \
  -o Sp2_SAW_spatial_scRNA_V2_batch2.xlsx \
  -p "/Files/snRNA-seq_Data/Specie_name" \
  -r "/Files/Species_name/STAR" \
  --mem 120 \
  --sc_mem 80 \
  --organism "Species_name" \
  --tissue "Tissue_name" 
```

## 2.单细胞流程分析结果指标提取

在运行完`spatial_scRNA-V2`流程分析后，会生成相应的`.html`报告文件，从中提取单细胞质控后的相关指标，可利用脚本`2_extract_metrics.py`实现。导出的格式为 Excel 表格.

### Usage

```bash
python 2_extract_metrics.py \
  -i /Files/ResultData/.../SpeciesName/
  -o summary_metrics.xlsx
```

这里我们只需输入对应任务输出目录中`task ID`的前一级目录，代码即可遍历检索全部子文件夹.

<div align="right"><a href="#navi">⬆ Back to top</a></div>
