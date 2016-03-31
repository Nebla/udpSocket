plotratio <- function(data, nvar = 50, power1 = 0.7, power2 = 2.5, 
	plotflag = T)  
{
#       Variables:
#               data    --      The data being used.
#               nvar    --      The number of aggregation levels.
#               power1,power2-- Cut-offs for points to be used in estimating
#                               beta.
#	Calls functions Speng and Speng.av which themselves call Cpeng.o and
#	Cpeng_av.o.  Written by Vadim Teverovsky.
	
        cat("\n")
# n is the length of the data vector
#Compute the MEDIAN Variance of Residuals
        n <- length(data)
        med <- Speng(data, nvar)
# The increment to be used in plotting and estimating the slope.  Depends on 
# the number of levels, and the minimum number of points needed at each
# level.
        increment <- (log10(n/3))/nvar
# lv and lm are going to be the y and x values respectively of the points
# in the  plot.
        lr <- log10(med)
        lm <- rep(0, nvar)
# power1 and power2 determine whether the points will be included in the 
# estimate of beta.
        for(i in 1:nvar)
                lm[i] <- log10(3 * floor(10^(i * increment)))
        lmadj <- lm[(lm >= power1) & (lm <= power2)]
        lradj <- lr[(lm >= power1) & (lm <= power2)]
        lmadjc <- lm[(lm < power1) | (lm > power2)]
        lradjc <- lr[(lm < power1) | (lm > power2)]

#Compute the AVERAGE Variance of Residuals
        ave <- Speng.av(data, nvar)
        lv <- log10(ave)
        lv <- lr - lv
        lvadj <- lv[(lm >= power1) & (lm <= power2)]
        lvadjc <- lv[(lm < power1) | (lm > power2)]
# The line is fitted to the appropriate points.
        fit <- lsfit(lmadj, lvadj - lv[1])$coef
        if(plotflag == T) {
                plot(c(0, lm), c(0, lv - lv[1]), xlab = 
                        "log(aggregation level)", type = "n", cex = 1.3)
                points(lmadj, lvadj - lv[1], pch = 16, mkh = 0.08)
                points(lmadjc, lvadjc - lv[1], pch = 3, mkh = 0.06)
                abline(fit)
        }
# estimate of alpha returned.
	
        return(2/(fit[2] + 1))
}
plotratio.reg <- 
function(data, nvar = 50, power1 = 0.7, power2 = 2.5, plotflag = T)
{
#       Variables:
#               data    --      The data being used.
#               nvar    --      The number of aggregation levels.
#               power1,power2-- Cut-offs for points to be used in estimating
#                               beta.
        cat("\n")
# n is the length of the data vector, variances is the vector of length nvar+1
# which is the output of Speng1.  It is the vector of variances at the 
# different levels of aggregation.
        n <- length(data)
        med <- Speng(data, nvar)
# The increment to be used in plotting and estimating the slope.  Depends on 
# the number of levels, and the minimum number of points needed at each
# level.
        increment <- (log10(n/3))/nvar
# lv and lm are going to be the y and x values respectively of the points
# in the  plot.
        lr <- log10(med)
        lm <- rep(0, nvar)
# power1 and power2 determine whether the points will be included in the 
# estimate of beta.
        for(i in 1:nvar)
                lm[i] <- log10(3 * floor(10^(i * increment)))
        lmadj <- lm[(lm >= power1) & (lm <= power2)]
        lradj <- lr[(lm >= power1) & (lm <= power2)]
        lmadjc <- lm[(lm < power1) | (lm > power2)]
        lradjc <- lr[(lm < power1) | (lm > power2)]
        ave <- Speng.av(data, nvar)
        lv <- log10(ave)
        lv <- lr - lv
        lvadj <- lv[(lm >= power1) & (lm <= power2)]
        lvadjc <- lv[(lm < power1) | (lm > power2)]
# The line is fitted to the appropriate points.  Here is the one difference 
# from plotratio!!!!   
        fit <- ltsreg(lmadj, lvadj - lv[1])$coefficients
        if(plotflag == T) {
                plot(c(0, lm), c(0, lv - lv[1]), xlab = 
                        "log(aggregation level)", type = "n", cex = 1.3)
                points(lmadj, lvadj - lv[1], pch = 16, mkh = 0.08)
                points(lmadjc, lvadjc - lv[1], pch = 3, mkh = 0.06)
                abline(0, 0, lty = 2)
                abline(fit)
        }
        return(2/(fit[2] + 1))
}
	
	
	
	Speng <- function(data, nvar)
{
        n <- length(data)
        if(!is.loaded("Cpeng"))
                dyn.load("Cpeng.so")
        minpts <- 1
        .C("Cpeng",
                data = as.double(data),
                n = as.integer(n),
                nvar = as.integer(nvar),
                minpts = as.integer(minpts),
                v = double(length = nvar + 1))$v[2:(nvar + 1)]
}



Speng.av <- function(data, nvar)
{
        n <- length(data)
        if(!is.loaded("Cpeng_av"))
                dyn.load("Cpeng_av.so")
        minpts <- 1
        .C("Cpeng_av",
                data = as.double(data),
                n = as.integer(n),
                nvar = as.integer(nvar),
                minpts = as.integer(minpts),
                v = double(length = nvar + 1))$v[2:(nvar + 1)]
}
	
