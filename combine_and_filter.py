import os
import csv
from datetime import datetime

# Specify the directory containing .wiglecsv and .csv files
input_directory = 'path/to/your/directory'
output_file_base = 'combined_output'

# Latitude and longitude bounds for filtering
lat_min, lat_max = 35.0, 42.0
lon_min, lon_max = -120.0, -110.0

# SSIDs to omit
ssids_to_omit = ['ssid1', 'ssid2']

# Timestamp bounds for filtering (in 'YYYY-MM-DD HH:MM:SS' format)
timestamp_start = '2023-01-01 00:00:00'
timestamp_end = '2023-12-31 23:59:59'

def is_within_bounds(lat, lon):
    return lat_min <= lat <= lat_max and lon_min <= lon <= lon_max

def is_within_timestamp_range(timestamp_str, start_str, end_str):
    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
    start = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S')
    end = datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S')
    return start <= timestamp <= end

def combine_and_filter_csv_files(input_directory, output_file_base):
    header_row_1 = None
    header_row_2 = None
    combined_data = []
    total_rows_parsed = 0
    rows_omitted = 0

    for root, _, files in os.walk(input_directory):
        for filename in files:
            if filename.endswith('.wiglecsv') or filename.endswith('.csv'):
                filepath = os.path.join(root, filename)
                print(f"Processing file: {filepath}")
                with open(filepath, 'r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    try:
                        file_header_row_1 = next(reader)
                        file_header_row_2 = next(reader)
                    except StopIteration:
                        print(f"File {filename} is empty or does not have the correct header rows.")
                        continue

                    if header_row_1 is None and header_row_2 is None:
                        header_row_1 = file_header_row_1
                        header_row_2 = file_header_row_2
                    elif header_row_1 != file_header_row_1 or header_row_2 != file_header_row_2:
                        print(f"Header mismatch in file: {filename}")
                        continue

                    try:
                        lat_index = header_row_2.index("CurrentLatitude")
                        lon_index = header_row_2.index("CurrentLongitude")
                        ssid_index = header_row_2.index("SSID")
                        timestamp_index = header_row_2.index("FirstSeen")
                    except ValueError as e:
                        print(f"Error finding necessary columns in file: {filename} - {e}")
                        continue
                    
                    for row in reader:
                        total_rows_parsed += 1
                        if len(row) <= max(lat_index, lon_index, ssid_index, timestamp_index):
                            print(f"Row with insufficient columns in file: {filename} - {row}")
                            rows_omitted += 1
                            continue

                        try:
                            lat = float(row[lat_index])
                            lon = float(row[lon_index])
                            ssid = row[ssid_index]
                            timestamp = row[timestamp_index]
                        except ValueError as e:
                            print(f"Error converting data in file: {filename} - {row} - {e}")
                            rows_omitted += 1
                            continue

                        if (is_within_bounds(lat, lon) and 
                            ssid not in ssids_to_omit and 
                            is_within_timestamp_range(timestamp, timestamp_start, timestamp_end)):
                            combined_data.append(row)
                        else:
                            rows_omitted += 1

    if header_row_1 and header_row_2:
        timestamp_str = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"{output_file_base}_{timestamp_str}.wiglecsv"

        with open(output_file, 'w', newline='', encoding='utf-8') as output_csv:
            writer = csv.writer(output_csv)
            writer.writerow(header_row_1)
            writer.writerow(header_row_2)
            writer.writerows(combined_data)

        rows_included = total_rows_parsed - rows_omitted
        print(f"Total rows parsed: {total_rows_parsed}")
        print(f"Rows omitted: {rows_omitted}")
        print(f"Rows included in final file: {rows_included}")
    else:
        print("No valid header rows found, no output file created.")

combine_and_filter_csv_files(input_directory, output_file_base)
