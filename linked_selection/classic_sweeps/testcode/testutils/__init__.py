ALPHAS = [100.0, 1000.0, 10000.0]
CUM_RHOS = [10.0, 100.0, 1000.0]
RHOS = []
__last_rho = 0
for i in CUM_RHOS:
    RHOS.append(i - __last_rho)
    __last_rho += RHOS[-1]
    RHOS.append(0.0)
DBNAME = "output/data.sqlite3"

SCALING = 2.0
DOMINANCE = 1.0

KIM_STEPAN_FIG4_N = int(2e5)
KIM_STEPAN_FIG4_S = 1e-3
KIM_STEPAN_FIG4_R_OVER_S = [0.01, 0.1, 0.2]
KIM_STEPAN_FIG4_R = [i * KIM_STEPAN_FIG4_S for i in KIM_STEPAN_FIG4_R_OVER_S]
