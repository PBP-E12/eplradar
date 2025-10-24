import os
import django
import csv

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nama_projectmu.settings')
django.setup()

from clubs.models import Club

# Path ke file CSV (misal disimpan di folder data/)
csv_path = os.path.join(os.getcwd(), 'data', 'clubs.csv')

with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    count = 0

    for row in reader:
        club, created = Club.objects.update_or_create(
            nama_klub=row['Club_name'],
            defaults={
                'jumlah_win': int(row['Win_count']),
                'jumlah_draw': int(row['Draw_count']),
                'jumlah_lose': int(row['Lose_count']),
            }
        )
        count += 1

print(f"✅ Berhasil mengimport {count} klub dari {csv_path}")
