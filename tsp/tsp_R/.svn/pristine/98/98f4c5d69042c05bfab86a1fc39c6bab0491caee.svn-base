library("TSP")

m <- matrix(scan("usca312_dist.txt", skip=7), nrow=312, byrow=TRUE )
d <- as.dist(m)

l <- readLines("usca312_name.txt")[-c(1:15)]


attr(d, "Labels") <- l
attr(d, "method") <- "euclidean"

USCA312 <- TSP(as.dist(d))
save(USCA312, file="USCA312.rda", compress = TRUE)
