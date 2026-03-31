library(Seurat)
library(Matrix)

# Loading mapping
mapping <- read.table("./Gallus_gallus.rmRepeatedGeneName.gtf.gid.txt", header = FALSE, sep = "\t", stringsAsFactors = FALSE)
seurat_obj <- readRDS("./Gallus.Y01453JDKE_bs11md9_bin20_RCTD_doublet.celltype.rds")

# If header=FALSE, add colnames
colnames(mapping) <- c("gene_id", "gene_name")

# Construct new Seurat object
counts <- GetAssayData(seurat_obj, assay = "Spatial", slot = "counts")
common_genes <- intersect(rownames(counts), mapping$gene_id)
counts <- counts[common_genes, ]
new_names <- mapping$gene_name[match(common_genes, mapping$gene_id)]
counts_new <- rowsum(as.matrix(counts), group = new_names)

new_seurat <- CreateSeuratObject(counts = counts_new, meta.data = seurat_obj@meta.data)

# Check for image
if ("spatial" %in% names(seurat_obj@images)) {
  new_seurat@images <- seurat_obj@images
}

saveRDS(new_seurat, "/data/work/Gallus/Gallus.Y01453JDKE_bs11md9_bin20_RCTD_doublet.celltype.gn.rds")

# Check gene names
new_seurat[["RNA"]]@meta.features