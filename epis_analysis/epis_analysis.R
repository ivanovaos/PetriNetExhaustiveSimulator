# this script takes care of output from exhasutive modeling of models
# Saman Amini

# Collect arguments
args <- commandArgs(TRUE)

# Default setting when no argument passed
if (length(args) < 1) {
    args <- c("--help")
}

# Help section
if ("--help" %in% args) {
    cat("
        modeling_downstream.R
        script to parse through results of simulation and get petrinets that show inversion.
        Arguments:
        --arg1=full path of folder you want to parse           - /hpc/dbg_gen/samini/gi_kp_gstf/modeling/simulation_results/models_row_1
        \n")
         q(save="no")
}

path    <- args[1]
print(path)

##########################################
# functions to do epis analysis.
##########################################

parse_sim_lines <- function(petri_net) {
    model_num <- petri_net[1]
    transitions <- petri_net[2]
    results <- petri_net[3]
    results_parse <- unlist(strsplit(results, split = ":"))

    petri_net_results <- as.data.frame(matrix(nrow = 4, ncol = 2))
    colnames(petri_net_results) <- c("G1", "G2")
    rownames(petri_net_results) <- c("wildtype", "R1", "R2", "R1_R2")

# get number of tokens from output of the simulation
    wildtype <- unlist(strsplit(results_parse[1], split = " "))
    petri_net_results[1,] <- wildtype

    r1_Deletion <- unlist(strsplit(results_parse[3], split = " "))
    petri_net_results[2,] <- r1_Deletion

    r2_Deletion <- unlist(strsplit(results_parse[2], split = " "))
    petri_net_results[3,] <- r2_Deletion

    r1_r2_Deletion <- unlist(strsplit(results_parse[4], split = " "))
    petri_net_results[4,] <- r1_r2_Deletion

    return(petri_net_results)
}

FC_and_GI_calc <- function(petri_net_r) {
    petri_net_r$G1 <- as.numeric(petri_net_r$G1)
    petri_net_r$G2 <- as.numeric(petri_net_r$G2)

    petri_net_r <- petri_net_r + 1
    petri_net_results_FC <- petri_net_r

    for(row in 1:nrow(petri_net_r)) {
        petri_net_results_FC[row,] <- log2(petri_net_r[row,]/petri_net_r["wildtype", ])
    }

    petri_net_results_FC <- petri_net_results_FC[-1,]

    # calculate sgi score for G1 and G2 and get those ones that are significant
    petri_net_results_FC["sgi","G1"] <- petri_net_results_FC["R1_R2","G1"] - (petri_net_results_FC["R1","G1"] + petri_net_results_FC["R2","G1"])

    petri_net_results_FC["sgi","G2"] <- petri_net_results_FC["R1_R2","G2"] - (petri_net_results_FC["R1","G2"] + petri_net_results_FC["R2","G2"])

    return(petri_net_results_FC)
}

direction_of_changes <- function(petri_net_results_FC) {
    deletions <- c("R1", "R2", "R1_R2")
    genes <- c("G1", "G2")

    for (gene in genes) {
        direction_all <- c()
        for (del in deletions) {
            if (petri_net_results_FC[del, gene] < -log2(1.7)) {
                if (del == "R1_R2") {
                    direction <- "DOWN"
                } else {
                    direction <- "down"
                }
            }
            else if (petri_net_results_FC[del, gene] > log2(1.7)) {
                if (del == "R1_R2") {
                    direction <- "UP"
                } else {
                    direction <- "up"
                }
            }
            else {
                if (del == "R1_R2") {
                    direction <- "NO"
                } else {
                    direction <- "no"
                }
            }
            direction_all <- cbind(direction_all, direction)
            direction_all <- paste(direction_all, collapse = ".")
        }
        petri_net_results_FC["direction", gene] <- direction_all
    }

    if (petri_net_results_FC["sgi", "G1"] < 0) petri_net_results_FC["direction", "G1"] <- paste(petri_net_results_FC["direction", "G1"], "negGI", sep = "-")
    if (petri_net_results_FC["sgi", "G1"] > 0) petri_net_results_FC["direction", "G1"] <- paste(petri_net_results_FC["direction", "G1"], "posGI", sep = "-")

    if (petri_net_results_FC["sgi", "G2"] < 0) petri_net_results_FC["direction", "G2"] <- paste(petri_net_results_FC["direction", "G2"], "negGI", sep = "-")
    if (petri_net_results_FC["sgi", "G2"] > 0) petri_net_results_FC["direction", "G2"] <- paste(petri_net_results_FC["direction", "G2"], "posGI", sep = "-")

    return(petri_net_results_FC)
}

filter_misc_patterns <- function(petri_net_results_FC) {

    patterns <- c("buffering",
                  "quantitative buffering",
                  "suppression",
                  "quantitative suppression",
                  "masking",
                  "inversion")

    for (pattern in patterns) {
        for (gene in c("G1", "G2")) {
            double <- as.numeric(petri_net_results_FC["R1_R2", gene])
            single_R1 <- as.numeric(petri_net_results_FC["R1", gene])
            single_R2 <- as.numeric(petri_net_results_FC["R2", gene])

            if ((petri_net_results_FC["epis", gene] == pattern) & (grepl("posGI", petri_net_results_FC["direction", gene]) == TRUE)) {
                if ((double < single_R1) & (double < single_R2)) {
                    petri_net_results_FC["epis", gene] <- "misc_sim"
                    #print(petri_net_results_FC)
                }
            }

            if ((petri_net_results_FC["epis", gene] == pattern) & (grepl("negGI", petri_net_results_FC["direction", gene]) == TRUE)) {
                if ((double > single_R1) & (double > single_R2)) {
                    petri_net_results_FC["epis", gene] <- "misc_sim"
                    #print(petri_net_results_FC)
                }
            }
        }
    }
    return(petri_net_results_FC)
}

##########################################
# main script
##########################################
epis_patterns <- read.delim("/hpc/dbg_gen/samini/repos/exhaustivepetrinetsim/epis_analysis/Transcription-GI-types_v2.txt") # read epistatic patterns

# read and parse files
sim_files <- list.files(path, pattern = "[0-9].txt", full.name = T)

#inv_all <- as.data.frame(matrix(NA, nrow = 0, ncol = 3))
genes <- c("G1", "G2")

for (sim_file in sim_files) {
    f <- sprintf("working now on: %s", sim_file)
    print(f)
    abs_sim_results <- read.delim(sim_file, header = F)
    m_epis_all <- as.data.frame(matrix(NA, nrow = 0, ncol = 3))

    sgi_scores <- vector(mode = "numeric", length = 0)

    for (petri in 1:nrow(abs_sim_results)) {
        #print(petri)
        petri_net <- unlist(strsplit(as.character(abs_sim_results[petri,]), split = ";"))
        model_num <- petri_net[1]
        petri_net_results <- parse_sim_lines(petri_net) # use function to get tokens from sim results
        #print(petri_net_results)
        # calculate FC for G1 and G2 in all deletion mutants.
        petri_net_results_FC <- FC_and_GI_calc(petri_net_results)
        #print(petri_net_results_FC)
        # collect all sgi scores to make a density plot
        sgi_scores <- c(sgi_scores, as.numeric(petri_net_results_FC["sgi",]))

        petri_net_results_FC <- direction_of_changes(petri_net_results_FC)

        for (gene in genes) {
            if (abs(as.numeric(petri_net_results_FC["sgi", gene])) > log2(1.7)) {
                petri_net_results_FC["epis", gene] <- as.character(epis_patterns$description[grepl(petri_net_results_FC["direction", gene], epis_patterns$name)])
            } else {
                petri_net_results_FC["epis", gene] <- 0
            }
        }
        #put the results of different models together
        petri_net_results_FC <- filter_misc_patterns(petri_net_results_FC)
        #print(petri_net_results_FC)
        m_epis <- c(model_num, as.character(petri_net_results_FC["epis",]))
        m_epis <- data.frame(t(m_epis))
        colnames(m_epis) <- c("model", "G1", "G2")
        m_epis_all <- rbind(m_epis_all, m_epis)
    }

    m_epis_all$G1 <- as.character(m_epis_all$G1)
    m_epis_all$G2 <- as.character(m_epis_all$G2)

    # write output into txt files.
    out_file <- paste(strsplit(sim_file, split = "\\.")[[1]][1], "_epis.txt", sep = "")
    write.table(m_epis_all, out_file, row.names = F, quote = F, sep = "\t")
    #print(m_epis_all)
    out_file_sgi_scores <- paste(strsplit(sim_file, split = "\\.")[[1]][1], "_epis_sgi_scores.txt", sep = "")
    sgi_scores <- round(sgi_scores, digits = 3)
    write.table(sgi_scores, out_file_sgi_scores, row.names = F, quote = F, sep = "\t", col.names = F)
    #print(out_file_sgi_scores)
}
