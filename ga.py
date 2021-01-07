import json, random

with open("genes.json") as gene_file:
    gene_template = json.load(gene_file)


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
    "int": lambda g: choose_value_or_null(random.choice(value_range(g)), 0.2),
    "double": lambda g: choose_value_or_null(random.choice(value_range(g)), 0.2),
    "bool": lambda g: random.random() >= 0.5
}


def set_seed(s):
    random.seed(s)


def new_subject():
    sequence = []
    for gene in gene_template['genes']:
        sequence.append(gene_init[gene["type"]](gene))
    return sequence


def crossover(sbj1, sbj2):
    new_sbj = []
    for i in range(len(sbj1)):
        if random.random() >= 0.5:
            new_sbj.append(sbj2[i])
        else:
            new_sbj.append(sbj1[i])
    return new_sbj


def new_generation(target):
    return [[new_subject(), 999999] for i in range(target)] #genes, time


def next_generation(subjects, target):
    random.shuffle(subjects)
    for i in range(0, len(subjects)-1, 2):
        j = i+1
        subjects.append([crossover(subjects[i][0], subjects[j][0]), 999999])
        subjects.append([crossover(subjects[i][0], subjects[j][0]), 999999])
    while len(subjects) < target:
        i,j = random.choices(range(len(subjects)), k=2)
        subjects.append([crossover(subjects[i][0], subjects[j][0]), 999999])
    return subjects


def get_active_genes(subject):
    active = []
    deactivated = []
    for i in range(len(subject)):
        if i in deactivated or subject[i] == None:
            continue
        g = gene_template["genes"][i] 
        if g["type"] == "control":
            deactivated.extend(g["variants"][subject[i]]["deactivate"])
            active.append(g["variants"][subject[i]]["format"])
        elif g["type"] == "bool":
            if subject[i]:
                active.append(g["format"])
        else:
            active.append(g["format"].format(subject[i]))
    return active



if __name__ == '__main__':
    set_seed(48)
    a = new_subject()
    b = new_subject()
    print("Subj 1", a)
    print("Subj 2", b)
    print("Child", crossover(a, b))
    print("Subj 1 flags", get_active_genes(a))