rule python_fixation_times:
    input: "testcode/fixation_times_from_binomial_simulation.py", "output/data.sqlite3"
    log: "python_fixation_times.log"
    threads: 64
    params:
        nreps=expand("{nreps}", nreps=config["nreps"]),
        popsize=expand("{popsize}", popsize=config["popsize"]),
    shell:
        """
        python3 testcode/fixation_times_from_binomial_simulation.py --popsize {params.popsize} --nreps {params.nreps} --ncores {threads} > python_fixation_times.log
        """

