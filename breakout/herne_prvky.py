import pygame
import random

from typing import Optional
from typing import TYPE_CHECKING
from config import *

if TYPE_CHECKING:
    from hra import Hra

obrazovka = pygame.display.set_mode((SIRKA_OBRAZOVKY, VYSKA_OBRAZOVKY))  # Inicializácia obrazovky


class Palka:
    def __init__(self):
        self.x = SIRKA_OBRAZOVKY // 2 - SIRKA_PALKY // 2
        self.y = VYSKA_OBRAZOVKY - VYSKA_PALKY - 10
        self.original_sirka_palky = SIRKA_PALKY
        self.sirka_palky = SIRKA_PALKY
        self.vyska_palky = VYSKA_PALKY
        self.rychlost_palky = RYCHLOST_PALKY
        self.tvar_palky = pygame.Rect(self.x, self.y, self.sirka_palky, self.vyska_palky)
        self.aktivne_powerupy = {}

    def pohyb(self, smer: str):
        if smer == "VLAVO" and self.tvar_palky.left > 0:
            self.tvar_palky.x -= self.rychlost_palky
        if smer == "VPRAVO" and self.tvar_palky.right < SIRKA_OBRAZOVKY:
            self.tvar_palky.x += self.rychlost_palky

    def powerup_na_zmenu_palky(self, typ: str):
        if typ == 'zvacsi':
            self.sirka_palky = int(self.original_sirka_palky * POWERUP_ZVACSENIE_PADLA)
            self.aktivne_powerupy['zvacsi'] = pygame.time.get_ticks() + POWERUP_CAS * 1000
        elif typ == 'zmensi':
            self.sirka_palky = int(self.original_sirka_palky * POWERUP_ZMENSENIE_PADLA)
            self.aktivne_powerupy['zmensi'] = pygame.time.get_ticks() + POWERUP_CAS * 1000
        self.aktualizuj_palku()

    def nakresli_palku(self):
        pygame.draw.rect(obrazovka, FARBA_LOPTY_A_PALKY, self.tvar_palky)

    def reset_velkost_palky(self):
        if not ('zvacsi' in self.aktivne_powerupy or 'zmensi' in self.aktivne_powerupy):
            self.sirka_palky = self.original_sirka_palky
            self.aktualizuj_palku()

    def aktualizuj(self):
        # Kontrola ukoncenia dlzky casu powerupu
        aktualny_cas = pygame.time.get_ticks()
        for typ_powerupu, koniec_cas in list(self.aktivne_powerupy.items()):
            if aktualny_cas > koniec_cas:
                del self.aktivne_powerupy[typ_powerupu]
                if typ_powerupu in ['zvacsi', 'zmensi']:
                    self.reset_velkost_palky()

    def aktualizuj_palku(self):
        center_x = self.tvar_palky.centerx
        self.tvar_palky = pygame.Rect(center_x - self.sirka_palky // 2, self.y, self.sirka_palky, self.vyska_palky)


class PowerUp:
    def __init__(self, x: int, y: int, typ: str):
        self.x = x
        self.y = y
        self.typ_powerupu = typ
        self.tvar_powerupu = pygame.Rect(x, y, 20, 20)
        self.aktivny = True

    def nakresli_powerup(self):
        if self.typ_powerupu == "zvacsi":
            farba = FARBA_ZVACSENIA_PADLA
        elif self.typ_powerupu == "zmensi":
            farba = FARBA_ZMENSENIA_PADLA
        elif self.typ_powerupu == "triple":
            farba = FARBA_TRIPLE
        else:
            farba = (255, 255, 255)  # default, nemalo by nastať

        if self.aktivny:
            # Použity kruh pre grafiku powerupu
            pygame.draw.circle(obrazovka, farba, (self.tvar_powerupu.centerx, self.tvar_powerupu.centery), 10)

    def aktivuj_powerup(self, palka: 'Palka', hra: 'Hra'):
        if self.typ_powerupu == "triple":
            for _ in range(len(hra.lopticky)):
                prvotna_lopticka = hra.lopticky[_]
                for _ in range(2):
                    nova_lopticka = Lopticka()
                    nova_lopticka.x = prvotna_lopticka.x
                    nova_lopticka.y = prvotna_lopticka.y
                    # Smery powerupu
                    nova_lopticka.rychlost_lopticky_x = random.choice([-3, -2, -1, 1, 2, 3])    # Horizontalne
                    nova_lopticka.rychlost_lopticky_y = -random.choice([2, 3, 4])               # Vertikalne
                    hra.lopticky.append(nova_lopticka)
        elif self.typ_powerupu in ["zvacsi", "zmensi"]:
            palka.powerup_na_zmenu_palky(self.typ_powerupu)
        self.aktivny = False

    def vertikalny_pohyb_powerupu(self):
        self.y += 2
        self.tvar_powerupu.y = self.y
        if self.y > VYSKA_OBRAZOVKY:
            self.aktivny = False


class Tehlicka:
    def __init__(self, x: int, y: int, farba: tuple, znicitelna=True):
        self.x = x
        self.y = y
        self.sirka_tehlicky = SIRKA_TEHLICIEK
        self.vyska_tehlicky = VYSKA_TEHLICIEK
        self.tvar_tehlicky = pygame.Rect(self.x, self.y, self.sirka_tehlicky, self.vyska_tehlicky)
        self.viditelna = True
        self.farba_tehlicky = farba
        self.znicitelna = znicitelna
        self.powerup = None

    def nakresli(self):
        if self.viditelna:
            pygame.draw.rect(obrazovka, self.farba_tehlicky, self.tvar_tehlicky)

    def pridaj_powerup(self, powerup_typ: str) -> Optional[PowerUp]:
        if not self.powerup:
            self.powerup = PowerUp(self.x + self.sirka_tehlicky // 2, self.y + self.vyska_tehlicky // 2, powerup_typ)
            return self.powerup
        return None


class Lopticka:
    def __init__(self):
        self.x = SIRKA_OBRAZOVKY // 2
        self.y = VYSKA_OBRAZOVKY // 2
        self.radius_lopticky = RADIUS_LOPTICKY
        self.rychlost_lopticky_x = RYCHLOST_LOPTICKY_X
        self.rychlost_lopticky_y = RYCHLOST_LOPTICKY_Y
        self.tvar_lopticky = pygame.Rect(self.x - self.radius_lopticky, self.y - self.radius_lopticky,
                                         self.radius_lopticky * 2, self.radius_lopticky * 2)
        self.max_rychlost_lopticky_x = 5  # horizontalne
        self.max_rychlost_lopticky_y = 5  # vertikalne

    def pohyb(self):
        self.tvar_lopticky.x += self.rychlost_lopticky_x
        self.tvar_lopticky.y += self.rychlost_lopticky_y
        # Kolízia so stenami
        if self.tvar_lopticky.right >= SIRKA_OBRAZOVKY or self.tvar_lopticky.left <= 0:
            self.rychlost_lopticky_x *= -1
        if self.tvar_lopticky.top <= 0:
            self.rychlost_lopticky_y *= -1

    def smer_kolizie_lotpicka_tehlicka(self, tehlicka: Tehlicka):
        # Zistenie strany kolízie
        stredobod_x = self.tvar_lopticky.centerx
        stredobod_y = self.tvar_lopticky.centery

        if (tehlicka.tvar_tehlicky.collidepoint(stredobod_x, self.tvar_lopticky.top) or
                tehlicka.tvar_tehlicky.collidepoint(stredobod_x, self.tvar_lopticky.bottom)):
            self.rychlost_lopticky_y *= -1  # Vertikalna kolizia
        elif tehlicka.tvar_tehlicky.collidepoint(self.tvar_lopticky.left, stredobod_y) or tehlicka.tvar_tehlicky.collidepoint(
                self.tvar_lopticky.right, stredobod_y):
            self.rychlost_lopticky_x *= -1  # Horizontalna kolizia
        else:
            self.rychlost_lopticky_y *= -1  # Default

    def nakresli_lopticku(self):
        pygame.draw.circle(obrazovka, FARBA_LOPTY_A_PALKY, (self.tvar_lopticky.x + self.radius_lopticky, self.tvar_lopticky.y + self.radius_lopticky), self.radius_lopticky)
