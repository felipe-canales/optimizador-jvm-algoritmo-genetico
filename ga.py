import json, random


MAX_FITNESS = 999999
MUTATION_CHANCE = 0.1
DEFAULT_CHANCE = 0.3


with open("genes.json") as gene_file:
    gene_template = json.load(gene_file)
    
excluded_categories = [] #Accept gc, c1, c2, runtime

used_genes = list(gene_template["genes"])

def exclude(cats):
    used_genes.clear()
    excluded_categories.extend(cats)
    print("Excluding", ",".join(cats))
    for gene in gene_template["genes"]:
        if not gene["category"] in excluded_categories:
            used_genes.append(gene)


def value_range(g):
    spacing, step = g["step"]
    values = [g["min"]]
    if spacing == "linear":
        while values[-1] < g["max"]:
            values.append(values[-1] + step)
        return values

    while values[-1] < g["max"]:
        values.append(values[-1] * step)
    return values


def choose_value_or_null(val, chance):
    if random.random() < chance:
        return None
    return val


gene_init = {
    "control": lambda g: random.randint(0, len(g["variants"]) - 1),
    "int": lambda g: choose_value_or_null(random.choice(value_range(g)), DEFAULT_CHANCE),
    "double": lambda g: choose_value_or_null(random.choice(value_range(g)), DEFAULT_CHANCE),
    "bool": lambda g: random.random() >= 0.5
}


def set_seed(s):
    random.seed(s)


def new_subject():
    sequence = []
    for gene in used_genes:
        sequence.append(gene_init[gene["type"]](gene))
    return sequence


def crossover(sbj1, sbj2):
    new_sbj = []
    for i in range(len(sbj1)):
        if random.random() >= 0.5:
            new_sbj.append(sbj2[i])
        else:
            new_sbj.append(sbj1[i])
    # mutation
    if random.random() < MUTATION_CHANCE:
        mutation = random.randint(0, len(new_sbj)-1)
        alt_genes = new_subject()
        new_sbj[mutation] = alt_genes[mutation]
    return new_sbj


def new_generation(target):
    return [[new_subject(), MAX_FITNESS] for i in range(target)] #genes, time


def tournament_select(pop, k):
    candidates = random.choices(pop, k=k)
    best = candidates[0]
    for i in range(1,k):
        c = candidates[i]
        if c[1] <= best[1]:
            best = c
    return pop.index(best)


def next_generation(subjects, target):
    new_gen = []
    # selecting survivors
    for i in range(target//2):
        new_gen.append(subjects.pop(tournament_select(subjects, 5)))
    # reproducing survivors
    for i in range(0, (target//2) - 1, 2):
        j = i+1
        new_gen.append([crossover(subjects[i][0], subjects[j][0]), MAX_FITNESS])
        new_gen.append([crossover(subjects[i][0], subjects[j][0]), MAX_FITNESS])
    # remaining few
    while len(new_gen) < target:
        print("remaining?")
        i,j = random.choices(range(target//2), k=2)
        new_gen.append([crossover(subjects[i][0], subjects[j][0]), MAX_FITNESS])
    return new_gen


def is_deactivated(gene_groups, deactivated_list):
    for deac in deactivated_list:
        if deac in gene_groups:
            return True
    return False


def get_active_genes(subject):
    active = []
    deactivated = []
    # get deactivated genes
    for i in range(len(subject)):
        g = used_genes[i]
        if g["type"] == "control":
            deactivated.extend(g["variants"][subject[i]]["deactivate"])
    # get flags
    for i in range(len(subject)):
        if subject[i] == None or is_deactivated(used_genes[i]["groups"], deactivated):
            continue
        g = used_genes[i]
        if g["type"] == "control":
            active.append(g["variants"][subject[i]]["format"])
        elif g["type"] == "bool":
            if subject[i]:
                active.append(g["format"])
        else:
            active.append(g["format"].format(subject[i]))
    return active



if __name__ == '__main__':
    set_seed(913)
    a = new_subject()
    b = new_subject()
    c = crossover(a, b)
    print("Subj 1", a)
    print("Subj 2", b)
    print("Child", c)
    
    print("Subj 1 flags", get_active_genes(a))

    def detect_mutation(a,b,c):
        for i in range(len(c)):
            if c[i] != a[i] and c[i] != b[i]:
                return True
        return False
    
    print("Mutations")
    pop_size = 40
    pop = [[crossover(a,b), k + 1] for k in range(pop_size)]
    mutated = 0
    for s, _ in pop:
        if detect_mutation(a,b,s):
            mutated += 1
    print(mutated, "out of", pop_size, "mutated")
    
    pop = next_generation(pop, 40)
    print("Selected")
    for i in range(20):
        print(pop[i][1], end=" ")


    