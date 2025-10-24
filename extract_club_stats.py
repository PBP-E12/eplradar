import csv
import os
from datetime import datetime
from matches.models import Match

base_dir = os.getcwd()
csv_path = os.path.join(base_dir, 'data', 'matches.csv')

with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    count = 0
    for row in reader:
        Match.objects.create(
            week=int(row['Week']),
            match_date=datetime.strptime(row['Date'], "%d-%m-%Y"),
            home_team=row['Home_Team'],
            away_team=row['Away_Team'],
            home_score=int(row['Home_Team_Score']),
            away_score=int(row['Away_Team_Score']),
        )
        count += 1

print(f"✅ Berhasil menambahkan {count} pertandingan dari {csv_path}")
