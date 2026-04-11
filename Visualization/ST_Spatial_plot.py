import scanpy as sc
import matplotlib.pyplot as plt
import pandas as pd

adata = sc.read_h5ad("RCTD_doublet.celltype.h5ad")
adata = adata[adata.obs["Celltype"].notna()].copy()

coords = adata.obsm["spatial"]
df = pd.DataFrame({
    "x": coords[:,0],
    "y": coords[:,1],
    "celltype": adata.obs["Celltype"].values
})

celltype_colors = {
    "Retinal_Ganglion_Cells": "#DC143C",
    "Oligodendrocytes": "#20B2AA",
    "Amacrine_Cells": "#FFA500",
    "Muller_Glia": "#9370DB",
    "Bipolar_Cells": "#98FB98",
    "Horizontal_Cells": "#F08080",
    "Photoreceptor_Rods": "#1E90FF",
    "Photoreceptor_Cones": "#F0E68C"
}

# Method 1: Scatter plot
plt.figure(figsize=(16,8))

for ct in celltype_colors:
    
    sub = df[df["celltype"] == ct]
    
    plt.scatter(
        sub["x"],
        sub["y"],
        s=0.3,
        c=celltype_colors[ct],
        edgecolors='none',
        label=ct
    )

# plt.gca().invert_yaxis()
plt.axis("equal")

plt.legend(
    bbox_to_anchor=(1.05,1),
    loc="upper left",
    markerscale=20,
)

plt.tight_layout()

plt.savefig("Spatial_celltype_dotplot.pdf", dpi = 300, bbox_inches="tight")
plt.show()

# Method 2: sc.pl.spatial
sc.pl.spatial(
    adata,
    color = 'Celltype',
    palette = celltype_colors,
    spot_size = 20,
    size = 0.05,
    vmax = 1,
    img = None,
    save = "RCTD_spatial.pdf"
)