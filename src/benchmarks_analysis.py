import datetime
import os

import json
import warnings
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from pandas.core.interchange.dataframe_protocol import DataFrame
from scipy.signal import savgol_filter


class BenchmarksAnalysis:
    """
    Class for managing the analysis of benchmarks.

    This class provides functionality to handle benchmark data including loading,
    processing into a DataFrame, and generating various visual plots for performance
    analysis. It ensures proper organization of benchmark files and provides specific
    plot types to assess performance metrics and acceleration factors across a range
    of input sizes.

    :ivar benchmarks_plot_dir: Directory for storing generated benchmark plots.
    :type benchmarks_plot_dir: pathlib.Path
    :ivar test_number: The integer representation of the test identifier.
    :type test_number: int
    """

    def __init__(self, test_id: str) -> None:
        self.benchmarks_plot_dir = self.benchmarks_setup()
        self.test_number = int(test_id)

    @staticmethod
    def benchmarks_setup() -> Path:
        """
        Creates and initializes a directory for storing benchmark plots.

        This static method generates a uniquely named directory based on the current
        date and time in the "purem_benchmarks" directory relative to the script's
        location. If the directory does not already exist, it will be created. The
        directory name includes a timestamp in the format "YYYY-MM-DD_HH_MM_SS__FFF".

        :return: A `Path` object pointing to the created directory.
        :rtype: Path
        """
        current_time = datetime.datetime.now()
        benchmarks_id: str = f"""purem_benchmarks_{current_time.strftime("%Y-%m-%d_%H_%M_%S__%f")[:-4]}"""
        current_dir: str = os.path.dirname(__file__)
        benchmarks_plot_dir: Path = Path(current_dir) / "purem_benchmarks" / benchmarks_id
        os.makedirs(benchmarks_plot_dir, exist_ok=True)

        return benchmarks_plot_dir

    @staticmethod
    def extract_size_from_filepath(filepath: str) -> int:
        """
        Extract the `size` value from the given file path.
        Assumes the size is encoded as the last part before the file extension.
        """
        split_filepath = filepath.split("_")
        return int(split_filepath[-1].split(".")[0])

    def run(self) -> None:
        """
        Executes the process of generating benchmarks and acceleration plots, as well as creating
        and saving Markdown-formatted data frames. This function orchestrates the pipeline by
        calling several helper methods to handle plotting and data frame construction.

        :raises AnyRelevantError: Description of why and when it might be raised.

        :return: None
        """
        benchmarks_df = self.benchmarks_data_frame()
        self.benchmarks_plot(benchmarks_df)
        self.acceleration_plot(benchmarks_df)

        markdown_df = self.markdown_data_frame()
        self.markdown_save(markdown_df)

    def load_benchmarks_files(self) -> List[str]:
        """
        Loads benchmark files matching a specific test number from a designated directory.
        The function identifies files in the benchmarks directory that match a given test number,
        extracts a unique timestamp from the matching files, and retrieves all files that share
        the same timestamp. This ensures that all related benchmark files for a specific test are
        collected efficiently.

        :param test_number: An integer representing the test number used to filter and locate
            benchmark files. The test number will be zero-padded to ensure a four-digit format.
        :return: A list of file paths for all benchmark files associated with the specified test
            number and same timestamp.
        :rtype: List[str]
        :raises FileNotFoundError: If no benchmark files matching the specified test number
            are found in the benchmarks directory.
        """
        benchmarks_dir = ".benchmarks/Darwin-CPython-3.11-64bit"
        search_pattern = str(self.test_number).zfill(4)

        matched_files = [f for f in os.listdir(benchmarks_dir) if f.startswith(search_pattern) and f.endswith(".json")]

        if not matched_files:
            raise FileNotFoundError(f"No benchmark files found starting with {search_pattern} in {benchmarks_dir}")

        file_stamp = matched_files[0].split("_")[2]
        return [
            os.path.join(benchmarks_dir, f)
            for f in os.listdir(benchmarks_dir)
            if f.split("_")[2] == file_stamp and f.endswith(".json")
        ]

    def benchmarks_data_frame(self) -> pd.DataFrame:
        """
        Generates a Pandas DataFrame containing benchmark data extracted
        from all related files. The method processes multiple files, loads
        their content, extracts benchmark statistics, and organizes them
        into a structured tabular format.

        :param self: The instance of the class containing this method.

        :returns: A pandas DataFrame where each row represents a single
            benchmark entry. The columns include 'size', 'func', 'min',
            'max', 'mean', 'stddev', and 'ops', corresponding to the
            benchmark statistics and other metadata.
        :rtype: pd.DataFrame
        """
        files = self.load_benchmarks_files()

        records = []

        for filepath in files:
            with open(filepath, "r") as f:
                data = json.load(f)

            filepath_split = filepath.split("_")

            for entry in data["benchmarks"]:
                size = self.extract_size_from_filepath(filepath)
                func = entry["params"]["func_name"]
                stats = entry["stats"]
                records.append({
                    "size": size,
                    "func": func,
                    "min": stats["min"],
                    "max": stats["max"],
                    "mean": stats["mean"],
                    "stddev": stats["stddev"],
                    "ops": stats["ops"]
                })

        return pd.DataFrame(records)

    def benchmarks_plot(self, df: DataFrame) -> None:
        """
        Generates and saves benchmarking plots for various performance metrics.

        This function iterates over a defined list of metrics such as "min", "max", "mean",
        "stddev", and "ops", and generates two types of plots for each metric:
        one for the full range of input sizes and another for large input sizes only.
        Each plot visualizes the relationship between input sizes and metric values for all
        functions provided in the DataFrame. The x-axis is set to log scale for both
        plots. The y-axis is also set to log scale for all metrics except "stddev".
        The generated plots are saved as PNG files in a directory defined by
        `self.benchmarks_plot_dir`.

        :param df: A DataFrame containing benchmarking data. The DataFrame must have the
            following columns:
            - "func": Names of the functions being benchmarked.
            - "size": Input sizes corresponding to the benchmarks.
            - Metric columns (e.g., "min", "max", "mean", "stddev", "ops"): Values of the
              respective performance metrics.
        """
        metrics = ["min", "max", "mean", "stddev", "ops"]

        for metric in metrics:
            plt.figure(figsize=(10, 6))
            for func_name in df["func"].unique():
                data_by_func = df[df["func"] == func_name].sort_values("size")
                plt.plot(data_by_func["size"], data_by_func[metric], label=func_name, marker='o')
            plt.title(f"{metric.upper()} vs Size (Full Range)")
            plt.xlabel("Input Size")
            plt.ylabel(metric)
            plt.legend()
            plt.grid(True)
            plt.xscale("log")
            if metric != "stddev":
                plt.yscale("log")
            plt.tight_layout()
            plt.savefig(f"{self.benchmarks_plot_dir}/benchmark_{metric}_full.png")
            plt.close()

            plt.figure(figsize=(10, 6))
            for func_name in df["func"].unique():
                data_by_func = df[(df["func"] == func_name) & (df["size"] > 1e5)].sort_values("size")
                if not data_by_func.empty:
                    plt.plot(data_by_func["size"], data_by_func[metric], label=func_name, marker='o')
            plt.title(f"{metric.upper()} vs Size (Large Inputs Only)")
            plt.xlabel("Input Size (>1e5)")
            plt.ylabel(metric)
            plt.legend()
            plt.grid(True)
            plt.xscale("log")
            if metric != "stddev":
                plt.yscale("log")
            plt.tight_layout()
            plt.savefig(f"{self.benchmarks_plot_dir}/benchmark_{metric}_large.png")
            plt.close()

    def acceleration_plot(self, df: pd.DataFrame) -> None:
        """
        Plots the acceleration of the "Purem" implementation relative to other functions/libraries
        based on their performance for different input sizes. The plot shows acceleration as a
        function of the input size as a logarithmic graph, detailing the relative performance
        gain or loss.

        This function is intended to visualize and compare performance metrics for computational
        functions with respect to a "Purem" baseline. It ensures that shared input sizes
        are used for comparison and applies smoothing (Savitzky-Golay filter) to the acceleration
        curve for better interpretability.

        :param df: A pandas DataFrame containing benchmarking results with the following
            columns:
            - "func": The name of the function or library being benchmarked.
            - "size": The size of the input data for the benchmark.
            - "ops": The respective operations per second or performance metric for each
              function.

        :return: None
        """
        func_names = df["func"].unique()

        assert any("Purem" in name for name in func_names), "Purem is missed!"

        df_purem = df[df["func"].str.contains("Purem")].sort_values("size")

        plt.figure(figsize=(14, 8))

        for func_name in func_names:
            if "Purem" in func_name:
                continue

            df_other = df[df["func"] == func_name].sort_values("size")
            common_sizes = np.intersect1d(df_purem["size"], df_other["size"])

            if len(common_sizes) == 0:
                continue

            purem_ops = df_purem[df_purem["size"].isin(common_sizes)]["ops"].values
            other_ops = df_other[df_other["size"].isin(common_sizes)]["ops"].values

            acceleration = purem_ops / other_ops

            try:
                if len(acceleration) >= 5:
                    acceleration_smooth = savgol_filter(acceleration, window_length=5, polyorder=2)
                else:
                    acceleration_smooth = acceleration
            except Exception as e:
                warnings.warn(f"Smoothing skipped: {e}")
                acceleration_smooth = acceleration

            plt.plot(common_sizes, acceleration_smooth, marker='o', label=f"Purem vs {func_name}")

        plt.xscale('log')
        plt.yscale('log')
        plt.axhline(y=1, color='black', linestyle='--', linewidth=1, label='Equal Performance (x1)')
        plt.xlabel('Input Size', fontsize=14)
        plt.ylabel('Acceleration (Purem / Other)', fontsize=14)
        plt.title('Purem Acceleration Relative to Other Libraries (Production Level)', fontsize=16)
        plt.grid(True, which="both", linestyle='--', linewidth=0.6)
        plt.legend(fontsize=12)
        plt.tight_layout()
        plt.savefig(f"{self.benchmarks_plot_dir}/benchmark_acceleration_large.png")
        plt.close()

    def markdown_data_frame(self) -> pd.DataFrame:
        """
        Converts benchmark data from files into a structured pandas DataFrame.

        This method processes a collection of JSON files that contain benchmark
        results. It reads the files, extracts relevant statistical information
        about the benchmarking process, and formats this data into a structured
        pandas DataFrame. Each record in the resultant DataFrame represents a
        specific benchmark test and includes its relevant metadata and statistical
        metrics.

        :return:
            A pandas DataFrame where each row corresponds to a benchmark with
            columns that include details such as 'Elements', 'Function', 'OPS',
            'Min Time (s)', 'Max Time (s)', 'Mean Time (s)', and 'Std Dev'.
        :rtype:
            pd.DataFrame
        """
        files = self.load_benchmarks_files()

        records_markdown = []

        for filepath in files:
            with open(filepath, "r") as f:
                data = json.load(f)

            filepath_split = filepath.split("_")

            for b in data['benchmarks']:
                size = self.extract_size_from_filepath(filepath)
                func_name = b['params']['func_name']
                stats = b['stats']
                records_markdown.append({
                    "Elements": size,
                    "Function": func_name,
                    "OPS": stats["ops"],
                    "Min Time (s)": stats["min"],
                    "Max Time (s)": stats["max"],
                    "Mean Time (s)": stats["mean"],
                    "Std Dev": stats["stddev"]
                })

        return pd.DataFrame(records_markdown)

    def markdown_save(self, df: pd.DataFrame) -> None:
        """
        Saves a markdown file summarizing benchmark results in a human-readable format. The function processes
        a pandas DataFrame containing benchmark data, formats specific columns for scientific notation or fixed-point
        notation, and groups the results by the "Elements" column. Each group is written as a separate section
        in the markdown file, where the file is saved to the benchmarks directory.

        :param df: A pandas DataFrame containing benchmark results. Expected columns include "Elements",
            "OPS", "Min Time (s)", "Max Time (s)", "Mean Time (s)", and "Std Dev".
        :return: None
        """
        df = df.sort_values(by=["Elements", "OPS"], ascending=[True, False])

        df["Min Time (s)"] = df["Min Time (s)"].map(lambda x: f"{x:.2e}")
        df["Max Time (s)"] = df["Max Time (s)"].map(lambda x: f"{x:.2e}")
        df["Mean Time (s)"] = df["Mean Time (s)"].map(lambda x: f"{x:.2e}")
        df["Std Dev"] = df["Std Dev"].map(lambda x: f"{x:.2e}")
        df["OPS"] = df["OPS"].map(lambda x: f"{x:.2f}")

        grouped = df.groupby('Elements')

        with open(f"{self.benchmarks_plot_dir}/benchmarks_table.md", "w") as f:
            f.write("# Benchmark Results\n\n")
            for size, group in grouped:
                f.write(f"### Elements: {size}\n\n")
                f.write(group.drop(columns=["Elements"]).to_markdown(index=False))
                f.write("\n\n")
