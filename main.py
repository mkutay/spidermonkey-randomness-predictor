#!/usr/bin/python3
import z3
import struct

sequence = [
  0.7177022661837045,
  0.4951146730115529,
  0.8135234699950077,
  0.6650083345378781,
  0.35751644064280597
]

def get_states():
  solver = z3.Solver()

  se_state0, se_state1 = z3.BitVecs("se_state0 se_state1", 64)

  for i in range(len(sequence)):
    se_s1 = se_state0
    se_s0 = se_state1
    se_s1 ^= se_s1 << 23
    se_s1 ^= z3.LShR(se_s1, 17)  # Logical shift instead of Arthmetric shift
    se_s1 ^= se_s0
    se_s1 ^= z3.LShR(se_s0, 26)
    se_state0 = se_state1
    se_state1 = se_s1
    calc = se_state1 + se_state0

    # Get the lower 52 bits (mantissa)
    mantissa = sequence[i] * (0x1 << 53)

    # Compare Mantissas
    solver.add(int(mantissa) == (calc & 0x1FFFFFFFFFFFFF))


  if solver.check() == z3.sat:
    model = solver.model()

    states = {}
    for state in model.decls():
      states[state.__str__()] = model[state]

    print(states)
    return states
  print('oops')

MASK = 0xFFFFFFFFFFFFFFFF

def next(state0, state1):
  s1 = state0 & MASK
  s0 = state1 & MASK
  s1 ^= (s1 << 23) & MASK
  s1 ^= (s1 >> 17) & MASK
  s1 ^= s0 & MASK
  s1 ^= (s0 >> 26) & MASK 
  state0 = state1 & MASK
  state1 = s1 & MASK
  gen = (state0 + state1) & MASK
  return state0, state1, gen
states = get_states()

state0 = states["se_state0"].as_long();
state1 = states["se_state1"].as_long();

for i in range(len(sequence)):
  state0, state1, out = next(state0, state1)

for i in range(15):
  state0, state1, out = next(state0, state1)
  state0, state1, out = next(state0, state1)

  double = float(out & 0x1FFFFFFFFFFFFF) / (0x1 << 53) 

  print(double)
