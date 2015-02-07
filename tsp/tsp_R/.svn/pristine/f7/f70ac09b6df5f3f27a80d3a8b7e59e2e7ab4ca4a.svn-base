library("TSP")
data("USCA312")

m <- as.matrix(USCA312)

labels <- dimnames(m)[1]

m <- m[1:50,1:50]
USCA50 <- TSP(m)
attr(USCA50, "method") <- "euclidean"
save(USCA50, file="USCA50.rda", compress = TRUE)





