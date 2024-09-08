from PIL import Image
import pytesseract
from thefuzz import process
import gspread

# Server list for sanity-checking strings that don't match player names
SERVERS = [
    # Chaos
    "Cerberus", "Louisoix", "Moogle", "Omega", "Phantom", "Ragnarok", "Sagittarius", "Spriggan",
    # Light
    "Alpha", "Lich", "Odin", "Phoenix", "Raiden", "Shiva", "Twintania", "Zodiark"
]

# Duty list for sanity checking strings that don't match player names
DUTIES = [
    "The Weapon's Refrain (Ultimate)",
    "The Epic of Alexander (Ultimate)"
]


# Grab member list from the history sheet (should probably be substituted with data from discord)
"""
gc = gspread.api_key("changeme")
sheet = gc.open_by_key("1dj7kcMrePdALYDmCmmdBEkycjhGrJqdTIjETua_vZhk")

USERS = set(sheet.get_worksheet(0).col_values(1)[3:])\
    .union(set(sheet.get_worksheet(1).col_values(1)[3:]))\
    .union(set(sheet.get_worksheet(2).col_values(1)[3:]))

with open("members.txt", "w") as f:
    for user in USERS:
        f.write(f"{user}\n")
"""

# Or load a cached list
with open("members.txt", "r") as f:
    USERS = f.read().split("\n")

# Tesseract assumed installed here
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'

# Raw data (if debugging)
# print(pytesseract.image_to_data(Image.open('test2.png'), config="--psm 11"))

# Segment and parse image
# Two main issues
# - Most user names aren't English words, this confused the OCR net which was trained on english
# (other languages are possible but not helpful either)
# - OCR gets confused by duty and role icons
#
# Alleviated by:
# - fuzzy matching on the known user list (gsheets/discord as data source)
# - loose cropping to get rid of duty icons
#
# Some options that seemed relevant but weren't useful:
# -c load_system_dawg=0
# -c load_freq_dawg=0
# --user-words=members.txt
data = pytesseract.image_to_string(Image.open('test2.png'), config="--psm 11").split("\n")

players = []
unclassied = []

# participation data contains player names, servers and duty names. try and match which is which
# We extract players and discard servers and duties
# we also keep track of strings we could not confidently identify
for line in data:
    line = line.strip()
    if not line:
        continue

    # first try and figure out if we got a player
    player, confidence = process.extractOne(line, USERS)
    if confidence > 90:
        players.append(player)
        continue

    # if not, see if we got a server
    server, confidence = process.extractOne(line, SERVERS)
    if confidence > 90:
        # confidently identified a server, discard
        continue

    duty, confidence = process.extractOne(line, DUTIES)
    if confidence > 90:
        # confidently identified a duty, discard
        continue

    # make a note of unidentified lines
    unclassied.append(line)

print(f"Identified {len(players)} participants")
for player in players:
    print(f"- {player}")

print(f"{len(unclassied)} unclassified lines remain")
for line in unclassied:
    print(f"- {unclassied}")
