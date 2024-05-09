# EJBCA_log_verifier_tools
Tools to verify EJBCA logs

This is a Python utility to extract specific information from log files and generate a formatted output file.

# Installation

1. Clone the repository

2. Navigate to the project directory:

    Windows:
    ```shell
    cd cert_issuance_time\final
    ```

    Linux:
    ```shell
    cd cert_issuance_time/final
    ```

# Usage
The cert_issuance_time.py script is used to extract information from log files. It accepts the following command-line arguments:

    -in, --input_file: Path to the input log file.
    -out, --output_file: Path to the output file where the extracted information will be stored.
    -sep, --separator: Delimiter used to separate fields in the log file.

Example usage:  
    ```shell
    python cert_issuance_time.py -in server.log.2024-04-18 -out outfile.txt -sep ";"
    ```

This command will extract information from the input_log.txt file, using ";" as the field delimiter, and generate an output file named  output.txt.

#   Notes

Inside the "cert_issuance_time" folder, there are two folders: "final" and "old_versions." As the name suggests, within the "final" folder, we have the latest version of the extractor, and within the "old_versions" folder, there are older versions that were developed before reaching the "final" version.






