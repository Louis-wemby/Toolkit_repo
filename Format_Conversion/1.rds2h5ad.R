library(Seurat)
library(reticulate)

object <- readRDS("RData.rds")

genes <- as.data.frame(rownames(object), row.names = rownames(object))
names(genes) <- "Gene"

# Add Celltype information
cells <- data.frame(CellID = colnames(object),
                    Celltype = object@meta.data$first_type,
                    row.names = colnames(object))

# If your Seurat obj looks like this:
# Active assay: Spatial
#  1 image present: slice1
row <- object@images[["slice1"]]@coordinates$row
col <- object@images[["slice1"]]@coordinates$col
coordinates <- list(matrix(c(row, col), ncol = 2))
names(coordinates) <- "spatial"

# If your Seurat obj looks like this:
# Active assay: RNA
#  1 dimensional reduction calculated: spatial
# Use the code below:

# coords <- as.data.frame(object[["spatial"]]@cell.embeddings)
# row <- coords$SPATIAL_1
# col <- coords$SPATIAL_2
# coordinates <- list(matrix(c(row, col), ncol = 2))

anndata <- import("anndata", delay_load = TRUE)
ad <- anndata$AnnData(X = object@assays$Spatial@counts,
                      # or `X = object@assays$RNA@counts`, respectively
                      obs = genes,
                      var = cells,
                      varm = coordinates)

ad <- ad$T
ad$write_h5ad(file.path("AnnData.h5ad"))