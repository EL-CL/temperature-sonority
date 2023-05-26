library(lmerTest)
library(ggplot2)
library(ggrepel)
library(ggeffects)
library(dplyr)
library(effects)
library(patchwork)


# Read csv files

d_mac <- read.csv(file = "data_macroarea.csv")
d_fam <- read.csv(file = "data_family.csv")
d_all <- read.csv(file = "data.csv")

d_mac$Macroarea <- sub("Am", "\nAm", d_mac$Macroarea)
d_all$Macroarea <- sub("Am", "\nAm", d_all$Macroarea)
d_mac_mean <- d_mac %>% filter(Method == "mean")
d_mac_med <- d_mac %>% filter(Method == "median")
d_fam_mean <- d_fam %>% filter(Method == "mean")


# Fit models

m_mac_mean <- lm(Index0 ~ T, data = d_mac_mean)
m_mac_med <- lm(Index0 ~ T, data = d_mac_med)
m_fam <- lm(Index0_trans ~ T_trans, data = d_fam_mean)
m_all <- lmer(Index0_trans ~ T_trans + (T_trans | Family), data = d_all)
m_all_2 <- lmer(Index0_trans ~ T_trans + (1 | Family), data = d_all)
anova(m_all, m_all_2)  # p < 0.001. Use m_all

summary(m_mac_mean)
summary(m_mac_med)
summary(m_fam)
summary(m_all)


# Plot distribution

order <- d_mac_med[order(d_mac_med$Index0), ]$Macroarea
d_mac$Macroarea <- factor(d_mac$Macroarea, levels = order) # reorder by medians
d_all$Macroarea <- factor(d_all$Macroarea, levels = order)

p01 <- ggplot(d_all, aes(x = Macroarea, y = T, color = Macroarea)) +
  geom_violin(scale = "width", width = 0.8) +
  geom_boxplot(width = 0.09, lwd = 0.4, outlier.shape = NA, coef = 0) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black"),
        legend.position = "none", axis.title.x = element_blank()) +
  coord_trans(y = scales::exp_trans(1.06)) +
  scale_y_continuous(breaks = c(-20,-10,0,10,15,20,25,30)) +
  ylab("MAT (°C)")
p02 <- ggplot(d_all, aes(x = Macroarea, y = Index0, color = Macroarea)) +
  geom_violin(scale = "width", width = 0.75) +
  geom_boxplot(width = 0.09, lwd = 0.4, outlier.shape = NA, coef = 0) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black"),
        legend.position = "none", axis.title.x = element_blank()) +
  ylab("MSI")
p01 + p02
# Then, save as PDF (7 * 4 inches)


# Plot correlation

e_mac_mean <- ggpredict(m_mac_mean, terms = "T")
e_mac_med <- ggpredict(m_mac_med, terms = "T")
e_fam <- ggpredict(m_fam, terms = "T_trans")
e_all <- ggpredict(m_all, terms = "T_trans")

p1_labels <- c("Mean (solid line)", "Median (dashed line)")
p1 <- ggplot() +
  geom_line(data = e_mac_mean, aes(x, predicted)) +
  geom_line(data = e_mac_med, aes(x, predicted), linetype = "dashed") +
  geom_point(data = d_mac, aes(T, Index0, color = Macroarea,
                               shape = Method, stroke = Method, size = Method)) +
  scale_shape_manual(labels = p1_labels, values = c(16, 3)) +
  scale_size_manual(labels = p1_labels, values = c(1.5, 1.1)) +
  scale_discrete_manual(labels = p1_labels, aesthetics = "stroke", values = c(1, 0.8)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black"),
        legend.title = element_blank(),
        legend.spacing.y = unit(-0.5, "cm"), legend.margin = margin(),
        plot.title = element_text(hjust = 0.5)) +
  coord_cartesian(ylim = c(9, 11)) +
  ggtitle("Macroareas") +
  xlab("MAT (°C)") + ylab("MSI")
p2 <- ggplot() +
  geom_point(data = d_fam_mean, aes(T_trans, Index0_trans), color = "blue", alpha = 0.7) +
  geom_ribbon(data = e_fam, aes(x, ymin = conf.low, ymax = conf.high), alpha = 0.35) +
  geom_line(data = e_fam, aes(x, predicted)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black"),
        plot.title = element_text(hjust = 0.5)) +
  ggtitle("Families") +
  xlab("MAT (transformed)") + ylab("MSI (transformed)")
p3 <- ggplot() +
  geom_point(data = d_all, aes(T_trans, Index0_trans), color = "blue", alpha = 0.08) +
  geom_ribbon(data = e_all, aes(x, ymin = conf.low, ymax = conf.high), alpha = 0.35) +
  geom_line(data = e_all, aes(x, predicted)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black"),
        plot.title = element_text(hjust = 0.5)) +
  coord_cartesian(xlim = c(-2.2, 2)) +
  ggtitle("All Doculects") +
  xlab("MAT (transformed)") + ylab("MSI (transformed)")
p1 + guide_area() + p2 + p3 + plot_layout(guides = "collect", design = "AAB#\nCCDD")
# Then, save as PDF (6 * 6 inches)


# Linear correlation between different sonority scales

r2s <- matrix(0, 5, 5)
r2s_trans <- matrix(0, 5, 5)
for (i in 0:4) {
  for (j in 0:4) {
    if (i == j) next
    fomula <- paste("Index", i, " ~ ", "Index", j, sep = "")
    fomula_trans <- paste("Index", i, "_trans ~ ", "Index", j, "_trans", sep = "")
    r2s[i + 1, j + 1] <- summary(lm(fomula, data = d_all))$r.squared
    r2s_trans[i + 1, j + 1] <- summary(lm(fomula_trans, data = d_all))$r.squared
  }
}
print(r2s)

ggplot(d_all, aes(x = Index0, y = Index4)) +
  geom_point() +
  geom_smooth(method = lm)
m_in0_in4 <- lm(Index4 ~ Index0, data = d_all)
summary(m_in0_in4)

# Linear correlation between mean annual range or standard deviation

m_diff <- lm(T_diff ~ T, data = d_all)
m_sd <- lm(T_sd ~ T, data = d_all)
summary(m_diff)$r.squared
summary(m_sd)$r.squared
ggplot(d_all, aes(x = T, y = T_diff)) + geom_point()
ggplot(d_all, aes(x = T, y = T_sd)) + geom_point()

m_all_diff <- lmer(Index0_trans ~ T_trans + T_diff + (T_trans | Family), data = d_all)
m_all_sd <- lmer(Index0_trans ~ T_trans + T_sd + (T_trans | Family), data = d_all)
summary(m_all_diff)
summary(m_all_sd)
anova(m_all_diff, m_all)  # p = 0.222
anova(m_all_sd, m_all)  # p = 0.169
