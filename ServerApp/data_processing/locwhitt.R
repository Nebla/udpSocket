# Code taken from Murad S. Taqqu's web site.  Adapted to R by
# Richard G. Clegg (richard@richardclegg.org) 2005.

#These are the functions performing the local Whittle algorithm.
#	rfunc	--	Function which is minimized in the local Whittle
#			estimator. 
#	locwhitt  --	Basic local whittle.  Finds periodogram (uses
#			function   per  ), then minimizes rfunc.
#	locwhitt.cont -- Continuous version of local Whittle.  Calculates
#			local Whittle with various values of m, and returns
#			a vector of results. 


rfunc <- function(h, len, im, peri)
#	h	-- Starting H value for minimization.
#	len	-- Length of time series.
#	im	-- Use only len/im frequencies.
#	peri	-- Periodogram of data.
{
#        cat ("Getting im ",im, "len ",len,"\n");
        m <- len %/% im
        peri <- peri[2:(m + 1)]
        z <- c(1:m)
        freq <- (2 * pi)/len * z
        result <- log(sum(freq^(2 * h - 1) * peri)) - (2 * h)/m * sum(log(freq))
                 #       cat("H = ", h, "R = ", result, "\n")
        drop(result)
}


locwhitt <- function(data, h = 0.5, im = 2, output=T)
#	data	--	Time series.
#	h	-- Starting H value for minimization.
#	im	-- Use only N/im frequencies where N is length of series.

{
        peri <- per(data)
        len <- length(data)
#        return(nlminb(start = h, obj = rfunc, len = len, im = im, peri = peri)$
#               parameters)
#        cat ("Passing im ",im, "len ",len,"\n")
        z<-optim(par=h, fn= rfunc, len=len, im= im, peri=peri,method="BFGS")
        if (output == T) {
            cat ("H = ",z$par,"\n")
        }
        return (z$par)
}

locwhitt.cont <- function(data, h = 0.5, i = 20, minm = 50)
#	data	--	Time series.
#	h	-- Starting H value for minimization.
#	i	-- Number of different m's to use.
#	minm	-- Minimum number of frequencies to use in estimation.

{
        peri <- per(data)
        len <- length(data)
        len1 <- len/minm
        cat("len = ", len, "len1 = ", len1, "\n")
        hvec <- rep(0, i)
        if(i > len1)
                i <- len1
        for(j in 1:i) {
                im <- as.integer(len1/i * j)
#                hvec[j] <- nlminb(start = h, obj = rfunc, len = len, im = im, 
#                        peri = peri)$parameters
                 hvec[j] <- optim(par = h, fn = rfunc, len = len, im = im, 
                       peri = peri,method="BFGS")$par
                cat("im = ", im, "\n\n")
        }
        return(hvec)
}


#Function to compute periodogram.

per <- function(z)
{
        n <- length(z)
        (Mod(fft(z))^2/(2 * pi * n))[1:(n %/% 2 + 1)]
}
