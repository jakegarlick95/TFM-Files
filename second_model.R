data <- read.csv("ordered_data.csv", sep = ",")

training_set <- data[c(1:206), ]

home_train <- training_set[training_set$HomeTeam == 1, ]

for (i in c(1:206)) {
  if (training_set[i, "Shots.on.target.received"] == 0) {
    training_set[i, "Shots.on.target.saved.proportion"] = 100
    }
}

for (i in c(0:102)) {
  training_set[1 + 2*i, "Oppo.Shots.On.Target.Saved.Proportion"] = training_set[2 + 2*i, "Shots.on.target.saved.proportion"]
  training_set[2 + 2*i, "Oppo.Shots.On.Target.Saved.Proportion"] = training_set[1 + 2*i, "Shots.on.target.saved.proportion"]
  }

model <- glm(Goals ~ Expected.goals
                     + Goals.proportion.among.shots
                     + Dangerous.possessions.with.shot
                     + Shots.on.target.from.the.box
                     + Oppo.Shots.On.Target.Saved.Proportion,
             family = "poisson", 
             data = training_set)

summary(model)


library(MASS)
stepAIC(model, direction = "both")
  
