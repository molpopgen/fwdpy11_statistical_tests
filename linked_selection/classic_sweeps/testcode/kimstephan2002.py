"""
Equation 5 from Kim, Yuseob, and Wolfgang Stephan. 2002. “Detecting a Local Signature of Genetic Hitchhiking along a Recombining Chromosome.” Genetics 160 (2): 765–77.
"""

import argparse
import math

import numpy as np


def phi1p(theta, p, r, s, epsilon):
    assert p > 0.0
    assert p < 1.0
    C = 1.0 - epsilon ** (r / s)

    if p < C:
        return theta / p - theta / C
    elif 1.0 - C < p:
        return theta / C
    return 0


def Pnk(n, k, theta, r, s, epsilon, delta):
    assert k > 0
    assert k < n
    p = delta
    rv = 0.0
    C = math.comb(n, k)
    ldelta = math.log(delta)
    while p < 1:
        #rv += p ** k * (1.0 - p) ** (n - k) * phi1p(theta, p, r, s, epsilon) * delta
        phi = phi1p(theta,p,r,s,epsilon)
        if phi > 0.0:
            temp = k*math.log(p) + (n-k)*math.log(1.-p) + math.log(phi) + ldelta
            rv += math.exp(temp)
        p += delta

    return C * rv


def polarised_sfs(n, theta, r, s, epsilon, delta=1e-5):
    return [Pnk(n, i, theta, r, s, epsilon, delta) for i in range(1, n)]


N = 5000
alpha = 1000
rho = 100
r = rho / 4 / N
s = alpha / 2 / N

print(polarised_sfs(20, 1.0, r, s, 1.0 / alpha, 1e-6))
