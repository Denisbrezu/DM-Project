import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import os
import re
from datetime import datetime
from urllib.parse import urljoin, urlparse


def setup_driver():
    """Set up and return a configured Chrome driver"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--no-first-run")
    options.add_argument("--disable-default-apps")
    options.add_argument("--disable-infobars")
    options.add_argument("--lang=en-US,en")
    options.add_argument("--accept-lang=en-US,en")
    options.add_argument("--accept-charset=utf-8")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")

    # Set encoding preferences
    prefs = {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_settings.popups": 0,
        "profile.managed_default_content_settings.images": 2,
        "intl.accept_languages": "en-US,en"
    }
    options.add_experimental_option("prefs", prefs)

    return webdriver.Chrome(options=options)


def discover_domestic_leagues_by_tier():
    """
    Discover domestic leagues from FBRef's competitions page, specifically from the
    1st Tier, 2nd Tier, and 3rd Tier and Lower sections
    """
    print("Discovering domestic leagues from FBRef competitions page...")

    base_url = "https://fbref.com"
    competitions_url = "https://fbref.com/en/comps/"

    driver = setup_driver()
    leagues_by_tier = {
        'Tier 1': {},
        'Tier 2': {},
        'Tier 3': {}
    }

    try:
        driver.get(competitions_url)
        time.sleep(3)

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find all tables on the page
        tables = soup.find_all('table')

        # Look for tables that contain domestic league information
        # We'll identify them by looking for preceding headers or context

        current_tier = None

        # Find all elements and process them in order to maintain context
        all_elements = soup.find_all(['h2', 'h3', 'h4', 'table'])

        for element in all_elements:
            if element.name in ['h2', 'h3', 'h4']:
                header_text = element.get_text().strip().lower()

                # Identify which tier section we're in
                if 'domestic leagues - 1st tier' in header_text or 'domestic leagues-1st tier' in header_text:
                    current_tier = 'Tier 1'
                    print(f"Found Tier 1 section: {element.get_text().strip()}")
                elif 'domestic leagues - 2nd tier' in header_text or 'domestic leagues-2nd tier' in header_text:
                    current_tier = 'Tier 2'
                    print(f"Found Tier 2 section: {element.get_text().strip()}")
                elif ('domestic leagues - 3rd tier' in header_text or
                      'domestic leagues-3rd tier' in header_text or
                      '3rd tier and lower' in header_text):
                    current_tier = 'Tier 3'
                    print(f"Found Tier 3 section: {element.get_text().strip()}")
                elif ('international' in header_text or
                      'continental' in header_text or
                      'women' in header_text or
                      'youth' in header_text):
                    current_tier = None  # Reset when we hit non-domestic sections

            elif element.name == 'table' and current_tier:
                # Process this table as it belongs to a domestic tier
                print(f"Processing table in {current_tier} section")

                links = element.find_all('a', href=True)

                for link in links:
                    href = link.get('href', '')
                    text = link.text.strip()

                    # Look for competition links
                    if '/comps/' in href and text and len(text) > 3:
                        # Extract competition ID
                        comp_match = re.search(r'/comps/(\d+)/', href)
                        if comp_match:
                            comp_id = comp_match.group(1)

                            # Skip year-only entries (like "2024-2025", "2025", etc.)
                            if re.match(r'^\d{4}(-\d{4})?$', text):
                                continue

                            # Skip single years
                            if re.match(r'^\d{4}$', text):
                                continue

                            # Skip cup competitions and tournaments
                            if any(cup_keyword in text.lower() for cup_keyword in [
                                'cup', 'copa', 'coupe', 'pokal', 'trophy', 'trophée', 'shield',
                                'supercup', 'qualification', 'playoff', 'championship playoff'
                            ]):
                                continue

                            # Skip clearly international competitions
                            if any(exclude in text.lower() for exclude in [
                                'champions league', 'europa league', 'conference league',
                                'world cup', 'euro', 'copa america', 'nations league',
                                'uefa', 'fifa', 'international', 'olympics', 'libertadores',
                                'concacaf', 'afc', 'caf', 'cup of nations'
                            ]):
                                continue

                            # Only include if it looks like a proper league name
                            # Must contain actual words, not just numbers/symbols
                            if (len([word for word in text.split() if word.isalpha()]) >= 1 and
                                    not text.lower().startswith('matchday') and
                                    not text.lower().startswith('round')):
                                # Construct stats URL
                                league_name = text.strip()
                                stats_url = f"{base_url}/en/comps/{comp_id}/stats/{league_name.replace(' ', '-')}-Stats"

                                leagues_by_tier[current_tier][league_name] = {
                                    'url': stats_url,
                                    'comp_id': comp_id
                                }

                                print(f"  Added to {current_tier}: {league_name}")

        driver.quit()

        # Clean up and remove duplicates based on competition ID
        for tier in leagues_by_tier:
            cleaned_leagues = {}
            seen_comp_ids = set()

            for name, info in leagues_by_tier[tier].items():
                comp_id = info['comp_id']
                if comp_id not in seen_comp_ids:
                    seen_comp_ids.add(comp_id)
                    cleaned_leagues[name] = info['url']

            leagues_by_tier[tier] = cleaned_leagues

        # Print summary
        total_leagues = sum(len(leagues_by_tier[tier]) for tier in leagues_by_tier)
        print(f"\nDiscovered {total_leagues} domestic leagues across all tiers")

        for tier in ['Tier 1', 'Tier 2', 'Tier 3']:
            count = len(leagues_by_tier[tier])
            print(f"{tier}: {count} leagues")

            if count > 0:
                print(f"  Examples: {list(leagues_by_tier[tier].keys())[:3]}")

        return leagues_by_tier

    except Exception as e:
        print(f"Error discovering domestic leagues: {str(e)}")
        try:
            driver.quit()
        except:
            pass
        return {'Tier 1': {}, 'Tier 2': {}, 'Tier 3': {}}


def scrape_fbref_players_selenium(league_url, league_name):
    """
    Scrape player data from FBRef for a specific league
    """
    print(f"Starting scrape for {league_name}...")

    driver = setup_driver()

    try:
        driver.get(league_url)
        time.sleep(5)  # Wait for page to fully load

        # Get page source - no need for explicit encoding since Selenium handles it
        page_source = driver.page_source
        # Create BeautifulSoup object without specifying from_encoding
        soup = BeautifulSoup(page_source, 'html.parser')
        driver.quit()

        # Find the main player stats table
        table = None
        for t in soup.find_all('table'):
            tid = t.get('id', '')
            if 'stats_players' in tid or 'stats_standard' in tid:
                table = t
                break

        if table is None:
            print(f"No suitable stats table found for {league_name}")
            return None

        # Read table with pandas first using StringIO to avoid deprecation warning
        from io import StringIO
        df = pd.read_html(StringIO(str(table)))[0]

        # Remove any duplicate/header rows within the data
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [' '.join(col).strip() for col in df.columns.values]

        # Filter out rows that contain header text or are duplicates of column names
        # This removes the repeated header rows that appear in the middle of tables
        header_mask = df.apply(lambda row: row.astype(str).str.contains('Player|Rk|Age|Nation').any(), axis=1)
        df = df[~header_mask].reset_index(drop=True)

        # Extract player names and nationalities manually - PRESERVE ORIGINAL TEXT
        player_names = []
        nationalities = []
        team_names = []
        rows = table.find('tbody').find_all('tr')

        # Filter out header rows and empty rows
        data_rows = []
        for row in rows:
            # Skip if it's a header row or has thead class
            if (row.get('class') and any('thead' in str(cls) for cls in row.get('class'))) or \
                    row.find('th', {'data-stat': 'player'}):
                continue

            # Skip if no player data
            player_cell = row.find('td', {'data-stat': 'player'})
            if not player_cell:
                continue

            # Skip if this is a repeated header row (contains "Player" text)
            if player_cell.text.strip() == 'Player':
                continue

            data_rows.append(row)

        print(f"Found {len(data_rows)} data rows, DataFrame has {len(df)} rows")

        for row in data_rows:
            # Get player name from the <a> inside data-stat="player" - PRESERVE ORIGINAL
            player_cell = row.find('td', {'data-stat': 'player'})
            player_name = 'N/A'
            if player_cell:
                a_tag = player_cell.find('a')
                if a_tag:
                    # Use string content directly to preserve encoding
                    player_name = str(a_tag.string) if a_tag.string else a_tag.get_text(strip=False)
                else:
                    # Use string content directly to preserve encoding
                    text_content = player_cell.get_text(strip=False)
                    player_name = text_content if text_content else 'N/A'
            player_names.append(player_name)

            # Get nationality - PRESERVE ORIGINAL TEXT
            nationality_cell = row.find('td', {'data-stat': 'nationality'})
            nationality = 'N/A'
            if nationality_cell:
                # Look for the country code in nested spans
                spans = nationality_cell.find_all('span')
                if len(spans) >= 2:
                    # Second span usually contains the country code - preserve original
                    nationality = str(spans[1].string) if spans[1].string else spans[1].get_text(strip=False)
                else:
                    # Fallback to full text - preserve original
                    nationality = nationality_cell.get_text(strip=False)
            nationalities.append(nationality)

            # Get team name - PRESERVE ORIGINAL TEXT
            team_cell = row.find('td', {'data-stat': 'team'})
            team_name = 'N/A'
            if team_cell:
                a_tag = team_cell.find('a')
                if a_tag:
                    # Use string content directly to preserve encoding
                    team_name = str(a_tag.string) if a_tag.string else a_tag.get_text(strip=False)
                else:
                    # Use string content directly to preserve encoding
                    text_content = team_cell.get_text(strip=False)
                    team_name = text_content if text_content else 'N/A'
            team_names.append(team_name)

        # Adjust DataFrame length to match extracted data
        if len(player_names) != len(df):
            print(f"Adjusting DataFrame from {len(df)} to {len(player_names)} rows")
            if len(player_names) < len(df):
                df = df.head(len(player_names))
            else:
                # This shouldn't happen, but handle it gracefully
                player_names = player_names[:len(df)]
                nationalities = nationalities[:len(df)]
                team_names = team_names[:len(df)]

        # Ensure length matches before inserting
        if len(player_names) == len(df) and len(nationalities) == len(df):
            df.insert(0, 'Team', team_names)
            df.insert(0, 'Nationality', nationalities)
            df.insert(0, 'Player', player_names)
            df.insert(0, 'League', league_name)  # Add league identifier
        else:
            print(f"Warning: Still have row count mismatch for {league_name}")
            print(f"Players: {len(player_names)}, Nationalities: {len(nationalities)}, DataFrame: {len(df)}")
            return None

        # REMOVE THE LAST COLUMN
        if len(df.columns) > 0:
            df = df.iloc[:, :-1]  # Remove the last column
            print(f"Removed last column. DataFrame now has {len(df.columns)} columns")

        return df

    except Exception as e:
        print(f"Error scraping {league_name}: {str(e)}")
        try:
            driver.quit()
        except:
            pass
        return None


def main():
    """
    Main function to discover and scrape domestic football leagues from specific tier sections
    """
    print("🏆 FBREF DOMESTIC LEAGUES SCRAPER (TIER-SPECIFIC)")
    print("=" * 60)

    # Step 1: Discover domestic leagues by tier from specific sections
    leagues_by_tier = discover_domestic_leagues_by_tier()

    total_leagues = sum(len(leagues_by_tier[tier]) for tier in leagues_by_tier)
    if total_leagues == 0:
        print("❌ No domestic leagues discovered. Exiting.")
        return

    # Print detailed breakdown
    print("\n📊 Discovered leagues by tier:")
    for tier in ['Tier 1', 'Tier 2', 'Tier 3']:
        count = len(leagues_by_tier[tier])
        print(f"\n{tier}: {count} leagues")
        if count > 0:
            for i, league_name in enumerate(sorted(leagues_by_tier[tier].keys()), 1):
                print(f"  {i:2d}. {league_name}")

    # Step 2: Scrape all discovered leagues
    all_leagues_data = []
    successful_scrapes = 0
    failed_scrapes = []

    print(f"\n🚀 Starting to scrape {total_leagues} domestic football leagues...")
    print("=" * 60)

    league_counter = 1
    for tier in ['Tier 1', 'Tier 2', 'Tier 3']:
        tier_leagues = leagues_by_tier[tier]

        if len(tier_leagues) > 0:
            print(f"\n🏆 Processing {tier} leagues ({len(tier_leagues)} leagues)...")

            for league_name, league_url in tier_leagues.items():
                print(f"\n[{league_counter}/{total_leagues}] Processing {league_name} ({tier})...")

                # Scrape league data
                league_data = scrape_fbref_players_selenium(league_url, league_name)

                if league_data is not None:
                    # Clean up column names if they're MultiIndex
                    if isinstance(league_data.columns, pd.MultiIndex):
                        league_data.columns = [' '.join(col).strip() for col in league_data.columns.values]

                    # Remove unnamed columns
                    league_data = league_data.loc[:, ~league_data.columns.str.contains('^Unnamed')]

                    # Add tier information
                    league_data.insert(1, 'Tier', tier)

                    # Add to combined dataset
                    all_leagues_data.append(league_data)
                    successful_scrapes += 1

                    print(f"✅ Successfully scraped {len(league_data)} players from {league_name}")
                    print(f"   DataFrame has {len(league_data.columns)} columns")
                else:
                    failed_scrapes.append(f"{league_name} ({tier})")
                    print(f"❌ Failed to scrape {league_name}")

                league_counter += 1

                # Add delay between requests to be respectful
                if league_counter <= total_leagues:
                    print("   Waiting 3 seconds before next request...")
                    time.sleep(3)

    # Step 3: Save results
    if all_leagues_data:
        combined_df = pd.concat(all_leagues_data, ignore_index=True)

        # Generate timestamp for filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        combined_filename = f"Football_Players_Data.csv"

        # Save with proper UTF-8 encoding to preserve special characters
        combined_df.to_csv(combined_filename, index=False, encoding='utf-8-sig')

        print("\n" + "=" * 60)
        print("🎉 SCRAPING SUMMARY")
        print("=" * 60)
        print(f"✅ Successful scrapes: {successful_scrapes}/{total_leagues}")
        print(f"📊 Total players scraped: {len(combined_df):,}")
        print(f"📋 Total columns in dataset: {len(combined_df.columns)}")
        print(f"💾 Combined dataset saved to: {combined_filename}")

        if failed_scrapes:
            print(f"❌ Failed leagues ({len(failed_scrapes)}): {', '.join(failed_scrapes[:10])}")
            if len(failed_scrapes) > 10:
                print(f"    ... and {len(failed_scrapes) - 10} more")

        # Display sample of combined data
        print(f"\n📋 Sample of combined dataset:")
        sample_cols = ['League', 'Tier', 'Player', 'Team', 'Nationality']
        available_cols = [col for col in sample_cols if col in combined_df.columns]
        print(combined_df[available_cols].head(15).to_string(index=False))

        # Show all column names
        print(f"\n📝 All columns in the dataset:")
        for i, col in enumerate(combined_df.columns, 1):
            print(f"  {i:2d}. {col}")

        # Tier distribution
        print(f"\n🏆 Players per tier:")
        if 'Tier' in combined_df.columns:
            tier_counts = combined_df['Tier'].value_counts()
            for tier in ['Tier 1', 'Tier 2', 'Tier 3']:
                if tier in tier_counts:
                    print(f"  {tier}: {tier_counts[tier]:,} players")

        # League distribution (top 15)
        print(f"\n🏟️  Top leagues by player count:")
        league_counts = combined_df['League'].value_counts().head(15)
        for league, count in league_counts.items():
            print(f"  {league}: {count} players")

        # Country distribution (top 10)
        if 'Nationality' in combined_df.columns:
            print(f"\n🌍 Top nationalities:")
            nationality_counts = combined_df['Nationality'].value_counts().head(10)
            for nationality, count in nationality_counts.items():
                print(f"  {nationality}: {count} players")

    else:
        print("\n❌ No data was successfully scraped from any league.")


if __name__ == "__main__":
    main()
