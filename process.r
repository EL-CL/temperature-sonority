library(lmerTest)
library(ggplot2)
library(ggrepel)
library(ggeffects)
library(dplyr)
library(effects)
library(patchwork)
library(tibble)


# Read csv files
# ==============

d_mac <- read.csv(file = "data/data_macroarea.csv")
d_fam <- read.csv(file = "data/data_family.csv")
d_gen <- read.csv(file = "data/data_genus.csv")
d_all <- read.csv(file = "data/data.csv")

d_mac$Macroarea <- sub("Am", " Am", d_mac$Macroarea)
d_all$Macroarea <- sub("Am", " Am", d_all$Macroarea)
d_mac_mean <- d_mac %>% filter(Method == "mean")
d_mac_med <- d_mac %>% filter(Method == "median")
d_fam_mean <- d_fam %>% filter(Method == "mean")
d_gen_mean <- d_gen %>% filter(Method == "mean")

order <- d_mac_med[order(d_mac_med$Index0), ]$Macroarea
d_mac$Macroarea <- factor(d_mac$Macroarea, levels = order) # reorder by medians
d_all$Macroarea <- factor(d_all$Macroarea, levels = order)


# Fit models
# ==========

m_mac_mean <- lm(Index0 ~ T, data = d_mac_mean)
m_mac_med <- lm(Index0 ~ T, data = d_mac_med)
m_fam <- lm(Index0_trans ~ T_trans, data = d_fam_mean)
m_gen <- lmer(Index0_trans ~ T_trans + (T_trans | Family), data = d_gen)
m_gen_1 <- lmer(Index0_trans ~ T_trans + (1 | Family), data = d_gen)
m_all <- lmer(Index0_trans ~ T_trans + (T_trans | Family), data = d_all)
m_all_1 <- lmer(Index0_trans ~ T_trans + (1 | Family), data = d_all)
anova(m_gen, m_gen_1)  # p < 0.001. Use m_gen
anova(m_all, m_all_1)  # p < 0.001. Use m_all
m_all_lm <- lm(Index0_trans ~ T_trans, data = d_all)

summary(m_mac_mean)
summary(m_mac_med)
summary(m_fam)
summary(m_gen)
summary(m_all)
summary(m_all_lm)


# Plot distribution
# =================

p01 <- ggplot(d_all, aes(x = Macroarea, y = T, color = Macroarea)) +
  geom_violin(scale = "width", width = 0.8) +
  geom_boxplot(width = 0.09, lwd = 0.4, outlier.shape = NA, coef = 0) +
  scale_x_discrete(labels = sub(" ", "\n", levels(d_all$Macroarea))) +
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
  scale_x_discrete(labels = sub(" ", "\n", levels(d_all$Macroarea))) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black"),
        legend.position = "none", axis.title.x = element_blank()) +
  ylab("MSI")
p01 + p02
# Then, save as distribution.pdf (7 * 4 inches)


# Plot correlation
# ================

e_mac_mean <- ggpredict(m_mac_mean, terms = "T")
e_mac_med <- ggpredict(m_mac_med, terms = "T")
e_fam <- ggpredict(m_fam, terms = "T_trans")
e_gen <- ggpredict(m_gen, terms = "T_trans")
e_all_lm <- ggpredict(m_all_lm, terms = "T_trans")
e_all_lmer <- ggpredict(m_all, terms = "T_trans")

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
        legend.spacing.y = unit(0, "cm"), legend.margin = margin(),
        plot.title = element_text(hjust = 0.5)) +
  coord_cartesian(ylim = c(9, 11)) +
  ggtitle("Macroareas") +
  xlab("MAT (°C)") + ylab("MSI")
p2 <- ggplot() +
  geom_point(data = d_fam_mean, aes(T_trans, Index0_trans), color = "blue", alpha = 0.7) +
  geom_line(data = e_fam, aes(x, predicted)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black"),
        plot.title = element_text(hjust = 0.5)) +
  ggtitle("Families") +
  xlab("MAT (transformed)") + ylab("MSI (transformed)")
p3 <- ggplot() +
  geom_point(data = d_all, aes(T_trans, Index0_trans), color = "blue", alpha = 0.08) +
  geom_line(data = e_all_lmer, aes(x, predicted), color = "darkorange4") +
  geom_line(data = e_all_lm, aes(x, predicted)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black"),
        plot.title = element_text(hjust = 0.5)) +
  coord_cartesian(xlim = c(-2.2, 2)) +
  ggtitle("All Doculects") +
  xlab("MAT (transformed)") + ylab("MSI (transformed)")
p1 + guide_area() + p2 + p3 + plot_layout(guides = "collect", design = "AAB#\nCCDD")
# Then, save as correlation.pdf (6 * 6 inches)

ggplot() +
  geom_point(data = d_gen_mean, aes(T_trans, Index0_trans), color = "blue", alpha = 0.7) +
  geom_ribbon(data = e_gen, aes(x, ymin = conf.low, ymax = conf.high), alpha = 0.35) +
  geom_line(data = e_gen, aes(x, predicted)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black"),
        plot.title = element_text(hjust = 0.5)) +
  ggtitle("Genera") +
  xlab("MAT (transformed)") + ylab("MSI (transformed)")
# Then, save as correlation_genera.pdf (4 * 4 inches) [not used]


# Correlation with word length
# ============================

m_s_wl_mac <- lm(Index0 ~ WL,  data = d_mac_med)
m_t_wl_mac <- lm(WL ~ T, data = d_mac_med)
m_s_wl_fam <- lm(Index0_trans ~ WL,  data = d_fam_mean)
m_t_wl_fam <- lm(WL ~ T_trans, data = d_fam_mean)
m_s_wl_all <- lm(Index0 ~ WL,  data = d_all)
m_t_wl_all <- lm(WL ~ T_trans, data = d_all)
summary(m_s_wl_mac)
summary(m_t_wl_mac)
summary(m_s_wl_fam)
summary(m_t_wl_fam)
summary(m_s_wl_all)
summary(m_t_wl_all)

p1 <- ggplot(d_mac_med, aes(WL, Index0)) +
  geom_point(color = "blue") +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black")) +
  xlab('Mean word length') + ylab('MSI')
p2 <- ggplot(d_mac_med, aes(T, WL)) +
  geom_point(color = "blue") +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black")) +
  xlab('MAT (°C)') + ylab('Mean word length')
p3 <- ggplot(d_fam_mean, aes(WL, Index0_trans)) +
  geom_point(color = "blue", alpha = 0.6) +
  geom_smooth(method = lm, color = "black", se = F) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black")) +
  xlab('Mean word length') + ylab('MSI (transformed)')
p4 <- ggplot(d_fam_mean, aes(T_trans, WL)) +
  geom_point(color = "blue", alpha = 0.6) +
  geom_smooth(method = lm, color = "black", se = F) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black")) +
  xlab('MAT (transformed)') + ylab('Mean word length')
p1 + p2 + p3 + p4  # Unused
p3 + p4
# Then, save as word_length.pdf (6 * 3 inches)

m_wl_fam_1 <- lm(Index0_trans ~ T_trans * WL, data = d_fam_mean)
m_wl_fam_2 <- lm(Index0_trans ~ T_trans + WL, data = d_fam_mean)
anova(m_wl_fam_1, m_wl_fam_2)  # Not significant. Use 2
m_wl_fam_3 <- lm(Index0_trans ~ T_trans, data = d_fam_mean)
m_wl_fam_4 <- lm(Index0_trans ~ WL, data = d_fam_mean)
anova(m_wl_fam_2, m_wl_fam_3)  # Significant. Use 2
anova(m_wl_fam_2, m_wl_fam_4)  # Significant. Use 2
summary(m_wl_fam_2)

# Unused
m_wl_all_1 <- lmer(Index0_trans ~ T_trans * WL + (T_trans * WL | Family), data = d_all)
m_wl_all_2 <- lmer(Index0_trans ~ T_trans * WL + (T_trans + WL | Family), data = d_all)
m_wl_all_3 <- lmer(Index0_trans ~ T_trans + WL + (T_trans * WL | Family), data = d_all)
m_wl_all_4 <- lmer(Index0_trans ~ T_trans + WL + (T_trans + WL | Family), data = d_all)
m_wl_all_5 <- lmer(Index0_trans ~ T_trans + (T_trans * WL | Family), data = d_all)
anova(m_wl_all_1, m_wl_all_2)  # Significant. Use 1
anova(m_wl_all_1, m_wl_all_3)  # Not significant. Use 3
anova(m_wl_all_3, m_wl_all_4)  # Significant. Use 3
anova(m_wl_all_3, m_wl_all_5)  # Significant. Use 3
summary(m_wl_all_3)


# Linear correlation between different sonority scales (for SI)
# =============================================================

r2s <- matrix(0, 5, 5)
ps <- matrix(0, 5, 5)
r2s_trans <- matrix(0, 5, 5)
ps_trans <- matrix(0, 5, 5)
for (i in 0:4) {
  for (j in 0:4) {
    if (i == j) next
    fomula <- paste("Index", i, " ~ ", "Index", j, sep = "")
    fomula_trans <- paste("Index", i, "_trans ~ ", "Index", j, "_trans", sep = "")
    r2s[i + 1, j + 1] <- summary(lm(fomula, data = d_all))$r.squared
    ps[i + 1, j + 1] <- summary(lm(fomula, data = d_all))$coefficients[8]
    r2s_trans[i + 1, j + 1] <- summary(lm(fomula_trans, data = d_all))$r.squared
    ps_trans[i + 1, j + 1] <- summary(lm(fomula_trans, data = d_all))$coefficients[8]
  }
}
print(r2s)
print(ps)
print(r2s_trans)
print(ps_trans)

ggplot(d_all, aes(x = Index1, y = Index3)) + geom_point() + geom_smooth(method = lm)
ggplot(d_all, aes(x = Index0, y = Index4)) + geom_point() + geom_smooth(method = lm)
m_in0_in4 <- lm(Index4 ~ Index0, data = d_all)
summary(m_in0_in4)


# Linear correlation between mean annual range or standard deviation
# ==================================================================

m_all_diff_sd <- lm(T_sd ~ T_diff, data = d_all)
summary(m_all_diff_sd)

m_fam_diff_0 <- lm(Index0_trans ~ T_trans * T_diff, data = d_fam)
m_fam_diff_1 <- lm(Index0_trans ~ T_trans + T_diff, data = d_fam)
anova(m_fam_diff_0, m_fam_diff_1)  # p = 0.216. Use m_fam_diff_1
summary(m_fam_diff_1)

m_fam_sd_0 <- lm(Index0_trans ~ T_trans * T_sd, data = d_fam)
m_fam_sd_1 <- lm(Index0_trans ~ T_trans + T_sd, data = d_fam)
anova(m_fam_sd_0, m_fam_sd_1)  # p = 0.170. Use m_fam_sd_1
summary(m_fam_sd_1)

m_fam_diff <- lm(T_diff ~ T, data = d_fam)
m_fam_sd <- lm(T_sd ~ T, data = d_fam)
m_all_diff <- lm(T_diff ~ T, data = d_all)
m_all_sd <- lm(T_sd ~ T, data = d_all)
summary(m_fam_diff)
summary(m_fam_sd)
summary(m_all_diff)
summary(m_all_sd)

p1 <- ggplot(d_fam, aes(T, T_diff)) +
  geom_point(color = "blue", alpha = 0.7) +
  geom_smooth(method = lm, color = "black", se = F) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black"),
        plot.title = element_text(hjust = 0.5)) +
  ggtitle("Families") +
  xlab("MAT") + ylab("Mean annual range")
p2 <- ggplot(d_fam, aes(T, T_sd)) +
  geom_point(color = "blue", alpha = 0.7) +
  geom_smooth(method = lm, color = "black", se = F) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black"),
        plot.title = element_text(hjust = 0.5)) +
  ggtitle("Families") +
  xlab("MAT") + ylab("Standard deviation")
p3 <- ggplot(d_all, aes(T, T_diff)) +
  geom_point(color = "blue", alpha = 0.08) +
  geom_smooth(method = lm, color = "black", se = F) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black"),
        plot.title = element_text(hjust = 0.5)) +
  ggtitle("All Doculects") +
  xlab("MAT") + ylab("Mean annual range")
p4 <- ggplot(d_all, aes(T, T_sd)) +
  geom_point(color = "blue", alpha = 0.08) +
  geom_smooth(method = lm, color = "black", se = F) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black"),
        plot.title = element_text(hjust = 0.5)) +
  ggtitle("All Doculects") +
  xlab("MAT") + ylab("Standard deviation")
(p1 + p2) / (p3 + p4)
# Then, save as range.pdf (6 * 6 inches) (for SI)


# Plot correlations by language family (for SI)
# =============================================

top_num <- 25
fam_count <- d_all %>% group_by(Family) %>% summarise(Count = n()) %>% arrange(desc(Count))
top_families <- fam_count$Family[1:top_num]

full_family_names <- c(
  "NC"  = "Niger-Congo",
  "An"  = "Austronesian",
  "ST"  = "Sino-Tibetan",
  "TNG" = "Trans-New Guinea",
  "AA"  = "Afro-Asiatic",
  "IE"  = "Indo-European",
  "AuA" = "Austro-Asiatic",
  "PN"  = "Pama-Nyungan",
  "TK"  = "Tai-Kadai",
  "Tor" = "Torricelli",
  "Man" = "Mande",
  "CSu" = "Central Sudanic",
  "Alt" = "Altaic",
  "ESu" = "Eastern Sudanic",
  "OM"  = "Oto-Manguean",
  "May" = "Mayan",
  "UA"  = "Uto-Aztecan",
  "Dra" = "Dravidian",
  "GWB" = "Greater West Bomberai",
  "Sep" = "Sepik",
  "Dog" = "Dogon",
  "Arw" = "Arawakan",
  "Que" = "Quechuan",
  "NDa" = "Nakh-Daghestanian",
  "Ura" = "Uralic")

temperature_results <- character(top_num)
word_length_results <- character(top_num)
labels <- character(top_num)
names(labels) <- top_families
for (i in 1:top_num) {
  family_i <- top_families[i]
  filtered <- filter(d_all, Family == family_i)
  model <- lm(Index0_trans ~ T_trans, data = filtered)
  s <- summary(model)
  temperature_results[i] <- paste(full_family_names[family_i], nrow(filtered),
                                  s$coefficients[2], s$r.squared, s$coefficients[8])
  model <- lm(Index0_trans ~ WL, data = filtered)
  s <- summary(model)
  word_length_results[i] <- paste(full_family_names[family_i], nrow(filtered),
                                  s$coefficients[2], s$r.squared, s$coefficients[8])
  labels[i] <- paste(full_family_names[family_i], ": ", nrow(filtered), sep = "")
}
# family name, number of doculects, estimate slope, r^2, p value
print(temperature_results)
print(word_length_results)

ggplot(data = filter(d_all, Family %in% top_families), aes(T_trans, Index0_trans)) +
  geom_point(na.rm = T, color = "blue", alpha = 0.1) +
  geom_smooth(method = lm, color = "black", se = F, linewidth = 0.5) +
  facet_wrap( ~ Family, labeller = labeller(Family = labels)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black")) +
  xlab("MAT (transformed)") + ylab("MSI (transformed)")
# Then, save as correlation_by_family.pdf (8 * 8 inches)

ggplot(data = filter(d_all, Family %in% top_families), aes(WL, Index0_trans)) +
  geom_point(na.rm = T, color = "blue", alpha = 0.1) +
  geom_smooth(method = lm, color = "black", se = F, linewidth = 0.5) +
  facet_wrap( ~ Family, labeller = labeller(Family = labels)) +
  theme(panel.grid.major = element_blank(), panel.grid.minor = element_blank(),
        axis.text.x = element_text(color = "black"),
        axis.text.y = element_text(color = "black")) +
  xlab("Mean word length") + ylab("MSI (transformed)")
# Then, save as word_length_by_family.pdf (8 * 8 inches)
