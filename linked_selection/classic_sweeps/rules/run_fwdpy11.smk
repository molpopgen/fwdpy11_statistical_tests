rule make_database:
    input: "testcode/classic_sweep.py",
    output: "output/data.sqlite3",
    threads: 64
    params:
        nreps=expand("{nreps}", nreps=config["nreps"]),
        popsize=expand("{popsize}", popsize=config["popsize"]),
    shell:
        """
        python3 testcode/classic_sweep.py --popsize {params.popsize} --nreps 1024 --ncores {threads}
        """

