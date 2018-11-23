#########################################################
## This script contains functions that can be used in modeling script: generate_models.R
#########################################################
# function to check our assumptions
# two assumptions are taken into account here
# 1. at least two arcs from regulators to responders
# 2. the number of incoming arcs on any node will be limited to two
assumptions <- function (list_of_matrices) {
    list <- lapply(list_of_matrices, function(x)
    if ((nnzero(as.matrix(x)[3:4, 1]) >= 1) && (nnzero(as.matrix(x)[3:4, 2]) >= 1))
    return(x))
    list <- list[lapply(list, length) > 0]
    return(list)
}

# builds a block matrix whose diagonals are the square matrices provided.
blockMatrixDiagonal <- function(...) {
    matrixList <- list(...)
    if (is.list(matrixList[[1]])) matrixList <- matrixList[[1]]

    dimensions <- sapply(matrixList, FUN = function(x) dim(x)[1])
    finalDimension <- sum(dimensions)
    finalMatrix <- matrix("", nrow = finalDimension, ncol = finalDimension)
    index <- 1
    for (k in 1:length(dimensions)) {
        finalMatrix[index:(index+dimensions[k]-1), index:(index+dimensions[k]-1)] <- matrixList[[k]]
        index <- index+dimensions[k]
    }
    finalMatrix
}

# this funtion will take a block matrix and break to smaller matrices.
blockMatrixSplitter <- function(...) {
    matrix <- as.matrix(...)
    for (i in seq(1, nrow(matrix), 4)) {
        j <- i+3
        singleMatrix <- matrix[i:j, i:j]
        singleMatrix
    }
}
