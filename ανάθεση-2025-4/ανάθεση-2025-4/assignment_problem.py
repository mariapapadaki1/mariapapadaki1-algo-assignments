import sys
# Διαβάζει πίνακα κόστους και ελέγχει ότι είναι τετράγωνος
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
    n = len(cost_table)
    if n == 0 or any(len(r) != n for r in cost_table):
        raise ValueError("Ο πίνακας κόστους πρέπει να είναι τετράγωνος και μη κενός.")
    return cost_table



# Βοηθητικές μορφοποιήσεις προς εκτύπωση

def num_no_float(x: float) -> str:
    """Επιστρέφει '2' αντί για '2.0' όταν γίνεται."""
    return str(int(x)) if float(x).is_integer() else str(x)

def format_vector(vec):
    """Μορφοποίηση διανύσματος για labels U,V."""
    return "[ " + " ".join(f"{v:.2f}" for v in vec) + " ]"


# Hungarian  - μόνο αποτέλεσμα (για απλή εκδοχή)

def hungarian(cost):
    n = len(cost)
    u = [0.0] * (n + 1)    # labels για γραμμές
    v = [0.0] * (n + 1)    # labels για στήλες
    p = [0]   * (n + 1)    # p[j]: ποια γραμμή είναι matched στη στήλη j
    way = [0] * (n + 1)    # way[j]: προκάτοχος στήλης για το augmenting path

    for i in range(1, n + 1):               # ταιριάζουμε τη γραμμή i
        p[0] = i
        minv = [float("inf")] * (n + 1)     # slacks για κάθε στήλη - πόσο απέχει από τη καλύτερη στηλη
        used = [False] * (n + 1)            # ποιες στήλες ανήκουν στο δέντρο
        j0 = 0                              # ξεκινάμε από τη στήλη 0

        while True:
            used[j0] = True
            i0 = p[j0]                      # γραμμή που «βλέπει» η j0
            delta = float("inf")
            j1 = 0

            # ενημέρωση slacks — βρίσκουμε την καλύτερη στήλη επόμενου βήματος
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]  # reduced cost
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]; j1 = j

            # δημιουργούμε νέα μηδενικά reduced costs
            for j in range(0, n + 1):
                if used[j]:
                    u[p[j]] += delta
                    v[j]     -= delta
                else:
                    minv[j]  -= delta

            j0 = j1
            if p[j0] == 0:                  # βρέθηκε ελεύθερη στήλη → augment
                break

        # αναστρέφουμε ακμές κατά μήκος του augmenting path
        while True:
            j1 = way[j0]
            p[j0] = p[j1]
            j0 = j1
            if j0 == 0:
                break

    # σύνθεση τελικού matching + κόστος
    assignment = [-1] * n
    total = 0.0
    for j in range(1, n + 1):
        i = p[j]
        assignment[i - 1] = j - 1
        total += cost[i - 1][j - 1]
    return assignment, total



# Hungarian (V) — εκτύπωση S/T, tight edges, augment κλπ.

def hungarian_v(cost):
    n = len(cost)
    u = [0.0] * (n + 1)
    v = [0.0] * (n + 1)
    r = [0]   * (n + 1)    # r[j]: ποια γραμμή είναι matched στη στήλη j (0=καμία)
    pro = [0] * (n + 1)    # pro[j]: προκάτοχος στήλης j στο augmenting path

    for i in range(1, n + 1):
        print(f"\n--- Matching size {i - 1}, start from free row r={i - 1} ---")
        r[0] = i
        minv = [float("inf")] * (n + 1)
        used = [False] * (n + 1)
        j0 = 0
        S, T = set(), set()
        S.add(i - 1)
        print(f"Set S: {S}")
        print(f"Set T: {T}")

        while True:
            used[j0] = True
            i0 = r[j0]                      # γραμμή που αντιστοιχεί στη j0
            delta = float("inf")
            j1 = 0

            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        pro[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]; j1 = j

            for j in range(0, n + 1):       # ενημέρωση labels & slacks
                if used[j]:
                    u[r[j]] += delta
                    v[j]     -= delta
                else:
                    minv[j]  -= delta

            j0 = j1
            if r[j0] == 0:
                print(f"Tight edge discovered: ({i0 - 1}, {j0 - 1}). Column {j0 - 1} is free: AUGMENT MATCHING")
                break
            else:
                matched_row = r[j0] - 1
                print(f"Tight edge discovered: ({i0 - 1}, {j0 - 1}). Column {j0 - 1} is matched to row {matched_row}: EXTEND TREE")
                S.add(matched_row); T.add(j0 - 1)
                print(f"Set S: {S}")
                print(f"Set T: {T}")

                # ενημερωτικό: αν δεν υπάρχει tight edge εκτός Τ, δείξε το delta
                if all(minv[j] > 0 for j in range(1, n + 1) if not used[j]):
                    dd = min(minv[j] for j in range(1, n + 1) if not used[j])
                    print(f"No tight edge outside T. Update potentials by delta={dd:.0f}")
                    print("U:", format_vector(u[1:]))
                    print("V:", format_vector(v[1:]))

        # AUGMENT: backtrack και flip των ακμών
        path = []
        j1 = j0
        while True:
            j_prev = pro[j1]
            r[j1] = r[j_prev]
            path.append(f"R{r[j1]-1}->C{j1-1}")
            j1 = j_prev
            if j1 == 0:
                break
        print("Augmenting path:", "=>".join(reversed(path)))

        print("Matching:", end=" ")
        for j in range(1, n + 1):
            if r[j] != 0:
                print(f"R{r[j]-1}->C{j-1}", end=", ")
        print()

    # τελική εκτύπωση
    assignment = [-1] * n
    total = 0.0
    for j in range(1, n + 1):
        i = r[j]
        assignment[i - 1] = j - 1
        total += cost[i - 1][j - 1]

    print("\n=== Final Result ===")
    for i, j in enumerate(assignment):
        print(f"row {i} -> col {j} cost={cost[i][j]:.1f}")
    print(f"Total cost: {total:.1f}")


# Απλή εκδοχή: χωρίς v
def print_assignment_simple(cost_table):
    # Πίνακας κόστους όπως στο PDF (ακέραιοι με κόμμα-κενό)
    for row in cost_table:
        print(", ".join(num_no_float(x) for x in row))
    print()

    # Τελικό matching + κόστος
    assignment, total_cost = hungarian(cost_table)
    for i, j in enumerate(assignment):
        print(f"row {i} -> col {j} cost={cost_table[i][j]:.1f}")
    print(f"Total cost: {total_cost:.1f}")


#main
def main():
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        filename = sys.argv[2] if len(sys.argv) > 2 else "costs_1.csv"
        cost_table = read_costs(filename)

        # Header + matrix με δεκαδικά + αρχικά labels 
        n = len(cost_table)
        print("=== Assignment Problem ===")
        print(f"{n}x{n} cost matrix:")
        for row in cost_table:
            print(" ".join(f"{x:.2f}" for x in row))
        U = [min(row) for row in cost_table]
        V = [0.0 for _ in range(n)]
        print("\nInitial potentials:")
        print("U:", format_vector(U))
        print("V:", format_vector(V))

        # Αναλυτική εκτέλεση
        hungarian_v(cost_table)

    else:
        filename = "costs_1.csv" if len(sys.argv) == 1 else sys.argv[1]
        cost_table = read_costs(filename)
        print_assignment_simple(cost_table)


if __name__ == "__main__":
    main()

