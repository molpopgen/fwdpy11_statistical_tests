import argparse
import os
import sys
import subprocess


def make_parser():
    parser = argparse.ArgumentParser(
        description="Generate report for models built with the demes.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--tag",
        "-t",
        type=str,
        default=None,
        help="The fwdpy11 version tag.  This will be used to build a new image based on the local base image for the specified version. If 'None', will default to 'stable'",
    )
    parser.add_argument(
        "--nreps",
        "-n",
        default=8,
        help="Number of simulation replicates to run for each test scenario.",
    )
    parser.add_argument(
        "--cores",
        "-c",
        default=1,
        help="Maximum cores/threads to use during work flow.",
    )

    return parser


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args(sys.argv[1:])

    if args.tag is None:
        tag = "stable"
    else:
        tag = args.tag

    sys.stderr.write(f"Building base docker image demes_statistical_tests:{tag}\n")

    subprocess.run(
        [
            "docker",
            "build",
            "--build-arg",
            f"tag={tag}",
            ".",
            "-t",
            f"demes_statistical_tests:{tag}",
        ]
    )
    sys.stderr.write("Running Snakefile.\n")

    local_folder = os.getcwd() + ":/mnt"

    snakemake_cmd = " ".join(
        [
            '"snakemake',
            "all_models",
            "-j",
            str(args.cores),
            "--config",
            f"nreps={args.nreps}",
            "&&",
            "snakemake",
            "all_models",
            "--report",
            '/mnt/report.html"',
        ]
    )

    subprocess.run(
        [
            "docker",
            "run",
            "-v",
            f"{local_folder}",
            f"demes_statistical_tests:{tag}",
            "/bin/bash",
            "-c",
            f'"{snakemake_cmd}"',
        ]
    )

    subprocess.run(["docker", "image", "rm", "-f", f"im_lowlevel:{tag}"])
