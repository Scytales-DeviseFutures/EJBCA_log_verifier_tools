import re
import argparse
from datetime import datetime
from collections import defaultdict

def extract_user_logs(log_file):
    user_logs = defaultdict(lambda: defaultdict(list))
    current_log_set = defaultdict(int)  # Contador para o conjunto de logs atual de cada usuário
    current_user_id = None  # Último ID de usuário encontrado
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
                            user_logs[user_id][current_log_set[user_id]].append((log_type, millisec))
                            current_user_id = user_id
                    elif log_type in ["CERT_REQUEST", "CERT_STORED", "CERT_CREATION"]:
                        user_id = line.split(";")[8]
                        user_logs[user_id][current_log_set[user_id]].append((log_type, millisec))
                        current_user_id = user_id
            elif "to STATUS_GENERATED." in line:
                status_generated_match = re.search(r" '(.+?)' to STATUS_GENERATED", line)
                if status_generated_match:
                    user_id = status_generated_match.group(1)
                    log_time_match = re.search(r'\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2},\d{3}', line)
                    if log_time_match:
                        log_time = datetime.strptime(log_time_match.group(), '%Y-%m-%d %H:%M:%S,%f')
                        millisec = int(log_time.timestamp() * 1000)
                        user_logs[user_id][current_log_set[user_id]].append(("STATUS_GENERATED", millisec))
                        current_log_set[user_id] += 1  # Incrementa o contador para criar um novo conjunto de logs para este usuário
                        current_user_id = None

    return user_logs





def write_output_to_file(user_logs, output_file):
    with open(output_file, 'w') as file:
        for user_id, logs in user_logs.items():
            file.write(f"--- User ID: {user_id} ---\n")
            for log_index, log_entries in logs.items():
                file.write(f"Log Set {log_index}:\n")
                ca_userauth_time = None
                cert_request_time = None
                cert_stored_time = None
                cert_creation_time = None
                status_generated_time = None
                for log_type, log_time in log_entries:
                    if log_type == "CA_USERAUTH":
                        ca_userauth_time = log_time
                    elif log_type == "CERT_REQUEST":
                        cert_request_time = log_time
                    elif log_type == "CERT_STORED":
                        cert_stored_time = log_time
                    elif log_type == "CERT_CREATION":
                        cert_creation_time = log_time
                    elif log_type == "STATUS_GENERATED":
                        status_generated_time = log_time
                
                if ca_userauth_time:
                    file.write(f"User ID: {user_id}\n")
                    file.write(f"Cert_Request - CA_Userauth: {cert_request_time - ca_userauth_time if cert_request_time else 'N/A'}\n")
                    file.write(f"Cert_Stored - CA_Userauth: {cert_stored_time - ca_userauth_time if cert_stored_time else 'N/A'}\n")
                    file.write(f"Cert_Creation - CA_Userauth: {cert_creation_time - ca_userauth_time if cert_creation_time else 'N/A'}\n")
                    file.write(f"Status_Generated - CA_Userauth: {status_generated_time - ca_userauth_time if status_generated_time else 'N/A'}\n")
            file.write("\n")



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
    print(user_logs['2024-04-18-1-0000001'])

    # Write output to output file
    write_output_to_file(user_logs, args.output_file)

    print("Output has been written to", args.output_file)

if __name__ == "__main__":
    main()
