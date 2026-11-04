import random
import qiskit
import circuit_maker


def main() -> None:
    qubit_count: int = 3
    depth: int = 4
    two_qubit_density: float = 0.5
    rng: random.Random = random.Random(0)
    circuit: qiskit.QuantumCircuit = circuit_maker.make_mirror_circuit(qubit_count, depth, two_qubit_density, rng)
    print(circuit.draw())
    print(f"all zeros: {circuit_maker.is_all_zeros(circuit, qubit_count)}")
    print(f"identity: {circuit_maker.is_identity(circuit, qubit_count)}")


if __name__ == "__main__":
    main()