import sys
import matplotlib.pyplot as plt

if len(sys.argv) < 2:
    print("Use: python graph_ga_res.py results_file [title]")
    quit(1)

gens = [i for i in range(1,11)]
times = []
default = None
with open(sys.argv[1], "r") as res:
    for line in res.readlines():
        if "Default flags" in line:
            default = int(line.split(' ')[-1])
        elif "Time:" in line:
            times.append(int(line.split(' ')[-1]))

plt.figure(figsize=(9,6))
plt.plot(gens, [default]*10, color="red", label="Default flags")
plt.plot(gens, times, color="blue", label="Customized flags")
plt.ylim(0, int(max(default, *times) * 1.1))
plt.xlim(1, 10)
plt.legend()
plt.ylabel("Time [ms]")
plt.xlabel("Generation")
if len(sys.argv) == 3:
    plt.title(sys.argv[2])

plt.show()