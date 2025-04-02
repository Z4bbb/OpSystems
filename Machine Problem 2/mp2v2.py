import csv
import os
import sys
from collections import deque
from tabulate import tabulate

class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.start_time = 0
        self.finish_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.executed = False

    def reset(self):
        self.remaining_time = self.burst_time
        self.start_time = 0
        self.finish_time = 0
        self.waiting_time = 0
        self.turnaround_time = 0
        self.executed = False

    def __str__(self):
        return (f"Process {self.pid}: Arrival={self.arrival_time}, Burst={self.burst_time}, "
                f"Priority={self.priority}, Wait={self.waiting_time}, "
                f"Turnaround={self.turnaround_time}")


class Scheduler:
    def __init__(self):
        self.processes = []
        self.timeline = []
        self.current_time = 0
        self.total_waiting_time = 0
        self.total_turnaround_time = 0

    def load_from_file(self, filename):
        self.processes = []
        
        # Detect if the file is a .txt or .csv
        extension = os.path.splitext(filename)[1].lower()
        
        if extension == '.txt':
            with open(filename, 'r') as file:
                # Skip the header line
                lines = file.readlines()[1:]
                for line in lines:
                    values = line.strip().split()
                    if len(values) >= 4:
                        pid = int(values[0])
                        arrival_time = int(values[1])
                        burst_time = int(values[2])
                        priority = int(values[3])
                        self.processes.append(Process(pid, arrival_time, burst_time, priority))
        elif extension == '.csv':
            with open(filename, 'r') as file:
                csv_reader = csv.reader(file)
                # Skip the header row
                next(csv_reader)
                for row in csv_reader:
                    if len(row) >= 4:
                        pid = int(row[0])
                        arrival_time = int(row[1])
                        burst_time = int(row[2])
                        priority = int(row[3])
                        self.processes.append(Process(pid, arrival_time, burst_time, priority))
        else:
            print(f"Unsupported file format: {extension}")
            return False
            
        return True

    def convert_to_csv(self, txt_filename, csv_filename):
        with open(txt_filename, 'r') as txt_file:
            # Skip the header line in the txt file
            lines = txt_file.readlines()[1:]
            
            with open(csv_filename, 'w', newline='') as csv_file:
                csv_writer = csv.writer(csv_file)
                # Write the header row to CSV
                csv_writer.writerow(['Process', 'Arrival', 'CPU Burst Time', 'Priority'])
                
                for line in lines:
                    values = line.strip().split()
                    if len(values) >= 4:
                        csv_writer.writerow([values[0], values[1], values[2], values[3]])
        
        print(f"Converted {txt_filename} to {csv_filename}")
        return True

    def reset_processes(self):
        for process in self.processes:
            process.reset()
        self.timeline = []
        self.current_time = 0
        self.total_waiting_time = 0
        self.total_turnaround_time = 0

    def calculate_statistics(self):
        self.total_waiting_time = sum(process.waiting_time for process in self.processes)
        self.total_turnaround_time = sum(process.turnaround_time for process in self.processes)
        avg_waiting_time = self.total_waiting_time / len(self.processes)
        avg_turnaround_time = self.total_turnaround_time / len(self.processes)
        return avg_waiting_time, avg_turnaround_time

    def display_results(self, algorithm_name):
        print(f"\n{algorithm_name} Scheduling Results:")
        
        # Display process statistics in a table
        table_data = []
        for p in self.processes:
            table_data.append([
                f"P{p.pid}", p.arrival_time, p.burst_time, p.priority,
                p.waiting_time, p.turnaround_time
            ])
        
        headers = ["Process", "Arrival", "Burst", "Priority", "Waiting Time", "Turnaround Time"]
        print(tabulate(table_data, headers=headers, tablefmt="pretty"))
        
        # Calculate and display average metrics
        avg_waiting_time, avg_turnaround_time = self.calculate_statistics()
        print(f"Average Waiting Time: {avg_waiting_time:.2f}")
        print(f"Average Turnaround Time: {avg_turnaround_time:.2f}")
        
        # Display Gantt chart
        self.display_gantt_chart()

    def display_gantt_chart(self):
        if not self.timeline:
            print("No processes were scheduled.")
            return
            
        print("\nGantt Chart:")
        
        # Prepare the chart header (time markers)
        max_time = self.timeline[-1]['end']
        time_markers = "".join([f"{t:5d}" for t in range(0, max_time + 5, 5)])
        print(" " * 6 + "|" + time_markers)
        
        # Prepare the chart body
        chart = " " * 6 + "|"
        last_end = 0
        
        for segment in self.timeline:
            # Add empty space for idle time
            if segment['start'] > last_end:
                idle_duration = segment['start'] - last_end
                chart += " " * idle_duration
            
            # Add the process block
            duration = segment['end'] - segment['start']
            process_block = f"P{segment['pid']}"
            
            # Center the process ID in its time slot
            padding = duration - len(process_block)
            left_padding = padding // 2
            right_padding = padding - left_padding
            
            chart += " " * left_padding + process_block + " " * right_padding
            last_end = segment['end']
        
        print(chart)
        
        # Prepare the chart footer (time markers)
        footer = " " * 6 + "|"
        for segment in self.timeline:
            footer += f"{segment['start']:<{segment['end'] - segment['start']}}"
        footer += str(self.timeline[-1]['end'])
        print(footer)
        
        # Display time intervals
        print("\nTime Intervals:")
        for segment in self.timeline:
            print(f"P{segment['pid']}: {segment['start']} -> {segment['end']}")

    def fcfs(self):
        self.reset_processes()
        
        # Sort by arrival time (already assumed to be at time 0 in the order given)
        # We don't actually need to sort here since the problem specifies using the order given
        # but we include this for completeness
        
        current_time = 0
        
        for process in self.processes:
            # If the process hasn't arrived yet, advance time
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            
            process.start_time = current_time
            process.finish_time = current_time + process.burst_time
            
            # Update timeline for Gantt chart
            self.timeline.append({
                'pid': process.pid,
                'start': current_time,
                'end': process.finish_time
            })
            
            # Update waiting time (time spent waiting after arrival)
            process.waiting_time = process.start_time - process.arrival_time
            
            # Update turnaround time (finish time - arrival time)
            process.turnaround_time = process.finish_time - process.arrival_time
            
            current_time = process.finish_time

    def sjf(self):
        self.reset_processes()
        
        # For SJF, assume all processes arrive at time 0 in the given order
        # Sort the processes by burst time
        sorted_processes = sorted(self.processes, key=lambda p: p.burst_time)
        
        current_time = 0
        
        for process in sorted_processes:
            # All processes are assumed to be available at time 0
            process.start_time = current_time
            process.finish_time = current_time + process.burst_time
            
            # Update timeline for Gantt chart
            self.timeline.append({
                'pid': process.pid,
                'start': current_time,
                'end': process.finish_time
            })
            
            # Waiting time is simply the start time (since arrival time is 0)
            process.waiting_time = process.start_time - process.arrival_time
            
            # Turnaround time is finish time (since arrival time is 0)
            process.turnaround_time = process.finish_time - process.arrival_time
            
            current_time = process.finish_time

    def srpt(self):
        self.reset_processes()
        
        # Create a copy of processes for sorting
        remaining_processes = self.processes.copy()
        
        # Sort by arrival time initially
        remaining_processes.sort(key=lambda p: p.arrival_time)
        
        current_time = 0
        completed_processes = 0
        ready_queue = []
        last_process_id = -1  # Track the last executed process for Gantt chart
        
        while completed_processes < len(self.processes):
            # Add newly arrived processes to the ready queue
            while remaining_processes and remaining_processes[0].arrival_time <= current_time:
                process = remaining_processes.pop(0)
                ready_queue.append(process)
            
            if not ready_queue:
                # If no process is ready, advance time to the next arrival
                if remaining_processes:
                    current_time = remaining_processes[0].arrival_time
                    continue
                else:
                    break  # No more processes
            
            # Sort the ready queue by remaining time
            ready_queue.sort(key=lambda p: p.remaining_time)
            
            # Get the process with the shortest remaining time
            current_process = ready_queue[0]
            
            # Check if we need to start a new segment in the Gantt chart
            if last_process_id != current_process.pid:
                self.timeline.append({
                    'pid': current_process.pid,
                    'start': current_time,
                    'end': current_time  # Will be updated later
                })
                last_process_id = current_process.pid
            
            # Determine how long this process will run
            # Either until completion or until a new process arrives
            time_slice = current_process.remaining_time
            
            if remaining_processes:
                next_arrival = remaining_processes[0].arrival_time
                if next_arrival > current_time:
                    time_slice = min(time_slice, next_arrival - current_time)
            
            # Update the process and current time
            current_process.remaining_time -= time_slice
            current_time += time_slice
            
            # Update the end time of the current Gantt chart segment
            self.timeline[-1]['end'] = current_time
            
            # If the process is complete, calculate its metrics
            if current_process.remaining_time == 0:
                current_process.finish_time = current_time
                current_process.turnaround_time = current_process.finish_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                
                ready_queue.pop(0)  # Remove the completed process
                completed_processes += 1
                last_process_id = -1  # Reset for Gantt chart tracking
    
    def priority(self):
        self.reset_processes()
        
        # Create a copy of processes
        remaining_processes = self.processes.copy()
        
        # Sort by arrival time initially
        remaining_processes.sort(key=lambda p: p.arrival_time)
        
        current_time = 0
        completed_processes = 0
        ready_queue = []
        
        while completed_processes < len(self.processes):
            # Add newly arrived processes to the ready queue
            while remaining_processes and remaining_processes[0].arrival_time <= current_time:
                process = remaining_processes.pop(0)
                ready_queue.append(process)
            
            if not ready_queue:
                # If no process is ready, advance time to the next arrival
                if remaining_processes:
                    current_time = remaining_processes[0].arrival_time
                    continue
                else:
                    break  # No more processes
            
            # Sort the ready queue by priority (lower value = higher priority)
            ready_queue.sort(key=lambda p: p.priority)
            
            # Get the process with the highest priority
            current_process = ready_queue.pop(0)
            
            # If this process hasn't started yet, record its start time
            if current_process.start_time == 0 and not current_process.executed:
                current_process.start_time = current_time
                current_process.executed = True
            
            # Update timeline for Gantt chart
            self.timeline.append({
                'pid': current_process.pid,
                'start': current_time,
                'end': current_time + current_process.remaining_time
            })
            
            # Execute the entire process
            current_time += current_process.remaining_time
            current_process.remaining_time = 0
            
            # Update finish time and calculate metrics
            current_process.finish_time = current_time
            current_process.turnaround_time = current_process.finish_time - current_process.arrival_time
            current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
            
            completed_processes += 1
    
    def round_robin(self, quantum=4):
        self.reset_processes()
        
        # Create a copy of processes
        process_queue = deque(sorted(self.processes, key=lambda p: p.arrival_time))
        
        current_time = 0
        completed_processes = 0
        ready_queue = deque()
        
        while completed_processes < len(self.processes) or ready_queue:
            # Add newly arrived processes to the ready queue
            while process_queue and process_queue[0].arrival_time <= current_time:
                ready_queue.append(process_queue.popleft())
            
            if not ready_queue:
                # If no process is ready, advance time to the next arrival
                if process_queue:
                    current_time = process_queue[0].arrival_time
                    continue
                else:
                    break  # No more processes
            
            # Get the next process from the ready queue
            current_process = ready_queue.popleft()
            
            # If the process is executing for the first time, set its start time
            if not current_process.executed:
                current_process.start_time = current_time
                current_process.executed = True
            
            # Determine execution time for this quantum
            execution_time = min(quantum, current_process.remaining_time)
            
            # Update timeline for Gantt chart
            self.timeline.append({
                'pid': current_process.pid,
                'start': current_time,
                'end': current_time + execution_time
            })
            
            # Update process and current time
            current_process.remaining_time -= execution_time
            current_time += execution_time
            
            # Add any newly arrived processes during this quantum
            while process_queue and process_queue[0].arrival_time <= current_time:
                ready_queue.append(process_queue.popleft())
            
            # Check if the process is complete
            if current_process.remaining_time == 0:
                current_process.finish_time = current_time
                current_process.turnaround_time = current_process.finish_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                completed_processes += 1
            else:
                # If not complete, put it back in the ready queue
                ready_queue.append(current_process)

def main():
    scheduler = Scheduler()
    
    while True:
        print("\nCPU Scheduling Simulator")
        print("========================")
        print("1. Load batch1.txt")
        print("2. Load batch2.txt")
        print("3. Convert TXT to CSV")
        print("4. Exit")
        
        file_choice = input("Enter your choice (1-4): ")
        
        if file_choice == '4':
            print("Exiting the program.")
            break
        elif file_choice == '3':
            txt_file = input("Enter TXT filename to convert: ")
            csv_file = input("Enter CSV output filename: ")
            scheduler.convert_to_csv(txt_file, csv_file)
            continue
        elif file_choice == '1':
            file_name = "batch1.txt"
        elif file_choice == '2':
            file_name = "batch2.txt"
        else:
            print("Invalid choice. Please try again.")
            continue
        
        # Load the selected file
        if not scheduler.load_from_file(file_name):
            print(f"Failed to load {file_name}")
            continue
        
        print(f"\nLoaded {len(scheduler.processes)} processes from {file_name}")
        
        # Algorithm selection menu
        while True:
            print("\nSelect Scheduling Algorithm:")
            print("1. First-Come, First-Served (FCFS)")
            print("2. Shortest Job First (SJF)")
            print("3. Shortest Remaining Processing Time (SRPT)")
            print("4. Priority Scheduling")
            print("5. Round-Robin (quantum = 4ms)")
            print("6. Back to File Selection")
            
            algo_choice = input("Enter your choice (1-6): ")
            
            if algo_choice == '6':
                break
            
            # Run the selected algorithm
            if algo_choice == '1':
                scheduler.fcfs()
                scheduler.display_results("First-Come, First-Served (FCFS)")
            elif algo_choice == '2':
                scheduler.sjf()
                scheduler.display_results("Shortest Job First (SJF)")
            elif algo_choice == '3':
                scheduler.srpt()
                scheduler.display_results("Shortest Remaining Processing Time (SRPT)")
            elif algo_choice == '4':
                scheduler.priority()
                scheduler.display_results("Priority Scheduling")
            elif algo_choice == '5':
                scheduler.round_robin(4)
                scheduler.display_results("Round-Robin (quantum = 4ms)")
            else:
                print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
