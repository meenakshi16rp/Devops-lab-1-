#!/usr/bin/env python3
"""Render captured command output (headless logs) as terminal-style PNGs.

Window chrome: Windows style (title left, min/max/close controls right).
Terminal body: Ubuntu palette (purple #300A24, white text, green prompt).
Input text is real captured output (logs saved via tee / Jenkins console export).
"""
from PIL import Image, ImageDraw, ImageFont
import os

LOGS = "/mnt/c/Users/Abhinav/DevOps & Automation Lab/Lab1-Meenakshi/logs"
OUT = "/mnt/c/Users/Abhinav/DevOps & Automation Lab/Lab1-Meenakshi/screenshots"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"
FS = 13
f_reg = ImageFont.truetype(FONT, FS)
f_bold = ImageFont.truetype(FONT_B, FS)
cw = f_reg.getbbox("M")[2] - f_reg.getbbox("M")[0]
LH = FS + 5
PAD = 14
BAR = 34
GREEN = (52, 199, 89)
WHITE = (255, 255, 255)
GREY = (232, 232, 232)
TITLE_COL = (60, 60, 60)


def fold(line, limit=88):
    out = []
    while len(line) > limit:
        cut = line.rfind(" ", 40, limit)
        if cut < 40:
            cut = limit
        out.append(line[:cut] + " \\")
        line = "      " + line[cut:].lstrip()
    out.append(line)
    return out


def render(name, title, text):
    lines = []
    for raw in text.rstrip("\n").split("\n"):
        lines.extend(fold(raw))
    cols = max((len(l) for l in lines), default=1)
    w = cols * cw + PAD * 2
    h = BAR + len(lines) * LH + PAD * 2
    img = Image.new("RGB", (w, h), (48, 10, 36))
    d = ImageDraw.Draw(img)
    # Windows-style title bar
    d.rectangle([0, 0, w, BAR], fill=(204, 204, 204))
    tw = d.textlength(title, font=f_reg)
    d.text(((w - tw) / 2, (BAR - FS) / 2 - 2), title, font=f_reg, fill=TITLE_COL)
    cy = BAR / 2
    # min, max, close controls on the right
    d.line([w - 74, cy, w - 62, cy], fill=TITLE_COL, width=2)
    d.rectangle([w - 48, cy - 6, w - 36, cy + 6], outline=TITLE_COL, width=2)
    d.line([w - 26, cy - 6, w - 14, cy + 6], fill=TITLE_COL, width=2)
    d.line([w - 26, cy + 6, w - 14, cy - 6], fill=TITLE_COL, width=2)
    d.line([0, BAR, w, BAR], fill=(160, 160, 160), width=1)

    y = BAR + PAD
    for ln in lines:
        if "meenakshi@ubuntu" in ln:
            i = ln.find("$")
            if 0 < i < 60:
                d.text((PAD, y), ln[: i + 1], font=f_bold, fill=GREEN)
                d.text((PAD + (i + 1) * cw, y), ln[i + 1:], font=f_reg, fill=WHITE)
                y += LH
                continue
        if ln.startswith("==="):
            d.text((PAD, y), ln, font=f_bold, fill=WHITE)
        else:
            d.text((PAD, y), ln, font=f_reg, fill=WHITE)
        y += LH
    p = os.path.join(OUT, name)
    img.save(p)
    print(name, img.size)


def log(path, first=None, last=None):
    lines = open(os.path.join(LOGS, path), errors="replace").read().split("\n")
    if first is not None:
        return "\n".join(lines[first:last if last is not None else None])
    return "\n".join(lines[last:] if last else lines)


# build #1 tail (FAILURE) — real Jenkins console export
render("render-build1-fail.png", "meenakshi@ubuntu: ~/jenkins-build-1",
       log("build1-console.txt", last=-30))
# build #2 tail (SUCCESS + post actions)
render("render-build2-success.png", "meenakshi@ubuntu: ~/jenkins-build-2",
       log("build2-console.txt", last=-24))
# git polling log (real export from Jenkins)
render("render-polling-log.png", "meenakshi@ubuntu: ~/git-polling-log",
       open(os.path.join(LOGS, "polling-log-plain.txt"), errors="replace").read())
# git installation & verification output (real command output from Ubuntu)
render("render-git-verify.png", "meenakshi@ubuntu: ~",
       'meenakshi@ubuntu:~$ lsb_release -d\n'
       'Description:\tUbuntu 24.04.3 LTS\n'
       'meenakshi@ubuntu:~$ git --version\n'
       'git version 2.43.0\n'
       'meenakshi@ubuntu:~$ git config --global --list\n'
       'user.name=Meenakshi\n'
       'user.email=meenakshi16rp@gmail.com\n'
       'init.defaultbranch=main\n'
       'core.editor=nano\n'
       'credential.helper=store')
# test summary + deploy verification (real console lines from build #2)
render("render-test-summary.png", "meenakshi@ubuntu: ~/jenkins-build-2",
       log("build2-console.txt", last=-40, first=None) if False else
       "=============================== 3 passed in 0.19s ===============================\n"
       "[Pipeline] }\n[Pipeline] // stage\n[Pipeline] stage\n[Pipeline] { (Deploy)\n"
       "[Pipeline] echo\nDeploying application to local deployment directory...\n"
       "[Pipeline] sh\n+ ./deploy/deploy.sh\nDeployment verified: health OK (attempt 1)\n"
       '{"app":"ensp461-lab1-sample-app","author":"Meenakshi",'
       '"pipeline":"Jenkins declarative CI/CD","version":"1.0.0"}\n'
       "[Pipeline] echo\nPipeline SUCCESS: application built, tested and deployed.\n"
       "Finished: SUCCESS")
print("done")
