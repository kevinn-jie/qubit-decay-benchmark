## What a SWAP gate is

A SWAP gate exchanges the states of two qubits: |a⟩|b⟩ becomes |b⟩|a⟩.

On IBM hardware, a two-qubit gate like CZ only works between qubits that are physically wired together. Current IBM chips use a sparse "heavy-hex" layout, where each qubit connects to only 2–3 neighbours. If your circuit asks for a CZ between two qubits that aren't connected, the transpiler (Qiskit's SABRE routing pass) inserts SWAPs to move one qubit's state next to the other.

A SWAP isn't a native gate. It's built from **3 two-qubit gates** plus some single-qubit gates. Two-qubit gates are the noisiest operations on the chip, typically about 10× worse than single-qubit gates.

**Example:** physical qubits connected in a line, `0 — 1 — 2`.
- `cz(0, 1)` → 1 CZ.
- `cz(0, 2)` → SWAP(1,2), then CZ(0,1) → about 4 CZs instead of 1.

## Why this matters for your project

In `make_layer` ([circuit.py:35-43](src/circuit.py#L35-L43)) you shuffle qubits and pair them at random, without knowing which qubits are connected. That causes four problems:

1. **Your depth axis stops being accurate.** You're measuring accuracy against `depth`, but the circuit that actually runs might have 1 CZ in one layer and 7 in the next. The decay curve then reflects routing overhead, not depth.
2. **Extra variance.** Each random circuit needs a different number of SWAPs. Circuits at the same depth can carry very different amounts of noise, so you'd need more samples to get a clean curve.
3. **`two_qubit_density` loses its meaning.** You set how often a CZ appears, but routing adds a hidden, uncontrolled number of extra two-qubit gates.
4. **Weaker comparison between hardware and simulation.** Both run the same transpiled circuit, so the comparison isn't invalid. But your conclusions become things like "the noise model predicts SABRE's routing of my circuit". The cleaner claim you want is "the noise model predicts error per layer".

With 3 qubits you may be fine if you happen to get 3 connected ones. As qubit count grows, this gets worse quickly.

## Fix

Make sure every CZ already sits on a hardware connection, so the router has nothing to add:

1. Choose a fixed set of connected physical qubits on the device. A simple chain is easiest.
2. In `make_layer`, only pair qubits that are connected within that set. For example, shuffle the list of connections and greedily pick ones that don't share a qubit.
3. Transpile with `initial_layout` set to those physical qubits.
4. Check: `transpiled.count_ops().get("swap", 0) == 0`, and the CZ count matches what you generated.

I can implement this in `circuit.py` if you'd like.

One caveat: the details on Heron's native gates (CZ) and heavy-hex connectivity come mostly from secondary sources and preprints, not official IBM gate-set docs. You can confirm them directly with `backend.target` / `backend.coupling_map`.

Sources:
- [IBM SABRE transpilation tutorial](https://quantum.cloud.ibm.com/docs/tutorials/transpilation-optimizations-with-sabre)
- [IBM Heron R2 overview](https://postquantum.com/industry-news/ibm-heron-r2-quantum/)
- [Heron native gate set (arXiv:2602.10695)](https://arxiv.org/pdf/2602.10695)
- [SWAP = 3 two-qubit gates (RubriQ, arXiv:2607.07554)](https://arxiv.org/pdf/2607.07554)
- [Gate teleportation routing on heavy-hex (arXiv:2502.04138)](https://arxiv.org/html/2502.04138v2)
- [Quantum connectivity explainer](https://www.freecodecamp.org/news/how-quantum-connectivity-shapes-what-your-quantum-computer-can-actually-compute/)