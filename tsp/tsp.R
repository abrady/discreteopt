# tsp visualizer
#install.packages("TSP")
library(igraph)
library(TSP)
g <- barabasi.game(100)
#plot( g, vertex.size=0, vertex.label=NA, edge.arrow.size=0 )
# read.graph('./data/tsp_5_1')
# data("USCA50")

## make runs comparable
data("USCA50")
## set the distances towards Austin to zero which makes it a ATSP
austin <- which(labels(USCA50) == "Austin, TX")
atsp <- as.ATSP(USCA50)
atsp[, austin] <- 0
## reformulate as a TSP
tsp <- reformulate_ATSP_as_TSP(atsp)
labels(tsp)
## create tour (now you could use Concorde or LK)
tour_atsp <- solve_TSP(tsp, method="nn")
head(labels(tour_atsp), n = 10)
## filter out the dummy cities
tour <- TOUR(tour_atsp[tour_atsp <= n_of_cities(atsp)])
tour_len = tour_length(atsp, tour)