import contextlib
import io
import unittest

import scanner
import categoriser
import planner
import executor
import logger
import config
import cli
import system_logger
import display
import duplicates
import undo
import history
import tests


def run_self_check() -> bool:
    """Run the automated test suite and report whether it all passed."""
    suite = unittest.TestLoader().loadTestsFromModule(tests)
    with contextlib.redirect_stdout(io.StringIO()):
        result = unittest.TextTestRunner(verbosity=0).run(suite)
    return result.wasSuccessful()


def main() -> None:
    """Run the file organiser: parse arguments, then organise or undo."""
    system_logger.setup_logger()
    system_logger.info("Application Started")
    display.print_welcome()

    args = cli.parse_args()
    folder = args.folder

    config_data = config.load_config()
    show_summary = config_data["show_summary"]
    run_tests_enabled = config_data["run_tests"]

    if run_tests_enabled:
        system_logger.info("Running self-check test suite")
        if not run_self_check():
            display.print_error("Self-check failed, aborting.")
            system_logger.error("Self-check failed")
            return

    if args.undo:
        operations = history.load_history(folder)

        if operations is None:
            display.print_error("No undo history found")
        else:
            undone = undo.undo_operations(folder, operations)
            display.print_undo_result(undone)

            if undone > 0:
                history.clear_history(folder)

        return

    if args.prefix is None:
        prefix = config_data["default_prefix"]
    else:
        prefix = args.prefix

    system_logger.info("Scanning folder...")
    files = scanner.scan_folder(folder)

    if files is None:
        display.print_error("Folder not found")
        system_logger.error("Folder not found")
    else:
        system_logger.info(f"Found {len(files)} files")

        if args.check_duplicates:
            duplicate_files = duplicates.find_duplicates(folder)

            if duplicate_files:
                display.print_duplicates(duplicate_files)

        categories = categoriser.categorise_files(files)

        if show_summary:
            display.print_file_count(len(files))
            display.print_categories(categories)

        operations = planner.build_operations(files, prefix)
        display.print_operations(operations)

        if args.dry_run:
            print("Dry run - no changes made.")

        elif display.confirm_action("Proceed with rename?", auto_confirm=args.no_confirm):
            system_logger.info("Executing rename plan")

            rename_result = executor.execute_plan(folder, operations)
            display.print_execution_report(rename_result)

            log_path = logger.create_log_file()
            logger.write_execution_log(log_path, folder, operations, rename_result)
            display.print_log_saved(log_path)

            history.save_history(folder, rename_result["successful_operations"])

            system_logger.info("Execution complete")

            if show_summary:
                files = scanner.scan_folder(folder)
                display.print_heading("NEW FOLDER CONTENTS")
                display.print_files(files)

if __name__ == "__main__":
    main()