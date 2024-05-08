import re
from datetime import datetime
import argparse
import re
from datetime import datetime

from collections import defaultdict

def extract_user_logs(log_file):
    user_logs = defaultdict(lambda: defaultdict(int))
    aux = 0
    with open(log_file, 'r') as file:
        for line in file:
            if ";SUCCESS;" in line:
                log_time_match = re.search(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3}', line)
                if log_time_match:
                    log_time = datetime.strptime(log_time_match.group(), '%Y-%m-%d %H:%M:%S,%f')
                    millisec = int(log_time.timestamp() * 1000)
                    log_type = line.split(";")[1]

                    if log_type == "CA_USERAUTH":
                        aux += 1
                        start_index = line.find(";;") + 2
                        end_index = line.find(";", start_index)
                        if start_index != -1 and end_index != -1:
                            user_id = line[start_index:end_index]
                            user_logs[user_id][log_type] += millisec
                    elif log_type in ["CERT_REQUEST", "CERT_STORED", "CERT_CREATION"]:
                        user_id = line.split(";")[8]
                        user_logs[user_id][log_type] += millisec
            elif "to STATUS_GENERATED." in line:
                status_generated_match = re.search(r" '(.+?)' to STATUS_GENERATED", line)
                if status_generated_match:
                    user_id = status_generated_match.group(1)
                    log_time_match = re.search(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3}', line)
                    if log_time_match:
                        log_time = datetime.strptime(log_time_match.group(), '%Y-%m-%d %H:%M:%S,%f')
                        millisec = int(log_time.timestamp() * 1000)
                        user_logs[user_id]["STATUS_GENERATED"] += millisec

    return user_logs, aux

def calculate_time_differences(accumulated_logs):
    time_differences = defaultdict(dict)
    for user_id, logs in accumulated_logs.items():
        if 'CA_USERAUTH' in logs:
            ca_time = logs['CA_USERAUTH']
            time_differences[user_id]['CERT_REQUEST'] = logs.get('CERT_REQUEST', 0) - ca_time
            time_differences[user_id]['CERT_STORED'] = logs.get('CERT_STORED', 0) - ca_time
            time_differences[user_id]['CERT_CREATION'] = logs.get('CERT_CREATION', 0) - ca_time
            time_differences[user_id]['STATUS_GENERATED'] = logs.get('STATUS_GENERATED', 0) - ca_time

    return time_differences

def write_output_to_file(user_logs, aux, output_file, sep):
    with open(output_file, 'w') as file:
        file.write("User;Request;Stored;Creation;Generated\n")
        for user_id, logs in user_logs.items():
            file.write(f"\n{user_id}")
            for log_type, total_time in logs.items():
                if int(total_time) < 0:
                    file.write(f"{sep}-")
                else:
                    file.write(f"{sep}{total_time}")
        
        file.write("\n\nCerts;min;max;avg")
        file.write(f"\n {aux}")

def main():
    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description='Extract user logs from log file and write to output file')

    # Add arguments
    parser.add_argument('-in', dest='input_file', help='Input log file', required=True)
    parser.add_argument('-out', dest='output_file', help='Output file', required=True)
    parser.add_argument('-sep', dest='sep', help='sep file', required=True)

    # Parse arguments
    args = parser.parse_args()

    # Extract user logs from input file
    user_logs, aux = extract_user_logs(args.input_file)

    user_logs = calculate_time_differences(user_logs)

    # Write output to output file
    write_output_to_file(user_logs, aux, args.output_file, args.sep)

    print("Output has been written to", args.output_file)

if __name__ == "__main__":
    main()
