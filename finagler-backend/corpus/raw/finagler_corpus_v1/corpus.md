# Quantum Finagler corpus v1.0 (58 equations)

Retrieve entries relevant to the user's problem, explain the math, then (if backend_support is direct/partial and job_hint exists) propose ONE job via run_quantum_job. Fill only allowed job fields.

## Honesty rules

- Current quantum hardware is noisy and uncorrected; 100-qubit runs are experiments, not proofs of quantum advantage.
- Always report the classical baselines the backend returns (random_guess_mean_cut, true_optimum_bruteforce).
- Beyond about 30-40 qubits results cannot be verified by classical simulation except for structured circuits.
- Never present outputs on markets, health or moral questions as predictions or professional advice.
- If an equation is marked backend_support 'none', explain it as theory and do not pretend it was computed.

## Problem routing

- **Entanglement or device-noise benchmark, Bell/GHZ states** -> `ghz`  
  Example: `{"algorithm": "ghz", "num_qubits": 100, "shots": 2000}`
- **Graph partitioning, community split, max-cut, scheduling that reduces to cutting an unweighted graph** -> `qaoa_maxcut`  
  Example: `{"algorithm": "qaoa_maxcut", "num_qubits": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0], [0, 3]], "shots": 2000}`
- **Spin chains, magnets, quench dynamics, transverse-field Ising** -> `ising_trotter`  
  Example: `{"algorithm": "ising_trotter", "num_qubits": 20, "steps": 3, "j": 1.0, "h": 0.5, "dt": 0.2, "shots": 2000}`
- **Chemistry ground states, search, factoring, kernels, weighted QUBO, portfolio optimization** -> `None`  
  Not runnable in the backend yet. Explain the theory, say it is unsupported, and suggest the closest supported experiment.

## Backend limits

```json
{
  "simulator_max_qubits": {
    "ghz": 100,
    "ising_trotter": 100,
    "qaoa_maxcut": 24
  },
  "max_qubits": 156,
  "max_shots": 100000,
  "hardware_depth_limit": 500,
  "hardware_two_qubit_gate_limit": 3000,
  "qaoa_layers": "1-3",
  "ising_steps": "1-20",
  "hardware_requires": "the user's own IBM key; QPU time on the free plan is about 10 minutes per rolling window"
}
```

## Quantum Mechanics

### 1. Time-dependent Schrodinger equation (`schrodinger_time`)
- Equation: $i\hbar\,\frac{\partial \psi}{\partial t}=\hat H\psi$  
- Plain: `i*hbar * d(psi)/dt = H psi`
- Variables: psi: state; H: Hamiltonian operator; hbar = 1.054571817e-34 J*s
- Use when: Any isolated quantum system's dynamics; the starting point for Hamiltonian simulation.
- Quantum link: Gate-based machines approximate exp(-iHt/hbar) with gate sequences (see trotter_suzuki).
- Backend support: **partial**
- Job hint: `{"algorithm": "ising_trotter", "num_qubits": 20, "steps": 3, "j": 1.0, "h": 0.5, "dt": 0.2, "shots": 2000}`
- Caveat: Classical cost of exact solutions grows as 2^n for n qubits; only small or structured systems are exactly solvable.

### 2. Time-independent Schrodinger equation (`schrodinger_stationary`)
- Equation: $\hat H\psi=E\psi$  
- Plain: `H psi = E psi`
- Variables: H: Hamiltonian; psi: eigenstate; E: energy eigenvalue
- Use when: Finding energy levels and stationary states.
- Quantum link: Ground-state energy is the target of VQE-style methods (see vqe_variational).
- Backend support: **none**
- Caveat: The backend has no ground-state solver; this is theory context.

### 3. Born rule (`born_rule`)
- Equation: $P(i)=|\langle i|\psi\rangle|^2=|c_i|^2,\quad \sum_i P(i)=1$  
- Plain: `P(i) = |<i|psi>|^2`
- Variables: c_i: amplitude of basis state i
- Use when: Turning amplitudes into measurement probabilities.
- Quantum link: Every shot returns one bitstring drawn from this distribution; counts/shots estimates P(i).
- Backend support: **direct**
- Job hint: `{"algorithm": "ghz", "num_qubits": 3, "shots": 2000}`
- Caveat: Single shots are random; estimates carry shot noise (see shot_noise).

### 4. Expectation value (`expectation_value`)
- Equation: $\langle A\rangle=\langle\psi|A|\psi\rangle=\mathrm{Tr}(\rho A)$  
- Plain: `<A> = <psi|A|psi> = Tr(rho A)`
- Variables: A: observable; rho: density matrix
- Use when: Average outcome of measuring an observable.
- Quantum link: Z-type expectations come from counts: <Z_i> = P(0) - P(1) (the Ising analysis uses this).
- Backend support: **direct**
- Job hint: `{"algorithm": "ising_trotter", "num_qubits": 20, "steps": 3, "j": 1.0, "h": 0.5, "dt": 0.2, "shots": 2000}`
- Caveat: Non-Z observables need basis-change gates before measurement; the backend measures Z only.

### 5. Heisenberg uncertainty relation (`heisenberg_uncertainty`)
- Equation: $\sigma_x\sigma_p\ge\frac{\hbar}{2}$  
- Plain: `sigma_x * sigma_p >= hbar/2`
- Variables: sigma: standard deviation of position / momentum
- Use when: Bounding how sharply conjugate quantities can be known together.
- Quantum link: Underlies why measuring in one basis disturbs another.
- Backend support: **none**
- Caveat: A statistical property of prepared states, not a limit on measurement apparatus precision.

### 6. Robertson uncertainty relation (`robertson_uncertainty`)
- Equation: $\sigma_A\sigma_B\ge\tfrac12\left|\langle[\hat A,\hat B]\rangle\right|$  
- Plain: `sigma_A * sigma_B >= 0.5 * |<[A,B]>|`
- Variables: A, B: observables; [A,B] = AB - BA
- Use when: General bound for any two non-commuting observables.
- Quantum link: Pauli X, Y, Z do not commute, so they cannot all be sharp on one qubit.
- Backend support: **none**
- Caveat: Bound can be zero when the commutator expectation is zero.

### 7. Canonical commutation relation (`canonical_commutator`)
- Equation: $[\hat x,\hat p]=i\hbar$  
- Plain: `[x, p] = i*hbar`
- Variables: x: position operator; p: momentum operator
- Use when: Deriving uncertainty and quantization rules.
- Quantum link: Qubit analogue: [X, Y] = 2iZ (see pauli_matrices).
- Backend support: **none**
- Caveat: Only representable in infinite-dimensional spaces; qubits are finite-dimensional.

### 8. Time-evolution operator (`time_evolution_operator`)
- Equation: $U(t)=e^{-i\hat H t/\hbar},\quad U^\dagger U=I$  
- Plain: `U(t) = exp(-i H t / hbar), unitary`
- Variables: H: time-independent Hamiltonian
- Use when: Expressing dynamics as a reversible, norm-preserving map.
- Quantum link: A quantum circuit is a product of unitaries; Hamiltonian simulation implements U(t) directly.
- Backend support: **partial**
- Job hint: `{"algorithm": "ising_trotter", "num_qubits": 20, "steps": 3, "j": 1.0, "h": 0.5, "dt": 0.2, "shots": 2000}`
- Caveat: Exact exponentiation needs diagonalization; circuits approximate it with Trotter error.

### 9. Heisenberg equation of motion (`heisenberg_picture`)
- Equation: $\frac{dA}{dt}=\frac{i}{\hbar}[\hat H,A]+\frac{\partial A}{\partial t}$  
- Plain: `dA/dt = (i/hbar)[H, A] + dA/dt (explicit)`
- Variables: A: operator
- Use when: Tracking observables instead of states; conserved quantities when [H,A]=0.
- Quantum link: Useful for reasoning about which observables a circuit preserves.
- Backend support: **none**
- Caveat: Operator growth makes it hard to use classically for many-body systems.

### 10. Particle in an infinite box (`particle_in_box`)
- Equation: $E_n=\frac{n^2\pi^2\hbar^2}{2mL^2},\; n=1,2,\dots$  
- Plain: `E_n = n^2 * pi^2 * hbar^2 / (2 m L^2)`
- Variables: m: mass; L: box width; n: quantum number
- Use when: Quantum confinement, quantum dots, level spacing estimates.
- Quantum link: Textbook check for any discretized-Hamiltonian simulation.
- Backend support: **none**
- Caveat: Idealized: real wells are finite and their levels are lower.

### 11. Quantum harmonic oscillator (`harmonic_oscillator`)
- Equation: $E_n=\hbar\omega\left(n+\tfrac12\right)$  
- Plain: `E_n = hbar*omega*(n + 1/2)`
- Variables: omega: angular frequency
- Use when: Vibrations, trapped ions, superconducting resonators, small oscillations near a minimum.
- Quantum link: Transmon qubits are weakly anharmonic oscillators; the lowest two levels act as the qubit.
- Backend support: **none**
- Caveat: Real potentials are anharmonic at high n.

### 12. Tunneling probability (WKB) (`tunneling_wkb`)
- Equation: $T\approx\exp\!\left(-2\int_{x_1}^{x_2}\kappa(x)\,dx\right),\ \kappa=\frac{\sqrt{2m(V-E)}}{\hbar}$  
- Plain: `T ~ exp(-2 * integral(kappa dx)), kappa = sqrt(2m(V-E))/hbar`
- Variables: V: barrier; E: particle energy; x1,x2: turning points
- Use when: Estimating transmission through barriers: STM, tunnel junctions, decay rates.
- Quantum link: Josephson junctions in IBM's qubits rely on tunneling of Cooper pairs.
- Backend support: **none**
- Caveat: Approximation for smooth, thick barriers; poor near turning points.

### 13. Rabi oscillation (`rabi_oscillation`)
- Equation: $P_{0\to1}(t)=\frac{\Omega^2}{\Omega^2+\Delta^2}\sin^2\!\left(\tfrac12\sqrt{\Omega^2+\Delta^2}\,t\right)$  
- Plain: `P(t) = Omega^2/(Omega^2+Delta^2) * sin^2(sqrt(Omega^2+Delta^2) * t / 2)`
- Variables: Omega: Rabi frequency; Delta: detuning from resonance
- Use when: How a driven two-level system flips; the physical origin of single-qubit gates.
- Quantum link: A pi-pulse (Omega*t = pi) implements an X gate up to a global phase.
- Backend support: **none**
- Caveat: Ignores decoherence; real oscillations damp (see decoherence_t1_t2).


## Quantum Information

### 14. Qubit state and Bloch sphere (`qubit_bloch`)
- Equation: $|\psi\rangle=\cos\tfrac\theta2|0\rangle+e^{i\varphi}\sin\tfrac\theta2|1\rangle$  
- Plain: `|psi> = cos(theta/2)|0> + e^{i phi} sin(theta/2)|1>`
- Variables: theta in [0,pi], phi in [0,2pi): spherical angles
- Use when: Visualizing and parametrizing any pure single-qubit state.
- Quantum link: Single-qubit gates are rotations of the Bloch vector.
- Backend support: **direct**
- Job hint: `{"algorithm": "ghz", "num_qubits": 2, "shots": 2000}`
- Caveat: Only pure single-qubit states fit on the sphere surface; mixed states lie inside.

### 15. Pauli matrices (`pauli_matrices`)
- Equation: $\sigma_x=\begin{pmatrix}0&1\\1&0\end{pmatrix},\ \sigma_y=\begin{pmatrix}0&-i\\i&0\end{pmatrix},\ \sigma_z=\begin{pmatrix}1&0\\0&-1\end{pmatrix},\ [\sigma_i,\sigma_j]=2i\epsilon_{ijk}\sigma_k$  
- Plain: `X=[[0,1],[1,0]], Y=[[0,-i],[i,0]], Z=[[1,0],[0,-1]]; eigenvalues +/-1`
- Variables: epsilon_ijk: Levi-Civita symbol
- Use when: Building blocks of qubit Hamiltonians and observables.
- Quantum link: Every n-qubit Hamiltonian is a sum of Pauli strings.
- Backend support: **direct**
- Job hint: `{"algorithm": "ising_trotter", "num_qubits": 20, "steps": 3, "j": 1.0, "h": 0.5, "dt": 0.2, "shots": 2000}`
- Caveat: Pauli strings grow as 4^n; useful Hamiltonians are sparse in this basis.

### 16. Rotation gates (`rotation_gates`)
- Equation: $R_{\hat n}(\theta)=e^{-i\theta\,\hat n\cdot\vec\sigma/2}=\cos\tfrac\theta2\,I-i\sin\tfrac\theta2\,\hat n\cdot\vec\sigma$  
- Plain: `R_n(theta) = cos(theta/2) I - i sin(theta/2) (n . sigma)`
- Variables: n: unit axis; theta: angle
- Use when: Parametrized gates in variational circuits.
- Quantum link: RZZ(theta) = exp(-i theta ZZ/2) is the entangling rotation used in the QAOA and Ising circuits.
- Backend support: **direct**
- Job hint: `{"algorithm": "qaoa_maxcut", "num_qubits": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0], [0, 3]], "shots": 2000}`
- Caveat: Physical devices implement these by compiling to native gates, adding depth.

### 17. Hadamard gate (`hadamard_gate`)
- Equation: $H=\tfrac1{\sqrt2}\begin{pmatrix}1&1\\1&-1\end{pmatrix},\ H|0\rangle=|+\rangle$  
- Plain: `H = (1/sqrt2) [[1,1],[1,-1]]`
- Variables: |+> = (|0>+|1>)/sqrt2
- Use when: Creating equal superpositions; the first layer of QAOA.
- Quantum link: Maps Z-basis to X-basis and back.
- Backend support: **direct**
- Job hint: `{"algorithm": "ghz", "num_qubits": 2, "shots": 2000}`
- Caveat: Alone it creates no entanglement.

### 18. Bell state (`bell_state`)
- Equation: $|\Phi^+\rangle=\tfrac{1}{\sqrt2}(|00\rangle+|11\rangle)$  
- Plain: `(|00> + |11>)/sqrt2`
- Use when: Minimal maximally entangled pair; teleportation, Bell tests.
- Quantum link: Prepared by H then CNOT. In the backend this is the ghz algorithm with num_qubits=2.
- Backend support: **direct**
- Job hint: `{"algorithm": "ghz", "num_qubits": 2, "shots": 2000}`
- Caveat: Ideal outcomes are only 00 and 11; any 01/10 counts measure noise.

### 19. GHZ state (`ghz_state`)
- Equation: $|\mathrm{GHZ}_n\rangle=\tfrac1{\sqrt2}(|0\rangle^{\otimes n}+|1\rangle^{\otimes n})$  
- Plain: `(|00...0> + |11...1>)/sqrt2`
- Variables: n: number of qubits
- Use when: Benchmarking multi-qubit entanglement and device noise.
- Quantum link: Log-depth doubling circuits keep 100-qubit GHZ shallow enough to run on heavy-hex devices.
- Backend support: **direct**
- Job hint: `{"algorithm": "ghz", "num_qubits": 100, "shots": 2000}`
- Caveat: Population in the two ideal outcomes is a noise proxy, not full fidelity. Expect it to fall as n grows on real hardware.

### 20. Density matrix (`density_matrix`)
- Equation: $\rho=\sum_i p_i|\psi_i\rangle\langle\psi_i|,\ \mathrm{Tr}\rho=1,\ \rho\ge0,\ \mathrm{Tr}\rho^2\le1$  
- Plain: `rho = sum p_i |psi_i><psi_i|`
- Variables: p_i: classical probabilities
- Use when: Describing noisy or partially known states and subsystems.
- Quantum link: Noise turns pure circuit output states into mixed ones.
- Backend support: **none**
- Caveat: Needs 4^n numbers for n qubits, so full tomography is infeasible beyond a few qubits.

### 21. Partial trace (`partial_trace`)
- Equation: $\rho_A=\mathrm{Tr}_B\,\rho_{AB}$  
- Plain: `rho_A = Tr_B(rho_AB)`
- Variables: A, B: subsystems
- Use when: State of one part of an entangled system.
- Quantum link: A pure entangled global state gives a mixed reduced state (see von_neumann_entropy).
- Backend support: **none**
- Caveat: Discards information about B permanently.

### 22. Von Neumann entropy (`von_neumann_entropy`)
- Equation: $S(\rho)=-\mathrm{Tr}(\rho\log\rho)=-\sum_i\lambda_i\log\lambda_i$  
- Plain: `S = -sum lambda_i log lambda_i`
- Variables: lambda_i: eigenvalues of rho
- Use when: Measuring mixedness and entanglement (S of a subsystem of a pure state).
- Quantum link: Bell state subsystem has S = ln 2 (1 bit).
- Backend support: **none**
- Caveat: Needs the full density matrix; not directly measurable from counts for many qubits.

### 23. State fidelity (`fidelity`)
- Equation: $F(\rho,\sigma)=\left(\mathrm{Tr}\sqrt{\sqrt\rho\,\sigma\sqrt\rho}\right)^2,\ \ F=|\langle\psi|\phi\rangle|^2\ \text{(pure)}$  
- Plain: `F = |<psi|phi>|^2 for pure states`
- Variables: rho, sigma: density matrices
- Use when: How close a noisy output is to the ideal state.
- Quantum link: The GHZ population check lower-bounds the diagonal part only.
- Backend support: **partial**
- Job hint: `{"algorithm": "ghz", "num_qubits": 10, "shots": 2000}`
- Caveat: Full fidelity needs coherences (parity oscillations), which the backend does not measure.

### 24. CHSH inequality (`chsh_inequality`)
- Equation: $S=E(a,b)-E(a,b')+E(a',b)+E(a',b'),\ |S|\le2\ (\text{local}),\ |S|\le2\sqrt2\ (\text{quantum})$  
- Plain: `|S| <= 2 classically; quantum max 2*sqrt(2)`
- Variables: E: correlator of outcomes
- Use when: Certifying that correlations cannot be explained by local hidden variables.
- Quantum link: Run on a Bell pair with rotated measurement bases.
- Backend support: **none**
- Caveat: Needs measurement in rotated bases; the backend measures Z only.

### 25. No-cloning theorem (`no_cloning`)
- Equation: $\nexists\,U:\ U|\psi\rangle|0\rangle=|\psi\rangle|\psi\rangle\ \ \forall\psi$  
- Plain: `No unitary copies an arbitrary unknown quantum state`
- Use when: Reasoning about quantum cryptography and why quantum data cannot be backed up by copying.
- Quantum link: Makes quantum key distribution secure in principle.
- Backend support: **none**
- Caveat: Known states can be re-prepared; only unknown states cannot be copied.


## Quantum Algorithms

### 26. Quantum Fourier transform (`qft`)
- Equation: $\mathrm{QFT}|j\rangle=\tfrac1{\sqrt N}\sum_{k=0}^{N-1}e^{2\pi i jk/N}|k\rangle$  
- Plain: `QFT|j> = (1/sqrt(N)) sum_k exp(2 pi i j k / N)|k>`
- Variables: N = 2^n
- Use when: Period finding and phase estimation subroutine.
- Quantum link: Circuit size O(n^2) gates for n qubits.
- Backend support: **none**
- Caveat: Too deep for today's noisy devices at useful sizes.

### 27. Grover search (`grover`)
- Equation: $\#\text{iterations}\approx\tfrac\pi4\sqrt{N/M}$  
- Plain: `iterations ~ (pi/4) * sqrt(N/M)`
- Variables: N: search space size; M: number of solutions
- Use when: Unstructured search; quadratic speedup over classical.
- Quantum link: Optimal iteration count; overshooting reduces success probability.
- Backend support: **none**
- Caveat: Quadratic (not exponential) speedup; needs fault tolerance to beat classical at scale.

### 28. Quantum phase estimation (`phase_estimation`)
- Equation: $U|u\rangle=e^{2\pi i\varphi}|u\rangle;\ t=n+\lceil\log_2(2+\tfrac1{2\epsilon})\rceil\ \text{ancillas for } n \text{ bits, success } 1-\epsilon$  
- Plain: `t = n + ceil(log2(2 + 1/(2*eps))) ancilla qubits`
- Variables: phi: eigenphase; n: bits of precision
- Use when: Eigenvalue extraction; core of Shor and quantum chemistry.
- Quantum link: Precision doubles with each added ancilla but costs exponentially more controlled-U applications.
- Backend support: **none**
- Caveat: Requires long coherent circuits; not feasible on current noisy hardware at useful precision.

### 29. Variational principle (VQE) (`vqe_variational`)
- Equation: $E_0\le\frac{\langle\psi(\theta)|H|\psi(\theta)\rangle}{\langle\psi(\theta)|\psi(\theta)\rangle}$  
- Plain: `E_0 <= <psi(theta)|H|psi(theta)>`
- Variables: theta: ansatz parameters
- Use when: Estimating ground-state energies by classical optimization of a quantum circuit.
- Quantum link: Every measured energy is an upper bound, so lower is better.
- Backend support: **none**
- Caveat: Shot noise and hardware errors can push a measured energy below the true E0 even though the physical bound holds, so check variance. Optimizers can stall in flat landscapes.

### 30. Parameter-shift rule (`parameter_shift`)
- Equation: $\frac{\partial\langle C\rangle}{\partial\theta}=\tfrac12\left[\langle C\rangle_{\theta+\pi/2}-\langle C\rangle_{\theta-\pi/2}\right]$  
- Plain: `dC/dtheta = 0.5 * (C(theta+pi/2) - C(theta-pi/2))`
- Variables: C: cost expectation; theta: gate angle (Pauli-generated)
- Use when: Exact gradients of variational circuits using two circuit runs per parameter.
- Quantum link: Lets gradient descent run on hardware.
- Backend support: **none**
- Caveat: Costs 2 circuit evaluations per parameter, each with shot noise.

### 31. QAOA ansatz (`qaoa_ansatz`)
- Equation: $|\gamma,\beta\rangle=\prod_{k=1}^{p}e^{-i\beta_kB}e^{-i\gamma_kC}|+\rangle^{\otimes n},\ B=\sum_iX_i$  
- Plain: `|gamma,beta> = prod_k exp(-i beta_k B) exp(-i gamma_k C) |+>^n`
- Variables: p: layers; C: cost Hamiltonian; B: mixer
- Use when: Approximate combinatorial optimization.
- Quantum link: Backend: algorithm qaoa_maxcut, layers 1-3, angles auto-tuned on the simulator up to 16 qubits.
- Backend support: **direct**
- Job hint: `{"algorithm": "qaoa_maxcut", "num_qubits": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0], [0, 3]], "shots": 2000}`
- Caveat: No proven advantage over best classical heuristics at current sizes; always compare with the classical baseline fields.

### 32. MaxCut cost Hamiltonian (`maxcut_hamiltonian`)
- Equation: $C=\tfrac12\sum_{(i,j)\in E}(1-Z_iZ_j)$  
- Plain: `C = 0.5 * sum_edges (1 - Z_i Z_j)`
- Variables: E: graph edges
- Use when: Encoding graph partitioning: each cut edge contributes 1.
- Quantum link: Expectation <C> is computed from counts as the mean cut value.
- Backend support: **direct**
- Job hint: `{"algorithm": "qaoa_maxcut", "num_qubits": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0], [0, 3]], "shots": 2000}`
- Caveat: Backend supports unweighted edges only; weighted graphs need a future extension.

### 33. Trotter-Suzuki product formula (`trotter_suzuki`)
- Equation: $e^{-i(A+B)t}\approx\left(e^{-iAt/r}e^{-iBt/r}\right)^r,\ \text{error }O(t^2/r)$  
- Plain: `exp(-i(A+B)t) ~ (exp(-iAt/r) exp(-iBt/r))^r`
- Variables: r: Trotter steps
- Use when: Simulating dynamics of Hamiltonians made of non-commuting terms.
- Quantum link: Backend: ising_trotter with steps 1-20; error shrinks with smaller dt and more steps but depth grows.
- Backend support: **direct**
- Job hint: `{"algorithm": "ising_trotter", "num_qubits": 20, "steps": 3, "j": 1.0, "h": 0.5, "dt": 0.2, "shots": 2000}`
- Caveat: More steps reduce Trotter error but add noise; there is a sweet spot on hardware.

### 34. Quantum kernel (`quantum_kernel`)
- Equation: $k(x,x')=|\langle\phi(x)|\phi(x')\rangle|^2$  
- Plain: `k(x,x') = |<phi(x)|phi(x')>|^2`
- Variables: phi(x): feature-map state
- Use when: Machine-learning classification with a quantum feature map.
- Quantum link: Kernel entries estimated from overlap circuits.
- Backend support: **none**
- Caveat: Exponential concentration can make kernels useless at large qubit counts; advantage unproven for practical data.


## Statistical Physics

### 35. Classical Ising model (`ising_classical`)
- Equation: $H=-J\sum_{\langle i,j\rangle}s_is_j-h\sum_is_i,\ s_i=\pm1$  
- Plain: `H = -J sum s_i s_j - h sum s_i`
- Variables: J: coupling; h: field; s: spins
- Use when: Magnets, phase transitions, and as the target form of many optimization problems.
- Quantum link: MaxCut and QUBO problems map onto Ising Hamiltonians.
- Backend support: **partial**
- Job hint: `{"algorithm": "qaoa_maxcut", "num_qubits": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0], [0, 3]], "shots": 2000}`
- Caveat: Finding the exact ground state is NP-hard for general graphs.

### 36. Transverse-field Ising model (`tfim`)
- Equation: $H=-J\sum_iZ_iZ_{i+1}-h\sum_iX_i$  
- Plain: `H = -J sum Z_i Z_{i+1} - h sum X_i`
- Variables: J: coupling; h: transverse field
- Use when: Quantum phase transitions, quench dynamics, benchmark for quantum simulators.
- Quantum link: Backend: ising_trotter simulates this chain from |0...0> and reports magnetization and nearest-neighbor ZZ.
- Backend support: **direct**
- Job hint: `{"algorithm": "ising_trotter", "num_qubits": 20, "steps": 3, "j": 1.0, "h": 0.5, "dt": 0.2, "shots": 2000}`
- Caveat: Backend covers the 1D chain with first-order Trotterization only.

### 37. Boltzmann distribution and partition function (`boltzmann_partition`)
- Equation: $p_i=\frac{e^{-E_i/k_BT}}{Z},\ Z=\sum_ie^{-E_i/k_BT},\ F=-k_BT\ln Z$  
- Plain: `p_i = exp(-E_i/kT)/Z; F = -kT ln Z`
- Variables: T: temperature; k_B: Boltzmann constant
- Use when: Thermal equilibrium probabilities and free energy.
- Quantum link: Sampling thermal states is a candidate use for quantum samplers.
- Backend support: **none**
- Caveat: Z is a sum over exponentially many states; exact evaluation is infeasible for large systems.

### 38. QUBO to Ising mapping (`qubo_ising_mapping`)
- Equation: $\min_{x\in\{0,1\}^n}x^TQx\ \Leftrightarrow\ x_i=\tfrac{1-z_i}{2},\ z_i=\pm1$  
- Plain: `x_i = (1 - z_i)/2 turns QUBO into an Ising Hamiltonian`
- Variables: Q: cost matrix
- Use when: Converting scheduling, routing and portfolio problems into a form QAOA can take.
- Quantum link: Step needed before any optimization problem becomes a circuit.
- Backend support: **partial**
- Job hint: `{"algorithm": "qaoa_maxcut", "num_qubits": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0], [0, 3]], "shots": 2000}`
- Caveat: Backend accepts only unweighted MaxCut edge lists; general Q needs a new algorithm.


## Probability Statistics

### 39. Bayes' theorem (`bayes`)
- Equation: $P(H|D)=\frac{P(D|H)P(H)}{P(D)}$  
- Plain: `P(H|D) = P(D|H) P(H) / P(D)`
- Variables: H: hypothesis; D: data
- Use when: Updating beliefs with evidence; diagnostics, inference.
- Quantum link: Quantum measurement results are data to update estimates of circuit parameters.
- Backend support: **none**
- Caveat: Result depends on the prior; state it explicitly.

### 40. Law of total probability (`total_probability`)
- Equation: $P(A)=\sum_iP(A|B_i)P(B_i)$  
- Plain: `P(A) = sum_i P(A|B_i) P(B_i)`
- Variables: B_i: partition of outcomes
- Use when: Marginalizing over unknown cases.
- Quantum link: Marginal distributions of qubit subsets come from summing counts over the other bits.
- Backend support: **none**
- Caveat: B_i must be mutually exclusive and exhaustive.

### 41. Expectation and variance (`expectation_variance`)
- Equation: $\mathbb E[X]=\sum_ix_ip_i,\ \mathrm{Var}X=\mathbb E[X^2]-\mathbb E[X]^2$  
- Plain: `Var X = E[X^2] - E[X]^2`
- Variables: X: random variable
- Use when: Summarizing any distribution, including measurement outcomes.
- Quantum link: Variance of a Pauli measurement is 1 - <P>^2.
- Backend support: **direct**
- Job hint: `{"algorithm": "qaoa_maxcut", "num_qubits": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0], [0, 3]], "shots": 2000}`
- Caveat: Heavy tails make sample means unreliable.

### 42. Shot noise (binomial standard error) (`shot_noise`)
- Equation: $\sigma_{\hat p}=\sqrt{\frac{p(1-p)}{N}}$  
- Plain: `sigma = sqrt(p(1-p)/N)`
- Variables: p: true probability; N: shots
- Use when: Deciding how many shots a result deserves.
- Quantum link: Estimates of any bitstring probability have this error from finite shots alone, before hardware noise.
- Backend support: **direct**
- Job hint: `{"algorithm": "ghz", "num_qubits": 10, "shots": 2000}`
- Caveat: Quadrupling shots only halves the error; hardware error often dominates anyway.

### 43. Hoeffding bound for shots (`hoeffding_shots`)
- Equation: $P(|\hat p-p|\ge\epsilon)\le2e^{-2N\epsilon^2}\ \Rightarrow\ N\ge\frac{\ln(2/\delta)}{2\epsilon^2}$  
- Plain: `N >= ln(2/delta) / (2 eps^2)`
- Variables: eps: accuracy; delta: failure probability
- Use when: Choosing shots to guarantee accuracy for any observable bounded in [0,1].
- Quantum link: Example: eps=0.01, delta=0.05 needs N >= 18,445 shots.
- Backend support: **direct**
- Job hint: `{"algorithm": "ghz", "num_qubits": 10, "shots": 2000}`
- Caveat: Worst-case; actual needs are smaller when p is near 0 or 1.

### 44. Central limit theorem (`central_limit`)
- Equation: $\sqrt N\,(\bar X-\mu)\xrightarrow{d}\mathcal N(0,\sigma^2)$  
- Plain: `sample mean ~ Normal(mu, sigma^2/N) for large N`
- Variables: mu, sigma: mean and standard deviation
- Use when: Putting error bars on averaged results.
- Quantum link: Justifies normal confidence intervals on mean cut value or magnetization.
- Backend support: **none**
- Caveat: Fails for heavy-tailed or strongly correlated samples.

### 45. Shannon entropy (`shannon_entropy`)
- Equation: $H(X)=-\sum_xp(x)\log_2p(x)$  
- Plain: `H = -sum p log2 p`
- Variables: p(x): outcome probabilities
- Use when: Measuring uncertainty or information content of a distribution.
- Quantum link: Entropy of measured counts shows how spread the output is: noise raises it.
- Backend support: **direct**
- Job hint: `{"algorithm": "ghz", "num_qubits": 10, "shots": 2000}`
- Caveat: Estimated entropy from few shots is biased low.

### 46. Kullback-Leibler divergence (`kl_divergence`)
- Equation: $D_{KL}(p\|q)=\sum_xp(x)\log\frac{p(x)}{q(x)}$  
- Plain: `D(p||q) = sum p log(p/q)`
- Variables: p: reference; q: model
- Use when: Comparing a measured distribution to the ideal one.
- Quantum link: Quantifies how far hardware counts are from simulator counts.
- Backend support: **direct**
- Job hint: `{"algorithm": "ghz", "num_qubits": 10, "shots": 2000}`
- Caveat: Not symmetric and infinite if q(x)=0 where p(x)>0; smooth counts first.

### 47. Mutual information (`mutual_information`)
- Equation: $I(X;Y)=\sum_{x,y}p(x,y)\log\frac{p(x,y)}{p(x)p(y)}$  
- Plain: `I = sum p(x,y) log(p(x,y)/(p(x)p(y)))`
- Variables: X, Y: variables or qubit subsets
- Use when: Detecting correlations between variables, including between measured qubits.
- Quantum link: In GHZ counts every qubit pair has 1 bit of mutual information.
- Backend support: **direct**
- Job hint: `{"algorithm": "ghz", "num_qubits": 10, "shots": 2000}`
- Caveat: Detects any dependence but not its cause.

### 48. Maximum likelihood estimation (`mle`)
- Equation: $\hat\theta=\arg\max_\theta\sum_i\log p(x_i|\theta)$  
- Plain: `theta_hat = argmax sum log p(x_i | theta)`
- Variables: theta: parameters; x_i: observations
- Use when: Fitting model parameters (for example noise rates) to observed counts.
- Quantum link: Used to fit error rates from calibration circuits.
- Backend support: **none**
- Caveat: Overfits small samples; check with held-out data.


## Hardware Noise

### 49. Circuit fidelity estimate (`circuit_fidelity_estimate`)
- Equation: $F\approx\prod_g(1-\epsilon_g)\approx e^{-\sum_g\epsilon_g}$  
- Plain: `F ~ prod(1 - eps_g)`
- Variables: eps_g: error rate of gate g
- Use when: Judging up front whether a circuit is worth running.
- Quantum link: With two-qubit error ~0.5% and 600 gates, F ~ 5%: this is why the backend warns above 500 two-qubit gates.
- Backend support: **direct**
- Job hint: `{"algorithm": "ghz", "num_qubits": 100, "shots": 2000}`
- Caveat: Rough, assumes independent errors; ignores correlated noise and readout error.

### 50. Qubit decoherence (T1, T2) (`decoherence_t1_t2`)
- Equation: $P_1(t)=P_1(0)e^{-t/T_1},\quad |\rho_{01}(t)|=|\rho_{01}(0)|e^{-t/T_2}$  
- Plain: `population decays exp(-t/T1); coherence decays exp(-t/T2)`
- Variables: T1: relaxation time; T2: dephasing time (T2 <= 2*T1)
- Use when: Bounding how long a circuit can run before information is lost.
- Quantum link: Total circuit duration should be much less than T2; shallow circuits are essential.
- Backend support: **direct**
- Job hint: `{"algorithm": "ghz", "num_qubits": 100, "shots": 2000}`
- Caveat: Typical T1/T2 vary by qubit and day; read them from the backend properties.

### 51. Readout error mitigation (`readout_mitigation`)
- Equation: $\vec p_{obs}=M\,\vec p_{ideal}\ \Rightarrow\ \vec p_{mit}=M^{-1}\vec p_{obs}$  
- Plain: `p_mit = inverse(M) p_obs`
- Variables: M: calibration (confusion) matrix
- Use when: Correcting measurement bit-flip errors in counts.
- Quantum link: Cheap for few qubits; use per-qubit (tensored) calibration for many qubits.
- Backend support: **none**
- Caveat: Inversion can give negative probabilities; project back to a valid distribution.


## Probability Statistics

### 52. Markov chain stationary distribution (`markov_stationary`)
- Equation: $\pi P=\pi,\ \sum_i\pi_i=1$  
- Plain: `pi P = pi`
- Variables: P: transition matrix; pi: stationary distribution
- Use when: Long-run behavior of random processes: queues, weather, PageRank.
- Quantum link: Quantum walks offer quadratic speedups in hitting times for some graphs.
- Backend support: **none**
- Caveat: Exists uniquely only for irreducible chains.


## Applied Science

### 53. Leaky integrate-and-fire neuron (`lif_neuron`)
- Equation: $\tau_m\frac{dV}{dt}=-(V-V_{rest})+RI(t),\ \text{spike and reset if }V\ge V_{th}$  
- Plain: `tau dV/dt = -(V - V_rest) + R I(t)`
- Variables: V: membrane potential; tau_m: time constant; R: resistance; I: input current
- Use when: Simplest spiking model for neuroscience simulation.
- Quantum link: Network connectivity patterns can be partitioned with graph methods (qaoa_maxcut).
- Backend support: **partial**
- Job hint: `{"algorithm": "qaoa_maxcut", "num_qubits": 6, "edges": [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 0], [0, 3]], "shots": 2000}`
- Caveat: No ion-channel detail; quantum computing has no established advantage for neural simulation.

### 54. Hopfield network energy (`hopfield_energy`)
- Equation: $E=-\tfrac12\sum_{i\ne j}w_{ij}s_is_j-\sum_i\theta_is_i$  
- Plain: `E = -0.5 sum w_ij s_i s_j - sum theta_i s_i`
- Variables: w: symmetric weights; s=+/-1: neuron states
- Use when: Associative memory; minima are stored patterns.
- Quantum link: Same form as the Ising Hamiltonian, so ground-state search maps to quantum optimization.
- Backend support: **none**
- Caveat: Weighted couplings are not supported by the backend yet; uniform-weight cases reduce to MaxCut.

### 55. Tsiolkovsky rocket equation (`tsiolkovsky`)
- Equation: $\Delta v=v_e\ln\frac{m_0}{m_f}$  
- Plain: `delta_v = v_e * ln(m0/mf)`
- Variables: v_e: exhaust velocity; m0, mf: initial and final mass
- Use when: Propellant budgeting for any rocket stage.
- Quantum link: Classical equation; quantum methods enter only in optimization around it (staging, trajectories).
- Backend support: **none**
- Caveat: Ignores gravity and drag losses.

### 56. Lift equation (`lift_equation`)
- Equation: $L=\tfrac12\rho v^2SC_L$  
- Plain: `L = 0.5 * rho * v^2 * S * C_L`
- Variables: rho: air density; v: airspeed; S: wing area; C_L: lift coefficient
- Use when: First-pass aircraft sizing and performance.
- Quantum link: Classical; relevant to quantum only via combinatorial design optimization.
- Backend support: **none**
- Caveat: C_L varies with angle of attack and Reynolds number.

### 57. Markowitz mean-variance portfolio (`markowitz`)
- Equation: $\min_w\ w^T\Sigma w-\lambda\,\mu^Tw\ \ \text{s.t.}\ \textstyle\sum w_i=1$  
- Plain: `minimize risk (w' Sigma w) - lambda * return (mu' w)`
- Variables: w: weights; Sigma: covariance; mu: expected returns
- Use when: Allocation under risk-return tradeoff.
- Quantum link: Discrete asset selection becomes a QUBO (see qubo_ising_mapping).
- Backend support: **none**
- Caveat: Estimates of mu and Sigma are noisy; this is research, not financial advice, and the backend has no portfolio algorithm.

### 58. Kelly criterion (`kelly`)
- Equation: $f^*=\frac{bp-q}{b},\ q=1-p$  
- Plain: `f* = (b p - q) / b`
- Variables: p: win probability; b: net odds; q: loss probability
- Use when: Sizing repeated bets to maximize long-run growth.
- Quantum link: Probability estimates could come from quantum samplers, but the sizing rule is classical.
- Backend support: **none**
- Caveat: Highly sensitive to the estimated p; practitioners use a fraction of Kelly. Not financial advice.
