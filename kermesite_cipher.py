#!/usr/bin/env python3
"""Kermesite Cipher — neon glyph-stamp arcade for ElbowOS. Python 3 + pygame."""
import os, random, subprocess, sys

RECORD = "--record" in sys.argv or os.environ.get("ELBOWOS_RECORD") == "1"
PLAY = "--play" in sys.argv
if RECORD or not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/KERMESITE_CIPHER_ElbowOS.mp4")
TITLE, HANDLE = "KERMESITE CIPHER", "x.com/ElbowOS"
OX, BONE = (32, 6, 14), (244, 230, 200)
SULFUR, CRIM = (232, 196, 72), (255, 72, 98)
AQUA, WINE = (120, 255, 214), (90, 16, 36)
WORDS = ["FLARE", "EMBER", "VEIN", "GLOW", "SPARK", "ORE"]
LANES = [140, 320, 500, 680, 860]
ALPH = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


class Glyph:
    def __init__(self, lane, ch, y):
        self.lane, self.ch, self.y = lane, ch, y
        self.alive = True


class Game:
    def __init__(self):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        self.big = pygame.font.SysFont("dejavusans", 58, bold=True)
        self.mid = pygame.font.SysFont("dejavusans", 40, bold=True)
        self.glyph = pygame.font.SysFont("dejavusans", 52, bold=True)
        self.small = pygame.font.SysFont("dejavusans", 28, bold=True)
        self.reset()

    def reset(self):
        self.wi, self.prog = 0, 0
        self.lane, self.score, self.streak = 2, 0, 0
        self.t, self.flash, self.stamp = 0, 0, 0
        self.glyphs, self.sparks = [], []
        self.spawn = 8
        self.banner = "STAMP THE WORD"

    def word(self):
        return WORDS[self.wi % len(WORDS)]

    def need(self):
        w = self.word()
        return w[self.prog] if self.prog < len(w) else ""

    def stamp_now(self):
        self.stamp = 8
        need = self.need()
        hit = None
        for g in self.glyphs:
            if g.alive and g.lane == self.lane and 1080 < g.y < 1280 and g.ch == need:
                hit = g
                break
        if hit:
            hit.alive = False
            self.prog += 1
            self.streak += 1
            self.score += 80 + self.streak * 15
            self.flash = 10
            self.banner = "LOCKED"
            self.sparks.append([LANES[self.lane], 1180, AQUA, 18])
            if self.prog >= len(self.word()):
                self.score += 250
                self.wi += 1
                self.prog = 0
                self.banner = "WORD SET"
        else:
            self.streak = 0
            self.prog = max(0, self.prog - 1)
            self.banner = "MISS"
            self.sparks.append([LANES[self.lane], 1180, CRIM, 16])

    def step(self, keys=None, auto=False):
        self.t += 1
        if self.flash:
            self.flash -= 1
        if self.stamp:
            self.stamp -= 1
        if auto:
            need = self.need()
            cands = [g for g in self.glyphs if g.alive and g.ch == need and 500 < g.y < 1260]
            if cands:
                g = min(cands, key=lambda q: abs(q.y - 1180))
                if g.lane != self.lane:
                    self.lane += 1 if g.lane > self.lane else -1
                elif 1100 < g.y < 1260 and self.stamp == 0:
                    self.stamp_now()
            elif self.t % 18 == 0:
                self.lane = (self.lane + 1) % 5
        elif keys:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if self.t % 4 == 0:
                    self.lane = max(0, self.lane - 1)
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if self.t % 4 == 0:
                    self.lane = min(4, self.lane + 1)
        self.spawn -= 1
        if self.spawn <= 0:
            self.spawn = 7
            lane = random.randrange(5)
            ch = self.need() if random.random() < 0.42 else random.choice(ALPH)
            self.glyphs.append(Glyph(lane, ch, 430))
        for g in self.glyphs:
            g.y += 7.2
            if g.y > 1500:
                g.alive = False
        self.glyphs = [g for g in self.glyphs if g.alive][-40:]
        for s in self.sparks:
            s[3] -= 1
        self.sparks = [s for s in self.sparks if s[3] > 0]

    def draw(self, surf):
        surf.fill(OX)
        pygame.draw.rect(surf, WINE, (70, 300, 940, 1280), border_radius=36)
        for i, x in enumerate(LANES):
            col = SULFUR if i == self.lane else (70, 24, 36)
            pygame.draw.line(surf, col, (x, 420), (x, 1460), 6 if i == self.lane else 3)
        plate = self.word()
        for i, ch in enumerate(plate):
            on = i < self.prog
            box = pygame.Rect(240 + i * 120, 340, 100, 110)
            pygame.draw.rect(surf, AQUA if on else (50, 16, 28), box, border_radius=12)
            img = self.big.render(ch, True, OX if on else BONE)
            surf.blit(img, img.get_rect(center=box.center))
        for g in self.glyphs:
            col = AQUA if g.ch == self.need() else BONE
            tile = pygame.Rect(LANES[g.lane] - 42, int(g.y) - 42, 84, 84)
            pygame.draw.rect(surf, (48, 12, 24), tile, border_radius=10)
            pygame.draw.rect(surf, col, tile, 3, border_radius=10)
            img = self.glyph.render(g.ch, True, col)
            surf.blit(img, img.get_rect(center=tile.center))
        sx = LANES[self.lane]
        sy = 1210 + (6 if self.stamp else 0)
        pygame.draw.rect(surf, SULFUR, (sx - 70, sy, 140, 36), border_radius=8)
        pygame.draw.polygon(surf, CRIM, [(sx - 28, sy + 36), (sx + 28, sy + 36), (sx, sy + 78)])
        for s in self.sparks:
            pygame.draw.circle(surf, s[2], (int(s[0]), int(s[1])), s[3])
        title = self.big.render(TITLE, True, SULFUR)
        surf.blit(title, title.get_rect(center=(W // 2, 96)))
        score = self.mid.render(f"SCORE {self.score}", True, BONE)
        surf.blit(score, score.get_rect(center=(W // 2, 190)))
        need = self.mid.render(f"NEED {self.need()}", True, AQUA)
        surf.blit(need, need.get_rect(center=(W // 2, 250)))
        ban = self.small.render(self.banner, True, CRIM if self.banner == "MISS" else AQUA)
        surf.blit(ban, ban.get_rect(center=(W // 2, 1640)))
        handle = self.small.render(HANDLE, True, AQUA)
        surf.blit(handle, handle.get_rect(center=(W // 2, 1800)))
        hint = self.small.render("A/D move   SPACE stamp", True, SULFUR)
        surf.blit(hint, hint.get_rect(center=(W // 2, 1860)))

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            keys = pygame.key.get_pressed()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_SPACE:
                    self.stamp_now()
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    self.reset()
            self.step(keys, auto=False)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

    def record(self):
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-an",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20",
            "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frame = pygame.Surface((W, H))
        try:
            for _ in range(FPS * SECS):
                self.step(auto=True)
                self.draw(frame)
                proc.stdin.write(pygame.image.tobytes(frame, "RGB"))
        finally:
            proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore")
        rc = proc.wait()
        if rc != 0:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1200:]}")
        print("wrote", OUT, "score", self.score)
        pygame.quit()


def main():
    g = Game()
    if PLAY and not RECORD:
        g.play_interactive()
    else:
        g.record()


if __name__ == "__main__":
    main()
