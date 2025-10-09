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

def format_vector(vec):
    return "[ " + " ".join(f"{v:.2f}" for v in vec) + " ]"

def print_labels(cost_table):
    n = len(cost_table)
    m = len(cost_table[0]) if n > 0 else 0
    print("=== Assignment Problem ===")
    print(f"{n}x{m} cost matrix:")
    for row in cost_table:
        print(" ".join(f"{x:.2f}" for x in row))
    # Initial potentials
    U = [min(row) for row in cost_table]
    V = [0.0 for _ in range(m)]
    print("\nInitial potentials:")
    print("U:", format_vector(U))
    print("V:", format_vector(V))

def print_costs(cost_table):
    total_cost = 0
    for i in range(len(cost_table)):
        for j in range(len(cost_table[i])):
            cost = cost_table[i][j]
            print(f"row {i} -> col {j}  cost={cost:.1f}")
            total_cost += cost
    print(f"Total cost: {total_cost:.1f}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "-v":
        filename = sys.argv[2] if len(sys.argv) > 2 else "costs_1.csv"
        cost_table = read_costs(filename)
        print_labels(cost_table)
    else:
        filename = "costs_1.csv" if len(sys.argv) == 1 else sys.argv[1]
        cost_table = read_costs(filename)
        print_costs(cost_table)

if __name__ == "__main__":
    main()
