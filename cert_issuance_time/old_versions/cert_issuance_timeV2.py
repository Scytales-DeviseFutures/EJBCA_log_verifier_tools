import re
from datetime import datetime
import argparse

def extract_user_logs(log_file):
    user_logs = {}
    with open(log_file, 'r') as file:
        for line in file:
            if ";SUCCESS;" in line:
                log_time_match = re.search(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3}', line)
                if log_time_match:
                    log_time = datetime.strptime(log_time_match.group(), '%Y-%m-%d %H:%M:%S,%f')
                    millisec = int(log_time.timestamp() * 1000)
                    log_type = line.split(";")[1]
                    if log_type == "CA_USERAUTH":
                        start_index = line.find(";;") + 2
                        end_index = line.find(";", start_index)
                        if start_index != -1 and end_index != -1:
                            user_id = line[start_index:end_index]
                            if user_id not in user_logs:
                                user_logs[user_id] = []
                            user_logs[user_id].append((millisec, f"{millisec}-u"))  # Adiciona o tempo e a letra 'u' ao tipo de log
                    elif log_type == "CERT_REQUEST":
                        user_id = line.split(";")[8]
                        if user_id not in user_logs:
                            user_logs[user_id] = []
                        user_logs[user_id].append((millisec, f"{millisec}-r"))  # Adiciona o tempo e a letra 'r' ao tipo de log
                    elif log_type == "CERT_STORED":
                        user_id = line.split(";")[8]
                        if user_id not in user_logs:
                            user_logs[user_id] = []
                        user_logs[user_id].append((millisec, f"{millisec}-s"))  # Adiciona o tempo e a letra 's' ao tipo de log
                    elif log_type == "CERT_CREATION":
                        user_id = line.split(";")[8]
                        if user_id not in user_logs:
                            user_logs[user_id] = []
                        user_logs[user_id].append((millisec, f"{millisec}-c"))  # Adiciona o tempo e a letra 'c' ao tipo de log
            elif "to STATUS_GENERATED." in line:
                status_generated_match = re.search(r" '(.+?)' to STATUS_GENERATED", line)
                if status_generated_match:
                    user_id = status_generated_match.group(1)
                    if user_id not in user_logs:
                        user_logs[user_id] = []
                    log_time_match = re.search(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3}', line)
                    if log_time_match:
                        log_time = datetime.strptime(log_time_match.group(), '%Y-%m-%d %H:%M:%S,%f')
                        millisec = int(log_time.timestamp() * 1000)
                        user_logs[user_id].append((millisec, f"{millisec}-g"))  # Adiciona o tempo e a letra 'g' ao tipo de log
    return user_logs


def write_output_to_file(user_logs, output_file):
    with open(output_file, 'w') as file:
        for user_id, logs in user_logs.items():
            file.write(f"--- User ID: {user_id} ---\n")
            log_times = [f"{log[0]}{log[1]}" for log in logs]  # Adiciona o tempo e a letra ao log
            file.write(f"Log Times: {log_times}\n")

def main():
    # Create ArgumentParser object
    parser = argparse.ArgumentParser(description='Extract user logs from log file and write to output file')

    # Add arguments
    parser.add_argument('-in', dest='input_file', help='Input log file', required=True)
    parser.add_argument('-out', dest='output_file', help='Output file', required=True)

    # Parse arguments
    args = parser.parse_args()

    # Extract user logs from input file
    user_logs = extract_user_logs(args.input_file)

    # Write output to output file
    write_output_to_file(user_logs, args.output_file)

    print("Output has been written to", args.output_file)

if __name__ == "__main__":
    main()
