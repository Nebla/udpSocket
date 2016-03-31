source("calcHurst.R")

args <- commandArgs(trailingOnly = TRUE)
#print(args[2])
calcHurst(file=args[2], terse=F)

