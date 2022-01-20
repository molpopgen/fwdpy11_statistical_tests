rule make_windowed_variation_plot:
    input: "output/windowed_variation.sqlite3",
           "testcode/windowed_variation_plot.py",
    output: report("output/windowed_variation.png", category="Windowed variation")
    threads: 1
    shell:
        """
        python3 testcode/windowed_variation_plot.py output/windowed_variation.sqlite3 output/windowed_variation.png
        """
