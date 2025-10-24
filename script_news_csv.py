import csv
import os
from django.contrib.auth.models import User
from news.models import News

# Pastikan path CSV benar
base_dir = os.getcwd()
csv_path = os.path.join(base_dir, 'data', 'news.csv')

# Pilih user default (misal admin)
default_user = User.objects.get(username='daniel')

with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    count = 0
    for row in reader:
        # Ambil data dari setiap kolom
        title = row['title'].strip()
        content = row['content'].strip()
        category = row['category'].strip()
        thumbnail = row['thumbnail'].strip()
        is_featured = row['is_featured'].strip().lower() in ['true', '1', 'yes']

        # Buat objek News
        News.objects.create(
            user=default_user,
            title=title,
            content=content,
            category=category,
            thumbnail=thumbnail,
            is_featured=is_featured,
        )
        count += 1

print(f"✅ Berhasil menambahkan {count} berita dari {csv_path}")
