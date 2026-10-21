library(Hmisc)
library(psych)

library(ggridges)
library(ggplot2)
library(ggridges)
library(dplyr)
library(tidyr)
library(viridis)
library(hrbrthemes)

# install.packages("extrafont")
library(extrafont)
#font_import() 
loadfonts(device = "pdf")  # Load fonts for PDF output
library(showtext)


##############################################
# SUMMARY STATISTICS TABLE
##############################################

data <- read.csv("/Users/mrobredo23/OULU/2025_projects/refactoring-ripple-effects/basic_statistics_table.csv")
head(data)

summary(data)
describe(data)
descriptive_stats <- psych::describe(data)  # The most complete one
write.csv(descriptive_stats, 
          file = "/Users/mrobredo23/OULU/2025_projects/refactoring-ripple-effects/descriptive_stats_table.csv",
          row.names = TRUE)

##############################################
# PLOTTING STATISTICS 
##############################################

# "Creation.year" - Categorical
# "Age" - Continuous                         
# "Size" - Continuous
# "Main.Language" - Categorical
# "Stars" - Continuous                       
# "Open.issues" - Continuous
# "Closed.issues" - Continuous
# "Overall.issues" - Continuous              
# "Commits" - Continuous
# "Contributors" - Continuous
# "X..Languages" - Continuous                
# "X..Refactoring.Types" - Continuous
# "X..Mined.Refactoring.Commits" - Continuous
# "X..Mined.Refactorings" - Continuous

# Bin the Age variable into intervals
data$Age_bin <- cut(data$Age,
                    breaks = seq(0, ceiling(max(data$Age, na.rm = TRUE)), by = 3),
                    include.lowest = TRUE,
                    right = FALSE)

# Select only continuous variables (excluding IDs or factors)
continuous_vars <- data %>%
  select(Age_bin, Stars, Overall.issues, Commits, Size, `X..Languages`, `X..Refactoring.Types`, `X..Mined.Refactorings`, X..Mined.Refactoring.Commits) %>%
  rename(
    Issues = Overall.issues
  ) %>%
  pivot_longer(cols = -c(Age_bin), names_to = "Metric", values_to = "Value") %>%
  drop_na()

# Filter only selected metrics for the ridge plot
filtered_vars <- continuous_vars %>%
  filter(Metric %in% c("Commits", "Issues", "Size", "Stars"))

font_add_google(name = "PT Serif", family = "ptserif")
showtext_auto()

# Ridge plot with lighter color
ridge_plot <- ggplot(filtered_vars, aes(x = Value, y = Age_bin)) +
  geom_density_ridges(scale = 3, rel_min_height = 0.01, fill = "azure3", color = "black") +
  facet_wrap(~ Metric, scales = "free_x", ncol = 1) +
  labs(
    title = "",
    x = "Density of projects",
    y = "Project Age"
  ) +
  theme_minimal(base_size = 14, base_family = "ptserif") +
  theme(
    axis.title.x = element_text(size = 16, face = "bold"),
    axis.title.y = element_text(size = 16, face = "bold"),
    strip.text.x = element_text(size = 14, face = "bold"),
    legend.position = "none",
    panel.spacing = unit(0.1, "lines"),
    axis.text.y = element_text(size = 12)
  )

ggsave("/Users/mrobredo23/Library/CloudStorage/OneDrive-UniversityofOuluandOamk/PhD/2025_papers/RR-extensions/ICSME_EMSE/figuresridge_plot_output.pdf", 
       plot = ridge_plot, width = 8, height = 10)
showtext_auto(FALSE)

# Set font globally for base R plots
par(family = "Times")
# Plotting creation year plot
hist(data$Creation.year, ylab = "# Projects", xlab = "Creation years", 
     main = "", col = "azure3", freq = T,
     cex.lab=1.2, font.lab=2, breaks=20)

plot(data$Commits)
