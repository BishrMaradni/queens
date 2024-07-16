"""Main module to start a dask jobqueue cluster."""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

from queens.schedulers.cluster_scheduler import VALID_WORKLOAD_MANAGERS
from queens.utils.logger_settings import setup_basic_logging
from queens.utils.valid_options_utils import get_option

_logger = logging.getLogger(__name__)


def parse_arguments(unparsed_args):
    """Parse arguments passed via command line call."""
    parser = argparse.ArgumentParser(description="Arguments for the dask cluster starting routine")

    parser.add_argument("--workload-manager", help="type of workload manager (e.g., slurm or pbs)")

    parser.add_argument(
        "--dask-cluster-kwargs", help="keyword arguments for dask cluster in JSON format"
    )
    parser.add_argument(
        "--dask-cluster-adapt-kwargs",
        help="keyword arguments for dask cluster adapt method in JSON format",
    )

    parser.add_argument("--experiment-dir", help="Directory of QUEENS experiment on remote")

    parser.add_argument("--debug", default=False, help="flag to control on debug mode")

    return parser.parse_args(unparsed_args)


# Main program
if __name__ == "__main__":
    # Parsing the arguments
    args = parse_arguments(sys.argv[1:])
    experiment_dir = Path(args.experiment_dir)

    log_file_path = experiment_dir / "dask_cluster.log"
    setup_basic_logging(log_file_path=log_file_path, logger=_logger, debug=args.debug)

    # Parsing the JSON arguments
    try:
        dask_cluster_kwargs = json.loads(args.dask_cluster_kwargs)
    except json.JSONDecodeError:
        _logger.error("Invalid JSON argument for dask cluster keyword args:")
        _logger.error(args.dask_cluster_kwargs)
        sys.exit(1)

    try:
        dask_cluster_adapt_kwargs = json.loads(args.dask_cluster_adapt_kwargs)
    except json.JSONDecodeError:
        _logger.error("Invalid JSON argument for dask cluster adapt keyword args:")
        _logger.error(args.dask_cluster_adapt_kwargs)
        sys.exit(1)

    dask_cluster_options = get_option(VALID_WORKLOAD_MANAGERS, args.workload_manager)
    dask_cluster_cls = dask_cluster_options["dask_cluster_cls"]

    _logger.info("Starting event loop")
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        _logger.info("Starting dask cluster of type: %s", dask_cluster_cls)
        _logger.debug("Dask cluster kwargs:")
        _logger.debug(dask_cluster_kwargs)
        cluster = dask_cluster_cls(**dask_cluster_kwargs)

        _logger.info("Adapting dask cluster settings")
        _logger.debug("Dask cluster adapt kwargs:")
        _logger.debug(dask_cluster_adapt_kwargs)
        cluster.adapt(**dask_cluster_adapt_kwargs)

        _logger.info("Dask cluster info:")
        _logger.info(cluster)

        dask_jobscript = experiment_dir / "dask_jobscript.sh"
        _logger.info("Writing dask jobscript to:")
        _logger.info(dask_jobscript)
        dask_jobscript.write_text(str(cluster.job_script()))

        loop.run_forever()
    except KeyboardInterrupt:
        _logger.info("Caught keyboard interrupt")
    finally:
        _logger.info("Closing event loop")
        loop.close()
