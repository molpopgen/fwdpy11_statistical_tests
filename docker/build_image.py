import argparse
import logging
import sys
import subprocess

logging.basicConfig(
    filename="logfile.txt",
    filemode="w",
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)


def make_parser():
    parser = argparse.ArgumentParser(
        description="Build the base docker image",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--tag",
        "-t",
        type=str,
        default=None,
        help="Use one of the images from Docker hub. Valid values are 'stable' or 'latest'. The default of None will mean that the 'stable' tag will be used.",
    )

    return parser


if __name__ == "__main__":
    parser = make_parser()
    args = parser.parse_args(sys.argv[1:])

    if args.tag is None:
        tag = "stable"
    else:
        tag = args.tag

    logging.info(f"Building base docker image fwdpy11_statistical_tests:{tag}")

    output = subprocess.run(
        [
            "docker",
            "build",
            "--build-arg",
            f"tag={tag}",
            ".",
            "-t",
            f"fwdpy11_statistical_tests:{tag}",
        ],
        capture_output=True,
    )
    if output.returncode != 0:
        logging.error(output.stderr.decode("utf8").rstrip())
        sys.exit(1)

    logging.info("Finished building base docker image.")
