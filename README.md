# Flow Log Parser

## Description
This program parses a flow log file and maps each row to a tag based on a lookup table. The lookup table is a CSV file containing columns for `dstport`, `protocol`, and `tag`. The combination of `dstport` and `protocol` in the flow log determines which tag, if any, should be applied. 

The program generates an output file containing:
1. The count of matches for each tag.
2. The count of matches for each port/protocol combination present in the flow log.

## Features
- **Tag Matching:** Matches each log entry to a tag based on a `dstport` and `protocol` combination from the lookup table.
- **Untagged Count:** Identifies log entries that do not match any combination in the lookup table.
- **Logging:** Uses a rotating log file to keep track of events, warnings, and errors during execution.

## Input Files
### 1. Flow Log File (`flow_logs.txt`)
- Contains log entries in the following format:
    ```
     2 123456789012 eni-0a1b2c3d 10.0.1.201 198.51.100.2 443 49153 6 25 20000 1620140761 1620140821 ACCEPT OK
    ```
- **Fields of Interest:**
- `dstport` (5th field in the log entry)
- `protocol` (7th field in the log entry, represented by a protocol number)

### 2. Lookup Table File (`lookup.csv`)
- A CSV file containing columns: `dstport`, `protocol`, `tag`.
- Example content:
    dstport,protocol,tag
    25,tcp,sv_P1
    68,udp,sv_P2
    443,tcp,sv_P2
    110,tcp,email


## Output File
The program generates an output file (`output.txt`) with the following sections:
1. **Tag Counts:** The number of times each tag is applied based on the lookup table.
2. **Port/Protocol Combination Counts:** The count of each unique port/protocol combination found in the flow logs.

### Sample Output Format
Tag Counts:
Tag,Count
sv_P2,1
sv_P1,2
email,3
Untagged,8

Port/Protocol Combination Counts:
Port,Protocol,Count
23,tcp,1
25,tcp,1
110,tcp,1
143,tcp,1
443,tcp,1
993,tcp,1
1024,tcp,1
80,tcp,1
1030,tcp,1
49152,tcp,1
49153,tcp,1
49154,tcp,1
49321,tcp,1
56000,tcp,1

## How to Use
1. **Prepare Input Files:**
   - Create a flow log file named `flow_logs.txt` in the same directory as the script.
   - Create a lookup table file named `lookup.csv` with columns: `dstport`, `protocol`, and `tag`.

2. **Run the Program:**
   - Execute the script using Python:
     ```
     python flow_log_parser.py
     ```
   - Ensure that `flow_logs.txt` and `lookup.csv` are present in the same directory as the script.

3. **Output:**
   - The program will generate an `output.txt` file containing the tag counts and port/protocol combination counts.
   - A log file named `flow_log_parser.log` will also be created, recording the program’s events.

## Dependencies
- Python 3.x
- Standard Python libraries: `csv`, `logging`, and `logging.handlers`.

## Logging
- The program uses a rotating file handler to log events, warnings, and errors to `flow_log_parser.log`.
- Logs include:
  - Information on successful processing of input files.
  - Warnings for invalid or malformed entries in the lookup table and flow logs.
  - Errors encountered during file operations.
- Log files are capped at 5 MB in size, with up to 3 backup files to avoid excessive disk usage.

## Code Overview
1. **`load_lookup_table(lookup_filename)`**:
   - Reads the lookup table from a CSV file and stores the mappings in a dictionary.
   - Normalizes protocol names to lowercase for case-insensitive matching.
   - Logs warnings for invalid entries.

2. **`get_protocol_name(protocol_number)`**:
   - Converts a protocol number (e.g., `6`) to its corresponding name (`tcp`).
   - Uses a predefined mapping of protocol numbers to names.

3. **`process_flow_log(log_filename, lookup_dict)`**:
   - Reads the flow logs line by line.
   - Extracts the `dstport` and `protocol` fields.
   - Matches each entry against the lookup table to find the appropriate tag or classify it as "Untagged."
   - Counts occurrences of tags and port/protocol combinations.
   - Logs information about each log entry's classification.

4. **`write_output(output_filename, tag_counts, port_protocol_counts)`**:
   - Writes the tag counts and port/protocol combination counts to the output file in the specified format.
   - Only includes ports/protocols found in the flow logs.

5. **`main()`**:
   - Coordinates the loading of input files, processing of logs, and writing of output.

## Error Handling
- **File Not Found:** Logs an error if the lookup table or flow log file is missing.
- **Malformed Entries:** Logs warnings for invalid or malformed entries in both the lookup table and flow log file.
- **Rotating Logs:** Limits the log file size to 5 MB with up to 3 backups to prevent excessive disk usage.

## Limitations and Assumptions
- The flow log file size is assumed to be up to 10 MB.
- The lookup table can have up to 10,000 mappings.
- Matching is case-insensitive for protocols.
- Untagged entries occur when no matching port/protocol combination is found in the lookup table.

## Future Improvements
- Support for additional protocols by expanding the `get_protocol_name()` mapping.
- Enhanced error handling for various edge cases in log file parsing.
- Option to specify input/output filenames via command-line arguments.

