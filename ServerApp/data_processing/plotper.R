# Adapted to R by Richard G. Clegg richard@richardclegg.org (2005)

#plotper Written by Bob Sherman, modified by Walter Willinger, 
# Vadim Teverovsky.  Other functions by Vadim Teverovsky.	

#Contains plotper which plots the periodogram and produces linear
#regression estimate of H, plotavper which plots the averaged periodogram
#and produces estimate of H from that, perbox, a modified version of the
#periodogram method (sometimes called smoothed periodogram). Also contains
# routine per, which calculates actual periodogram for all of the above.
#	per.cont -- Continuous version of periodogram.  Calculates
#			periodogram with various cut-off value, and returns
#			a vector of results. 
#	per.cont.theory  -- Takes as argument the theoretical spectral
#			density of a time series model instead of an actual
#			time series, and produces the same vector as in
#			per.cont.  Useful for predicting the BIAS of
#			this estimator for known time series models. 
#

	
plotper<-function(data, percent = 10, plotflag = T,output = T)
{
#Function to plot periodogram of data set, and calculate estimate for H.
#	Calls function   per  .
#Variables:
#	data 	--  Data set.
#	percent	--  Percent of frequencies to use in calculating H.
#	plotflag	--	To plot or not to plot?


	pgram <- per(data)
	n <- length(pgram)
	if(plotflag == T)
		plot(log10((pi/n) * c(2:n)), log10(pgram[2:n]), xlab = 
			"log10(frequency)", ylab = "log10(periodogram)", type
			 = "p", pch = ".")
	fit <- lsfit(log10((pi/n) * c(2:((n * percent)/100))), log10(pgram[2:((
		n * percent)/100)]))
	if(plotflag == T)
		lines(log10((pi/n) * c(2:n)), fit$coef[1] + fit$coef[2] * log10(
			(pi/n) * c(2:n)), type = "l", lty = 3)
	if (output == T) {
    	cat(" H = ", (1 - fit$coef[2])/2, "\n")
    }
	result <- (1 - fit$coef[2])/2
	names(result) <- NULL
	return(result)
}


plot.av.per<-function(data, percent = 10, plotflag = T)

{
#Function to plot averaged periodogram of data set, and 
# calculate estimate for H.
#	Calls function   per  .
#Variables:
#	data 	--  Data set.
#	percent	--  Percent of frequencies to use in calculating H.
#	plotflag	--	To plot or not to plot?


	pgram1 <- per(data)
	n <- length(pgram1)
	pgram<-cumsum(pgram1[2:n])
	fit <- lsfit(log10((pi/n) * c(1:(((n-1) * percent)/100))), 
		log10(pgram[1:(((n-1) * percent)/100)]))
	if(plotflag == T){
		ymax <- max(log10(pgram),fit$coef[1] + fit$coef[2]* 
			log10((pi/n) * c(1:(n-1))))
		ymin <- min(log10(pgram),fit$coef[1] + fit$coef[2]* 
			log10((pi/n) * c(1:(n-1))))
		plot(log10((pi/n) * c(1:(n-1))), log10(pgram), xlab = 
			"log10(frequency)", ylab = "log10(periodogram)", type
			 = "p", pch = ".",ylim=c(ymin,ymax))
		lines(log10((pi/n) * c(1:(n-1))), fit$coef[1] + fit$coef[2] 
			* log10((pi/n) * c(1:(n-1))), type = "l", lty = 3)
		title(main="Plot of the Averaged Periodogram")}
	cat(" H = ", (2 - fit$coef[2])/2, "\n")
	result <- (2 - fit$coef[2])/2
	names(result) <- NULL
	return(result)
}



perbox<-function(data, percent = 1, plotflag = T, nbox = 100, tempper = 1)
{

#This is a routine to calculate the boxed periodogram for a set of data, and
#give an estimate for H.
#
#It calls the function per, which actually calculates the periodogram.
#Variables:
#	data	--	data set.
#	percent	--	percent of frequencies at the beginning not to box.
#	plotfalg--	To plot or not.
#	nbox	--	Number of boxes.
#	tempper	--	Fraction of points to use in calculating the H.
#
#
#Calculate periodogram.
	pgram <- per(data)
	n <- length(pgram)

#Calculate fractions from percentage.

	per1 <- percent/100
	per2 <- 1 - per1

	m <- log10(per2 * n)/nbox

	padj <- rep(0, nbox)

#Initialize vectors to be used later.

	x <- rep(0, (floor(per1 * n) + nbox))
	y <- rep(0, (floor(per1 * n) + nbox))
	z <- rep(0, nbox)

#Do the boxes (except for beginning few points.

	for(i in 1:nbox) {
		m1 <- floor(10^(m * i - m) + per1 * n)
		m2 <- floor(10^(m * i) + per1 * n)
		padj[i] <- sum(pgram[m1:m2])/(m2 - m1 + 1)
		z[i] <- log10((pi * (m2 + m1))/(2 * n))
	}

#Do calculations for first few points.

	for(i in 2:floor(per1 * n)) {
		x[i] <- log10((pi/n) * (i))
		y[i] <- log10(pgram[i])
	}
#Put all into samwe vectors.

	for(i in (floor(per1 * n) + 1):(floor(per1 * n) + nbox)) {
		x[i] <- z[i - floor(per1 * n)]
		y[i] <- log10(padj[i - floor(per1 * n)])
	}

#Plot if flag = T.

	if(plotflag == T)
		plot(x, y, xlab = "log10(frequency)", ylab = 
			"log10(periodogram)", type = "p", pch = 16, mkh = 0.06)

#Calculate numbers for fitting a line to find H.

	n1 <- length(x)
	n2 <- floor(tempper * n1)


#	fit <- ltsreg(x[1:n2], y[1:n2])	

	fit <- lsfit(x[1:n2], y[1:n2])

#If plot=T, put in line of fit.

	if(plotflag == T) lines(x, fit$coefficients[1] + fit$coefficients[2] * 
			x, type = "l", lty = 3)	

#	lines(x, fit$coef[1] + fit$coef[2] * x, type = "l", lty = 3)	
#Output results

	cat(" H = ", (1 - fit$coefficients[2])/2, "\n")
	result <- (1 - fit$coefficients[2])/2	

#	cat(" H = ", (1 - fit$coef[2])/2, "\n")
#	result <- (1 - fit$coef[2])/2

	names(result) <- NULL
	return(result)
}


per.cont <- function(data, i = 10, mult = 5, plotflag = T)
#Continuous version of periodogram, does periodogram for several values of
#cut-offs and then shows results. 
#	data	--	time series
#	i	--	number of different estimates to make.
#	mult	--	Changes the spacing between the values of the cut-offs.
#	plotflag	--	To plot or not to plot.

{
        result <- NULL
        pgram <- per(data)
        n <- length(pgram)
        if(plotflag == T)
                plot(log10((pi/n) * c(1:(n - 1))), log10(pgram[2:n]), xlab = 
                        "log10(frequency)", ylab = "log10(periodogram)", type
                         = "p", pch = ".")
#Go through loop, once for each value of cut-offs.

        for(j in 1:i) {

#Determine what percent of frequencies to use.

                percent <- (2 * n)/(mult * j)

#	Do the fit

                fit <- lsfit(log10((pi/n) * c(1:percent)), log10(pgram[2:(
                        percent + 1)]))
                if(plotflag == T)
                        lines(log10((pi/n) * c(1:(n - 1))), fit$coef[1] + fit$
                                coef[2] * log10((pi/n) * c(1:(n - 1))), type = 
                                "l", lty = 3)

                cat(" H = ", (1 - fit$coef[2])/2, "\n")
                result <- c(result, (0.5 - fit$coef[2]/2))
        }
        names(result) <- NULL
        return(result)
}



####Same as previous, except that computes the theoretical estimates based
#on the spectral density instead of the periodogram.  specdens is the
#theoretical spectral density.  i, mult, plotflag are as in per.cont.

per.theory.cont <- function(specdens, i = 10, mult = 5, plotflag = F)
{
        result <- NULL
        pgram <- c(0, specdens)
        n <- length(pgram)
        if(plotflag == T)
                plot(log10((pi/n) * c(1:(n - 1))), log10(pgram[2:n]), xlab = 
                        "log10(frequency)", ylab = "log10(periodogram)", type
                         = "p", pch = ".")
        for(j in 1:i) {
                percent <- (2 * n)/(mult * j)
                fit <- lsfit(log10((pi/n) * c(1:percent)), log10(pgram[2:(
                        percent + 1)]))
                if(plotflag == T)
                        lines(log10((pi/n) * c(1:(n - 1))), fit$coef[1] + fit$
                                coef[2] * log10((pi/n) * c(1:(n - 1))), type = 
                                "l", lty = 3)
                cat(" H = ", (1 - fit$coef[2])/2, "\n")
                result <- c(result, (0.5 - fit$coef[2]/2))
        }
        names(result) <- NULL
        return(result)
}




#Function to determine the periodogram of a set of data.


 per <- function (z)
          {n<-length(z)
          (Mod(fft(z))^2/(2*pi*n)) [1:(n %/% 2 + 1)]}
