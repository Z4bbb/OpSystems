"""
Memory Management and Allocation Strategies Simulation
This program simulates three memory allocation strategies (First-fit, Worst-fit, Best-fit)
using an event-driven approach for a fixed partition multiprogramming system.
"""

import heapq
from collections import defaultdict
import copy

class MemoryBlock:
    """Represents a memory partition in the system"""
    def __init__(self, block_id, size):
        self.id = block_id
        self.size = size
        self.available = True
        self.job = None
        self.usage_count = 0
        self.fragmentation = 0
    
    def allocate(self, job):
        """Allocate this block to a job"""
        self.available = False
        self.job = job
        self.usage_count += 1
        self.fragmentation = self.size - job.size
        return True
    
    def release(self):
        """Release this block when job completes"""
        self.available = True
        self.job = None

class Job:
    """Represents a job to be executed"""
    def __init__(self, job_id, execution_time, size):
        self.id = job_id
        self.execution_time = execution_time
        self.size = size
        self.arrival_time = 0  # All jobs arrive at time 0 in this simulation
        self.start_time = None
        self.completion_time = None
        self.waiting_time = 0

class Event:
    """Represents an event in the simulation"""
    JOB_ARRIVAL = 0
    JOB_COMPLETION = 1
    
    def __init__(self, time, job, event_type):
        self.time = time
        self.job = job
        self.event_type = event_type
    
    def __lt__(self, other):
        """For priority queue comparison"""
        return self.time < other.time

class MemoryAllocationSimulator:
    """Event-driven simulator for memory allocation strategies"""
    def __init__(self, strategy_name):
        self.strategy_name = strategy_name
        self.current_time = 0
        self.jobs = []
        self.memory_blocks = []
        self.event_queue = []
        self.waiting_queue = []
        self.completed_jobs = []
        
        # Statistics tracking
        self.queue_length_samples = []
        self.waiting_times = []
        self.total_fragmentation = 0
        self.block_usage = defaultdict(int)
    
    def initialize(self, jobs_data, memory_data):
        """Initialize the simulation with jobs and memory blocks"""
        # Create jobs
        self.jobs = [Job(job_id, time, size) for job_id, time, size in jobs_data]
        
        # Create memory blocks
        self.memory_blocks = [MemoryBlock(block_id, size) for block_id, size in memory_data]
        
        # For best-fit, sort memory blocks by size
        if self.strategy_name == "Best-fit":
            self.memory_blocks = sorted(self.memory_blocks, key=lambda block: block.size)
        
        # Initialize event queue with all job arrivals at time 0
        for job in self.jobs:
            heapq.heappush(self.event_queue, Event(0, job, Event.JOB_ARRIVAL))
    
    def allocate_memory_first_fit(self, job):
        """First-fit allocation strategy"""
        for block in self.memory_blocks:
            if block.available and block.size >= job.size:
                return block
        return None
    
    def allocate_memory_best_fit(self, job):
        """Best-fit allocation strategy (assumes memory blocks are sorted by size)"""
        best_block = None
        best_fit_size = float('inf')
        
        for block in self.memory_blocks:
            if block.available and block.size >= job.size:
                if block.size - job.size < best_fit_size:
                    best_fit_size = block.size - job.size
                    best_block = block
        
        return best_block
    
    def allocate_memory_worst_fit(self, job):
        """Worst-fit allocation strategy"""
        worst_block = None
        worst_fit_size = -1
        
        for block in self.memory_blocks:
            if block.available and block.size >= job.size:
                if block.size - job.size > worst_fit_size:
                    worst_fit_size = block.size - job.size
                    worst_block = block
        
        return worst_block
    
    def allocate_memory(self, job):
        """Allocate memory using the selected strategy"""
        block = None
        
        if self.strategy_name == "First-fit":
            block = self.allocate_memory_first_fit(job)
        elif self.strategy_name == "Best-fit":
            block = self.allocate_memory_best_fit(job)
        elif self.strategy_name == "Worst-fit":
            block = self.allocate_memory_worst_fit(job)
        
        if block:
            # Update job and block status
            block.allocate(job)
            job.start_time = self.current_time
            job.completion_time = self.current_time + job.execution_time
            
            # Schedule job completion event
            heapq.heappush(self.event_queue, Event(job.completion_time, job, Event.JOB_COMPLETION))
            
            # Record fragmentation
            self.total_fragmentation += block.fragmentation
            
            # Record block usage
            self.block_usage[block.id] += 1
            
            # Record waiting time
            self.waiting_times.append(job.waiting_time)
            
            return True
        
        return False
    
    def process_job_arrival(self, event):
        """Process a job arrival event"""
        job = event.job
        
        # Try to allocate memory
        if not self.allocate_memory(job):
            # If allocation fails, put job in waiting queue
            self.waiting_queue.append(job)
        
        # Record current queue length
        self.queue_length_samples.append(len(self.waiting_queue))
    
    def process_job_completion(self, event):
        """Process a job completion event"""
        job = event.job
        
        # Find and release the memory block
        for block in self.memory_blocks:
            if not block.available and block.job == job:
                block.release()
                break
        
        # Add job to completed list
        self.completed_jobs.append(job)
        
        # Try to allocate memory to waiting jobs
        self.try_allocate_waiting_jobs()
        
        # Record current queue length
        self.queue_length_samples.append(len(self.waiting_queue))
    
    def try_allocate_waiting_jobs(self):
        """Try to allocate memory to jobs in the waiting queue"""
        allocated_indices = []
        
        for i, job in enumerate(self.waiting_queue):
            # Update waiting time for this job
            job.waiting_time += self.current_time - job.arrival_time
            
            if self.allocate_memory(job):
                allocated_indices.append(i)
        
        # Remove allocated jobs from waiting queue (in reverse order)
        for i in sorted(allocated_indices, reverse=True):
            self.waiting_queue.pop(i)
        
        # Update waiting time for remaining jobs
        for job in self.waiting_queue:
            job.arrival_time = self.current_time  # Reset arrival time for waiting time calculation
    
    def run(self):
        """Run the simulation until all jobs are completed"""
        while self.event_queue or self.waiting_queue:
            if not self.event_queue:
                # If no more events but jobs are waiting, advance time to next possible allocation
                # (This would happen in a real system when a job completes)
                self.current_time += 1
                self.try_allocate_waiting_jobs()
                continue
            
            # Get next event
            event = heapq.heappop(self.event_queue)
            
            # Update current time
            self.current_time = event.time
            
            # Process event based on type
            if event.event_type == Event.JOB_ARRIVAL:
                self.process_job_arrival(event)
            else:  # JOB_COMPLETION
                self.process_job_completion(event)
            
            # Update waiting time for all jobs in queue
            for job in self.waiting_queue:
                job.waiting_time += 1
    
    def get_results(self):
        """Calculate and return performance metrics"""
        if not self.completed_jobs:
            return {
                "strategy": self.strategy_name,
                "error": "No jobs completed"
            }
        
        total_simulation_time = max(job.completion_time for job in self.completed_jobs)
        
        # Calculate throughput
        throughput = len(self.completed_jobs) / total_simulation_time if total_simulation_time > 0 else 0
        
        # Calculate average queue length
        avg_queue_length = sum(self.queue_length_samples) / len(self.queue_length_samples) if self.queue_length_samples else 0
        
        # Calculate average waiting time
        avg_waiting_time = sum(self.waiting_times) / len(self.waiting_times) if self.waiting_times else 0
        
        # Calculate average internal fragmentation
        avg_fragmentation = self.total_fragmentation / len(self.completed_jobs) if self.completed_jobs else 0
        
        # Calculate memory block utilization
        unused_blocks = sum(1 for block_id in range(1, len(self.memory_blocks) + 1) if self.block_usage[block_id] == 0)
        unused_percentage = (unused_blocks / len(self.memory_blocks)) * 100
        
        heavily_used_threshold = len(self.jobs) / 10  # Define "heavily used" as being used for >10% of jobs
        heavily_used_blocks = sum(1 for usage in self.block_usage.values() if usage > heavily_used_threshold)
        heavily_used_percentage = (heavily_used_blocks / len(self.memory_blocks)) * 100
        
        return {
            "strategy": self.strategy_name,
            "completed_jobs": len(self.completed_jobs),
            "total_simulation_time": total_simulation_time,
            "throughput": throughput,
            "avg_queue_length": avg_queue_length,
            "avg_waiting_time": avg_waiting_time,
            "avg_fragmentation": avg_fragmentation,
            "unused_blocks_percentage": unused_percentage,
            "heavily_used_blocks_percentage": heavily_used_percentage,
            "block_usage": dict(self.block_usage)
        }

def run_simulations():
    """Run simulations for all three allocation strategies"""
    # Job data format: [job_id, execution_time, size]
    job_data = [
        [1, 5, 5760], [2, 4, 4190], [3, 8, 3290], [4, 2, 2030], [5, 2, 2550],
        [6, 6, 6990], [7, 8, 8940], [8, 10, 740], [9, 7, 3930], [10, 6, 6890],
        [11, 5, 6580], [12, 8, 3820], [13, 9, 9140], [14, 10, 420], [15, 10, 220],
        [16, 7, 7540], [17, 3, 3210], [18, 1, 1380], [19, 9, 9850], [20, 3, 3610],
        [21, 7, 7540], [22, 2, 2710], [23, 8, 8390], [24, 5, 5950], [25, 10, 760]
    ]
    
    # Memory data format: [block_id, size]
    memory_data = [
        [1, 9500], [2, 7000], [3, 4500], [4, 8500], [5, 3000],
        [6, 9000], [7, 1000], [8, 5500], [9, 1500], [10, 500]
    ]
    
    # Run simulations for all three strategies
    strategies = ["First-fit", "Worst-fit", "Best-fit"]
    results = []
    
    for strategy in strategies:
        simulator = MemoryAllocationSimulator(strategy)
        simulator.initialize(job_data, memory_data)
        simulator.run()
        results.append(simulator.get_results())
    
    return results

def print_results(results):
    """Print formatted simulation results"""
    print("\n===== MEMORY ALLOCATION SIMULATION RESULTS =====\n")
    
    for result in results:
        print(f"Strategy: {result['strategy']}")
        print(f"Completed Jobs: {result['completed_jobs']}")
        print(f"Total Simulation Time: {result['total_simulation_time']}")
        print(f"Throughput: {result['throughput']:.4f} jobs per time unit")
        print(f"Average Queue Length: {result['avg_queue_length']:.2f}")
        print(f"Average Waiting Time: {result['avg_waiting_time']:.2f} time units")
        print(f"Average Internal Fragmentation: {result['avg_fragmentation']:.2f} memory units")
        print(f"Unused Blocks: {result['unused_blocks_percentage']:.2f}%")
        print(f"Heavily Used Blocks: {result['heavily_used_blocks_percentage']:.2f}%")
        print(f"Block Usage: {result['block_usage']}")
        print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    results = run_simulations()
    print_results(results)
