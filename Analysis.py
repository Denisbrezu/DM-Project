import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv("domestic_leagues_by_tier_20250527_230225.csv")

# Set plot style
sns.set(style="whitegrid")

# Filter players with significant playing time (e.g., more than 5 full games)
df_filtered = df[df['Playing Time 90s'] > 5]

# 1. Top Goal Scorers
top_scorers = df_filtered.sort_values('Performance Gls', ascending=False).head(20)
plt.figure(figsize=(12, 8))
sns.barplot(x='Performance Gls', y='Player', data=top_scorers, palette='rocket')
plt.title("Top 20 Goal Scorers")
plt.xlabel("Goals")
plt.ylabel("Player")
plt.tight_layout()
plt.show()

# 2. Top Assist Providers
top_assists = df_filtered.dropna(subset=['Performance Ast'])
top_assists = top_assists.sort_values('Performance Ast', ascending=False).head(20)
plt.figure(figsize=(12, 8))
sns.barplot(x='Performance Ast', y='Player', data=top_assists, palette='crest')
plt.title("Top 20 Assist Providers")
plt.xlabel("Assists")
plt.ylabel("Player")
plt.tight_layout()
plt.show()

# 3. xG vs Actual Goals (Top scorers with xG data)
xg_data = df_filtered.dropna(subset=['Expected xG'])
top_xg = xg_data.sort_values('Performance Gls', ascending=False).head(30)
plt.figure(figsize=(12, 8))
sns.scatterplot(x='Expected xG', y='Performance Gls', hue='Player', data=top_xg, palette='tab20', legend=False)
plt.plot([0, top_xg['Expected xG'].max()], [0, top_xg['Performance Gls'].max()], ls='--', c='gray')
plt.title("Expected Goals (xG) vs Actual Goals")
plt.xlabel("xG")
plt.ylabel("Goals")
plt.tight_layout()
plt.show()

# 4. Distribution of Goals per 90 Minutes
plt.figure(figsize=(10, 6))
sns.histplot(df_filtered['Per 90 Minutes Gls'], bins=30, kde=True, color='darkblue')
plt.title("Distribution of Goals per 90 Minutes")
plt.xlabel("Goals per 90 Minutes")
plt.ylabel("Player Count")
plt.tight_layout()
plt.show()

# 5. Team Average Performance (G+A per 90)
df_filtered['G+A/90'] = df_filtered['Per 90 Minutes G+A']
team_avg = df_filtered.groupby('Team')['G+A/90'].mean().sort_values(ascending=False).head(15)
plt.figure(figsize=(12, 8))
sns.barplot(x=team_avg.values, y=team_avg.index, palette='mako')
plt.title("Top 15 Teams by Average G+A per 90 Minutes")
plt.xlabel("Average G+A per 90")
plt.ylabel("Team")
plt.tight_layout()
plt.show()

# 6. Tier Comparison
tier_avg = df_filtered.groupby('Tier')[['Per 90 Minutes Gls', 'Per 90 Minutes Ast']].mean().reset_index()
tier_avg = pd.melt(tier_avg, id_vars='Tier', var_name='Metric', value_name='Value')
plt.figure(figsize=(10, 6))
sns.barplot(x='Tier', y='Value', hue='Metric', data=tier_avg, palette='viridis')
plt.title("Average Goals and Assists per 90 by Tier")
plt.ylabel("Average per 90 Minutes")
plt.xlabel("Tier")
plt.tight_layout()
plt.show()
