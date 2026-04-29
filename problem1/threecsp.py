"""
Problem 1: 3-Color Shortest Path (3CSP).

Decide whether undirected graph G has a path from s to t of length <= k
whose vertex colors strictly alternate among the three colors {b, w, r}
(equivalently: any three consecutive vertices on the path have all three
distinct colors).

Run:
    python3 threecsp.py <input.txt>
or
    python3 threecsp.py < input.txt
"""

import sys
from collections import deque
from itertools import permutations

# Six color patterns = all 3! permutations of (b, w, r). The path's color
# sequence must be a contiguous substring of one of these cycled patterns.
PATTERNS = list(permutations(('b', 'w', 'r')))


def parse_input(text):
    """Parse a 3CSP input file. Returns (vertices, color, adj, s, t, k)."""
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    # Line 1: vertex labels with single-character color suffix, e.g. "1w 2w 3r"
    vertices = []
    color = {}
    for tok in lines[0].split():
        label, c = tok[:-1], tok[-1].lower()
        vertices.append(label)
        color[label] = c
    n = len(vertices)
    # Lines 2..n+1: adjacency matrix (symmetric, undirected)
    adj = {v: [] for v in vertices}
    for i in range(n):
        row = lines[1 + i].split()
        for j in range(n):
            if i != j and int(row[j]) == 1:
                adj[vertices[i]].append(vertices[j])
    # Line n+2: s and t
    s, t = lines[1 + n].split()[:2]
    # Line n+3: k
    k = int(lines[2 + n])
    return vertices, color, adj, s, t, k


def solve(color, adj, s, t, k):
    """Return (accepted, path). If accepted, path is the shortest valid path."""
    # Trivial case: s == t already satisfies "path of length 0".
    if s == t:
        return True, [s]

    best = None
    # Try every pattern whose first color matches color(s). Color sequences
    # along a valid path must follow one of these cycles, and the cycle is
    # pinned by the starting vertex's color, so at most 2 patterns matter.
    for pat in PATTERNS:
        if color[s] != pat[0]:
            continue
        # State = (vertex, position mod 3 in the pattern). BFS gives the
        # shortest valid path under this pattern.
        start = (s, 0)
        dist = {start: 0}
        parent = {start: None}
        q = deque([start])
        found = None
        while q:
            v, p = q.popleft()
            d = dist[(v, p)]
            if v == t:
                found = (v, p)
                break
            if d == k:
                continue
            np_ = (p + 1) % 3
            need = pat[np_]
            for u in adj[v]:
                if color[u] == need and (u, np_) not in dist:
                    dist[(u, np_)] = d + 1
                    parent[(u, np_)] = (v, p)
                    q.append((u, np_))
        if found is None:
            continue
        # Reconstruct path
        path = []
        cur = found
        while cur is not None:
            path.append(cur[0])
            cur = parent[cur]
        path.reverse()
        if best is None or len(path) < len(best):
            best = path

    if best is None:
        return False, None
    return True, best


def main():
    text = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    _vertices, color, adj, s, t, k = parse_input(text)
    accepted, path = solve(color, adj, s, t, k)
    if not accepted:
        print("Reject")
        return
    print("Accept")
    pretty = " -> ".join(f"{v}({color[v]})" for v in path)
    print(f"Path: {pretty}")
    print(f"Length: {len(path) - 1}  (k = {k})")


if __name__ == "__main__":
    main()
