# plotvar. R adapted to R by Richard G. Clegg (richard@richardclegg.org) 2005
#Written by Bob Sherman, modified by Walter Willinger, 
# Vadim Teverovsky.  

plotvar<-function(data, nvar = 50, minnpts = 5, power1 = 0.7, power2 = 2.5, 
			slopes = 1, difference = 0, plotflag = T, output=T)
{
#	This is a function which gives a plot of the variances for various
#	aggregation levels.  It calls the function Svariances.S, which, in
#	turn, calls Cvariances.c.  The estimate of the slope, beta, gives
#	an estimate for the parameter, H, via :  H = (beta+2)/2.
#	Variables:
#		data	--	The data being used.
#		nvar	-- 	The number of aggregation levels.
#		minnpts	--	The minimum number of points to be used to
#				estimate the variance at any aggregation level
#		power1,power2-- Cut-offs for points to be used in estimating
#				beta.
#		slopes  --	Flag.  If 1, draw the estimated line whose 
#				slope is beta.
#		difference --   If non-stationarity is suspected, differencing 
#				can be performed by setting to != 0.  Flag.
#		plotflag  --	Flag.  If T, plot is performed.  12/27/94

#	cat("\n")	

# n is the length of the data vector, variances is the vector of length nvar+1
# which is the output of Svariances.  It is the vector of variances at the 
# different levels of aggregation.
 
	n <- length(data)
	variances <- Svariances(data, nvar, minnpts)	

# The increment to be used in plotting and estimating the slope.  Depends on 
# the number of levels, and the minimum number of points needed at each level.

	increment <- (log10(n/minnpts))/nvar	

# May be a problem with non-stationarity
	if (difference != 0)
          {
	    cat("May be problem with non-stationarity.")
	    cat("  Taking differences of variances.", fill = T)
		variances <-  - diff(variances)	

# lv and lm are going to be the y and x values respectively of the points in
# the plot.

	    lv <- log10(variances)
	    lm <- rep(0, nvar)	

# power1 and power2 determine whether the points will be included in the 
# estimate of beta.
 
	    for (i in 1:nvar)
              lm[i] <- log10(floor(10^((i - 1) * increment)))

# Above line changed 2/28/95, to make the plotting consistent with
# calculations.

	    lmadj <- lm[(lm >= power1) & (lm <= power2)]
	    lvadj <- lv[(lm >= power1) & (lm <= power2)]
	    lmadjc <- lm[(lm < power1) | (lm > power2)]
	    lvadjc <- lv[(lm < power1) | (lm > power2)]

	    fit <- lsfit(lmadj, lvadj)
	    intercept <- fit$coef[1]
	    beta <- fit$coef[2]
	    cat("Beta = ", beta, fill = T)
	    cat("H = ", (beta + 2)/2, fill = T)	

# Plotflag added 12/27/94
  
	    if (plotflag == T)
              {
	        plot(c(0, lm), c(0, lv), xlab = "log10(m)", ylab = 
		     "log10(variances)", type = "n")
		points(lmadj, lvadj, pch = 16, mkh = 0.06)
		points(lmadjc, lvadjc, pch = 3, mkh = 0.06)

		if (slopes == 1)
		  lines(lmadj, intercept + (beta) * lmadj)
	      }

# Returning results 12/27/94.

	     result <- (beta + 2)/2
	     names(result) <- NULL
	     return(result)

	  }
	else
          {
 
# lv and lm are going to be the y and x values respectively of the points in
# the plot.

            lv <- log10(variances)
	    lm <- rep(0, nvar + 1)	

# power1 and power2 determine whether the points will be included in the 
# estimate of beta.

	    for (i in 1:nvar + 1)
	      lm[i] <- log10(floor(10^((i - 1) * increment)))

# Above line changed 2/28/95, to make the plotting consistent with
# calculations.
#cat ("power1= ", power1, " power2= ",power2, "\n")
	    lmadj <- lm[(lm >= power1) & (lm <= power2)]
	    lvadj <- lv[(lm >= power1) & (lm <= power2)]
	    lmadjc <- lm[(lm < power1) | (lm > power2)]
	    lvadjc <- lv[(lm < power1) | (lm > power2)]	

# The line is fitted to the appropriate points.
            if (output == T) {
                cat ("Fitting\n")
                cat(lmadj,"\n")
                cat (lvadj,"\n")
            }
	    fit <- lsfit(lmadj, lvadj)
	    intercept <- fit$coef[1]
	    beta <- fit$coef[2]	# The plot is done here.

# Changed the normalization from dividing by lv[1] to subtracting it.(Logs!)
# 5/23/1994.  Plotflag added 12/27/94

            if (plotflag == T)
              {
	        plot(c(0, lm), c(0, lv - lv[1]), xlab = "log10(m)", 
		     ylab = "log10(variances)", type = "n")
		points(lmadj, lvadj - lv[1], pch = 16, mkh = 0.06)
		points(lmadjc, lvadjc - lv[1], pch = 3, mkh = 0.06)
#		abline(0, -1, lty = 2)	

		if (slopes == 1)
                  {
		    lines(lmadj, intercept - lv[1] + (beta) * lmadj)	
		  }
	      }

# Returning results 12/27/94.
        if (output == T) {
            cat(" beta = ", beta, "\n\n")
	       cat("H= ", (beta + 2)/2, "\n\n")
	    }
	    result <- (beta + 2)/2
	    names(result) <- NULL
	    return(result)
	}
}

Svariances<-function(data, nvar, minpts)
{
	n <- length(data)
	if(!is.loaded("Cvariances"))
		dyn.load("Cvariances.so")
	.C("Cvariances",
		data = as.double(data),
		n = n,
		nvar = as.integer(nvar),
		minpts = as.integer(minpts),
		v = double(nvar + 1))$v
}

plotvar2<-function(data, nvar = 50, minnpts = 5, power1 = 0.7, power2 = 2.5, slopes = 1, 
        difference = 0, plotflag = T)
{

#       This is a function which gives a plot of the variances for various
#       aggregation levels.  It calls the function Svariances.S, which, in
#       turn, calls Cvariances.c.  Instead of estimating a straight line
#	with lsfit, as does plotvar, this function attempts to compensate for
#	possible non-stationarities by fitting a curve of the form C<-1 + C<-2
#	m^(2H-2) to the variance vector.  Similar to differenced variance
#	method, but less precise than the original variance method, due to
#	fitting 3 parameters (C<-1,C<-2,H) instead of one.
#
#       Variables:
#               data    --      The data being used.
#               nvar    --      The number of aggregation levels.
#               minnpts --      The minimum number of points to be used to
#                               estimate the variance at any aggregation level
#               power1,power2-- Cut-offs for points to be used in estimating
#                               beta.
#               slopes  --      Flag.  If 1, draw the estimated line whose 
#                               slope is beta.
#               difference --   If non-stationarity is suspected, differencing 
#                               can be performed by setting to != 0.  Flag.
#               plotflag  --    Flag.  If T, plot is performed.  12/27/94

        cat("\n")

# n is the length of the data vector, variances is the vector of length nvar+1
# which is the output of Svariances.  It is the vector of variances at the 
# different levels of aggregation.

        n <- length(data)
        variances <- Svariances(data, nvar, minnpts)

# The increment to be used in plotting and estimating the slope.  Depends on 
# the number of levels, and the minimum number of points needed at each level.

        increment <- (log10(n/minnpts))/nvar

# lv and lm are going to be the y and x values respectively of the points in
# the plot.

        lv <- log10(variances)
        lm <- rep(0, nvar + 1)

# power1 and power2 determine whether the points will be included in the 
# estimate of beta.

        for (i in 1:(nvar + 1))
          lm[i] <- log10(floor(10^((i - 1) * increment)))

# Above line changed 2/28/95, to make the plotting consistent with
# calculations.

        lmadj <- lm[(lm >= power1) & (lm <= power2)]
        lvadj <- lv[(lm >= power1) & (lm <= power2)]
        lmadjc <- lm[(lm < power1) | (lm > power2)]
        lvadjc <- lv[(lm < power1) | (lm > power2)]

### Different from plotvar here.

        cvector <- c(0, 1, -1)
#        fit <- nlminb(start = cvector, obj = minvar, variances = lvadj - lv[1],                     
# m = 10^lmadj)$parameters
        fit <-optim(par= cvector, fn=minvar, variances=lvadj - lv[1],
           method="L-BFGS-B", m = 10^lmadj)$par
        beta <- fit[3]
        cat("fit =", fit, "Beta = ", beta, fill = T)
        cat("H = ", (beta + 2)/2, fill = T)     # Plotflag added 12/27/94

        if (plotflag == T)
          {
            plot(c(0, lm), c(0, lv - lv[1]), xlab = "log10(m)", ylab = 
                 "log10(variances)", type = "n")
            points(lmadj, lvadj - lv[1], pch = 16, mkh = 0.06)
            points(lmadjc, lvadjc - lv[1], pch = 3, mkh = 0.06)
            lines(lm, log10(fit[1] + fit[2] * 10^(fit[3] * lm)), type = "l")
          }

# Returning results 12/27/94.

        result <- (beta + 2)/2
        names(result) <- NULL
        return(result)
}

minvar<- function(cvector, variances, m)

#Function used by plotvar2 to minimize.

{
        c1 <- cvector[1]
        c2 <- cvector[2]
        c3 <- cvector[3]        
        result <- sum((10^variances - (c1 + c2 * m^(c3)))^2)
        drop(result)
}

# eof plotvar.S
