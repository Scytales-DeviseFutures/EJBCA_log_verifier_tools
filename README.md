# EJBCA_log_verifier_tools
Tools to verify EJBCA logs

This is a Python utility to extract specific information from log files and generate a formatted output file.

# Installation

1. Clone the repository

2. Navigate to the project directory:

Windows:

    cd cert_issuance_time\final


Linux:

    cd cert_issuance_time/final


# Usage
The cert_issuance_time.py script is used to extract information from log files. It accepts the following command-line arguments:

    -in, --input_file: Path to the input log file.
    -out, --output_file: Path to the output file where the extracted information will be stored.
    -sep, --separator: Delimiter used to separate fields in the log file.

Example usage:  

    python cert_issuance_time.py -in input_log.txt -out output.txt -sep ";"

This command will extract information from the input_log.txt file, using ";" as the field delimiter, and generate an output file named  output.txt.

# Results
(";" was used as the parameter for -sep.)

The output file is divided into two parts. The first part contains all issuances performed by all users, where they are divided by:

User;Request;Stored;Creation;Generated

* The first entry is the user ID.
* The second entry is the time difference (in milliseconds) between CERT_REQUEST and CA_USERAUTH (relative to the user ID).
* The third entry is the time difference (in milliseconds) between CERT_STORED and CA_USERAUTH (relative to the user ID).
* The fourth entry is the time difference (in milliseconds) between CERT_CREATION and CA_USERAUTH (relative to the user ID).
* Finally, the fifth entry is the time difference (in milliseconds) between STATUS_GENERATED and CA_USERAUTH (relative to the user ID), which represents the type of certificate issuance.

Example:

    2024-04-18-0000001;28;55;60;70
    

The last two lines contain:

    Certs;min;max;avg
    A;B;C;D
    

where:
* A - number of certificates processed
* B - minimum issuance time (in milliseconds) of the processed certificates
* C - maximum issuance time (in milliseconds) of the processed certificates
* D - average issuance time (in milliseconds) of the processed certificates

#   Notes

Inside the "cert_issuance_time" folder, there are two folders: "final" and "old_versions." 
As the name suggests, within the "final" folder, we have the latest version of the extractor, and within the "old_versions" folder, there are older versions that were developed before reaching the "final" version.






