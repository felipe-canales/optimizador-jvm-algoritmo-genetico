import argparse

parser = argparse.ArgumentParser()
parser.add_argument("file", type=str)
parser.add_argument("pop", type=int)
parser.add_argument("iters", type=int)
parser.add_argument("--seed", type=int, required=False)
parser.add_argument("--verbose", action="store_true")
excluded = parser.add_mutually_exclusive_group()
excluded.add_argument('--gc', action='store_const', const=['c1','c2','runtime'])
excluded.add_argument('--c1', action='store_const', const=['gc','c2','runtime'])
excluded.add_argument('--c2', action='store_const', const=['gc','c1','runtime'])
excluded.add_argument('--runtime', action='store_const', const=['gc','c1','c2'])
excluded.add_argument('--no-runtime', action='store_const', const=['runtime'])

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
    if args.verbose:
        print("Evaluating subject")
    for i  in range(its):
        s = subprocess.run(params, capture_output=True)
        
        if b"Could not create the Java Virtual Machine" in s.stderr:
            print('  '.join(params))
            print(str(s.stderr,encoding="latin1"))
            raise RuntimeError("Invalid parameter values")
        elif b"PASSED" in s.stderr:
            try:
                times.append(int(s.stderr.split(b' ')[-3]))
            except:
                print(s.stderr.split(b'\n')[-1])
                times.append(999999)
        else:
            times.append(999999)
    return sum(times)//its



def main():
    if args.gc:
        ga.exclude(args.gc)
    elif args.c1:
        ga.exclude(args.c1)
    elif args.c2:
        ga.exclude(args.c2)
    elif args.runtime:
        ga.exclude(args.runtime)
    elif args.no_runtime:
        ga.exclude(args.no_runtime)
    
    if args.seed:
        print("Using", args.seed, "as seed")
        ga.set_seed(args.seed)

    if args.verbose:
        print("Starting reference evaluation")
    # Warmup
    evaluate(None, 3)
    print("Default flags time: {}".format(evaluate(None)))
    
    if args.verbose:
        print("Starting genetic algorithm optimization")
    
    population = ga.new_generation(args.pop)
    
    for it in range(args.iters):
        for i in range(args.pop):
            population[i][1] = evaluate(population[i][0]) #subject.time = eval(subject.genes)
        
        population.sort(key=lambda x: x[1]) #sort by subject.time
        print("Generation", it+1)
        print("{}\n  Time: {}".format(' '.join(ga.get_active_genes(population[0][0])), population[0][1]))
        #print("  Population:")
        #for i in range(len(population)):
        #    print("\t{}\t{}".format(population[i][1], ga.get_active_genes(population[i][0])))

        population = ga.next_generation(population, args.pop)

if __name__ == '__main__':
    main()
