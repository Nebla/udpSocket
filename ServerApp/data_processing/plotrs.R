# Converted to R by Richard G. Clegg (richard@richardclegg.org) 2005
#Written by Bob Sherman, modified by Walter Willinger, Vadim Teverovsky.
	
plotrs<-function(data, nblk = 5, nlag = 50, power1 = 0.7, power2 = 2.5,
  shuffle = 0, overlap = 1, ndiff = 0, lag = 0, rflag = 1, slopes = 1,
  connect = 0, fitls = 1, plotflag = T, output = T)
{
#       This is the higher level function which produces a plot of the R/S 
#       statistic, and gives an estimate for H, the index of similarity.
#       This calls the routines Srs and plotit and plotitrs, also included 
#       in this package.  Srs calls the C routine Crs.  
#       The variables used are as follows:
#       
#               data    --      The sample data values.  
#               slopes  --      A flag.  If it is not 0, The estimate for H is 
#                                       printed out.
#               nblk    --      The number of blocks the data should be divided
#                                       into.  
#               nlag    --      The number of different lags at which to
#                                       determine R/S.
#               power1  --      Gives the lower limit on which points to use
#                                       to calculate the slope(H).
#               power2  --      Gives the upper limit on which points to use
#                                       to calculate the slope(H).
#               shuffle --      Flag.  If not 0, then shuffle the data randomly.
#               overlap --      Flag.  Determines whether the lag values can 
#                               exceed the size of the block(1) or not(0).
#               ndiff   --      If the data is to be differenced, the number of
#                                       differences to take.
#               lag     --      If the data is to be differenced, the lag at 
#                                       which to difference it.
#               rflag   --      If 0, do the output for R itself.  Else, R/S.
#                               5/1/94.VT.
#               connect --      Flag.  If not 0, connect the points inside the 
#                               blocks with lines. 5/26/94.VT.  Also, output the
#                               values of H for each block.  11/20/94.  VT
#               fitls --        Flag.  If 1, do regular R/S.  If 2, use ltsreg 
#                               for fit.  If 3, use Lo's modified R/S.
#               plotflag --     Flag.  If T, the plot is done, otherwise, not.
#                               12/27/94.  VT.
#               output --       Flag.  If T then print in human readable form
#                               otherwise just return H. 26/6/05 RGC
        x <- NULL
        r <- NULL
        ra <- NULL
        xc <- NULL
        rc <- NULL
        rac <- NULL
#        cat("\n")       

        # Get the length of data vector.

        n <- length(data)       

        # Randomly shuffle the data or not?
        
        if(shuffle != 0) data <- data[sample(n)]        

        # Any differencing to be done?

        if(lag != 0 && ndiff != 0) data <- diff(data, lag, ndiff)       
        
        # Find the size of each of the blocks.          
        
        blksize <- n %/% nblk   
        
        # Find the increment, the intervals at which R/S is calculated.
        # If overlap = 0, then each block is divided into nlag intervals.
        # If it is not 0, then the whole data vector is divided into nlag
        # intervals.  The division is logarithmic.

        if(overlap != 0)
          increment <- (log10(n))/nlag
        else
          increment <- (log10(blksize))/nlag

        range <- Srs(data, nblk, nlag, overlap) 
        
        # Make vectors of x and y coordinates for the plot. They are
        # separated into the ones that will be used in calculating H,
        # and the ones that will not be used so.

        for(i in 1:nlag)
          {

            if (i * increment < power1)
              {
                xc <- c(xc, rep(log10(floor(10^(i * increment))), nblk))

                # Above line changed 2/28/95 to make the plotting consistent
                # with calculations.

                rc <- c(rc, range[((i - 1) * nblk + 1):(i * nblk)])
                rac <- c(rac, range[(nblk * nlag + (i - 1) * nblk + 1):
                                (nblk * nlag + i * nblk)])
              }

            if ((i * increment >= power1) & (log10(floor(10^(i * increment)))
                                             <= power2))
              {
                # Above/below line changed 2/28/95 to make plotting consistent 
                # with calculations.

                x <- c(x, rep(log10(floor(10^(i * increment))), nblk))
                r <- c(r, range[((i - 1) * nblk + 1):(i * nblk)])
                ra <- c(ra, range[(nblk * nlag + (i - 1) * nblk + 1):(
                                nblk * nlag + i * nblk)])
              }
                
            if (i * increment > power2)
              {
                xc <- c(xc, rep(log10(floor(10^(i * increment))), nblk))

                # Above line changed 2/28/95 to make the plotting consistent
                # with calculations.

                rc <- c(rc, range[((i - 1) * nblk + 1):(i * nblk)])
                rac <- c(rac, range[(nblk * nlag + (i - 1) * nblk + 1):
                                    (nblk * nlag + i * nblk)])
              }
          }

        # Take only the positive values of R.

        if (length(r[r > 1e-10]) > 0)
          {
            ld <- x[r > 0]
            rt <- r[r > 0]
            rat <- ra[r > 0]
            lr <- log10(rt)
            lra <- log10(rat)
          }
        else {
          cat("\n either the series is constant or no data was entered.\n\n")
          return(0)
        }

        if (length(rc[rc > 1e-10]) > 0)
          {
            ldc <- xc[rc > 0]
            rtc <- rc[rc > 0]
            ratc <- rac[rc > 0]
            lrc <- log10(rtc)
            lrac <- log10(ratc)
          }
        else {
          cat("\n either the series is constant or no data was entered.\n\n")
          return(0)
        }

        if (rflag == 0)
          {
            if (fitls == 1)
              {
                fit <- lsfit(ld, lr)$coef
                b <- fit[1]
                m <- fit[2]
              }

              if (fitls == 2)
                {
                  fit <- ltsreg(ld, lr)$coefficients
                  b <- fit[1]
                  m <- fit[2]
                }

              if (plotflag == T)
                plotit(slopes, b, m, ld, lr, "log10(r)", overlap, nblk)
          }
        else
          {
            # Do the calculations for fitting a least-squares line. For R/S.

            if (fitls == 1)
              {
                fita <- lsfit(ld, lra)$coef
                ba <- fita[1]
                ma <- fita[2]
              }
                
            if (fitls == 2)
              {
                fita <- ltsreg(ld, lra)$coefficients
                ba <- fita[1]
                ma <- fita[2]
              }

            # Plot the R/S statistic.
        
            if (plotflag == T)
              plotitrs(ba, ma, ld[ld >= 0.5], lra[ld >= 0.5], ldc[ldc >= 0.5],
                       lrac[ldc >= 0.5], "log10(r/s)")
          }

	if (connect != 0)
	  {
	    fitb <- array(0, dim = c(nblk, 2))
	    bb <- rep(0, nblk)
	    mb <- rep(0, nblk)
	    adjust <- 0

            if (rflag != 0)
              adjust <- nblk * nlag

            for (j in 1:nblk)
              {
		linex <- NULL
		liner <- NULL

		for (i in 1:nlag)
                   {
		     linex <- c(linex, log10(floor(10^(i * increment))))
		     liner <- c(liner, log10(range[adjust + (i - 1) * 
			        nblk + j]))
		   }

		lines(linex, liner, type = "l", lty = j)

		if (fitls == 1)
                  {
		    fitb[j,  ] <- lsfit(linex[power1 < linex & 
		                  linex < power2 & liner > 0], liner[power1 < 
		                  linex & linex < power2 & liner > 0])$coef

		    bb[j] <- fitb[j, 1]
		    mb[j] <- fitb[j, 2]
                  }

                if (fitls == 2)
                  {
		    fitb[j,  ] <- ltsreg(linex[power1 < linex & 
				  linex < power2 & liner > 0], liner[power1 < 
				  linex & linex < power2 & liner > 0])$
				  coefficients
		    bb[j] <- fitb[j, 1]
		    mb[j] <- fitb[j, 2]
		  }
	      }
	
            cat("\n Multiple values of H, :", mb, "\n")

        }

	# Output the H value.  

	if (slopes != 0)
          {
	    if (rflag == 0)
              {
	        cat("\n H for range: ", m, "\n")
		names(m) <- NULL
		
                if (connect == 0)
	          result <- m
		else
                  {
		    names(mb) <- NULL
		    result <- list(H.R = m, MultipleH = mb)
		  }
	      }
	    else
              {
                  
		      if (output) {
		          cat(" H for adjusted range: ", ma, "\n\n")
		      }
		names(ma) <- NULL
		if (connect == 0)
                  {
		    result <- ma
		  }
		else
                  {
		    names(mb) <- NULL
		    result <- list(H.RS = ma, MultipleH = mb)
	          }
	      }

	    return(result)
	  }
}



# Function which is called by plotrs.S to calculate the R/S statistic.
# Calls Crs.c, which does the actual work.

Srs<-function(data, nblk, nlag, overlap)
{
  n <- length(data)

  if (!is.loaded("Crs"))
      dyn.load("Crs.so")

  .C("Crs",
	   data = as.double(data),
	   n = n,
	   nblk = as.integer(nblk),
	   nlag = as.integer(nlag),
	   overlap = as.integer(overlap),
	   output = double(2 * nblk * nlag))$output
}

# This is a function which actually does the pox plot of R/S.  It is called by
# plotrs.S.
#
# yinter  -- The y-intercept of the calculated least-squares line(plotrs).
# slope   -- Slope of the calculated least-squares line(plotrs).
# x,y     -- Vectors of points to be plotted.   Used in calculating H.
# xc,yc   -- Vectors of points to be plotted. Not Used in calculating H.
# ylabel  -- Label for y-axis.
 
plotitrs <- function (yinter, slope, x, y, xc, yc, ylabel, overlap, nblk)
{
	# Plot the points.

        plot ( c (xc,0), c (yc,yinter), xlab="log10(d)", ylab=ylabel, type="n")
        points (xc,yc, pch=3, mkh=.06)
        points (x,y, pch=18, mkh=.06)
 
	# Plot the reference lines, with slopes 1/2, 1.

        abline (-.25,.5,lty=2)
        abline (yinter,1,lty=2)
}

plotit <- function (slopes, yinter, slope, x, y, ylabel, overlap, nblk)
{
        if (overlap != 0)
          {
            plot(c(x,0),c(y,yinter),xlab="log10(d)",ylab=ylabel,type="n")
            points(x,y)
          }
        else
          {
            plot(c(x,0),c(y,yinter),xlab="log10(d)",ylab=ylabel,type="n")
            text(x,y,label=c(1:nblk))
          }

        abline(yinter,.5,lty=2)
        abline(yinter,1,lty=2)

        if (slopes == 0)
          abline(yinter,slope)
}

plotrs.reg<-function(data, nblk = 5, nlag = 50, power1 = 0.7, power2 = 2.5,
     shuffle = 0, overlap = 1, ndiff = 0, lag = 0, rflag = 1, slopes = 1,
     connect = 0, plotflag = T)
{

# This function is different from R/S only in the way the fit is done.
# Instead of using lsfit(linear least squares), we use the more robust
# ltsreg.  The cost for this is a slight increase in the scattering
# of the estimates, but the advantage is the great increase in robustness
# (especially non-stationarity robustness.)
#
# This is the higher level function which produces a plot of the R/S 
# statistic, and gives an estimate for H, the index of similarity.
# This calls the routines Srs and plotit and plotitrs, also included 
# in this package.  Srs calls the C routine Crs.  
#
# The variables used are as follows:
#
#      data    --      The sample data values.  
#      nblk    --      The number of blocks the data should be divided
#                          into.  
#      nlag    --      The number of different lags at which to
#                          determine R/S.
#      power1  --      Gives the lower limit on which points to use
#                          to calculate the slope(H).
#      power2  --      Gives the upper limit on which points to use
#                          to calculate the slope(H).
#      shuffle --      Flag.  If not 0, then shuffle the data randomly.
#      overlap --      Flag.  Determines whether the lag values can 
#                          exceed the size of the block(1) or not(0).
#      ndiff   --      If the data is to be differenced, the number of
#                          differences to take.
#      lag     --      If the data is to be differenced, the lag at 
#                          which to difference it.
#      rflag   --      If 0, do the output for R itself.  Else, R/S.
#                          5/1/94.VT.
#      slopes  --      A flag.  If it is not 0, The estimate for H is 
#                          printed out.
#      connect --      Flag.  If not 0, connect the points inside the 
#                          blocks with lines. 5/26/94.VT. Also, output the
#                          values of H for each block.  11/20/94.  VT
#      plotflag --     Flag.  If T, the plot is done, otherwise, not.
#                          12/27/94.  VT.
        x <- NULL
        r <- NULL
        ra <- NULL
        xc <- NULL
        rc <- NULL
        rac <- NULL

        cat("\n")

        # Get the length of data vector.

        n <- length(data) 
 
        # Randomly shuffle the data or not?

        if (shuffle != 0)
          data <- data [sample(n)]

        # Any differencing to be done?

        if (lag != 0 && ndiff != 0)
          data <- diff(data, lag, ndiff)

        # Get the size of each of the blocks.

        blksize <- n %/% nblk

        # Find the increment, the intervals at which R/S is calculated.
        # If overlap = 0, then each block is divided into nlag intervals.
        # If it is not 0, then the whole data vector is divided into nlag
        # intervals.  The division is logarithmic.

        if (overlap != 0)
          increment <- (log10(n))/nlag
        else
          increment <- (log10(blksize))/nlag

        range <- Srs (data, nblk, nlag, overlap)

        # Make vectors of x and y coordinates for the plot.  They are
        # separated into the ones that will be used in calculating H,
        # and the ones that will not be used so.

        for (i in 1:nlag)
          {

            if (i * increment < power1)
              {
                xc <- c(xc, rep(i * increment, nblk))
                rc <- c(rc, range[((i - 1) * nblk + 1):(i * nblk)])
                rac <- c(rac, range[(nblk * nlag + (i - 1) * nblk + 1):
                                    (nblk * nlag + i * nblk)])
              }

            if ((i * increment >= power1) & (i * increment <= power2))
              {
                x <- c(x, rep(i * increment, nblk))
                r <- c(r, range[((i - 1) * nblk + 1):(i * nblk)])
                ra <- c(ra, range[(nblk * nlag + (i - 1) * nblk + 1):
                                  (nblk * nlag + i * nblk)])
              }

            if (i * increment > power2)
              {
                xc <- c(xc, rep(i * increment, nblk))
                rc <- c(rc, range[((i - 1) * nblk + 1):(i * nblk)])
                rac <- c(rac, range[(nblk * nlag + (i - 1) * nblk + 1):
                                    (nblk * nlag + i * nblk)])
              }
          }

        # Take only the positive values of R.

        if (length(r[r > 1e-10]) > 0)
          {
            ld <- x[r > 0]
            rt <- r[r > 0]
            rat <- ra[r > 0]
            lr <- log10(rt)
            lra <- log10(rat)
          }
        else
          cat("\n either the series is constant or no data was entered.\n\n")

        if (length(rc[rc > 1e-10]) > 0)
          {
            ldc <- xc[rc > 0]
            rtc <- rc[rc > 0]
            ratc <- rac[rc > 0]
            lrc <- log10(rtc)
            lrac <- log10(ratc)
          }
        else
          cat("\n either the series is constant or no data was entered.\n\n")

        if (rflag == 0)
          {
##############################			Different from R/S.   
            fit <- ltsreg(ld, lr)
            b <- fit$coefficients[1]
            m <- fit$coefficients[2]
##############################		
            if (plotflag == T)
              plotit (slopes, b, m, ld, lr, "log10(r)", overlap, nblk)
          }
        else
          {
            # Do the calculations for fitting a least-squares line. For R/S.

##############################			Different from R/S.
            fita <- ltsreg(ld, lra)
            ba <- fita$coefficients[1]
            ma <- fita$coefficients[2]          # Plot the R/S statistic.
##############################

            if (plotflag == T)
              plotitrs(ba, ma, ld[ld >= 0.5], lra[ld >= 0.5],
                       ldc[ldc >= 0.5], lrac[ldc >= 0.5], "log10(r/s)")
          }

        if (connect != 0)
          {
            fitb <- rep(0, nblk)
            bb <- rep(0, nblk)
            mb <- rep(0, nblk)
            adjust <- nblk * nlag

            if (rflag == 0)
              adjust <- 0

            for (j in 1:nblk)
              {
                linex <- NULL
                liner <- NULL

                for (i in 1:nlag)
                  {
                    linex <- c(linex, i * increment)
                    liner <- c(liner, log10(range[adjust + (i - 1) * 
                               nblk + j]))
                  }

                lines(linex, liner, type = "l", lty = j)
                fitb[j] <- lsfit(linex[power1 < linex & linex < power2],
                                liner[power1 < linex & linex < power2])
                bb[j] <- fitb[j]$coef[1]
                mb[j] <- fitb[j]$coef[2]
              }

            cat("\n Multiple values of H, :", mb, "\n")

          }

        # Output the H value.

        if (slopes != 0)
          {

            if (rflag == 0)
              {
                cat("\n H for range: ", m, "\n")
                names(m) <- NULL

                if (connect == 0)
                  {
                    result <- list(H.R = m)
                  }
                else
                  {
                    names(mb) <- NULL
                    result <- list(H.R = m, MultipleH = mb)
                  }
              }
            else
              {
                cat(" H for adjusted range: ", ma, "\n\n")
                names(ma) <- NULL

                if (connect == 0)
                  {
                    result <- list(H.RS = ma)
                  }
                else
                  {
                    names(mb) <- NULL
                    result <- list(H.RS = ma, MultipleH = mb)
                  }
              }

            return(result)
        }     
}

# eof plotrs.S
