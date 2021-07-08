import argparse
import time

parser = argparse.ArgumentParser()
parser.add_argument("pop", type=int)
parser.add_argument("iters", type=int)
parser.add_argument("--seed", type=int, required=False)
parser.add_argument("--verbose", action="store_true")

benchmark = parser.add_mutually_exclusive_group(required = True)
benchmark.add_argument("--file", type=str)
benchmark.add_argument('--dacapo', type=str)
benchmark.add_argument('--fx', action="store_true")
benchmark.add_argument('--skija', action="store_true")

excluded = parser.add_mutually_exclusive_group()
excluded.add_argument('--gc', action='store_const', const=['c1','c2','runtime'])
excluded.add_argument('--c1', action='store_const', const=['gc','c2','runtime'])
excluded.add_argument('--c2', action='store_const', const=['gc','c1','runtime'])
excluded.add_argument('--compilers', action='store_const', const=['gc','runtime'])
excluded.add_argument('--runtime', action='store_const', const=['gc','c1','c2'])
excluded.add_argument('--no-runtime', action='store_const', const=['runtime'])

args = parser.parse_args()

import subprocess, time, math
import ga

def general_get_score(sbj, its = 2):
    if sbj == None:
        params = ["java", "-jar"] + args.file.split(' ')
    else:
        params = ["java"] + ga.get_active_genes(sbj) + ["-jar"] + args.file.split(' ')
        while "" in params:
            params.remove("")
    times = []
    if args.verbose:
        print("Evaluating subject")
    for i in range(its):
        t = time.time()
        s = subprocess.run(params, capture_output=True)
        
        if b"Could not create the Java Virtual Machine" in s.stderr:
            print('  '.join(params))
            print(str(s.stderr,encoding="latin1"))
            raise RuntimeError("Invalid parameter values")
        else:
            times.append(time.time() - t)
    return sum(times)//its

def dacapo_get_score(sbj, its = 2):
    if sbj == None:
        params = ["java", "-jar", "dacapo-9.12-MR1-bach.jar", args.dacapo, "-C"]
    else:
        params = ["java"] + ga.get_active_genes(sbj) + ["-jar", "dacapo-9.12-MR1-bach.jar", args.dacapo, "-C"]
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
                times.append(ga.MAX_FITNESS)
        else:
            times.append(ga.MAX_FITNESS)
    return sum(times)//its
    
def fx_get_score(sbj, its = 2):
    if sbj == None:
        params = ["python", "java-graphics-benchmark-master/script/fx.py"]
    else:
        params = ["python", "java-graphics-benchmark-master/script/fx.py"] + ga.get_active_genes(sbj)
        while "" in params:
            params.remove("")
    times = []
    if args.verbose:
        print("Evaluating subject")
    for i in range(its):
        try:
            s = subprocess.run(params, capture_output=True, timeout=120)
            line = s.stdout.rfind(b"CirclesDemo")
            if line == -1:
                print(str(s.stdout, "ascii"))
                times.append(ga.MIN_FITNESS)
            else:
                times.append(int(s.stdout[line:].split(b" ")[4]))
        except:
            times.append(ga.MIN_FITNESS)
    return sum(times)//its
    
def skija_get_score(sbj, its = 2):
    if sbj == None:
        params = ["python", "java-graphics-benchmark-master/script/skija.py"]
    else:
        params = ["python", "java-graphics-benchmark-master/script/skija.py"] + ga.get_active_genes(sbj)
        while "" in params:
            params.remove("")
    times = []
    if args.verbose:
        print("Evaluating subject")
    for i in range(its):
        s = subprocess.run(params, capture_output=True)
        if line == -1:
            print(str(s.stdout, "ascii"))
        else:
            times.append(int(s.stdout[line:].split(b" ")[4]))
    return sum(times)//its
    
#######

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
    elif args.compilers:
        ga.exclude(args.compilers)
        
    if args.dacapo:
        get_score = dacapo_get_score
        def_val = ga.MAX_FITNESS
        sorter = lambda x: x[1]
        maximize = False
    elif args.fx:
        get_score = fx_get_score
        def_val = ga.MIN_FITNESS
        sorter = lambda x: -x[1]
        maximize = True
    elif args.skija:
        get_score = dacapo_get_score
        def_val = ga.MIN_FITNESS
        sorter = lambda x: -x[1]
        maximize = True
    elif args.file:
        get_score = dacapo_get_score
        def_val = ga.MAX_FITNESS
        sorter = lambda x: x[1]
        maximize = False
    
    if args.seed:
        print("Using", args.seed, "as seed")
        ga.set_seed(args.seed)
    if args.verbose:
        print("Starting reference evaluation")
    
    
    # Warmup
    get_score(None, 3)
    print("Default flags score: {}".format(get_score(None)))
    
    if args.verbose:
        print("Starting genetic algorithm optimization")
    
    population = ga.new_generation(args.pop, def_val)
    
    for it in range(args.iters):
        for i in range(args.pop):
            population[i][1] = get_score(population[i][0]) #subject.time = eval(subject.genes)
        
        population.sort(key=sorter) #sort by subject.time
        print("Generation", it+1)
        print("{}\n  Score: {}".format(' '.join(ga.get_active_genes(population[0][0])), population[0][1]))
        
        population = ga.next_generation(population, args.pop, def_val, maximize)

if __name__ == '__main__':
    main()
