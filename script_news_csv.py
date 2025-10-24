import csv
import os
from django.contrib.auth.models import User
from news.models import News

# Pastikan path CSV benar
base_dir = os.getcwd()
csv_path = os.path.join(base_dir, 'data', 'news.csv')

# Pilih user default
default_user = User.objects.first()  # atau ganti dengan User.objects.get(username='admin')

def safe_strip(value):
    """Kembalikan string kosong jika value None"""
    if value is None:
        return ""
    return str(value).strip()

with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    count = 0
    for row in reader:
        title = safe_strip(row.get('title'))
        content = safe_strip(row.get('content'))
        category = safe_strip(row.get('category'))
        thumbnail = safe_strip(row.get('thumbnail'))
        is_featured = safe_strip(row.get('is_featured')).lower() in ['true', '1', 'yes']

        # Lewati baris kosong total
        if not title and not content:
            continue

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
