# IT 328 Programming Project 2 — Report

**Team:** _[fill in member names]_

**Contributions:** _[fill in per-member contributions, e.g. "X: Problem 1 algorithm and code; Y: Problem 2 reduction and report; Z: testing and writeup"]._

**AI use disclosure.** ChatGPT/Claude was used to draft skeletons of the BFS state-space and the gadget construction in `problem2/reduce.py`, plus a first pass of this report. Every function was hand-reviewed and edited; the algorithm design (state product, gadget structure, length accounting) is ours.

---

## Problem 1 — 3-Color Shortest Path (3CSP)

### Proof that 3CSP is in P

Read "alternates all three colors" as the rule used in the spec's examples: **for any three consecutive vertices on the path, all three colors {b, w, r} appear**. Equivalently, `c_i ≠ c_{i+1}` and `c_i ≠ c_{i+2}` for every position `i`. So once the colors of the first two vertices on the path are chosen, every subsequent color is forced — the path's color sequence must be a contiguous substring of one of the six cyclic patterns (the 3! permutations of (b,w,r) cycled).

Build an auxiliary graph `G' = (V', E')` ("the product graph") for a fixed pattern `P = (P[0], P[1], P[2])`:

- `V' = { (v, p) : v ∈ V(G), p ∈ {0,1,2}, color(v) = P[p] }` — at most `|V|` states (each vertex appears at one position only).
- `((u, p), (v, (p+1) mod 3)) ∈ E'` whenever `(u, v) ∈ E(G)` — at most `|E|` edges.

A length-`m` path from `(s, 0)` to `(t, m mod 3)` in `G'` corresponds **bijectively** to a length-`m` path from `s` to `t` in `G` whose color sequence follows pattern `P`. Running BFS on `G'` finds the shortest such path in `O(|V| + |E|)`. We try each of the 6 patterns (only those with `P[0] = color(s)` are non-trivial — at most 2 patterns), so the total runtime is `O(|V| + |E|)`. That is polynomial in the input size, so 3CSP ∈ P. ∎

### Algorithm summary

The solver lives in [`problem1/threecsp.py`](problem1/threecsp.py).

1. **Parse** ([`parse_input`](problem1/threecsp.py)). Read line 1 to get vertex labels and colors, the next `n` lines as the adjacency matrix, then `s t` and `k`.
2. **For each pattern** in `PATTERNS` (the six permutations of `(b, w, r)`), skip if `pattern[0] != color(s)`; otherwise BFS on the product state space ([`solve`](problem1/threecsp.py)).
3. **BFS state** is `(vertex, position mod 3)`. We expand `(v, p)` to `(u, (p+1) mod 3)` for each neighbor `u` whose color equals `pattern[(p+1) mod 3]`. We track `parent[]` to reconstruct the path.
4. **Cutoff at `k`.** We stop expanding any state whose distance equals `k`.
5. **Result.** Across patterns we keep the shortest accepting path (or report Reject).

### Worked example (the spec input, `tests/p1_spec_example.txt`)

```
Vertices: 1w 2w 3r 4b 5b
Edges (undirected): 1-2, 1-5, 2-3, 3-4, 4-5
s=2, t=4, k=2
```

`color(2) = w`, so we try the patterns starting with `w`: `(w,b,r)` and `(w,r,b)`.

- Pattern `(w,r,b)`: BFS from `(2, 0)`. From `2`, neighbors are `1 (w)` and `3 (r)`; we need position 1 = `r`, so only `3` qualifies → state `(3, 1)` at distance 1. From `3`, neighbors are `2 (w)` and `4 (b)`; we need position 2 = `b`, so only `4` qualifies → `(4, 2)` at distance 2. We reached `t = 4` within `k = 2`.
- Reconstruct via parents: `4 ← 3 ← 2`. Path `2(w) → 3(r) → 4(b)`. Output:

```
Accept
Path: 2(w) -> 3(r) -> 4(b)
Length: 2  (k = 2)
```

### Reject example (`tests/p1_reject.txt`)

A 6-vertex path graph `1(b)-2(w)-3(b)-4(w)-5(r)-6(b)`, asking `s=1, t=6, k=5`. The only `s→t` walk in this tree is the colors `b w b w r b` — which fails the rule (positions 0 and 2 are both `b`). Every pattern starting with `b` dies at the third hop. Output: `Reject`.

---

## Problem 2 — DGSP ≤ₚ 3CSP

### Reduction proof

Given DGSP input `<H, u, v, l>`, construct 3CSP input `<G, s, t, k>` as follows:

- **Source guard.** Add a fresh vertex `S` colored white. Set `s = S`. `S` has exactly one neighbor: `V_u` (defined below).
- **Vertex copies.** For each `x ∈ V(H)`, add `V_x` colored black.
- **Edge tunnels.** For each directed edge `(x → y) ∈ E(H)`, add two new vertices `R_xy` (red) and `W_xy` (white) and the three undirected edges `V_x — R_xy — W_xy — V_y`.
- `t = V_v` and `k = 3l + 1`.

The construction adds `1 + |V(H)| + 2|E(H)|` vertices and `1 + 3|E(H)|` edges, computed in linear time — so the reduction is polynomial-time.

**Forward direction (`⇒`).** If `H` has a directed walk `u = x_0, x_1, …, x_m = v` of length `m ≤ l`, then in `G` follow

```
S → V_{x_0} → R_{x_0 x_1} → W_{x_0 x_1} → V_{x_1} → R_{x_1 x_2} → W_{x_1 x_2} → V_{x_2} → … → V_{x_m}
```

Colors: `w b r w b r w b r … b`. This is the cyclic pattern `wbr` repeating, so it satisfies "alternates all three colors". Length is `1 + 3m ≤ 1 + 3l = k`. So `(G, s, t, k)` is accepted.

**Backward direction (`⇐`).** Suppose `G` has an alternating path of length `≤ k` from `S` to `V_v`. The path starts at `S` (white), so its color cycle is one of `wbr` or `wrb`. The only neighbor of `S` is `V_u` (black), forcing the second color to be `b` — so the cycle is locked to `wbr` and position 1 must be black, position 2 red, position 0 (mod 3) white.

The locked cycle eliminates every "wrong direction" move. For any `V_x` (black, at position 1 mod 3), the next color must be red. The neighbors of `V_x` in `G` are exactly:

- `R_{x,y}` for each *outgoing* H-edge `(x → y)` — color **red** ✅
- `W_{z,x}` for each *incoming* H-edge `(z → x)` — color **white** ❌
- (and possibly `S`, white, also wrong)

So we can only enter outgoing-edge tunnels. Once inside a tunnel, the intermediate vertices `R_xy` and `W_xy` each have degree exactly 2, so the path must traverse the entire tunnel `V_x → R_xy → W_xy → V_y`. Three steps later we are at `V_y`, again black at position ≡ 1 (mod 3). The G-walk therefore decomposes into the initial step `S → V_u` followed by complete tunnels, each corresponding to one directed H-edge. If the total G-length is `1 + 3m`, the corresponding H-walk has length `m`, and `1 + 3m ≤ k = 3l + 1` gives `m ≤ l`. So `H` has a directed walk from `u` to `v` of length `≤ l`. ∎

### Implementation summary

The reducer lives in [`problem2/reduce.py`](problem2/reduce.py).

1. **Parse** ([`parse_dgsp`](problem2/reduce.py)). Same format as Problem 1 minus colors; the adjacency matrix is read as directed.
2. **Build G** ([`reduce_dgsp_to_3csp`](problem2/reduce.py)). Allocate `S`, the `V_x` copies, then walk every directed H-edge and emit the three-edge tunnel with two fresh intermediates per edge.
3. **Render** ([`format_3csp`](problem2/reduce.py)). Reindex symbolic vertex names to integers `1..n` so the output matches Problem 1's input grammar (token format `"<idx><color>"`). Emit the symmetric adjacency matrix, then `s t` and `k = 3l + 1`.

### Worked example (`tests/p2_example.txt`)

Input H is the directed path `1 → 2 → 3 → 4`, with `u = 1, v = 4, l = 3`.

The reducer outputs an 11-vertex 3CSP instance with `k = 10`:

```
1w  2b 3b 4b 5b   6r 7w   8r 9w   10r 11w
S   V1 V2 V3 V4  R12 W12  R23 W23 R34 W34
```

(plus the edge `S–V1` and the three tunnels). Piping this into the Problem 1 solver:

```
$ python3 problem2/reduce.py tests/p2_example.txt | python3 problem1/threecsp.py
Accept
Path: 1(w) -> 2(b) -> 6(r) -> 7(w) -> 3(b) -> 8(r) -> 9(w) -> 4(b) -> 10(r) -> 11(w) -> 5(b)
Length: 10  (k = 10)
```

The path is `S → V1 → R12 → W12 → V2 → R23 → W23 → V3 → R34 → W34 → V4`, exactly the directed H-walk `1 → 2 → 3 → 4` (length 3) lifted through the gadgets.

### Reject example (`tests/p2_reject.txt`)

Same H, but querying `u = 4, v = 1, l = 3`. There is no directed walk from `4` back to `1`, so the reducer's output is rejected by the 3CSP solver — confirming the reduction respects directionality.

### Edge case (`u = v, l = 0`)

The reducer emits `k = 3·0 + 1 = 1`. The single edge `S → V_u = V_v` has length 1 with colors `w, b`; with only two vertices on the path, the "any three consecutive" rule is vacuous, so 3CSP accepts. This matches DGSP accepting the trivial length-0 walk.

---

## How to run

```
# Problem 1 solver
python3 problem1/threecsp.py tests/p1_spec_example.txt
python3 problem1/threecsp.py tests/p1_reject.txt
python3 problem1/threecsp.py tests/p1_longer.txt

# Problem 2 reducer (output is valid Problem-1 input)
python3 problem2/reduce.py tests/p2_example.txt

# End-to-end: reduce DGSP, then solve as 3CSP
python3 problem2/reduce.py tests/p2_example.txt | python3 problem1/threecsp.py
python3 problem2/reduce.py tests/p2_reject.txt  | python3 problem1/threecsp.py
```
