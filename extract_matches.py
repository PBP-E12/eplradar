import csv
import os
from datetime import datetime
from matches.models import Match
from clubs.models import Club

# Dapatkan path absolut ke file CSV
base_dir = os.getcwd()
csv_path = os.path.join(base_dir, 'data', 'matches.csv')

# Buka file CSV
with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    count = 0
    for row in reader:
        # Ambil klub home & away dari model Club
        try:
            home_team = Club.objects.get(name=row['Home_Team'])
            away_team = Club.objects.get(name=row['Away_Team'])
        except Club.DoesNotExist:
            print(f"⚠️ Klub tidak ditemukan: {row['Home_Team']} atau {row['Away_Team']}")
            continue

        # Konversi tanggal
        match_date = datetime.strptime(row['Date'], "%d-%m-%Y")

        # Buat objek Match baru
        Match.objects.create(
            home_team=home_team,
            away_team=away_team,
            home_score=int(row['Home_Team_Score']),
            away_score=int(row['Away_Team_Score']),
            week=int(row['Week']),
            match_date=match_date,
            status='finished'  # karena semua pertandingan sudah selesai
        )

        count += 1

print(f"✅ Berhasil import {count} data pertandingan dari {csv_path}")
