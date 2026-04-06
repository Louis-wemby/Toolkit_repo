### Construct new Seurat object from RCTD object, accomodated for Full mode.

library(Seurat)
library(Matrix)

# Loading objects
obj <- readRDS("./RCTD.rds")
obj2 <- readRDS("./RData.rds")

# Case1: Add weights
ratios <- as.data.frame(as.matrix(obj@results[["weights"]]))
colnames(ratios) <- paste0("Full_", colnames(ratios))
geoseu1 <- AddMetaData(obj2, metadata = ratios)
if (!is.null(obj@results[["weights_doublet"]])) {
  comp <- as.data.frame(as.matrix(obj@results[["weights_doublet"]]))
  colnames(comp) <- paste0(colnames(comp), "_proportion")
  geoseu1 <- AddMetaData(geoseu1, metadata = comp)
} else {
  message("Notice: Running Full Mode, skip weights_doublet")
}

meta <- geoseu1@meta.data
if ("spot_class" %in% colnames(meta)) {
  meta <- meta[which(!is.na(meta$spot_class)), ]
} else {
  meta <- meta[rownames(ratios), ]
}
meta$barcode <- rownames(meta)

write.csv(meta, file = "meta_weights.csv", quote = FALSE, row.names = FALSE)
saveRDS(geoseu1, file = "RCTD_full.weights.rds", compress = TRUE)

# Case2: Specifying Celltypes
weights <- as.matrix(obj@results[["weights"]])
dominant_type <- colnames(weights)[max.col(weights, ties.method = "first")]
ct_manual <- data.frame(
  first_type = dominant_type,
  spot_class = "classified",
  row.names = rownames(weights),
  stringsAsFactors = FALSE
)

geoseu1 <- AddMetaData(obj2, metadata = ct_manual)
ratios <- as.data.frame(weights)
colnames(ratios) <- paste0("Full_", colnames(ratios))
geoseu1 <- AddMetaData(geoseu1, metadata = ratios)

if (!is.null(obj@results[["weights_doublet"]])) {
  comp <- as.data.frame(as.matrix(obj@results[["weights_doublet"]]))
  colnames(comp) <- paste0(colnames(comp), "_proportion")
  geoseu1 <- AddMetaData(geoseu1, metadata = comp)
} else {
  message("Notice: weights_doublet is NULL in Full Mode, skipping.")
}

meta <- geoseu1@meta.data
meta <- meta[which(!is.na(meta$spot_class)), ]
meta$barcode <- rownames(meta)

write.csv(meta, file = "meta_celltype.csv", quote = FALSE, row.names = FALSE)
saveRDS(geoseu1, file = "RCTD_full.celltype.rds", compress = TRUE)