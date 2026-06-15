# -*- coding: utf-8 -*-
import pygame
import sys
import random
from collections import deque

pygame.init()

# =========================================================
# CONFIGURACAO GERAL
# =========================================================
TILE = 34
MAP_W = 24
MAP_H = 16
UI_H = 150

WIDTH = MAP_W * TILE
HEIGHT = MAP_H * TILE + UI_H
FPS = 60

MAX_PARTY_SIZE = 4

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TRPG Fantasia Tatica - Campanha Infinita")
clock = pygame.time.Clock()

font = pygame.font.SysFont("arial", 24)
small_font = pygame.font.SysFont("arial", 18)
tiny_font = pygame.font.SysFont("arial", 14)

# =========================================================
# CORES
# =========================================================
BLACK = (12, 12, 16)
WHITE = (240, 240, 240)
YELLOW = (255, 220, 80)
GOLD = (255, 200, 70)

GREEN_A = (68, 127, 70)
GREEN_B = (82, 145, 82)
GREEN_C = (54, 112, 60)
GRID_GREEN = (38, 82, 42)

DIRT_A = (128, 98, 62)
DIRT_B = (145, 112, 74)

WATER = (45, 105, 165)
WATER_EDGE = (65, 135, 190)

BLUE = (70, 120, 255)
CYAN = (85, 220, 255)
PURPLE = (180, 100, 220)
RED = (220, 70, 70)
LIGHT_RED = (255, 110, 110)
ORANGE = (255, 155, 80)
DARK_RED = (155, 48, 48)

GRAY = (115, 115, 115)
GRAY_DARK = (70, 70, 70)

TREE = (34, 95, 46)
TREE_DARK = (21, 58, 33)

MOVE_COLOR = (120, 210, 255)
ATTACK_COLOR = (255, 120, 120)
SKILL_COLOR = (255, 180, 255)
SKILL_RANGE_FILL = (255, 120, 255, 55)
GLOBAL_RANGE_FILL = (255, 80, 160, 40)
SELECT_COLOR = (255, 255, 120)
COVER_COLOR = (255, 190, 70)
TRAP_COLOR = (255, 70, 210)

PANEL_BG = (22, 22, 30)
PANEL_BOX = (38, 38, 50)
PANEL_DARK = (28, 28, 38)
PANEL_LINE = (82, 82, 105)

HP_GREEN = (60, 220, 90)
HP_RED_BG = (90, 25, 25)
SHIELD_COLOR = (160, 220, 255)

RARITY_COLORS = {
    "Comum": (210, 210, 210),
    "Raro": (80, 170, 255),
    "Epico": (190, 100, 255),
    "Lendario": (255, 190, 60),
    "Mercado Negro": (255, 45, 120),
}

# =========================================================
# TIPOS DE TILE
# =========================================================
VOID = 0
FLOOR = 1
OBSTACLE = 2
WATER_TILE = 3
PATH_TILE = 4


# =========================================================
# FUNCOES DE TEXTO / UTILIDADES
# =========================================================
def in_bounds(x, y):
    return 0 <= x < MAP_W and 0 <= y < MAP_H


def is_floor_cell(cell):
    return cell in (FLOOR, PATH_TILE)


def trim_text(text, font_obj, max_width):
    if font_obj.size(text)[0] <= max_width:
        return text

    while text and font_obj.size(text + "...")[0] > max_width:
        text = text[:-1]

    return text + "..."


def draw_text_fit(surf, text, font_obj, color, x, y, max_width):
    final_text = trim_text(str(text), font_obj, max_width)
    surf.blit(font_obj.render(final_text, True, color), (x, y))


def seeded_dot(x, y, salt, chance=13):
    value = (x * 73856093) ^ (y * 19349663) ^ (salt * 83492791)
    return value % chance == 0


# =========================================================
# DADOS DAS HABILIDADES
# =========================================================
ABILITY_DATA = {
    "Cavaleiro": [
        {"id": "corte_de_vento", "name": "Corte de Vento", "type": "damage", "range": 3, "bonus": 12, "cooldown": 3, "desc": "Lamina distante."},
        {"id": "juramento_de_ferro", "name": "Juramento de Ferro", "type": "shield", "cooldown": 4, "duration": 2, "reduction": 0.50, "desc": "Metade do dano."},
        {"id": "desafio_real", "name": "Desafio Real", "type": "mark", "range": 3, "vulnerability": 0.30, "duration": 2, "cooldown": 3, "desc": "Marca o alvo."},
    ],

    "Arqueiro": [
        {"id": "flecha_ricochete", "name": "Flecha Ricochete", "type": "aoe", "range": 5, "bonus": 8, "radius": 1, "cooldown": 3, "desc": "Acerta vizinhos."},
        {"id": "olhos_de_aguia", "name": "Olhos de Aguia", "type": "buff", "cooldown": 3, "duration": 2, "atk_bonus": 6, "desc": "ATK aumentado."},
        {"id": "tiro_perfurante", "name": "Tiro Perfurante", "type": "damage", "range": 6, "bonus": 16, "cooldown": 4, "desc": "Tiro preciso."},
    ],

    "Mago": [
        {"id": "cometa_arcano", "name": "Cometa Arcano", "type": "aoe", "range": 4, "bonus": 15, "radius": 1, "cooldown": 3, "desc": "Explosao magica."},
        {"id": "barreira_arcana", "name": "Barreira Arcana", "type": "shield", "cooldown": 4, "duration": 2, "reduction": 0.40, "desc": "Protecao magica."},
        {"id": "surto_de_mana", "name": "Surto de Mana", "type": "focus", "cooldown": 4, "ap_gain": 1, "ap_cap": 3, "desc": "Ganha AP."},
    ],

    "Lanceiro": [
        {"id": "linha_perfurante", "name": "Linha Perfurante", "type": "damage", "range": 2, "bonus": 14, "cooldown": 2, "desc": "Ataque a 2 casas."},
        {"id": "bandeira_de_avanco", "name": "Bandeira de Avanco", "type": "buff", "cooldown": 3, "duration": 2, "atk_bonus": 5, "desc": "ATK aumentado."},
        {"id": "postura_firme", "name": "Postura Firme", "type": "shield", "cooldown": 3, "duration": 1, "reduction": 0.35, "desc": "Defesa rapida."},
    ],

    "Clerigo": [
        {"id": "cura_teimosa", "name": "Cura Teimosa", "type": "heal", "range": 4, "amount": 50, "cooldown": 3, "desc": "Cura aliado."},
        {"id": "selo_do_sol", "name": "Selo do Sol", "type": "mark", "range": 4, "vulnerability": 0.35, "duration": 2, "cooldown": 3, "desc": "Alvo sofre mais."},
        {"id": "luz_explosiva", "name": "Luz Explosiva", "type": "aoe", "range": 4, "bonus": 10, "radius": 1, "cooldown": 3, "desc": "Luz em area."},
    ],

    "Ladino": [
        {"id": "punhal_cruel", "name": "Punhal Cruel", "type": "damage", "range": 1, "bonus": 24, "cooldown": 3, "desc": "Dano perto."},
        {"id": "passo_fantasma", "name": "Passo Fantasma", "type": "focus", "cooldown": 4, "ap_gain": 2, "ap_cap": 3, "desc": "Recupera AP."},
        {"id": "capa_de_sombra", "name": "Capa de Sombra", "type": "shield", "cooldown": 3, "duration": 1, "reduction": 0.65, "desc": "Muito evasivo."},
    ],

    "Paladino": [
        {"id": "luz_julgadora", "name": "Luz Julgadora", "type": "damage", "range": 3, "bonus": 17, "cooldown": 3, "desc": "Dano sagrado."},
        {"id": "bencao_sagrada", "name": "Bencao Sagrada", "type": "heal", "range": 3, "amount": 65, "cooldown": 4, "desc": "Cura forte."},
        {"id": "sol_na_armadura", "name": "Sol na Armadura", "type": "shield", "cooldown": 4, "duration": 2, "reduction": 0.55, "desc": "Defesa epica."},
    ],

    "Necromante": [
        {"id": "drenar_vida", "name": "Drenar Vida", "type": "drain", "range": 4, "bonus": 16, "cooldown": 3, "desc": "Dano e cura."},
        {"id": "maldicao_de_osso", "name": "Maldicao de Osso", "type": "mark", "range": 4, "vulnerability": 0.50, "duration": 2, "cooldown": 4, "desc": "Enfraquece."},
        {"id": "explosao_cemiterio", "name": "Explosao Cemiterio", "type": "aoe", "range": 4, "bonus": 18, "radius": 1, "cooldown": 4, "desc": "Area sombria."},
    ],

    "Arquimago": [
        {"id": "meteoro", "name": "Meteoro", "type": "aoe", "range": 5, "bonus": 32, "radius": 1, "cooldown": 4, "desc": "Explosao lendaria."},
        {"id": "dobra_temporal", "name": "Dobra Temporal", "type": "focus", "cooldown": 4, "ap_gain": 2, "ap_cap": 4, "desc": "Ganha AP."},
        {"id": "prisao_astral", "name": "Prisao Astral", "type": "mark", "range": 5, "vulnerability": 0.55, "duration": 2, "cooldown": 4, "desc": "Marca lendaria."},
    ],

    "Dragoon": [
        {"id": "lanca_celeste", "name": "Lanca Celeste", "type": "damage", "range": 3, "bonus": 30, "cooldown": 4, "desc": "Golpe lendario."},
        {"id": "sangue_draconico", "name": "Sangue Draconico", "type": "buff", "cooldown": 4, "duration": 2, "atk_bonus": 12, "desc": "ATK brutal."},
        {"id": "salto_do_dragao", "name": "Salto do Dragao", "type": "aoe", "range": 4, "bonus": 20, "radius": 1, "cooldown": 4, "desc": "Cai em area."},
    ],

    "Guardiao Solar": [
        {"id": "corte_solar", "name": "Corte Solar", "type": "aoe", "range": 4, "bonus": 24, "radius": 1, "cooldown": 4, "desc": "Luz em area."},
        {"id": "aura_solar", "name": "Aura Solar", "type": "heal", "range": 4, "amount": 80, "cooldown": 4, "desc": "Cura lendaria."},
        {"id": "nucleo_do_sol", "name": "Nucleo do Sol", "type": "shield", "cooldown": 5, "duration": 2, "reduction": 0.70, "desc": "Defesa solar."},
    ],

    "Oraculo do Caos": [
        {"id": "decreto_impossivel", "name": "Decreto Impossivel", "type": "mark", "range": 5, "vulnerability": 0.70, "duration": 2, "cooldown": 4, "desc": "Alvo vira piada."},
        {"id": "risada_do_destino", "name": "Risada do Destino", "type": "aoe", "range": 5, "bonus": 26, "radius": 1, "cooldown": 4, "desc": "Caos em area."},
        {"id": "sorte_roubada", "name": "Sorte Roubada", "type": "buff", "cooldown": 4, "duration": 2, "atk_bonus": 14, "desc": "ATK absurdo."},
    ],

    "Mestre das Sombras": [
        {"id": "chamar_lacaios", "name": "Chamar Lacaios", "type": "summon_minions", "cooldown": 3, "count": 2, "desc": "Invoca lacaios."},
        {"id": "dragao_de_sombras", "name": "Dragao de Sombras", "type": "summon_dragon", "cooldown": 8, "starts_cd": 5, "desc": "Invoca dragao."},
        {"id": "manto_vazio", "name": "Manto Vazio", "type": "shield", "cooldown": 4, "duration": 2, "reduction": 0.50, "desc": "Sobrevive, talvez."},
    ],

    "Alquimista": [
        {"id": "chimera", "name": "Chimera", "type": "summon_chimera", "cooldown": 99, "starts_cd": 3, "once": True, "desc": "Invoca 1 quimera."},
    ],

    "Chimera Comum": [
        {"id": "morteiro_quimico", "name": "Morteiro Quimico", "type": "mortar", "range": 99, "bonus": 18, "radius": 1, "cooldown": 3, "ignore_los": True, "desc": "Mapa todo."},
        {"id": "rugido_torto", "name": "Rugido Torto", "type": "mark", "range": 4, "vulnerability": 0.30, "duration": 2, "cooldown": 3, "desc": "Enfraquece."},
    ],

    "Chimera Rara": [
        {"id": "morteiro_acido", "name": "Morteiro Acido", "type": "mortar", "range": 99, "bonus": 24, "radius": 1, "cooldown": 3, "ignore_los": True, "desc": "Mapa todo."},
        {"id": "mutacao_agressiva", "name": "Mutacao Agressiva", "type": "buff", "cooldown": 4, "duration": 2, "atk_bonus": 10, "desc": "ATK sobe."},
    ],

    "Chimera Lendaria": [
        {"id": "morteiro_apex", "name": "Morteiro Apex", "type": "mortar", "range": 99, "bonus": 34, "radius": 1, "cooldown": 3, "ignore_los": True, "desc": "Mapa todo."},
        {"id": "rugido_da_coroa", "name": "Rugido da Coroa", "type": "mark", "range": 99, "vulnerability": 0.50, "duration": 2, "cooldown": 4, "ignore_los": True, "desc": "Marca longe."},
    ],

    "Chimera Planta": [
        {"id": "armadilhas_vivas", "name": "Armadilhas Vivas", "type": "traps", "cooldown": 4, "count": 7, "desc": "Espalha bombas."},
        {"id": "jardim_monstruoso", "name": "Jardim Monstruoso", "type": "summon_plants", "cooldown": 5, "desc": "Invoca plantas."},
        {"id": "laser_clorofila", "name": "Laser de Clorofila", "type": "laser", "range": 99, "bonus": 32, "cooldown": 4, "ignore_los": True, "desc": "Linha ate o fim."},
    ],

    "Dragao de Planta": [
        {"id": "laminas_de_vento", "name": "Laminas de Vento", "type": "aoe", "range": 4, "bonus": 24, "radius": 1, "cooldown": 3, "desc": "Vento cortante."},
        {"id": "laser_verde", "name": "Laser Verde", "type": "laser", "range": 99, "bonus": 28, "cooldown": 4, "ignore_los": True, "desc": "Linha longa."},
    ],
}# =========================================================
# DADOS DAS UNIDADES
# =========================================================
CLASS_DATA = {
    "Cavaleiro": {"hp": 135, "atk": 24, "move": 3, "range": 1, "color": BLUE, "role": "Tanque", "ai": "none", "personality": "Orgulhoso, protetor e teimoso."},
    "Arqueiro": {"hp": 90, "atk": 18, "move": 4, "range": 4, "color": CYAN, "role": "Distancia", "ai": "none", "personality": "Calmo demais. Isso irrita."},
    "Mago": {"hp": 80, "atk": 23, "move": 3, "range": 3, "color": PURPLE, "role": "Magia", "ai": "none", "personality": "Dramatico e perigoso."},
    "Lanceiro": {"hp": 115, "atk": 22, "move": 4, "range": 1, "color": (95, 160, 255), "role": "Ofensivo", "ai": "none", "personality": "Impaciente e direto."},
    "Clerigo": {"hp": 92, "atk": 15, "move": 3, "range": 3, "color": (245, 230, 130), "role": "Suporte", "ai": "none", "personality": "Gentil, mas julga em silencio."},
    "Ladino": {"hp": 82, "atk": 28, "move": 5, "range": 1, "color": (110, 110, 135), "role": "Rapido", "ai": "none", "personality": "Sorri quando nao devia."},
    "Paladino": {"hp": 155, "atk": 29, "move": 3, "range": 1, "color": (255, 210, 90), "role": "Epico", "ai": "none", "personality": "Heroico ate irritar."},
    "Necromante": {"hp": 86, "atk": 31, "move": 3, "range": 4, "color": (105, 70, 150), "role": "Epico", "ai": "none", "personality": "Educado e macabro."},
    "Arquimago": {"hp": 115, "atk": 39, "move": 3, "range": 5, "color": (255, 120, 255), "role": "Lendario", "ai": "none", "personality": "Arrogante com motivo."},
    "Dragoon": {"hp": 172, "atk": 37, "move": 4, "range": 2, "color": (255, 120, 80), "role": "Lendario", "ai": "none", "personality": "Explosivo e nobre."},
    "Guardiao Solar": {"hp": 220, "atk": 33, "move": 3, "range": 1, "color": (255, 235, 80), "role": "Lendario", "ai": "none", "personality": "Calmo. Queima tudo."},
    "Oraculo do Caos": {"hp": 125, "atk": 36, "move": 3, "range": 5, "color": (230, 90, 255), "role": "Lendario", "ai": "none", "personality": "Fala em enigmas so para irritar."},

    "Mestre das Sombras": {"hp": 70, "atk": 12, "move": 3, "range": 3, "color": (45, 25, 75), "role": "Mercado Negro", "ai": "none", "personality": "Fraco sozinho. Covarde? Nao. Estrategico."},
    "Alquimista": {"hp": 68, "atk": 11, "move": 3, "range": 3, "color": (90, 190, 110), "role": "Mercado Negro", "ai": "none", "personality": "Parece inofensivo. Essa e a mentira.", "normal_aoe": 1},

    "Lacaio Sombrio": {"hp": 38, "atk": 14, "move": 4, "range": 1, "color": (80, 45, 120), "role": "Invocado", "ai": "none"},
    "Dragao de Sombras": {"hp": 170, "atk": 58, "move": 2, "range": 99, "color": (25, 10, 35), "role": "Invocado", "ai": "none", "ignore_los": True, "normal_aoe": 1},

    "Chimera Comum": {"hp": 90, "atk": 24, "move": 3, "range": 3, "color": (120, 210, 120), "role": "Invocado", "ai": "none", "normal_aoe": 1, "zombie_on_kill": True},
    "Chimera Rara": {"hp": 118, "atk": 31, "move": 4, "range": 4, "color": (90, 180, 255), "role": "Invocado", "ai": "none", "normal_aoe": 1, "zombie_on_kill": True},
    "Chimera Lendaria": {"hp": 155, "atk": 43, "move": 4, "range": 99, "color": (255, 210, 80), "role": "Invocado", "ai": "none", "ignore_los": True, "normal_aoe": 1, "zombie_on_kill": True},
    "Chimera Planta": {"hp": 165, "atk": 39, "move": 0, "range": 99, "color": (35, 130, 45), "role": "Mercado Negro", "ai": "none", "ignore_los": True, "normal_aoe": 1},

    "Zumbi Aliado": {"hp": 48, "atk": 13, "move": 2, "range": 1, "color": (90, 130, 90), "role": "Invocado", "ai": "none"},
    "Zumbi Planta": {"hp": 55, "atk": 14, "move": 2, "range": 1, "color": (70, 150, 70), "role": "Invocado", "ai": "none"},
    "Golem de Madeira": {"hp": 145, "atk": 23, "move": 2, "range": 1, "color": (130, 85, 45), "role": "Invocado", "ai": "none"},
    "Dragao de Planta": {"hp": 155, "atk": 36, "move": 3, "range": 4, "color": (60, 190, 80), "role": "Invocado", "ai": "none"},

    "Goblin": {"hp": 55, "atk": 11, "move": 3, "range": 1, "color": RED, "role": "Melee", "ai": "melee"},
    "Arqueiro Goblin": {"hp": 48, "atk": 14, "move": 3, "range": 4, "color": LIGHT_RED, "role": "Atirador", "ai": "ranged"},
    "Xama": {"hp": 62, "atk": 17, "move": 2, "range": 3, "color": PURPLE, "role": "Magia tribal", "ai": "ranged"},
    "Ogro": {"hp": 145, "atk": 25, "move": 2, "range": 1, "color": ORANGE, "role": "Bruto", "ai": "brute"},
    "Chefe Ogro": {"hp": 300, "atk": 32, "move": 2, "range": 1, "color": DARK_RED, "role": "Boss", "ai": "boss"},
}

HERO_SHOP_DATA = {
    "Lanceiro": {"rarity": "Comum", "price": 120},
    "Clerigo": {"rarity": "Raro", "price": 220},
    "Ladino": {"rarity": "Raro", "price": 240},
    "Paladino": {"rarity": "Epico", "price": 420},
    "Necromante": {"rarity": "Epico", "price": 450},
    "Arquimago": {"rarity": "Lendario", "price": 850},
    "Dragoon": {"rarity": "Lendario", "price": 900},
    "Guardiao Solar": {"rarity": "Lendario", "price": 1000},
    "Oraculo do Caos": {"rarity": "Lendario", "price": 1200},
    "Mestre das Sombras": {"rarity": "Mercado Negro", "price": 1800},
    "Alquimista": {"rarity": "Mercado Negro", "price": 2000},
}


# =========================================================
# GERACAO DE MAPA
# =========================================================
def flood_fill_walkable(game_map, start):
    visited = {start}
    q = deque([start])

    while q:
        x, y = q.popleft()

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx = x + dx
            ny = y + dy

            if not in_bounds(nx, ny):
                continue
            if (nx, ny) in visited:
                continue
            if not is_floor_cell(game_map[ny][nx]):
                continue

            visited.add((nx, ny))
            q.append((nx, ny))

    return visited


def paint_disc(game_map, cx, cy, rx, ry, cell):
    for y in range(cy - ry - 1, cy + ry + 2):
        for x in range(cx - rx - 1, cx + rx + 2):
            if not in_bounds(x, y):
                continue

            dx = (x - cx) / max(1, rx)
            dy = (y - cy) / max(1, ry)

            if dx * dx + dy * dy <= 1.0:
                game_map[y][x] = cell


def paint_rect(game_map, x1, y1, x2, y2, cell):
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if in_bounds(x, y):
                game_map[y][x] = cell


def paint_path(game_map, points, width=1):
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i + 1]
        x, y = x1, y1

        while x != x2:
            for wy in range(-width, width + 1):
                for wx in range(-width, width + 1):
                    nx = x + wx
                    ny = y + wy
                    if in_bounds(nx, ny):
                        game_map[ny][nx] = PATH_TILE
            x += 1 if x2 > x else -1

        while y != y2:
            for wy in range(-width, width + 1):
                for wx in range(-width, width + 1):
                    nx = x + wx
                    ny = y + wy
                    if in_bounds(nx, ny):
                        game_map[ny][nx] = PATH_TILE
            y += 1 if y2 > y else -1

        for wy in range(-width, width + 1):
            for wx in range(-width, width + 1):
                nx = x + wx
                ny = y + wy
                if in_bounds(nx, ny):
                    game_map[ny][nx] = PATH_TILE


def can_place_obstacle(game_map, x, y):
    original = game_map[y][x]

    if not is_floor_cell(original):
        return False

    game_map[y][x] = OBSTACLE
    floors = [(fx, fy) for fy in range(MAP_H) for fx in range(MAP_W) if is_floor_cell(game_map[fy][fx])]

    if not floors:
        game_map[y][x] = original
        return False

    region = flood_fill_walkable(game_map, floors[0])
    ok = len(region) >= len(floors) * 0.96

    game_map[y][x] = original
    return ok


def place_cover_pattern(game_map, cx, cy, pattern):
    positions = []

    for ox, oy in pattern:
        x = cx + ox
        y = cy + oy

        if not in_bounds(x, y):
            return
        if not is_floor_cell(game_map[y][x]):
            return

        positions.append((x, y))

    placed = []

    for x, y in positions:
        if not can_place_obstacle(game_map, x, y):
            for px, py, old in placed:
                game_map[py][px] = old
            return

        placed.append((x, y, game_map[y][x]))
        game_map[y][x] = OBSTACLE


def add_water_border_pattern(game_map):
    patches = [
        (2, 2, 3, 1),
        (21, 2, 2, 2),
        (2, 13, 2, 2),
        (21, 13, 3, 1),
    ]

    random.shuffle(patches)

    for cx, cy, rx, ry in patches[:random.randint(2, 4)]:
        for y in range(cy - ry, cy + ry + 1):
            for x in range(cx - rx, cx + rx + 1):
                if not in_bounds(x, y):
                    continue
                if 5 <= x <= MAP_W - 6 and 4 <= y <= MAP_H - 5:
                    continue

                dx = (x - cx) / max(1, rx)
                dy = (y - cy) / max(1, ry)

                if dx * dx + dy * dy <= 1.1:
                    if game_map[y][x] in (VOID, FLOOR):
                        game_map[y][x] = WATER_TILE


def clear_spawn_areas(game_map):
    center_y = MAP_H // 2

    paint_disc(game_map, 4, center_y, 3, 3, FLOOR)
    paint_path(game_map, [(2, center_y), (7, center_y)], width=1)

    paint_disc(game_map, MAP_W - 5, center_y, 3, 3, FLOOR)
    paint_path(game_map, [(MAP_W - 8, center_y), (MAP_W - 3, center_y)], width=1)

    for cx, cy in [(4, center_y), (MAP_W - 5, center_y)]:
        for y in range(cy - 2, cy + 3):
            for x in range(cx - 2, cx + 3):
                if in_bounds(x, y) and game_map[y][x] == OBSTACLE:
                    game_map[y][x] = FLOOR


def generate_random_map():
    game_map = [[VOID for _ in range(MAP_W)] for _ in range(MAP_H)]
    center_y = MAP_H // 2

    paint_rect(game_map, 2, 2, MAP_W - 3, MAP_H - 3, FLOOR)

    for x in range(MAP_W):
        game_map[0][x] = VOID
        game_map[MAP_H - 1][x] = VOID

    for y in range(MAP_H):
        game_map[y][0] = VOID
        game_map[y][MAP_W - 1] = VOID

    corner_cuts = [
        (1, 1), (2, 1), (1, 2),
        (MAP_W - 2, 1), (MAP_W - 3, 1), (MAP_W - 2, 2),
        (1, MAP_H - 2), (2, MAP_H - 2), (1, MAP_H - 3),
        (MAP_W - 2, MAP_H - 2), (MAP_W - 3, MAP_H - 2), (MAP_W - 2, MAP_H - 3),
    ]

    for x, y in corner_cuts:
        if in_bounds(x, y):
            game_map[y][x] = VOID

    paint_disc(game_map, 4, center_y, 3, 3, FLOOR)
    paint_disc(game_map, MAP_W - 5, center_y, 3, 3, FLOOR)
    paint_disc(game_map, MAP_W // 2, center_y, 5, 4, FLOOR)
    paint_disc(game_map, MAP_W // 2, 4, 3, 2, FLOOR)
    paint_disc(game_map, MAP_W // 2, MAP_H - 5, 3, 2, FLOOR)

    paint_path(game_map, [(3, center_y), (8, center_y), (12, center_y), (16, center_y), (MAP_W - 4, center_y)], width=1)
    paint_path(game_map, [(12, center_y), (12, 4)], width=1)
    paint_path(game_map, [(12, center_y), (12, MAP_H - 5)], width=1)

    if random.random() < 0.5:
        paint_path(game_map, [(7, center_y - 2), (11, center_y - 2), (14, center_y)], width=0)

    if random.random() < 0.5:
        paint_path(game_map, [(16, center_y + 2), (13, center_y + 2), (10, center_y)], width=0)

    add_water_border_pattern(game_map)

    cover_patterns = [
        [(0, 0)],
        [(0, 0), (1, 0)],
        [(0, 0), (0, 1)],
        [(0, 0), (1, 0), (0, 1)],
        [(0, 0), (-1, 0), (1, 0)],
        [(0, 0), (0, -1), (0, 1)],
    ]

    cover_spots = [
        (7, center_y - 2), (7, center_y + 2),
        (10, center_y - 3), (10, center_y + 3),
        (14, center_y - 3), (14, center_y + 3),
        (17, center_y - 2), (17, center_y + 2),
        (12, 5), (12, MAP_H - 6),
        (5, 4), (MAP_W - 6, 4),
        (5, MAP_H - 5), (MAP_W - 6, MAP_H - 5),
    ]

    random.shuffle(cover_spots)

    for cx, cy in cover_spots:
        place_cover_pattern(game_map, cx, cy, random.choice(cover_patterns))

    clear_spawn_areas(game_map)

    floors = [(x, y) for y in range(MAP_H) for x in range(MAP_W) if is_floor_cell(game_map[y][x])]

    if floors:
        region = flood_fill_walkable(game_map, floors[0])
        if len(region) < len(floors) * 0.95:
            return generate_random_map()

    return game_map


# =========================================================
# CLASSE UNIT
# =========================================================
class Unit:
    def __init__(self, class_name, team, x, y, level=1, boss=False, summoned=False):
        data = CLASS_DATA[class_name]

        self.name = class_name
        self.team = team

        self.x = x
        self.y = y
        self.draw_x = x * TILE
        self.draw_y = y * TILE

        self.color = data["color"]
        self.role = data.get("role", "")
        self.ai = data.get("ai", "none")
        self.personality = data.get("personality", "")

        self.is_boss = boss
        self.summoned = summoned

        self.ignore_los = data.get("ignore_los", False)
        self.normal_aoe = data.get("normal_aoe", 0)
        self.zombie_on_kill = data.get("zombie_on_kill", False)

        stage = ((level - 1) % 5) + 1
        cycle = (level - 1) // 5

        base_hp = data["hp"]
        base_atk = data["atk"]

        if team == "player":
            growth = 0 if summoned else level // 3
            self.max_hp = base_hp + growth * 10
            self.atk = base_atk + growth * 2
        else:
            self.max_hp = base_hp + cycle * 22 + (stage - 1) * 5
            self.atk = base_atk + cycle * 3 + (stage - 1)

            if boss:
                self.max_hp += cycle * 70
                self.atk += cycle * 5

        self.hp = self.max_hp
        self.move_range = data["move"]
        self.atk_range = data["range"]

        self.alive = True
        self.actions_left = 2
        self.moved = False
        self.attacked = False

        self.move_path = []
        self.is_moving = False
        self.move_speed = 260

        self.effects = {}
        self.cooldowns = {}
        self.used_once = set()

        for ability in ABILITY_DATA.get(self.name, []):
            self.cooldowns[ability["id"]] = ability.get("starts_cd", 0)

    def current_atk(self):
        return self.atk + self.effects.get("atk_bonus", 0)

    def reset_turn(self):
        self.actions_left = 2
        self.moved = False
        self.attacked = False

    def has_actions(self):
        return self.actions_left > 0

    def spend_action(self):
        if self.actions_left <= 0:
            return False

        self.actions_left -= 1
        return True

    def tick_cooldowns(self):
        for key in list(self.cooldowns.keys()):
            if self.cooldowns[key] > 0:
                self.cooldowns[key] -= 1

    def tick_effects(self):
        self._tick_effect("shield_turns", "shield_reduction")
        self._tick_effect("vulnerable_turns", "vulnerability")
        self._tick_effect("atk_bonus_turns", "atk_bonus")

    def _tick_effect(self, turn_key, value_key):
        if self.effects.get(turn_key, 0) <= 0:
            return

        self.effects[turn_key] -= 1

        if self.effects[turn_key] <= 0:
            self.effects.pop(turn_key, None)
            self.effects.pop(value_key, None)

    def has_shield(self):
        return self.effects.get("shield_turns", 0) > 0

    def is_vulnerable(self):
        return self.effects.get("vulnerable_turns", 0) > 0

    def has_atk_buff(self):
        return self.effects.get("atk_bonus_turns", 0) > 0

    def heal(self, amount):
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp

    def take_damage(self, damage):
        final_damage = damage

        if self.has_shield():
            final_damage = max(1, int(final_damage * (1 - self.effects.get("shield_reduction", 0))))

        if self.is_vulnerable():
            final_damage = max(1, int(final_damage * (1 + self.effects.get("vulnerability", 0))))

        self.hp -= final_damage

        if self.hp <= 0:
            self.hp = 0
            self.alive = False

        return final_damage

    def start_path(self, path):
        self.move_path = path[:]
        self.is_moving = len(self.move_path) > 0

    def update_animation(self, dt):
        if not self.alive or not self.is_moving:
            return False

        if not self.move_path:
            self.is_moving = False
            return True

        tx, ty = self.move_path[0]
        target_x = tx * TILE
        target_y = ty * TILE

        dx = target_x - self.draw_x
        dy = target_y - self.draw_y
        distance = (dx * dx + dy * dy) ** 0.5
        step = self.move_speed * dt

        if distance <= step or distance == 0:
            self.draw_x = target_x
            self.draw_y = target_y
            self.x = tx
            self.y = ty
            self.move_path.pop(0)

            if not self.move_path:
                self.is_moving = False
                return True

            return False

        self.draw_x += (dx / distance) * step
        self.draw_y += (dy / distance) * step
        return False

    def draw(self, surf, selected=False):
        px = int(self.draw_x)
        py = int(self.draw_y)

        big_body = self.is_boss or "Dragao" in self.name

        if big_body:
            shadow = pygame.Rect(px + 3, py + 3, TILE - 6, TILE - 6)
            body = pygame.Rect(px + 1, py + 1, TILE - 2, TILE - 2)
        else:
            shadow = pygame.Rect(px + 6, py + 6, TILE - 12, TILE - 12)
            body = pygame.Rect(px + 4, py + 4, TILE - 8, TILE - 8)

        pygame.draw.rect(surf, BLACK, shadow, border_radius=8)
        pygame.draw.rect(surf, self.color, body, border_radius=8)
        pygame.draw.rect(surf, BLACK, body, 2, border_radius=8)

        if self.has_shield():
            pygame.draw.rect(surf, SHIELD_COLOR, body.inflate(7, 7), 3, border_radius=12)

        if self.is_vulnerable():
            pygame.draw.rect(surf, SKILL_COLOR, body.inflate(9, 9), 2, border_radius=12)

        if self.has_atk_buff():
            pygame.draw.rect(surf, GOLD, body.inflate(5, 5), 2, border_radius=12)

        if self.is_boss:
            pygame.draw.rect(surf, YELLOW, body, 3, border_radius=8)

        if selected:
            pygame.draw.rect(surf, SELECT_COLOR, body.inflate(6, 6), 3, border_radius=12)

        hp_percent = self.hp / self.max_hp
        bar_bg = pygame.Rect(px + 4, py + 1, TILE - 8, 5)
        bar_fg = pygame.Rect(px + 4, py + 1, int((TILE - 8) * hp_percent), 5)

        pygame.draw.rect(surf, HP_RED_BG, bar_bg, border_radius=2)
        pygame.draw.rect(surf, HP_GREEN, bar_fg, border_radius=2)

        letter = "D" if "Dragao" in self.name else self.name[0]
        txt = tiny_font.render(letter, True, WHITE)
        surf.blit(txt, txt.get_rect(center=body.center))# =========================================================
# CLASSE GAME
# =========================================================
class Game:
    def __init__(self):
        self.level = 1
        self.gold = 180
        self.infinite_gold = False
        self.god_mode = False

        self.party_names = ["Cavaleiro", "Arqueiro", "Mago"]

        self.mode = "battle"
        self.shop_items = []
        self.pending_purchase = None

        self.console_open = False
        self.console_text = ""
        self.console_log = ["F1 abre/fecha console dev. Digite help."]

        self.traps = []

        self.reset_level(self.level)

    # =====================================================
    # CAMPANHA
    # =====================================================
    def get_stage(self):
        return ((self.level - 1) % 5) + 1

    def get_cycle(self):
        return ((self.level - 1) // 5) + 1

    def enemy_names_for_level(self):
        stage = self.get_stage()

        if stage == 1:
            return ["Goblin", "Goblin", "Arqueiro Goblin"]
        if stage == 2:
            return ["Goblin", "Goblin", "Arqueiro Goblin", "Xama"]
        if stage == 3:
            return ["Goblin", "Goblin", "Arqueiro Goblin", "Xama", "Ogro"]
        if stage == 4:
            return ["Goblin", "Goblin", "Arqueiro Goblin", "Arqueiro Goblin", "Xama", "Ogro"]

        return ["Chefe Ogro", "Goblin", "Arqueiro Goblin", "Xama"]

    def level_reward(self):
        reward = 70 + self.level * 18

        if self.get_stage() == 5:
            reward += 90

        return reward

    def reset_campaign(self):
        self.level = 1
        self.gold = 180
        self.infinite_gold = False
        self.god_mode = False
        self.party_names = ["Cavaleiro", "Arqueiro", "Mago"]
        self.mode = "battle"
        self.shop_items = []
        self.pending_purchase = None
        self.reset_level(self.level)

    def retry_level(self):
        self.mode = "battle"
        self.pending_purchase = None
        self.reset_level(self.level)

    def next_level(self, amount=1):
        self.level = max(1, self.level + amount)
        self.mode = "battle"
        self.shop_items = []
        self.pending_purchase = None
        self.reset_level(self.level)

    def give_reward_once(self):
        if self.reward_given:
            return

        reward = self.level_reward()
        self.gold += reward
        self.reward_given = True

        self.message = f"Vitoria! +{reward} ouro."

        if self.level % 3 == 0:
            self.message += " Loja liberada! ENTER para abrir."
        else:
            self.message += " ENTER para proximo nivel."

    def reset_level(self, level):
        self.map = generate_random_map()

        self.turn = "player"
        self.selected = None
        self.skill_targeting = None
        self.message = f"Nivel {self.level} iniciado"
        self.winner = None
        self.reward_given = False
        self.animating = False
        self.traps = []

        self.enemy_turn_queue = []
        self.enemy_state = "idle"
        self.current_enemy = None
        self.enemy_action_timer = 0

        enemy_names = self.enemy_names_for_level()
        spawn_data = self.choose_spawns(len(self.party_names), len(enemy_names))

        self.players = []
        self.enemies = []

        for i, hero_name in enumerate(self.party_names):
            x, y = spawn_data["players"][i]
            self.players.append(Unit(hero_name, "player", x, y, self.level))

        for i, enemy_name in enumerate(enemy_names):
            x, y = spawn_data["enemies"][i]
            is_boss = enemy_name == "Chefe Ogro"
            self.enemies.append(Unit(enemy_name, "enemy", x, y, self.level, boss=is_boss))

    # =====================================================
    # LOJA
    # =====================================================
    def generate_shop_items(self):
        available = [name for name in HERO_SHOP_DATA if name not in self.party_names]

        if not available:
            return []

        weights = {
            "Comum": 50,
            "Raro": 28,
            "Epico": 14,
            "Lendario": 7 + self.get_cycle() * 2,
            "Mercado Negro": 2 + self.get_cycle(),
        }

        result = []

        while available and len(result) < 4:
            total = sum(weights[HERO_SHOP_DATA[name]["rarity"]] for name in available)
            roll = random.randint(1, total)
            acc = 0
            chosen = available[0]

            for name in available:
                rarity = HERO_SHOP_DATA[name]["rarity"]
                acc += weights[rarity]

                if roll <= acc:
                    chosen = name
                    break

            result.append(chosen)
            available.remove(chosen)

        return result

    def open_shop(self):
        self.mode = "shop"
        self.selected = None
        self.skill_targeting = None
        self.pending_purchase = None
        self.shop_items = self.generate_shop_items()
        self.message = "Loja aberta. 1/2/3/4 compra. ENTER segue."

    def can_afford(self, name):
        return self.infinite_gold or self.gold >= HERO_SHOP_DATA[name]["price"]

    def pay_for(self, name):
        if self.infinite_gold:
            return True

        price = HERO_SHOP_DATA[name]["price"]

        if self.gold < price:
            return False

        self.gold -= price
        return True

    def buy_shop_item(self, index):
        if self.mode != "shop":
            return
        if index < 0 or index >= len(self.shop_items):
            return

        name = self.shop_items[index]

        if name in self.party_names:
            self.message = f"{name} ja esta no grupo."
            return

        if not self.can_afford(name):
            self.message = f"Ouro insuficiente para comprar {name}."
            return

        if len(self.party_names) >= MAX_PARTY_SIZE:
            self.pending_purchase = name
            self.message = f"Equipe cheia. Escolha 1-{MAX_PARTY_SIZE} para trocar por {name}."
            return

        if not self.pay_for(name):
            self.message = f"Ouro insuficiente para comprar {name}."
            return

        self.party_names.append(name)
        self.shop_items.pop(index)
        self.message = f"{name} entrou no grupo!"

    def replace_party_member(self, index):
        if self.mode != "shop" or self.pending_purchase is None:
            return
        if index < 0 or index >= len(self.party_names):
            return

        new_name = self.pending_purchase

        if not self.can_afford(new_name):
            self.message = f"Ouro insuficiente para comprar {new_name}."
            self.pending_purchase = None
            return

        old_name = self.party_names[index]

        if not self.pay_for(new_name):
            self.message = f"Ouro insuficiente para comprar {new_name}."
            self.pending_purchase = None
            return

        self.party_names[index] = new_name

        if new_name in self.shop_items:
            self.shop_items.remove(new_name)

        self.pending_purchase = None
        self.message = f"{old_name} saiu. {new_name} entrou no grupo."

    def cancel_purchase(self):
        if self.pending_purchase:
            self.message = f"Compra de {self.pending_purchase} cancelada."
            self.pending_purchase = None

    # =====================================================
    # CONSOLE HACKER
    # =====================================================
    def console_print(self, text):
        self.console_log.append(text)
        self.console_log = self.console_log[-6:]

    def toggle_console(self):
        self.console_open = not self.console_open
        self.console_text = ""

    def execute_console_command(self, command):
        command = command.strip()

        if not command:
            return

        self.console_print("> " + command)

        parts = command.split()
        cmd = parts[0].lower()

        if cmd == "help":
            self.console_print("gold [N] | infgold | heal | revive | next N")
            self.console_print("level N | win | kill | shop | add Nome [slot]")
            self.console_print("ap | cd | god | party")
            return

        if cmd in ("gold", "money", "ouro"):
            if len(parts) == 1:
                self.gold = 9999
                self.console_print("Ouro definido para 9999.")
                return

            value = parts[1].lower()

            if value in ("inf", "infinite", "infinito"):
                self.infinite_gold = True
                self.console_print("Ouro infinito ativado.")
                return

            try:
                self.gold = int(value)
                self.console_print(f"Ouro definido para {self.gold}.")
            except ValueError:
                self.console_print("Uso: gold ou gold 9999")
            return

        if cmd in ("infgold", "infinitegold"):
            self.infinite_gold = not self.infinite_gold
            self.console_print(f"Ouro infinito: {'ON' if self.infinite_gold else 'OFF'}")
            return

        if cmd == "god":
            self.god_mode = not self.god_mode
            self.console_print(f"God mode: {'ON' if self.god_mode else 'OFF'}")
            return

        if cmd == "heal":
            for unit in self.players:
                if unit.alive:
                    unit.hp = unit.max_hp
            self.console_print("Herois curados.")
            return

        if cmd == "revive":
            for unit in self.players:
                unit.alive = True
                unit.hp = unit.max_hp
            self.winner = None
            self.console_print("Herois revividos.")
            return

        if cmd == "ap":
            for unit in self.players:
                if unit.alive:
                    unit.actions_left = 2
                    unit.moved = False
                    unit.attacked = False
            self.console_print("AP restaurado.")
            return

        if cmd == "cd":
            for unit in self.players:
                for key in unit.cooldowns:
                    unit.cooldowns[key] = 0
            self.console_print("Cooldowns zerados.")
            return

        if cmd == "next":
            amount = 1

            if len(parts) >= 2:
                try:
                    amount = int(parts[1])
                except ValueError:
                    amount = 1

            self.next_level(amount)
            self.console_print(f"Pulou {amount} nivel(is).")
            return

        if cmd == "level":
            if len(parts) < 2:
                self.console_print("Uso: level 10")
                return

            try:
                self.level = max(1, int(parts[1]))
                self.mode = "battle"
                self.reset_level(self.level)
                self.console_print(f"Nivel definido para {self.level}.")
            except ValueError:
                self.console_print("Uso: level 10")
            return

        if cmd in ("win", "kill"):
            for enemy in self.enemies:
                enemy.alive = False
                enemy.hp = 0
            self.check_winner()
            self.console_print("Vitoria forcada.")
            return

        if cmd == "shop":
            self.open_shop()
            self.console_print("Loja aberta.")
            return

        if cmd == "party":
            self.console_print("Grupo: " + ", ".join(self.party_names))
            return

        if cmd == "add":
            self.console_add_character(parts)
            return

        self.console_print("Comando desconhecido. Digite help.")

    def console_add_character(self, parts):
        if len(parts) < 2:
            self.console_print("Uso: add Alquimista ou add Mestre das Sombras 2")
            return

        slot_index = None
        name_parts = parts[1:]

        if name_parts[-1].isdigit():
            slot_index = int(name_parts[-1]) - 1
            name_parts = name_parts[:-1]

        wanted = " ".join(name_parts).lower()
        found = None

        for name in HERO_SHOP_DATA:
            if name.lower() == wanted:
                found = name
                break

        if found is None:
            self.console_print("Heroi nao encontrado.")
            return

        if found in self.party_names:
            self.console_print(f"{found} ja esta no grupo.")
            return

        if len(self.party_names) < MAX_PARTY_SIZE:
            self.party_names.append(found)
            self.reset_level(self.level)
            self.console_print(f"{found} adicionado.")
            return

        if slot_index is None or slot_index < 0 or slot_index >= len(self.party_names):
            slot_index = 0

        old = self.party_names[slot_index]
        self.party_names[slot_index] = found
        self.reset_level(self.level)
        self.console_print(f"{old} trocado por {found}.")

    def handle_console_event(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_F1, pygame.K_BACKQUOTE):
            self.toggle_console()
            return

        if event.key == pygame.K_ESCAPE:
            self.console_open = False
            return

        if event.key == pygame.K_RETURN:
            text = self.console_text
            self.console_text = ""
            self.execute_console_command(text)
            return

        if event.key == pygame.K_BACKSPACE:
            self.console_text = self.console_text[:-1]
            return

        if event.unicode and len(self.console_text) < 80:
            self.console_text += event.unicode

    # =====================================================
    # UNIDADES / MAPA
    # =====================================================
    def all_units(self):
        return self.players + self.enemies

    def living_players(self):
        return [unit for unit in self.players if unit.alive]

    def living_enemies(self):
        return [unit for unit in self.enemies if unit.alive]

    def get_floor_positions(self):
        return [(x, y) for y in range(MAP_H) for x in range(MAP_W) if is_floor_cell(self.map[y][x])]

    def unit_at(self, x, y):
        if not hasattr(self, "players") or not hasattr(self, "enemies"):
            return None

        for unit in self.all_units():
            if unit.alive and unit.x == x and unit.y == y:
                return unit

        return None

    def walkable(self, x, y):
        return in_bounds(x, y) and is_floor_cell(self.map[y][x])

    def blocked(self, x, y, ignore=None):
        if not self.walkable(x, y):
            return True

        unit = self.unit_at(x, y)

        return unit is not None and unit != ignore

    def dist_pos(self, x1, y1, x2, y2):
        return abs(x1 - x2) + abs(y1 - y2)

    def dist(self, a, b):
        return self.dist_pos(a.x, a.y, b.x, b.y)

    def any_unit_moving(self):
        return any(unit.is_moving for unit in self.all_units() if unit.alive)

    def choose_spawns(self, player_count, enemy_count):
        floor_positions = self.get_floor_positions()

        player_base = (4, MAP_H // 2)
        enemy_base = (MAP_W - 5, MAP_H // 2)

        players = self.find_nearby_floor_tiles(player_base, player_count, 1)
        enemies = self.find_nearby_floor_tiles(enemy_base, enemy_count, 1)

        if len(players) < player_count or len(enemies) < enemy_count:
            random.shuffle(floor_positions)
            return {
                "players": floor_positions[:player_count],
                "enemies": floor_positions[player_count:player_count + enemy_count],
            }

        return {"players": players, "enemies": enemies}

    def find_nearby_floor_tiles(self, center, count, min_dist_between=1):
        cx, cy = center
        candidates = []

        for radius in range(0, 14):
            for y in range(cy - radius, cy + radius + 1):
                for x in range(cx - radius, cx + radius + 1):
                    if not in_bounds(x, y):
                        continue
                    if not self.walkable(x, y):
                        continue
                    if self.unit_at(x, y) is not None:
                        continue
                    if (x, y) not in candidates:
                        candidates.append((x, y))

            if len(candidates) >= count * 3:
                break

        chosen = []

        for pos in candidates:
            valid = True

            for other in chosen:
                if self.dist_pos(pos[0], pos[1], other[0], other[1]) <= min_dist_between:
                    valid = False
                    break

            if valid:
                chosen.append(pos)

            if len(chosen) >= count:
                break

        return chosen

    def find_empty_near(self, x, y, radius=4):
        spots = []

        for r in range(1, radius + 1):
            for yy in range(y - r, y + r + 1):
                for xx in range(x - r, x + r + 1):
                    if not in_bounds(xx, yy):
                        continue
                    if not self.walkable(xx, yy):
                        continue
                    if self.unit_at(xx, yy) is not None:
                        continue
                    spots.append((xx, yy))

            if spots:
                return random.choice(spots)

        return None

    def random_empty_floor(self):
        spots = [
            (x, y)
            for y in range(MAP_H)
            for x in range(MAP_W)
            if self.walkable(x, y) and self.unit_at(x, y) is None
        ]

        if not spots:
            return None

        return random.choice(spots)

    def summon_unit(self, name, x, y, near_target=None):
        if near_target:
            spot = self.find_empty_near(near_target[0], near_target[1], 4)
        else:
            spot = self.find_empty_near(x, y, 4)

        if spot is None:
            return None

        sx, sy = spot
        unit = Unit(name, "player", sx, sy, self.level, summoned=True)
        self.players.append(unit)
        return unit

    # =====================================================
    # LINHA DE VISAO / ALCANCE
    # =====================================================
    def line_of_sight(self, x1, y1, x2, y2):
        if self.dist_pos(x1, y1, x2, y2) <= 1:
            return True

        steps = max(abs(x2 - x1), abs(y2 - y1)) * 8

        if steps <= 0:
            return True

        start_x = x1 + 0.5
        start_y = y1 + 0.5
        end_x = x2 + 0.5
        end_y = y2 + 0.5

        for i in range(1, steps):
            t = i / steps
            px = start_x + (end_x - start_x) * t
            py = start_y + (end_y - start_y) * t

            gx = int(px)
            gy = int(py)

            if (gx, gy) in [(x1, y1), (x2, y2)]:
                continue
            if not in_bounds(gx, gy):
                return False
            if not is_floor_cell(self.map[gy][gx]):
                return False

        return True

    def can_attack_pos(self, attacker, tx, ty, from_x=None, from_y=None):
        ax = attacker.x if from_x is None else from_x
        ay = attacker.y if from_y is None else from_y

        if self.dist_pos(ax, ay, tx, ty) > attacker.atk_range:
            return False

        if attacker.ignore_los or attacker.atk_range >= 99:
            return True

        if attacker.atk_range <= 1:
            return True

        return self.line_of_sight(ax, ay, tx, ty)

    def can_attack(self, attacker, target):
        if not attacker.alive or not target.alive:
            return False

        return self.can_attack_pos(attacker, target.x, target.y)

    def ability_can_reach_tile(self, caster, x, y, ability):
        ability_range = ability.get("range", 0)
        ability_type = ability["type"]

        if not self.walkable(x, y):
            return False

        if ability_range < 99 and self.dist_pos(caster.x, caster.y, x, y) > ability_range:
            return False

        if ability.get("ignore_los") or ability_type in ("mortar", "laser"):
            return True

        if ability_type in ("damage", "drain", "aoe", "mark"):
            if ability_range <= 1:
                return True
            return self.line_of_sight(caster.x, caster.y, x, y)

        return True

    def ability_range_tiles(self, caster, ability):
        tiles = []

        for y in range(MAP_H):
            for x in range(MAP_W):
                if self.ability_can_reach_tile(caster, x, y, ability):
                    tiles.append((x, y))

        return tiles

    def cover_score(self, x, y):
        score = 0

        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx = x + dx
            ny = y + dy

            if not in_bounds(nx, ny):
                score += 2
            elif self.map[ny][nx] == OBSTACLE:
                score += 4
            elif self.map[ny][nx] in (VOID, WATER_TILE):
                score += 1

        return score

    def exposed_to_heroes(self, x, y):
        danger = 0

        for hero in self.living_players():
            if self.can_attack_pos(hero, x, y):
                danger += hero.current_atk() * 3
            elif self.dist_pos(hero.x, hero.y, x, y) <= hero.move_range + hero.atk_range:
                danger += hero.current_atk()

        danger -= self.cover_score(x, y) * 7
        return max(0, danger)# =====================================================
    # PATHFINDING
    # =====================================================
    def reachable_tiles(self, unit):
        q = deque([(unit.x, unit.y, 0)])
        visited = {(unit.x, unit.y)}
        result = set()

        while q:
            x, y, distance = q.popleft()
            result.add((x, y))

            if distance >= unit.move_range:
                continue

            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx = x + dx
                ny = y + dy

                if (nx, ny) in visited:
                    continue
                if not self.walkable(nx, ny):
                    continue

                occ = self.unit_at(nx, ny)

                if occ is not None and occ != unit:
                    continue

                visited.add((nx, ny))
                q.append((nx, ny, distance + 1))

        return result

    def shortest_path(self, unit, target_x, target_y):
        start = (unit.x, unit.y)
        goal = (target_x, target_y)

        q = deque([start])
        came_from = {start: None}

        while q:
            cx, cy = q.popleft()

            if (cx, cy) == goal:
                break

            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx = cx + dx
                ny = cy + dy
                nxt = (nx, ny)

                if nxt in came_from:
                    continue
                if not self.walkable(nx, ny):
                    continue

                occ = self.unit_at(nx, ny)

                if occ is not None and occ != unit and nxt != goal:
                    continue

                came_from[nxt] = (cx, cy)
                q.append(nxt)

        if goal not in came_from:
            return []

        path = []
        cur = goal

        while cur is not None:
            path.append(cur)
            cur = came_from[cur]

        path.reverse()
        return path

    def path_distance_ignoring_units(self, sx, sy, tx, ty):
        q = deque([(sx, sy, 0)])
        visited = {(sx, sy)}

        while q:
            x, y, distance = q.popleft()

            if (x, y) == (tx, ty):
                return distance

            for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                nx = x + dx
                ny = y + dy

                if (nx, ny) in visited:
                    continue
                if not self.walkable(nx, ny):
                    continue

                visited.add((nx, ny))
                q.append((nx, ny, distance + 1))

        return 9999

    # =====================================================
    # COMBATE
    # =====================================================
    def target_team_units(self, unit):
        return self.living_enemies() if unit.team == "player" else self.living_players()

    def enemies_in_range(self, unit):
        return [target for target in self.target_team_units(unit) if self.can_attack(unit, target)]

    def calc_damage(self, attacker, target):
        base = attacker.current_atk()
        variance = random.randint(-3, 3)

        if attacker.name == "Ogro":
            base += 4
        elif attacker.name == "Chefe Ogro":
            base += 8

        return max(1, base + variance)

    def deal_damage(self, attacker, target, raw_damage):
        if target.team == "player" and self.god_mode:
            raw_damage = 0

        final_damage = target.take_damage(raw_damage)

        if not target.alive:
            self.handle_kill_passives(attacker, target)

        return final_damage

    def handle_kill_passives(self, attacker, target):
        if not attacker:
            return

        if attacker.team == "player" and attacker.zombie_on_kill and not target.alive:
            zombie = self.summon_unit("Zumbi Aliado", attacker.x, attacker.y, near_target=(target.x, target.y))

            if zombie:
                self.message += " Um zumbi aliado nasceu!"

    def attack(self, attacker, target):
        if not attacker.has_actions():
            self.message = f"{attacker.name} nao tem mais acoes."
            return False

        if attacker.attacked:
            self.message = f"{attacker.name} ja atacou neste turno."
            return False

        if not self.can_attack(attacker, target):
            self.message = f"{attacker.name} nao tem linha de visao!"
            return False

        raw_damage = self.calc_damage(attacker, target)

        if attacker.normal_aoe > 0:
            self.perform_normal_aoe_attack(attacker, target, raw_damage)
            return True

        final_damage = self.deal_damage(attacker, target, raw_damage)

        attacker.attacked = True
        attacker.spend_action()

        self.message = f"{attacker.name} atacou {target.name} (-{final_damage} HP)"

        if not target.alive:
            self.message = f"{target.name} foi derrotado!"

        self.check_winner()
        return True

    def perform_normal_aoe_attack(self, attacker, main_target, raw_damage):
        targets = []

        for unit in self.target_team_units(attacker):
            if self.dist_pos(main_target.x, main_target.y, unit.x, unit.y) <= attacker.normal_aoe:
                targets.append(unit)

        total_damage = 0
        defeated = 0

        for unit in targets:
            damage = raw_damage if unit == main_target else max(1, raw_damage // 2)
            dealt = self.deal_damage(attacker, unit, damage)
            total_damage += dealt

            if not unit.alive:
                defeated += 1

        attacker.attacked = True
        attacker.spend_action()

        self.message = f"{attacker.name} fez ataque em area: {total_damage} dano total."

        if defeated:
            self.message += f" {defeated} derrotado(s)!"

        self.check_winner()

    def check_winner(self):
        if not self.living_players():
            self.winner = "Inimigos"
            self.message = "Os herois cairam..."
        elif not self.living_enemies():
            self.winner = "Herois"
            self.give_reward_once()

    # =====================================================
    # HABILIDADES
    # =====================================================
    def get_selected_abilities(self):
        if not self.selected:
            return []

        return ABILITY_DATA.get(self.selected.name, [])

    def ability_button_rects(self):
        y = MAP_H * TILE + 100
        pad = 10
        gap = 8
        width = (WIDTH - pad * 2 - gap * 2) // 3

        return [
            pygame.Rect(pad, y, width, 42),
            pygame.Rect(pad + width + gap, y, width, 42),
            pygame.Rect(pad + (width + gap) * 2, y, width, 42),
        ]

    def handle_ability_key(self, index):
        if self.turn != "player" or self.winner or self.mode != "battle":
            return
        if self.animating or self.any_unit_moving():
            return
        if self.selected is None or not self.selected.alive:
            self.message = "Selecione um heroi primeiro."
            return

        abilities = self.get_selected_abilities()

        if index < 0 or index >= len(abilities):
            return

        ability = abilities[index]

        if self.skill_targeting == index:
            self.skill_targeting = None
            self.message = f"{ability['name']} cancelada."
            return

        if not self.selected.has_actions():
            self.message = f"{self.selected.name} nao tem mais acoes."
            return

        if ability.get("once") and ability["id"] in self.selected.used_once:
            self.message = f"{ability['name']} so pode ser usada uma vez."
            return

        cooldown = self.selected.cooldowns.get(ability["id"], 0)

        if cooldown > 0:
            self.message = f"{ability['name']} recarrega em {cooldown} rodada(s)."
            return

        if ability["type"] in ("damage", "heal", "drain", "aoe", "mark", "mortar", "laser"):
            self.skill_targeting = index
            self.message = f"Escolha um alvo para {ability['name']}."
            return

        self.use_self_ability(self.selected, ability)

    def finish_ability_use(self, caster, ability):
        caster.cooldowns[ability["id"]] = ability["cooldown"]

        if ability.get("once"):
            caster.used_once.add(ability["id"])

        caster.spend_action()
        self.skill_targeting = None

    def use_self_ability(self, caster, ability):
        if not caster.has_actions():
            self.message = f"{caster.name} nao tem mais acoes."
            return False

        if ability.get("once") and ability["id"] in caster.used_once:
            self.message = f"{ability['name']} so pode ser usada uma vez."
            return False

        ability_type = ability["type"]

        if ability_type == "shield":
            caster.effects["shield_turns"] = ability["duration"]
            caster.effects["shield_reduction"] = ability["reduction"]
            self.finish_ability_use(caster, ability)

            percent = int(ability["reduction"] * 100)
            self.message = f"{caster.name} usou {ability['name']}: dano -{percent}%."
            return True

        if ability_type == "buff":
            caster.effects["atk_bonus_turns"] = ability["duration"]
            caster.effects["atk_bonus"] = ability["atk_bonus"]
            self.finish_ability_use(caster, ability)

            self.message = f"{caster.name} usou {ability['name']}: ATK +{ability['atk_bonus']}."
            return True

        if ability_type == "focus":
            caster.spend_action()
            before = caster.actions_left
            caster.actions_left = min(ability["ap_cap"], caster.actions_left + ability["ap_gain"])
            gained = caster.actions_left - before

            caster.cooldowns[ability["id"]] = ability["cooldown"]

            if ability.get("once"):
                caster.used_once.add(ability["id"])

            self.skill_targeting = None
            self.message = f"{caster.name} usou {ability['name']}: +{gained} AP."
            return True

        if ability_type == "summon_minions":
            made = 0

            for _ in range(ability.get("count", 2)):
                if self.summon_unit("Lacaio Sombrio", caster.x, caster.y):
                    made += 1

            self.finish_ability_use(caster, ability)
            self.message = f"{caster.name} chamou {made} lacaio(s) das sombras."
            return True

        if ability_type == "summon_dragon":
            unit = self.summon_unit("Dragao de Sombras", caster.x, caster.y)
            self.finish_ability_use(caster, ability)

            self.message = f"{caster.name} invocou o Dragao de Sombras!" if unit else "Sem espaco para invocar o dragao."
            return True

        if ability_type == "summon_chimera":
            unit_name = self.roll_chimera()
            unit = self.summon_unit(unit_name, caster.x, caster.y)
            self.finish_ability_use(caster, ability)

            if unit:
                rarity = "Mercado Negro" if unit_name == "Chimera Planta" else unit_name.replace("Chimera ", "")
                self.message = f"{caster.name} invocou {unit_name}! Raridade: {rarity}."
            else:
                self.message = "Sem espaco para invocar a Chimera."
            return True

        if ability_type == "traps":
            made = 0

            for _ in range(ability.get("count", 6)):
                spot = self.random_empty_floor()

                if spot:
                    self.traps.append({"x": spot[0], "y": spot[1], "damage": caster.current_atk() + 18})
                    made += 1

            self.finish_ability_use(caster, ability)
            self.message = f"{caster.name} espalhou {made} armadilha(s) vivas."
            return True

        if ability_type == "summon_plants":
            options = ["Zumbi Planta", "Zumbi Planta", "Golem de Madeira", "Dragao de Planta"]
            made = []

            for _ in range(random.randint(2, 3)):
                unit_name = random.choice(options)

                if self.summon_unit(unit_name, caster.x, caster.y):
                    made.append(unit_name)

            self.finish_ability_use(caster, ability)

            if made:
                self.message = f"{caster.name} invocou: {', '.join(made)}."
            else:
                self.message = "Sem espaco para invocar monstros de planta."

            return True

        return False

    def roll_chimera(self):
        roll = random.randint(1, 100)

        if roll <= 50:
            return "Chimera Comum"
        if roll <= 78:
            return "Chimera Rara"
        if roll <= 95:
            return "Chimera Lendaria"

        return "Chimera Planta"

    def can_use_ability_on(self, caster, target, ability):
        if target is None or not target.alive:
            return False

        ability_type = ability["type"]

        if ability_type in ("damage", "drain", "aoe", "mark", "mortar", "laser"):
            if caster.team == target.team:
                return False

        if ability_type == "heal":
            if caster.team != target.team:
                return False

        if self.dist_pos(caster.x, caster.y, target.x, target.y) > ability.get("range", 99):
            return False

        if ability.get("ignore_los") or ability_type in ("mortar", "laser"):
            return True

        if ability_type in ("damage", "drain", "aoe", "mark"):
            return self.line_of_sight(caster.x, caster.y, target.x, target.y)

        return True

    def use_target_ability(self, caster, target, ability):
        if not caster.has_actions():
            self.message = f"{caster.name} nao tem mais acoes."
            self.skill_targeting = None
            return False

        if ability.get("once") and ability["id"] in caster.used_once:
            self.message = f"{ability['name']} so pode ser usada uma vez."
            self.skill_targeting = None
            return False

        cooldown = caster.cooldowns.get(ability["id"], 0)

        if cooldown > 0:
            self.message = f"{ability['name']} recarrega em {cooldown} rodada(s)."
            self.skill_targeting = None
            return False

        if not self.can_use_ability_on(caster, target, ability):
            self.message = f"{ability['name']} nao alcanca esse alvo."
            return False

        ability_type = ability["type"]

        if ability_type == "heal":
            return self.use_heal_ability(caster, target, ability)

        if ability_type == "mark":
            return self.use_mark_ability(caster, target, ability)

        if ability_type in ("aoe", "mortar"):
            return self.use_aoe_ability(caster, target, ability)

        if ability_type == "laser":
            return self.use_laser_ability(caster, target, ability)

        return self.use_damage_ability(caster, target, ability)

    def use_heal_ability(self, caster, target, ability):
        amount = ability["amount"] + caster.current_atk() // 2
        healed = target.heal(amount)

        self.finish_ability_use(caster, ability)
        self.message = f"{caster.name} usou {ability['name']} em {target.name}: +{healed} HP."
        return True

    def use_mark_ability(self, caster, target, ability):
        target.effects["vulnerable_turns"] = ability["duration"]
        target.effects["vulnerability"] = ability["vulnerability"]

        self.finish_ability_use(caster, ability)

        percent = int(ability["vulnerability"] * 100)
        self.message = f"{caster.name} marcou {target.name}: dano recebido +{percent}%."
        return True

    def use_aoe_ability(self, caster, target, ability):
        targets = []

        for enemy in self.living_enemies():
            if self.dist_pos(target.x, target.y, enemy.x, enemy.y) <= ability.get("radius", 1):
                targets.append(enemy)

        total_damage = 0
        defeated = 0

        for enemy in targets:
            raw_damage = max(1, caster.current_atk() + ability["bonus"] + random.randint(-2, 3))
            dealt = self.deal_damage(caster, enemy, raw_damage)
            total_damage += dealt

            if not enemy.alive:
                defeated += 1

        self.finish_ability_use(caster, ability)

        self.message = f"{caster.name} usou {ability['name']}: {total_damage} dano total."

        if defeated:
            self.message += f" {defeated} derrotado(s)!"

        self.check_winner()
        return True

    def use_laser_ability(self, caster, target, ability):
        dx = 0
        dy = 0

        if target.x > caster.x:
            dx = 1
        elif target.x < caster.x:
            dx = -1

        if target.y > caster.y:
            dy = 1
        elif target.y < caster.y:
            dy = -1

        hit = []
        x = caster.x + dx
        y = caster.y + dy

        while in_bounds(x, y):
            unit = self.unit_at(x, y)

            if unit and unit.team == "enemy":
                hit.append(unit)

            x += dx
            y += dy

            if dx == 0 and dy == 0:
                break

        if target not in hit:
            hit.append(target)

        total_damage = 0
        defeated = 0

        for enemy in hit:
            raw_damage = max(1, caster.current_atk() + ability["bonus"] + random.randint(-2, 4))
            dealt = self.deal_damage(caster, enemy, raw_damage)
            total_damage += dealt

            if not enemy.alive:
                defeated += 1

        self.finish_ability_use(caster, ability)

        self.message = f"{caster.name} disparou {ability['name']}: {total_damage} dano em linha."

        if defeated:
            self.message += f" {defeated} derrotado(s)!"

        self.check_winner()
        return True

    def use_damage_ability(self, caster, target, ability):
        raw_damage = max(1, caster.current_atk() + ability["bonus"] + random.randint(-2, 3))
        final_damage = self.deal_damage(caster, target, raw_damage)

        extra = ""

        if ability["type"] == "drain":
            healed = caster.heal(final_damage // 2)
            extra = f" e curou {healed} HP"

        self.finish_ability_use(caster, ability)

        self.message = f"{caster.name} usou {ability['name']} em {target.name}! (-{final_damage} HP){extra}"

        if not target.alive:
            self.message = f"{target.name} foi derrotado por {ability['name']}!"

        self.check_winner()
        return True

    def cancel_skill(self):
        if self.skill_targeting is not None:
            self.skill_targeting = None
            self.message = "Habilidade cancelada."

    # =====================================================
    # TURNOS / MOVIMENTO
    # =====================================================
    def start_player_turn(self):
        self.turn = "player"
        self.selected = None
        self.skill_targeting = None
        self.message = "Turno do jogador"

        for unit in self.living_players():
            unit.reset_turn()
            unit.tick_cooldowns()
            unit.tick_effects()

        for enemy in self.living_enemies():
            enemy.reset_turn()
            enemy.tick_effects()

    def end_player_turn(self):
        if self.animating or self.any_unit_moving() or self.winner or self.mode != "battle":
            return

        self.turn = "enemy"
        self.selected = None
        self.skill_targeting = None
        self.message = "Turno dos inimigos"
        self.enemy_turn_queue = self.living_enemies()[:]
        self.enemy_state = "choose"
        self.current_enemy = None
        self.enemy_action_timer = pygame.time.get_ticks()

    def move_unit_with_animation(self, unit, x, y):
        if not unit.has_actions():
            self.message = f"{unit.name} nao tem mais acoes."
            return False

        if unit.moved:
            self.message = f"{unit.name} ja se moveu neste turno."
            return False

        if (x, y) not in self.reachable_tiles(unit):
            return False

        if self.blocked(x, y, ignore=unit):
            return False

        path = self.shortest_path(unit, x, y)

        if len(path) <= 1:
            return False

        unit.moved = True
        unit.spend_action()
        unit.start_path(path[1:])

        self.animating = True
        self.skill_targeting = None
        self.message = f"{unit.name} moveu"
        return True

    # =====================================================
    # IA INIMIGA
    # =====================================================
    def choose_enemy_target(self, enemy):
        targets = self.living_players()

        if not targets:
            return None

        def score(player):
            path_d = self.path_distance_ignoring_units(enemy.x, enemy.y, player.x, player.y)
            hp_missing = player.max_hp - player.hp
            kill_bonus = 80 if player.hp <= enemy.current_atk() + 8 else 0
            visible_bonus = 20 if self.can_attack(enemy, player) else 0
            shield_penalty = 25 if player.has_shield() else 0

            return path_d * 10 - hp_missing - kill_bonus - visible_bonus + shield_penalty

        return min(targets, key=score)

    def choose_attack_target(self, enemy):
        targets = self.enemies_in_range(enemy)

        if not targets:
            return None

        def score(player):
            kill_bonus = 100 if player.hp <= enemy.current_atk() + 8 else 0
            weak_bonus = player.max_hp - player.hp
            shield_penalty = 25 if player.has_shield() else 0

            return -kill_bonus - weak_bonus + self.dist(enemy, player) + shield_penalty

        return min(targets, key=score)

    def can_any_player_attack_tile(self, x, y):
        return any(self.can_attack_pos(player, x, y) for player in self.living_players())

    def evaluate_enemy_tile(self, enemy, tx, ty, target):
        current_dist = self.path_distance_ignoring_units(enemy.x, enemy.y, target.x, target.y)
        new_dist = self.path_distance_ignoring_units(tx, ty, target.x, target.y)
        manhattan = self.dist_pos(tx, ty, target.x, target.y)

        can_attack = self.can_attack_pos(enemy, target.x, target.y, tx, ty)
        cover = self.cover_score(tx, ty)
        danger = self.exposed_to_heroes(tx, ty)
        visible_to_hero = self.can_any_player_attack_tile(tx, ty)

        score = 0

        if can_attack:
            score -= 180
        else:
            score += new_dist * 16

            if new_dist < current_dist:
                score -= 70
            elif new_dist == current_dist:
                score += 18
            else:
                score += 160

        score -= cover * 14
        score += danger * 2

        if visible_to_hero and cover <= 0:
            score += 45

        if enemy.ai in ("melee", "brute", "boss"):
            score += manhattan * 8
            if manhattan <= enemy.atk_range:
                score -= 70

        if enemy.ai == "ranged":
            ideal = enemy.atk_range

            if can_attack:
                score += abs(manhattan - ideal) * 7
                if cover > 0:
                    score -= 35
            else:
                score += new_dist * 8

            if manhattan <= 1:
                score += 55

        if enemy.ai == "boss":
            score -= 25
            score -= cover * 4

        score += random.randint(-4, 4)
        return score

    def choose_enemy_move(self, enemy, target):
        if not enemy.has_actions():
            return None

        reachable = list(self.reachable_tiles(enemy))
        valid_tiles = []

        for tx, ty in reachable:
            occ = self.unit_at(tx, ty)
            if occ is not None and occ != enemy:
                continue
            valid_tiles.append((tx, ty))

        if not valid_tiles:
            return None

        current_dist = self.path_distance_ignoring_units(enemy.x, enemy.y, target.x, target.y)
        can_attack_now = self.can_attack(enemy, target)

        best_tile = None
        best_score = 999999

        for tx, ty in valid_tiles:
            score = self.evaluate_enemy_tile(enemy, tx, ty, target)
            new_dist = self.path_distance_ignoring_units(tx, ty, target.x, target.y)

            if not can_attack_now and new_dist > current_dist:
                score += 200

            if score < best_score:
                best_score = score
                best_tile = (tx, ty)

        if best_tile == (enemy.x, enemy.y):
            return None

        return best_tile

    def update_enemy_turn(self):
        if self.turn != "enemy" or self.winner or self.mode != "battle":
            return
        if self.any_unit_moving():
            return

        now = pygame.time.get_ticks()

        if self.enemy_state == "choose":
            if not self.enemy_turn_queue:
                self.start_player_turn()
                return

            self.current_enemy = self.enemy_turn_queue.pop(0)

            if not self.current_enemy.alive:
                return

            self.current_enemy.reset_turn()
            self.enemy_state = "act"
            self.enemy_action_timer = now
            return

        if self.enemy_state == "act":
            if now - self.enemy_action_timer < 250:
                return

            enemy = self.current_enemy

            if enemy is None or not enemy.alive:
                self.enemy_state = "choose"
                return

            target = self.choose_attack_target(enemy)

            if target and not enemy.attacked and enemy.has_actions():
                self.attack(enemy, target)
                self.enemy_state = "choose"
                self.enemy_action_timer = now
                return

            target = self.choose_enemy_target(enemy)

            if target is None:
                self.check_winner()
                return

            if not enemy.moved and enemy.has_actions():
                move_pos = self.choose_enemy_move(enemy, target)

                if move_pos:
                    path = self.shortest_path(enemy, move_pos[0], move_pos[1])

                    if len(path) > 1:
                        enemy.moved = True
                        enemy.spend_action()
                        enemy.start_path(path[1:])
                        self.animating = True
                        self.enemy_state = "post_move"
                        return

            self.enemy_state = "choose"
            self.enemy_action_timer = now
            return

        if self.enemy_state == "post_move":
            if self.any_unit_moving():
                return

            enemy = self.current_enemy

            if enemy and enemy.alive and enemy.has_actions() and not enemy.attacked:
                target = self.choose_attack_target(enemy)

                if target:
                    self.attack(enemy, target)

            self.enemy_state = "choose"
            self.enemy_action_timer = now

    # =====================================================
    # ARMADILHAS
    # =====================================================
    def check_traps(self):
        if not self.traps:
            return

        remaining = []

        for trap in self.traps:
            triggered = False

            for enemy in self.living_enemies():
                if self.dist_pos(trap["x"], trap["y"], enemy.x, enemy.y) <= 1:
                    triggered = True
                    break

            if triggered:
                defeated = 0

                for enemy in self.living_enemies():
                    if self.dist_pos(trap["x"], trap["y"], enemy.x, enemy.y) <= 1:
                        enemy.take_damage(trap["damage"])

                        if not enemy.alive:
                            defeated += 1

                self.message = "Uma armadilha viva explodiu!"

                if defeated:
                    self.message += f" {defeated} derrotado(s)."

                self.check_winner()
            else:
                remaining.append(trap)

        self.traps = remaining

    # =====================================================
    # INPUT
    # =====================================================
    def handle_enter(self):
        if self.mode == "shop":
            self.next_level(1)
            return

        if self.winner == "Herois":
            if self.level % 3 == 0:
                self.open_shop()
            else:
                self.next_level(1)

    def handle_ui_click(self, mx, my):
        if self.selected is None or not self.selected.alive:
            return

        for i, rect in enumerate(self.ability_button_rects()):
            if rect.collidepoint(mx, my):
                self.handle_ability_key(i)
                return

    def handle_click(self, mx, my):
        if self.mode == "shop":
            return
        if self.turn != "player" or self.winner:
            return
        if self.animating or self.any_unit_moving():
            return

        if my >= MAP_H * TILE:
            self.handle_ui_click(mx, my)
            return

        gx = mx // TILE
        gy = my // TILE
        clicked = self.unit_at(gx, gy)

        if self.skill_targeting is not None:
            self.handle_skill_click(clicked)
            return

        if clicked and clicked.team == "player":
            self.selected = clicked
            self.skill_targeting = None
            self.message = f"{clicked.name} selecionado"
            return

        if self.selected is None or not self.selected.alive:
            return

        if clicked and clicked.team == "enemy":
            self.attack(self.selected, clicked)
            return

        if clicked is None and self.walkable(gx, gy):
            self.move_unit_with_animation(self.selected, gx, gy)

    def handle_skill_click(self, clicked):
        abilities = self.get_selected_abilities()

        if not (0 <= self.skill_targeting < len(abilities)):
            self.skill_targeting = None
            return

        ability = abilities[self.skill_targeting]

        if clicked:
            if ability["type"] == "heal" and clicked.team == "player":
                self.use_target_ability(self.selected, clicked, ability)
                return

            if ability["type"] in ("damage", "drain", "aoe", "mark", "mortar", "laser") and clicked.team == "enemy":
                self.use_target_ability(self.selected, clicked, ability)
                return

            if clicked.team == "player":
                self.selected = clicked
                self.skill_targeting = None
                self.message = f"{clicked.name} selecionado"
                return

        self.message = "Escolha um alvo valido ou aperte ESC."

    # =====================================================
    # UPDATE
    # =====================================================
    def update(self, dt):
        if self.mode == "shop":
            return

        for unit in self.all_units():
            if unit.alive:
                unit.update_animation(dt)

        if not self.any_unit_moving():
            self.animating = False

        self.check_traps()
        self.update_enemy_turn()

    # =====================================================
    # DRAW MAPA
    # =====================================================
    def draw_map(self):
        for y in range(MAP_H):
            for x in range(MAP_W):
                rect = pygame.Rect(x * TILE, y * TILE, TILE, TILE)
                cell = self.map[y][x]

                if cell == VOID:
                    pygame.draw.rect(screen, BLACK, rect)

                elif cell == FLOOR:
                    color = GREEN_A if (x + y) % 2 == 0 else GREEN_B

                    if seeded_dot(x, y, 7):
                        color = GREEN_C

                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, GRID_GREEN, rect, 1)

                    if seeded_dot(x, y, 11):
                        pygame.draw.circle(screen, (210, 220, 120), (x * TILE + 10, y * TILE + 11), 2)

                    if seeded_dot(x, y, 17):
                        pygame.draw.circle(screen, (230, 170, 210), (x * TILE + 24, y * TILE + 21), 2)

                elif cell == PATH_TILE:
                    color = DIRT_A if (x + y) % 2 == 0 else DIRT_B
                    pygame.draw.rect(screen, color, rect)
                    pygame.draw.rect(screen, (100, 75, 50), rect, 1)

                elif cell == WATER_TILE:
                    pygame.draw.rect(screen, WATER, rect)
                    inner = rect.inflate(-7, -7)
                    pygame.draw.rect(screen, WATER_EDGE, inner, border_radius=7)

                elif cell == OBSTACLE:
                    base = GREEN_A if (x + y) % 2 == 0 else GREEN_B
                    pygame.draw.rect(screen, base, rect)
                    pygame.draw.rect(screen, GRID_GREEN, rect, 1)

                    if seeded_dot(x, y, 5):
                        trunk = pygame.Rect(x * TILE + 13, y * TILE + 16, 7, 13)
                        crown = pygame.Rect(x * TILE + 6, y * TILE + 4, 22, 22)

                        pygame.draw.rect(screen, (105, 75, 45), trunk, border_radius=3)
                        pygame.draw.ellipse(screen, TREE_DARK, crown.inflate(4, 4))
                        pygame.draw.ellipse(screen, TREE, crown)
                    else:
                        block = rect.inflate(-7, -7)
                        pygame.draw.rect(screen, GRAY, block, border_radius=7)
                        pygame.draw.rect(screen, GRAY_DARK, block, 2, border_radius=7)

    def draw_traps(self):
        for trap in self.traps:
            cx = trap["x"] * TILE + TILE // 2
            cy = trap["y"] * TILE + TILE // 2
            pygame.draw.circle(screen, TRAP_COLOR, (cx, cy), 6)
            pygame.draw.circle(screen, BLACK, (cx, cy), 6, 1)

    def draw_cover_marks(self):
        if self.selected is None or not self.selected.alive:
            return
        if self.turn != "player":
            return
        if self.animating or self.any_unit_moving():
            return

        for y in range(MAP_H):
            for x in range(MAP_W):
                if not self.walkable(x, y):
                    continue
                if self.cover_score(x, y) >= 4:
                    pygame.draw.circle(screen, COVER_COLOR, (x * TILE + TILE // 2, y * TILE + TILE // 2), 3)

    def draw_skill_range_tiles(self):
        if self.selected is None or not self.selected.alive:
            return
        if self.turn != "player":
            return
        if self.skill_targeting is None:
            return
        if self.animating or self.any_unit_moving():
            return

        abilities = self.get_selected_abilities()

        if not (0 <= self.skill_targeting < len(abilities)):
            return

        ability = abilities[self.skill_targeting]
        tiles = self.ability_range_tiles(self.selected, ability)

        layer = pygame.Surface((WIDTH, MAP_H * TILE), pygame.SRCALPHA)

        if ability.get("range", 0) >= 99 or ability.get("ignore_los"):
            fill_color = GLOBAL_RANGE_FILL
        else:
            fill_color = SKILL_RANGE_FILL

        for x, y in tiles:
            if (x, y) == (self.selected.x, self.selected.y):
                continue

            rect = pygame.Rect(x * TILE + 3, y * TILE + 3, TILE - 6, TILE - 6)
            pygame.draw.rect(layer, fill_color, rect, border_radius=6)
            pygame.draw.rect(layer, (255, 180, 255, 120), rect, 1, border_radius=6)

        screen.blit(layer, (0, 0))

    def draw_highlights(self):
        if self.selected is None or not self.selected.alive:
            return
        if self.turn != "player":
            return
        if self.animating or self.any_unit_moving():
            return

        if self.skill_targeting is not None:
            self.draw_skill_range_tiles()

            abilities = self.get_selected_abilities()

            if 0 <= self.skill_targeting < len(abilities):
                ability = abilities[self.skill_targeting]
                targets = self.living_players() if ability["type"] == "heal" else self.living_enemies()

                for target in targets:
                    if self.can_use_ability_on(self.selected, target, ability):
                        rect = pygame.Rect(target.x * TILE + 1, target.y * TILE + 1, TILE - 2, TILE - 2)
                        pygame.draw.rect(screen, SKILL_COLOR, rect, 4, border_radius=9)

            return

        if self.selected.has_actions() and not self.selected.moved:
            for x, y in self.reachable_tiles(self.selected):
                if (x, y) == (self.selected.x, self.selected.y):
                    continue

                if self.unit_at(x, y) is None and self.walkable(x, y):
                    rect = pygame.Rect(x * TILE + 5, y * TILE + 5, TILE - 10, TILE - 10)
                    pygame.draw.rect(screen, MOVE_COLOR, rect, 2, border_radius=7)

        if self.selected.has_actions() and not self.selected.attacked:
            for enemy in self.living_enemies():
                if self.can_attack(self.selected, enemy):
                    rect = pygame.Rect(enemy.x * TILE + 3, enemy.y * TILE + 3, TILE - 6, TILE - 6)
                    pygame.draw.rect(screen, ATTACK_COLOR, rect, 3, border_radius=8)

    def draw_units(self):
        for player in self.players:
            if player.alive:
                player.draw(screen, selected=(player == self.selected))

        for enemy in self.enemies:
            if enemy.alive:
                enemy.draw(screen)

    # =====================================================
    # DRAW UI
    # =====================================================
    def draw_unit_card(self):
        y = MAP_H * TILE + 42
        rect = pygame.Rect(10, y, 285, 50)

        pygame.draw.rect(screen, PANEL_BOX, rect, border_radius=10)
        pygame.draw.rect(screen, PANEL_LINE, rect, 2, border_radius=10)

        if not self.selected:
            draw_text_fit(screen, "Nenhum heroi selecionado", small_font, WHITE, rect.x + 10, rect.y + 8, rect.w - 20)
            draw_text_fit(screen, "Clique em um heroi.", tiny_font, YELLOW, rect.x + 10, rect.y + 30, rect.w - 20)
            return

        unit = self.selected

        draw_text_fit(screen, f"{unit.name} - {unit.role}", small_font, WHITE, rect.x + 10, rect.y + 5, rect.w - 20)

        info = f"HP {unit.hp}/{unit.max_hp}  AP {unit.actions_left}/2  ATK {unit.current_atk()}  MOV {unit.move_range}"
        draw_text_fit(screen, info, tiny_font, YELLOW, rect.x + 10, rect.y + 25, rect.w - 20)

    def draw_level_card(self):
        y = MAP_H * TILE + 42
        rect = pygame.Rect(305, y, 235, 50)

        pygame.draw.rect(screen, PANEL_BOX, rect, border_radius=10)
        pygame.draw.rect(screen, PANEL_LINE, rect, 2, border_radius=10)

        draw_text_fit(screen, f"Nivel {self.level}   Fase {self.get_stage()}/5", small_font, WHITE, rect.x + 10, rect.y + 5, rect.w - 20)
        draw_text_fit(screen, f"Ciclo {self.get_cycle()} - Ouro: {'INF' if self.infinite_gold else self.gold}", tiny_font, GOLD, rect.x + 10, rect.y + 27, rect.w - 20)

    def draw_team_card(self):
        y = MAP_H * TILE + 42
        rect = pygame.Rect(550, y, WIDTH - 560, 50)

        pygame.draw.rect(screen, PANEL_BOX, rect, border_radius=10)
        pygame.draw.rect(screen, PANEL_LINE, rect, 2, border_radius=10)

        real_heroes = len([p for p in self.players if p.alive and not p.summoned])
        enemies = len(self.living_enemies())

        draw_text_fit(screen, f"Equipe: {real_heroes}/{MAX_PARTY_SIZE}  Inimigos: {enemies}", small_font, WHITE, rect.x + 10, rect.y + 5, rect.w - 20)
        draw_text_fit(screen, "F1 console | 1/2/3 habilidades", tiny_font, YELLOW, rect.x + 10, rect.y + 27, rect.w - 20)

    def draw_ability_menu(self):
        for i, rect in enumerate(self.ability_button_rects()):
            pygame.draw.rect(screen, PANEL_DARK, rect, border_radius=10)
            pygame.draw.rect(screen, PANEL_LINE, rect, 2, border_radius=10)

            if self.selected is None or not self.selected.alive:
                draw_text_fit(screen, f"{i + 1} - Selecione", tiny_font, GRAY, rect.x + 10, rect.y + 14, rect.w - 20)
                continue

            abilities = self.get_selected_abilities()

            if i >= len(abilities):
                draw_text_fit(screen, f"{i + 1} - Vazio", tiny_font, GRAY, rect.x + 10, rect.y + 14, rect.w - 20)
                continue

            ability = abilities[i]
            cooldown = self.selected.cooldowns.get(ability["id"], 0)

            if ability.get("once") and ability["id"] in self.selected.used_once:
                status = "usada"
                color = GRAY
            elif not self.selected.has_actions():
                status = "sem AP"
                color = GRAY
            elif cooldown > 0:
                status = f"CD {cooldown}"
                color = ORANGE
            else:
                status = "pronto"
                color = CYAN

            if self.skill_targeting == i:
                pygame.draw.rect(screen, SKILL_COLOR, rect, 3, border_radius=10)

            draw_text_fit(screen, f"{i + 1}-{ability['name']} [{status}]", tiny_font, color, rect.x + 7, rect.y + 5, rect.w - 14)
            draw_text_fit(screen, ability["desc"], tiny_font, WHITE, rect.x + 7, rect.y + 24, rect.w - 14)

    def draw_ui(self):
        ui_y = MAP_H * TILE
        ui_rect = pygame.Rect(0, ui_y, WIDTH, UI_H)

        pygame.draw.rect(screen, PANEL_BG, ui_rect)
        pygame.draw.line(screen, PANEL_LINE, (0, ui_y), (WIDTH, ui_y), 2)

        turn_label = "Jogador" if self.turn == "player" else "Inimigos"
        draw_text_fit(screen, f"Turno: {turn_label}", font, WHITE, 10, ui_y + 6, 190)
        draw_text_fit(screen, self.message, small_font, YELLOW, 205, ui_y + 9, WIDTH - 215)

        if self.skill_targeting is not None:
            help_text = "MODO HABILIDADE: blocos rosas = alcance | clique em alvo valido | ESC cancela"
            color = SKILL_COLOR
        else:
            help_text = "Cada unidade tem 2 AP | 1/2/3 habilidades | ESPACO passar turno | ENTER apos vencer"
            color = WHITE

        draw_text_fit(screen, help_text, tiny_font, color, 10, ui_y + 28, WIDTH - 20)

        self.draw_unit_card()
        self.draw_level_card()
        self.draw_team_card()
        self.draw_ability_menu()

        if self.winner:
            self.draw_winner_overlay()

    def draw_winner_overlay(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 165))
        screen.blit(overlay, (0, 0))

        if self.winner == "Herois":
            title = "Vitoria dos Herois!"

            if self.level % 3 == 0:
                subtitle = "ENTER: abrir loja | T: repetir | R: reiniciar"
            else:
                subtitle = "ENTER: proximo nivel | T: repetir | R: reiniciar"
        else:
            title = "Os Inimigos Venceram..."
            subtitle = "T: tentar de novo | R: reiniciar"

        win_text = font.render(title, True, WHITE)
        sub_text = small_font.render(subtitle, True, YELLOW)

        screen.blit(win_text, win_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 15)))
        screen.blit(sub_text, sub_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

    def draw_shop(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 190))
        screen.blit(overlay, (0, 0))

        panel = pygame.Rect(42, 35, WIDTH - 84, HEIGHT - 70)

        pygame.draw.rect(screen, (28, 25, 38), panel, border_radius=18)
        pygame.draw.rect(screen, GOLD, panel, 3, border_radius=18)

        title = font.render("LOJA DO MERCADOR", True, GOLD)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, panel.y + 28)))

        draw_text_fit(screen, f"Ouro: {'INFINITO' if self.infinite_gold else self.gold}", small_font, WHITE, panel.x + 20, panel.y + 58, 250)
        draw_text_fit(screen, f"Equipe: {len(self.party_names)}/{MAX_PARTY_SIZE}", small_font, WHITE, panel.right - 190, panel.y + 58, 170)

        if self.pending_purchase:
            self.draw_replace_menu(panel)
        else:
            self.draw_shop_items(panel)

        help_text = "1/2/3/4 comprar | ENTER ou N: proximo nivel | F1: console dev | gold no console = 9999"
        draw_text_fit(screen, help_text, small_font, YELLOW, panel.x + 25, panel.bottom - 45, panel.w - 50)

    def draw_replace_menu(self, panel):
        warning = f"Equipe cheia! Escolha 1-{MAX_PARTY_SIZE} para trocar por {self.pending_purchase}. ESC cancela."
        draw_text_fit(screen, warning, small_font, SKILL_COLOR, panel.x + 20, panel.y + 82, panel.w - 40)

        for i, name in enumerate(self.party_names):
            row = pygame.Rect(panel.x + 25, panel.y + 115 + i * 58, panel.w - 50, 45)
            data = CLASS_DATA[name]

            pygame.draw.rect(screen, PANEL_BOX, row, border_radius=10)
            pygame.draw.rect(screen, PANEL_LINE, row, 2, border_radius=10)

            text = f"{i + 1} - Trocar {name} | HP {data['hp']} | ATK {data['atk']} | {data.get('personality', '')}"
            draw_text_fit(screen, text, small_font, WHITE, row.x + 12, row.y + 12, row.w - 24)

    def draw_shop_items(self, panel):
        if not self.shop_items:
            draw_text_fit(screen, "Nao ha novos personagens para comprar.", small_font, WHITE, panel.x + 30, panel.y + 105, panel.w - 60)
            return

        for i, name in enumerate(self.shop_items):
            shop_data = HERO_SHOP_DATA[name]
            unit_data = CLASS_DATA[name]
            rarity = shop_data["rarity"]
            color = RARITY_COLORS[rarity]

            row = pygame.Rect(panel.x + 25, panel.y + 95 + i * 76, panel.w - 50, 64)

            pygame.draw.rect(screen, PANEL_BOX, row, border_radius=12)
            pygame.draw.rect(screen, color, row, 2, border_radius=12)

            draw_text_fit(screen, f"{i + 1} - {name}", small_font, color, row.x + 12, row.y + 6, 230)
            draw_text_fit(screen, f"{rarity} | Preco: {shop_data['price']}", tiny_font, GOLD, row.x + 12, row.y + 29, 220)

            stats = f"HP {unit_data['hp']} | ATK {unit_data['atk']} | MOV {unit_data['move']} | ALC {unit_data['range']}"
            draw_text_fit(screen, stats, tiny_font, WHITE, row.x + 250, row.y + 7, row.w - 270)

            abilities = ABILITY_DATA.get(name, [])
            ability_text = " / ".join(ability["name"] for ability in abilities[:3]) if abilities else "Sem habilidades"

            draw_text_fit(screen, ability_text, tiny_font, CYAN, row.x + 250, row.y + 28, row.w - 270)
            draw_text_fit(screen, unit_data.get("personality", ""), tiny_font, YELLOW, row.x + 250, row.y + 47, row.w - 270)

    def draw_console(self):
        if not self.console_open:
            return

        rect = pygame.Rect(8, 8, WIDTH - 16, 145)

        pygame.draw.rect(screen, (5, 5, 8), rect, border_radius=8)
        pygame.draw.rect(screen, (90, 255, 120), rect, 2, border_radius=8)

        y = rect.y + 8

        for line in self.console_log[-5:]:
            draw_text_fit(screen, line, tiny_font, (130, 255, 150), rect.x + 10, y, rect.w - 20)
            y += 18

        draw_text_fit(screen, "> " + self.console_text, small_font, WHITE, rect.x + 10, rect.bottom - 28, rect.w - 20)

    def draw(self):
        self.draw_map()
        self.draw_traps()
        self.draw_cover_marks()
        self.draw_highlights()
        self.draw_units()
        self.draw_ui()

        if self.mode == "shop":
            self.draw_shop()

        self.draw_console()


# =========================================================
# LOOP PRINCIPAL
# =========================================================
def main():
    game = Game()

    while True:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game.console_open:
                game.handle_console_event(event)
                continue

            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_F1, pygame.K_BACKQUOTE):
                    game.toggle_console()

                elif game.mode == "shop":
                    if game.pending_purchase:
                        if event.key == pygame.K_1:
                            game.replace_party_member(0)
                        elif event.key == pygame.K_2:
                            game.replace_party_member(1)
                        elif event.key == pygame.K_3:
                            game.replace_party_member(2)
                        elif event.key == pygame.K_4:
                            game.replace_party_member(3)
                        elif event.key == pygame.K_ESCAPE:
                            game.cancel_purchase()
                    else:
                        if event.key == pygame.K_1:
                            game.buy_shop_item(0)
                        elif event.key == pygame.K_2:
                            game.buy_shop_item(1)
                        elif event.key == pygame.K_3:
                            game.buy_shop_item(2)
                        elif event.key == pygame.K_4:
                            game.buy_shop_item(3)
                        elif event.key in (pygame.K_RETURN, pygame.K_n):
                            game.next_level(1)

                else:
                    if event.key == pygame.K_SPACE and not game.winner:
                        game.end_player_turn()
                    elif event.key == pygame.K_r:
                        game.reset_campaign()
                    elif event.key == pygame.K_t:
                        game.retry_level()
                    elif event.key == pygame.K_RETURN:
                        game.handle_enter()
                    elif event.key == pygame.K_ESCAPE:
                        game.cancel_skill()
                    elif event.key == pygame.K_1:
                        game.handle_ability_key(0)
                    elif event.key == pygame.K_2:
                        game.handle_ability_key(1)
                    elif event.key == pygame.K_3:
                        game.handle_ability_key(2)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.handle_click(*event.pos)

        game.update(dt)

        screen.fill(BLACK)
        game.draw()
        pygame.display.update()


if __name__ == "__main__":
    main()