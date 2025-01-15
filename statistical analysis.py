# Import Libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import pearsonr
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from sklearn.cluster import KMeans

# Load Data
file_path = "" 
df = pd.read_excel(file_path)

# Descriptive Statistics
mean_data = df.groupby(["Sensitivity", "ShrinkRate"])[
    ["Stress", "Thrill", "Engagement", "Enjoyment", "Replay"]
].mean().reset_index()

variance_data = df.groupby(["Sensitivity", "ShrinkRate"])[
    ["Stress", "Thrill", "Engagement", "Enjoyment", "Replay"]
].var().reset_index()

# Mean Bar Charts
plt.figure(figsize=(8, 6))
sns.barplot(data=mean_data, x="Sensitivity", y="Thrill", hue="ShrinkRate")
plt.title("Mean Thrill by Sensitivity and Shrink Rate")
plt.xlabel("Sensitivity")
plt.ylabel("Mean Thrill")
plt.legend(title="Shrink Rate")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show()

plt.figure(figsize=(8, 6))
sns.barplot(data=mean_data, x="Sensitivity", y="Engagement", hue="ShrinkRate")
plt.title("Mean Engagement by Sensitivity and Shrink Rate")
plt.xlabel("Sensitivity")
plt.ylabel("Mean Engagement")
plt.legend(title="Shrink Rate")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show()

# Variance Bar Charts
plt.figure(figsize=(8, 6))
sns.barplot(data=variance_data, x="Sensitivity", y="Thrill", hue="ShrinkRate")
plt.title("Variance of Thrill by Sensitivity and Shrink Rate")
plt.xlabel("Sensitivity")
plt.ylabel("Variance of Thrill")
plt.legend(title="Shrink Rate")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show()

plt.figure(figsize=(8, 6))
sns.barplot(data=variance_data, x="Sensitivity", y="Engagement", hue="ShrinkRate")
plt.title("Variance of Engagement by Sensitivity and Shrink Rate")
plt.xlabel("Sensitivity")
plt.ylabel("Variance of Engagement")
plt.legend(title="Shrink Rate")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show()

# Perform ANOVA for Thrill
model_thrill = ols("Thrill ~ C(Sensitivity) * C(ShrinkRate)", data=df).fit()
anova_thrill = anova_lm(model_thrill)
print("ANOVA Results for Thrill:")
print(anova_thrill)

# Perform ANOVA for Engagement
model_engagement = ols("Engagement ~ C(Sensitivity) * C(ShrinkRate)", data=df).fit()
anova_engagement = anova_lm(model_engagement)
print("\nANOVA Results for Engagement:")
print(anova_engagement)

# Correlation Between Stress and Enjoyment
stress_enjoyment_corr, stress_enjoyment_pval = pearsonr(df["Stress"], df["Enjoyment"])
print(f"Correlation Between Stress and Enjoyment: r={stress_enjoyment_corr:.2f}, p={stress_enjoyment_pval:.2e}")

# Clustering Participants
clustering_data = df[["Stress", "Thrill", "Engagement", "Enjoyment", "Replay"]]
kmeans = KMeans(n_clusters=3, random_state=42)
df["Cluster"] = kmeans.fit_predict(clustering_data)

# Visualize Cluster Distribution
plt.figure(figsize=(8, 6))
sns.countplot(data=df, x="Cluster", palette="pastel")
plt.title("Participant Clusters Based on Emotional Responses")
plt.xlabel("Cluster")
plt.ylabel("Count")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show()

# Composite Scoring System
weights = {"Thrill": 0.4, "Engagement": 0.4, "Stress": -0.2}
df["Score"] = (
    weights["Thrill"] * df["Thrill"] +
    weights["Engagement"] * df["Engagement"] +
    weights["Stress"] * df["Stress"]
)

# Mean Scores by Sensitivity and Shrink Rate
mean_scores = df.groupby(["Sensitivity", "ShrinkRate"])["Score"].mean().reset_index()

# Plot Mean Composite Scores
plt.figure(figsize=(8, 6))
sns.barplot(data=mean_scores, x="Sensitivity", y="Score", hue="ShrinkRate", palette="coolwarm")
plt.title("Mean Composite Scores by Sensitivity and Shrink Rate")
plt.xlabel("Sensitivity")
plt.ylabel("Composite Score")
plt.legend(title="Shrink Rate")
plt.grid(axis="y", linestyle="--", alpha=0.7)
plt.show()
