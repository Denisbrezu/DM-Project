# 🏟️ Football Players Data Scraper

This project scrapes detailed player statistics from domestic football leagues around the world using [FBRef](https://fbref.com). The scraper is built using Selenium and BeautifulSoup, and it compiles data into a structured CSV dataset of over **35,000 players** across multiple tiers and leagues.

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

---

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
