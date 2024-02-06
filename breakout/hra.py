import pygame
import sys
import random
import herne_prvky

from herne_prvky import Palka, Lopticka, Tehlicka
from config import *


class Hra:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        try:
            pygame.mixer.music.load(HUDBA_HRY)
            pygame.mixer.music.play(-1)  # Hranie hudby donekonecna
        except pygame.error as e:
            print(f"Nepodarilo sa nacitat hudbu: {e}")

        self.stadium_hry = "bezi"
        self.skore = 0
        self.zivoty = POCET_ZIVOTOV
        self.pauza = False
        self.obrazovka = herne_prvky.obrazovka
        self.hodiny = pygame.time.Clock()  # Na sledovanie casu
        self.font = pygame.font.Font(None, 36)
        pygame.display.set_caption(NAZOV_HRY)  # Nazov hry
        self.palka = Palka()
        self.lopticky = [Lopticka()]
        self.tehlicky = self.vytvor_tehlicky()
        self.tlacidlo_restart = None
        self.powerupy = []
        self.volume_slider_x = self.obrazovka.get_width() / 2 - 50
        self.volume_slider_y = self.obrazovka.get_height() / 2 + 100
        self.volume_slider_width = 100

        try:
            pozadie = pygame.image.load(POZADIE_HRY)
            self.upravene_pozadie = pygame.transform.scale(pozadie, (SIRKA_OBRAZOVKY, VYSKA_OBRAZOVKY))
        except pygame.error as e:
            print(f"Nepodarilo sa nacitat obrazok pozadia: {e}")
            sys.exit()

    def spusti(self):
        while True:
            self.spracuj_udalosti()
            if self.stadium_hry == "bezi":
                self.aktualizuj_hru()
            self.vykresli_prvky()
            self.hodiny.tick(FPS_HRY)

    def spracuj_udalosti(self):
        for udalost in pygame.event.get():
            if udalost.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif udalost.type == pygame.KEYDOWN:
                if udalost.key == pygame.K_ESCAPE:
                    self.pauza = not self.pauza
            elif udalost.type == pygame.MOUSEBUTTONDOWN and self.pauza:
                myska_pozicia = pygame.mouse.get_pos()
                if self.tlacidlo_restart and self.tlacidlo_restart.collidepoint(myska_pozicia):
                    self.restart_hry()
                x, y = pygame.mouse.get_pos()
                if self.volume_slider_x <= x <= self.volume_slider_x + self.volume_slider_width and self.volume_slider_y <= y <= self.volume_slider_y + 10:
                    nova_hlasitost = (x - self.volume_slider_x) / self.volume_slider_width
                    pygame.mixer.music.set_volume(nova_hlasitost)
            elif (self.stadium_hry == "vyhra" or self.stadium_hry == "koniec_hry") and udalost.type == pygame.MOUSEBUTTONDOWN:
                myska_pozicia = pygame.mouse.get_pos()
                if self.tlacidlo_restart.collidepoint(myska_pozicia):
                    self.restart_hry()

        if not self.pauza:
            klavesy = pygame.key.get_pressed()
            if klavesy[pygame.K_a]:
                self.palka.pohyb("VLAVO")
            if klavesy[pygame.K_d]:
                self.palka.pohyb("VPRAVO")

    def vytvor_tehlicky(self) -> list:
        tehlicky = []

        # Hranice pre generaciu neznicitelnych tehliciek
        vrchny_riadok = STENA_OD_VRCHU
        spodny_riadok = STENA_OD_SPODKU
        lavy_stlpec = STENA_OD_LAVEHO_STLPCA
        pravy_stlpec = STENA_OD_PRAVEHO_STLPCA

        for riadok in range(herne_prvky.POCET_RIADKOV_TEHLICIEK):
            for stlpec in range(herne_prvky.POCET_STLPCOV_TEHLICIEK):
                x = stlpec * (
                        herne_prvky.SIRKA_TEHLICIEK + herne_prvky.MEDZERA_TEHLICIEK) + herne_prvky.MEDZERA_TEHLICIEK
                y = riadok * (
                        herne_prvky.VYSKA_TEHLICIEK + herne_prvky.MEDZERA_TEHLICIEK) + herne_prvky.MEDZERA_TEHLICIEK
                farba = FARBY_TEHLICIEK[riadok % len(FARBY_TEHLICIEK)]
                znicitelna = True  # Default

                # Nastavenie neznicitelnych tehliciek v ramci definovaneho obdlznika, az na vrchnu cast
                if (vrchny_riadok < riadok <= spodny_riadok and (stlpec == lavy_stlpec or stlpec == pravy_stlpec)) or (
                        riadok == spodny_riadok and lavy_stlpec <= stlpec <= pravy_stlpec):
                    farba = (150, 150, 150)  # farba_tehlicky neznicitelnych
                    znicitelna = False

                tehlicky.append(Tehlicka(x, y, farba, znicitelna))

        return tehlicky

    def aktualizuj_hru(self):
        if not self.pauza and self.stadium_hry == "bezi":
            self.palka.aktualizuj()
            for lopticka in self.lopticky:
                lopticka.pohyb()
            self.skontroluj_kolizie()
            self.kontrola_vyhry()
            self.aktualizuj_cas_powerupu()

    def skontroluj_kolizie(self):
        self.kolizia_lopta_palka()
        self.kolizia_lopta_tehlicka()
        self.kolizia_lopta_obrazovka()
        self.kolizia_palka_powerup()
        self.handle_pohyb_powerupov()

    def kolizia_lopta_palka(self):
        for lopticka in self.lopticky:
            if lopticka.tvar_lopticky.colliderect(self.palka.tvar_palky):
                offset_rozdielu_stredov = lopticka.tvar_lopticky.centerx - self.palka.tvar_palky.centerx
                normalizovany_offset = offset_rozdielu_stredov / (self.palka.sirka_palky / 2)

                min_horizontal_offset = 0.2
                if abs(normalizovany_offset) < min_horizontal_offset:
                    normalizovany_offset = min_horizontal_offset if normalizovany_offset >= 0 else -min_horizontal_offset

                # Horizontalna rychlost
                lopticka.rychlost_lopticky_x = normalizovany_offset * lopticka.max_rychlost_lopticky_x
                # Vertikalna rychlost, pevna, -abs pretoze lopta potrebuje ist hore
                lopticka.rychlost_lopticky_y = -abs(lopticka.max_rychlost_lopticky_y)

                lopticka.tvar_lopticky.bottom = self.palka.tvar_palky.top  # pre istotu, aby sa nezalepili o seba

    def kolizia_lopta_tehlicka(self):
        for lopticka in self.lopticky:
            for tehlicka in self.tehlicky:
                if tehlicka.viditelna and lopticka.tvar_lopticky.colliderect(tehlicka.tvar_tehlicky):
                    lopticka.smer_kolizie_lotpicka_tehlicka(tehlicka)

                    if tehlicka.znicitelna:
                        self.skore += PRIDAJ_SKORE  # Zatial pevne, idealne prerobit + pamat na high_scores
                        tehlicka.viditelna = False

                        if random.random() < SANCA_NA_SPAWN_POWERUPU:
                            powerup = tehlicka.pridaj_powerup(random.choice(["zvacsi", "zmensi", "triple"]))
                            if powerup:
                                self.powerupy.append(powerup)
                    break  # Dôležitý break na vyhnutie sa viacnásobným kolíziám

    def kolizia_lopta_obrazovka(self):
        self.lopticky = [ball for ball in self.lopticky if ball.tvar_lopticky.bottom < self.obrazovka.get_height()]
        if not self.lopticky:
            self.strata_lopty_z_obrazovky()

    def strata_lopty_z_obrazovky(self):
        self.zivoty -= 1
        if self.zivoty <= 0:
            self.stadium_hry = "koniec_hry"
        else:
            self.lopticky.append(Lopticka())

    def kolizia_palka_powerup(self):
        for powerup in self.powerupy:
            if powerup.aktivny and self.palka.tvar_palky.colliderect(powerup.tvar_powerupu):
                powerup.aktivuj_powerup(self.palka, self)

    def handle_pohyb_powerupov(self):
        for powerup in list(self.powerupy):  # Kópia zoznamu na bezpečné odstránenie
            powerup.vertikalny_pohyb_powerupu()
            if not powerup.aktivny:
                self.powerupy.remove(powerup)

    def aktualizuj_cas_powerupu(self):
        aktualny_cas = pygame.time.get_ticks()
        if self.powerupy and aktualny_cas > herne_prvky.POWERUP_CAS * 1000:
            self.palka.reset_velkost_palky()
            self.powerupy = [pu for pu in self.powerupy if pu.aktivny]  # Vymazanie neaktivnych

    def restart_hry(self):
        self.skore = 0
        self.zivoty = POCET_ZIVOTOV
        self.pauza = False
        self.palka = Palka()
        self.lopticky = [Lopticka()]
        self.tehlicky = self.vytvor_tehlicky()
        self.powerupy = []
        self.stadium_hry = "bezi"

    def kontrola_vyhry(self):
        su_vsetky_tehlicky_znicene = all(not tehlicka.viditelna for tehlicka in self.tehlicky if tehlicka.znicitelna)
        if su_vsetky_tehlicky_znicene:
            self.stadium_hry = "vyhra"

    def vykresli_pauzu(self):
        pauza_text = self.font.render("Stlač 'ESC' pre pokračovanie", True, BIELA)
        text_rect = pauza_text.get_rect(center=(self.obrazovka.get_width() / 2, self.obrazovka.get_height() / 2))
        self.obrazovka.blit(pauza_text, text_rect)
        self.vykresli_volume_slider()
        reset_text = self.font.render('Reštartuj hru', True, BIELA)
        self.tlacidlo_restart = reset_text.get_rect(
            center=(self.obrazovka.get_width() / 2, self.obrazovka.get_height() / 2 + 50))
        self.obrazovka.blit(reset_text, self.tlacidlo_restart)

    def vykresli_volume_slider(self):
        level_hlasitosti = pygame.mixer.music.get_volume()
        pygame.draw.rect(self.obrazovka, (255, 255, 255), [self.volume_slider_x, self.volume_slider_y, self.volume_slider_width, 10], 2)
        pygame.draw.rect(self.obrazovka, (0, 255, 0),
                         [self.volume_slider_x, self.volume_slider_y, self.volume_slider_width * level_hlasitosti, 10])  # level hlasitosti

    def vykresli_skore_a_zivoty(self):
        self._blit_text(f'Skóre: {self.skore}', (10, self.obrazovka.get_height() - 30))
        self._blit_text(f'Životy: {self.zivoty}', (self.obrazovka.get_width() - 100, self.obrazovka.get_height() - 30))

    def vykresli_koniec_hry(self, text: str):
        self.obrazovka.fill((0, 0, 0))
        text_koniec_hry = self.font.render(text, True, BIELA)
        skore_text = self.font.render(f'Tvoje skore: {self.skore}', True, BIELA)
        restart_text = self.font.render('Reštartuj hru', True, BIELA)

        koniec_hry_rect = text_koniec_hry.get_rect(
            center=(self.obrazovka.get_width() / 2, self.obrazovka.get_height() / 2 - 50))
        skore_rect = skore_text.get_rect(center=(self.obrazovka.get_width() / 2, self.obrazovka.get_height() / 2))
        self.tlacidlo_restart = restart_text.get_rect(
            center=(self.obrazovka.get_width() / 2, self.obrazovka.get_height() / 2 + 50))

        self.obrazovka.blit(text_koniec_hry, koniec_hry_rect)
        self.obrazovka.blit(skore_text, skore_rect)
        self.obrazovka.blit(restart_text, self.tlacidlo_restart)
        pygame.display.flip()

    def vykresli_prvky(self):
        if self.stadium_hry == "bezi":
            self.obrazovka.blit(self.upravene_pozadie, (0, 0))  # Nastavenie pozadia
            self.palka.nakresli_palku()

            for lopticka in self.lopticky:
                lopticka.nakresli_lopticku()
            for tehlicka in self.tehlicky:
                if tehlicka.viditelna:
                    tehlicka.nakresli()

            if self.pauza:
                self.vykresli_pauzu()

            for powerup in self.powerupy:
                if powerup.aktivny:
                    powerup.nakresli_powerup()

            self.vykresli_skore_a_zivoty()
        elif self.stadium_hry == "vyhra":
            self.vykresli_koniec_hry("Vyhral si")
        elif self.stadium_hry == "koniec_hry":
            self.vykresli_koniec_hry("Prehral si")
        pygame.display.flip()  # vykreslenie prvkov celej obrazovky

    def _blit_text(self, text, position):
        """Pomocná metóda na vykreslenie textu na obrazovku."""
        rendered_text = self.font.render(text, True, BIELA)
        self.obrazovka.blit(rendered_text, position)
