import random
import qiskit


def apply_one_qubit_clifford(layer: qiskit.QuantumCircuit, gate: str, qubit: int) -> None:
    match gate:
        case "id":
            layer.id(qubit)
        case "x":
            layer.x(qubit)
        case "y":
            layer.y(qubit)
        case "z":
            layer.z(qubit)
        case "h":
            layer.h(qubit)
        case "s":
            layer.s(qubit)
        case "sdg":
            layer.sdg(qubit)
        case _:
            raise ValueError(f"error: unknown one-qubit Clifford gate {gate}")


def make_layer(qubit_count: int, two_qubit_density: float, rng: random.Random) -> qiskit.QuantumCircuit:
    one_qubit_cliffords: list[str] = ["id", "x", "y", "z", "h", "s", "sdg"]
    layer: qiskit.QuantumCircuit = qiskit.QuantumCircuit(qubit_count)

    for qubit in range(qubit_count):
        gate: str = rng.choice(one_qubit_cliffords)

        # note: more readable than getattr(layer, gate)(qubit)
        apply_one_qubit_clifford(layer, gate, qubit)

    qubits: list[int] = list(range(qubit_count))
    rng.shuffle(qubits)

    for index in range(0, len(qubits) - 1, 2):
        qubit1: int = qubits[index]
        qubit2: int = qubits[index + 1]

        if rng.random() < two_qubit_density:
            layer.cz(qubit1, qubit2)

    return layer


def make_layers(qubit_count: int, depth: int, two_qubit_density: float, rng: random.Random) -> list[qiskit.QuantumCircuit]:
    layers: list[qiskit.QuantumCircuit] = []

    for index in range(depth):
        layer: qiskit.QuantumCircuit = make_layer(qubit_count, two_qubit_density, rng)
        layers.append(layer)

    return layers


def make_mirror_circuit(qubit_count: int, depth: int, two_qubit_density: float, rng: random.Random) -> qiskit.QuantumCircuit:
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


def main() -> None:
    qubit_count: int = 3
    depth: int = 4
    two_qubit_density: float = 0.5
    rng: random.Random = random.Random(0)
    circuit: qiskit.QuantumCircuit = make_mirror_circuit(qubit_count, depth, two_qubit_density, rng)
    print(circuit.draw())


if __name__ == "__main__":
    main()