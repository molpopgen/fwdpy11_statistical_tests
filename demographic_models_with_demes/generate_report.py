import argparse
import logging
import os
import sys
import subprocess

logging.basicConfig(
    filename="logfile.txt",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)


def handle_return_value(output, *, log=False):
    if output.returncode != 0:
        logging.error(output.stderr.decode("utf8").rstrip())
        sys.exit(1)
    elif log is True:
        stdout = output.stdout.decode("utf8").rstrip()
        if len(stdout) > 0:
            logging.info(f"STDOUT:\n{stdout}")
        stderr = output.stderr.decode("utf8").rstrip()
        if len(stderr) > 0:
            logging.info(f"STDERR:\n{stderr}")


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

    logging.info(f"Building temporary docker image demes_statistical_tests:{tag}.")

    output = subprocess.run(
        [
            "docker",
            "build",
            "--build-arg",
            f"tag={tag}",
            ".",
            "-t",
            f"demes_statistical_tests:{tag}",
        ],
        capture_output=True,
    )
    handle_return_value(output)

    logging.info("Running Snakefile.")

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

    output = subprocess.run(
        [
            "docker",
            "run",
            "-v",
            f"{local_folder}",
            f"demes_statistical_tests:{tag}",
            "/bin/bash",
            "-c",
            f'"{snakemake_cmd}"',
        ],
        capture_output=True,
    )
    handle_return_value(output, log=True)

    logging.info(f"Removing temporary docker image demes_statistical_tests:{tag}.")
    output = subprocess.run(
        ["docker", "image", "rm", "-f", f"im_lowlevel:{tag}"], capture_output=True
    )
    handle_return_value(output)
    logging.info("Done!")
