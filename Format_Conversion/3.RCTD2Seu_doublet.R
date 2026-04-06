### Construct new Seurat object from RCTD object, accomodated for Doublet mode.

library(Seurat)
library(Matrix)

# Loading objects
obj <- readRDS("./RCTD.rds")
obj2 <- readRDS("./RData.rds")

ct <- obj@results[["results_df"]]
geoseu1 <- AddMetaData(obj2, metadata = ct)
ratios <- as.data.frame(as.matrix(obj@results[["weights"]]))
geoseu1 <- AddMetaData(geoseu1, metadata = ratios)
comp <- as.data.frame(as.matrix(obj@results[["weights_doublet"]]))
colnames(comp) <- paste0(colnames(comp), "_proportion")
geoseu1 <- AddMetaData(geoseu1, metadata = comp)

meta <- geoseu1@meta.data
meta <- meta[which(!is.na(meta$spot_class)), ]
meta$orig.ident <- rownames(meta)

write.csv(meta, file = "meta.csv", quote = FALSE, row.names = FALSE)
saveRDS(geoseu1, file = "RCTD_doublet.celltype.rds", compress = TRUE)