stage.data <- read.table(stage_matrix_file)
stage_matrix <- as.matrix(stage.data)
dimnames(stage_matrix) <- list(stages, stages)
