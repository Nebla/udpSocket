# Calc Hurst Parameter by various means ---  
# Richard G. Clegg (richard@richardclegg.org) 2005

source ("plotrs.R")
#source ("plotvar.R")
#source ("plotper.R")
source ("wavelet.R")
#source ("locwhitt.R")

#Given a file or a vector of data, calculates H in 
# various ways.  Terse produces latex friendly output
# for tables. 
# fast attempts to smartly truncate data to powers of 2, 3, or 5 which can
# speed up fft -- use this if per and wavelet are taking undue time
calcHurst <-function(data= NULL, file= NULL, terse=F, fast=F)

{
    if (is.character(data)) {
       stop("data must be numeric, to read from file use file=")
    }
    if (!is.null(file)) {
        data<-scan(file)
    }   
    if (fast == T) {
       data<-powTruncate(c(2,3,5), data)
    }
    if (length(data) <=100 || !is.double(data)) {
        stop("Bad data supplied\n")
    }
    
    
    hrs<-plotrs(data,plotflag= F, output=F)
    #hvar<-plotvar(data,plotflag= F,output=F)
    #hper<-plotper(data,plotflag=F, output=F)
    hwav<-wavelet(data,plotflag=F, output=F)
    #hwhi<-locwhitt(data,output=F)
    if (terse == T) {
        cat (round(hrs,digits=3)," & ",
            #round(hvar, digits=3), " & ",
            #round(hper, digits=3), " & ",
            round(hwav[1], digits=3), "$\\pm$",round(hwav[2], digits=3), " & ",
            #round(hwhi, digits=3), " \\\\ \n"
            )
    } else {
        cat ("RS plot H=",hrs,"\n")
        #cat ("Agg var H=",hvar,"\n")
        #cat ("Period. H=",hper,"\n")
        cat ("Wavelet H=", hwav[1], " +/- ", hwav[2],"\n")
        #cat ("Loc. W. H=", hwhi,"\n")
    }
}

powTruncate<-function(powers,data)
{
  n<-length(data)
  ps<-powers^(floor(log(n,powers)))
  newn<-max(ps)
  cat ("Truncating data from ",n," to ",newn," \n")
  data[1:newn]
}

calcHurstDistort <-function(data= NULL, file= NULL, terse=F)
{
    
    if (!is.null(file)) {
        data<-scan(file)
    }   
    if (length(data) <=100 || !is.double(data)) {
        stop("Bad data supplied\n")
    }
    if (!terse)
        cat("Raw data\n")
    else 
        cat("None & ")
    calcHurst(data, terse= terse)
#    cat(sd(data),"\n")
    x<-seq(1,length(data))
    if (!terse)
        cat("Distorted with AR(1)\n")
    else 
        cat("AR(1) & ")
    ar<-arima.sim(model=list(ar=0.9), n=length(data))
    ar<-sd(data)/sd(ar)*ar
#    cat(sd(ar),"\n")
    data2<-data+ar
    calcHurst(data2, terse=terse)
    if (!terse)
        cat("Distorted with sin wave\n")
    else
        cat("Sin & ")
    sinwave<-sin(20*pi*x/length(x))
    sinwave<-sd(data)/sd(sinwave)*sinwave
#    cat(sd(sinwave),"\n")
    data3 <- data+sinwave
    calcHurst(data3, terse=terse)
    if (!terse)
        cat("Distorted with trend\n")
    else
        cat("Trend & ")
    lintrend <- 2*x/length(x)- 1
    lintrend<- sd(data)/sd(lintrend)*lintrend
#    cat(sd(lintrend),"\n")
    data4 <- data + lintrend
    calcHurst(data4,terse=terse)
   
}

calcHurstFilter <-function(data= NULL, file= NULL, terse=F)
{
    
    if (!is.null(file)) {
        data<-scan(file)
    }   
    if (length(data) <=100 || !is.double(data)) {
        stop("Bad data supplied\n")
    }
    x<-seq(1,length(data))
    if (!terse)
        cat("Raw data\n")
    else
        cat("None & ")
    calcHurst(data,terse=terse)
    if (min(data) <= 0) {
        cat("Log inappropriate for negative or zero data\n")
    } else {
        if (!terse)
            cat("Logged data\n")
        else
            cat("Log & ")
        data2<- log(data)
        calcHurst(data2,terse=terse)
    }
    if (!terse)
        cat("Subtract trend\n")
    else
        cat("Trend & ")
    pm<-lm(data ~ poly(x, degree=1))
    data3<-pm$residuals
    calcHurst(data3, terse=terse)
    if (!terse)
        cat("Subtract polynomial\n")
    else
        cat("Poly & ")
    pm<-lm(data ~ poly(x, degree=10))
    
    data4<-pm$residuals
    calcHurst(data4, terse=terse) 
}
