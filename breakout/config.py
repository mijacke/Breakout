# ZIVOTY
POCET_ZIVOTOV = 3

# Pozadie hry
POZADIE_HRY = "res/pozadie.jpg"

# Hudba
HUDBA_HRY = "res/hudba.mp3"

# Nazov hry
NAZOV_HRY = 'Hra Breakout'

# Rozmery obrazovky
SIRKA_OBRAZOVKY = 800
VYSKA_OBRAZOVKY = 600

# Farby
FARBA_TRIPLE = (191, 97, 212),       # Lavender
FARBA_LOPTY_A_PALKY = (255, 0, 0)    # Red
FARBA_ZVACSENIA_PADLA = (0, 255, 0)  # Green
FARBA_ZMENSENIA_PADLA = (0, 0, 255)  # Blue

# Vlastnosti pálky
SIRKA_PALKY = 120
VYSKA_PALKY = 20
RYCHLOST_PALKY = 6

# Vlastnosti loptičky
RADIUS_LOPTICKY = 10
RYCHLOST_LOPTICKY_X = 5
RYCHLOST_LOPTICKY_Y = -5

# Vlastnosti tehličiek
POCET_RIADKOV_TEHLICIEK = 8
POCET_STLPCOV_TEHLICIEK = 13
MEDZERA_TEHLICIEK = 5
SIRKA_TEHLICIEK = (SIRKA_OBRAZOVKY - ((POCET_STLPCOV_TEHLICIEK + 1) * MEDZERA_TEHLICIEK)) // POCET_STLPCOV_TEHLICIEK
VYSKA_TEHLICIEK = 20

# Vlastnosti Power-up
POWERUP_CAS = 10
POWERUP_ZVACSENIE_PADLA = 2.5
POWERUP_ZMENSENIE_PADLA = 0.5

# Farby
BIELA = (255, 255, 255)
FARBY_TEHLICIEK = [
    (236, 18, 84),   # Vivid Red
    (242, 124, 20),  # Electric Orange
    (245, 227, 29),  # Lemon Yellow
    (30, 232, 182),  # Bright Green
    (38, 161, 213),  # Sky Blue
    (58, 229, 231),  # Aqua
    (87, 11, 183),   # Royal Purple
    (135, 86, 228),  # Soft Violet
    # dalšie farby
    (191, 97, 212),  # Lavender
    (241, 9, 131)    # Magenta
]

# Neznicitelna stena
STENA_OD_VRCHU = 1
STENA_OD_SPODKU = 5
STENA_OD_LAVEHO_STLPCA = 3
STENA_OD_PRAVEHO_STLPCA = 9

# Skore
PRIDAJ_SKORE = 10

# šanca powerupu pri trafení lopty a tehličky
SANCA_NA_SPAWN_POWERUPU = 0.17

FPS_HRY = 60
