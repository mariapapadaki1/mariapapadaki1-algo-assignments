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
    u = [0] + [min(row) for row in cost]
    v = [0.0] * (n + 1)
    r = [0] * (n + 1)
    pro = [0] * (n + 1)
    EPS = 1e-12

    def print_header_and_matrix():
        print("===AssignmentProblem===")
        print(f"{n}x{n} cost matrix:")
        for row in cost:
            print(" ".join(f"{x:.2f}" for x in row))

    def fmt_vec(vec):
        return "[ " + " ".join(f"{x:.2f}" for x in vec[1:]) + " ]"

    def print_initial_potentials():
        print("Initial potentials:")
        print("U:", fmt_vec(u))
        print("V:", fmt_vec(v))

    def print_phase_start(i0):
        print(f"--- Matching size {i0}, start from free row r={i0} ---")

    def print_sets(S, T):
        def fmt_set(st):
            if not st:
                return "{}"
            lst = sorted(st)
            return "{ " + ", ".join(str(x) for x in lst) + " }"
        print(f"Set S: {fmt_set(S)}")
        print(f"Set T: {fmt_set(T)}")

    def print_tight_edge(i0, j0, is_free, matched_row=None):
        if is_free:
            print(f"Tight edge discovered: ({i0}, {j0}). Column {j0} is free: AUGMENT MATCHING")
        else:
            print(f"Tight edge discovered: ({i0}, {j0}). Column {j0} is matched to row {matched_row}: EXTEND TREE")

    def print_update_potentials(delta):
        print(f"No tight edge outside T. Update potentials by delta={int(delta) if abs(delta-round(delta))<EPS else f'{delta:g}'}")
        print("U:", fmt_vec(u))
        print("V:", fmt_vec(v))

    def print_matching_pairs():
        pairs = []
        for i in range(1, n + 1):
            col = next((j for j in range(1, n + 1) if r[j] == i), None)
            if col is not None:
                pairs.append(f"R{i-1}->C{col-1}")
        print("Matching: " + ", ".join(pairs))

    def print_add_edge(ri, cj):
        print(f"Adding edge R{ri}->C{cj}")

    def print_remove_edge(ri, cj):
        print(f"Removing edge R{ri}->C{cj}")

    def augment_from_free_column(j_free):
        seq = []
        j = j_free
        while j != 0:
            seq.append(j)
            j = pro[j]
        free_row = r[0] - 1
        if len(seq) == 1:
            print(f"Augmenting path: R{free_row}->C{seq[0]-1}")
        else:
            start_col = seq[-1] - 1
            path_parts = [f"R{free_row}->C{start_col}"]
            for k in range(len(seq) - 1, 1, -1):
                row_k = r[seq[k-1]] - 1
                col_k = seq[k-2] - 1
                path_parts.append(f"R{row_k}->C{col_k}")
            row_last = r[seq[1]] - 1
            col_last = seq[0] - 1
            path_parts.append(f"R{row_last}->C{col_last}")
            print("Augmenting path: " + "=>".join(path_parts))

        print_matching_pairs()
        j = j_free
        while j != 0:
            j_prev = pro[j]
            i = r[j_prev]
            if j_prev != 0 and r[j_prev] != 0:
                print_remove_edge(i - 1, j_prev - 1)
            print_add_edge(i - 1, j - 1)
            r[j] = i
            j = j_prev

    print_header_and_matrix()
    print_initial_potentials()

    for i in range(1, n + 1):
        print_phase_start(i - 1)
        r[0] = i
        minv = [float("inf")] * (n + 1)
        used = [False] * (n + 1)
        j0 = 0
        S, T = set(), set()
        S.add(i - 1)
        print_sets(S, T)

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

            for j in range(0, n + 1):
                if used[j]:
                    u[r[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta

            if delta > EPS:
                print_update_potentials(delta)

            j0 = j1

            if r[j0] == 0:
                i_print = i0 - 1
                j_print = j0 - 1
                print_tight_edge(i_print, j_print, True)
                augment_from_free_column(j0)
                break
            else:
                matched_row = r[j0] - 1
                i_print = i0 - 1
                j_print = j0 - 1
                print_tight_edge(i_print, j_print, False, matched_row)
                S.add(matched_row)
                T.add(j_print)
                print_sets(S, T)

    assignment = []
    total = 0.0
    print("=== Final Result ===")
    for i in range(n):
        col = next(j for j in range(1, n + 1) if r[j] == i + 1) - 1
        val = cost[i][col]
        total += val
        print(f"row {i}-> col {col} cost={val:.1f}")
        assignment.append((i, col))
    print(f"Total cost: {total:.1f}")
    return assignment, total




   
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
