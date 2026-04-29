"""
Problem 2: Reduce DGSP <H, u, v, l>  to  3CSP <G, s, t, k>.

Construction (gadget-based, polynomial time):
  - Add a fresh source S colored W; this locks the color cycle to w-b-r.
  - Each H-vertex x becomes V_x in G, colored B.
  - Each directed H-edge (x -> y) becomes a 3-edge tunnel
        V_x  --  R_xy (red)  --  W_xy (white)  --  V_y
    so that under the locked cycle, only forward traversal is possible.
  - s = S, t = V_v, k = 3l + 1.

Run:
    python3 reduce.py <input.txt> > problem1_input.txt
"""

import sys


def parse_dgsp(text):
    """Parse DGSP input. Returns (vertices, edges, u, v, l)."""
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    # Line 1: bare vertex labels (no colors)
    vertices = lines[0].split()
    n = len(vertices)
    # Lines 2..n+1: directed adjacency matrix; row i col j = 1 means i -> j
    edges = []
    for i in range(n):
        row = lines[1 + i].split()
        for j in range(n):
            if i != j and int(row[j]) == 1:
                edges.append((vertices[i], vertices[j]))
    u, v = lines[1 + n].split()[:2]
    l = int(lines[2 + n])
    return vertices, edges, u, v, l


def reduce_dgsp_to_3csp(vertices, edges, u, v, l):
    """Build the 3CSP instance. Returns (g_vertices, g_edges, s, t, k)
    where g_vertices is a list of (name, color) and g_edges is a list of
    undirected pairs (a, b)."""
    g_vertices = []  # ordered: source first, then H-vertex copies, then tunnel intermediates
    g_edges = []

    # Fresh source S (white), connected only to V_u. Forces pattern w-b-r.
    source = "__S"
    g_vertices.append((source, 'w'))

    # H-vertex copies, all black.
    def vname(x): return f"__V_{x}"
    for x in vertices:
        g_vertices.append((vname(x), 'b'))

    g_edges.append((source, vname(u)))

    # Edge tunnels: V_x -- R_xy -- W_xy -- V_y for each directed (x, y).
    for (x, y) in edges:
        r_node = f"__R_{x}_{y}"
        w_node = f"__W_{x}_{y}"
        g_vertices.append((r_node, 'r'))
        g_vertices.append((w_node, 'w'))
        g_edges.append((vname(x), r_node))
        g_edges.append((r_node, w_node))
        g_edges.append((w_node, vname(y)))

    s = source
    t = vname(v)
    k = 3 * l + 1
    return g_vertices, g_edges, s, t, k


def format_3csp(g_vertices, g_edges, s, t, k):
    """Render the 3CSP instance in the file format from Problem 1.
    Internal symbolic names are replaced with integer labels 1..n."""
    n = len(g_vertices)
    name_to_idx = {name: i + 1 for i, (name, _) in enumerate(g_vertices)}

    lines = []
    # Line 1: "<idx><color>" tokens, e.g. "1w 2b 3b ..."
    lines.append(" ".join(f"{name_to_idx[name]}{c}" for name, c in g_vertices))
    # Adjacency matrix (undirected, so symmetric)
    matrix = [[0] * n for _ in range(n)]
    for a, b in g_edges:
        i, j = name_to_idx[a] - 1, name_to_idx[b] - 1
        matrix[i][j] = 1
        matrix[j][i] = 1
    for row in matrix:
        lines.append(" ".join(str(x) for x in row))
    lines.append(f"{name_to_idx[s]} {name_to_idx[t]}")
    lines.append(str(k))
    return "\n".join(lines) + "\n"


def main():
    text = open(sys.argv[1]).read() if len(sys.argv) > 1 else sys.stdin.read()
    vertices, edges, u, v, l = parse_dgsp(text)
    g_vertices, g_edges, s, t, k = reduce_dgsp_to_3csp(vertices, edges, u, v, l)
    sys.stdout.write(format_3csp(g_vertices, g_edges, s, t, k))


if __name__ == "__main__":
    main()
