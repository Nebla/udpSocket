# Code by Diethelm Wuertz, modified by Richard G. Clegg 2005.

wavelet <- function(x, length = NULL, order = 2, octave = c(2, 8), 
plotflag = TRUE, title = NULL, description = NULL, output= T)    
{   # A function implemented by Diethelm Wuertz
    dyn.load ("wavedecomp.so")
    # Description:
    #   Function to do the Wavelet estimator of H.
    
    # Arguments:
    #   x - Data set.
    #   length - Length of data to be used (must be power of 2) 
    #       if NULL, the previous power will be used
    #   octave - Beginning and ending octave for estimation.

    # Details:
    #   This method computes the Discrete Wavelet Transform, averages the 
    #   squares of the coefficients of the transform, and then performs a 
    #   linear regression on the logarithm of the average, versus the log 
    #   of j, the scale parameter of the transform. The result should be 
    #   directly proportional to H.
    #   There are several options available for using this method: method.
    #   1.  The length of the data must be entered (power of 2).
    #   2.  c(j1, j2) are the beginning and ending octaves for the estimation.
    #   3.  'order' is the order of the wavelet. (2 default)
    #   5.  Calls functions from R's Wavelet package. ( wd, accessD ).
    #   6.  Inside function, a bound.effect is used in the estimation to 
    #       avoid boundary effects on the coefficients.

    # Authors:
    #   Based on work by Ardry and Flandrin.
    #   Originally written by Vadim Teverovsky 1997.   
    
    # Notes:
    #   Calls functions from R's package 'wavethresh'
    
    # FUNCTION:
    
    # Settings:
    N = order
    call = match.call()
    j1 = octave[1]
    j2 = octave[2]
    if(is.null(length)) length = 2^floor(log(length(x))/log(2))
    noctave = log(length, base = 2) - 1
    bound.effect = ceiling(log(2*N, base = 2))     
    
    # Calculate:
    transform = .wwd(x[1:(length)], filter = N)
    statistic = rep(0, noctave)
    if (j2 > noctave - bound.effect) {
        # cat("Upper bound too high, resetting to ", noctave-bound.effect, "\n")
        j2 = noctave - bound.effect 
        octave[2] = j2
    }       
    for (j in 1:(noctave - bound.effect)) {
        statistic[j] = log(mean((.waccessD(transform, 
            lev = (noctave+1-j))[N:(2^(noctave+1-j)-N)])^2), base = 2) 
    }
    
    # Fit:
    X = 10^c(j1:j2)
    Y = 10^statistic[j1:j2]
    fit = lsfit(log10(X), log10(Y))
    fitH = lsfit(log10(X), log10(Y*X)/2)
    diag = as.data.frame(ls.print(fitH, print.it = FALSE)[[2]][[1]])   
    beta = fit$coef[[2]]
    H = (beta+1)/2
    
    # Plot Values:
    plot = list(
        m = 10^c(1:(noctave - bound.effect)), 
        data = 10^statistic[1:(noctave - bound.effect)], 
        weights = rep(1, times = length(X)), 
        abline = FALSE, cex = 0.5, 
        xlab = "Octave", ylab = "Statistic") 
        
    # Add Slope:    
    # abline(fit$coef[[1]], fit$coef[[2]])}
    
    # Add:
    if (is.null(title)) title = "Hurst Exponent from Wavelet Estimator"
    if (is.null(description)) description = as.character(date())
    
    # Return Value:
    if (output == T) {
        cat ("H = ",diag[[1]][2]," +/- ", diag[[2]][2], " \n")
    }
    if (plotflag == T) {
        labels = TRUE
		if (labels) {
	        xlab = plot$xlab
	        ylab = plot$ylab
	        H = as.character(round(diag[[1]][2], digits = 4))
	        main = paste( "Wavelet Method\n H =", H)
	        M = plot$m[plot$weights == 1]
	        min.M = as.character(min(M))
	        max.M = as.character(max(M))
	        M = as.character(length(M))
	        gridlines = TRUE 
	    } else {    
	        xlab = ""
	        ylab = ""
	        main = "" 
	        gridlines = FALSE 
	    } 
	     x = c(0, log10(plot$m))
	    y = c(0, log10(plot$data))
	    wt = plot$weights
	    plot(x, y, type = "n", xlab = xlab, ylab = ylab)
	    title(main = main)
	    if (gridlines) grid()
	    x = x[-1]
	    y = y[-1]
	    points(x[wt == 1], y[wt == 1], pch = 19, cex = plot$cex)
	    points(x[wt == 0], y[wt == 0], pch = 3, cex = plot$cex)
	    # y = mx + c
	    m = fit$coeff[[2]]
	    a = fit$coeff[[1]]
	    x.fit = x[wt == 1]
	    y.fit = m * x.fit + a
	    lines(x.fit, y.fit, lwd = 2)
	    if (is.numeric(plot$abline))
	        abline(plot$abline[1], plot$abline[2], lty = 3)
    }
    return (c(diag[[1]][2],diag[[2]][2]))
#    new("fHURST", 
#        call = call,
#       method = "Wavelet Method",
#       hurst = list(H = H, beta = beta, diag = diag),
#       parameter = list(length = length, order = order, octave = octave),        
#        data = list(x = x),
#        plot = plot,
#        fit = fit,
#        title = title,
#        description = description
#        )    
}

.waccessD = 
function(wd.obj, level, boundary = FALSE)
{	# A function copied from R-package wavethresh

    # FUNCTION:
    
    # Settings:
    ctmp = class(wd.obj)
    if (is.null(ctmp) || all(ctmp != "wd"))
        stop("argument `wd.obj' is not of class \"wd\"")
    if (level < 0) 
        stop("Must have a positive level")
    else if(level > wd.obj$nlevels - 1)
        stop("`level' must be less than resolution (= nlevels)")
    level = level + 1
    first.last.d = wd.obj$fl.dbase$first.last.d
    first.level = first.last.d[level, 1]
    last.level  = first.last.d[level, 2]
    off.l = first.last.d[level, 3]
    
    if (boundary) {
        n = last.level - first.level + 1
        wd.obj$D[(off.l + 1):(off.l + n)]
    } else {
        n = 2^(level - 1)
        wd.obj$D[(off.l + 1 - first.level):(off.l + n - first.level)]
    }
}


.wwd = 
function(data, filter.number = 2, family = c("DaubExPhase", "DaubLeAsymm"),
bc = c("periodic", "symmetric"), verbose = getOption("verbose"))
{	# A function copied from R-package wavethresh

    # FUNCTION:
    
    # Settings:
    if (verbose) cat("Argument checking...")
    family = match.arg(family)
    bc = match.arg(bc)
    DataLength = length(data)           

    # Check that we have a power of 2 data elements
    nlevels = log(DataLength)/log(2)
    if(round(nlevels) != nlevels)
        stop("The length of data is not a power of 2")

    # Select the appropriate filter
    if (verbose) cat("...done\nFilter...")
    filter = .wfilter.select(filter.number = filter.number, family = family)

    # Build the first/last database
    if (verbose) cat("...selected\nFirst/last database...")
    fl.dbase = .wfirst.last(LengthH = length(filter$H), DataLength =
        DataLength, bc = bc) 

    # Put in the data
    C = rep(0, fl.dbase$ntotal)
    C[1:DataLength] = data              
    error = if (verbose) 1 else 0
    if (verbose) cat("built\nObject code...")

    # Compute the decomposition
    if(verbose) cat("Decomposing...\n")
    nbc = switch(bc, periodic = 1, symmetric = 2)
    wavelet.decomposition = .C("wavedecomp",
        C = as.double(C),
        LengthC = as.integer(fl.dbase$ntotal),
        D = double(fl.dbase$ntotal.d),
        LengthD = as.integer(fl.dbase$ntotal.d),
        H = as.double(filter$H),
        LengthH = as.integer(length(filter$H)),
        nlevels = as.integer(nlevels),
        firstC = as.integer(fl.dbase$first.last.c[, 1]),
        lastC = as.integer(fl.dbase$first.last.c[, 2]),
        offsetC = as.integer(fl.dbase$first.last.c[, 3]),
        firstD = as.integer(fl.dbase$first.last.d[, 1]),
        lastD = as.integer(fl.dbase$first.last.d[, 2]),
        offsetD = as.integer(fl.dbase$first.last.d[, 3]),
        nbc = as.integer(nbc),
        error = as.integer(error))
           
    if (verbose) cat("done\n")
    error = wavelet.decomposition$error
    if (error != 0) stop(paste("Error", error, " occured in wavedecomp"))

    # Result:
    l = list(C = wavelet.decomposition$C, D = wavelet.decomposition$D,
        nlevels = wavelet.decomposition$nlevels, fl.dbase = fl.dbase,
        filter = filter, bc = bc)
    class(l) = "wd"
    
    # Return Value:
    l
}
.wfilter.select = 
function(filter.number, family = c("DaubExPhase", "DaubLeAsymm"),
constant = 1)
{	# A function copied from R-package wavethresh

    # FUNCTION:
    
    # Settings:
    family = match.arg(family)# one of the two, maybe abbrev. in call
    if ((filter.number = as.integer(filter.number)) <= 0)
        stop("invalid `filter.number'")
    if (family == "DaubExPhase") {

    # The following wavelet coefficients are taken from 
    # 	Daubechies, I (1988) 
    # 	Orthonormal Bases of Wavelets
    # 	Communications on Pure and Applied Mathematics. Page 980
    # or 
    #	Ten Lectures on Wavelets, Daubechies, I, 1992
    # 	CBMS-NSF Regional Conference Series, page 195, Table 6.1
    # 	Comment from that table reads:
    #   "The filter coefficients for the compactly supported wavelets
    #   with extremal phase and highest number of vanishing moments
    #   compatible with their support width".
    filter.name = 
        switch(filter.number,
            { 
            # filter.number  -- 1 --
            # This is for the Haar basis. (not in Daubechies).
            H = rep(1/sqrt(2), 2)
            "Haar wavelet"
            },
            { # filter.number  -- 2 --
            H = c(0.48296291314500001,   0.83651630373800001, 
                  0.22414386804200001, 
                 -0.12940952255099999)
            "Daub cmpct on ext. phase N=2"
            },
            { # filter.number  -- 3 --
            H = c(0.33267055294999998,   0.80689150931099995,  
                  0.45987750211799999,  -0.13501102001000001, 
                 -0.085441273882,        0.035226291882000001) 
           "Daub cmpct on ext. phase N=3"
           },
           { # filter.number  -- 4 --
           H = c(0.23037781330900001,    0.71484657055300005,  
                 0.63088076793000003,   -0.027983769417,        
                -0.18703481171899999,    0.030841381836,   
                 0.032883011667000001,  -0.010597401785) 
           "Daub cmpct on ext. phase N=4"
           },
           { # filter.number  -- 5 --
           H = c(0.160102397974,         0.60382926979700002,  
                 0.72430852843799998,    0.138428145901,      
                -0.242294887066,        -0.032244869585000002,
                 0.07757149384,         -0.006241490213,      
                -0.012580751999,         0.003335725285)
           "Daub cmpct on ext. phase N=5"
           },
           { # filter.number  -- 6 --
           H = c(0.11154074335,          0.49462389039799998,  
                 0.751133908021,         0.31525035170900001,   
                -0.22626469396500001,   -0.12976686756700001, 
                 0.097501605586999995,   0.02752286553,       
                -0.031582039318000001,   0.000553842201,         
                 0.004777257511,        -0.001077301085)  
           "Daub cmpct on ext. phase N=6"
           },
           {  # filter.number -- 7 --
           H = c(0.077852054084999997,   0.396539319482,       
                 0.72913209084599995,    0.469782287405,        
                -0.14390600392899999,   -0.22403618499399999, 
                 0.071309219267,         0.080612609151000006,
                -0.038029936935000001,  -0.016574541631,         
                 0.012550998556,         0.000429577973,   
                -0.001801640704,         0.0003537138)     
           "Daub cmpct on ext. phase N=7"
           },
           { # filter.number  -- 8 --
           H = c(0.054415842243000001,   0.31287159091400002,  
                 0.67563073629699999,    0.58535468365400001,   
                -0.015829105256,        -0.28401554296199999, 
                 0.000472484574,         0.12874742662,         
                -0.017369301002000001,  -0.044088253931,         
                 0.013981027917,         0.008746094047,  
                -0.004870352993,        -0.000391740373,         
                 0.000675449406,        -0.000117476784) 
           "Daub cmpct on ext. phase N=8"
           },
           { # filter.number  -- 9 --
           H = c(0.038077947363999998,   0.24383467461300001, 
                 0.60482312369000002,    0.65728807805099998,    
                 0.13319738582499999,   -0.293273783279,  
                -0.096840783222999993,   0.14854074933799999,  
                 0.030725681479000001,  -0.067632829061000002,   
                 0.000250947115,         0.022361662124,   
                -0.004723204758,        -0.004281503682,       
                 0.001847646883,         0.000230385764,         
                -0.000251963189,         3.934732e-05)     
           "Daub cmpct on ext. phase N=9"
           },
           { # filter.number -- 10 --
           H = c(0.026670057901000001,   0.188176800078,        
                 0.52720118893199996,    0.688459039454,         
                 0.28117234366100002,   -0.24984642432699999,
                -0.19594627437699999,    0.127369340336,         
                 0.093057364604000006,  -0.071394147165999997,  
                -0.029457536822,         0.033212674058999997, 
                 0.003606553567,        -0.010733175483,        
                 0.001395351747,         0.001992405295,        
                -0.000685856695,        -0.000116466855,  
                 9.358867e-05,          -1.3264203e-05)   
           "Daub cmpct on ext. phase N=10"
           }
           ) #  switch ( filter.number )
    if (is.null(filter.name))
        stop(paste("Unknown filter number (not in {1:10}) for", family,
               "(Daubechies wavelets with extremal phase...)"))

    } else { 
        # if(family == "DaubLeAsymm")
        # The following wavelet coefficients are taken from
        # Ten Lectures on Wavelets, Daubechies, I, 1992
        # CBMS-NSF Regional Conference Series, page 198, Table 6.3
        # Comment from that table reads:
        #   "The low pass filter coefficients for the "least-asymmetric"
        #   compactly supported wavelets with maximum number of
        #   vanishing moments, for N = 4 to 10
        filter.name = 
            switch(filter.number,
               NULL, NULL, NULL, 
               { # filter.number  -- 4 --
               H = c(-0.107148901418, -0.041910965125,   0.703739068656,   
                     1.136658243408,   0.421234534204,  -0.140317624179,  
                    -0.017824701442,   0.045570345896)   
               "Daub cmpct on least asymm N=4"
               },
               { # filter.number  -- 5 --
               H = c(0.038654795955,   0.041746864422,  -0.055344186117,  
                     0.281990696854,   1.023052966894,   0.89658164838,    
                     0.023478923136,  -0.247951362613,  -0.029842499869,  
                     0.027632152958)   
               "Daub cmpct on least asymm N=5"
               },
               { # filter.number  -- 6 --
               H = c(0.021784700327,   0.004936612372,  -0.166863215412,  
                    -0.068323121587,   0.694457972958,   1.113892783926,   
                     0.477904371333,  -0.102724969862,  -0.029783751299,  
                     0.06325056266,    0.002499922093,  -0.011031867509)  
               "Daub cmpct on least asymm N=6"
               },
               { # filter.number  -- 7 --
               H = c(0.003792658534,  -0.001481225915,  -0.017870431651,  
                     0.043155452582,   0.096014767936,  -0.070078291222,  
                     0.024665659489,   0.758162601964,   1.085782709814,   
                     0.408183939725,  -0.198056706807,  -0.152463871896,  
                     0.005671342686,   0.014521394762)   
               "Daub cmpct on least asymm N=7"
               },
               { # filter.number  -- 8 --
               H = c(0.002672793393,  -0.0004283943,    -0.021145686528,   
                     0.005386388754,   0.069490465911,  -0.038493521263,   
                    -0.073462508761,   0.515398670374,   1.099106630537,    
                     0.68074534719,   -0.086653615406,  -0.202648655286,  
                     0.010758611751,   0.044823623042,  -0.000766690896,   
                    -0.004783458512)   
               "Daub cmpct on least asymm N=8"
               },
               { # filter.number  -- 9 --
               H = c(0.001512487309,  -0.000669141509,  -0.014515578553, 
                     0.012528896242,   0.087791251554,  -0.02578644593,  
                    -0.270893783503,   0.049882830959,   0.873048407349,  
                     1.015259790832,   0.337658923602,  -0.077172161097,  
                     0.000825140929,   0.042744433602,  -0.016303351226,  
                    -0.018769396836,   0.000876502539,   0.001981193736)   
               "Daub cmpct on least asymm N=9"
               },
               { # filter.number  -- 10 --
               H = c(0.001089170447,   0.00013524502,   -0.01222064263,   
                    -0.002072363923,   0.064950924579,   0.016418869426,  
                    -0.225558972234,  -0.100240215031,   0.667071338154,  
                     1.0882515305,     0.542813011213,  -0.050256540092,  
                    -0.045240772218,   0.07070356755,    0.008152816799,   
                    -0.028786231926,  -0.001137535314,   0.006495728375,   
                     8.0661204e-05,   -0.000649589896)  
               "Daub cmpct on least asymm N=10"
               }
           ) # switch ( filter.number )

    if(is.null(filter.name))
        stop(paste("Unknown filter number (not in {4:10}) for", family,
            "\n (Daubechies wavelets with least asymmetry...)"))
    H = H/sqrt(2)
    } # ""DaubLeAsymm" family

    H = H/constant
    
    # Return Value:
    list(H = H, name = filter.name, family = family,
        filter.number = filter.number)
}


# ------------------------------------------------------------------------------


.wfirst.last = 
function(LengthH, DataLength, bc = c("periodic", "symmetric"))
{	# A function copied from R-package wavethresh

    # FUNCTION:
    
    # Settings:
    bc = match.arg(bc)
    levels = log(DataLength)/log(2)
    first.last.c = matrix(0, nrow = levels + 1, ncol = 3,
        dimnames = list(NULL, c("First", "Last", "Offset")))
    first.last.d = matrix(0, nrow = levels, ncol = 3,
        dimnames = list(NULL, c("First", "Last", "Offset")))
    if (bc == "periodic") {
        # Periodic boundary correction
        first.last.c[, 1] = rep(0, levels + 1)
        first.last.c[, 2] = 2^(0:levels) - 1
        first.last.c[, 3] = rev(c(0, cumsum(rev(1 + first.last.c[, 2])
                             )[1:levels]))
        first.last.d[, 1] = rep(0, levels)
        first.last.d[, 2] = 2^(0:(levels - 1)) - 1
        first.last.d[, 3] = rev(c(0, cumsum(rev(1 + first.last.d[, 2])
            )[1:(levels - 1)]))
        ntotal = 2 * DataLength - 1
        ntotal.d = DataLength - 1
    } else { 
        # (bc == "symmetric")
        # Symmetric boundary reflection
        first.last.c[levels + 1, 1] = 0
        first.last.c[levels + 1, 2] = DataLength - 1
        first.last.c[levels + 1, 3] = 0
        ntotal = first.last.c[levels + 1, 2] - first.last.c[levels + 1, 1] + 1
        ntotal.d = 0
        for (i in levels:1) {
            first.last.c[i, 1] = trunc(0.5 * (1 - LengthH +
                first.last.c[i + 1, 1]))
            first.last.c[i, 2] = trunc(0.5 * first.last.c[i + 1, 2])
            first.last.c[i, 3] = first.last.c[i + 1, 3] +
            first.last.c[i + 1, 2] - first.last.c[i + 1, 1] + 1
            first.last.d[i, 1] = trunc(0.5 * (first.last.c[i + 1, 1] - 1))
            first.last.d[i, 2] = trunc(0.5 * (first.last.c[i + 1, 2] + 
                LengthH - 2))
            if(i != levels) {
                first.last.d[i, 3] = first.last.d[i + 1, 3] +
                    first.last.d[i + 1, 2] - first.last.d[i + 1, 1] + 1
            }
            ntotal = ntotal + first.last.c[i, 2] - first.last.c[i, 1] + 1
            ntotal.d = ntotal.d + first.last.d[i, 2] - first.last.d[i, 1] + 1
        }
    }
    names(ntotal) = NULL
    names(ntotal.d) = NULL
    
    # Return Value:
    list(first.last.c = first.last.c, ntotal = ntotal,
        first.last.d = first.last.d, ntotal.d = ntotal.d)
}




