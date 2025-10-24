import csv
import os
import re
import shutil
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from players.models import Player
from clubs.models import Club


class Command(BaseCommand):
    help = 'Import data pemain dari CSV dan salin foto dari static/img/player/ ke media/player_thumbnails/'

    def handle(self, *args, **options):
        csv_path = os.path.join(settings.BASE_DIR, 'data', 'players.csv')
        photo_static_dir = os.path.join(settings.BASE_DIR, 'static', 'img', 'player')
        photo_media_dir = os.path.join(settings.MEDIA_ROOT, 'player_thumbnails')

        # Pastikan folder media tersedia
        os.makedirs(photo_media_dir, exist_ok=True)

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"❌ File {csv_path} tidak ditemukan."))
            return

        with open(csv_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter='\t')  # pakai tab (karena contoh kamu tab-separated)
            for row in reader:
                name = row['name'].strip()
                position = row['position'].strip()
                team_name = row['team'].strip()
                citizenship = row['citizenship'].strip()
                age = int(row['age'] or 0)
                goals = int(row['curr_goals'] or 0)
                assists = int(row['curr_assists'] or 0)
                matches = int(row['match_played'] or 0)
                cleansheet = int(row['curr_cleansheet'] or 0)

                # --- 🏟️ cari klub ---
                try:
                    club = Club.objects.get(nama_klub=team_name)
                except Club.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"⚠️ Klub '{team_name}' tidak ditemukan untuk {name}."))
                    continue

                # --- 🔍 cari foto pemain ---
                normalized_name = re.sub(r'\s+', '_', name)
                photo_source_path = None

                for ext in ['.png', '.jpg', '.jpeg', '.webp']:
                    candidate = os.path.join(photo_static_dir, f"{normalized_name}{ext}")
                    if os.path.exists(candidate):
                        photo_source_path = candidate
                        break
                    candidate_lower = os.path.join(photo_static_dir, f"{normalized_name.lower()}{ext}")
                    if os.path.exists(candidate_lower):
                        photo_source_path = candidate_lower
                        break

                # --- 🧱 simpan ke database ---
                player, created = Player.objects.get_or_create(
                    name=name,
                    team=club,
                    defaults={
                        'position': position,
                        'citizenship': citizenship,
                        'age': age,
                        'curr_goals': goals,
                        'curr_assists': assists,
                        'match_played': matches,
                        'curr_cleansheet': cleansheet,
                    }
                )

                if not created:
                    player.position = position
                    player.citizenship = citizenship
                    player.age = age
                    player.curr_goals = goals
                    player.curr_assists = assists
                    player.match_played = matches
                    player.curr_cleansheet = cleansheet

                # --- 📸 salin foto ke media/player_thumbnails ---
                if photo_source_path:
                    photo_filename = os.path.basename(photo_source_path)
                    photo_destination = os.path.join(photo_media_dir, photo_filename)

                    if not os.path.exists(photo_destination):
                        shutil.copy(photo_source_path, photo_destination)

                    player.profile_picture_url.name = f"player_thumbnails/{photo_filename}"
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Foto untuk {name} tidak ditemukan."))

                player.save()

                status = "🟢 Dibuat" if created else "🟡 Diperbarui"
                self.stdout.write(self.style.SUCCESS(f"{status}: {player.name} ({player.team.nama_klub})"))

        self.stdout.write(self.style.SUCCESS("✅ Import pemain selesai!"))
