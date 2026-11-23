#!/usr/bin/env python3
"""Herz 2.0 backend (Data Structures course project).

Run:  python server.py [port]      then open  http://localhost:8000

Every graph algorithm below is written by hand (no networkx, no heapq):
adjacency lists, BFS, DFS, connected components, Dijkstra, Kruskal with
union-find, Prim, cycle detection, bipartite check, Welsh-Powell coloring,
Euler test, triangle counting and the friend-recommendation score.
The browser (index.html + style.css + app.js) only draws; it asks this
server for every result through the /api/... endpoints.
"""
import json, math, os, sys, threading
from collections import deque
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# ----------------------------------------------------------------- data
NAMES = "Aarav Diya Rohan Priya Kabir Isha Vihaan Anaya Arjun Meera Sai Neha Aditya Riya Karan Tara Yash Sneha Dev Mira".split()
# interest indexes: 0 Sports 1 Movies 2 Music 3 Gaming 4 Tech 5 Travel
INTERESTS = "03,12,04,25,03,15,34,12,04,25,34,12,03,15,04,25,34,15,03,24".split(",")
EDGES = [(0, 2), (0, 4), (2, 4), (0, 12), (4, 12), (2, 8), (8, 14), (12, 18), (1, 3), (1, 5), (3, 5), (1, 7), (3, 11),
         (7, 11), (5, 13), (13, 17), (9, 13), (6, 10), (6, 16), (10, 16), (10, 15), (8, 6), (11, 9), (15, 19), (14, 16), (7, 9)]
SEED = len(NAMES)  # ids below SEED are sample people who answer automatically
REPLIES = ["Haha nice!", "Tell me more 😄", "Same here!", "Sounds good, let’s catch up soon."]


# ------------------------------------------------- data structure: union-find
class DisjointSet:
    """Union-find with path compression. Used by Kruskal."""
    def __init__(self, n):
        self.p = list(range(n))

    def find(self, x):
        if self.p[x] != x:
            self.p[x] = self.find(self.p[x])
        return self.p[x]

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        self.p[ra] = rb
        return True


# ------------------------------------------------------------------- graph
class Graph:
    """Undirected graph as adjacency lists. Each list is a dict used as an
    insertion-ordered set, so membership is O(1) and traversal order is stable."""

    def __init__(self):
        self.users, self.adj = [], []

    # --- representation
    def add_user(self, name, email, interests):
        self.users.append({"n": name, "e": email, "i": interests})
        self.adj.append({})
        return len(self.users) - 1

    def add_edge(self, a, b):
        if a != b:
            self.adj[a][b] = True
            self.adj[b][a] = True

    def n(self): return len(self.adj)
    def degree(self, u): return len(self.adj[u])

    def edges(self):
        return [(a, b) for a in range(self.n()) for b in self.adj[a] if a < b]

    def adjacency_list(self):
        return [f"{i} {self.users[i]['n']}: {', '.join(map(str, self.adj[i]))}" for i in range(self.n())]

    def adjacency_matrix(self):
        return [[1 if j in self.adj[i] else 0 for j in range(self.n())] for i in range(self.n())]

    # --- edge weight: 1 + number of interests the two people do not share
    def shared(self, a, b):
        return sum(1 for x in self.users[a]["i"] if x in self.users[b]["i"])

    def weight(self, a, b):
        return 1 + len(self.users[a]["i"]) + len(self.users[b]["i"]) - 2 * self.shared(a, b)

    # --- traversals, O(V + E)
    def bfs(self, s):
        order, dist, parent, q = [s], {s: 0}, {}, deque([s])
        while q:
            u = q.popleft()
            for v in self.adj[u]:
                if v not in dist:
                    dist[v], parent[v] = dist[u] + 1, u
                    order.append(v)
                    q.append(v)
        return order, dist, parent

    def dfs(self, s):
        order, seen = [], set()

        def visit(u):
            seen.add(u)
            order.append(u)
            for v in self.adj[u]:
                if v not in seen:
                    visit(v)
        visit(s)
        return order

    def components(self):
        comp, k = [-1] * self.n(), 0
        for i in range(self.n()):
            if comp[i] < 0:
                for x in self.bfs(i)[0]:
                    comp[x] = k
                k += 1
        return comp, k

    # --- shortest paths
    def shortest_path(self, s, t):
        """Unweighted shortest path (BFS parents)."""
        _, dist, parent = self.bfs(s)
        if t not in dist:
            return None
        p = [t]
        while p[0] != s:
            p.insert(0, parent[p[0]])
        return p

    def dijkstra(self, s, t):
        """Weighted shortest path, array version, O(V^2)."""
        INF, n = float("inf"), self.n()
        D, P, done = [INF] * n, {}, set()
        D[s] = 0
        while True:
            u = -1
            for i in range(n):
                if i not in done and D[i] < INF and (u < 0 or D[i] < D[u]):
                    u = i
            if u < 0:
                break
            done.add(u)
            for v in self.adj[u]:
                nd = D[u] + self.weight(u, v)
                if nd < D[v]:
                    D[v], P[v] = nd, u
        if D[t] == INF:
            return None
        p = [t]
        while p[0] != s:
            p.insert(0, P[p[0]])
        return p, D[t]

    # --- minimum spanning trees
    def kruskal(self):
        ds, tree, total = DisjointSet(self.n()), [], 0
        for a, b in sorted(self.edges(), key=lambda e: self.weight(*e)):
            if ds.union(a, b):
                tree.append((a, b))
                total += self.weight(a, b)
        return tree, total

    def prim(self, s):
        order, seen, tree, total = [s], {s}, [], 0
        while True:
            best = None
            for u in order:
                for v in self.adj[u]:
                    if v not in seen and (best is None or self.weight(u, v) < best[2]):
                        best = (u, v, self.weight(u, v))
            if best is None:
                break
            order.append(best[1])
            seen.add(best[1])
            tree.append((best[0], best[1]))
            total += best[2]
        return tree, total

    # --- structure tests
    def find_cycle(self):
        seen, found = set(), [None]

        def go(u, parent, stack):
            seen.add(u)
            stack.append(u)
            for x in self.adj[u]:
                if found[0]:
                    return
                if x == parent:
                    continue
                if x in seen:
                    found[0] = stack[stack.index(x):]
                    return
                go(x, u, stack)
            stack.pop()
        for i in range(self.n()):
            if found[0]:
                break
            if i not in seen:
                go(i, -1, [])
        return found[0]

    def bipartite(self):
        color, ok = {}, True
        for s in range(self.n()):
            if s in color:
                continue
            color[s], q, k = 0, [s], 0
            while k < len(q):
                u = q[k]
                k += 1
                for v in self.adj[u]:
                    if v not in color:
                        color[v] = 1 - color[u]
                        q.append(v)
                    elif color[v] == color[u]:
                        ok = False
        return ok, color

    def welsh_powell(self):
        color = {}
        for u in sorted(range(self.n()), key=lambda x: -self.degree(x)):
            used = {color[v] for v in self.adj[u] if v in color}
            k = 0
            while k in used:
                k += 1
            color[u] = k
        return color

    def triangles(self):
        return sum(1 for a, b in self.edges() for z in self.adj[a] if z in self.adj[b]) // 3

    # --- statistics shown in the Graph Lab
    def stats(self):
        V, M, k = self.n(), len(self.edges()), self.components()[1]
        return [["Vertices |V|", V], ["Edges |E|", M], ["Sum of degrees", f"{2 * M} = 2|E|"],
                ["Average degree", f"{2 * M / V:.2f}"], ["Components", k], ["Triangles", self.triangles()],
                ["Planar bound E ≤ 3V−6", "holds" if M <= 3 * V - 6 else "violated"],
                ["Is a tree?", "yes" if k == 1 and M == V - 1 else "no"]]

    # --- friend recommendation: mutual friends + Adamic-Adar + Jaccard on interests
    def recommend(self, me):
        _, dist, _ = self.bfs(me)
        rows = []
        for v in range(self.n()):
            if v == me:
                continue
            mutual = [z for z in self.adj[me] if z in self.adj[v]]
            s = self.shared(me, v)
            jac = s / (len(self.users[me]["i"]) + len(self.users[v]["i"]) - s)
            aa = sum(1 / math.log(self.degree(z)) for z in mutual)
            score = (-9 if v in self.adj[me] else 0) + 2 * aa + 3 * jac
            rows.append({"v": v, "N": mutual, "s": s, "d": dist.get(v), "sc": score})
        rows.sort(key=lambda r: -r["sc"])
        return rows


# ------------------------------------------- Graph Lab: one function per button
def run_algorithm(g, algo, a, b):
    nm = lambda x: g.users[x]["n"]
    L = lambda l: " → ".join(nm(x) for x in l)
    links = lambda l: [(l[i], l[i + 1]) for i in range(len(l) - 1)]
    nodes, edges, colors, out = [], [], None, "Unknown algorithm."
    if algo == "bfs":
        order, dist, parent = g.bfs(a)
        nodes, edges = order, [(x, parent[x]) for x in order if x != a]
        out = (f"BFS from {nm(a)}, visit order with hops:\n" + ", ".join(f"{nm(x)}={dist[x]}" for x in order)
               + f"\nReaches {len(order)} of {g.n()} people. Bold edges form the BFS tree.")
    elif algo == "dfs":
        nodes = g.dfs(a)
        out = f"DFS from {nm(a)}, visit order:\n{L(nodes)}"
    elif algo == "comp":
        comp, k = g.components()
        colors = {i: c for i, c in enumerate(comp)}
        out = f"{k} connected component(s). Same color means reachable from each other.\n" + "\n".join(
            "• " + ", ".join(nm(i) for i, c in enumerate(comp) if c == q) for q in range(k))
    elif algo == "sp":
        p = g.shortest_path(a, b)
        if p:
            nodes, edges = p, links(p)
            out = f"Shortest path by BFS: {L(p)}\n{len(p) - 1} hop(s), i.e. degrees of separation."
        else:
            out = f"No path between {nm(a)} and {nm(b)}: different components."
    elif algo == "dij":
        r = g.dijkstra(a, b)
        if r:
            nodes, edges = r[0], links(r[0])
            out = f"Dijkstra (weighted by shared interests):\n{L(r[0])}\nTotal weight {r[1]}. Lower means a closer circle."
        else:
            out = "No path: different components."
    elif algo in ("kru", "pri"):
        tree, total = g.kruskal() if algo == "kru" else g.prim(a)
        edges, nodes = tree, sorted({x for e in tree for x in e}, key=lambda x: [y for e in tree for y in e].index(x))
        head = ("Kruskal (sorted edges + union-find), spanning forest" if algo == "kru"
                else f"Prim from {nm(a)}, spanning tree of its component")
        out = f"{head}:\n{len(tree)} edges, total weight {total}\n" + ", ".join(f"{nm(x)}–{nm(y)} ({g.weight(x, y)})" for x, y in tree)
    elif algo == "cyc":
        f = g.find_cycle()
        if f:
            nodes, edges = f, links(f + [f[0]])
            out = f"Cycle found via a DFS back edge: {L(f + [f[0]])}\nLength {len(f)}."
        else:
            out = "No cycle: the graph is a forest."
    elif algo == "bip":
        ok, c = g.bipartite()
        colors = c if ok else None
        out = ("Bipartite: the graph is 2-colorable and has no odd cycle." if ok
               else "Not bipartite: it contains an odd cycle, for example a friend triangle.")
    elif algo == "eul":
        odd = [i for i in range(g.n()) if g.degree(i) % 2]
        comp, _ = g.components()
        nc = len({comp[i] for i in range(g.n()) if g.degree(i)})
        nodes = odd
        out = f"Odd-degree vertices (highlighted): {len(odd)}\n" + (
            "Edges span more than one component, so no Euler trail or circuit." if nc > 1 else
            "Euler circuit exists." if not odd else
            "Euler trail exists (not a circuit): it starts and ends at the highlighted people." if len(odd) == 2 else
            "No Euler trail or circuit.")
    elif algo == "col":
        colors = g.welsh_powell()
        out = (f"Welsh–Powell greedy coloring uses {max(colors.values()) + 1} colors. People with the same color are "
               "never direct friends, so each color is an independent set, useful for forming teams with no existing friendships.")
    return {"out": out, "nodes": nodes, "edges": [list(e) for e in edges], "colors": colors}


# --------------------------------------------- social layer (requests, chat)
G, LOCK = Graph(), threading.RLock()
PENDING, CHATS = set(), {}          # PENDING holds (from, to); CHATS maps a sorted pair to messages


def pair(a, b): return (a, b) if a < b else (b, a)


def say(frm, to, text): CHATS.setdefault(pair(frm, to), []).append({"f": frm, "t": text})


def seed():
    for name, ints in zip(NAMES, INTERESTS):
        G.add_user(name, "", [int(c) for c in ints])
    for a, b in EDGES:
        G.add_edge(a, b)


def login(name, email, interests):
    for i, u in enumerate(G.users):
        if u["e"].lower() == email.lower():
            return i                      # same email logs back into the same account
    me = G.add_user(name, email, interests)
    PENDING.update({(2, me), (9, me)})    # two sample people have already sent you a request
    return me


def accept(frm, to, greeter, text):
    PENDING.discard((frm, to))
    G.add_edge(frm, to)
    say(greeter, frm if greeter == to else to, text)


def auto_accept(me, to):
    with LOCK:
        if (me, to) in PENDING:
            accept(me, to, to, "Thanks for connecting! 👋")


def auto_reply(me, to, k):
    with LOCK:
        say(to, me, REPLIES[k % len(REPLIES)])


def send_request(me, to):
    if to == me or to in G.adj[me] or (me, to) in PENDING:
        return
    if (to, me) in PENDING:               # they already asked you: connect immediately
        return accept(to, me, to, "Hey, glad we’re connected 🙂")
    PENDING.add((me, to))
    if to < SEED:
        threading.Timer(1.5, auto_accept, (me, to)).start()


def send_chat(me, to, text):
    if to not in G.adj[me] or not text.strip():
        return
    say(me, to, text.strip()[:500])
    if to < SEED:
        threading.Timer(0.9, auto_reply, (me, to, len(CHATS[pair(me, to)]))).start()


def state(me):
    return {"users": [{"n": u["n"], "i": u["i"]} for u in G.users], "edges": [list(e) for e in G.edges()],
            "incoming": sorted(f for f, t in PENDING if t == me), "outgoing": sorted(t for f, t in PENDING if f == me),
            "chats": {str(f): CHATS.get(pair(me, f), []) for f in G.adj[me]}}


# ---------------------------------------------------------------- HTTP layer
def uid(x):
    x = int(x)
    if not 0 <= x < G.n():
        raise ValueError("bad user id")
    return x


def handle(path, q, b):
    arg = lambda k: uid(q[k][0])
    if path == "login":
        name, email = str(b["name"]).strip()[:40], str(b["email"]).strip()[:80]
        interests = [int(x) for x in b["interests"] if 0 <= int(x) < 6]
        if not name or "@" not in email or not interests:
            raise ValueError("bad login")
        return {"me": login(name, email, interests)}
    if path == "state": return state(arg("me"))
    if path == "recommendations": return G.recommend(arg("me"))
    if path == "request": return send_request(uid(b["me"]), uid(b["to"])) or {"ok": True}
    if path == "accept":
        me, frm = uid(b["me"]), uid(b["from"])
        if (frm, me) in PENDING:
            accept(frm, me, frm, "Hey, glad we’re connected 🙂")
        return {"ok": True}
    if path == "decline":
        PENDING.discard((uid(b["from"]), uid(b["me"])))
        return {"ok": True}
    if path == "chat": return send_chat(uid(b["me"]), uid(b["to"]), str(b["text"])) or {"ok": True}
    if path == "graph/stats":
        return {"stats": G.stats(), "adj_list": G.adjacency_list(), "matrix": G.adjacency_matrix()}
    if path == "graph/run": return run_algorithm(G, q["algo"][0], arg("a"), arg("b"))
    raise KeyError(path)


BASE = os.path.dirname(os.path.abspath(__file__))


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=BASE, **k)

    def log_message(self, *a): pass

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def reply(self, obj, code=200):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def api(self, query, body):
        try:
            with LOCK:
                self.reply(handle(urlparse(self.path).path[5:], query, body))
        except (ValueError, KeyError, IndexError, TypeError):
            self.reply({"error": "bad request"}, 400)

    def do_GET(self):
        if self.path.startswith("/api/"):
            return self.api(parse_qs(urlparse(self.path).query), None)
        super().do_GET()

    def do_POST(self):
        size = int(self.headers.get("Content-Length") or 0)
        try:
            body = json.loads(self.rfile.read(size) or b"{}")
        except ValueError:
            return self.reply({"error": "bad json"}, 400)
        self.api({}, body)


if __name__ == "__main__":
    seed()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Herz 2.0 running: http://localhost:{port}  (other devices on your Wi-Fi can use this PC’s IP address)")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
