
library(readxl)
setwd("D:/study/last one/HW5")
#load data from xlsx, and set the first row as column names
data <- read_xlsx("HW5_PCA.xlsx", col_names = TRUE)
summary(data)

table(is.na(data))
data$judge <- as.factor(data$judge)
data$wine <- as.factor(data$wine)
data$rep <- as.factor(data$rep)
str(data)

da.f <- data
da.f$judge <- as.numeric(da.f$judge)
da.f$wine <- as.numeric(da.f$wine)
da.f$rep <- as.numeric(da.f$rep)
str(da.f)
head(da.f)
table(is.na(da.f))

#######################
##PCA ON NON-AVERAGED DATA
###PCA on non-averaged data set using correlation matrix
library(SensoMineR)
out <- panellipse.session(as.data.frame(da.f), col.p = 2, col.j = 1, col.s = 3,
                          firstvar = 4, alpha = 0.05, coord = c(1,2),
                          scale.unit = TRUE, nbsimul = 500, nbchoix = NULL,
                          level.search.desc = 0.2, centerbypanelist = TRUE,
                          scalebypanelist = FALSE, name.panelist = FALSE,
                          variability.variable = FALSE, cex = 1, color = NULL,
                          graph.type = c("ggplot"))
plot(out)