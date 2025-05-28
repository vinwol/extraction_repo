library(tabulizer)
library(tibble)
library(readr)
library(survival)
library(ggplot2)
library(dplyr)
library(ipdrecon)

source('ipd_guyot.R')
source('ipd_rogula.R')
source('util_ipd.R')
source('util_point_translation.R')
source('util_validation.R')

# Input files need to run this R script:
#
# 1) Example publication:
# https://www.thelancet.com/journals/lanonc/article/PIIS1470-2045(17)30517-X/fulltext
# file: weller_paper.pdf
#
# 2) Extraction of individual patient data from figure 2b of the Weller et al publication, 
# intention-to-treat population, OS of control arm.
# file: weller_figure_2b_control_temozolomide.csv.

path <- 'weller_paper.pdf'

# Extraction of table 1: baseline characteristics.
# The coordinates of the columns and area is retrieved by using tabulizer::locate_areas(path, pages = 6).
# As an example how to do this see this tutorial: https://rpubs.com/behzod/tabulizer
out <- tabulizer::extract_tables(path, 
                                 pages = 6, 
                                 guess = FALSE,
                                 columns = list(c(121.5, 218, # left, right coordinates of column.
                                                  273.4, 320.5, 
                                                  389.1, 440.9, 
                                                  501.7,  552.9)),
                                 # top, left, bottom and right coordinates.
                                 area = list(c(405.3033, 
                                               119.1051, 
                                               749.7125, 
                                               558.2295)))
table_1 <- tibble::as_tibble(out[[1]])[,2:8]
# Adjust further manually by using Excel or with additional formatting in R.
# The following is omitted:
# Time from diagnosis to randomisation (months)
# Previous radiotherapy dose (Gy)
# Previous temozolomide dose (mg/m2)
# The final result should be a tibble in long format.

# Extraction of table 2 (first part): adverse events.
# The coordinates of the columns and area is retrieved by using tabulizer::locate_areas(path, pages = 10).
# As an example how to do this see this tutorial: https://rpubs.com/behzod/tabulizer
out <- tabulizer::extract_tables(path, 
                                 pages = 10, 
                                 guess = FALSE,
                                 columns = list(c(121.8906,220.5364,
                                                  259.0891,302.1759,
                                                  349.7982,388.3495,
                                                  432.5702,469.9877,
                                                  510.8068,552.7598)),
                                 # top, left, bottom and right pixel coordinates.
                                 area = list(c(264.7043,123.0254,746.5941,556.1614)))
table_2_part_1 <- tibble::as_tibble(out[[1]])[,2:10]

# Extraction of table 2 (second part): adverse events.
# The coordinates of the columns and area is retrieved by using tabulizer::locate_areas(path, pages = 11).
# As an example how to do this see this tutorial: https://rpubs.com/behzod/tabulizer
out <- tabulizer::extract_tables(path, 
                                 pages = 11, 
                                 guess = FALSE,
                                 columns = list(c(39.32082,133.56520,
                                                  181.8227,219.2934,
                                                  269.8206,308.4266,
                                                  353.2787,391.8849,
                                                  430.4911,465.6908)),
                                 area = list(c(144.72095,37.61652,343.42840,473.63914)))
table_2_part_2 <- tibble::as_tibble(out[[1]])[,2:10]
# Adjust further manually by using Excel or with additional formatting in R the 
# two parts of the adverse event table.
# The final result should be a tibble in long format.

# Guyot et al algorithm:
# Extraction of individual patient data from figure 2b of Weller et al publication, 
# intention-to-treat population, OS of control arm.
# The digitization is done using WebPlotDigitizer: https://automeris.io/WebPlotDigitizer/
# which results in the file weller_figure_2b_control_temozolomide.csv.
# We are using here the R package ipdrecon: https://github.com/vinwol/ipdrecon
# which is a wrapper around the algorithm by Guyot et al and Rogula et al.
data <- readr::read_csv('./files/weller_figure_2b_control_temozolomide.csv', col_names=FALSE)
surv_time <- dplyr::pull(data,1)
surv_prob <- dplyr::pull(data,2) 
trisk <- seq(from=0, to=42, by=6)
nrisk <- c(371,345,261,159,72,32,12,7)
tot_events <- NA
lower <- ipdrecon::get_lower_indices(surv_time, trisk) 
upper <- ipdrecon::get_upper_indices(surv_time, trisk) 
res <- ipdrecon::get_ipd_guyot(surv_time,
                               surv_prob,
                               trisk,
                               nrisk,
                               lower,
                               upper,
                               tot_events)
ipd <- res[[1]]
fit <- ggsurvfit::survfit2(survival::Surv(time, event) ~ 1, data = ipd)
ggsurvfit::ggsurvfit(fit, color = 'blue') +
    ggplot2::labs(x = "Time (Months)", y = "Overall Survival Probability") +
    ggplot2::scale_x_continuous(limits = c(0, 48),
                                breaks = seq(0, 48, by = 6),
                                expand = c(0.02, 0)) +
    ggplot2::scale_y_continuous(limits = c(0, 1),
                                breaks = seq(0, 1, by = 0.1),
                                expand = c(0.02, 0)) +
    ggsurvfit::add_risktable() 

# Rogula et al algorithm (no explicit censoring here):
# Extraction of individual patient data from figure 2b of Weller et al publication, 
# intention-to-treat population, OS of control arm.
# The digitization is done using WebPlotDigitizer: https://automeris.io/WebPlotDigitizer/
# which results in the file weller_figure_2b_control_temozolomide.csv.
# We are using here the R package ipdrecon: https://github.com/vinwol/ipdrecon
# which is a wrapper around the algorithm by Guyot et al and Rogula et al.
data <- readr::read_csv('./files/weller_figure_2b_control_temozolomide.csv', col_names=FALSE)
surv_time <- dplyr::pull(data,1)
surv_prob <- dplyr::pull(data,2) 
n <- 137
cen_t <- NA
ipd <- get_ipd_rogula(n, surv_time, surv_prob, cen_t)
fit <- ggsurvfit::survfit2(survival::Surv(time, event) ~ 1, data = ipd)
ggsurvfit::ggsurvfit(fit, color = 'blue') +
    ggplot2::labs(x = "Time (Months)", y = "Overall Survival Probability") +
    ggplot2::scale_x_continuous(limits = c(0, 48),
                                breaks = seq(0, 48, by = 6),
                                expand = c(0.02, 0)) +
    ggplot2::scale_y_continuous(limits = c(0, 1),
                                breaks = seq(0, 1, by = 0.1),
                                expand = c(0.02, 0)) +
    ggsurvfit::add_risktable() 