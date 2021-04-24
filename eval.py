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
    bm_params = "-ikv -wt 40 -it 20"
    if sbj == None:
        params = ["C:/Program Files/Java/jre7/bin/java.exe", "-jar"] + args.file.split(' ') + bm_params.split(' ')
    else:
        params = ["C:/Program Files/Java/jre7/bin/java.exe"] + ga.get_active_genes(sbj) + ["-jar"] + args.file.split(' ') + bm_params.split(' ')
        while "" in params:
            params.remove("")
    times = []
    for _  in range(its):
        s = subprocess.run(params, capture_output=True)
        
        if b"Could not create the Java Virtual Machine" in s.stderr:
            print('  '.join(params))
            print(str(s.stderr, encoding="latin1"))
            raise RuntimeError("Invalid parameter values")
        elif b"Valid run!" in s.stdout:
            times.append(float(s.stdout.split(b' ')[-2].replace(b',',b'.')))
        else:
            print(s.stdout)
            print(s.stderr)
            times.append(0)
    return sum(times)/its



def main():
    if args.seed:
        ga.set_seed(args.seed)

    # Warmup
    #evaluate(None, 3)
    print("Default flags time: {}".format(evaluate(None)))

    population = ga.new_generation(args.pop)
    
    for it in range(args.iters):
        for i in range(args.pop):
            population[i][1] = evaluate(population[i][0]) #subject.time = eval(subject.genes)
        
        population.sort(key=lambda x: -x[1]) #sort by subject.time
        print("Generation", it+1)
        print("{}\n  Time: {}".format(' '.join(ga.get_active_genes(population[0][0])), population[0][1]))

        population = ga.next_generation(population, args.pop)

if __name__ == '__main__':
    main()
