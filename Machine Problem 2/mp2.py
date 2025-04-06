import csv
import os
import sys
from collections import deque
from tabulate import tabulate
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colored terminal output
init(autoreset=True)

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

    def display_job_order(self):
        """Display the full job execution order including repeats (especially for RR, SRPT)."""
        if not self.timeline:
            return

        # Show all execution segments in order
        execution_order = [f"P{segment['pid']}" for segment in self.timeline]
        job_order_str = " → ".join(execution_order)

        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}Job Execution Order (with repeats):{Style.RESET_ALL}")
        print(f"{job_order_str}")


    def display_results(self, algorithm_name):
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{algorithm_name} Scheduling Results:{Style.RESET_ALL}")
        
        # Display job execution order
        self.display_job_order()
        
        # Display process statistics in a table
        table_data = []
        for p in self.processes:
            table_data.append([
                f"P{p.pid}", p.arrival_time, p.burst_time, p.priority,
                p.waiting_time, p.turnaround_time
            ])
        
        headers = ["Process", "Arrival", "Burst", "Priority", "Waiting Time", "Turnaround Time"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        
        # Calculate and display average metrics
        avg_waiting_time, avg_turnaround_time = self.calculate_statistics()
        print(f"{Fore.GREEN}Average Waiting Time: {avg_waiting_time:.2f} ms")
        print(f"{Fore.GREEN}Average Turnaround Time: {avg_turnaround_time:.2f} ms")
        
        # Display Gantt chart
        self.display_gantt_chart()

    def display_gantt_chart(self):
        if not self.timeline:
            print("No processes were scheduled.")
            return
        
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}Gantt Chart:{Style.RESET_ALL}")
        
        # Get the maximum width for the chart
        terminal_width = 80  # Default width
        try:
            terminal_width = os.get_terminal_size().columns - 5
        except:
            pass  # Use default width if can't detect terminal size

        max_time = self.timeline[-1]['end']
        scale_factor = min(1, terminal_width / max_time)
        
        # Create a list of process colors (cycling through available colors)
        colors = [Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN]
        process_colors = {}
        
        # Create a more visually appealing Gantt chart with better spacing
        print(f"Time: 0{' ' * 9}10{' ' * 9}20{' ' * 9}30{' ' * 9}40{' ' * 9}50")
        print(f"     |{'-' * min(terminal_width, max_time)}|")
        
        # Print the chart bars
        idle_char = "·"
        process_char = "█"
        
        for i, segment in enumerate(self.timeline):
            # Assign color to process if not already assigned
            pid = segment['pid']
            if pid not in process_colors:
                process_colors[pid] = colors[len(process_colors) % len(colors)]
            
            # Calculate the visual positions
            start_pos = int(segment['start'] * scale_factor)
            end_pos = int(segment['end'] * scale_factor)
            duration = end_pos - start_pos
            
            # Build the chart bar
            if i == 0 and start_pos > 0:
                # Handle idle time at the beginning
                bar = idle_char * start_pos
            else:
                bar = ""
                
            bar += process_colors[pid] + process_char * duration + Style.RESET_ALL
            
            # Add process label
            print(f"P{pid:<2}  |{bar}")
            
            # Add small gap between processes for readability
            if i < len(self.timeline) - 1:
                next_start = int(self.timeline[i+1]['start'] * scale_factor)
                if next_start > end_pos:
                    # Show idle time between processes
                    idle_bar = " " * start_pos + idle_char * (next_start - end_pos)
                    print(f"     |{idle_bar}")
        
        print(f"     |{'-' * min(terminal_width, max_time)}|")
        
        # Display time intervals in a more structured format
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}Time Intervals:{Style.RESET_ALL}")
        interval_data = []
        for segment in self.timeline:
            interval_data.append([
                f"P{segment['pid']}",
                segment['start'],
                segment['end'],
                segment['end'] - segment['start']
            ])
        
        interval_headers = ["Process", "Start Time", "End Time", "Duration"]
        print(tabulate(interval_data, headers=interval_headers, tablefmt="simple"))

    def fcfs(self):
        self.reset_processes()
        
        # Sort by arrival time
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
            # process.waiting_time = process.start_time - process.arrival_time
            process.waiting_time = process.start_time 

            # Update turnaround time (finish time - arrival time)
            # process.turnaround_time = process.finish_time - process.arrival_time
            process.turnaround_time = process.finish_time
            
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
            # process.waiting_time = process.start_time - process.arrival_time
            process.waiting_time = process.start_time 
            
            # Turnaround time is finish time (since arrival time is 0)
            # process.turnaround_time = process.finish_time - process.arrival_time
            process.turnaround_time = process.finish_time 
            
            current_time = process.finish_time

    def srpt(self):
        self.reset_processes()
        
        # Create copies of processes manually
        remaining_processes = []
        for p in self.processes:
            new_process = Process(
                pid=p.pid,
                arrival_time=p.arrival_time,
                burst_time=p.burst_time
            )
            new_process.remaining_time = p.burst_time
            new_process.start_time = -1  # Initialize to -1 (not started)
            remaining_processes.append(new_process)
        
        # Sort by arrival time initially
        remaining_processes.sort(key=lambda p: p.arrival_time)
        
        current_time = 0
        completed_processes = 0
        ready_queue = []
        last_process_id = -1  # For Gantt chart
        
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
            
            # Record start time if this is the first time the process runs
            if current_process.start_time == -1:
                current_process.start_time = current_time
            
            # Check if we need to start a new segment in the Gantt chart
            if last_process_id != current_process.pid:
                self.timeline.append({
                    'pid': current_process.pid,
                    'start': current_time,
                    'end': current_time  # Will be updated later
                })
                last_process_id = current_process.pid
            
            # Determine time slice (until completion or next arrival)
            time_slice = current_process.remaining_time
            if remaining_processes:
                next_arrival = remaining_processes[0].arrival_time
                time_slice = min(time_slice, next_arrival - current_time)
            
            # Execute the process for the time slice
            current_process.remaining_time -= time_slice
            current_time += time_slice
            
            # Update the end time of the current Gantt chart segment
            self.timeline[-1]['end'] = current_time
            
            # If the process is complete, calculate its metrics
            if current_process.remaining_time == 0:
                current_process.finish_time = current_time
                current_process.turnaround_time = current_process.finish_time 
                current_process.waiting_time = (current_process.turnaround_time - current_process.burst_time) - current_process.arrival_time
                
                # Update the original process with the results
                for original_p in self.processes:
                    if original_p.pid == current_process.pid:
                        original_p.start_time = current_process.start_time
                        original_p.finish_time = current_process.finish_time
                        original_p.turnaround_time = current_process.turnaround_time
                        original_p.waiting_time = current_process.waiting_time
                        break
                
                ready_queue.pop(0)
                completed_processes += 1
                last_process_id = -1
    
    def priority(self):
        self.reset_processes()
        
        # Create a copy of processes and sort by priority (lower number = higher priority)
        remaining_processes = sorted(self.processes.copy(), key=lambda p: p.priority)
        
        current_time = 0
        completed_processes = 0
        
        while completed_processes < len(self.processes):
            if not remaining_processes:
                break  # No more processes
            
            # Get the highest priority process (first in the sorted list)
            current_process = remaining_processes.pop(0)
            
            # Set start time (since arrival time is ignored)
            current_process.start_time = current_time
            
            # Execute the entire process (non-preemptive)
            execution_time = current_process.burst_time
            
            # Update timeline
            self.timeline.append({
                'pid': current_process.pid,
                'start': current_time,
                'end': current_time + execution_time
            })
            
            current_time += execution_time
            
            # Update process completion details
            current_process.finish_time = current_time
            current_process.remaining_time = 0
            
            # Waiting time = start_time (since arrival_time is ignored)
            current_process.waiting_time = current_process.start_time
            
            # Turnaround time = finish_time (since arrival_time is ignored)
            current_process.turnaround_time = current_process.finish_time
            
            completed_processes += 1
        

    def round_robin(self, quantum):
        self.reset_processes()
        
        # Create a queue of processes (ignoring arrival time)
        ready_queue = deque(self.processes.copy())
        current_time = 0
        completed_processes = 0
        
        while completed_processes < len(self.processes):
            if not ready_queue:
                break  # No more processes to execute
            
            current_process = ready_queue.popleft()
            
            # Set start time if this is the first execution
            if current_process.start_time == -1:  # Assuming reset sets to -1
                current_process.start_time = current_time
            
            # Execute for the quantum time or remaining time (whichever is smaller)
            execution_time = min(quantum, current_process.remaining_time)
            
            # Record in timeline
            self.timeline.append({
                'pid': current_process.pid,
                'start': current_time,
                'end': current_time + execution_time
            })
            
            # Update process and time
            current_process.remaining_time -= execution_time
            current_time += execution_time
            
            # Check if process completed
            if current_process.remaining_time == 0:
                current_process.finish_time = current_time
                current_process.turnaround_time = current_process.finish_time  # Since arrival time is ignored
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                completed_processes += 1
            else:
                # Put back in queue if not finished
                ready_queue.append(current_process)

def main():
    scheduler = Scheduler()
    
    while True:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}CPU Scheduling Simulator{Style.RESET_ALL}")
        print(f"{Fore.CYAN}========================{Style.RESET_ALL}")
        print("1. Load batch1.txt")
        print("2. Load batch2.txt")
        print("3. Load quiz.txt")
        print("4. Exit")
        
        file_choice = input(f"{Fore.GREEN}Enter your choice (1-4): {Style.RESET_ALL}")
        
        if file_choice == '4':
            print("Exiting the program.")
            break
        # elif file_choice == '3':
        #     txt_file = input("Enter TXT filename to convert: ")
        #     csv_file = input("Enter CSV output filename: ")
        #     scheduler.convert_to_csv(txt_file, csv_file)
        #     continue
        elif file_choice == '1':
            file_name = "batch1.txt"
        elif file_choice == '2':
            file_name = "batch2.txt"
        elif file_choice == "3":
            file_name = "quiz.txt"
        else:
            print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")
            continue
        
        # Load the selected file
        if not scheduler.load_from_file(file_name):
            print(f"{Fore.RED}Failed to load {file_name}{Style.RESET_ALL}")
            continue
        
        print(f"\n{Fore.GREEN}Loaded {len(scheduler.processes)} processes from {file_name}{Style.RESET_ALL}")
        
        # Algorithm selection menu
        while True:
            print(f"\n{Fore.CYAN}Select Scheduling Algorithm:{Style.RESET_ALL}")
            print("1. First-Come, First-Served (FCFS)")
            print("2. Shortest Job First (SJF)")
            print("3. Shortest Remaining Processing Time (SRPT)")
            print("4. Priority Scheduling")
            print("5. Round-Robin")
            print("6. Back to File Selection")
            
            algo_choice = input(f"{Fore.GREEN}Enter your choice (1-6): {Style.RESET_ALL}")
            
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
                quantum_time = int(input("Quantum Time: "))
                scheduler.round_robin(quantum_time)
                scheduler.display_results("Round-Robin (quantum = 4ms)")
            else:
                print(f"{Fore.RED}Invalid choice. Please try again.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
