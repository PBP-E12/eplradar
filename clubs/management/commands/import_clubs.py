import csv
import os
import re
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from clubs.models import Club


class Command(BaseCommand):
    help = 'Import data clubs dari CSV dan gambar logo dari static/img/club/'

    def handle(self, *args, **options):
        csv_path = os.path.join(settings.BASE_DIR, 'data', 'clubs.csv')
        logo_dir = os.path.join(settings.BASE_DIR, 'static', 'img', 'club')

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"❌ File {csv_path} tidak ditemukan."))
            return

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                name = row['Club_name'].strip()
                win = int(row['Win_count'])
                draw = int(row['Draw_count'])
                lose = int(row['Lose_count'])

                # --- 🔍 cari logo berdasarkan nama klub ---
                # Ubah nama klub jadi format nama file (spasi → underscore, huruf besar/kecil tidak masalah)
                normalized_name = re.sub(r'\s+', '_', name)
                logo_path = None

                # Coba berbagai kemungkinan ekstensi dan variasi nama
                for ext in ['.png', '.jpg', '.jpeg', '.webp']:
                    candidate = os.path.join(logo_dir, f"{normalized_name}{ext}")
                    if os.path.exists(candidate):
                        logo_path = candidate
                        break
                    # beberapa file bisa juga huruf kecil semua
                    candidate_lower = os.path.join(logo_dir, f"{normalized_name.lower()}{ext}")
                    if os.path.exists(candidate_lower):
                        logo_path = candidate_lower
                        break

                # --- 🧱 Simpan ke database ---
                club, created = Club.objects.get_or_create(
                    nama_klub=name,
                    defaults={
                        'jumlah_win': win,
                        'jumlah_draw': draw,
                        'jumlah_lose': lose,
                    }
                )

                if not created:
                    club.jumlah_win = win
                    club.jumlah_draw = draw
                    club.jumlah_lose = lose

                # Jika ada logo, simpan ke field ImageField
                if logo_path:
                    with open(logo_path, 'rb') as f:
                        club.logo.save(os.path.basename(logo_path), File(f), save=False)
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Logo untuk {name} tidak ditemukan."))

                club.save()

                status = "🟢 Dibuat" if created else "🟡 Diperbarui"
                self.stdout.write(self.style.SUCCESS(f"{status}: {club.nama_klub}"))

        self.stdout.write(self.style.SUCCESS("✅ Import selesai!"))
