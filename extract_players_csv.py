import csv
import os
from players.models import Player
from clubs.models import Club
from django.core.files import File
from django.conf import settings

# Get the current working directory (usually the root of the project)
base_dir = os.getcwd()
csv_path = os.path.join(base_dir, 'data', 'players.csv')

with open(csv_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        # Get the team name and search for the corresponding Club object
        team_name = row['team']  # Adjust this if the CSV uses a different column name
        try:
            club = Club.objects.get(name=team_name)  # Fetch the Club object based on the name
        except Club.DoesNotExist:
            print(f"Club '{team_name}' does not exist.")
            continue  # Skip to the next row if the club doesn't exist

        # Set the path to the profile picture
        player_name = row['name']
        profile_picture_path = os.path.join(settings.STATIC_URL, 'player', f'{player_name.replace(" ",'_')}.png')  # Adjust the extension as needed
        
        # Create the Player object
        player = Player.objects.create(
            name=row['name'],
            position=row['position'],
            team=club,
            profile_picture_url=profile_picture_path,
            citizenship=row['citizenship'],
            age=int(row['age']),
            curr_goals=int(row['curr_goals']),
            curr_assists=int(row['curr_assists']),
            match_played=int(row['match_played']),
            curr_cleansheet=int(row['curr_cleansheet']),
        )