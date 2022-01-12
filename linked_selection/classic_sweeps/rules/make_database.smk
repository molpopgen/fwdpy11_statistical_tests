rule make_database:
    input: "testcode/classic_sweep.py",
    output: "output/data.sqlite3",
    threads: 64
    params:
        nreps=expand("{nreps}", nreps=config["nreps"])
    shell:
        """
        python3 testcode/classic_sweep.py --nreps {params.nreps}
        """

