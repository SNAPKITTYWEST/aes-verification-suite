"""
GF(2^8) Field Arithmetic for AES Verification

Irreducible polynomial: x^8 + x^4 + x^3 + x + 1 (0x11B)
All 256 elements, verified multiplicative group of order 255.
"""


def gf_mul(a: int, b: int) -> int:
    """Multiply two elements in GF(2^8)."""
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1B
        b >>= 1
    return p


def gf_pow(x: int, n: int) -> int:
    """Compute x^n in GF(2^8) via square-and-multiply."""
    result = 1
    base = x
    while n > 0:
        if n & 1:
            result = gf_mul(result, base)
        base = gf_mul(base, base)
        n >>= 1
    return result


def gf_inv(x: int) -> int:
    """Multiplicative inverse: x^{-1} = x^254 in GF(2^8). Convention: 0^{-1} = 0."""
    if x == 0:
        return 0
    return gf_pow(x, 254)


def verify_field():
    """Verify GF(2^8) properties."""
    results = {}

    # 1. x * x^254 = 1 for all nonzero x (Fermat's little theorem)
    fermat_ok = all(gf_mul(x, gf_pow(x, 254)) == 1 for x in range(1, 256))
    results["fermat_little_theorem"] = fermat_ok

    # 2. Multiplicative group is cyclic of order 255
    # Find a generator (primitive element)
    generator = None
    for g in range(2, 256):
        seen = set()
        val = 1
        for _ in range(255):
            val = gf_mul(val, g)
            seen.add(val)
        if len(seen) == 255:
            generator = g
            break
    results["generator_exists"] = generator is not None
    results["generator_value"] = generator

    # 3. x^255 = 1 for all nonzero x
    order_ok = all(gf_pow(x, 255) == 1 for x in range(1, 256))
    results["all_order_divides_255"] = order_ok

    # 4. Distributivity: a * (b ^ c) = (a*b) ^ (a*c)
    import random
    random.seed(42)
    dist_ok = True
    for _ in range(10000):
        a = random.randint(0, 255)
        b = random.randint(0, 255)
        c = random.randint(0, 255)
        lhs = gf_mul(a, b ^ c)
        rhs = gf_mul(a, b) ^ gf_mul(a, c)
        if lhs != rhs:
            dist_ok = False
            break
    results["distributivity"] = dist_ok

    return results


if __name__ == "__main__":
    results = verify_field()
    print("GF(2^8) Verification:")
    for k, v in results.items():
        print(f"  {k}: {v}")
