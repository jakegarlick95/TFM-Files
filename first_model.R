train_set <- read.csv("training_set.csv")
train_set <- train_set[, c(2:15)]
head(train_set)

train_set$AdjustedGoals <- train_set$Goals + 1 - train_set$HomeTeam * 0.192 + (1 - train_set$HomeTeam) * 0.192
train_set$AdjustedShotsOnTargetFor <- train_set$ShotsOnTargetFor + 1 - train_set$HomeTeam * 0.575 + (1 - train_set$HomeTeam) * 0.575
train_set$AdjustedShotsOnTargetAgainst <- train_set$ShotsOnTargetAgainst + 1 + train_set$HomeTeam * 0.575 - (1 - train_set$HomeTeam) * 0.575

train_set$AdjustedShotsFor <- train_set$ShotsFor + 2 - train_set$HomeTeam * 1.6 + (1 - train_set$HomeTeam) * 1.6
train_set$AdjustedShotsAgainst <- train_set$ShotsAgainst + 2 + train_set$HomeTeam * 1.6 - (1 - train_set$HomeTeam) * 1.6

train_set$AdjustedCornersFor <- train_set$CornersFor + 1 - train_set$HomeTeam * 0.69 + (1 - train_set$HomeTeam) * 0.69
train_set$AdjustedCornersAgainst <- train_set$CornersAgainst + 1 + train_set$HomeTeam * 0.69 - (1 - train_set$HomeTeam) * 0.69

train_set$AdjustedFoulsFor <- train_set$FoulsFor + 1 - train_set$HomeTeam * -0.0153 + (1 - train_set$HomeTeam) * -0.0153
train_set$AdjustedFoulsAgainst <- train_set$FoulsAgainst + 1 + train_set$HomeTeam * -0.0153 - (1 - train_set$HomeTeam) * -0.0153

train_set$AdjustedYellowsFor <- train_set$YellowsFor + 1 - train_set$HomeTeam * -0.074 + (1 - train_set$HomeTeam) * -0.074
train_set$AdjustedYellowsAgainst <- train_set$YellowsAgainst + 1 + train_set$HomeTeam * -0.074 - (1 - train_set$HomeTeam) * -0.074

train_set$AdjustedRedsFor <- train_set$RedsFor + 1 - train_set$HomeTeam * -0.0153 + (1 - train_set$HomeTeam) * -0.0153
train_set$AdjustedRedsAgainst <- train_set$RedsAgainst + 1 + train_set$HomeTeam * -0.0153 - (1 - train_set$HomeTeam) * -0.0153

model <- glm(AdjustedGoals ~ AdjustedShotsOnTargetFor + 
                             AdjustedShotsFor +
                             AdjustedCornersFor,
                             data = train_set,
                             family = "poisson"
               )

summary(model)

season1 <- read.csv("18_19.csv")
mean1 <- mean(season1$HST + season1$AST)
goals1 <- mean(season1$FTHG + season1$FTAG)
season2 <- read.csv("20_21.csv")
mean2 <- mean(season2$HST + season2$AST)
goals2 <- mean(season2$FTHG + season2$FTAG)

mean1
goals1

mean2
goals2

