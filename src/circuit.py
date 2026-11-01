import random
import qiskit


def make_layer(qubit_count: int, rng: random.Random, two_qubit_density: float) -> qiskit.QuantumCircuit:
    one_qubit_cliffords: list[str] = ["id", "x", "y", "z", "h", "s", "sdg"]
    layer: qiskit.QuantumCircuit = qiskit.QuantumCircuit(qubit_count)

    for qubit in range(qubit_count):
        gate: str = rng.choice(one_qubit_cliffords)
        getattr(layer, gate)(qubit)

    qubits: list[int] = list(range(qubit_count))
    rng.shuffle(qubits)

    for qubit1, qubit2 in zip(qubits[::2], qubits[1::2]):
        if rng.random() < two_qubit_density:
            layer.cz(qubit1, qubit2)

    return layer


def main() -> None:
    qubit_count: int = 3
    rng: random.Random = random.Random(0)
    two_qubit_density: float = 0.5
    layer: qiskit.QuantumCircuit = make_layer(qubit_count, rng, two_qubit_density)
    print(layer.draw())


if __name__ == "__main__":
    main()