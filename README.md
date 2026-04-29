# IT 328 Project 2

Python 3, no external dependencies.

```
problem1/threecsp.py    # 3-Color Shortest Path solver
problem2/reduce.py      # DGSP -> 3CSP reduction
tests/                  # sample inputs (incl. spec example)
report.md               # written report (proofs, walkthroughs, AI disclosure)
```

## Quick start

```
python3 problem1/threecsp.py tests/p1_spec_example.txt
python3 problem2/reduce.py tests/p2_example.txt | python3 problem1/threecsp.py
```

See `report.md` for details.
