matrix.data <- read.table(matrix_file)
matrix <- as.matrix(matrix.data)
dimnames(matrix) <- list(xlabels, ylabels)
