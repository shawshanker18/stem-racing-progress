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

**Now:** Carving 200 on the new code (Jdiejei 43093351425): 193 legal, 6 illegal, 1 over time. The 6 are halo or block 7-15 mm3 on 41504/9, 41514/3 and 41518/4, and front span 24.2-24.9 mm on 41516/8, 41518/1 and 41518/6. Rerunning those seeds (Jdiejei 43140540669) and carving 41520-41524 (anasssssssss1 43140536546). Grid seeds 41381-41390 all within 0.5% (43118866738). Remap passes as is (43066533385). Sizing 200 queued on main (43118952256). Not tagged.

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

*Times a finished car over the 20 m race.* 61.8% · being built

- An airflow simulation measures how hard the air pushes back on the car and its wheels.
- A race model turns that push, the weight and the launch into a race time, and says which inputs matter most.
- It must be right (checked against published wind-tunnel results), quiet (a tiny change gives a tiny time change) and give the same answer on every machine.
- Every other part trusts it to say which car is faster.

**Now:** Timing noise met on the smooth-change test: 0.20 ms against the 0.3 ms mark (16 cars). A confirming rerun is going. Repeat on six machines still 0.29 ms against 0.1; cause being checked.

**Timeline:** 1 of 10 steps done

| # | Step | Status | Started | Finished | Note |
|---|---|---|---|---|---|
| 1 | Check against published wind-tunnel results | 🔄 Working on it | 2026-11-09 |  | Drag reads too high so far; testing settings to find out why. |
| 2 | Cut the timing noise | 🔄 Working on it | 2026-11-09 |  | Re-measured without the early stop: far above target. Cars jump between three drag levels; testing whether the mesh or the airflow causes it. |
| 3 | Quick vs detailed ranking check | ✅ Done | 2026-11-09 | 2026-11-10 | Passed: the quick mesh orders twenty cars the same way as the detailed mesh, well above the pass marks. |
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

**Now:** Compass test on two carved cars: car 2 has most of its measurements back, car 1 restarted on a teammate account after GitHub refused to start it for a while. Part 5 carving loop: four ways of reaching the best car faster were tried and none reached the mark, so they were undone; now recording every step of the chains that fall short to find where they stall.

**Timeline:** 0 of 9 steps done

| # | Step | Status | Started | Finished | Note |
|---|---|---|---|---|---|
| 1 | Known-answer test | ❌ Failed, being redone | 2026-11-09 |  | Fast map fails on every setting tried, including the maker's own full setup; the backup measured map passes. |
| 2 | Compass test on the car | 🔄 Working on it | 2026-11-11 |  | Running on two carved cars: the measured map is built from small bumps, then checked against 40 random cuts per car. Pass: direction right on 8 of 10 cuts that clearly change the time, and a close match overall. |
| 3 | Fixes, tried in order | ⬜ To do |  |  |  |
| 4 | Backup measured map (only if needed) | 🔄 Working on it | 2026-11-09 |  | Passed on the simple wing: matched every test shape it had not seen. Waiting for quieter car runs before trying it on cars. |
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

**Now:** Recheck of the first 200 carved cars on the body builder's fixed code: 153 legal, 32 not, 14 stopped for running over time (to fix). The cargo, mesh-sliver and rear-overhang faults are gone. Car 43100/8 is now legal; 43107/15 ran over time. Rejects: no room for logo or number (25), rear slot too tight for the cutter (6), front wing span (2), halo pocket (2).

**Timeline:** 3 of 10 steps done

| # | Step | Status | Started | Finished | Note |
|---|---|---|---|---|---|
| 1 | List every rule and its check | ✅ Done | 2026-11-09 | 2026-11-09 | Every rule matched to a check or a reason, none left open. |
| 2 | Just-inside and just-outside tests | ✅ Done | 2026-11-09 | 2026-11-09 | Every size rule has a pass car and a fail car; all tests pass on GitHub. |
| 3 | Make the referee independent | ✅ Done | 2026-11-09 | 2026-11-09 | The checker uses only its own rule numbers; tests pass. |
| 4 | Parts on carved bodies (2,000 cars) | 🔄 Working on it | 2026-11-09 |  | Trial runs on the body builder's changing code, to find crashes and new kinds of rejects; the counted run waits for its frozen version. |
| 5 | Real part weights | ⬜ To do |  |  |  |
| 6 | Build files | 🔄 Working on it | 2026-11-09 |  | Parts list done; thinnest walls measured; waiting for the team's printer limits and a makeable check. |
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
