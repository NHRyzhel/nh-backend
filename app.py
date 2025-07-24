from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
CORS(app)

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.get_json()
    ninjas = data['ninjas']
    combos = data['combos']
    priority = data.get('priority', 'hp')

    POP_SIZE = 100
    GENERATIONS = 100
    MUTATION_RATE = 0.1

    def total_stat(combo_list):
        total = {'atk': 0, 'def': 0, 'hp': 0, 'agi': 0}
        for c in combo_list:
            for key in total:
                total[key] += int(c['attributes'].get(key, 0))
        return total

    def evaluate(team):
        active = [c for c in combos if all(n in team for n in c['ninjas'])]
        return total_stat(active)

    def fitness(stat):
        if priority == 'total':
            return sum(stat.values())
        return stat[priority]

    def crossover(p1, p2):
        child = list(set(p1[:8] + p2[8:]))
        while len(child) < 15:
            n = random.choice(ninjas)
            if n not in child:
                child.append(n)
        return child

    def mutate(team):
        if random.random() < MUTATION_RATE:
            idx = random.randint(0, 14)
            replacement = random.choice([n for n in ninjas if n not in team])
            team[idx] = replacement
        return team

    population = [random.sample(ninjas, 15) for _ in range(POP_SIZE)]

    for _ in range(GENERATIONS):
        scored = [(team, evaluate(team)) for team in population]
        scored.sort(key=lambda x: fitness(x[1]), reverse=True)
        top = scored[:POP_SIZE // 2]
        next_gen = [t for t, _ in top]
        while len(next_gen) < POP_SIZE:
            p1, p2 = random.sample(top, 2)
            child = mutate(crossover(p1[0], p2[0]))
            next_gen.append(child)
        population = next_gen

    best_team = scored[0][0]
    best_stat = scored[0][1]

    return jsonify({
        'best_team': best_team,
        'stat': best_stat
    })

import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
