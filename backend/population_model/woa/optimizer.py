import numpy as np

from population_model.bp.network import BPNeuralNetwork


def whale_optimization(
    x_train: np.ndarray,
    y_train: np.ndarray,
    input_size: int,
    hidden_size: int,
    population_size: int = 10,
    iterations: int = 30,
    seed: int = 42,
) -> tuple[BPNeuralNetwork, float]:
    """WOA-inspired metaheuristic to optimize BP weight vectors (research placeholder)."""
    rng = np.random.default_rng(seed)
    template = BPNeuralNetwork(input_size, hidden_size, seed=seed)
    dim = template.flatten().shape[0]

    agents = rng.normal(0, 0.1, size=(population_size, dim))
    fitness = np.array([_fitness(v, x_train, y_train, input_size, hidden_size, seed) for v in agents])
    best_idx = int(np.argmin(fitness))
    best = agents[best_idx].copy()
    best_fit = float(fitness[best_idx])

    for t in range(iterations):
        a = 2 - t * (2 / iterations)
        for i in range(population_size):
            r = rng.random()
            A = 2 * a * r - a
            C = 2 * r
            p = rng.random()
            if p < 0.5:
                if abs(A) < 1:
                    D = abs(C * best - agents[i])
                    agents[i] = best - A * D
                else:
                    rand_agent = agents[rng.integers(0, population_size)]
                    D = abs(C * rand_agent - agents[i])
                    agents[i] = rand_agent - A * D
            else:
                D = abs(best - agents[i])
                b = 1
                l = (2 * rng.random() - 1) if rng.random() > 0.5 else -1
                agents[i] = D * np.exp(b * l) * np.cos(2 * np.pi * l) + best
            fit = _fitness(agents[i], x_train, y_train, input_size, hidden_size, seed)
            if fit < fitness[i]:
                fitness[i] = fit
                if fit < best_fit:
                    best_fit = fit
                    best = agents[i].copy()

    net = BPNeuralNetwork(input_size, hidden_size, seed=seed)
    net.load_flat(best, input_size, hidden_size)
    return net, best_fit


def _fitness(params: np.ndarray, x: np.ndarray, y: np.ndarray, input_size: int, hidden_size: int, seed: int) -> float:
    net = BPNeuralNetwork(input_size, hidden_size, seed=seed)
    net.load_flat(params, input_size, hidden_size)
    return net.mse(x, y)
