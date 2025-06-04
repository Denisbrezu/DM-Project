# 🏟️ Football Players Data Scraper

This project scrapes detailed player statistics from domestic football leagues around the world using [FBRef](https://fbref.com). The scraper is built using Selenium and BeautifulSoup, and it compiles data into a structured CSV dataset of over **35,000 players** across multiple tiers and leagues.

The date of the dataset is 28.05.2025.

Team Members: Agoci Roberto, Bledea Christian, Brezovan Denis, Manolache Alexandru.

---

## 📌 Features

- Scrapes **Tier 1, Tier 2, and Tier 3** domestic football leagues.
- Extracts player-level stats including **names**, **nationalities**, **teams**, and **performance metrics**.
- Uses a **headless Chrome driver** with custom configurations to avoid detection.
- Outputs data as a clean, UTF-8 encoded CSV file (`Football_Players_Data.csv`).
- Gracefully handles partial failures and provides detailed summary statistics.

---

## 🛠️ Technologies Used

- `Python 3.13+`
- `Selenium` for browser automation
- `BeautifulSoup4` for HTML parsing
- `Pandas` for data manipulation
- `FBRef` as the primary data source

---

## 🚀 Getting Started

### Requirements

- Chrome & compatible ChromeDriver installed
- Python 3.10+ installed
- Dependencies:
  ```bash
  pip install pandas selenium beautifulsoup4
  ```

### Running the Scraper

```bash
python Scrapper.py
```

This will:

1. Discover all relevant domestic football leagues by tier.
2. Scrape player-level data from each league.
3. Save the compiled dataset to `Football_Players_Data.csv`.

---

## 📁 Output

The final CSV file contains over **35,000 records** with the following key columns:

- `League`
- `Tier`
- `Player`
- `Team`
- `Nationality`
- `... + performance stats`

---

## ⚠️ Challenges Faced

### 1. 🌐 Request Limiting & Anti-Bot Measures

TransfrMarkt, Sofascore, Flashscore, Fbref and basically any other football statistics website implements request throttling and basic bot detection. To mitigate this, weneeded to find a website that structures well the statistics in order to do as few as possible requests and also:

- A **headless browser** setup was used instead of direct HTTP requests.
- **Custom user-agent headers** and **delays** (`time.sleep`) between requests were introduced.

### 2. 🧱 Library Compatibility Issues

The `soccerdata` Python library was initially considered, but:

- **Incompatibility with Python 3.12+**
- Frequent **breaking changes** in FBRef’s structure made it unreliable
- Scraper was fully custom-built instead

### 3. 📉 Inconsistent or Sparse Data

Some leagues had:

- **Minimal player data**
- **Missing tables**
- **Unstructured layouts**

To address this:

- The scraper skips leagues without valid player stats.
- Validation and cleaning steps ensure the output remains consistent.
- We added a failed, but a good version of a TransfrMarkt scraper that works just fine, but doesn't support many requests

---

### 4. Failed Scraper

As we began to tackle this project, the first site we wanted to get data from was transfermarkt.com, probably the most well known site for finding the stats and transfer value of players. We then, encountered an issue, that would persist across all the other sites that offer signigficant amounts of player data. The issue was that we were limited to a number of requests/a period of time, a measure included by the developers of those sites for discouraging and making scraping incredibly slow. The alternative that they offer, being an API that gives you access to their data, but for a reoccuring cost.

We decided however to keep the failed version of the scraper in this repository, as it represents a fair amount of our work, and it can showcase some of the things that we learned, so , below you will find a short description of that scraper.

# Transfermarkt Player Scraper
A Python web scraper that extracts comprehensive player data from Transfermarkt.com, the world's leading football transfer database.

# Features

 - Individual Player Search: Search and scrape detailed data for specific players
 - Team-based Scraping: Extract data for all players from a specific football club
 - League-wide Scraping: Scrape all players from major European leagues (Premier League, La Liga, Serie A, Bundesliga, Ligue 1)

# Data Extracted
For each player, the scraper collects:

 - Personal Info: Name, age, height, nationality
 - Playing Details: Position, preferred foot, current team
 - Performance Stats: Career appearances, goals, assists
 - Market Value: Current transfer market valuation
 - Profile URL: Direct link to player's Transfermarkt page

# Usage
Run the script and choose from three options:

1. Search for individual players by name
2. Scrape all players from a specific team
3. Scrape all players from an entire league

All data is automatically saved to CSV format and consolidated into a central PLAYERS_DATA.csv file.
# Requirements

Python 3.x
Required packages: requests, beautifulsoup4, pandas
Respectful usage with built-in delays to avoid overloading the server

# Technical Implementation
# Architecture
The scraper is built around a TransfermarktScraper class that handles all web requests, HTML parsing, and data extraction with the following key components:
# Web Scraping Strategy

 - Request Headers: Implements realistic browser headers to avoid detection
 - Rate Limiting: Built-in random delays (1-2 seconds) between requests to prevent server overload
 - Error Handling: Comprehensive exception handling for network failures and parsing errors

# Data Extraction Methods
1. HTML Parsing

 - Uses BeautifulSoup4 for robust HTML parsing
 - Multiple CSS selector strategies for reliable data extraction
 - Handles complex nested HTML structures and dynamic content

2. Player Data Extraction

 - Profile Parsing: Extracts basic info from player profile pages using multiple selector fallbacks
 - Performance Data: Fetches career statistics from dedicated performance pages (/leistungsdaten/)
 - Market Value: Implements advanced regex patterns to extract monetary values in various formats (€20.00m, €500k, etc.)

3. URL Construction & Navigation

 - Dynamic URL Building: Constructs performance data URLs using extracted player IDs
 - Search Functionality: Implements Transfermarkt's search API for player/team discovery
 - League Navigation: Automated traversal of league → team → player hierarchies

# Data Processing Features

 - Duplicate Prevention: Uses player ID tracking to avoid duplicate entries
 - Data Normalization: Converts heights to consistent units (cm), standardizes text formatting
 - Flexible Export: Supports both individual CSV files and consolidated data storage

# Robustness Features

 - Multiple Selector Strategies: Implements fallback selectors for different page layouts
 - Text Cleaning: Handles special characters, non-breaking spaces, and formatting inconsistencies
 - Partial Data Recovery: Continues scraping even when some data fields are unavailable





## 📊 Summary Insights (from sample run)

- **Players scraped**: 35,000+
- **Successful leagues**: ~60+
- **Top nationalities**: 🇫🇷 🇧🇷 🇪🇸 🇩🇪 🇦🇷
- **Tiers**:
  - Tier 1: 🟢 Most data-rich
  - Tier 2: 🟡 Moderate coverage
  - Tier 3: 🔴 Sparse data, often skipped

---

## 📎 Example Output Snippet

| League         | Tier   | Player          | Team            | Nationality |
| -------------- | ------ | --------------- | --------------- | ----------- |
| Premier League | Tier 1 | Erling Haaland  | Manchester City | NOR         |
| La Liga        | Tier 1 | Jude Bellingham | Real Madrid     | ENG         |
| Serie B        | Tier 2 | Mario Balotelli | Brescia         | ITA         |

---

## Legend

| **Column**                  | **Description**                                          |
| --------------------------- | -------------------------------------------------------- |
| **League**                  | Competition the player is in (e.g., Premier League).     |
| **Tier**                    | Division level of the league.                            |
| **Player**                  | Name of the player.                                      |
| **Nationality**             | Player's nationality.                                    |
| **Team**                    | Club or national team name.                              |
| **Playing Time MP**         | Matches played.                                          |
| **Playing Time Starts**     | Matches started.                                         |
| **Playing Time Min**        | Total minutes played.                                    |
| **Playing Time 90s**        | Minutes played divided by 90 (useful for per 90 stats).  |
| **Performance Gls**         | Goals scored.                                            |
| **Performance Ast**         | Assists.                                                 |
| **Performance G+A**         | Goals + Assists.                                         |
| **Performance G-PK**        | Non-penalty goals.                                       |
| **Performance PK**          | Penalty goals scored.                                    |
| **Performance PKatt**       | Penalties attempted.                                     |
| **Performance CrdY**        | Yellow cards.                                            |
| **Performance CrdR**        | Red cards.                                               |
| **Expected xG**             | Expected goals — quality of shots.                       |
| **Expected npxG**           | Non-penalty expected goals.                              |
| **Expected xAG**            | Expected assisted goals — based on shot-creating passes. |
| **Expected npxG+xAG**       | Combined non-penalty xG and xAG.                         |
| **Progression PrgC**        | Progressive carries — runs moving ball toward goal.      |
| **Progression PrgP**        | Progressive passes — forward passes advancing the ball.  |
| **Progression PrgR**        | Progressive passes received.                             |
| **Per 90 Minutes Gls**      | Goals per 90 minutes.                                    |
| **Per 90 Minutes Ast**      | Assists per 90 minutes.                                  |
| **Per 90 Minutes G+A**      | Goals + Assists per 90.                                  |
| **Per 90 Minutes G-PK**     | Non-penalty goals per 90.                                |
| **Per 90 Minutes G+A-PK**   | Non-penalty goals + assists per 90.                      |
| **Per 90 Minutes xG**       | Expected goals per 90.                                   |
| **Per 90 Minutes xAG**      | Expected assisted goals per 90.                          |
| **Per 90 Minutes xG+xAG**   | Total expected goals + assists per 90.                   |
| **Per 90 Minutes npxG**     | Non-penalty expected goals per 90.                       |
| **Per 90 Minutes npxG+xAG** | Combined non-penalty xG and xAG per 90.                  |

| **Term**                          | **Meaning**                                                                                                                                                     |
| --------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **xG (Expected Goals)**           | Measures the quality of a shot by estimating the probability it results in a goal (0–1 scale). Based on factors like shot angle, distance, body part used, etc. |
| **npxG (Non-penalty xG)**         | Expected goals *excluding* penalty kicks. Focuses on open play and non-penalty situations.                                                                      |
| **xAG (Expected Assisted Goals)** | Expected value of a pass leading to a shot. Measures the chance that a pass results in a goal. Similar to xG, but for the assist.                               |
| **npxG+xAG**                      | Combines non-penalty xG and xAG for a fuller picture of contribution in open play.                                                                              |
| **xG+xAG**                        | Combines total expected goals and expected assisted goals — both shooting and passing threat.                                                                   |


## 📌 Next Steps & Improvements

- 🗓️ Schedule scraper as a cron job for **weekly updates**
- 📊 Add **player performance visualizations** using matplotlib or seaborn
- 🌍 Expand coverage to **international tournaments** with filters

---

## 📊 Data Analysis with `Analysis.py`

To explore insights from the dataset, an additional script `Analysis.py` is provided.

### Key Analyses Performed

1. **Top Goal Scorers** – Identifies the top 20 players with the most goals.
2. **Top Assist Providers** – Highlights the top 20 players based on assists.
3. **xG vs Actual Goals** – Visualizes overperformers and underperformers using xG (expected goals).
4. **Goals per 90 Minutes Distribution** – Shows how frequently players score per 90 minutes.
5. **Team Performance** – Ranks teams by average G+A (goals + assists) per 90 minutes.
6. **Tier Comparison** – Compares average goals and assists per 90 across Tier 1, 2, and 3 leagues.

### Running the Analysis

Make sure your CSV is named appropriately (or update the filename in the script):

```bash
python Analysis.py
```

This will generate a series of plots for visual analysis using `matplotlib` and `seaborn`.

## 📄 License

This project is for educational and research purposes only. Respect the terms and conditions of FBRef and any data provider.
