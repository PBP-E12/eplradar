import csv
from collections import defaultdict

# Dictionary to store club statistics
club_stats = defaultdict(lambda: {
    'wins': 0,
    'draws': 0,
    'losses': 0
})

# Read the matches CSV file
with open('data/matches.csv', 'r', encoding='utf-8') as file:
    csv_reader = csv.DictReader(file)
    
    for row in csv_reader:
        # Filter only Premier League matches
        if row['League'] == 'Premier League':
            home_team = row['Home_Team']
            away_team = row['Away_Team']
            home_score = int(row['Home_Team_Score'])
            away_score = int(row['Away_Team_Score'])
            
            # Calculate results for home team
            if home_score > away_score:
                club_stats[home_team]['wins'] += 1
                club_stats[away_team]['losses'] += 1
            elif home_score < away_score:
                club_stats[home_team]['losses'] += 1
                club_stats[away_team]['wins'] += 1
            else:  # Draw
                club_stats[home_team]['draws'] += 1
                club_stats[away_team]['draws'] += 1

# Write to clubs.csv
with open('data/clubs.csv', 'w', newline='', encoding='utf-8') as file:
    fieldnames = ['Club_name', 'Win_count', 'Draw_count', 'Lose_count']
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    
    writer.writeheader()
    
    # Sort clubs by points (wins * 3 + draws) in descending order
    sorted_clubs = sorted(
        club_stats.items(),
        key=lambda x: (x[1]['wins'] * 3 + x[1]['draws']),
        reverse=True
    )
    
    for club_name, stats in sorted_clubs:
        writer.writerow({
            'Club_name': club_name,
            'Win_count': stats['wins'],
            'Draw_count': stats['draws'],
            'Lose_count': stats['losses']
        })

print(f"Successfully created clubs.csv with {len(club_stats)} clubs")
print("\nTop 5 clubs by points:")
for i, (club_name, stats) in enumerate(sorted_clubs[:5], 1):
    points = stats['wins'] * 3 + stats['draws']
    print(f"{i}. {club_name}: {stats['wins']}W {stats['draws']}D {stats['losses']}L ({points} pts)")