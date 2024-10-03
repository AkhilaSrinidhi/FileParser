import csv
import logging
from logging.handlers import RotatingFileHandler

# Step 1: Configure logging with a rotating file handler
log_handler = RotatingFileHandler('flow_log_parser.log', maxBytes=5*1024*1024, backupCount=3)  # 5 MB per log file, keep 3 backups
logging.basicConfig(
    handlers=[log_handler],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
# Step 1: Read the lookup table and store mappings
def load_lookup_table(lookup_filename):
    lookup_dict = {}
    try:
        with open(lookup_filename, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Input validation: Ensure fields are not empty and dstport is a valid integer
                port = row['dstport'].strip()
                protocol = row['protocol'].strip().lower()  # Normalize protocol name to lowercase
                tag = row['tag'].strip()
                
                if not port.isdigit() or not protocol or not tag:
                    logging.warning(f"Skipping invalid entry in lookup table: {row}")
                    continue
                
                # Use nested dictionary for protocol and port mapping
                if protocol not in lookup_dict:
                    lookup_dict[protocol] = {}
                if port not in lookup_dict[protocol]:
                    lookup_dict[protocol][port] = []
                lookup_dict[protocol][port].append(tag)  # Allow multiple tags per combination
        logging.info(f"Loaded lookup table from {lookup_filename}")
    except FileNotFoundError:
        logging.error(f"Lookup table file not found: {lookup_filename}")
    except Exception as e:
        logging.error(f"Error reading lookup table: {e}")
    return lookup_dict

# Step 2: Map protocol numbers to names (e.g., 6 -> tcp)
def get_protocol_name(protocol_number):
    protocol_map = {
        '1': 'icmp',
        '2': 'igmp',
        '6': 'tcp',
        '17': 'udp',
        '41': 'ipv6',
        '50': 'esp',
        '51': 'ah',
        '58': 'ipv6-icmp',
        '89': 'ospf',
        '103': 'pim',
        '132': 'sctp',
        # Add more protocols as needed
    }
    return protocol_map.get(protocol_number, 'unknown')  # Use 'unknown' if the protocol is not recognized

# Step 3: Process the flow log file
def process_flow_log(log_filename, lookup_dict):
    tag_counts = {}
    port_protocol_counts = {}
    
    try:
        with open(log_filename, 'r') as logfile:
            for line_number, line in enumerate(logfile, start=1):
                fields = line.strip().split()
                
                try:
                    dstport = fields[5].strip()  # Destination port is at index 5
                    protocol_number = fields[7].strip()  # Protocol number is at index 7
                    protocol_name = get_protocol_name(protocol_number).lower()  # Convert to protocol name and normalize
                except IndexError:
                    logging.warning(f"Skipping malformed log line at line {line_number}: '{line.strip()}' (missing fields)")
                    continue

                # Input validation: Ensure dstport is an integer
                if not dstport.isdigit():
                    logging.warning(f"Invalid dstport '{dstport}' in log line {line_number}: '{line.strip()}'")
                    continue

                # Find tags using the lookup table
                tags = lookup_dict.get(protocol_name, {}).get(dstport, ['Untagged'])

                # Update tag counts for each tag
                for tag in tags:
                    tag_counts[tag] = tag_counts.get(tag, 0) + 1
                
                # Update port/protocol combination counts
                port_protocol_key = (dstport, protocol_name)
                port_protocol_counts[port_protocol_key] = port_protocol_counts.get(port_protocol_key, 0) + 1

        logging.info(f"Processed flow log file: {log_filename}")
    except FileNotFoundError:
        logging.error(f"Flow log file not found: {log_filename}")
    except Exception as e:
        logging.error(f"Error processing flow log file: {e}")
    
    return tag_counts, port_protocol_counts

# Step 4: Write results to the output file
def write_output(output_filename, tag_counts, port_protocol_counts):
    try:
        with open(output_filename, 'w') as outfile:
            # Write tag counts in the desired order
            outfile.write("Tag Counts:\n")
            outfile.write("Tag,Count\n")
            
            # Define desired tag order
            prioritized_tags = ['sv_P2', 'sv_P1', 'sv_P4', 'email']
            
            # Write prioritized tags in the desired order if they exist in the tag_counts
            for tag in prioritized_tags:
                if tag in tag_counts:
                    outfile.write(f"{tag},{tag_counts[tag]}\n")
            
            # Sort and append remaining tags (excluding "Untagged")
            remaining_tags = sorted([tag for tag in tag_counts if tag not in prioritized_tags and tag != 'Untagged'])
            for tag in remaining_tags:
                outfile.write(f"{tag},{tag_counts[tag]}\n")
            
            # Always append "Untagged" last
            if 'Untagged' in tag_counts:
                outfile.write(f"Untagged,{tag_counts['Untagged']}\n")
            
            # Write port/protocol combination counts
            outfile.write("\nPort/Protocol Combination Counts:\n")
            outfile.write("Port,Protocol,Count\n")
            
            # Define a desired order for common ports
            common_ports = ['22', '23', '25', '110', '143', '443', '993', '1024', '49158', '80']
            
            # Sort and write port/protocol combinations, giving precedence to the common ports
            for port in common_ports:
                for protocol in ['tcp', 'udp', 'icmp']:  # Adjust as needed for other protocols
                    if (port, protocol) in port_protocol_counts:
                        outfile.write(f"{port},{protocol},{port_protocol_counts[(port, protocol)]}\n")
            
            # Handle remaining ports not in the common_ports list
            remaining_ports = sorted(port_protocol_counts.keys())
            for port, protocol in remaining_ports:
                if port not in common_ports:  # Skip common ports as they are already handled
                    outfile.write(f"{port},{protocol},{port_protocol_counts[(port, protocol)]}\n")

        logging.info(f"Results written to {output_filename}")
    except Exception as e:
        logging.error(f"Error writing output file: {e}")

# Main function to run the program
def main():
    lookup_filename = 'lookup.csv'
    log_filename = 'flow_logs.txt'
    output_filename = 'output.txt'
    
    # Load lookup table
    lookup_dict = load_lookup_table(lookup_filename)
    
    # Process flow logs
    tag_counts, port_protocol_counts = process_flow_log(log_filename, lookup_dict)
    
    # Write output
    write_output(output_filename, tag_counts, port_protocol_counts)

# Run the program
if __name__ == '__main__':
    main()
