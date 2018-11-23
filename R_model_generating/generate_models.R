#########################################################
## This script generates all possible models with 4 nodes and filters out some based on our assumptions
## Saman Amini
#########################################################
## Load libraries and variables from arguments
require(Matrix)
require(gdata)
source("/hpc/dbg_gen/samini/gi_kp_gstf/script/functions_modeling.R")
path <- "/hpc/dbg_gen/samini/gi_kp_gstf/modeling/generated_models"

# Collect arguments
args <- commandArgs(TRUE)

# Default setting when no argument passed
if (length(args) < 1) {
    args <- c("--help")
}

# Help section
if ("--help" %in% args) {
    cat("
        generate_models.R
        script to generate all topologies we want to epistasis simulation.

        Arguments:
        --arg1=row number for the first row from                   -number of row you want to start with
        --arg2=row number for the first row to                     -number of row you want to end with
        \n")
         q(save = "no")
}

row_num_1_from    <- as.numeric(args[1])
row_num_1_to      <- as.numeric(args[2])
print(row_num_1_from)
print(row_num_1_to)

## main script to generate all possible models

# generate all possible combinations per row
all_possibilities <- c(0, 1, 5, -1, -5)
all_rows <- expand.grid(all_possibilities, all_possibilities, all_possibilities, all_possibilities) # 625 is the total number of combinations per row in the matrix

# filter out rows that can have self edges
all_rows_row1 <- all_rows[(which(all_rows[,1] == 0)),]
all_rows_row2 <- all_rows[(which(all_rows[,2] == 0)),]
all_rows_row3 <- all_rows[(which(all_rows[,3] == 0)),]
all_rows_row4 <- all_rows[(which(all_rows[,4] == 0)),]

# filter out models that have more than two incoming edges.
all_rows_row1_1 <- all_rows_row1[rowSums(all_rows_row1 != 0) < 3,]
all_rows_row2_1 <- all_rows_row2[rowSums(all_rows_row2 != 0) < 3,]
all_rows_row3_1 <- all_rows_row3[rowSums(all_rows_row3 != 0) < 3,]
all_rows_row4_1 <- all_rows_row4[rowSums(all_rows_row4 != 0) < 3,]

# convert dataframes to lists
all_rows_row1_list <- split(all_rows_row1_1, seq(nrow(all_rows_row1_1)))
all_rows_row2_list <- split(all_rows_row2_1, seq(nrow(all_rows_row2_1)))
all_rows_row3_list <- split(all_rows_row3_1, seq(nrow(all_rows_row3_1)))
all_rows_row4_list <- split(all_rows_row4_1, seq(nrow(all_rows_row4_1)))

# all combinations of rows
for (i in seq(row_num_1_from, row_num_1_to)) {
    print(i)
    row_comb <- expand.grid(all_rows_row1_list[i], all_rows_row2_list, all_rows_row3_list, all_rows_row4_list)

    row_comb_matrix <- apply(row_comb, 1, function(x) rbind(x$Var1, x$Var2, x$Var3, x$Var4))
    x <- sprintf("number of generated models is %d", length(row_comb_matrix))
    print(x)

    # filter models based on our assumptions
    filtered_models <- assumptions(row_comb_matrix)
    y <- sprintf("number of filtered models is %d", length(filtered_models))
    print(y)

    # specify folder path
    folder_name <- paste("models", "row", i, sep = "_")
    o_path_1 <- paste(path, folder_name, sep = "/")
    if (!file.exists(o_path_1)) dir.create(o_path_1)

    models_from <- 1
    file_counter <- 1

    while(models_from < length(filtered_models)) {
        models_to <- models_from + (5000-1)
        if (models_to > length(filtered_models)) models_to <- length(filtered_models)
        file_name <- paste(paste("/models", file_counter, models_from, models_to, sep = "_"), ".txt", sep = "")
        file_path <- paste(o_path_1, file_name, sep = "")
        sub_filtered_models <- filtered_models[models_from:models_to]
        sub_filtered_models <- lapply(sub_filtered_models, function(x) paste(unmatrix(x, byrow = T), sep = "", collapse = "")) # convert matrices to single lines of char
        invisible(lapply(sub_filtered_models, function(x) write.table(data.frame(x), file_path, append = T, sep = "\t" , row.names = F, col.names = F, quote = F)))

        l <- paste(models_from, models_to, sep = ":")
        print(paste("models", l, "are written to a file", sep = " "))
        models_from <- models_from + 5000
        file_counter <- file_counter + 1
    }
}
