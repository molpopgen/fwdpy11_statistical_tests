rule build_two_deme_IM_asymmetric_mig_recent_split:
    input:
        "testcode/build_two_deme_IM_model.py",
    output:
        "output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/model.pickle",
    threads: 1
    shell:
        """
        python3 testcode/build_two_deme_IM_model.py --Nref 1000 \
            --N0 2 --N1 3 --split 0.25 -T 0.03 --migrate 2.0 0. \
            --theta 100. \
            --outdir output/demographic_models/two_deme_IM_asymmetric_migration_recent_split
        """

rule integrate_two_deme_IM_asymmetric_mig_recent_split_moments:
    input:
        "testcode/integrate_two_deme_IM_model_moments.py",
    output:
        "output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/moments.fs",
    threads: 1
    shell:
        """
        OMP_NUM_THREADS=1 python3 testcode/integrate_two_deme_IM_model_moments.py \
            --N0 2 --N1 3 --split 0.25 -T 0.03 --migrate 2.0 0. --nsam 15 \
            --fsfile {output}
        """

rule run_two_deme_IM_asymmetric_mig_recent_split:
    input:
        "testcode/run_two_deme_IM_model.py",
        "output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/model.pickle",
    output:
        "output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/fst.np",
        "output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/deme0.np",
        "output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/deme1.np",
        "output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/caption.rst",
    threads: 64
    shell:
        """
        python3 testcode/run_two_deme_IM_model.py \
            --infile output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/model.pickle \
            --outdir output/demographic_models/two_deme_IM_asymmetric_migration_recent_split --nreps 128 --nworkers {threads} \
            --num_subsamples 1 --nsam 15
        """

rule plot_two_deme_IM_asymmetric_mig_recent_split:
    input:
        "testcode/plot_two_deme_IM_results.py",
        "output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/moments.fs",
        "output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/fst.np",
        "output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/deme0.np",
        "output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/deme1.np",
        "output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/caption.rst",
    output:
        report("output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/results.png",
            caption="../output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/caption.rst",
            category="Two deme IM")
    shell:
        """
        python3 testcode/plot_two_deme_IM_results.py --workdir output/demographic_models/two_deme_IM_asymmetric_migration_recent_split \
            --moments_theta 100.
        """


