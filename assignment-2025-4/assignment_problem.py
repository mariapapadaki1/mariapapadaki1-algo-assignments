import sys

def read_costs(filename):
    cost_table = []
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",") if "," in line else line.split()
            row = [float(x) for x in parts]
            cost_table.append(row)
    return cost_table

def num_no_float(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else str(x)

def format_vector(vec):
    return "[ " + " ".join(f"{v:.2f}" for v in vec) + " ]"

def hungarian(cost):
    n = len(cost)
    u = [0] + [min(row) for row in cost]
    v = [0.0] * (n + 1)
    p = [0] * (n + 1)
    way = [0] * (n + 1)
    for i in range(1, n + 1):
        p[0] = i
        minv = [float("inf")] * (n + 1)
        used = [False] * (n + 1)
        j0 = 0
        while True:
            used[j0] = True
            i0 = p[j0]
            delta = float("inf")
            j1 = 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j
            for j in range(0, n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if p[j0] == 0:
                break
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break
    assignment = [-1] * n
    total = 0.0
    for j in range(1, n + 1):
        i = p[j]
        assignment[i - 1] = j - 1
        total += cost[i - 1][j - 1]
    return assignment, total

def hungarian_v(cost):
    n = len(cost)
    print("=== Assignment Problem ===")
    print(f"{n}x{n} cost matrix:")
    for row in cost:
        print(" ".join(f"{x:.2f}" for x in row))
    U = [min(row) for row in cost]
    V = [0.0 for _ in range(n)]
    print("\nInitial potentials:")
    print("U:", format_vector(U))
    print("V:", format_vector(V))

    u = [0] + U[:]
    v = [0.0] * (n + 1)
    r = [0] * (n + 1)
    pro = [0] * (n + 1)
    EPS = 1e-12

    def print_rows(rmap):
        pairs = []
        for j in range(1, n + 1):
            if rmap[j] != 0:
                pairs.append(f"R{rmap[j]-1}->C{j-1}")
        print("Matching: " + (", ".join(pairs) if pairs else ""))

    for i in range(1, n + 1):
        print(f"--- Matching size {i - 1}, start from free row r={i - 1} --")
        r[0] = i
        minv = [float("inf")] * (n + 1)
        used = [False] * (n + 1)
        j0 = 0
        S, T = {i - 1}, set()
        print(f"Set S: {{ {', '.join(str(x) for x in sorted(S))} }}")
        print(f"Set T: {{ {', '.join(str(x) for x in sorted(T))} }}")
        while True:
            used[j0] = True
            i0 = r[j0]
            delta = float("inf")
            j1 = 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j] - EPS:
                        minv[j] = cur
                        pro[j] = j0
                    if (minv[j] < delta - EPS) or (abs(minv[j] - delta) <= EPS and r[j] == 0):
                        delta = minv[j]
                        j1 = j
            if delta > EPS:
                dtxt = f"{int(delta)}" if abs(delta - round(delta)) <= EPS else f"{delta:g}"
                print(f"No tight edge outside T. Update potentials by delta={dtxt}")
                for j in range(0, n + 1):
                    if used[j]:
                        u[r[j]] += delta
                        v[j] -= delta
                    else:
                        minv[j] -= delta
                def _fmt(vec):
                    return "[ " + " ".join(f"{x:.2f}" for x in vec[1:]) + " ]"
                print("U:", _fmt(u))
                print("V:", _fmt(v))
            i0 = r[j0]
            if r[j1] == 0:
                print(f"Tight edge discovered: ({i0 - 1}, {j1 - 1}). Column {j1 - 1} is free: AUGMENT MATCHING")
                j0 = j1
                break
            else:
                matched_row = r[j1] - 1
                print(f"Tight edge discovered: ({i0 - 1}, {j1 - 1}). Column {j1 - 1} is matched to row {matched_row}: EXTEND TREE")
                S.add(matched_row)
                T.add(j1 - 1)
                print(f"Set S: {{ {', '.join(str(x) for x in sorted(S))} }}")
                print(f"Set T: {{ {', '.join(str(x) for x in sorted(T))} }}")
                used[j1] = True
                j0 = j1

        old_r = r.copy()
        path = []
        j1 = j0
        while True:
            j_prev = pro[j1]
            row = old_r[j_prev] - 1
            col = j1 - 1
            path.append((row, col))
            j1 = j_prev
            if j1 == 0:
                break

        if len(path) == 1:
            print(f"Augmenting path: R{path[0][0]}->C{path[0][1]}")
        else:
            seq = []
            for k, (rr, cc) in enumerate(reversed(path)):
                if k == 0:
                    seq.append(f"R{rr}->C{cc}")
                else:
                    seq.append(f"=>R{rr}->C{cc}")
            print("Augmenting path: " + "".join(seq))

        print_rows(old_r)

        if len(path) == 1:
            rr, cc = path[0]
            print(f"Adding edge R{rr}->C{cc}")
        else:
            rev = list(reversed(path))
            for idx, (rr, cc) in enumerate(rev):
                prev_col = None
                for jj in range(1, n + 1):
                    if old_r[jj] == rr + 1:
                        prev_col = jj - 1
                        break
                if prev_col is not None and prev_col != cc:
                    print(f"Removing edge R{rr}->C{prev_col}")
                print(f"Adding edge R{rr}->C{cc}")

        j1 = j0
        while True:
            j_prev = pro[j1]
            r[j1] = r[j_prev]
            j1 = j_prev
            if j1 == 0:
                break

        print_rows(r)

    assignment = [-1] * n
    total = 0.0
    print("=== Final Result ===")
    for j in range(1, n + 1):
        irow = r[j]
        assignment[irow - 1] = j - 1
        total += cost[irow - 1][j - 1]
    for irow, jcol in enumerate(assignment):
        print(f"row {irow} -> col {jcol} cost={cost[irow][jcol]:.1f}")
    print(f"Total cost: {total:.1f}")

def print_assignment_simple(cost_table):
    assignment, total_cost = hungarian(cost_table)
    for i, j in enumerate(assignment):
        print(f"row {i} -> col {j} cost={cost_table[i][j]:.1f}")
    print(f"Total cost: {total_cost:.1f}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        filename = sys.argv[2] if len(sys.argv) > 2 else "costs_1.csv"
        cost_table = read_costs(filename)
        hungarian_v(cost_table)
    else:
        filename = "costs_1.csv" if len(sys.argv) == 1 else sys.argv[1]
        cost_table = read_costs(filename)
        print_assignment_simple(cost_table)

if __name__ == "__main__":
    main()
