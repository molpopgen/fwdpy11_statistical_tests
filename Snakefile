rule all:
    input:
        "demographic_models/two_deme_IM_assymetric_migration/S.png",
        "demographic_models/two_deme_IM_symetric_migration/S.png"

rule build_two_deme_IM_assymmetric_mig:
    input:
        "testcode/build_two_deme_IM_model.py",
    output:
        "demographic_models/two_deme_IM_assymetric_migration/model.pickle",
    threads: 1
    shell:
        """
        python3 testcode/build_two_deme_IM_model.py --Nref 1000 \
            --N0 2 --N1 3 --split 0.5 -T 0.3 --migrate 2.0 0.5 \
            --outdir demographic_models/two_deme_IM_assymetric_migration
        """

rule two_deme_IM_assymmetric_mig:
    input:
        "testcode/run_two_deme_IM_model.py",
        "demographic_models/two_deme_IM_assymetric_migration/model.pickle",
    output:
        report("demographic_models/two_deme_IM_assymetric_migration/S.png",
        caption="demographic_models/two_deme_IM_assymetric_migration/caption.rst",
        category="Two deme IM tests")
    threads: 64
    shell:
        """
        python3 testcode/run_two_deme_IM_model.py \
            --infile demographic_models/two_deme_IM_assymetric_migration/model.pickle \
            --outdir demographic_models/two_deme_IM_assymetric_migration --nreps 64 --nworkers {threads}
        """

rule build_two_deme_IM_symmetric_mig:
    input:
        "testcode/build_two_deme_IM_model.py",
    output:
        "demographic_models/two_deme_IM_symetric_migration/model.pickle",
    threads: 1
    run:
        shell("""
        python3 testcode/build_two_deme_IM_model.py --Nref 1000 --N0 2 --N1 3 --split 0.5 -T 0.3 \
        --migrate 1.0 1.0 --outdir demographic_models/two_deme_IM_symetric_migration
        """)

rule two_deme_IM_symmetric_mig:
    input:
        "testcode/run_two_deme_IM_model.py",
        "demographic_models/two_deme_IM_symetric_migration/model.pickle",
    output:
        report("demographic_models/two_deme_IM_symetric_migration/S.png",
        caption="demographic_models/two_deme_IM_symetric_migration/caption.rst",
        category="Two deme IM tests")
    threads: 64
    run:
        shell("""
        python3 testcode/run_two_deme_IM_model.py \
        --infile demographic_models/two_deme_IM_symetric_migration/model.pickle \
        --outdir demographic_models/two_deme_IM_symetric_migration --nreps 64 --nworkers {threads}
        """)

