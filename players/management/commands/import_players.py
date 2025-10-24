import csv
import os
import re
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from clubs.models import Club
from players.models import Player


class Command(BaseCommand):
    help = 'Import data pemain dari CSV dan gambar dari static/img/players/'

    def handle(self, *args, **options):
        csv_path = os.path.join(settings.BASE_DIR, 'data', 'players.csv')
        img_dir = os.path.join(settings.BASE_DIR, 'static', 'img', 'players')

        if not os.path.exists(csv_path):
            self.stderr.write(self.style.ERROR(f"❌ File {csv_path} tidak ditemukan."))
            return

        with open(csv_path, newline='', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',')  # 👈 pakai koma!

            for row in reader:
                # Normalisasi data
                name = row['name'].strip()
                position = row['position'].strip()
                team_name = row['team'].strip()
                citizenship = row['citizenship'].strip()
                age = int(row['age'])
                curr_goals = int(row['curr_goals'])
                curr_assists = int(row['curr_assists'])
                match_played = int(row['match_played'])
                curr_cleansheet = int(row['curr_cleansheet'])

                # 🔗 pastikan klub sudah ada
                try:
                    club = Club.objects.get(nama_klub=team_name)
                except Club.DoesNotExist:
                    self.stderr.write(self.style.WARNING(f"⚠️ Klub {team_name} belum ada di database. Lewati pemain {name}."))
                    continue

                # 🔍 cari foto pemain berdasarkan nama
                normalized_name = re.sub(r'\s+', '_', name)
                profile_path = None
                for ext in ['.png', '.jpg', '.jpeg', '.webp']:
                    candidate = os.path.join(img_dir, f"{normalized_name}{ext}")
                    if os.path.exists(candidate):
                        profile_path = candidate
                        break
                    candidate_lower = os.path.join(img_dir, f"{normalized_name.lower()}{ext}")
                    if os.path.exists(candidate_lower):
                        profile_path = candidate_lower
                        break

                # 🧱 Simpan atau update pemain
                player, created = Player.objects.get_or_create(
                    name=name,
                    team=club,
                    defaults={
                        'position': position,
                        'citizenship': citizenship,
                        'age': age,
                        'curr_goals': curr_goals,
                        'curr_assists': curr_assists,
                        'match_played': match_played,
                        'curr_cleansheet': curr_cleansheet,
                    }
                )

                if not created:
                    player.position = position
                    player.citizenship = citizenship
                    player.age = age
                    player.curr_goals = curr_goals
                    player.curr_assists = curr_assists
                    player.match_played = match_played
                    player.curr_cleansheet = curr_cleansheet

                if profile_path:
                    with open(profile_path, 'rb') as f:
                        player.profile_picture_url.save(os.path.basename(profile_path), File(f), save=False)
                else:
                    self.stdout.write(self.style.WARNING(f"⚠️ Foto untuk {name} tidak ditemukan."))

                player.save()
                status = "🟢 Dibuat" if created else "🟡 Diperbarui"
                self.stdout.write(self.style.SUCCESS(f"{status}: {player.name} ({club.nama_klub})"))

        self.stdout.write(self.style.SUCCESS("✅ Import data pemain selesai!"))
