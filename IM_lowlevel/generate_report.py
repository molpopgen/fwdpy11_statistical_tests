import argparse
import os
import sys
import subprocess


def make_parser():
    parser = argparse.ArgumentParser(
        description="Generate report for IM models built with the low-level demography API.",
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

    sys.stderr.write(f"Building base docker image im_lowlevel:{tag}\n")

    subprocess.run(
        [
            "docker",
            "build",
            "--build-arg",
            f"tag={tag}",
            ".",
            "-t",
            f"im_lowlevel:{tag}",
        ]
    )
    sys.stderr.write("Running Snakefile.\n")

    local_folder = os.getcwd() + ":/mnt"

    snakemake_cmd = " ".join(
        [
            '"snakemake',
            "-j",
            str(args.cores),
            "--config",
            f"nreps={args.nreps}",
            "&&",
            "snakemake",
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
            f"im_lowlevel:{tag}",
            "/bin/bash",
            "-c",
            f'"{snakemake_cmd}"',
        ]
    )

    subprocess.run(["docker", "image", "rm", "-f", f"im_lowlevel:{tag}"])
