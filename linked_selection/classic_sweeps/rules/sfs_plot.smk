rule make_sfs_plot:
    input: "output/data.sqlite3",
           "testcode/sfs_plot.py",
    output: report("output/sfs.png", category="Allele frequency spectrum")
    threads: 1
    shell:
        """
        python3 testcode/sfs_plot.py output/data.sqlite3 output/sfs.png
        """
