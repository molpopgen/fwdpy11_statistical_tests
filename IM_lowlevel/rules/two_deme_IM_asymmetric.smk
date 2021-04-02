rule build_two_deme_IM_asymmetric_mig:
    input:
        "testcode/build_two_deme_IM_model.py",
    output:
        "output/demographic_models/two_deme_IM_asymmetric_migration/model.pickle",
    threads: 1
    shell:
        """
        python3 testcode/build_two_deme_IM_model.py --Nref 1000 \
            --N0 2 --N1 3 --split 0.5 -T 0.3 --migrate 2.0 0.5 \
            --theta 100. \
            --outdir output/demographic_models/two_deme_IM_asymmetric_migration
        """

rule integrate_two_deme_IM_asymmetric_mig_moments:
    input:
        "testcode/integrate_two_deme_IM_model_moments.py",
    output:
        "output/demographic_models/two_deme_IM_asymmetric_migration/moments.fs",
    threads: 1
    shell:
        """
        OMP_NUM_THREADS=1 python3 testcode/integrate_two_deme_IM_model_moments.py \
            --N0 2 --N1 3 --split 0.5 -T 0.3 --migrate 2.0 0.5 --nsam 15 \
            --fsfile {output}
        """

rule run_two_deme_IM_asymmetric_mig:
    input:
        "testcode/run_two_deme_IM_model.py",
        "output/demographic_models/two_deme_IM_asymmetric_migration/model.pickle",
    params:
        nreps=expand("{nreps}", nreps=config["im_model_nreps"])
    output:
        "output/demographic_models/two_deme_IM_asymmetric_migration/fst.np",
        "output/demographic_models/two_deme_IM_asymmetric_migration/deme0.np",
        "output/demographic_models/two_deme_IM_asymmetric_migration/deme1.np",
        "output/demographic_models/two_deme_IM_asymmetric_migration/caption.rst",
    threads: 64
    shell:
        """
        python3 testcode/run_two_deme_IM_model.py \
            --infile output/demographic_models/two_deme_IM_asymmetric_migration/model.pickle \
            --outdir output/demographic_models/two_deme_IM_asymmetric_migration --nreps {params.nreps} --nworkers {threads} \
            --num_subsamples 1 --nsam 15
        """

rule plot_two_deme_IM_asymmetric_mig:
    input:
        "testcode/plot_two_deme_IM_results.py",
        "output/demographic_models/two_deme_IM_asymmetric_migration/moments.fs",
        "output/demographic_models/two_deme_IM_asymmetric_migration/fst.np",
        "output/demographic_models/two_deme_IM_asymmetric_migration/deme0.np",
        "output/demographic_models/two_deme_IM_asymmetric_migration/deme1.np",
        "output/demographic_models/two_deme_IM_asymmetric_migration/caption.rst",
    output:
        report("output/demographic_models/two_deme_IM_asymmetric_migration/results.png",
            caption="../output/demographic_models/two_deme_IM_asymmetric_migration/caption.rst",
            category="Two deme IM")
    shell:
        """
        python3 testcode/plot_two_deme_IM_results.py --workdir output/demographic_models/two_deme_IM_asymmetric_migration \
            --moments_theta 100.
        """

