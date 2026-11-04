import random
import qiskit
import qiskit.primitives
import qiskit.quantum_info


def make_layer(qubit_count: int, two_qubit_density: float, rng: random.Random) -> qiskit.QuantumCircuit:
    one_qubit_cliffords: list[str] = ["id", "x", "y", "z", "h", "s", "sdg"]
    layer: qiskit.QuantumCircuit = qiskit.QuantumCircuit(qubit_count)

    for qubit in range(qubit_count):
        gate: str = rng.choice(one_qubit_cliffords)
        getattr(layer, gate)(qubit)

    qubits: list[int] = list(range(qubit_count))
    rng.shuffle(qubits)

    for index in range(0, len(qubits) - 1, 2):
        qubit1: int = qubits[index]
        qubit2: int = qubits[index + 1]

        if rng.random() < two_qubit_density:
            # thought: reality does not guarantee neighboring qubits, so should change to avoid unwanted SWAP gates
            layer.cz(qubit1, qubit2)

    return layer


def make_layers(qubit_count: int, depth: int, two_qubit_density: float, rng: random.Random) -> list[qiskit.QuantumCircuit]:
    layers: list[qiskit.QuantumCircuit] = []

    for index in range(depth):
        layer: qiskit.QuantumCircuit = make_layer(qubit_count, two_qubit_density, rng)
        layers.append(layer)

    return layers


# thought: T1 relaxation makes noise push results to 0, so this could skew results
def make_mirror_circuit(qubit_count: int, depth: int, two_qubit_density: float, rng: random.Random) -> qiskit.QuantumCircuit:
    # thought: could add a random layer to enforce a non-0 answer
    layers: list[qiskit.QuantumCircuit] = make_layers(qubit_count, depth, two_qubit_density, rng)
    circuit: qiskit.QuantumCircuit = qiskit.QuantumCircuit(qubit_count)

    # note: the forward half
    for layer in layers:
        circuit.compose(layer, inplace=True)
        circuit.barrier()

    # note: the mirror half
    reversed_layers: list[qiskit.QuantumCircuit] = list(reversed(layers))

    for layer in reversed_layers:
        inverse_layer: qiskit.QuantumCircuit = layer.inverse()
        circuit.compose(inverse_layer, inplace=True)
        circuit.barrier()

    circuit.measure_all()
    return circuit


def is_all_zeros(circuit: qiskit.QuantumCircuit, qubit_count: int, shots: int = 1024) -> bool:
    sampler: qiskit.primitives.StatevectorSampler = qiskit.primitives.StatevectorSampler()
    result: qiskit.primitives.PrimitiveResult = sampler.run([circuit], shots=shots).result()
    counts: dict[str, int] = result[0].data.meas.get_counts()
    return counts == {"0" * qubit_count: shots}


def is_identity(circuit: qiskit.QuantumCircuit, qubit_count: int) -> bool:
    unmeasured_circuit: qiskit.QuantumCircuit = circuit.remove_final_measurements(inplace=False)
    identity: qiskit.QuantumCircuit = qiskit.QuantumCircuit(qubit_count)
    return qiskit.quantum_info.Operator(unmeasured_circuit).equiv(qiskit.quantum_info.Operator(identity))