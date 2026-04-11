library(ggplot2)
library(dplyr)

# Read sector counts data
df_Spe1 <- read.table("Spe1_sector_long_counts.txt", header = TRUE, sep = "\t", check.names = FALSE)
df_Spe2 <- read.table("Spe2_sector_long_counts.txt", header = TRUE, sep = "\t", check.names = FALSE)
df_Spe3 <- read.table("SPe2_sector_long_counts.txt", header = TRUE, sep = "\t", check.names = FALSE)

all_species_counts <- bind_rows(
  df_Spe1 %>% mutate(species = "Species 1"),
  df_Spe2 %>% mutate(species = "Species 2"),
  df_Spe3 %>% mutate(species = "Species 3")
)

species_order <- c("Species 1", "SPecies 2", "Species 3")
all_species_counts$species <- factor(all_species_counts$species,
                                     levels = species_order)

celltype_order <- c("Photoreceptor_Cones",
                    "Photoreceptor_Rods",
                    "Photoreceptors",
                    "Horizontal_Cells",
                    "Bipolar_Cells",
                    "Muller_Glia",
                    "Amacrine_Cells",
                    "Oligodendrocytes",
                    "Retinal_Ganglion_Cells")

all_species_counts$cluster <- factor(all_species_counts$cluster,
                                     levels = rev(celltype_order))

cols <- c("Retinal_Ganglion_Cells" = "#DC143C",
          "Oligodendrocytes" = "#20B2AA",
          "Amacrine_Cells" = "#FFA500",
          "Muller_Glia" = "#9370DB",
          "Bipolar_Cells" = "#98FB98",
          "Horizontal_Cells" = "#F08080",
          "Photoreceptor_Rods" = "#1E90FF",
          "Photoreceptor_Cones" = "#F0E68C")

# Plotting
pdf("All_Species_N2T_axis_celltype_barplot.pdf", width = 10, height = 12)

ggplot(all_species_counts, aes(x = sector, y = cell_count, fill = cluster)) +
  geom_bar(stat = "identity", position = "stack", width = 0.9) +
  facet_wrap(~species, ncol = 1, scales = "free") +
  labs(
    title = "Retinal Cell Distribution: Nasal to Temporal",
    x = "N -> T",
    y = "Cell Count",
    fill = "Cell Type"
  ) +
  theme_classic() +
  theme(
    plot.title = element_text(hjust = 0.5, face = "bold", size = 16),
    axis.title = element_text(size = 12),
    axis.text = element_text(size = 10),
    legend.position = "right",
    strip.text = element_text(size = 12, face = "bold"),
    strip.background = element_rect(color = "black", fill = "gray90"),
    panel.grid.major = element_blank(),
    panel.grid.minor = element_blank(),
    axis.line = element_line(color = "black", linewidth = 0.5),
    axis.text.x = element_blank(),
    axis.ticks.x = element_blank()
  ) +
  scale_fill_manual(values = cols) +
  scale_x_discrete(expand = c(0, 0)) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.05)))

dev.off()
