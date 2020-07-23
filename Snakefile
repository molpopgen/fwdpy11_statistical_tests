rule all:
    input:
        # Output from "rules/two_deme_IM_asymmetric.smk"
        "output/demographic_models/two_deme_IM_asymmetric_migration/results.png",
        # Output from "rules/two_deme_IM_asymmetric_recent_split.smk"
        "output/demographic_models/two_deme_IM_asymmetric_migration_recent_split/results.png",
        # Output from "rules/two_deme_IM_symmetric.smk"
        "output/demographic_models/two_deme_IM_symmetric_migration/results.png",
        # Output from "rules/two_deme_IM_no_migration_very_recent_split.smk"
        "output/demographic_models/two_deme_IM_no_migration_very_recent_split/results.png",

include: "rules/two_deme_IM_asymmetric.smk"
include: "rules/two_deme_IM_asymmetric_recent_split.smk"
include: "rules/two_deme_IM_symmetric.smk"
include: "rules/two_deme_IM_no_migration_very_recent_split.smk"

