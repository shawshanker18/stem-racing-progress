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

*Carves the car body out of the legal block, one safe cut at a time.* 38.9% · being built

- Starts from the full block of material the rules allow, with every rule zone already marked.
- Moves the surface in or out wherever it is told, in small steps, and checks every rule after each step: required solid areas, required open areas, left-right symmetry, one single piece, and a shape a real milling machine can cut.
- Re-sizes the whole body after each cut so the car always weighs the target.
- Hands over a clean, closed 3D shape. It never decides what is faster; it only cuts safely.

**Now:** Whole-car test (chained fine/resolved) running on main dd7427a: stem-racing-compute 43453873060; tag at once if green, then Part 3 told. Markings fix in (6d86afd). Open: Fault A 41594/8, halo-top 41518/4; 44130 claw clearance with Part 4.

**Timeline:** 3 of 9 steps done

| # | Step | Status | Started | Finished | Note |
|---|---|---|---|---|---|
| 1 | Fix the last failing test | ✅ Done | 2026-11-09 | 2026-11-09 | Both failing tests fixed; every check passes. |
| 2 | Build the cutting tool | ✅ Done | 2026-11-09 | 2026-11-09 | Built and all its checks pass; other parts can now use it. |
| 3 | Weight sizing for carved shapes | 🔄 Working on it | 2026-11-09 |  | Rerun needed on the fixed cutter; the Part 1 chat starts it. |
| 4 | Big random carving test (2,000 bodies) | ⏸️ Blocked | 2026-11-09 |  | Waits for the frozen tag: Part 4's cars pass on fef4130; own checks still running. |
| 5 | Grid-size check | 🔄 Working on it | 2026-11-09 |  | 19 of 20 bodies between 0.10 and 0.48 % after the two fixes; last body still running. |
| 6 | Same result on every machine | ✅ Done | 2026-11-09 | 2026-11-10 | Same-result test green on the current cutter. |
| 7 | Write-up | ⬜ To do |  |  |  |
| 8 | Full clean rerun of every test | ⬜ To do |  |  |  |
| 9 | Team sign-off | ⬜ To do |  |  |  |

### 2. The stopwatch

*Times a finished car over the 20 m race.* 78.2% · being built

- An airflow simulation measures how hard the air pushes back on the car and its wheels.
- A race model turns that push, the weight and the launch into a race time, and says which inputs matter most.
- It must be right (checked against published wind-tunnel results), quiet (a tiny change gives a tiny time change) and give the same answer on every machine.
- Every other part trusts it to say which car is faster.

**Now:** Medium-plus stopped (user: high mesh). Fine mesh skewed face found: one face on the machined body (not a wing or wheel), 1 of 13.3 million. Gate: the two long chained cars are still on their first link. Next: re-measure noise and repeat on the fine mesh, since the search now runs on fine.

**Timeline:** 3 of 10 steps done

| # | Step | Status | Started | Finished | Note |
|---|---|---|---|---|---|
| 1 | Check against published wind-tunnel results | 🔄 Working on it | 2026-11-09 |  | Bias measured: drag reads about 5 to 13 % high on the standard test body (central +9 %). Asked whether to carry a correction of 1/1.09 plus or minus 0.04 in the race model (question Q11). |
| 2 | Cut the timing noise | ✅ Done | 2026-11-09 | 2026-11-13 | Done: 0.09 ms against 0.3 ms (each car timed from both airflow states, confirmed on fresh machines). Same car on nine machines agrees to 0.01 ms. |
| 3 | Quick vs detailed ranking check | ✅ Done | 2026-11-09 | 2026-11-10 | Passed: the quick mesh orders twenty cars the same way as the detailed mesh, well above the pass marks. |
| 4 | Warm start | ⬜ To do |  |  |  |
| 5 | Runs longer than one machine slot | ✅ Done | 2026-11-13 | 2026-11-13 | Done: a long solve stops before the 6 h limit, saves, and the next job continues; chained and unbroken agree to 0.002 ms. The whole-car test run now uses it. |
| 6 | Real race inputs from the team | 🔄 Working on it | 2026-11-09 |  | Measured thrust in and checked (peak, timing and total push match). New slopes: 0.2 ms per mN of drag, 7.5 ms per gram. Rolling friction, wheel spin, tether drag and real weights still to come from the team. |
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

**Now:** Compass METHOD test (not car results): 45 carved cars on the medium mesh, none judged yet. Fine-mesh check (Q11): 2 cars (3.95 and 3.90 mm) chained across jobs on Jdiejei, 12 modes each, to compare directions with their medium maps. No loop step is kept unless confirmed on fine.

**Timeline:** 0 of 9 steps done

| # | Step | Status | Started | Finished | Note |
|---|---|---|---|---|---|
| 1 | Known-answer test | ❌ Failed, being redone | 2026-11-09 | 2026-11-13 | Fast map fails on every setting tried, including the maker's own full setup; the measured map passes. Decided 2026-11-13: fast map dropped, the measured map is the compass. |
| 2 | Compass test on the car | 🔄 Working on it | 2026-11-11 |  | Running on 45 carved cars (2 cores), a few moved at a time between accounts: the measured map is built from small bumps, then checked against 40 random cuts per car. No car judged yet. Pass: direction right on 8 of 10 cuts that clearly change the time, and a close match overall. |
| 3 | Fixes, tried in order | ❌ Failed, being redone | 2026-11-09 | 2026-11-13 | Stopped: no setting of the fast map passed the known-answer test, so it is no longer tuned. |
| 4 | Measured map (now the compass) | 🔄 Working on it | 2026-11-09 |  | Passed on the simple wing: matched every test shape it had not seen. Now the compass for every car: 54 timing jobs per car (start car, 60 bumps, 40 cuts), run on Part 3's accounts at the slow pace. |
| 5 | Map to race time | 🔄 Working on it | 2026-11-09 |  | Built and its check against the race model passes, including where the weight sits; waiting for Part 1 to confirm how it re-sizes the skin. |
| 6 | One-cut proof | ⬜ To do |  |  |  |
| 7 | Write-up | ⬜ To do |  |  |  |
| 8 | Full clean rerun of every test | ⬜ To do |  |  |  |
| 9 | Team sign-off | ⬜ To do |  |  |  |

### 4. Parts and the referee

*Turns a carved body into a whole car, makes the build files, and judges it.* 33.1% · being built

- Adds everything except the body: nose, front and rear wings, wheel supports, wheels, tether guides and the cartridge, and cuts the joints into the body.
- Makes the files the team needs to print the parts and mill the body.
- Holds the referee: an independent check of the finished car against every rule, measured from the outside like a scrutineer, showing how much room is left on each rule.
- The referee shares nothing with the cutter, so one cannot hide the other's mistakes.

**Now:** Waiting on GitHub runners: 180 cars (seeds 44359-44538) and the whole-car tests on 30d92d0 are queued. Last count on aa08f57: 98 of 120 legal; the rear-slot fix worked.

**Timeline:** 3 of 10 steps done

| # | Step | Status | Started | Finished | Note |
|---|---|---|---|---|---|
| 1 | List every rule and its check | ✅ Done | 2026-11-09 | 2026-11-09 | Every rule matched to a check or a reason, none left open. |
| 2 | Just-inside and just-outside tests | ✅ Done | 2026-11-09 | 2026-11-09 | Every size rule has a pass car and a fail car; all tests pass on GitHub. |
| 3 | Make the referee independent | ✅ Done | 2026-11-09 | 2026-11-09 | The checker uses only its own rule numbers; tests pass. |
| 4 | Parts on carved bodies (2,000 cars) | 🔄 Working on it | 2026-11-09 |  | 2026-11-13: about 470 one-car cars on the fixed code, about 80% legal, 0 crashes. Every reject has a named cause: number and logo room go to the body builder (exact sizes sent today); rear slot fixed (aa08f57); halo pocket and one unsolid file being traced. The counted run waits for the body builder's frozen version. |
| 5 | Real part weights | ⬜ To do |  |  |  |
| 6 | Build files | 🔄 Working on it | 2026-11-09 |  | 2026-11-13: parts list done and thinnest walls measured; still waiting for the team's printer limits and a makeable check. |
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
