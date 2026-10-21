# Load necessary library
library(ggplot2)
install.packages("extrafont")
library(extrafont)

##############################
# PRACTICAL EXAMPLE
##############################


# Initial Prior belief: Beta(99, 1)
# This implies a strong belief that nearly all lines remain unchanged initially
alpha_prior <- 99
beta_prior <- 1

# Observations from each commit: [unchanged, changed]
# Assume these are counts of unchanged and changed lines respectively
data <- matrix(c(25, 1, 5, 31, 36, 3, 39, 0), ncol = 2, byrow = TRUE)

# Prepare a data frame to track the updates
posterior_data <- data.frame(Commit = integer(), Alpha = double(), Beta = double(), PosteriorMean = double())

# Update beliefs iteratively
for (i in 1:nrow(data)) {
  unchanged <- data[i, 1]
  changed <- data[i, 2]

  # Update alpha and beta based on data
  alpha_post <- alpha_prior + unchanged
  beta_post <- beta_prior + changed

  # Calculate the mean of the posterior
  posterior_mean <- alpha_post / (alpha_post + beta_post)

  # Store the results
  posterior_data <- rbind(posterior_data, data.frame(Commit = i, Alpha = alpha_post, Beta = beta_post, PosteriorMean = posterior_mean))

  # Set the new priors for the next iteration
  alpha_prior <- alpha_post
  beta_prior <- beta_post
}

# Output the results
print(posterior_data)

# Plotting the posterior means
ggplot(posterior_data, aes(x = Commit, y = PosteriorMean)) +
  geom_line() +
  geom_point() +
  scale_x_continuous(breaks = 1:nrow(data)) +
  ggtitle("Evolution of Posterior Mean of Code Unchanged Probability") +
  xlab("Commit Number") +
  ylab("Posterior Mean Probability")

# Histograms of Posterior Distributions
for (i in 1:nrow(posterior_data)) {
  x <- seq(0, 1, length.out = 100)
  y <- dbeta(x, posterior_data$Alpha[i], posterior_data$Beta[i])
  plot(x, y, type = 'l', main = paste("Posterior Distribution after Commit", i),
       xlab = "Probability", ylab = "Density")
}

# Confidence Intervals
ggplot(posterior_data, aes(x = Commit, y = PosteriorMean)) +
  geom_line(size = 1) +  # Increases the size of the line
  geom_point(size = 2) +  # Increases the size of the points
  geom_errorbar(aes(ymin = qbeta(0.025, Alpha, Beta), ymax = qbeta(0.975, Alpha, Beta)),
                width = 0.05, size = 0.7) +  # Increases the size of the confidence intervals
  xlab("Commit Number") +
  ylab("Posterior Mean Probability") +
  theme_minimal() +  # Applies a minimal theme
  theme(
    axis.title.x = element_text(size = 14, family = "Times"),  # Sets font to Times New Roman
    axis.title.y = element_text(size = 14, family = "Times"),  # Sets font to Times New Roman
    axis.text.x = element_text(size = 12, family = "Times"),   # Sets font to Times New Roman
    axis.text.y = element_text(size = 12, family = "Times"),   # Sets font to Times New Roman
    plot.title = element_text(size = 16, family = "Times")     # If you add a title later
  )



# Evolution of parameters
ggplot(posterior_data, aes(x = Commit)) +
  geom_line(aes(y = Alpha, color = "Alpha")) +
  geom_line(aes(y = Beta, color = "Beta")) +
  scale_color_manual(name = "Parameters", values = c("Alpha" = "blue", "Beta" = "red")) +
  ggtitle("Evolution of Beta Distribution Parameters") +
  xlab("Commit Number") +
  ylab("Parameter Value")
