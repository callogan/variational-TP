import csv
import os

class CSVRecorder:
    def __init__(self, active_branches, thread_count):

        self.active_branches = active_branches
        self.thread_count = thread_count

    # def record_to_csv(self, file_path, additional_data, result, wallet):
    #     """Record additional data to a CSV file."""
    #     file_exists = os.path.isfile(file_path)
    #     with open(file_path, mode='a', newline='') as file:
    #         writer = csv.writer(file)
    #         # Write header only if the file is new
    #         if not file_exists:
    #             writer.writerow(['Active Branches', 'Thread Count', 'Additional Data'])
    #         writer.writerow([self.active_branches, self.thread_count, additional_data]) 

    def record_to_csv(self, file_path, additional_data, result, wallet):
        """Record additional data and result fields to a CSV file."""
        file_exists = os.path.isfile(file_path)
        with open(file_path, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Write header only if the file is new
            if not file_exists:
                writer.writerow([
                    'Active Branches', 'Thread Count', 'Additional Data',
                    'Timestamp', 'Status', 'Transaction Hash', 'Error'
                ])

            writer.writerow([
                self.active_branches,
                self.thread_count,
                additional_data,
                result.get('timestamp', ''),
                wallet,
                result.get('status', ''),
                result.get('transaction_hash', ''),
                result.get('error', '')
            ])
