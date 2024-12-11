import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt


def scrape_page(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "lxml-xml")

    players = []
    for entry in soup.select("entry"):
        rank_elem = entry.select_one("rank")
        score_elem = entry.select_one("score")
        # print(rank_elem, score_elem)

        if rank_elem and score_elem:
            score = int(score_elem.get_text(strip=True))
            rank = int(rank_elem.get_text(strip=True))
            # print(rank, score)
            players.append((rank, score))
    return players, soup


def scrape_all_pages(base_url):
    all_players = []

    while base_url is not None:
        print(f"Scraping: {base_url}")
        players, soup = scrape_page(base_url)
        if not players:
            # No more players found, stop scraping
            break
        next_url = soup.find("nextRequestURL")
        if next_url is not None:
            base_url = next_url.get_text(strip=True)
        else:
            base_url=None
        all_players.extend(players)
    return all_players


def group_elo_scores(players):
    elo_buckets = {
        "Stone": 0,
        "Bronze": 0,
        "Silver": 0,
        "Gold": 0,
        "Platinum": 0,
        "Diamond": 0,
        "Masters": 0
    }

    for _, elo in players:
        if 0 <= elo <= 499:
            elo_buckets["Stone"] += 1
        elif 500 <= elo <= 699:
            elo_buckets["Bronze"] += 1
        elif 700 <= elo <= 899:
            elo_buckets["Silver"] += 1
        elif 900 <= elo <= 1099:
            elo_buckets["Gold"] += 1
        elif 1100 <= elo <= 1299:
            elo_buckets["Platinum"] += 1
        elif 1300 <= elo <= 1499:
            elo_buckets["Diamond"] += 1
        else:
            elo_buckets["Masters"] += 1

    return elo_buckets


def plot_distribution(elo_buckets,total_players):
    custom_labels = ['Stone 0-499', 'Bronze 500-699', ' Silver 700-899', 'Gold 900-1099', 'Plat 1100-1299',
                     'Diamond 1300-1499', 'Master 1500+']
    counts = list(elo_buckets.values())
    colors = ['#A9A9A9', '#CD7F32', '#C0C0C0', '#FFD700', '#E5E4E2', '#00BFFF', '#98FB98']
    plt.figure(figsize=(10, 6))
    bars = plt.bar(custom_labels, counts, color=colors, edgecolor='black')
    plt.xticks(rotation=45)
    plt.xlabel('Rank')
    plt.ylabel('Number of Players')
    plt.title('Distribution of Players by Rank')
    for bar in bars.patches:
        height = bar.get_height()
        percentage = (height / total_players) * 100
        plt.text(bar.get_x() + bar.get_width() / 2, height, f'{percentage:.1f}%',
                 ha='center', va='bottom')
    plt.text(.06, .05, 'By Jayson B.', fontsize=10,
             transform=plt.gcf().transFigure)
    plt.subplots_adjust(bottom=0.25)
    plt.show()


def main():
    base_url = "https://steamcommunity.com/stats/2217000/leaderboards/14800950/?xml=1"
    all_players = scrape_all_pages(base_url)
    if not all_players:
        print("No players found.")
        return
    total_players = len(all_players)
    elo_buckets = group_elo_scores(all_players)
    plot_distribution(elo_buckets,total_players)


if __name__ == "__main__":
    main()



