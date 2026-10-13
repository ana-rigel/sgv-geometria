"""
sgv_rtt_operator.py — Módulo RTT (Redes de Transição Topológica) para o SGV
============================================================================

Versão de teste (local, ainda fora do repositório sgv-geometria).

Mantém a essência do desenho original:
    trajetória X_t = (z_t, iota_t, nu_t)
      -> quantização em N nós (protótipos)
      -> cadeia de Markov discreta entre nós
      -> corrente líquida / irreversibilidade
      -> projeção da densidade futura rho(H)

Correções técnicas em relação ao prompt original
-----------------------------------------------
C1  Corrente de probabilidade com peso de ocupação:
        J_ij = (N_ij - N_ji) / T      (= pi_i P_ij - pi_j P_ji empírico)
    O antigo J = P - P^T NÃO zera numa cadeia reversível com pi não uniforme.
    Ele é mantido só como diagnóstico `legacy_frobenius_P_minus_PT`.

C2  Produção de entropia de verdade (por passo):
        sigma = 1/2 * sum_ij (N_ij - N_ji)/T * ln((N_ij + a)/(N_ji + a))
    em vez de ||J||_F.

C3  Propagação da densidade com convenção de vetor-linha:
        rho(H) = rho0 @ P^H                       (padrão: 'discrete')
        rho(H) = rho0 @ expm(alpha * H * (P - I)) (opção: 'ctmc')
    O L = D - A com contagens brutas faz nós muito visitados "vazarem" mais
    rápido (taxa ~ ocupação). A versão normalizada D^-1 (-L) = P - I é a
    que entra aqui. Com alpha = 1, 'ctmc' é P^H suavizado por Poisson.

C4  Tamanho estatístico: padrão n_nodes=20, pseudocontagem de Dirichlet,
    linhas sem saída tratadas (sem NaN).

C5  Rótulos estáveis: codebook ajustado UMA vez (ex.: período de exploração)
    e congelado. Se precisar reajustar, `align_codebook` faz o casamento
    húngaro com os centróides anteriores.

C6  Padronização de (z, iota, nu) antes da distância euclidiana.

C7  Teste de Chapman–Kolmogorov (P estimada no lag k vs P^k).

C8  Nulas de irreversibilidade:
      - 'reversible_bootstrap': cadeia reversibilizada com a mesma pi
        (mede o viés de amostragem finita, que torna sigma sempre > 0);
      - 'pipeline': retornos embaralhados/invertidos passados pelo MESMO
        cálculo de features (mede a irreversibilidade criada pelos filtros
        causais de z, iota, nu).

C9  Validação walk-forward por log score contra baselines
    (persistência, estacionária pi, P^H, CTMC).

Nada aqui toca dados reservados: as funções recebem o que você passar.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, Optional, Sequence

import numpy as np
import pandas as pd
from scipy.linalg import expm
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import KMeans, MiniBatchKMeans

FEATURES = ("z", "iota", "nu")


# ---------------------------------------------------------------------------
# Núcleo matemático (funções puras, vetorizadas)
# ---------------------------------------------------------------------------

def transition_counts(nodes: np.ndarray, n_nodes: int, lag: int = 1) -> np.ndarray:
    """Matriz N_ij = #{t : node_t = i, node_{t+lag} = j}. Sem loops."""
    nodes = np.asarray(nodes, dtype=np.int64)
    if nodes.size <= lag:
        return np.zeros((n_nodes, n_nodes), dtype=float)
    src, dst = nodes[:-lag], nodes[lag:]
    flat = np.bincount(src * n_nodes + dst, minlength=n_nodes * n_nodes)
    return flat.reshape(n_nodes, n_nodes).astype(float)


def transition_matrix(counts: np.ndarray, pseudocount: float = 0.1) -> np.ndarray:
    """P_ij com pseudocontagem; linha sem nenhuma saída vira auto-laço (C4)."""
    C = counts + pseudocount
    rows = C.sum(axis=1, keepdims=True)
    P = np.divide(C, rows, out=np.zeros_like(C), where=rows > 0)
    empty = rows.ravel() == 0
    if empty.any():
        P[empty] = 0.0
        P[empty, np.flatnonzero(empty)] = 1.0
    return P


def occupation(counts: np.ndarray) -> np.ndarray:
    """pi empírica a partir das contagens de saída."""
    n = counts.sum(axis=1)
    tot = n.sum()
    return n / tot if tot > 0 else np.full(len(n), 1.0 / len(n))


def probability_current(counts: np.ndarray) -> np.ndarray:
    """C1: J_ij = (N_ij - N_ji)/T, antissimétrica, com peso de ocupação."""
    T = counts.sum()
    return (counts - counts.T) / T if T > 0 else np.zeros_like(counts)


def entropy_production(counts: np.ndarray, a: float = 0.5) -> float:
    """C2: produção de entropia por passo (nats/transição), estimador plug-in
    com pseudocontagem `a` nos pares visitados. Auto-laços não contribuem."""
    T = counts.sum()
    if T == 0:
        return 0.0
    N, Nt = counts, counts.T
    visited = (N + Nt) > 0
    np.fill_diagonal(visited, False)
    flux = (N - Nt) / T
    logr = np.log((N + a) / (Nt + a))
    return float(0.5 * np.sum(flux[visited] * logr[visited]))


def propagate(rho0: np.ndarray, P: np.ndarray, horizons: Iterable[int],
              mode: str = "discrete", alpha: float = 1.0) -> Dict[int, np.ndarray]:
    """C3: rho(H) como VETOR-LINHA. Preserva massa e positividade."""
    rho0 = np.asarray(rho0, dtype=float)
    out = {}
    if mode == "discrete":
        for H in horizons:
            out[int(H)] = rho0 @ np.linalg.matrix_power(P, int(H))
    elif mode == "ctmc":
        Q = P - np.eye(len(P))
        for H in horizons:
            out[int(H)] = rho0 @ expm(alpha * float(H) * Q)
    else:
        raise ValueError("mode deve ser 'discrete' ou 'ctmc'")
    return out


def reversibilized(counts: np.ndarray, pseudocount: float = 0.1) -> np.ndarray:
    """Cadeia reversível com a mesma ocupação: P_rev = S / rowsum(S), S simétrica.
    A pseudocontagem entra SÓ nas arestas observadas (e na diagonal): espalhá-la
    pela matriz toda cria ciclos inexistentes e infla a nula."""
    S = 0.5 * (counts + counts.T)
    support = (S > 0) | np.eye(len(S), dtype=bool)
    return transition_matrix(S + pseudocount * support, 0.0)


def simulate_chain(P: np.ndarray, n_steps: int, n_rep: int, start_dist: np.ndarray,
                   rng: np.random.Generator) -> np.ndarray:
    """Simula n_rep cadeias em paralelo (vetorizado nas réplicas). -> (n_rep, n_steps)"""
    cum = np.cumsum(P, axis=1)
    cum[:, -1] = 1.0
    states = np.empty((n_rep, n_steps), dtype=np.int64)
    states[:, 0] = rng.choice(len(P), size=n_rep, p=start_dist)
    u = rng.random((n_rep, n_steps))
    for t in range(1, n_steps):
        states[:, t] = (u[:, t, None] > cum[states[:, t - 1]]).sum(axis=1)
    return np.minimum(states, len(P) - 1)


def chapman_kolmogorov(nodes: np.ndarray, n_nodes: int, k: int = 5,
                       pseudocount: float = 0.1) -> Dict[str, float]:
    """C7: distância de variação total média (ponderada por pi) entre
    P_k estimada diretamente no lag k e P_1^k. ~0 se a discretização é Markov."""
    C1 = transition_counts(nodes, n_nodes, 1)
    Ck = transition_counts(nodes, n_nodes, k)
    P1k = np.linalg.matrix_power(transition_matrix(C1, pseudocount), k)
    Pk = transition_matrix(Ck, pseudocount)
    pi = occupation(Ck)
    tv_rows = 0.5 * np.abs(Pk - P1k).sum(axis=1)
    return {"k": k, "tv_weighted": float(pi @ tv_rows), "tv_max": float(tv_rows[pi > 0].max())}


# ---------------------------------------------------------------------------
# Operador
# ---------------------------------------------------------------------------

@dataclass
class TopologyGraphOperator:
    n_nodes: int = 20
    window_size: int = 1440
    horizons: Sequence[int] = (5, 15, 60)
    pseudocount: float = 0.1
    sigma_pseudocount: float = 0.5
    propagation: str = "discrete"   # 'discrete' (padrão) ou 'ctmc'
    alpha: float = 1.0               # só usado em 'ctmc'
    clusterer: str = "kmeans"        # 'kmeans' ou 'minibatch'
    random_state: int = 0

    mean_: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    scale_: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    centroids_std_: Optional[np.ndarray] = field(default=None, init=False, repr=False)
    _stream_nodes: deque = field(default_factory=deque, init=False, repr=False)
    _stream_counts: Optional[np.ndarray] = field(default=None, init=False, repr=False)

    # ---------------- codebook (C5, C6) ----------------
    @staticmethod
    def _as_array(X) -> np.ndarray:
        if isinstance(X, pd.DataFrame):
            return X.loc[:, list(FEATURES)].to_numpy(dtype=float)
        X = np.asarray(X, dtype=float)
        return X.reshape(1, -1) if X.ndim == 1 else X

    def fit_codebook(self, X_explore) -> "TopologyGraphOperator":
        """Ajusta padronização + nós UMA vez (período de exploração) e congela."""
        X = self._as_array(X_explore)
        X = X[np.isfinite(X).all(axis=1)]
        self.mean_ = X.mean(axis=0)
        self.scale_ = X.std(axis=0)
        self.scale_[self.scale_ == 0] = 1.0
        Xs = (X - self.mean_) / self.scale_
        if self.clusterer == "minibatch":
            km = MiniBatchKMeans(n_clusters=self.n_nodes, random_state=self.random_state,
                                 n_init=10, batch_size=2048)
        else:
            km = KMeans(n_clusters=self.n_nodes, random_state=self.random_state, n_init=10)
        km.fit(Xs)
        C = km.cluster_centers_
        # ordem canônica reprodutível (lexicográfica em z, iota, nu padronizados)
        self.centroids_std_ = C[np.lexsort(C.T[::-1])]
        return self

    def align_codebook(self, new_centroids_std: np.ndarray) -> np.ndarray:
        """Se um reajuste for inevitável: casamento húngaro com os nós atuais,
        para que o nó k continue significando a mesma região."""
        cost = ((self.centroids_std_[:, None, :] - new_centroids_std[None, :, :]) ** 2).sum(-1)
        _, col = linear_sum_assignment(cost)
        return new_centroids_std[col]

    @property
    def centroids(self) -> np.ndarray:
        """Centróides na escala original (z, iota, nu)."""
        self._check_fitted()
        return self.centroids_std_ * self.scale_ + self.mean_

    def _check_fitted(self):
        if self.centroids_std_ is None:
            raise RuntimeError("Chame fit_codebook() antes (codebook congelado).")

    def predict_node(self, X) -> np.ndarray:
        self._check_fitted()
        Xs = (self._as_array(X) - self.mean_) / self.scale_
        d2 = ((Xs[:, None, :] - self.centroids_std_[None, :, :]) ** 2).sum(-1)
        return d2.argmin(axis=1)

    # ---------------- assinatura RTT ----------------
    def signature_from_counts(self, counts: np.ndarray, current_node: int) -> Dict:
        P = transition_matrix(counts, self.pseudocount)
        pi = occupation(counts)
        J = probability_current(counts)
        rho0 = np.zeros(self.n_nodes)
        rho0[current_node] = 1.0
        n_out = counts.sum(axis=1)
        T = counts.sum()
        return {
            "centroids": self.centroids,
            "current_node": int(current_node),
            "transition_matrix": P,
            "occupation": pi,
            "probability_current": J,
            "entropy_production": entropy_production(counts, self.sigma_pseudocount),
            "predicted_density_vector": propagate(rho0, P, self.horizons,
                                                  self.propagation, self.alpha),
            "diagnostics": {
                "n_transitions": int(T),
                "self_transition_frac": float(np.trace(counts) / T) if T else np.nan,
                "nodes_without_exit": int((n_out == 0).sum()),
                "transitions_per_cell": float(T / self.n_nodes ** 2),
                "legacy_frobenius_P_minus_PT": float(np.linalg.norm(P - P.T)),
                "current_frobenius": float(np.linalg.norm(J)),
            },
        }

    def fit_transform(self, df_1m: pd.DataFrame) -> Dict:
        """Interface original: assinatura sobre a última janela de `df_1m`.
        Exige codebook já congelado (fit_codebook)."""
        X = self._as_array(df_1m)[-self.window_size:]
        nodes = self.predict_node(X)
        counts = transition_counts(nodes, self.n_nodes)
        return self.signature_from_counts(counts, nodes[-1])

    # ---------------- tempo real (loop de 1 min) ----------------
    def step(self, x_t) -> Dict:
        """Atualização O(1) das contagens na janela deslizante + assinatura."""
        node = int(self.predict_node(x_t)[0])
        if self._stream_counts is None:
            self._stream_counts = np.zeros((self.n_nodes, self.n_nodes))
        if self._stream_nodes:
            self._stream_counts[self._stream_nodes[-1], node] += 1
        self._stream_nodes.append(node)
        if len(self._stream_nodes) > self.window_size:
            a = self._stream_nodes.popleft()
            self._stream_counts[a, self._stream_nodes[0]] -= 1
        return self.signature_from_counts(self._stream_counts, node)

    # ---------------- nulas de irreversibilidade (C8) ----------------
    def null_reversible_bootstrap(self, counts: np.ndarray, n_rep: int = 200,
                                  seed: int = 0) -> Dict:
        """Distribuição de sigma sob uma cadeia REVERSÍVEL com a mesma pi e o
        mesmo número de transições. Responde: o sigma observado excede o viés
        de amostragem finita?"""
        rng = np.random.default_rng(seed)
        P_rev = reversibilized(counts, self.pseudocount)
        T = int(counts.sum())
        pi = occupation(counts)
        sims = simulate_chain(P_rev, T + 1, n_rep, pi, rng)
        null = np.array([entropy_production(transition_counts(s, self.n_nodes),
                                            self.sigma_pseudocount) for s in sims])
        obs = entropy_production(counts, self.sigma_pseudocount)
        return {"sigma_obs": obs, "null": null,
                "p_value": float((1 + (null >= obs).sum()) / (1 + n_rep))}

    def null_pipeline(self, close: np.ndarray,
                      feature_fn: Callable[[np.ndarray], pd.DataFrame],
                      n_rep: int = 50, kind: str = "shuffle", seed: int = 0) -> Dict:
        """Irreversibilidade criada pelo PRÓPRIO pipeline de features.
        Gera preços sintéticos a partir dos retornos log de `close`
        ('shuffle' = permutação; 'reverse' = ordem invertida, 1 réplica),
        recalcula (z, iota, nu) com `feature_fn`, discretiza com o codebook
        congelado e mede sigma na última janela."""
        rng = np.random.default_rng(seed)
        close = np.asarray(close, dtype=float)
        r = np.diff(np.log(close))

        def sigma_of(price):
            F = feature_fn(price)
            X = self._as_array(F)
            X = X[np.isfinite(X).all(axis=1)][-self.window_size:]
            c = transition_counts(self.predict_node(X), self.n_nodes)
            return entropy_production(c, self.sigma_pseudocount)

        obs = sigma_of(close)
        if kind == "reverse":
            reps = [r[::-1]]
        elif kind == "shuffle":
            reps = [rng.permutation(r) for _ in range(n_rep)]
        else:
            raise ValueError("kind deve ser 'shuffle' ou 'reverse'")
        null = np.array([sigma_of(close[0] * np.exp(np.concatenate([[0.0], np.cumsum(rr)])))
                         for rr in reps])
        return {"sigma_obs": obs, "null": null, "kind": kind,
                "p_value": float((1 + (null >= obs).sum()) / (1 + len(null)))}


# ---------------------------------------------------------------------------
# Validação walk-forward (C9)
# ---------------------------------------------------------------------------

def walk_forward_logscore(nodes: np.ndarray, n_nodes: int, window: int,
                          horizons: Sequence[int] = (5, 15, 60), stride: int = 10,
                          pseudocount: float = 0.1, eps: float = 1e-3,
                          alpha: float = 1.0) -> Dict:
    """Em cada t (de `stride` em `stride`), estima P só com transições até t,
    prevê o nó em t+H e pontua log p(nó realizado). Métodos:
        persistence  : fração de auto-transição no nó atual, resto em pi
        stationary   : pi da janela
        markov_PH    : rho0 @ P^H
        ctmc         : rho0 @ expm(alpha H (P - I))
    Retorna tabela de médias e as séries por t (para teste pareado)."""
    nodes = np.asarray(nodes, dtype=np.int64)
    Hmax = max(horizons)
    ts = np.arange(window, len(nodes) - Hmax, stride)
    methods = ("persistence", "stationary", "markov_PH", "ctmc")
    scores = {(m, H): [] for m in methods for H in horizons}
    counts = transition_counts(nodes[:window + 1], n_nodes)
    t_prev = window
    for t in ts:
        # desliza a janela [t-window, t] de forma incremental
        for s in range(t_prev + 1, t + 1):
            counts[nodes[s - 1], nodes[s]] += 1
            counts[nodes[s - window - 1], nodes[s - window]] -= 1
        t_prev = t
        P = transition_matrix(counts, pseudocount)
        pi = occupation(counts)
        pi = (1 - eps) * pi + eps / n_nodes
        rho0 = np.zeros(n_nodes)
        rho0[nodes[t]] = 1.0
        d = propagate(rho0, P, horizons, "discrete")
        c = propagate(rho0, P, horizons, "ctmc", alpha)
        stay = np.trace(counts) / max(counts.sum(), 1.0)
        pers = stay * rho0 + (1 - stay) * pi   # persistência calibrada
        for H in horizons:
            y = nodes[t + H]
            scores[("persistence", H)].append(np.log(pers[y]))
            scores[("stationary", H)].append(np.log(pi[y]))
            scores[("markov_PH", H)].append(np.log(max(d[H][y], 1e-12)))
            scores[("ctmc", H)].append(np.log(max(c[H][y], 1e-12)))
    series = {k: np.asarray(v) for k, v in scores.items()}
    table = pd.DataFrame({m: {H: series[(m, H)].mean() for H in horizons} for m in methods})
    table.index.name = "H"
    return {"table": table, "series": series, "n_forecasts": len(ts)}
