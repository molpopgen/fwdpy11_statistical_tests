rule windowed_variation_sims:
    input: "testcode/windowed_variation.py",
    output: "output/windowed_variation.sqlite3",
    threads: 64
    params:
        nreps=expand("{nreps}", nreps=config["nreps"]),
        popsize=expand("{popsize}", popsize=config["popsize"]),
    shell:
        """
        python3 testcode/windowed_variation.py --popsize {params.popsize} --nreps {params.nreps} --ncores {threads} 
        """
