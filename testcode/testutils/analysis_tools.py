import numpy as np
import tskit


def tskit_fs(pop, nsam, mode="site", joint=True):
    """
    pop - fwdpy11.DiploidPopulation
    nsam - sample size (diploids) per deme
    mode - the tree seq stat mode
    joint - Joint FS?
    """
    ts = pop.dump_tables_to_tskit()

    md = np.array(pop.diploid_metadata, copy=False)

    ud = np.unique(md["deme"])

    samples = []
    for i in ud:
        w = np.where(md["deme"] == i)[0]
        r = np.random.choice(w, nsam, replace=False)
        s = md["nodes"][r].flatten()
        samples.append(s)

    if joint is True:
        return ts.allele_frequency_spectrum(samples, mode=mode, polarised=True)

    afs = dict()
    for i, j in zip(ud, samples):
        afs[i] = ts.allele_frequency_spectrum([j], mode=mode, polarised=True)


def fs(pop, nsam, marginalize=False):
    md = np.array(pop.diploid_metadata, copy=False)

    ud = np.unique(md["deme"])

    samples = []
    for i in ud:
        w = np.where(md["deme"] == i)[0]
        r = np.random.choice(w, nsam, replace=False)
        s = md["nodes"][r].flatten()
        samples.append(s)
    return pop.tables.fs(samples, marginalize=marginalize)
