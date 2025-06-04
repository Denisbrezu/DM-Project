import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
import random
import csv
from datetime import datetime


class TransfermarktScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        self.base_url = "https://www.transfermarkt.com"

    def get_soup(self, url):
        """Make request and return BeautifulSoup object."""
        try:
            print(f"Requesting URL: {url}")
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            print(f"Request successful (status code: {response.status_code})")
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}")
            return None

    def extract_player_data(self, player_url):
        """Extract detailed data for a player from their profile page."""
        player_data = {
            'Nume': None,
            'Varsta': None,
            'Inaltime': None,
            'Pozitie': None,
            'Picior': None,
            'Aparitii': None,  # Added for appearances
            'Goluri': None,
            'Assisturi': None,
            'Tara': None,
            'Echipa': None,
            'Market_Value': None,
            'URL': player_url
        }

        print(f"Fetching data from: {player_url}")
        soup = self.get_soup(player_url)
        if not soup:
            return player_data

        try:
            # Print the title of the page for debugging
            title = soup.select_one('title')
            if title:
                print(f"Page title: {title.text.strip()}")

            # Basic info from header - Handle complex player name structure
            name_wrapper = soup.select_one('.data-header__headline-wrapper h1')
            if name_wrapper:
                # For players like Messi with shirt number and formatting
                full_name = ""
                # Get all text nodes and elements inside the h1
                for content in name_wrapper.contents:
                    if content.name == 'span' and 'data-header__shirt-number' in content.get('class', []):
                        # Skip the shirt number
                        continue
                    elif content.name == 'strong':
                        # Get the last name from strong tag
                        full_name += content.text.strip() + " "
                    elif isinstance(content, str):
                        # Get other text parts
                        full_name += content.strip() + " "

                player_data['Nume'] = full_name.strip()

            # If the above method didn't work, try a simpler approach as fallback
            if not player_data['Nume'] or player_data['Nume'] == "":
                title_tag = soup.select_one('title')
                if title_tag:
                    # Titles are often in format "Player Name - Profile"
                    name_parts = title_tag.text.split('-')
                    if len(name_parts) > 0:
                        player_data['Nume'] = name_parts[0].strip()

            # Current team - updated selector based on the HTML structure
            # Try first from the data header
            team_element = soup.select_one('span.data-header__club a')
            if team_element:
                player_data['Echipa'] = team_element.text.strip()

            # If not found, try from info table
            if not player_data['Echipa']:
                current_club_label = soup.select_one(
                    'span.info-table__content--regular:-soup-contains("Current club:")')
                if current_club_label:
                    value_span = current_club_label.find_next_sibling('span', class_='info-table__content--bold')
                    if value_span:
                        player_data['Echipa'] = value_span.text.strip()

            # IMPROVED MARKET VALUE EXTRACTION - Based on the provided HTML snippet
            # Current market value (inside div.current-value or its variants)
            current_value_element = soup.select_one('div.current-value.svelte-gfmgwx')
            if current_value_element:
                # The value is in the text content of the child element
                current_value_text = current_value_element.get_text(strip=True)
                if current_value_text:
                    # Extract the value which should be in a format like "€20.00m"
                    player_data['Market_Value'] = current_value_text

            # If not found with the previous selector, try alternative ones
            if not player_data['Market_Value']:
                alternative_selectors = [
                    'a.link.svelte-gfmgwx',  # Based on the HTML snippet
                    'div.tm-player-market-value-development__current-value',
                    'a.data-header__market-value-wrapper'
                ]

                for selector in alternative_selectors:
                    elements = soup.select(selector)
                    for el in elements:
                        # Check if the element contains a euro value
                        if el.text and '€' in el.text:
                            # Extract euro value using regex
                            euro_match = re.search(r'€(\d+(?:\.\d+)?(?:k|m|bn)?)', el.text)
                            if euro_match:
                                player_data['Market_Value'] = f"€{euro_match.group(1)}"
                                break

            # Info table data - using the updated HTML structure
            info_table = soup.select_one('div.info-table')
            if info_table:
                # Get all label-value pairs in the info table
                label_spans = info_table.select('span.info-table__content--regular')

                for label_span in label_spans:
                    label = label_span.text.strip()
                    # Get the next sibling which should be the value (bold span)
                    value_span = label_span.find_next_sibling('span', class_='info-table__content--bold')
                    if value_span:
                        value = value_span.text.strip()

                        if 'Date of birth/Age:' in label:
                            # Extract age from birthday string
                            age_match = re.search(r'\((\d+)\)', value)
                            if age_match:
                                player_data['Varsta'] = age_match.group(1)

                        elif 'Height:' in label:
                            # Extract height - handle the special &nbsp; character
                            height_text = value.replace('\xa0', ' ')  # Replace non-breaking space
                            # Try different patterns for height extraction
                            height_patterns = [
                                r'(\d+,\d+)m',  # For format like "1,70m"
                                r'(\d+\.\d+)m',  # For format like "1.70m"
                                r'(\d+,\d+)\s*m',  # For format with space like "1,70 m"
                                r'(\d+\.\d+)\s*m',  # For format with space like "1.70 m"
                                r'(\d+)\s*cm'  # For format in cm like "170 cm"
                            ]

                            height_value = None
                            for pattern in height_patterns:
                                match = re.search(pattern, height_text)
                                if match:
                                    height_value = match.group(1)
                                    # Convert to cm if in meters
                                    if 'm' in pattern:
                                        # Handle both comma and dot decimal separators
                                        height_value = height_value.replace(',', '.')
                                        try:
                                            height_cm = round(float(height_value) * 100)
                                            player_data['Inaltime'] = str(height_cm)
                                        except ValueError:
                                            player_data['Inaltime'] = height_value
                                    else:
                                        player_data['Inaltime'] = height_value
                                    break

                            # If no pattern matched, store the raw value
                            if not height_value and height_text:
                                player_data['Inaltime'] = height_text

                        elif 'Position:' in label:
                            player_data['Pozitie'] = value

                        elif 'Foot:' in label:
                            player_data['Picior'] = value

                        elif 'Citizenship:' in label:
                            player_data['Tara'] = value.split(',')[0] if ',' in value else value

                        # Get full name if available in the info table
                        elif 'Name in home country:' in label:
                            if not player_data['Nume'] or len(player_data['Nume']) < len(value):
                                player_data['Nume'] = value

            # Performance data (appearances, goals and assists)
            # First try the performance table in career stats
            player_id_match = re.search(r'/spieler/(\d+)', player_url)
            if player_id_match:
                player_id = player_id_match.group(1)

                # Get player name part for constructing URL
                player_name_part = player_url.split('/profil/')[0].split('/')[-1]

                # Construct performance data URL
                performance_url = f"{self.base_url}/{player_name_part}/leistungsdaten/spieler/{player_id}/plus/0?saison=ges"

                print(f"Fetching performance data from: {performance_url}")
                perf_soup = self.get_soup(performance_url)

                if perf_soup:
                    # Look for the career stats box
                    career_box = perf_soup.select_one('div.box h2.content-box-headline:-soup-contains("Career stats")')
                    if career_box:
                        # Find the table containing the stats - it should be the next table after the headline
                        stats_table = career_box.find_next('table', class_='items')

                        if stats_table:
                            # Get the footer row which contains the totals
                            footer_row = stats_table.select_one('tfoot tr')

                            if footer_row:
                                # Find all cells with class "zentriert"
                                cells = footer_row.select('td.zentriert')

                                # Based on the HTML snippet, appearances are in the 1st zentriert cell (index 0)
                                # goals are in the 2nd zentriert cell (index 1)
                                # and assists are in the 3rd zentriert cell (index 2)
                                if len(cells) > 2:
                                    # Appearances - first zentriert cell
                                    player_data['Aparitii'] = cells[0].get_text(strip=True)
                                    # Goals - second zentriert cell
                                    player_data['Goluri'] = cells[1].get_text(strip=True)
                                    # Assists - third zentriert cell
                                    player_data['Assisturi'] = cells[2].get_text(strip=True)
                                    print(
                                        f"Found appearances: {player_data['Aparitii']}, goals: {player_data['Goluri']}, assists: {player_data['Assisturi']}")

            # If performance data couldn't be fetched, try the original methods as fallback
            if not player_data['Goluri'] or not player_data['Assisturi'] or not player_data['Aparitii']:
                # Performance data (appearances, goals and assists) - Original fallback code
                performance_table = soup.select_one('div.tm-player-performance-table table.items')
                if performance_table:
                    # Find the career total row
                    total_row = soup.select_one('div.tm-player-performance-table tfoot tr')
                    if total_row:
                        columns = total_row.select('td')
                        if len(columns) >= 5:
                            # Assuming appearances are in the 3rd column
                            if not player_data['Aparitii'] and len(columns) > 2:
                                player_data['Aparitii'] = columns[2].text.strip()
                            # Goals are typically in the 4th column
                            if not player_data['Goluri'] and len(columns) > 3:
                                player_data['Goluri'] = columns[3].text.strip()
                            # Assists in 5th column
                            if not player_data['Assisturi'] and len(columns) > 4:
                                player_data['Assisturi'] = columns[4].text.strip()

                # If stats not found in performance table, try the quick stats boxes
                if not player_data['Goluri'] or not player_data['Assisturi'] or not player_data['Aparitii']:
                    # Look for the performance data boxes that often appear at the top of the page
                    performance_boxes = soup.select('div.dataMain div.dataBlockWidth')

                    for box in performance_boxes:
                        header = box.select_one('div.dataHeader')
                        value = box.select_one('div.dataValue')

                        if header and value:
                            if 'Appearances' in header.text and not player_data['Aparitii']:
                                player_data['Aparitii'] = value.text.strip()
                            elif 'Goals' in header.text and not player_data['Goluri']:
                                player_data['Goluri'] = value.text.strip()
                            elif 'Assists' in header.text and not player_data['Assisturi']:
                                player_data['Assisturi'] = value.text.strip()

        except Exception as e:
            print(f"Error extracting player data: {e}")

        return player_data

    def search_player(self, player_name):
        """Search for a player by name and return their profile URL."""
        search_url = f"{self.base_url}/schnellsuche/ergebnis/schnellsuche?query={player_name.replace(' ', '+')}"
        soup = self.get_soup(search_url)

        if not soup:
            return None

        # Find player in search results
        player_links = soup.select('table.items tbody tr td.hauptlink a')
        if not player_links:
            return None

        # Get the first player result
        player_url = player_links[0].get('href')
        if player_url:
            return f"{self.base_url}{player_url}"
        return None

    def get_players_from_team(self, team_url):
        """Extract all player URLs from a team page."""
        # Redirect to the squad/kader page that shows all players
        squad_url = team_url.replace("/startseite/", "/kader/")
        soup = self.get_soup(squad_url)

        if not soup:
            return []

        player_urls = []
        seen_player_ids = set()  # Track player IDs to avoid duplicates

        # Get player links from the squad table
        for row in soup.select('table.items tbody tr'):
            player_link = row.select_one('td.hauptlink a')
            if player_link and player_link.get('href') and '/spieler/' in player_link.get('href'):
                # Extract player ID to avoid duplicates
                player_id_match = re.search(r'/spieler/(\d+)', player_link.get('href'))
                if player_id_match:
                    player_id = player_id_match.group(1)
                    if player_id not in seen_player_ids:
                        seen_player_ids.add(player_id)
                        player_url = f"{self.base_url}{player_link.get('href')}"
                        player_urls.append(player_url)

        print(f"Found {len(player_urls)} unique players in {team_url}")
        return player_urls

    def get_league_teams(self, league_url):
        """Extract all team URLs from a league page."""
        soup = self.get_soup(league_url)
        if not soup:
            return []

        team_urls = []
        for team_link in soup.select('table.items tbody tr td.hauptlink a'):
            if team_link.get('href'):
                team_url = f"{self.base_url}{team_link.get('href')}"
                team_urls.append(team_url)

        return team_urls

    def scrape_league(self, league_url, max_teams=None, max_players=None):
        """Scrape player data from all teams in a league."""
        all_player_data = []

        # Get teams in the league
        team_urls = self.get_league_teams(league_url)
        if max_teams:
            team_urls = team_urls[:max_teams]

        print(f"Found {len(team_urls)} teams")

        for i, team_url in enumerate(team_urls):
            print(f"Processing team {i + 1}/{len(team_urls)}: {team_url}")

            # Add /startseite to team URL if it's not present
            if not team_url.endswith('/startseite'):
                team_url = f"{team_url}/startseite"

            # Get players from the team
            player_urls = self.get_players_from_team(team_url)
            if max_players:
                player_urls = player_urls[:max_players]

            print(f"  Found {len(player_urls)} players")

            for j, player_url in enumerate(player_urls):
                print(f"  Processing player {j + 1}/{len(player_urls)}")
                player_data = self.extract_player_data(player_url)
                all_player_data.append(player_data)

                # Be nice to the server with a short delay
                time.sleep(random.uniform(1.0, 2.0))

        return all_player_data
    def save_to_csv(self, data):
        """Save player data directly to the central PLAYERS_DATA.csv."""
        central_file = "PLAYERS_DATA.csv"
        df = pd.DataFrame(data)

        try:
            # Check if the central file exists
            try:
                existing_df = pd.read_csv(central_file, encoding='utf-8-sig')
                # Append new data to existing file
                combined_df = pd.concat([existing_df, df], ignore_index=True)
                combined_df.to_csv(central_file, index=False, encoding='utf-8-sig')
                print(f"Data appended to {central_file}")
            except FileNotFoundError:
                # If central file doesn't exist, create it
                df.to_csv(central_file, index=False, encoding='utf-8-sig')
                print(f"Created new central file {central_file}")
        except Exception as e:
            print(f"Error updating central file: {e}")
"""
    def save_to_csv(self, data, filename=None):
        Save player data to CSV file and append to PLAYERS_DATA.csv.
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transfermarkt_players_{timestamp}.csv"

        df = pd.DataFrame(data)

        # Save to the requested file
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Data saved to {filename}")

        # Append to the central PLAYERS_DATA.csv file
        central_file = "PLAYERS_DATA.csv"
        try:
            # Check if the central file exists
            try:
                existing_df = pd.read_csv(central_file, encoding='utf-8-sig')
                # Append new data to existing file
                combined_df = pd.concat([existing_df, df], ignore_index=True)
                combined_df.to_csv(central_file, index=False, encoding='utf-8-sig')
                print(f"Data appended to {central_file}")
            except FileNotFoundError:
                # If central file doesn't exist, create it
                df.to_csv(central_file, index=False, encoding='utf-8-sig')
                print(f"Created new central file {central_file}")
        except Exception as e:
            print(f"Error updating central file: {e}")

        return filename

"""
def main():
    scraper = TransfermarktScraper()

    print("Transfermarkt Player Scraper")
    print("---------------------------")
    print("NOTE: All player data will also be appended to PLAYERS_DATA.csv")
    print("Choose an option:")
    print("1. Search and scrape individual player")
    print("2. Scrape all players from a team")
    print("3. Scrape all players from a league")

    choice = input("Enter your choice (1-3): ")

    if choice == "1":
        player_name = input("Enter player name: ")
        player_url = scraper.search_player(player_name)
        if player_url:
            print(f"Found player: {player_url}")
            player_data = scraper.extract_player_data(player_url)
            print("\nData extracted:")
            for key, value in player_data.items():
                if value:  # Only print non-empty values
                    print(f"{key}: {value}")

            save = input("\nSave to CSV? (y/n): ")
            if save.lower() == 'y':
                #filename = f"{player_name.replace(' ', '_')}_data.csv"
                scraper.save_to_csv([player_data])

    elif choice == "2":

        team_name = input("Enter team name (e.g., FC Barcelona, Real Madrid): ")
        search_url = f"{scraper.base_url}/schnellsuche/ergebnis/schnellsuche?query={team_name.replace(' ', '+')}"
        soup = scraper.get_soup(search_url)

        if soup:
            # Print raw HTML for debugging
            print(f"Searching for team: {team_name}")

            # Try different selectors to find team entries
            teams = []

            # Method 1: Look for table rows with club indicator
            team_rows = soup.select('table.items tbody tr')

            for row in team_rows:
                # Try to find club indicator
                img_elem = row.select_one('img[title="Club"]')
                if img_elem:
                    link = row.select_one('td.hauptlink a')
                    if link and "/verein/" in link.get('href', ''):
                        team_url = f"{scraper.base_url}{link.get('href')}"

                        # Ensure URL format is correct
                        if "/startseite/verein/" not in team_url:
                            # Convert any team URL to the startseite format
                            team_id_match = re.search(r'/verein/(\d+)', team_url)
                            if team_id_match:
                                team_id = team_id_match.group(1)
                                team_url = f"{scraper.base_url}/startseite/verein/{team_id}"

                        team_name = link.text.strip()
                        teams.append((team_name, team_url))
                        print(f"{len(teams)}. {team_name}")

            # If no teams found with Method 1, try a more general approach
            if not teams:
                all_links = soup.select('a[href*="/verein/"]')
                for i, link in enumerate(all_links[:10]):
                    if "/verein/" in link.get('href', ''):
                        team_url = f"{scraper.base_url}{link.get('href')}"

                        # Ensure URL has correct format
                        if "/startseite/verein/" not in team_url:
                            team_id_match = re.search(r'/verein/(\d+)', link.get('href'))
                            if team_id_match:
                                team_id = team_id_match.group(1)
                                team_url = f"{scraper.base_url}/startseite/verein/{team_id}"

                        team_name = link.text.strip()
                        # Avoid duplicates
                        if any(name == team_name for name, _ in teams):
                            continue

                        teams.append((team_name, team_url))
                        print(f"{len(teams)}. {team_name}")

            if teams:
                team_choice = int(input("\nSelect team number: ")) - 1
                if 0 <= team_choice < len(teams):
                    team_name, team_url = teams[team_choice]
                    max_players = input("Enter max number of players to scrape (or press Enter for all): ")
                    max_players = int(max_players) if max_players.isdigit() else None

                    print(f"\nScraping {team_name}...")
                    player_urls = scraper.get_players_from_team(team_url)

                    if max_players:
                        player_urls = player_urls[:max_players]

                    all_player_data = []
                    for i, url in enumerate(player_urls):
                        print(f"Processing player {i + 1}/{len(player_urls)}")
                        player_data = scraper.extract_player_data(url)
                        all_player_data.append(player_data)
                        time.sleep(1)  # Be nice to the server

                    #filename = f"{team_name.replace(' ', '_')}_players.csv"
                    scraper.save_to_csv(all_player_data)
            else:
                print("No teams found matching your search.")
        else:
            print("Failed to retrieve search results. Please check your internet connection.")

    elif choice == "3":
        print("\nAvailable leagues:")
        print("1. Premier League (England)")
        print("2. La Liga (Spain)")
        print("3. Serie A (Italy)")
        print("4. Bundesliga (Germany)")
        print("5. Ligue 1 (France)")

        league_choice = input("\nSelect league number (1-5): ")

        league_urls = {
            "1": "https://www.transfermarkt.com/premier-league/startseite/wettbewerb/GB1",
            "2": "https://www.transfermarkt.com/primera-division/startseite/wettbewerb/ES1",
            "3": "https://www.transfermarkt.com/serie-a/startseite/wettbewerb/IT1",
            "4": "https://www.transfermarkt.com/bundesliga/startseite/wettbewerb/L1",
            "5": "https://www.transfermarkt.com/ligue-1/startseite/wettbewerb/FR1"
        }

        if league_choice in league_urls:
            league_url = league_urls[league_choice]
            max_teams = input("Enter max number of teams to scrape (or press Enter for all): ")
            max_teams = int(max_teams) if max_teams.isdigit() else None

            max_players = input("Enter max number of players per team (or press Enter for all): ")
            max_players = int(max_players) if max_players.isdigit() else None

            print("\nScraping league data...")
            all_player_data = scraper.scrape_league(league_url, max_teams, max_players)

            league_name = league_url.split('/')[-3]
            #filename = f"{league_name}_players.csv"
            scraper.save_to_csv(all_player_data)

    else:
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    main()
