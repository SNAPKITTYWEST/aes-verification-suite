"""
GF(2) Jacobian Computation for AES

Computes the 128x128 matrix D_{F_2} F_K over GF(2) and its rank.
Demonstrates: rank=128 (full) means F_K is a permutation,
but rank=128 does NOT imply efficient inversion.
"""

from gf256 import gf_mul
from sbox import sbox

MC_MATRIX = [[2, 3, 1, 1], [1, 2, 3, 1], [1, 1, 2, 3], [3, 1, 1, 2]]

SHIFT_ROWS = [0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11]


def aes_round(state: list, round_key: list) -> list:
    """One full AES round: SubBytes + ShiftRows + MixColumns + AddRoundKey."""
    # SubBytes
    s = [sbox(b) for b in state]
    # ShiftRows
    s = [s[SHIFT_ROWS[i]] for i in range(16)]
    # MixColumns
    result = [0] * 16
    for col in range(4):
        for row in range(4):
            val = 0
            for k in range(4):
                val ^= gf_mul(MC_MATRIX[row][k], s[col * 4 + k])
            result[col * 4 + row] = val
    # AddRoundKey
    return [r ^ k for r, k in zip(result, round_key)]


def compute_gf2_jacobian(func, key: list, point: list) -> list:
    """
    Compute the GF(2) Jacobian (128x128 matrix over F_2).
    J[i][j] = bit i of (F(X + e_j) XOR F(X))
    where e_j flips bit j of the input.
    """
    base = func(point, key)

    def to_bits(state):
        bits = []
        for byte in state:
            for bit in range(8):
                bits.append((byte >> bit) & 1)
        return bits

    base_bits = to_bits(base)
    jacobian = []

    for j in range(128):
        perturbed = point.copy()
        perturbed[j // 8] ^= (1 << (j % 8))
        out = func(perturbed, key)
        out_bits = to_bits(out)
        col = [base_bits[i] ^ out_bits[i] for i in range(128)]
        jacobian.append(col)

    # Transpose: jacobian[j] is column j, we want row-major
    matrix = [[jacobian[j][i] for j in range(128)] for i in range(128)]
    return matrix


def gf2_rank(matrix: list) -> int:
    """Rank of a matrix over GF(2) via Gaussian elimination."""
    n = len(matrix)
    m = [row[:] for row in matrix]
    rank = 0
    for col in range(n):
        pivot = -1
        for row in range(rank, n):
            if m[row][col] == 1:
                pivot = row
                break
        if pivot == -1:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        for row in range(n):
            if row != rank and m[row][col] == 1:
                for k in range(n):
                    m[row][k] ^= m[rank][k]
        rank += 1
    return rank


def verify_jacobian():
    """Compute and verify GF(2) Jacobian rank for AES round function."""
    import os
    key = list(os.urandom(16))
    plaintext = list(os.urandom(16))

    jacobian = compute_gf2_jacobian(aes_round, key, plaintext)
    rank = gf2_rank(jacobian)

    return {
        "matrix_size": "128x128 over GF(2)",
        "rank": rank,
        "full_rank": rank == 128,
        "interpretation": (
            "Full rank => F_K is locally injective (permutation). "
            "But rank=128 does NOT imply efficient inversion. "
            "A random permutation on 2^128 also has rank 128."
        ),
    }


if __name__ == "__main__":
    result = verify_jacobian()
    print("GF(2) Jacobian Analysis (1-round AES):")
    for k, v in result.items():
        print(f"  {k}: {v}")
