import csv
import logging
from typing import Dict, Any

#MAKE AS SEPARATE FUNCTION
# REMOVE REDUNDANT PARTS
class CSVWriter:

    def add_record(self, result: Dict[str, Any], wallet: str, csv_file: str, active_branches: int, thread_count: int):
        """Add record trade result to CSV file"""
        with open(csv_file, 'a', newline='') as csvfile:
            fieldnames = ['active_branches', 'thread_count']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            # Prepare row data
            row = {
                'active_branches': active_branches,
                'thread_count': thread_count
            }

            writer.writerow(row)
            logging.info(f"Added record to CSV: {row}")
