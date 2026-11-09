# STEM Racing car: progress

Our team is building, part by part, a computer system that designs the fastest legal car for the STEM Racing 20 m race. This page shows how far each part has come. It holds **no code and no design data**, only progress.

## Status

[![overall](board/badge-overall.svg)](https://shawshanker18.github.io/stem-racing-progress/progress.html) [![tests passed](board/badge-tests.svg)](https://shawshanker18.github.io/stem-racing-progress/progress.html) [![parts signed off](board/badge-parts.svg)](https://shawshanker18.github.io/stem-racing-progress/progress.html) [![updated](board/badge-updated.svg)](https://shawshanker18.github.io/stem-racing-progress/history.html)

[![timelines](board/timeline.svg)](#the-five-parts)

[![progress map](board/progress.svg)](https://shawshanker18.github.io/stem-racing-progress/progress.html)

**[Live panel: what each part is doing and what is running now](https://shawshanker18.github.io/stem-racing-progress/live.html)** · [Full progress, part by part](https://shawshanker18.github.io/stem-racing-progress/progress.html) · [Progress history](https://shawshanker18.github.io/stem-racing-progress/history.html)

<sub>Each square is one piece of work or one test case, counted from each part's progress file. "Groundwork" is work finished before this phase. Each part's builder updates its own file after every step.</sub>

## Ready to start?

- **Part 3 (The compass):** ✅ **Ready to start.**
- **Part 5 (The loop):** ⏳ Not yet. Waiting for D (Full-car building finished and tested, Part 4).

| Milestone | From | Done |
|---|---|---|
| A: Cutting tool finished and tested | Part 1 | ✅ 2026-11-09 |
| B: Timing noise measured (helps Part 3, not required) | Part 2 | ✅ 2026-11-09 |
| C: Compare-two-cars finished and tested | Part 2 | ✅ 2026-11-09 |
| D: Full-car building finished and tested | Part 4 | ⬜ not yet |

## The five parts

### 1. The cutter

*Carves the car body out of the legal block, one safe cut at a time.* 35.1% · being built

- Starts from the full block of material the rules allow, with every rule zone already marked.
- Moves the surface in or out wherever it is told, in small steps, and checks every rule after each step: required solid areas, required open areas, left-right symmetry, one single piece, and a shape a real milling machine can cut.
- Re-sizes the whole body after each cut so the car always weighs the target.
- Hands over a clean, closed 3D shape. It never decides what is faster; it only cuts safely.

**Now:** Fixing the last rule-zone edges (block slot, halo views) and checking the reference cars; big test waits for a frozen version.

**Timeline:** 2 of 9 steps done

| # | Step | Status | Started | Finished | Note |
|---|---|---|---|---|---|
| 1 | Fix the last failing test | ✅ Done | 2026-11-09 | 2026-11-09 | Both failing tests fixed; every check passes. |
| 2 | Build the cutting tool | ✅ Done | 2026-11-09 | 2026-11-09 | Built and all its checks pass; other parts can now use it. |
| 3 | Weight sizing for carved shapes | ❌ Failed, being redone | 2026-11-09 |  | Two hundred bodies: one hundred ninety nine on target, one came out light and under the floor. Open failure, being fixed. |
| 4 | Big random carving test (2,000 bodies) | ⏸️ Blocked | 2026-11-09 |  | Paused: Part 4 found problems on its reference cars; restarts on a frozen, tagged version once they are fixed. |
| 5 | Grid-size check | 🔄 Working on it | 2026-11-09 |  | Milling fix brought the spread down; exact rule zones written; retesting against the original bar. |
| 6 | Same result on every machine | 🔄 Working on it | 2026-11-09 |  | First try: all ten bodies identical on both runs. Final proof to be rerun across two accounts on the final code. |
| 7 | Write-up | ⬜ To do |  |  |  |
| 8 | Full clean rerun of every test | ⬜ To do |  |  |  |
| 9 | Team sign-off | ⬜ To do |  |  |  |

### 2. The stopwatch

*Times a finished car over the 20 m race.* 53.2% · being built

- An airflow simulation measures how hard the air pushes back on the car and its wheels.
- A race model turns that push, the weight and the launch into a race time, and says which inputs matter most.
- It must be right (checked against published wind-tunnel results), quiet (a tiny change gives a tiny time change) and give the same answer on every machine.
- Every other part trusts it to say which car is faster.

**Now:** Reusing one mesh shape for all near-identical cars halves the timing noise. What is left is the airflow settling into one of two patterns; testing warm starts and time-accurate runs.

**Timeline:** 0 of 10 steps done

| # | Step | Status | Started | Finished | Note |
|---|---|---|---|---|---|
| 1 | Check against published wind-tunnel results | 🔄 Working on it | 2026-11-09 |  | Drag reads too high so far; testing settings to find out why. |
| 2 | Cut the timing noise | 🔄 Working on it | 2026-11-09 |  | Re-measured without the early stop: far above target. Cars jump between three drag levels; testing whether the mesh or the airflow causes it. |
| 3 | Quick vs detailed ranking check | 🔄 Working on it | 2026-11-09 |  | Twenty cars on the detailed mesh are running; the quick-mesh twins follow. |
| 4 | Warm start | ⬜ To do |  |  |  |
| 5 | Runs longer than one machine slot | ⬜ To do |  |  |  |
| 6 | Real race inputs from the team | 🔄 Working on it | 2026-11-09 |  | Partly done: the team's measured thrust is in. Rolling friction, wheel weights and tether drag are still to come. |
| 7 | Model vs real track times | ⬜ To do |  |  |  |
| 8 | Write-up | ⬜ To do |  |  |  |
| 9 | Full clean rerun of every test | ⬜ To do |  |  |  |
| 10 | Team sign-off | ⬜ To do |  |  |  |

### 3. The compass

*Draws a map over the car showing where a cut would make it faster.* 44.4% · being built

- Looks at one car and draws a map over its whole surface: where pushing the surface in or out would make the race time faster or slower.
- One special simulation gives the whole map for about the cost of one normal run.
- The cutter carves along this map, so the map must be proven against real measurements before anyone trusts it.
- If the fast map cannot be made right, a slower map built from direct measurements is the backup.

**Now:** Wing test: map right direction but poor size match on every setting and on a finer mesh; testing the shipped full setup at its design speed and a backup measured map.

**Timeline:** 0 of 9 steps done

| # | Step | Status | Started | Finished | Note |
|---|---|---|---|---|---|
| 1 | Known-answer test | 🔄 Working on it | 2026-11-09 |  | Direction fixed and proven on all twenty bumps with fully settled runs; the strength of the map still matches only loosely, now testing why. |
| 2 | Compass test on the car | ⏸️ Blocked |  |  | Blocked: waiting on Part 2 to find why near-identical cars settle on different drag levels; measured car slopes cannot be trusted until then. |
| 3 | Fixes, tried in order | ⬜ To do |  |  |  |
| 4 | Backup measured map (only if needed) | 🔄 Working on it | 2026-11-09 |  | Trial run on the simple wing so it is proven before it might be needed. |
| 5 | Map to race time | 🔄 Working on it | 2026-11-09 |  | Built and its check against the race model passes, including where the weight sits; waiting for Part 1 to confirm how it re-sizes the skin. |
| 6 | One-cut proof | ⬜ To do |  |  |  |
| 7 | Write-up | ⬜ To do |  |  |  |
| 8 | Full clean rerun of every test | ⬜ To do |  |  |  |
| 9 | Team sign-off | ⬜ To do |  |  |  |

### 4. Parts and the referee

*Turns a carved body into a whole car, makes the build files, and judges it.* 28.4% · being built

- Adds everything except the body: nose, front and rear wings, wheel supports, wheels, tether guides and the cartridge, and cuts the joints into the body.
- Makes the files the team needs to print the parts and mill the body.
- Holds the referee: an independent check of the finished car against every rule, measured from the outside like a scrutineer, showing how much room is left on each rule.
- The referee shares nothing with the cutter, so one cannot hide the other's mistakes.

**Now:** Big batch of carved cars running; the checker measures every size rule itself now.

**Timeline:** 1 of 10 steps done

| # | Step | Status | Started | Finished | Note |
|---|---|---|---|---|---|
| 1 | List every rule and its check | ✅ Done | 2026-11-09 | 2026-11-09 | Every rule matched to a check or a reason, none left open. |
| 2 | Just-inside and just-outside tests | 🔄 Working on it | 2026-11-09 |  | First batch passed. The checker now measures the wings and wheels itself; those tests are running. |
| 3 | Make the referee independent | 🔄 Working on it | 2026-11-09 |  | The checker has its own rule numbers now; tests running. |
| 4 | Parts on carved bodies (2,000 cars) | 🔄 Working on it | 2026-11-09 |  | Trial runs on the body builder's changing code, to find crashes and new kinds of rejects; the counted run waits for its frozen version. |
| 5 | Real part weights | ⬜ To do |  |  |  |
| 6 | Build files | 🔄 Working on it | 2026-11-09 |  | A parts list now comes with every car: what to make, how, and from what. |
| 7 | Part setting ranges | ⬜ To do |  |  |  |
| 8 | Write-up | ⬜ To do |  |  |  |
| 9 | Full clean rerun of every test | ⬜ To do |  |  |  |
| 10 | Team sign-off | ⬜ To do |  |  |  |

### 5. The loop

*Runs the whole search and proves every step it keeps.* 23.1% · waiting to start

- Times the car, reads the map, tries a few cuts of different sizes, builds and judges each one, times them all, and keeps a cut only if the car is clearly faster.
- Runs many cars at once across many cloud machines, and picks up where it left off if a machine stops.
- Writes a certificate for the final car: every kept step and the proof it helped.
- In this phase it is only built and tested. The real search for the best car comes later.

**Now:** Waiting for the go to start this phase.

**Timeline:** 0 of 9 steps done

| # | Step | Status | Started | Finished | Note |
|---|---|---|---|---|---|
| 1 | Test bench with fake timings | ⬜ To do |  |  |  |
| 2 | Machine farm | ⬜ To do |  |  |  |
| 3 | Keep-rule check on real runs | ⬜ To do |  |  |  |
| 4 | Small smoke run | ⬜ To do |  |  |  |
| 5 | Final-run plan (ready, not started) | ⬜ To do |  |  |  |
| 6 | Settings searched together | ⬜ To do |  |  |  |
| 7 | Write-up | ⬜ To do |  |  |  |
| 8 | Full clean rerun of every test | ⬜ To do |  |  |  |
| 9 | Team sign-off | ⬜ To do |  |  |  |

---

*Drawn automatically from the progress files. Nothing here can be used to rebuild the work.*
