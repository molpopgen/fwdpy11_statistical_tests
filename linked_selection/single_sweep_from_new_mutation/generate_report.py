import argparse
import logging
import os
import subprocess
import sys


def setup_logging(logfile):
    logging.basicConfig(
        filename=logfile,
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


def set_tag(args):
    if args.tag is None:
        tag = "stable"
    else:
        tag = args.tag
    return tag


def run_sfs(args):
    tag = set_tag(args)
    setup_logging("hard_sweeps_sfs_logfile.txt")
    logging.info(f"Building temporary docker image hard_sweeps_sfs:{tag}.")

    output = subprocess.run(
        [
            "docker",
            "build",
            "--build-arg",
            f"tag={tag}",
            ".",
            "-t",
            f"hard_sweeps_sfs:{tag}",
        ],
        capture_output=True,
    )
    handle_return_value(output)

    logging.info("Running Snakefile.")

    local_folder = os.getcwd() + ":/mnt"

    snakemake_cmd = " ".join(
        [
            '"snakemake',
            "--snakefile",
            "Snakefile.sfs",
            "-j",
            str(args.cores),
            "--config",
            f"nreps={args.nreps}",
            f"popsize={args.popsize}",
            "&&",
            "snakemake",
            "--snakefile",
            "Snakefile.sfs",
            "--report",
            '/mnt/sfs_report.html"',
        ]
    )

    output = subprocess.run(
        [
            "docker",
            "run",
            "-v",
            f"{local_folder}",
            f"hard_sweeps_sfs:{tag}",
            "/bin/bash",
            "-c",
            f'"{snakemake_cmd}"',
        ],
        capture_output=True,
    )
    handle_return_value(output, log=True)

    logging.info(f"Removing temporary docker image hard_sweeps_sfs:{tag}.")
    output = subprocess.run(
        ["docker", "image", "rm", "-f", f"hard_sweeps_sfs:{tag}"], capture_output=True
    )
    handle_return_value(output)
    logging.info("Done!")


def run_windowed_variation(args):
    tag = set_tag(args)
    setup_logging("hard_sweeps_windowed_variation.txt")
    logging.info(
        f"Building temporary docker image hard_sweeps_windowed_variation:{tag}."
    )

    output = subprocess.run(
        [
            "docker",
            "build",
            "--build-arg",
            f"tag={tag}",
            ".",
            "-t",
            f"hard_sweeps_windowed_variation:{tag}",
        ],
        capture_output=True,
    )
    handle_return_value(output)

    logging.info("Running Snakefile.")

    local_folder = os.getcwd() + ":/mnt"

    snakemake_cmd = " ".join(
        [
            '"snakemake',
            "--snakefile",
            "Snakefile.windowed_variation",
            "-j",
            str(args.cores),
            "--config",
            f"nreps={args.nreps}",
            f"popsize={args.popsize}",
            "&&",
            "snakemake",
            "--snakefile",
            "Snakefile.windowed_variation",
            "--report",
            '/mnt/windowed_variation_report.html"',
        ]
    )

    output = subprocess.run(
        [
            "docker",
            "run",
            "-v",
            f"{local_folder}",
            f"hard_sweeps_windowed_variation:{tag}",
            "/bin/bash",
            "-c",
            f'"{snakemake_cmd}"',
        ],
        capture_output=True,
    )
    handle_return_value(output, log=True)

    logging.info(
        f"Removing temporary docker image hard_sweeps_windowed_variation:{tag}."
    )
    output = subprocess.run(
        ["docker", "image", "rm", "-f", f"hard_sweeps_windowed_variation:{tag}"],
        capture_output=True,
    )
    handle_return_value(output)
    logging.info("Done!")


def kim_stephan_fig4(args):
    tag = set_tag(args)
    setup_logging("kim_stephan_fig4.txt")
    logging.info(f"Building temporary docker image kim_stephan_fig4:{tag}.")
    output = subprocess.run(
        [
            "docker",
            "build",
            "--build-arg",
            f"tag={tag}",
            ".",
            "-t",
            f"kim_stephan_fig4:{tag}",
        ],
        capture_output=True,
    )
    handle_return_value(output)

    logging.info("Running Snakefile.")

    local_folder = os.getcwd() + ":/mnt"

    snakemake_cmd = " ".join(
        [
            '"snakemake',
            "--snakefile",
            "Snakefile.kim_stephan_fig4",
            "-j",
            str(args.cores),
            "--config",
            f"nreps={args.nreps}",
            # f"popsize={args.popsize}",
            "&&",
            "snakemake",
            "--snakefile",
            "Snakefile.kim_stephan_fig4",
            "--report",
            '/mnt/sfs_report.html"',
        ]
    )

    output = subprocess.run(
        [
            "docker",
            "run",
            "-v",
            f"{local_folder}",
            f"kim_stephan_fig4:{tag}",
            "/bin/bash",
            "-c",
            f'"{snakemake_cmd}"',
        ],
        capture_output=True,
    )
    handle_return_value(output, log=True)

    logging.info(f"Removing temporary docker image kim_stephan_fig4:{tag}.")
    output = subprocess.run(
        ["docker", "image", "rm", "-f", f"kim_stephan_fig4:{tag}"], capture_output=True
    )
    handle_return_value(output)
    logging.info("Done!")


def make_parser():
    parser = argparse.ArgumentParser(
        description='Generate reports for classic ("hard"/complete) sweep models.',
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

    subparsers = parser.add_subparsers(dest="subparser", required=True)

    sfs_parser = subparsers.add_parser("sfs")
    sfs_parser.set_defaults(func=run_sfs)
    windowed_variation_parser = subparsers.add_parser("windowed_variation")
    windowed_variation_parser.set_defaults(func=run_windowed_variation)

    for i in [sfs_parser, windowed_variation_parser]:
        i.add_argument(
            "--popsize", "-N", type=int, default=1000, help="Diploid population size"
        )

    kim_stephan_fig4_parser = subparsers.add_parser("kimstephanfig4")
    kim_stephan_fig4_parser.set_defaults(func=kim_stephan_fig4)

    return parser


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args(sys.argv[1:])

    args.func(args)
