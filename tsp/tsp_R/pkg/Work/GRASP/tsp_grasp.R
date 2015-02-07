## Greedy Randomized Adaptive Search Procedure
## (Leonidas S. Pitsoulis and Mauricio G. C. Resende 2001)

tsp_grasp <- function (x, control = NULL) 
{
  x <- as.matrix(x)
  n <- ncol(x)

  ## grasp parameters
  iterations <- control$iterations
  if(is.null(iterations)) iterations <- 100
  
  ## local search parameters
  max_i <- control$max_i
  if(is.null(max_i)) max_i <- 100
  k <- control$k
  if(is.null(k)) k <- 3
  
  ## starting optimum (f* = oo)
  optimum <- sum(x)

  i <- 0
  while(i < iterations){
    ## alpha for calculating threshold (the restricted candidate list - RCL)
    ## need an interface for selecting various methods

    ## alpha <- 0 # nearest neighbour
    ## alpha <- runif(1,0,1) ## proposed by Resende et al
    ## TODO: Reactive GRASP (Prais and Ribeiro)
    alpha <- rgamma(1,1,6) ## proposed by theussl, gartner, koeb, lovric
    ## alpha <- runif(1,0.05,0.25) ## also good solutions
  
    ## generate a greedy randomized solution
    grasp.route <- .construct_greedy(x, n, alpha)

    ## TODO: hash table

    ## improve solution using local search
    route <- local_search(x,grasp.route, n, max_i, k) 
    newopt <- .objective_function(x,route,n)
    if(newopt < optimum){
      optimum <- newopt
      order <- route
    }
    i <- i + 1
  }
  as.numeric(order)  
}

## construct initial solution
.construct_greedy <- function (x, n, alpha = runif(1, 0, 1)) 
{
  ## start with a random city
  order <- c(sample(1:n))
  city.indices <- c(1:n)[-start]
  while (length(city.indices) != 0) {
    current.dists <- x[, order[1]][-order]
    c0 <- min(current.dists)
    c1 <- max(current.dists)
    threshold <- c0 + alpha * (c1 - c0)
    candidate <- which(current.dists <= threshold)
    if(length(candidate) > 1) candidate <- sample(candidate, 1)
    order <- c(city.indices[candidate], order)
    city.indices <- city.indices[-candidate]
  }
  rev(order)
}

## calculates routelength including the route from end to start
.objective_function <- function(x,route,n)
{
  i <- route
  j <- c(route[-1],route[1])
  sum(x[(j-1)*n + i])
}

## local search algorithm
local_search <- function (x, route, n, max_i = 1000, k = 3) {
    startValue <- newValue <- .objective_function(x, route, n)
    i <- 0
    while ((startValue <= newValue) && (i <= max_i)) {
        newRoute <- .k_opt_move(route, k, n) ## call the k-opt neighborhood search
        newValue <- .objective_function(x, newRoute, n)
        i <- i + 1
    }
    if(newValue <= startValue) route <- newRoute
    route
}

## k-opt neighborhood
.k_opt_move <- function (route, k, n) {
    random.indices <- sample(2:n, k)
    indices.to.change <- route[random.indices]
    replace(route, random.indices[c(2:k, 1)], indices.to.change)
}
