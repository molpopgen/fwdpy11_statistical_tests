rule kimstephan:
    input: "output/data.sqlite3",
           "testcode/kimstephan2002.py",
    log: "output/kimstephan.log",
    threads: 8
    params:
        popsize=expand("{popsize}", popsize=config["popsize"]),
    shell:
        """
        python3 testcode/kimstephan2002.py --popsize {params.popsize} --cores {threads} > output/kimstephan.log
        """
