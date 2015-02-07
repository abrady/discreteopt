## create data

library(maps)
library(sp)
library(maptools)
nms <- scan("usca312_name.txt", "character", skip=15, sep="\n")
dms <- read.fwf("usca312_dms.txt", skip=4, header=FALSE,
    widths=c(2,1,2,1,2,1,1,1,3,1,2,1,2,1,1))
dd <- data.frame(long=-(dms$V9+(dms$V11/60)+(dms$V13/3600)),
    lat=(dms$V1+(dms$V3/60)+(dms$V5/3600)), name=nms)
USCA312_coords <- SpatialPointsDataFrame(cbind(dd$long, dd$lat),
    proj4string=CRS("+proj=longlat +datum=WGS84"), data=dd)
USCA312_basemap <- map2SpatialLines(map("world", 
        xlim=c(-166,-47), ylim=c(15,83),
        plot=FALSE), proj4string=CRS("+proj=longlat +datum=WGS84"))
plot(as(USCA312_coords, "Spatial"), axes=TRUE)
plot(USCA312_basemap, add=TRUE, col = "gray")
#points(USCA312_coords, pch=3, cex=0.5, col="black")

save(USCA312_coords, USCA312_basemap, , file = "USCA312_map.rda", compress = TRUE)




