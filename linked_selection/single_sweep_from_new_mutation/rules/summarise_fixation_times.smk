rule summarise_fixation_times:
    input: "output/data.sqlite3", "testcode/summarise_fixation_times.py",
    output: report("output/fixation_times.png", category="Fixation times")
    threads: 1
    shell:
        """
        python3 testcode/summarise_fixation_times.py
        """
