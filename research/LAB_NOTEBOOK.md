# USRT research lab notebook

This is the running record of every question, calculation, plot and conclusion in the USRT project after the audit. Entries are **appended, never rewritten**. A correction is added as a new dated note under the entry it corrects.

**Conventions**

- Each entry links the script that produced it, its text output in `results/` and its figures in `figures/`.
- Numbers are compared with measurements using their uncertainties.
- Status labels:
  - **established**: textbook or measured physics;
  - **computed here**: our own calculation;
  - **open**: not yet resolved;
  - **ruled out**: contradicted by calculation or experiment.
- To re-run everything: `python3 research/run_all.py` (a few seconds each).

| Entry | Date | Topic | Script |
|---|---|---|---|
| [E0](#e0) | 2026-10-10 | Starting point: what the audit established | `audit/` |
| [E1](#e1) | 2026-10-10 | Does the gravity "dent" create an anti-gravity high point? | r01 |
| [E2](#e2) | 2026-10-10 | Flexible superfluid instead of a crystal; can "interference" slow light? | r01 |
| [E3](#e3) | 2026-10-10 | Does more trapped energy give longer range? Extra dimensions? | r01 |
| [E4](#e4) | 2026-10-10 | Particles as trapped ripples obey relativity (sine-Gordon) | r01 |
| [E5](#e5) | 2026-10-10 | Real light from a substrate: Levin–Wen and Volovik routes | r02 |
| [E6](#e6) | 2026-10-10 | Inverse problem: what the vacuum medium must be, from its waves | r03 |
| [E7](#e7) | 2026-10-10 | Can a higher dimension explain entanglement? | r04 |
| [E8](#e8) | 2026-10-10 | Brainstorm: can the substrate fix the speed of light? | r05 |
| [E9](#e9) | 2026-10-10 | Synthesis: the current best substrate picture and open problems | — |
| [E10](#e10) | 2026-10-10 | The structure of the substrate, layer by layer (USRT v2) | r06 |

---

<a id="e0"></a>
## E0 — Starting point (2026-10-10)

The full audit is in [`audit/USRT_AUDIT_REPORT.md`](../audit/USRT_AUDIT_REPORT.md). It established:

- A Planck-scale **crystal** fails two ways:
  - light speed would depend on direction by 17–33 %;
  - its longitudinal wave is gapless (it is not "frozen out").
- The **mass formulas** are fits: electron 42σ, muon 452σ, proton ratio 5,523σ from measurement.
- **Gravity** as written is GR's metric typed in. A superfluid density dent is short-range.
- A **local** vortex picture of entanglement gives S = 2, below the measured values.

What survives:
- the vacuum as a condensed-matter medium;
- the inertia of confined energy;
- fermionic solitons;
- relational time;
- Koide's Q = 2/3 regularity.

---

<a id="e1"></a>
## E1 — Does the dent create an opposite "high point" (antigravity)? (2026-10-10)

**Question (user):** "Every action has an equal and opposite reaction, so the gravity well should also make a high point. Could that be antigravity?"

**Method:** Solved the radial Gross–Pitaevskii (superfluid) equation around a repulsive source at three strengths (0.5, 3.5, 20, in healing-length units). Searched for any density above the background.

**Result (computed here):**

| Source strength | Centre density | Maximum density anywhere | Tail |
|---|---|---|---|
| 0.5 | 0.807 | 1.000000 | e^(−1.414 r)/r |
| 3.5 | 0.191 | 1.000000 | e^(−1.414 r)/r |
| 20 | 0.000 | 1.000000 | e^(−1.414 r)/r |

The displaced amount (4.7, 28, 82 units) spreads thinly through the rest of the fluid. There is no bump anywhere.

**Interpretation:**
- **Newton's third law is already satisfied.** The reaction is the substrate pushing back on the mass, and that push is what holds the dent open. It does not create a hill elsewhere. A uniform rise in the background exerts no force, because forces come from slopes.
- **Fluids can produce repulsion in other ways** (established):
  - Bjerknes forces: pulsating bubbles attract when in phase and repel when out of phase, both as 1/r²;
  - density rings around impurities, in fluids with a roton minimum such as helium-4.

**Constraints from experiment (established):**
- all matter falls the same way to 1e-15 (MICROSCOPE);
- antimatter falls down (CERN ALPHA-g, 2023);
- gravity follows 1/r² down to about 50 μm, with no alternating rings.

Any repulsive mode therefore must not act on known matter.

**Status:** antigravity from a dent: **ruled out** in this model. Repulsion via out-of-phase pulsation: **open**, but heavily constrained.

**Files:** [`r01_dent_range_relativity.py`](r01_dent_range_relativity.py), [results](results/r01_dent_range_relativity.txt), ![dent](figures/r01_dent_range_relativity_dent_vs_source.png)

---

<a id="e2"></a>
## E2 — Flexible superfluid instead of a crystal; can interference slow light? (2026-10-10)

**Question (user):**
- "Rule out the crystal. What about uncharged Planckion-like entities in a flexible superfluid?"
- "If many ripples pile up near concentrated energy, wouldn't their interference slow light down?"

**Results (computed here):**
- **Isotropy: yes.** A fluid has no grain. With Planck-mass grains, the only speed change is that short waves go slightly faster (Bogoliubov dispersion):
  - green light: 5×10⁻⁵⁷;
  - 100 GeV gamma rays: 8×10⁻³⁶;
  - the same in every direction, far below any bound.
- **Wrong kind of wave: problem.** A superfluid carries only compression waves (one polarisation). Light is two transverse polarisations, so a plain superfluid cannot make light. Follow-up in E5.
- **Interference does not change speed.** Waves superpose linearly and pass through each other unchanged. Speed changes only if the medium itself changes. In a superfluid the wave speed rises with density (c ∝ √n), so a **thinner** region slows waves and bends them toward the mass.
- **Size of dent needed to copy GR's light bending exactly:**
  - δρ/ρ = −4GM/(rc²), falling as 1/r;
  - 8.5×10⁻⁶ at the Sun's surface;
  - 2.8×10⁻⁹ at Earth's surface.
- **The effect is real.** Radar grazing the Sun on an Earth–Mars round trip returns **247 μs** late (the Shapiro delay, measured).
- **Smooth, not random.** The slowing must be identical for all colours, because gravitational lensing is achromatic. Random interference would blur images and depend on colour.

**Prior art:** Dicke 1957 and Puthoff's "polarizable vacuum" use exactly this "vacuum slows light" idea. They pass the classic tests but predict scalar gravitational waves (see E6).

**Status:**
- isotropic fluid: **computed here, works**;
- light from a plain fluid: **ruled out**;
- slowing by the medium: **established mechanism, needs a 1/r dent**.

---

<a id="e3"></a>
## E3 — Bigger trapped energy, longer range? Spreading into extra dimensions? (2026-10-10)

**Question (user):** "The well should extend according to how much energy is trapped, and spread in all directions and dimensions."

**Results (computed here):**
- **More energy makes the dent deeper, not longer-reaching.** The tail decay rate is identical (−1.414) for all three source strengths (E1 figure, right). The range is the medium's healing length ξ = ħ/(√2 m c_s), not a property of the source.
- **Range requirement.** For the dent to reach galaxy scales, the healing length must be at least a kiloparsec, so the grain mass must be ≤ 4.5×10⁻²⁷ eV (10⁻⁵⁵ of the Planck mass). The LIGO graviton-mass bound alone requires ≤ 9×10⁻²⁴ eV. *Planck-mass grains and long-range dents contradict each other.*
- **Spreading in all directions** is Gauss's law, and it is exactly why gravity is 1/r² in 3 dimensions. In D space dimensions the force goes as 1/r^(D−1). Ehrenfest (1917) showed that stable orbits exist only for D = 3.
- **Extra dimensions** must therefore be curled up (ADD 1998; constrained to below tens of μm by Eöt-Wash) or warped so that gravity stays on our membrane (Randall–Sundrum 1999).

**Status:** "range grows with energy": **ruled out**. Long range via gapless flow (Bjerknes) or ultralight grains: **open**. Warped extra dimension: **established model, compatible**.

---

<a id="e4"></a>
## E4 — Particles as trapped ripples obey special relativity (2026-10-10)

**Question (user):** "Let's nail down the substrate and derive the speed of light."

**Method:** A discrete sine-Gordon chain (pendulums coupled by springs; the chain's wave speed is c = 1). A kink, a trapped twist, plays the particle. I measured its speed, its width and its energy, then pushed it with a constant force.

**Results (computed here):**

| Speed | Width shrink | Lorentz γ | Energy/rest energy |
|---|---|---|---|
| 0.30c | 1.048 | 1.048 | 1.048 |
| 0.60c | 1.250 | 1.250 | 1.250 |
| 0.80c | 1.667 | 1.667 | 1.667 |
| 0.90c | 2.296 | 2.294 | 2.294 |
| 0.95c | 3.226 | 3.203 | 3.201 |
| 0.99c | 6.055 | 7.089 | 7.073 |

Under a constant push the speed went 0.375 → 0.700 → 0.850 → 0.900c. Newton's prediction runs to 2.16c, relativity's to 0.907c, and the simulation matched relativity.

**Interpretation (established + computed):**
- **Relativity comes for free.** Matter made of ripples in a medium with wave speed c automatically obeys special relativity: Lorentz contraction, E = γmc², and c as an unreachable limit. Observers built from such ripples can never detect their motion through the medium. This is the Lorentz–FitzGerald / J.S. Bell picture, and it is how the substrate can "explain" c.
- **Graininess shows only at grain scale.** At 0.99c the particle is about 3 grains wide and starts to deviate (0.984c; shrink 6.06 vs 7.09). *Prediction of any grainy substrate:* relativity fails only when something is squeezed to grain size.

**Status:** **computed here, robust.** The numerical value of c is not derived (see E8).

---

<a id="e5"></a>
## E5 — Real light from a substrate: Levin–Wen and Volovik routes (2026-10-10)

**Question (user):** "Let's check Volovik's helium-3 work and Levin–Wen string-nets."

**Method:**
1. Diagonalised two simple-cubic lattices, both at small wavevector and along Γ–X–M–Γ–R:
   - an **elastic** lattice with central springs;
   - a **gauge ("twist-only")** lattice, whose energy is |curl A|².
2. Group-averaged random response tensors over the cubic (48 elements) and hexagonal (24 elements) symmetry groups.
3. Studied a Weyl point, H = c∥ p_z σ_z + c⊥(p_x σ_x + p_y σ_y), including its topological charge (Fukui–Hatsugai–Suzuki Berry flux).

**Results (computed here):**

*Elastic lattice:*
- Tuned springs (k₂ = k₁, Zener ratio 1) are isotropic, but there are still **3** waves, with the longitudinal at 1.73c.
- Generic springs give transverse speeds of 0.92–1.12c (a 21 % spread) and up to 0.21c of birefringence.

*Gauge lattice:*
- **Exactly 2** propagating waves, both at 1.00000000c in every direction.
- The third mode has zero frequency at every wavelength. It is pure gauge, and Gauss's law removes it.
- Direction dependence with Planck spacing is 1×10⁻⁵⁷ at 500 nm and 2×10⁻³⁶ at 100 GeV.

*Symmetry:*
- **Rank 2** (optics / gauge light): cubic forces exact isotropy; hexagonal gives uniaxial birefringence.
- **Rank 4** (elasticity): neither group forces isotropy. Isotropy requires tuning.

*Weyl point (Volovik):*
- A random perturbation only **moved** the massless node: the gap at the new node is 3.5×10⁻¹⁸, and the topological charge stays +1.000.
- Masslessness is protected by topology.
- An anisotropic light cone (c∥/c⊥ = 10 in the toy; about 55 m/s vs a few cm/s in ³He-A) is undetectable if **every** species shares it. A 10⁻⁶ species mismatch gives a 10⁻⁶ Michelson–Morley signal. Experiments bound such mismatches at about 10⁻¹⁷.

**Interpretation:**
- **Light should be a gauge field of the substrate, not its elastic displacement.** The gauge route automatically gives 2 polarisations and kills the longitudinal wave. On a **cubic** lattice it is also automatically isotropic. This is MacCullagh's 1839 "rotational aether", in modern form as Levin–Wen string-net condensation.
- **Particles come out as defects.** In that picture charges are string ends (violations of Gauss's law) and can be fermions, which is USRT's "particles as defects" intuition in a working form.
- **α becomes computable.** In quantum spin ice the emergent fine-structure constant is about 0.08 (Pace et al., PRL 127, 117205 (2021)).

**Status:**
- gauge-light substrate: **established mechanism, recommended direction**;
- HCP lattice: **disfavoured** (makes even gauge light birefringent unless tuned);
- universality across species: **open** (the fine-tuning problem).

**Files:** [`r02_emergent_light.py`](r02_emergent_light.py), [results](results/r02_emergent_light.txt), ![modes](figures/r02_emergent_light_elastic_vs_gauge.png) ![weyl](figures/r02_emergent_light_weyl_point.png)

---

<a id="e6"></a>
## E6 — Inverse problem: what the vacuum medium must be, from its waves (2026-10-10)

**Question (user):** "Any wave needs a medium, and its behaviour depends on the medium. Can't we calculate the medium's properties from the waves, and vice versa?"

**Answer:** Yes. This is exactly how seismology maps Earth's interior. Applied to light and gravitational waves:

| Observation | What the medium must be |
|---|---|
| c, and impedance Z₀ = 376.730 Ω | "inertia" μ₀ = Z₀/c and "stiffness" 1/ε₀ = Z₀c. In charge-independent units Z₀ = 4παħ/e², so the dimensionless stiffness is **α = 1/137.036** |
| only 2 transverse polarisations | twist-only stiffness: the wave matrix \|k\|²I − kkᵀ has eigenvalues (0, 1, 1)\|k\|². This is MacCullagh / gauge field |
| GW strain for a known flux | spacetime tension c⁴/8πG = **4.8×10⁴² N**. Check: GW150914 (3.6×10⁴⁹ W at 410 Mpc; flux 18 mW/m²) predicts h = 9.5×10⁻²²; LIGO measured about 1×10⁻²¹ ✓ |
| GW polarisation is tensor (GW170814) | a spin-2 stiffness is needed. Light repeats every 360°, gravity every 180°, and a "slowing medium" (scalar) never changes, so Dicke/Puthoff-type scalar media alone are ruled out |
| light and gravity speeds agree to 10⁻¹⁵ (GW170817) | one shared light cone |
| isotropy ~10⁻¹⁷; vacuum birefringence ≲ 10⁻³² | no preferred direction, no polarisation splitting |
| no dispersion up to 1.5×10¹⁹ GeV (order-1) / ~10¹¹ GeV (order-2) | grains < ~10⁻³⁵ m or < ~10⁻²⁷ m |
| light crosses ~10²⁶ m without loss | frictionless, superfluid-like |

**Interpretation:** Any substrate must look exactly like what physics already calls "fields in empty spacetime". It must have twist-only stiffness for light with strength α, a separate spin-2 stiffness for gravity, one universal light cone, and no detectable rest frame. That is why physics stopped talking about an aether: not because it is impossible, but because it is indistinguishable. The useful targets are therefore **α**, **why one light cone**, and **why spin-2**.

**Status:** **computed here / established.**

**Files:** [`r03_medium_from_waves.py`](r03_medium_from_waves.py), [results](results/r03_medium_from_waves.txt), ![pol](figures/r03_medium_from_waves_polarisation_patterns.png)

---

<a id="e7"></a>
## E7 — Can a higher dimension explain entanglement? (2026-10-10)

**Question (user):** "If Randall–Sundrum is real, entanglement could be the same object observed from different dimensions, which is why information *seems* faster than light."

**Results (computed here):**

- **A. "One object seen twice"** (Bohm's fish-tank analogy). A 3D object with each outcome fixed by its state plus the local setting gives S = 2.000 at the standard settings and at best over 300 random settings. *Seen-twice alone obeys Bell's limit;* experiments give 2.4–2.8.
- **B. Object reacting through the bulk at speed v**, over an 18 km baseline:
  - quantum correlations need v > 1.2×10⁴ c (5 ns simultaneity) or 1.2×10⁵ c (0.5 ns);
  - published bounds are > 10⁴ c (Salart 2008) and > 1.38×10⁴ c (Yin 2013);
  - Bancal et al. 2012: **any** finite-speed influence that reproduces quantum correlations would allow faster-than-light messages.
- **C. Is the bulk a shortcut?**
  - In RS2, where space and time share the same warp, no bulk path beats the membrane path (best ratio 1.0000).
  - An asymmetric warp (bulk speed up to 1.05c) does give a shortcut (ratio 0.962).
  - GW170817 limits any such speed-up for gravity to ~10⁻¹⁵.

**Interpretation:**
- **A bulk link can only be a nonlocal channel.** It must act effectively instantly and must never carry a message. ER = EPR's non-traversable wormholes have exactly those properties, so they are the serious version of this idea.
- **The value 2√2 is still missing.** The same cord with another rule gives 4 (audit/a03). The bulk must also explain why nature stops at 2√2 (Tsirelson's bound). Information causality (Pawłowski et al. 2009) is one candidate principle.

**Status:**
- local "seen twice": **ruled out**;
- finite-speed bulk channel: **ruled out**;
- instantaneous non-signalling bulk link: **open** (needs the 2√2 rule derived).

**Files:** [`r04_entanglement_extra_dimension.py`](r04_entanglement_extra_dimension.py), [results](results/r04_entanglement_extra_dimension.txt), ![bulk](figures/r04_entanglement_extra_dimension_bulk_channel.png)

---

<a id="e8"></a>
## E8 — Brainstorm: can the substrate fix the speed of light? (2026-10-10)

**Question (user):** "Let's brainstorm the possibilities and what we can synthesise for it."

**Results (computed here):**

- **A speed limit emerges from local coupling** (Lieb–Robinson). A particle hopping on a chain (numerics match the exact Bessel solution to 7×10⁻¹⁶) spreads inside a cone of speed 2Ja/ħ. At late times the edge moves at 2.07 and the leading peak at 1.96, and both converge to 2. Leakage beyond the cone is 3×10⁻⁹.
- **With Planck spacing:** reproducing c requires a coupling J = ħc/(2l_P) = **6.1×10¹⁸ GeV**, half the Planck energy.
- **The free knob is explicit.** The rules (i) c = 2Ja/ħ, (ii) ħ = Mac and (iii) G = c²a/M hold to rounding error for c = 1 m/s, 3×10⁸ m/s and 10¹² m/s alike. With only ħ and G as inputs, **every** c is consistent. Fixing it needs one independently measured substrate property. Since 1983 the metre has been defined from c anyway.

**Candidate routes:**

| Route | Status |
|---|---|
| c = grain spacing / grain tick | sound restatement: explains universality and the limit, not the number |
| c = Lieb–Robinson speed 2Ja/ħ | sound mechanism; needs J or a measured |
| one shared emergent light cone (Volovik) | open: why species agree to 10⁻¹⁵ |
| Lorentz invariance as a low-energy attractor (Chadha–Nielsen 1983) | partial: the flow is only logarithmic |
| supersymmetry protection (Groot Nibbelink–Pospelov 2005) | speculative |
| induced gravity (Sakharov 1967): a ~ √N l_P | testable in principle |
| measure the grain (dispersion, birefringence) | experimental; bounds a ≲ l_P (order-1) |
| derive α = 1/137 from substrate couplings | **the real prize**; possible in principle (spin ice ≈ 1/12) |

**Status:** the value of c is **not derivable** from ħ and G alone (proved). Its universality and its role as a limit **are** derivable.

**Files:** [`r05_speed_of_light.py`](r05_speed_of_light.py), [results](results/r05_speed_of_light.txt), ![lr](figures/r05_speed_of_light_lieb_robinson.png)

---

<a id="e9"></a>
## E9 — Synthesis: current best substrate picture and open problems (2026-10-10)

**A version of the idea that survives every check so far:**
1. **Substrate:** a quantum lattice of locally coupled, uncharged units. A cubic arrangement, or no fixed lattice, so that isotropy is protected (E5).
2. **The speed limit c** is the lattice's Lieb–Robinson speed, c ≈ 2Ja/ħ (E8).
3. **Light** is an emergent **gauge** field: exactly 2 polarisations, isotropic, massless by gauge symmetry (E5, E6).
4. **Matter** consists of defects and trapped ripples. They automatically obey special relativity (E4). Charges are string ends, possibly fermions (E5). Some may be Weyl points, massless by topology (E5).
5. **Gravity** has to be a separate **spin-2** collective mode sharing the same light cone (E6), with infinite range (E3).
6. **Entanglement** can only come from an instantaneous, non-signalling link (E7).

**Open problems, ranked:**
1. **Emergent spin-2 gravity.** The Weinberg–Witten theorem (1980) forbids a massless spin-2 particle that carries a Lorentz-covariant, conserved stress-energy tensor. So "graviton = ordinary emergent particle on a pre-existing flat spacetime" is blocked. Known loopholes:
   - the metric itself emerges, so spacetime is not pre-existing;
   - Lorentz symmetry is only approximate (Volovik's helium-3);
   - spacetime emerges from entanglement (holography).
2. **One light cone for every species**, to 10⁻¹⁵–10⁻¹⁷.
3. **Derive α = 1/137** (and then mass ratios) from the substrate's couplings, without fitting.
4. **Why quantum correlations stop at 2√2.**
5. **Dark energy:** Volovik's equilibrium argument removes the 10¹²⁰, but the observed value is still an input.

**Next steps (queue):**
- [ ] Classical lattice gauge simulation: show emergent Coulomb 1/r between two Gauss-law defects on a cubic lattice (light *and* a long-range force from the same medium).
- [ ] Compute the emergent α for a simple compact U(1) lattice model as a function of the coupling ratio, and see what ratio gives 1/137.
- [ ] Bjerknes test: two pulsating sources in a compressible fluid; force law and sign vs phase.
- [ ] Toy Weyl-metric "gravity": a texture in the Weyl vector bends all species' cones equally. Check against Shapiro delay scaling.
- [ ] (added 2026-10-10, from E10) Confinement threshold and photon speed for a Hamiltonian, spin-ice-type lattice model, to compare with the Wilson-action threshold α_c ≈ 0.079 used in E10.

> **Note (2026-10-10, later):** E10 gives the layered version of this picture, with parameter ranges and the new Coulomb-phase constraint α < α_c ≈ 0.079. Nothing in E9 is retracted.

---

<a id="e10"></a>
## E10 — The structure of the substrate, layer by layer (USRT v2) (2026-10-10)

**Question (user):** "So what's the structure of the substrate based on the improvements and modifications to the Universal Substrate Theory?"

**Method:** a synthesis of E1–E8, with no new assumptions. On top of that, three new calculations in `r06`:
1. the allowed range of cell size, coupling and tick;
2. whether our α puts the substrate in the phase that has photons;
3. the vacuum-energy bookkeeping.

**Result: the layers.** Each layer emerges from the one below it.

| # | Layer | Structure | Status | From |
|---|---|---|---|---|
| 0 | Units | Uncharged *quantum* units (spins or rotors, not hard balls), on a cubic lattice or no fixed lattice | open (size) | E5 |
| 1 | Couplings | Each unit talks only to its neighbours (energy J). This gives a built-in speed limit **c = 2Ja/ħ**: one cell per tick | computed here | E8 |
| 2 | Vacuum state | A frictionless condensate of closed flux loops (Levin–Wen string-net), in its **Coulomb phase**; equilibrium pressure zero (Volovik) | established + computed here | E5, r06 |
| 3 | Light | The *twist* of that condensate: exactly 2 polarisations, isotropic on a cubic lattice, massless by gauge symmetry, strength α | computed here | E5, E6 |
| 4 | Matter | Defects of the condensate: string ends = charges (can be fermions); Weyl points (massless by topology); trapped ripples (mass = confined energy, relativity automatic). **Mass values are not derived.** | computed here (mechanisms) / open (values) | E4, E5 |
| 5 | Gravity | A collective **metric** shared by every excitation: spin-2, infinite range, stiffness c⁴/8πG = 4.8×10⁴² N. *Not* a density dent | open | E3, E6 |
| 6 | Extra dimension (optional) | Curled up or warped. Entanglement needs an instant, non-signalling link (ER = EPR-like); the RS2 bulk is no shortcut | open | E3, E7 |

Time is the substrate's own ticking (relational; Page–Wootters).

**Result: numbers (computed here).**

*Cell size a, coupling J = ħc/2a, and tick a/c:*

| Case | a (m) | J (GeV) | tick (s) |
|---|---|---|---|
| Planck length | 1.6×10⁻³⁵ | 6.1×10¹⁸ | 5.4×10⁻⁴⁴ |
| induced gravity, N ≈ 100 fields | 1.6×10⁻³⁴ | 6.1×10¹⁷ | 5.4×10⁻⁴³ |
| largest allowed by order-2 dispersion data | ~2×10⁻²⁷ | 5×10¹⁰ | 6.6×10⁻³⁶ |

A gauge lattice has only even-order dispersion and no birefringence, so the data allow cells far larger than the Planck length. Gravity's strength (Sakharov) points to a few Planck lengths.

*Photon phase:*
- In the simplest lattice gauge substrate (compact U(1), Wilson action), photons exist only for β = 1/e² > 1.0111, i.e. **α < α_c = 0.0787**. Below that coupling the photon is confined and gets a gap.
- Our α(0) = 1/137.036 is **10.8× below** the threshold, and α(M_Z) = 1/127.95 is 10.1× below. So the substrate sits comfortably in the photon phase.
- Quantum spin ice's emergent α ≈ 0.08 sits right at the threshold.

*Vacuum energy:*
- Observed dark-energy density: 5.8×10⁻²⁷ kg/m³, which is 1.1×10⁻¹²³ of the Planck density.
- Volovik's equilibrium argument removes the naive 10¹²⁰ term, but the observed small value is still an input.

*Scale (fun fact):* with Planck-size cells, the observable universe holds about 2×10¹⁸⁴ of them.

**What was dropped from the original USRT:**
- Planck-mass balls joined by springs, and the close-packed HCP crystal;
- light as an elastic shear wave, and the 4.2×10¹⁹ GeV "gap";
- gravity as a density dent;
- the electron, proton and muon formulas;
- local vortex entanglement;
- c "derived" from ħ and G.

**What it still needs as measured inputs:** c (which fixes J·a), α, G, and the dark-energy density.

**Interpretation:** The revised substrate is no longer a *crystal of tiny balls*. It is a *quantum network* whose ground state is a loop condensate. Light is that condensate's twist, particles are its defects, and c is its built-in signal speed. Every layer is individually prior art: Lieb–Robinson, Levin–Wen, Volovik, Sakharov, Page–Wootters, Randall–Sundrum, ER = EPR. What would be *new* is a single model where all the layers come out together. In particular it would need to give gravity as a shared spin-2 metric and derive α = 1/137 rather than take it as input.

**Status:**
- the layered structure is consistent with every check so far;
- layers 1–3 and the matter mechanisms: **computed here / established**;
- layer 0 size, layer 5 (gravity) and layer 6 (entanglement): **open**.

**References:**
- **Lieb & Robinson**, Commun. Math. Phys. 28, 251 (1972)
- **Levin & Wen**, Rev. Mod. Phys. 77, 871 (2005)
- **Volovik**, *The Universe in a Helium Droplet* (2003)
- **Arnold, Lippert, Neuhaus & Schilling**, "Compact QED under scrutiny: it's first order", Nucl. Phys. B Proc. Suppl. 119, 864 (2003); β_c = 1.0111331
- **Pace, Morampudi, Moessner & Laumann**, PRL 127, 117205 (2021)
- **Sakharov**, Dokl. Akad. Nauk SSSR 177, 70 (1967)
- **Page & Wootters**, PRD 27, 2885 (1983)
- **Randall & Sundrum**, PRL 83, 4690 (1999)
- **Maldacena & Susskind**, arXiv:1306.0533
- **Data:** Planck 2018 (Ω_Λ = 0.6847, H₀ = 67.36); PDG 2024 (α(M_Z))

**Files:** [`r06_substrate_structure.py`](r06_substrate_structure.py), [results](results/r06_substrate_structure.txt), ![layers](figures/r06_substrate_structure_layers.png)
