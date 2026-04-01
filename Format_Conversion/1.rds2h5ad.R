library(Seurat)
library(reticulate)

object <- readRDS("RData.rds")

genes <- as.data.frame(rownames(object), row.names = rownames(object))
names(genes) <- "Gene"

# Add Celltype information
cells <- data.frame(CellID = colnames(object), Celltype = object@meta.data$first_type, row.names = colnames(object))
row <- object@images[["slice1"]]@coordinates$row
col <- object@images[["slice1"]]@coordinates$col
coordinates <- list(matrix(c(row, col), ncol = 2))
names(coordinates) <- "spatial"

anndata <- import("anndata", delay_load = TRUE)
ad <- anndata$AnnData(X = object@assays$Spatial@counts, obs = genes, var = cells, varm = coordinates)

ad <- ad$T
ad$write_h5ad(file.path("AnnData.h5ad"))