rule build_two_deme_IM_symmetric_mig:
    input:
        "testcode/build_two_deme_IM_model.py",
    output:
        "output/demographic_models/two_deme_IM_symmetric_migration/model.pickle",
    threads: 1
    run:
        shell("""
        python3 testcode/build_two_deme_IM_model.py --Nref 1000 --N0 2 --N1 3 --split 0.5 -T 0.3 \
        --theta 100. \
        --migrate 1.0 1.0 --outdir output/demographic_models/two_deme_IM_symmetric_migration
        """)

rule integrate_two_deme_IM_symmetric_mig_moments:
    input:
        "testcode/integrate_two_deme_IM_model_moments.py",
    output:
        "output/demographic_models/two_deme_IM_symmetric_migration/moments.fs",
    threads: 1
    shell:
        """
        OMP_NUM_THREADS=1 python3 testcode/integrate_two_deme_IM_model_moments.py \
            --N0 2 --N1 3 --split 0.5 -T 0.3 --migrate 1.0 1.0 --nsam 15 \
            --fsfile {output}
        """

rule run_two_deme_IM_symmetric_mig:
    input:
        "testcode/run_two_deme_IM_model.py",
        "output/demographic_models/two_deme_IM_symmetric_migration/model.pickle",
    output:
        "output/demographic_models/two_deme_IM_symmetric_migration/fst.np",
        "output/demographic_models/two_deme_IM_symmetric_migration/deme0.np",
        "output/demographic_models/two_deme_IM_symmetric_migration/deme1.np",
        "output/demographic_models/two_deme_IM_symmetric_migration/caption.rst",
    threads: 64
    run:
        shell("""
        python3 testcode/run_two_deme_IM_model.py \
        --infile output/demographic_models/two_deme_IM_symmetric_migration/model.pickle \
        --outdir output/demographic_models/two_deme_IM_symmetric_migration --nreps 128 --nworkers {threads} \
        --num_subsamples 1 --nsam 15
        """)

rule plot_two_deme_IM_symmetric_mig:
    input:
        "testcode/plot_two_deme_IM_results.py",
        "output/demographic_models/two_deme_IM_symmetric_migration/moments.fs",
        "output/demographic_models/two_deme_IM_symmetric_migration/fst.np",
        "output/demographic_models/two_deme_IM_symmetric_migration/deme0.np",
        "output/demographic_models/two_deme_IM_symmetric_migration/deme1.np",
        "output/demographic_models/two_deme_IM_symmetric_migration/caption.rst",
    output:
        report("output/demographic_models/two_deme_IM_symmetric_migration/results.png",
            caption="../output/demographic_models/two_deme_IM_symmetric_migration/caption.rst",
            category="Two deme IM")
    shell:
        """
        python3 testcode/plot_two_deme_IM_results.py --workdir output/demographic_models/two_deme_IM_symmetric_migration \
            --moments_theta 100.
        """

