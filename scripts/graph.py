"""draws assets/graph.svg: last 31 days of contributions as a smooth line chart."""
import json, os, urllib.request

USER = os.environ.get("GH_USER", "gregpierre")
TOKEN = os.environ["GH_TOKEN"]
DAYS = 31
W, H = 1200, 420
L, R, T, B = 70, 30, 70, 60

query = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{
weeks{contributionDays{date contributionCount}}}}}}"""
req = urllib.request.Request(
    "https://api.github.com/graphql",
    data=json.dumps({"query": query, "variables": {"u": USER}}).encode(),
    headers={"Authorization": f"bearer {TOKEN}", "Content-Type": "application/json"},
)
weeks = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
days = [d for w in weeks for d in w["contributionDays"]][-DAYS:]
counts = [d["contributionCount"] for d in days]

top = max(4, max(counts))
step = max(1, -(-top // 4))
top = step * 4
pw, ph = W - L - R, H - T - B
pts = [(L + i * pw / (DAYS - 1), T + ph - c / top * ph) for i, c in enumerate(counts)]

def smooth(p):
    d = f"M{p[0][0]:.1f},{p[0][1]:.1f}"
    for i in range(len(p) - 1):
        p0, p1, p2 = p[max(i - 1, 0)], p[i], p[i + 1]
        p3 = p[min(i + 2, len(p) - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        c1 = (c1[0], min(c1[1], T + ph)); c2 = (c2[0], min(c2[1], T + ph))
        d += f" C{c1[0]:.1f},{c1[1]:.1f} {c2[0]:.1f},{c2[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}"
    return d

line = smooth(pts)
area = f"{line} L{pts[-1][0]:.1f},{T + ph} L{pts[0][0]:.1f},{T + ph} Z"
font = "font-family=\"ui-monospace,SFMono-Regular,Menlo,Consolas,monospace\""

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
       '<defs><linearGradient id="a" x1="0" y1="0" x2="0" y2="1">'
       '<stop offset="0" stop-color="#c9d1d9" stop-opacity=".22"/>'
       '<stop offset="1" stop-color="#c9d1d9" stop-opacity="0"/></linearGradient></defs>',
       f'<rect width="{W}" height="{H}" rx="8" fill="#0d1117"/>',
       f'<text x="{W/2}" y="38" text-anchor="middle" fill="#c9d1d9" font-size="17" {font}>andy\'s contribution graph</text>']
for k in range(5):
    y = T + ph - k * ph / 4
    out.append(f'<line x1="{L}" y1="{y:.1f}" x2="{W-R}" y2="{y:.1f}" stroke="#21262d" stroke-width="1"/>')
    out.append(f'<text x="{L-14}" y="{y+4:.1f}" text-anchor="end" fill="#6e7681" font-size="12" {font}>{k*step}</text>')
for (x, _), d in zip(pts, days):
    out.append(f'<text x="{x:.1f}" y="{T+ph+24}" text-anchor="middle" fill="#6e7681" font-size="11" {font}>{int(d["date"][-2:])}</text>')
out.append(f'<text x="{L+pw/2}" y="{H-10}" text-anchor="middle" fill="#6e7681" font-size="12" {font}>days</text>')
out.append(f'<path d="{area}" fill="url(#a)"/>')
out.append(f'<path d="{line}" fill="none" stroke="#c9d1d9" stroke-width="2.5" stroke-linecap="round"/>')
for x, y in pts:
    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#0d1117" stroke="#f0f6fc" stroke-width="1.8"/>')
out.append("</svg>")

os.makedirs("assets", exist_ok=True)
with open("assets/graph.svg", "w") as f:
    f.write("\n".join(out))
print(f"wrote assets/graph.svg, {sum(counts)} contributions over {DAYS} days")
