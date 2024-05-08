import re
from datetime import datetime
import argparse
import re
from datetime import datetime

from collections import defaultdict

def extract_user_logs(log_file):
    user_logs = defaultdict(lambda: defaultdict(int))

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

    return user_logs

def extract_stats(log_file):
    user_logs = defaultdict(lambda: defaultdict(int))
    tempos_emissao = defaultdict(list)

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
                            user_logs[user_id][log_type] += millisec
                            tempos_emissao[user_id].append(millisec)
                    elif log_type == "STATUS_GENERATED":
                        status_generated_match = re.search(r" '(.+?)' to STATUS_GENERATED", line)
                        if status_generated_match:
                            user_id = status_generated_match.group(1)
                            tempos_emissao[user_id].append(millisec)

    return tempos_emissao

def calculate_time_statistics(tempos_emissao):
    tempos_minimos = {}
    tempos_maximos = {}
    num_certificados = 0

    for user_id, tempos in tempos_emissao.items():
        if tempos:
            tempos_minimos[user_id] = min(tempos)
            tempos_maximos[user_id] = max(tempos)
            num_certificados += len(tempos)

    tempo_minimo = min(tempos_minimos.values()) if tempos_minimos else 0
    tempo_maximo = max(tempos_maximos.values()) if tempos_maximos else 0

    tempo_total = sum(sum(tempos) for tempos in tempos_emissao.values())
    tempo_medio = tempo_total / num_certificados if num_certificados > 0 else 0

    return num_certificados, tempo_minimo, tempo_maximo, tempo_medio



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

def write_output_to_file(user_logs, num_certificados, tempo_minimo, tempo_maximo, tempo_medio, output_file, sep):
    with open(output_file, 'w') as file:
        file.write("User"+sep+"Request"+sep+"Stored"+sep+"Creation"+sep+"Generated\n")
        for user_id, logs in user_logs.items():
            file.write(f"\n{user_id}")
            for log_type, total_time in logs.items():
                if int(total_time) < 0:
                    file.write(f"{sep}-")
                else:
                    file.write(f"{sep}{total_time}")
        
        file.write("\n\nCerts"+sep+"min"+sep+"max"+sep+"avg")
        file.write(f"\n{num_certificados}{sep}{tempo_minimo}{sep}{tempo_maximo}{sep}{tempo_medio}")

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
    user_logs = extract_user_logs(args.input_file)

    user_logs = calculate_time_differences(user_logs)

    tempos_emissao = extract_stats(args.input_file)
    num_certificados, tempo_minimo, tempo_maximo, tempo_medio = calculate_time_statistics(tempos_emissao)

    # Write output to output file
    write_output_to_file(user_logs, num_certificados, tempo_minimo, tempo_maximo, tempo_medio, args.output_file, args.sep)

    print("Output has been written to", args.output_file)

if __name__ == "__main__":
    main()
