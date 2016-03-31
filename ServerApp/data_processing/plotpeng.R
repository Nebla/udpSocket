#Written by Vadim Teverovsky



plotpeng_function(data, nvar = 50, power1 = 0.7, power2 = 2.5, slopes = 1,
plotflag = T, aggreg = 1) 
{
#       This is a function which gives a plot of the variance of residuals
#	for various 
#       aggregation levels.  It calls the function Speng.S, which, in
#       turn, calls Cpeng.c.  The estimate of the slope, beta, gives
#       an estimate for the parameter, H, via :  H = beta/2.  This version
#	uses the median over the blocks to estimate the variance of
#	residuals. This is more robust when non-stationarities are present,
#	and produces d+1/alpha when infinite variance series are used.
#
#       Variables:
#               data    --      The data being used.
#               nvar    --      The number of aggregation levels.
#               power1,power2-- Cut-offs for points to be used in estimating
#                               beta.
#               slopes  --      Flag.  If 1, draw the estimated line whose 
#                               slope is beta.
#               plotflag  --    Flag.  If T, plot is produced.  VT 12/28/94
#		aggreg	--	Option to aggregate the series BEFORE using
#				the method.  Aggregation brings series
#				closer to "canonical" l.-r. dep.
        cat("\n")

# n is the length of the data vector, variances is the vector of length nvar+1
# which is the output of Speng.  It is the vector of variances at the 
# different levels of aggregation.

        n1 <- length(data)
        if(aggreg != 1) {
                n <- floor(n1/aggreg)
                data1 <- rep(0, n)
                for(i in 1:n)
                        data1[i] <- 1/aggreg * sum(data[(aggreg * (i - 1) + 1):(
                                aggreg * i)])
        }
        else {
                n <- n1
                data1 <- data
        }
        variances <- Speng(data1, nvar)

# The increment to be used in plotting and estimating the slope.  Depends on 
# the number of levels, and the minimum number of points needed at each level.

        increment <- (log10(n/3))/nvar

# lv and lm are going to be the y and x values respectively of the points
# in the plot.

        lv <- log10(variances)
        lm <- rep(0, nvar)

# power1 and power2 determine whether the points will be included in the 
# estimate of beta.

        for(i in 1:nvar)
                lm[i] <- log10(floor(10^((i) * increment)))

#Above line changed 2/28/95, to make the plotting consistent with calculations.

        lmadj <- lm[(lm >= power1) & (lm <= power2)]
        lvadj <- lv[(lm >= power1) & (lm <= power2)]
        lmadjc <- lm[(lm < power1) | (lm > power2)]
        lvadjc <- lv[(lm < power1) | (lm > power2)]

# The line is fitted to the appropriate points.

        return(lvadj, lmadj)
        fit <- lsfit(lmadj, lvadj)
        intercept <- fit$coef[1]
        beta <- fit$coef[2]     

# The plot is done here if plotflag == T.

        if(plotflag == T) {
                plot(c(0, lm), c(0, lv), xlab = "log10(m)", ylab = 
                        "log10(variances(residuals))", type = "n")
                points(lmadj, lvadj, pch = 16, mkh = 0.06)
                points(lmadjc, lvadjc, pch = 3, mkh = 0.06)
                if(slopes == 1)
                        lines(lmadj, intercept + (beta) * lmadj)
        }

#Output

        cat(" H = ", beta/2, "\n\n")
        result <- beta/2
        names(result) <- NULL
        return(result)
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



plotpeng.av_
function(data, nvar = 50, power1 = 0.7, power2 = 2.5, slopes = 1, plotflag = T)
{
#       This is a function which gives a plot of the variances for various
#       aggregation levels.  It calls the function Speng.S, which, in
#       turn, calls Cpeng.c.  The estimate of the slope, beta, gives
#       an estimate for the parameter, H, via :  H = beta/2.  The
#	difference from the function above is that instead of using the
#	median over the blocks to estimate the variance of residuals, the
#	average is used.  This results in non-robustness when
#	non-stationarities are included.  When the data series have
#	infinite variance, this estimator estimates d+1/2, and not d+
#	1/alpha as does the median version. 
#
#       Variables:
#               data    --      The data being used.
#               nvar    --      The number of aggregation levels.
#               power1,power2-- Cut-offs for points to be used in estimating
#                               beta.
#               slopes  --      Flag.  If 1, draw the estimated line whose 
#                               slope is beta.
#               plotflag  --    Flag.  If T, plot is produced.  VT 12/28/94
# n is the length of the data vector, variances is the vector of length nvar+1
# which is the output of Speng.  It is the vector of variances at the 
# different levels of aggregation.

        n <- length(data)
        variances <- Speng.av(data, nvar)

# The increment to be used in plotting and estimating the slope.  Depends on 
# the number of levels, and the minimum number of points needed at each level.

        increment <- (log10(n/3))/nvar

# lv and lm are going to be the y and x values respectively of the points
# in the  plot.

        lv <- log10(variances)
        lm <- rep(0, nvar)

# power1 and power2 determine whether the points will be included in the 
# estimate of beta.

        for(i in 1:nvar)
                lm[i] <- log10(floor(10^((i) * increment))) + log10(3)

#Above line changed 2/28/95, to make the plotting consistent with calculations.

        lmadj <- lm[(lm >= power1) & (lm <= power2)]
        lvadj <- lv[(lm >= power1) & (lm <= power2)]
        lmadjc <- lm[(lm < power1) | (lm > power2)]
        lvadjc <- lv[(lm < power1) | (lm > power2)]

# The line is fitted to the appropriate points.

        fit <- lsfit(lmadj, lvadj)
        intercept <- fit$coef[1]
        beta <- fit$coef[2]     

# The plot is done here if plotflag == T.

        if(plotflag == T) {
                plot(c(0, lm), c(0, lv), xlab = "log10(m)", ylab = 
                        "log10(variances(residuals))", type = "n")
                points(lmadj, lvadj, pch = 16, mkh = 0.06)
                points(lmadjc, lvadjc, pch = 3, mkh = 0.06)
                if(slopes == 1)
                        lines(lmadj, intercept + (beta) * lmadj)
        }
#Output
        cat(" H = ", beta/2, "\n\n")
        result <- beta/2
        names(result) <- NULL
        return(result)
}

Speng.av_
function(data, nvar)
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

