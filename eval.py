import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str)
parser.add_argument("pop", type=int)
parser.add_argument("iters", type=int)
parser.add_argument("--seed", type=int, required=False)
parser.add_argument("--verbose")

args = parser.parse_args()


import subprocess, time, math
import ga


def evaluate(sbj, its = 2):
    if sbj == None:
        params = ["java", "-jar"] + args.file.split(' ') + ["-C"]
    else:
        params = ["java"] + ga.get_active_genes(sbj) + ["-jar"] + args.file.split(' ') + ["-C"]
        while "" in params:
            params.remove("")
    times = []
    for _  in range(its):
        s = subprocess.run(params, capture_output=True)
        
        if b"Could not create the Java Virtual Machine" in s.stderr:
            print('  '.join(params))
            print(str(s.stderr,encoding="latin1"))
            raise RuntimeError("Invalid parameter values")
        elif b"PASSED" in s.stderr:
            times.append(int(s.stderr.split(b' ')[-3]))
        else:
            times.append(999999)
    return sum(times)//its



def main():
    if args.seed:
        ga.set_seed(args.seed)

    # Warmup
    evaluate(None, 3)
    print("Default flags time: {}".format(evaluate(None)))

    population = ga.new_generation(args.pop)
    
    for it in range(args.iters):
        for i in range(args.pop):
            population[i][1] = evaluate(population[i][0]) #subject.time = eval(subject.genes)
        
        population.sort(key=lambda x: x[1]) #sort by subject.time
        print("Generation", it+1)
        print("{}\n  Time: {}".format(' '.join(ga.get_active_genes(population[0][0])), population[0][1]))

        population = ga.next_generation(population, args.pop)

if __name__ == '__main__':
    main()
