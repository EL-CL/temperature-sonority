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

m_mac_mean <- lm(Index0 ~ T, data = d_mac_mean)
m_mac_med <- lm(Index0 ~ T, data = d_mac_med)
m_fam <- lm(Index0_trans ~ T_trans, data = d_fam_mean)
m_all <- lmer(Index0_trans ~ T_trans + (T_trans | Family), data = d_all)

summary(m_mac_mean)
summary(m_mac_med)
summary(m_fam)
summary(m_all)

e_mac_mean <- ggpredict(m_mac_mean, terms = "T")
e_mac_med <- ggpredict(m_mac_med, terms = "T")
e_fam <- ggpredict(m_fam, terms = "T_trans")
e_all <- ggpredict(m_all, terms = "T_trans")

order <- d_mac_mean[order(d_mac_mean$Index0), ]$Macroarea
d_mac$Macroarea <- factor(d_mac$Macroarea, levels = order)
d_all$Macroarea <- factor(d_all$Macroarea, levels = order)


# Plot distribution

p01 <- ggplot(d_all, aes(x = Macroarea, y = T, color = Macroarea)) +
  geom_violin() +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        legend.position = "none", axis.title.x = element_blank()) +
  ylab("MAT")
p02 <- ggplot(d_all, aes(x = Macroarea, y = Index0, color = Macroarea)) +
  geom_violin() + geom_boxplot(width = 0.1, outlier.shape = NA, coef = 0) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        legend.position = "none", axis.title.x = element_blank()) +
  ylab("MSI")
p01 + p02
# Save to PDF: 7 * 4 inches


# Plot correlation

p1 <- ggplot() +
  geom_line(data = e_mac_mean, aes(x, predicted)) +
  geom_line(data = e_mac_med, aes(x, predicted), linetype = "dashed") +
  geom_point(data = d_mac, aes(T, Index0, color = Macroarea, shape = Method)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        legend.title = element_blank(),
        legend.spacing.y = unit(-0.5, "cm"), legend.position = c(1.2, 0.5),
        plot.title = element_text(hjust = 0.5)) +
  coord_cartesian(ylim = c(9, 11)) +
  ggtitle("Macroareas") +
  xlab("MAT") + ylab("MSI")
p2 <- ggplot() +
  geom_point(data = d_fam_mean, aes(T_trans, Index0_trans), color = "blue", alpha = 0.7) +
  geom_ribbon(data = e_fam, aes(x, ymin = conf.low, ymax = conf.high), alpha = 0.35) +
  geom_line(data = e_fam, aes(x, predicted)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(), plot.title = element_text(hjust = 0.5)) +
  ggtitle("Families") +
  xlab("MAT") + ylab("MSI")
p3 <- ggplot() +
  geom_point(data = d_all, aes(T_trans, Index0_trans), color = "blue", alpha = 0.08) +
  geom_ribbon(data = e_all, aes(x, ymin = conf.low, ymax = conf.high), alpha = 0.35) +
  geom_line(data = e_all, aes(x, predicted)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(), plot.title = element_text(hjust = 0.5)) +
  coord_cartesian(xlim = c(-2.2, 2)) +
  ggtitle("All Doculects") +
  xlab("MAT") + ylab("MSI")
p1 + guide_area() + p2 + p3 + plot_layout(guides = "collect", design = "AAAAB###\nCCCCDDDD")
# Save to PDF: 6 * 6 inches


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
anova(m_all_diff, m_all)
anova(m_all_sd, m_all)
