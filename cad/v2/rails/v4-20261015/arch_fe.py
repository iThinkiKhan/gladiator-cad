"""Rough 3D beam-frame estimate for one arch rail (Claude, 2026-10-15). NOT a certified analysis.

Euler-Bernoulli beams along the arch centreline, fixed at both feet (screwed + nut), loads at the three deck-seat pads.
Section 8.5 (X) x 7.0 (radial, the thinnest part) mm, PETG E = 2000 MPa (low, to be conservative for printed parts), G = 725 MPa.
Stress = |N|/A + |M_in|/Z_in + |M_out|/Z_out (summed, conservative); torsion and stress concentrations ignored.
Allowable used for comparison: 20 MPa (printed PETG with 4+ walls, loaded along the layers). Print the rail lying on its inner face.
"""
import numpy as np, math, json, sys

E, G = 2000.0, 725.0
b, t = 8.5, 7.0                       # b along X (out of plane), t radial (in plane); 7.0 is the thinnest (leg) value, so this is conservative
A = b * t
I_in = b * t ** 3 / 12.0              # bending in the arch plane (about X)
I_out = t * b ** 3 / 12.0             # bending out of plane (about the in-plane normal)
J = 0.196 * b * t ** 3 * (b / b)      # rough
Zin, Zout = I_in / (t / 2), I_out / (b / 2)
yc, zc, a_c, b_c, zf = 68.35, 24.0, 51.15, 21.5, 6.0

# centreline nodes: rear leg up, ellipse over, front leg down
pts = []
for z in np.arange(zf, zc, 2.0):
    pts.append((yc - a_c, z))
for k in range(0, 91):
    th = math.pi - math.pi * k / 90
    pts.append((yc + a_c * math.cos(th), zc + b_c * math.sin(th)))
for z in np.arange(zc - 2.0, zf - 0.01, -2.0):
    pts.append((yc + a_c, z))
pts = np.array(pts)
n = len(pts)
# nodes in 3D: (X, Y, Z) with X = 0 (plane)
X3 = np.zeros((n, 3))
X3[:, 1] = pts[:, 0]
X3[:, 2] = pts[:, 1]


def kloc(L):
    k = np.zeros((12, 12))
    EA, GJ = E * A / L, G * J / L
    k[0, 0] = k[6, 6] = EA; k[0, 6] = k[6, 0] = -EA
    k[3, 3] = k[9, 9] = GJ; k[3, 9] = k[9, 3] = -GJ
    # bending about local y (displacement along local z): uses I_in
    a = E * I_in
    idx = [2, 4, 8, 10]
    kb = a / L ** 3 * np.array([[12, -6 * L, -12, -6 * L], [-6 * L, 4 * L * L, 6 * L, 2 * L * L], [-12, 6 * L, 12, 6 * L], [-6 * L, 2 * L * L, 6 * L, 4 * L * L]])
    for i in range(4):
        for j in range(4):
            k[idx[i], idx[j]] += kb[i, j]
    # bending about local z (displacement along local y): uses I_out
    a = E * I_out
    idx = [1, 5, 7, 11]
    kb = a / L ** 3 * np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L], [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]])
    for i in range(4):
        for j in range(4):
            k[idx[i], idx[j]] += kb[i, j]
    return k


def rot(d):
    x = d / np.linalg.norm(d)
    y = np.array([1.0, 0, 0])
    z = np.cross(x, y)
    return np.array([x, y, z])


K = np.zeros((6 * n, 6 * n))
elems = []
for e in range(n - 1):
    d = X3[e + 1] - X3[e]
    L = np.linalg.norm(d)
    Rm = rot(d)
    T = np.zeros((12, 12))
    for i in range(4):
        T[3 * i:3 * i + 3, 3 * i:3 * i + 3] = Rm
    kg = T.T @ kloc(L) @ T
    dofs = list(range(6 * e, 6 * e + 6)) + list(range(6 * (e + 1), 6 * (e + 1) + 6))
    K[np.ix_(dofs, dofs)] += kg
    elems.append((e, L, T, dofs))

fixed = list(range(0, 6)) + list(range(6 * (n - 1), 6 * n))
free = [i for i in range(6 * n) if i not in fixed]
pad_y = [24.0, 68.5, 113.0]
pad_nodes = [int(np.argmin(np.abs(X3[:, 1] - py) + (X3[:, 2] < 25) * 1e3)) for py in pad_y]
apex = int(np.argmax(X3[:, 2]))


def solve(fx, fy, fz):
    """per-rail total loads in N, shared equally by the three pads"""
    F = np.zeros(6 * n)
    for pn in pad_nodes:
        F[6 * pn + 0] += fx / 3; F[6 * pn + 1] += fy / 3; F[6 * pn + 2] += fz / 3
    u = np.zeros(6 * n)
    u[free] = np.linalg.solve(K[np.ix_(free, free)], F[free])
    smax, where = 0.0, None
    for (e, L, T, dofs) in elems:
        ul = T @ u[dofs]
        f = kloc(L) @ ul
        for end, o in ((0, 0), (1, 6)):
            N_ = abs(f[o]); Min = abs(f[o + 4]); Mout = abs(f[o + 5])
            s = N_ / A + Min / Zin + Mout / Zout
            if s > smax:
                smax, where = s, (round(float(X3[e + end][1]), 1), round(float(X3[e + end][2]), 1))
    return dict(max_stress_MPa=round(smax, 2), at_YZ=where, apex_dx_mm=round(float(u[6 * apex + 0]), 3), apex_dy_mm=round(float(u[6 * apex + 1]), 3),
                apex_dz_mm=round(float(u[6 * apex + 2]), 3))


# unit mass guess 0.9 kg for deck + boards + mast + head + drivers (not measured); shock factor 4 g; per rail half
m_kg, g_shock = 0.9, 4.0
W_rail = m_kg * 9.81 * g_shock / 2.0
cases = {
    'static weight (1 g, per rail)': solve(0, 0, -m_kg * 9.81 / 2),
    'shock 4 g down': solve(0, 0, -W_rail),
    'shock 4 g along Y (braking / hitting a wall) + 1 g weight': solve(0, W_rail, -m_kg * 9.81 / 2),
    'shock 4 g sideways (X, tipping or side hit) + 1 g weight': solve(W_rail, 0, -m_kg * 9.81 / 2),
}
out = dict(assumptions=dict(unit_mass_kg=m_kg, shock_g=g_shock, E_MPa=E, section_mm=[b, t], allowable_MPa=20.0), per_rail_load_N=round(W_rail, 1), cases=cases,
           note='Rough estimate: pinned screws assumed rigid, no stress concentrations at pads/feet, mass is a guess, deck stiffness ignored (it helps).')
print(json.dumps(out, indent=1))
open(sys.argv[1] if len(sys.argv) > 1 else 'arch_fe.json', 'w').write(json.dumps(out, indent=1))
