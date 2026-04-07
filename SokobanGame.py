"""
Sokoban - Python / pygame
Run: pip install pygame  then  python sokoban.py
"""

import sys
import copy
import pygame

# ── palette ────────────────────────────────────────────────────────────────
BG        = (17, 17, 24)
WALL_DARK = (30, 30, 50)
WALL_MID  = (42, 42, 70)
WALL_HI   = (55, 55, 90)
FLOOR     = (16, 16, 22)
TARGET_C  = (192, 57, 43)
BOX_BODY  = (176, 110, 65)
BOX_HI    = (210, 140, 78)
BOX_SH    = (100, 60, 28)
BOX_DONE  = (39, 174, 96)
BOX_DONE_HI = (52, 210, 120)
BOX_DONE_SH = (20, 90, 45)
PLAYER_B  = (41, 128, 185)
PLAYER_H  = (52, 152, 219)
PLAYER_SK = (247, 232, 200)
PLAYER_HAT= (230, 126, 34)
TEXT_GOLD = (247, 201, 72)
TEXT_GRAY = (140, 140, 160)
TEXT_WHITE= (220, 220, 220)
GREEN_HUD = (78, 201, 78)
OVERLAY   = (10, 10, 20, 220)


LEVELS = [
    # ── 1. Tutorial ──────────────────────────────────────────────────────
    # Solution: → (push box onto target)
    {"name": "Tutorial", "map": [
        "#####",
        "#@$.#",
        "#####",
    ]},

    # ── 2. Simple ────────────────────────────────────────────────────────
    # Solution: push top-box right onto top-right target,
    #           push bottom-box up then right onto bottom target
    {"name": "Simple", "map": [
        "######",
        "#@ . #",
        "# $  #",
        "#  . #",
        "#  $ #",
        "######",
    ]},

    # ── 3. Corner ────────────────────────────────────────────────────────
    # Solution: push top-left box left, push middle box down-right,
    #           push bottom box up to bottom-left target
    {"name": "Corner", "map": [
        "#######",
        "#.@ . #",
        "# $   #",
        "#   $ #",
        "# .   #",
        "#######",
    ]},

    # ── 4. Hallway ───────────────────────────────────────────────────────
    # Push bottom-row boxes left (they fill the three targets).
    # Then push top box right×3.
    {"name": "Hallway", "map": [
        "  #####",
        "###   #",
        "#@$...#",
        "###$$$#",
        "  #   #",
        "  #####",
    ]},

    # ── 5. L-Shape (FIXED) ───────────────────────────────────────────────
    # Two boxes in a column; push each one right onto its target.
    # Simple back-to-back pushes, no deadlock possible.
    {"name": "L-Shape", "map": [
        "########",
        "#      #",
        "# $..  #",
        "# $..  #",
        "#      #",
        "#  @   #",
        "########",
    ]},

    # ── 6. Cross (FIXED) ─────────────────────────────────────────────────
    # Four boxes in a plus shape; each target is in an arm of the cross.
    # Player starts in centre with room to walk behind every box.
    {"name": "Cross", "map": [
        "   ###   ",
        "####.####",
        "#..$@$..#",
        "####.####",
        "   ###   ",
    ]},

    # ── 7. Spiral (FIXED) ────────────────────────────────────────────────
    # Three boxes are in the outer ring where the player can reach them.
    # Targets are inside the inner chamber reachable via the open bottom gap.
    {"name": "Spiral", "map": [
        "#########",
        "#@$      #",
        "# #####  #",
        "# #...#  #",
        "# #   #  #",
        "# ##$##  #",
        "#    $   #",
        "#        #",
        "##########",
    ]},

    # ── 8. Tricky (FIXED) ────────────────────────────────────────────────
    # Removed the box that was permanently stuck in a corner.
    # Four boxes, four targets — all reachable.
    {"name": "Tricky", "map": [
        "########",
        "#  .   #",
        "#      #",
        "#  $   #",
        "## ### #",
        "# @$ . #",
        "#   $  #",
        "# . .  #",
        "########",
    ]},

    # ── 9. Warehouse ─────────────────────────────────────────────────────
    # 6 boxes, 6 targets arranged symmetrically.
    # All boxes have clear push paths; no corner deadlocks.
    {"name": "Warehouse", "map": [
        "##########",
        "#        #",
        "# .$$$.. #",
        "# $    $ #",
        "# ..$$.. #",
        "#   @    #",
        "##########",
    ]},

    # ── 10. Expert ───────────────────────────────────────────────────────
    # Multi-room layout; requires sequencing to avoid blocking.
    {"name": "Expert", "map": [
        "##########",
        "#   ##   #",
        "# $ .. $ #",
        "#  $  $  #",
        "## .$. ###",
        " # @$  #  ",
        " #  .  #  ",
        " #######  ",
    ]},
]

TILE = 48   # pixels per cell


# ── helpers ─────────────────────────────────────────────────────────────────
def parse_level(idx):
    raw = LEVELS[idx]["map"]
    rows = len(raw)
    cols = max(len(r) for r in raw)
    grid = []
    player = None
    boxes = []
    targets = []
    for r, row in enumerate(raw):
        grid.append([])
        for c in range(cols):
            ch = row[c] if c < len(row) else " "
            if ch == "@":
                player = [r, c]; grid[r].append(" ")
            elif ch == "!":
                player = [r, c]; grid[r].append("."); targets.append((r, c))
            elif ch == "$":
                boxes.append([r, c]); grid[r].append(" ")
            elif ch == "+":
                boxes.append([r, c]); grid[r].append("."); targets.append((r, c))
            elif ch == ".":
                targets.append((r, c)); grid[r].append(".")
            elif ch == "#":
                grid[r].append("#")
            else:
                grid[r].append(" ")
    return {
        "grid": grid, "player": player, "boxes": boxes,
        "targets": targets, "rows": rows, "cols": cols,
        "moves": 0, "pushes": 0,
    }


def box_at(state, r, c):
    for i, b in enumerate(state["boxes"]):
        if b[0] == r and b[1] == c:
            return i
    return -1


def target_at(state, r, c):
    return (r, c) in state["targets"]


def check_win(state):
    return all(box_at(state, t[0], t[1]) >= 0 for t in state["targets"])


def do_move(state, dr, dc, history):
    grid = state["grid"]
    pr, pc = state["player"]
    nr, nc = pr + dr, pc + dc
    if nr < 0 or nr >= state["rows"] or nc < 0 or nc >= state["cols"]:
        return False
    if grid[nr][nc] == "#":
        return False
    bi = box_at(state, nr, nc)
    if bi >= 0:
        br2, bc2 = nr + dr, nc + dc
        if (br2 < 0 or br2 >= state["rows"] or bc2 < 0 or bc2 >= state["cols"]
                or grid[br2][bc2] == "#" or box_at(state, br2, bc2) >= 0):
            return False
        history.append(copy.deepcopy({"player": state["player"], "boxes": state["boxes"]}))
        state["boxes"][bi] = [br2, bc2]
        state["pushes"] += 1
    else:
        history.append(copy.deepcopy({"player": state["player"], "boxes": state["boxes"]}))
    state["player"] = [nr, nc]
    state["moves"] += 1
    return True


def undo_move(state, history):
    if not history:
        return
    prev = history.pop()
    state["player"] = prev["player"]
    state["boxes"] = prev["boxes"]
    state["moves"] = max(0, state["moves"] - 1)


# ── drawing ──────────────────────────────────────────────────────────────────
def draw_wall(surf, x, y, ts):
    pygame.draw.rect(surf, WALL_DARK, (x, y, ts, ts))
    pygame.draw.rect(surf, WALL_MID,  (x+1, y+1, ts-2, ts//2-1))
    pygame.draw.rect(surf, WALL_DARK, (x+1, y+ts//2, ts-2, ts//2-1))
    pygame.draw.rect(surf, WALL_HI,   (x+1, y+1, ts-2, 2))
    pygame.draw.rect(surf, (20, 20, 35), (x, y, ts, ts), 1)


def draw_floor(surf, x, y, ts, is_target):
    pygame.draw.rect(surf, FLOOR, (x, y, ts, ts))
    if is_target:
        cx, cy = x + ts // 2, y + ts // 2
        r = int(ts * 0.28)
        pygame.draw.circle(surf, TARGET_C, (cx, cy), r, 2)
        pygame.draw.line(surf, TARGET_C, (cx - r//2, cy), (cx + r//2, cy), 2)
        pygame.draw.line(surf, TARGET_C, (cx, cy - r//2), (cx, cy + r//2), 2)


def draw_box(surf, x, y, ts, on_target):
    p = max(3, ts // 8)
    body = BOX_DONE if on_target else BOX_BODY
    hi   = BOX_DONE_HI if on_target else BOX_HI
    sh   = BOX_DONE_SH if on_target else BOX_SH
    pygame.draw.rect(surf, sh,   (x+p+2, y+p+3, ts-p*2-2, ts-p*2-2), border_radius=3)
    pygame.draw.rect(surf, body, (x+p,   y+p,   ts-p*2,   ts-p*2),   border_radius=3)
    pygame.draw.rect(surf, hi,   (x+p+2, y+p+2, ts-p*2-4, ts//4),    border_radius=3)
    if on_target:
        cx, cy = x + ts//2, y + ts//2
        s = ts * 0.18
        pts = [(cx-s, cy), (cx-s*0.3, cy+s*0.7), (cx+s, cy-s*0.6)]
        pygame.draw.lines(surf, (180, 255, 200), False,
                          [(int(a), int(b)) for a, b in pts], 2)
    else:
        pygame.draw.rect(surf, sh, (x+p+4, y+p+4, ts-p*2-8, ts-p*2-8), 1, border_radius=2)


def draw_player(surf, x, y, ts):
    cx, cy = x + ts // 2, y + ts // 2
    r = int(ts * 0.26)
    pygame.draw.circle(surf, PLAYER_B, (cx, cy + r//4), int(r * 1.1))
    pygame.draw.circle(surf, PLAYER_H, (cx, cy), r)
    pygame.draw.circle(surf, PLAYER_SK, (cx, cy - r//6), int(r * 0.55))
    pygame.draw.rect(surf, PLAYER_HAT, (cx - int(r*0.62), cy - int(r*0.9),
                                         int(r*1.24), int(r*0.55)))
    pygame.draw.rect(surf, PLAYER_HAT, (cx - int(r*0.4), cy - int(r*1.3),
                                         int(r*0.8), int(r*0.45)))


def draw_level(surf, state, ox, oy, ts):
    grid = state["grid"]
    for r in range(state["rows"]):
        for c in range(state["cols"]):
            x, y = ox + c * ts, oy + r * ts
            cell = grid[r][c] if c < len(grid[r]) else " "
            if cell == "#":
                draw_wall(surf, x, y, ts)
            else:
                draw_floor(surf, x, y, ts, target_at(state, r, c))
    for b in state["boxes"]:
        draw_box(surf, ox + b[1]*ts, oy + b[0]*ts, ts, target_at(state, b[0], b[1]))
    pr, pc = state["player"]
    draw_player(surf, ox + pc*ts, oy + pr*ts, ts)


# ── UI helpers ────────────────────────────────────────────────────────────────
def draw_text(surf, text, font, color, cx, cy, anchor="center"):
    img = font.render(text, True, color)
    r = img.get_rect()
    if anchor == "center":
        r.center = (cx, cy)
    elif anchor == "midleft":
        r.midleft = (cx, cy)
    elif anchor == "midright":
        r.midright = (cx, cy)
    surf.blit(img, r)
    return r


def draw_button(surf, rect, label, font, hover=False):
    col = (40, 40, 60) if hover else (25, 25, 40)
    pygame.draw.rect(surf, col, rect, border_radius=4)
    pygame.draw.rect(surf, TEXT_GOLD, rect, 1, border_radius=4)
    draw_text(surf, label, font, TEXT_GOLD, rect.centerx, rect.centery)


def overlay_surface(surf):
    ov = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
    ov.fill(OVERLAY)
    surf.blit(ov, (0, 0))


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    pygame.display.set_caption("SOKOBAN")

    def load_font(size):
        for name in ["Courier New", "Consolas", "monospace", None]:
            try:
                return pygame.font.SysFont(name, size, bold=(name is None))
            except Exception:
                pass
        return pygame.font.Font(None, size)

    font_title  = load_font(28)
    font_hud    = load_font(20)
    font_small  = load_font(16)
    font_btn    = load_font(15)
    font_tiny   = load_font(13)

    WIN_W, WIN_H = 900, 680
    screen = pygame.display.set_mode((WIN_W, WIN_H), pygame.RESIZABLE)
    clock  = pygame.time.Clock()

    current_level = 0
    state = parse_level(current_level)
    history = []
    completed = set()

    SCENE_MENU  = "menu"
    SCENE_GAME  = "game"
    SCENE_WIN   = "win"
    scene = SCENE_MENU

    key_repeat_timer = {}

    def start_level(idx):
        nonlocal state, history, current_level, scene
        current_level = idx
        state = parse_level(idx)
        history = []
        scene = SCENE_GAME

    while True:
        W, H = screen.get_size()
        mouse = pygame.mouse.get_pos()
        clicks = []

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.VIDEORESIZE:
                pass
            if event.type == pygame.KEYDOWN:
                key_repeat_timer[event.key] = pygame.time.get_ticks()
                if scene == SCENE_GAME:
                    moved = False
                    if event.key in (pygame.K_UP, pygame.K_w):
                        moved = do_move(state, -1, 0, history)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        moved = do_move(state, 1, 0, history)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        moved = do_move(state, 0, -1, history)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        moved = do_move(state, 0, 1, history)
                    elif event.key == pygame.K_z:
                        undo_move(state, history)
                    elif event.key == pygame.K_r:
                        start_level(current_level)
                    elif event.key == pygame.K_ESCAPE:
                        scene = SCENE_MENU
                    if moved and check_win(state):
                        completed.add(current_level)
                        scene = SCENE_WIN
                elif scene == SCENE_MENU:
                    if event.key == pygame.K_RETURN:
                        start_level(0)
                elif scene == SCENE_WIN:
                    if event.key == pygame.K_RETURN:
                        if current_level + 1 < len(LEVELS):
                            start_level(current_level + 1)
                        else:
                            scene = SCENE_MENU
                    elif event.key == pygame.K_r:
                        start_level(current_level)
            if event.type == pygame.KEYUP:
                key_repeat_timer.pop(event.key, None)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                clicks.append(event.pos)

        now = pygame.time.get_ticks()
        if scene == SCENE_GAME:
            for k, t0 in list(key_repeat_timer.items()):
                elapsed = now - t0
                if elapsed > 200:
                    interval = 80
                    moved = False
                    if k == pygame.K_UP or k == pygame.K_w:
                        moved = do_move(state, -1, 0, history)
                    elif k == pygame.K_DOWN or k == pygame.K_s:
                        moved = do_move(state, 1, 0, history)
                    elif k == pygame.K_LEFT or k == pygame.K_a:
                        moved = do_move(state, 0, -1, history)
                    elif k == pygame.K_RIGHT or k == pygame.K_d:
                        moved = do_move(state, 0, 1, history)
                    if moved:
                        key_repeat_timer[k] = now - interval
                        if check_win(state):
                            completed.add(current_level)
                            scene = SCENE_WIN

        screen.fill(BG)

        # ── MENU ───────────────────────────────────────────────────────────
        if scene == SCENE_MENU:
            draw_text(screen, "SOKOBAN", font_title, TEXT_GOLD, W//2, H//4)
            draw_text(screen, "Push all crates onto the red targets",
                      font_small, TEXT_GRAY, W//2, H//4 + 44)

            n = len(LEVELS)
            cols_g = min(5, n)
            rows_g = (n + cols_g - 1) // cols_g
            bw, bh, gap = 100, 44, 10
            gw = cols_g * (bw + gap) - gap
            gx0 = W // 2 - gw // 2
            gy0 = H // 2 - (rows_g * (bh + gap)) // 2

            for i, lv in enumerate(LEVELS):
                col_i = i % cols_g
                row_i = i // cols_g
                bx = gx0 + col_i * (bw + gap)
                by = gy0 + row_i * (bh + gap)
                rect = pygame.Rect(bx, by, bw, bh)
                hover = rect.collidepoint(mouse)
                done  = i in completed
                border_col = (78, 201, 78) if done else (TEXT_GOLD if hover else (60, 60, 80))
                bg_col = (20, 40, 20) if done else ((40, 40, 60) if hover else (20, 20, 35))
                pygame.draw.rect(screen, bg_col, rect, border_radius=4)
                pygame.draw.rect(screen, border_col, rect, 1, border_radius=4)
                num_col = GREEN_HUD if done else (TEXT_GOLD if hover else TEXT_WHITE)
                draw_text(screen, str(i+1), font_hud, num_col, bx+bw//2, by+bh//2-8)
                draw_text(screen, lv["name"], font_tiny, TEXT_GRAY, bx+bw//2, by+bh//2+10)
                if click_in(clicks, rect):
                    start_level(i)

            draw_text(screen, "↑↓←→ / WASD  move  ·  Z  undo  ·  R  reset  ·  ESC  menu",
                      font_tiny, TEXT_GRAY, W//2, H - 30)

        # ── GAME ───────────────────────────────────────────────────────────
        elif scene == SCENE_GAME:
            ts = min(TILE, (W - 40) // state["cols"], (H - 120) // state["rows"])
            ts = max(ts, 16)
            gw = state["cols"] * ts
            gh = state["rows"] * ts
            ox = (W - gw) // 2
            oy = 80 + (H - 120 - gh) // 2

            done_boxes = sum(1 for t in state["targets"] if box_at(state, t[0], t[1]) >= 0)
            total_boxes = len(state["targets"])
            hud_y = 30
            hud_items = [
                (f"LVL {current_level+1}/{len(LEVELS)}", W//2 - 220),
                (f"MOVES {state['moves']}", W//2 - 80),
                (f"PUSHES {state['pushes']}", W//2 + 60),
                (f"BOXES {done_boxes}/{total_boxes}", W//2 + 200),
            ]
            for label, hx in hud_items:
                draw_text(screen, label, font_hud, TEXT_GOLD, hx, hud_y)
            draw_text(screen, LEVELS[current_level]["name"],
                      font_small, TEXT_GRAY, W//2, 55)

            draw_level(screen, state, ox, oy, ts)

            draw_text(screen, "Z=UNDO  R=RESET  ESC=MENU",
                      font_tiny, TEXT_GRAY, W//2, H - 18)

            btn_undo = pygame.Rect(W//2 - 130, H - 52, 110, 28)
            btn_reset= pygame.Rect(W//2 + 20,  H - 52, 110, 28)
            draw_button(screen, btn_undo,  "↩ UNDO",  font_btn, btn_undo.collidepoint(mouse))
            draw_button(screen, btn_reset, "↺ RESET", font_btn, btn_reset.collidepoint(mouse))
            if click_in(clicks, btn_undo):  undo_move(state, history)
            if click_in(clicks, btn_reset): start_level(current_level)

        # ── WIN ────────────────────────────────────────────────────────────
        elif scene == SCENE_WIN:
            ts = min(TILE, (W-40)//state["cols"], (H-120)//state["rows"])
            ts = max(ts, 16)
            gw = state["cols"]*ts; gh = state["rows"]*ts
            ox = (W-gw)//2; oy = 80+(H-120-gh)//2
            draw_level(screen, state, ox, oy, ts)

            overlay_surface(screen)
            draw_text(screen, "LEVEL CLEAR!", font_title, TEXT_GOLD, W//2, H//2 - 80)
            draw_text(screen, f"Moves: {state['moves']}   Pushes: {state['pushes']}",
                      font_hud, TEXT_WHITE, W//2, H//2 - 36)
            draw_text(screen, f"Completed: {len(completed)}/{len(LEVELS)} levels",
                      font_small, GREEN_HUD, W//2, H//2 - 4)

            btn_y = H//2 + 36
            if current_level + 1 < len(LEVELS):
                btn_next = pygame.Rect(W//2 - 130, btn_y, 120, 36)
                draw_button(screen, btn_next, "NEXT ▶", font_btn, btn_next.collidepoint(mouse))
                if click_in(clicks, btn_next):
                    start_level(current_level + 1)
            btn_retry = pygame.Rect(W//2 + 10, btn_y, 120, 36)
            draw_button(screen, btn_retry, "↺ RETRY", font_btn, btn_retry.collidepoint(mouse))
            if click_in(clicks, btn_retry): start_level(current_level)
            btn_menu = pygame.Rect(W//2 - 60, btn_y + 48, 120, 36)
            draw_button(screen, btn_menu, "MENU", font_btn, btn_menu.collidepoint(mouse))
            if click_in(clicks, btn_menu): scene = SCENE_MENU
            draw_text(screen, "ENTER=next  R=retry  ESC=menu",
                      font_tiny, TEXT_GRAY, W//2, btn_y + 100)

        pygame.display.flip()
        clock.tick(60)


def click_in(clicks, rect):
    return any(rect.collidepoint(p) for p in clicks)


if __name__ == "__main__":
    main()