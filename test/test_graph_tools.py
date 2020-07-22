import sys
import pytest


def test_compute_sccs():
    from pytools.graph import compute_sccs
    import random

    rng = random.Random(0)

    def generate_random_graph(nnodes):
        graph = dict((i, set()) for i in range(nnodes))
        for i in range(nnodes):
            for j in range(nnodes):
                # Edge probability 2/n: Generates decently interesting inputs.
                if rng.randint(0, nnodes - 1) <= 1:
                    graph[i].add(j)
        return graph

    def verify_sccs(graph, sccs):
        visited = set()

        def visit(node):
            if node in visited:
                return []
            else:
                visited.add(node)
                result = []
                for child in graph[node]:
                    result = result + visit(child)
                return result + [node]

        for scc in sccs:
            scc = set(scc)
            assert not scc & visited
            # Check that starting from each element of the SCC results
            # in the same set of reachable nodes.
            for scc_root in scc:
                visited.difference_update(scc)
                result = visit(scc_root)
                assert set(result) == scc, (set(result), scc)

    for nnodes in range(10, 20):
        for i in range(40):
            graph = generate_random_graph(nnodes)
            verify_sccs(graph, compute_sccs(graph))


def test_compute_topological_order():
    from pytools.graph import compute_topological_order, CycleError

    empty = {}
    assert compute_topological_order(empty) == []

    disconnected = {1: [], 2: [], 3: []}
    assert len(compute_topological_order(disconnected)) == 3

    line = list(zip(range(10), ([i] for i in range(1, 11))))
    import random
    random.seed(0)
    random.shuffle(line)
    expected = list(range(11))
    assert compute_topological_order(dict(line)) == expected

    claw = {1: [2, 3], 0: [1]}
    assert compute_topological_order(claw)[:2] == [0, 1]

    repeated_edges = {1: [2, 2], 2: [0]}
    assert compute_topological_order(repeated_edges) == [1, 2, 0]

    self_cycle = {1: [1]}
    with pytest.raises(CycleError):
        compute_topological_order(self_cycle)

    cycle = {0: [2], 1: [2], 2: [3], 3: [4, 1]}
    with pytest.raises(CycleError):
        compute_topological_order(cycle)


def test_transitive_closure():
    from pytools.graph import compute_transitive_closure

    # simple test
    graph = {
        1: set([2, ]),
        2: set([3, ]),
        3: set([4, ]),
        4: set(),
        }

    expected_closure = {
        1: set([2, 3, 4, ]),
        2: set([3, 4, ]),
        3: set([4, ]),
        4: set(),
        }

    closure = compute_transitive_closure(graph)

    assert closure == expected_closure

    # test with branches that reconnect
    graph = {
        1: set([2, ]),
        2: set(),
        3: set([1, ]),
        4: set([1, ]),
        5: set([6, 7, ]),
        6: set([7, ]),
        7: set([1, ]),
        8: set([3, 4, ]),
        }

    expected_closure = {
        1: set([2, ]),
        2: set(),
        3: set([1, 2, ]),
        4: set([1, 2, ]),
        5: set([1, 2, 6, 7, ]),
        6: set([1, 2, 7, ]),
        7: set([1, 2, ]),
        8: set([1, 2, 3, 4, ]),
        }

    closure = compute_transitive_closure(graph)

    assert closure == expected_closure

    # test with cycles
    graph = {
        1: set([2, ]),
        2: set([3, ]),
        3: set([4, ]),
        4: set([1, ]),
        }

    expected_closure = {
        1: set([1, 2, 3, 4, ]),
        2: set([1, 2, 3, 4, ]),
        3: set([1, 2, 3, 4, ]),
        4: set([1, 2, 3, 4, ]),
        }

    closure = compute_transitive_closure(graph)

    assert closure == expected_closure


def test_graph_cycle_finder():

    from pytools.graph import contains_cycle

    graph = {
        "a": set(["b", "c"]),
        "b": set(["d", "e"]),
        "c": set(["d", "f"]),
        "d": set(),
        "e": set(),
        "f": set(["g", ]),
        "g": set(),
        }

    assert not contains_cycle(graph)

    graph = {
        "a": set(["b", "c"]),
        "b": set(["d", "e"]),
        "c": set(["d", "f"]),
        "d": set(),
        "e": set(),
        "f": set(["g", ]),
        "g": set(["a", ]),
        }

    assert contains_cycle(graph)

    graph = {
        "a": set(["a", "c"]),
        "b": set(["d", "e"]),
        "c": set(["d", "f"]),
        "d": set(),
        "e": set(),
        "f": set(["g", ]),
        "g": set(),
        }

    assert contains_cycle(graph)

    graph = {
        "a": set(["a"]),
        }

    assert contains_cycle(graph)


def test_induced_subgraph():

    from pytools.graph import compute_induced_subgraph

    graph = {
        "a": set(["b", "c"]),
        "b": set(["d", "e"]),
        "c": set(["d", "f"]),
        "d": set(),
        "e": set(),
        "f": set(["g", ]),
        "g": set(["h", "i", "j"]),
        }

    node_subset = set(["b", "c", "e", "f", "g"])

    expected_subgraph = {
        "b": set(["e", ]),
        "c": set(["f", ]),
        "e": set(),
        "f": set(["g", ]),
        "g": set(),
        }

    subgraph = compute_induced_subgraph(graph, node_subset)

    assert subgraph == expected_subgraph


def test_prioritzed_topological_sort_examples():

    from pytools.graph import compute_topological_order

    priorities = {'a': 1, 'b': 2, 'c': 3, 'e': 4, 'd': 1}
    dag = {
            'a': ['b', 'c'],
            'b': [],
            'c': ['d', 'e'],
            'd': [],
            'e': []}

    def key(u):
        return priorities[u]

    assert compute_topological_order(dag, key=key) == ['a', 'c', 'e', 'b', 'd']

    priorities = {'a': 0, 'b': 5, 'c': 6, 'd': 7}
    dag = {
            'd': set('c'),
            'b': set('a'),
            'a': set(),
            'c': set('a'),
            }

    assert compute_topological_order(dag, key=priorities.get) == ['d', 'c', 'b', 'a']


def test_prioritzed_topological_sort():

    import random
    from pytools.graph import compute_topological_order
    rng = random.Random(0)

    def generate_random_graph(nnodes):
        graph = dict((i, set()) for i in range(nnodes))
        for i in range(nnodes):
            # to avoid cycles only consider edges node_i->node_j where j > i.
            for j in range(i+1, nnodes):
                # Edge probability 4/n: Generates decently interesting inputs.
                if rng.randint(0, nnodes - 1) <= 2:
                    graph[i].add(j)
        return graph

    nnodes = rng.randint(40, 100)
    rev_dep_graph = generate_random_graph(nnodes)
    dep_graph = dict((i, set()) for i in range(nnodes))

    for i in range(nnodes):
        for rev_dep in rev_dep_graph[i]:
            dep_graph[rev_dep].add(i)

    priority = [rng.random() for _ in range(nnodes)]
    topo_order = compute_topological_order(rev_dep_graph, key=priority.__getitem__)

    for scheduled_node in topo_order:
        nodes_with_no_deps = set(node for node, deps in dep_graph.items()
                    if len(deps) == 0)

        # check whether the order is a valid topological order
        assert scheduled_node in nodes_with_no_deps
        # check whether priorites are upheld
        assert priority[scheduled_node] == max(priority[node] for node in
                nodes_with_no_deps)

        # 'scheduled_node' is scheduled => no longer a dependency
        dep_graph.pop(scheduled_node)

        for node, deps in dep_graph.items():
            deps.discard(scheduled_node)

    assert len(dep_graph) == 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        exec(sys.argv[1])
    else:
        from pytest import main
        main([__file__])
