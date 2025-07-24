from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import os

app = Flask(__name__)
CORS(app)

@app.route('/optimize', methods=['POST'])
def optimize():
    data = request.get_json()
    ninjas = data['ninjas']
    combos = data['combos']
    priority = data.get('priority', 'hp')
    main_ninjas = data.get('main_ninjas', [])[:3]  # Ambil maksimal 3

    POP_SIZE = 200
    GENERATIONS = 100
    MUTATION_RATE = 0.1
    ELITE_COUNT = 5
    RUNS = 3
    TOURNAMENT_SIZE = 5

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
        elif priority == 'atk+hp':
            return stat['atk'] + stat['hp']
        elif priority == 'hp+agi':
            return stat['hp'] + stat['agi']
        elif priority == 'atk+hp+agi':
            return stat['atk'] + stat['hp'] + stat['agi']
        else:
            return stat.get(priority, 0)

    def crossover(p1, p2):
        base = [n for n in (p1[:8] + p2[8:]) if n not in main_ninjas]
        child = []
        for n in base:
            if n not in child and len(child) < 15 - len(main_ninjas):
                child.append(n)
        child = main_ninjas + child
        while len(child) < 15:
            n = random.choice(ninjas)
            if n not in child:
                child.append(n)
        return child

    def mutate(team):
        if random.random() < MUTATION_RATE:
            idx = random.randint(len(main_ninjas), 14)  # jangan ganti posisi 0–2
            replacement = random.choice([n for n in ninjas if n not in team])
            team[idx] = replacement
        return team

    def tournament_selection(scored):
        return max(random.sample(scored, TOURNAMENT_SIZE), key=lambda x: fitness(x[1]))

    best_result = None

    for _ in range(RUNS):
        def generate_individual():
            pool = [n for n in ninjas if n not in main_ninjas]
            individual = random.sample(pool, 15 - len(main_ninjas))
            return main_ninjas + individual

        population = [generate_individual() for _ in range(POP_SIZE)]

        for _ in range(GENERATIONS):
            scored = [(team, evaluate(team)) for team in population]
            scored.sort(key=lambda x: fitness(x[1]), reverse=True)
            elites = [t for t, _ in scored[:ELITE_COUNT]]
            next_gen = elites[:]
            while len(next_gen) < POP_SIZE:
                p1 = tournament_selection(scored)
                p2 = tournament_selection(scored)
                child = mutate(crossover(p1[0], p2[0]))
                next_gen.append(child)
            population = next_gen

        final_scored = [(team, evaluate(team)) for team in population]
        final_scored.sort(key=lambda x: fitness(x[1]), reverse=True)
        top_team = final_scored[0]

        if not best_result or fitness(top_team[1]) > fitness(best_result[1]):
            best_result = top_team

    best_team, best_stat = best_result

    return jsonify({
        'best_team': best_team,
        'stat': best_stat
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
