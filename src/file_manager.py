"""
=========================================================
STL OPTIMIZER

File Manager

Automatically searches for STL files within the
working directory.

Compatible with:
    Windows
    Linux
    SteamOS

Author:
    Jose María Beltrán Díaz
=========================================================
"""

from pathlib import Path

from config_API import (
    OUTPUT_SUFFIX,
    SEARCH_SUBDIRECTORIES,
    SAVE_MODE,
    SaveMode,
    OUTPUT_FOLDER,
    INPUT_FOLDER,
    RESULTS_FOLDER,
    LOG_SUFFIX,
    CONVEX_HULL_STL_SUFFIX,
    CONVEX_HULL_IMAGE_SUFFIX
)


class FileManager:
    """
    Manages the search, output paths and report paths for
    STL files located within the configured working
    directory.
    """

    # ---------------------------------------------------------

    def __init__(self, directory=None):
        """
        Initializes the file manager.

        Parameters
        ----------
        directory : str or pathlib.Path, optional
            Directory containing the STL files.

            If no directory is supplied, the configured
            INPUT_FOLDER directory located in the current
            working directory is used.
        """

        if directory is None:

            self.directory = (
                Path.cwd()
                / INPUT_FOLDER
            )

        else:

            self.directory = Path(
                directory
            )

        self.directory = (
            self.directory
            .expanduser()
            .resolve()
        )

        if not self.directory.exists():

            raise FileNotFoundError(
                "The input directory was not found: "
                f"'{self.directory}'."
            )

        if not self.directory.is_dir():

            raise NotADirectoryError(
                "The configured input path is not a "
                f"directory: '{self.directory}'."
            )

    # ---------------------------------------------------------

    def working_directory(self):
        """
        Returns the STL input directory.
        """

        return self.directory

    # ---------------------------------------------------------

    @staticmethod
    def is_stl(file):
        """
        Checks whether a path points to an STL file.
        """

        file = Path(
            file
        )

        return (
            file.is_file()
            and file.suffix.lower() == ".stl"
        )

    # ---------------------------------------------------------

    @staticmethod
    def already_processed(file):
        """
        Checks whether an STL file name already contains the
        configured optimized-file suffix.
        """

        file = Path(
            file
        )

        return file.stem.lower().endswith(
            OUTPUT_SUFFIX.lower()
        )

    # ---------------------------------------------------------

    def stl_files(self):
        """
        Returns all unprocessed STL files found in the input
        directory.

        If SEARCH_SUBDIRECTORIES is enabled, all
        subdirectories are traversed recursively.
        """

        files = []

        if SEARCH_SUBDIRECTORIES:

            iterator = self.directory.rglob(
                "*"
            )

        else:

            iterator = self.directory.iterdir()

        for file in iterator:

            if not self.is_stl(file):
                continue

            if self.already_processed(file):
                continue

            files.append(
                file.resolve()
            )

        files.sort(
            key=lambda path: str(
                path
            ).lower()
        )

        return files

    # ---------------------------------------------------------

    def file_count(self):
        """
        Returns the number of STL files found.
        """

        return len(
            self.stl_files()
        )

    # ---------------------------------------------------------

    def has_files(self):
        """
        Checks whether there are STL files to process.
        """

        return self.file_count() > 0

    # ---------------------------------------------------------

    def relative_parent(self, input_file):
        """
        Returns the relative parent directory of an STL file
        inside the configured input folder.

        This allows the original subdirectory structure to
        be preserved when recursive searching is enabled.
        """

        input_file = (
            Path(input_file)
            .expanduser()
            .resolve()
        )

        try:

            relative_file = input_file.relative_to(
                self.directory
            )

        except ValueError as error:

            raise ValueError(
                "The input STL file is outside the configured "
                f"input directory: '{input_file}'."
            ) from error

        return relative_file.parent

    # ---------------------------------------------------------

    def results_directory(self):
        """
        Creates and returns the main results directory.
        """

        results = (
            Path.cwd()
            / RESULTS_FOLDER
        )

        results.mkdir(
            parents=True,
            exist_ok=True
        )

        return results.resolve()

    # ---------------------------------------------------------

    def general_output_directory(self):
        """
        Creates and returns the configured general output
        directory.

        This directory is used when SAVE_MODE is
        SaveMode.OUTPUT_FOLDER.
        """

        output = (
            Path.cwd()
            / OUTPUT_FOLDER
        )

        output.mkdir(
            parents=True,
            exist_ok=True
        )

        return output.resolve()

    # ---------------------------------------------------------

    def file_results_folder(self, input_file):
        """
        Creates and returns the individual results folder
        associated with an STL file.

        Example
        -------

        Input:

            Optimizable Mesh/
                Piece.stl

        Output:

            Results/
                Piece/
        """

        input_file = (
            Path(input_file)
            .expanduser()
            .resolve()
        )

        relative_parent = self.relative_parent(
            input_file
        )

        folder = (
            self.results_directory()
            / relative_parent
            / input_file.stem
        )

        folder.mkdir(
            parents=True,
            exist_ok=True
        )

        return folder.resolve()

    # ---------------------------------------------------------

    def output_directory(self, input_file):
        """
        Returns the directory where the optimized STL will
        be saved according to SAVE_MODE.

        SaveMode.SAME_FOLDER
            Saves the optimized STL beside the original STL.

        SaveMode.OUTPUT_FOLDER
            Saves the optimized STL inside OUTPUT_FOLDER.

        SaveMode.RESULTS_FOLDER
            Saves the optimized STL directly inside
            RESULTS_FOLDER.

        SaveMode.RESULTS_SUBFOLDER
            Saves the optimized STL inside a specific folder
            created for the original STL.
        """

        input_file = (
            Path(input_file)
            .expanduser()
            .resolve()
        )

        if SAVE_MODE == SaveMode.SAME_FOLDER:

            output = input_file.parent

        elif SAVE_MODE == SaveMode.OUTPUT_FOLDER:

            output = (
                self.general_output_directory()
                / self.relative_parent(input_file)
            )

        elif SAVE_MODE == SaveMode.RESULTS_FOLDER:

            output = (
                self.results_directory()
                / self.relative_parent(input_file)
            )

        elif SAVE_MODE == SaveMode.RESULTS_SUBFOLDER:

            output = self.file_results_folder(
                input_file
            )

        else:

            raise ValueError(
                f"Unsupported save mode: '{SAVE_MODE}'."
            )

        output.mkdir(
            parents=True,
            exist_ok=True
        )

        return output.resolve()

    # ---------------------------------------------------------

    def report_directory(self, input_file):
        """
        Returns the directory where the optimization report
        will be saved.

        When RESULTS_SUBFOLDER is selected, the report is
        stored beside the optimized STL.

        For all other modes, reports are stored in the
        individual results folder associated with each STL.
        """

        input_file = (
            Path(input_file)
            .expanduser()
            .resolve()
        )

        if SAVE_MODE == SaveMode.RESULTS_SUBFOLDER:

            return self.output_directory(
                input_file
            )

        return self.file_results_folder(
            input_file
        )

    # ---------------------------------------------------------

    def output_path(self, input_file):
        """
        Returns the full path of the optimized STL.
        """

        input_file = (
            Path(input_file)
            .expanduser()
            .resolve()
        )

        filename = (
            input_file.stem
            + OUTPUT_SUFFIX
            + input_file.suffix
        )

        folder = self.output_directory(
            input_file
        )

        return folder / filename

    # ---------------------------------------------------------

    def convex_hull_stl_path(self, input_file):
        """Returns the path of the convex-hull STL artifact."""

        input_file = Path(input_file).expanduser().resolve()
        filename = input_file.stem + CONVEX_HULL_STL_SUFFIX + ".stl"
        return self.report_directory(input_file) / filename

    # ---------------------------------------------------------

    def convex_hull_image_path(self, input_file):
        """Returns the path of the convex-hull PNG visualization."""

        input_file = Path(input_file).expanduser().resolve()
        filename = input_file.stem + CONVEX_HULL_IMAGE_SUFFIX + ".png"
        return self.report_directory(input_file) / filename

    # ---------------------------------------------------------

    # ---------------------------------------------------------

    def log_path(self, input_file):
        """
        Returns the report path associated with an STL.
        """

        input_file = (
            Path(input_file)
            .expanduser()
            .resolve()
        )

        filename = (
            input_file.stem
            + LOG_SUFFIX
            + ".txt"
        )

        folder = self.report_directory(
            input_file
        )

        return folder / filename

    # ---------------------------------------------------------

    def file_output_folder(self, input_file):
        """
        Returns the folder associated with the processing
        results of an STL file.

        This compatibility method is kept because other
        modules may already call file_output_folder().
        """

        if SAVE_MODE == SaveMode.RESULTS_SUBFOLDER:

            return self.output_directory(
                input_file
            )

        return self.file_results_folder(
            input_file
        )

    # ---------------------------------------------------------

    def summary(self):
        """
        Returns a summary of the current file-search and
        output configuration.
        """

        return {
            "directory":
                self.directory,

            "recursive":
                SEARCH_SUBDIRECTORIES,

            "file_count":
                self.file_count(),

            "save_mode":
                SAVE_MODE.name,

            "output_folder":
                OUTPUT_FOLDER,

            "results_folder":
                str(
                    self.results_directory()
                )
        }

    # ---------------------------------------------------------

    def __len__(self):
        """
        Allows the use of len(file_manager).
        """

        return self.file_count()

    # ---------------------------------------------------------

    def __iter__(self):
        """
        Allows direct iteration through the STL files.

        Example
        -------

        for stl in file_manager:
            ...
        """

        return iter(
            self.stl_files()
        )

    # ---------------------------------------------------------

    def output_exists(self, input_file):
        """
        Checks whether the optimized STL already exists.
        """

        return self.output_path(
            input_file
        ).exists()