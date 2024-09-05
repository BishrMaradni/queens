"""Global Settings module."""

import logging
from pathlib import Path

from queens.schedulers.dask_scheduler import SHUTDOWN_CLIENTS
from queens.utils.ascii_art import print_banner_and_description
from queens.utils.logger_settings import reset_logging, setup_basic_logging
from queens.utils.path_utils import PATH_TO_QUEENS
from queens.utils.print_utils import get_str_table
from queens.utils.run_subprocess import run_subprocess

_logger = logging.getLogger(__name__)


class GlobalSettings:
    """Class for global settings in Queens.

    Attributes:
        experiment_name (str): Experiment name of queens run
        output_dir (Path): Output directory for queens run
        git_hash (str): Hash of active git commit
        debug (bool): True if debug mode is to be used
    """

    def __init__(self, experiment_name, output_dir, debug=False):
        """Initialize global settings.

        Args:
            experiment_name (str): Experiment name of queens run
            output_dir (str, Path): Output directory for queens run
            debug (bool): True if debug mode is to be used
        """
        output_dir = Path(output_dir)
        if not output_dir.is_dir():
            raise FileNotFoundError(f"Output directory {output_dir} does not exist.")

        # Remove spaces as they can cause problems later on
        if " " in experiment_name:
            raise ValueError("Experiment name can not contain spaces!")

        self.experiment_name = experiment_name
        self.output_dir = Path(output_dir)
        self.debug = debug

        # set up logging
        log_file_path = self.result_file(".log")
        setup_basic_logging(log_file_path=log_file_path, debug=self.debug)

        return_code, _, stdout, stderr = run_subprocess(
            " ".join(["cd", f"{PATH_TO_QUEENS}", ";", "git", "rev-parse", "HEAD"]),
            raise_error_on_subprocess_failure=False,
        )
        if not return_code:
            git_hash = stdout.strip()
        else:
            git_hash = "unknown"
            _logger.warning("Could not get git hash. Failed with the following stderror:")
            _logger.warning(str(stderr))
            _logger.warning("Setting git hash to: %s!", git_hash)

        return_code, _, git_branch, stderr = run_subprocess(
            " ".join(["cd", f"{PATH_TO_QUEENS}", ";", "git", "rev-parse", "--abbrev-ref", "HEAD"]),
            raise_error_on_subprocess_failure=False,
        )
        git_branch = git_branch.strip()
        if return_code:
            git_branch = "unknown"
            _logger.warning("Could not determine git branch. Failed with the following stderror:")
            _logger.warning(str(stderr))
            _logger.warning("Setting git branch to: %s!", git_branch)

        return_code, _, git_status, stderr = run_subprocess(
            " ".join(["cd", f"{PATH_TO_QUEENS}", ";", "git", "status", "--porcelain"]),
            raise_error_on_subprocess_failure=False,
        )
        git_clean_working_tree = not git_status
        if return_code:
            git_clean_working_tree = "unknown"
            _logger.warning(
                "Could not determine if git working tree is clean. "
                "Failed with the following stderror:"
            )
            _logger.warning(str(stderr))
            _logger.warning("Setting git working tree status to: %s!", git_clean_working_tree)

        self.git_hash = git_hash
        self.git_branch = git_branch
        self.git_clean_working_tree = git_clean_working_tree

    def print_git_information(self):
        """Print information on the status of the git repository."""
        _logger.info(
            get_str_table(
                name="git information",
                print_dict={
                    "commit hash": self.git_hash,
                    "branch": self.git_branch,
                    "clean working tree": self.git_clean_working_tree,
                },
            )
        )

    def result_file(self, extension: str, suffix: str = None) -> Path:
        """Create path to a result file with a given extension.

        Args:
            extension (str): The extension of the file.
            suffix (str, optional): The suffix to be appended to the experiment_name
                                    i.e. the default stem of the filename.

        Returns:
            Path: Path of the file.
        """
        # Get the stem of the existing file name, should be the experiment_name
        file_stem = self.experiment_name

        # Append the suffix to the stem if provided
        if suffix is not None:
            file_stem += suffix

        # Create a new file name with the updated stem and provided extension
        file_name = file_stem + "." + extension.lstrip(".")

        # Create a new Path object with the updated file name
        file_path = self.output_dir / file_name

        return file_path

    def __enter__(self):
        """'enter'-function in order to use the global settings as a context.

        This function is called prior to entering the context.

        Returns:
            self
        """
        print_banner_and_description()

        return self

    def __exit__(self, exception_type, exception_value, traceback):
        """'exit'-function in order to use the global settings as a context.

        This function is called at the end of the context.

        The exception as well as traceback arguments are required to implement the `__exit__`
        method, however, we do not use them explicitly.

        Args:
            exception_type: indicates class of exception (e.g. ValueError)
            exception_value: indicates exception instance
            traceback: traceback object
        """
        for shutdown_client in SHUTDOWN_CLIENTS.copy():
            SHUTDOWN_CLIENTS.remove(shutdown_client)
            shutdown_client()

        reset_logging()
