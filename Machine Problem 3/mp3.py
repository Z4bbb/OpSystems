class Job:
    """
    Represents a job with its attributes.
    """
    def __init__(self, id, arrival_time, size, execution_time):
        """
        Initializes a Job object.
        """
        self.id = id
        self.arrival_time = arrival_time
        self.size = size
        self.execution_time = execution_time
        self.remaining_time = execution_time  # Track remaining time separately from execution_time
        self.start_time = None
        self.finish_time = None
        self.waiting_time = 0

    def __str__(self):
        return f"Job {self.id} (Size: {self.size}, Time: {self.remaining_time}/{self.execution_time})"


class MemoryBlock:
    """
    Represents a memory block with its attributes.
    """
    def __init__(self, id, size):
        """
        Initializes a MemoryBlock object.
        """
        self.id = id
        self.size = size
        self.is_allocated = False
        self.allocated_job = None

    def __str__(self):
        if self.is_allocated:
            used_space = self.allocated_job.size
            remaining_space = self.size - used_space
            return f"Memory {self.id} (Size: {self.size}, Used: {used_space}, Free: {remaining_space})"
        else:
            return f"Memory {self.id} (Size: {self.size}, Free: {self.size})"


def initialize_jobs():
    """
    Initializes a list of Job objects based on the provided data.
    """
    jobs_data = [
        {"id": 1, "arrival_time": 0, "size": 5760, "execution_time": 5},
        {"id": 2, "arrival_time": 0, "size": 4190, "execution_time": 4},
        {"id": 3, "arrival_time": 0, "size": 3290, "execution_time": 8},
        {"id": 4, "arrival_time": 0, "size": 2030, "execution_time": 2},
        {"id": 5, "arrival_time": 0, "size": 2550, "execution_time": 2},
        {"id": 6, "arrival_time": 0, "size": 6990, "execution_time": 6},
        {"id": 7, "arrival_time": 0, "size": 8940, "execution_time": 8},
        {"id": 8, "arrival_time": 0, "size": 740, "execution_time": 10},
        {"id": 9, "arrival_time": 0, "size": 3930, "execution_time": 7},
        {"id": 10, "arrival_time": 0, "size": 6890, "execution_time": 6},
        {"id": 11, "arrival_time": 0, "size": 6580, "execution_time": 5},
        {"id": 12, "arrival_time": 0, "size": 3820, "execution_time": 8},
        {"id": 13, "arrival_time": 0, "size": 9140, "execution_time": 9},
        {"id": 14, "arrival_time": 0, "size": 420, "execution_time": 10},
        {"id": 15, "arrival_time": 0, "size": 220, "execution_time": 10},
        {"id": 16, "arrival_time": 0, "size": 7540, "execution_time": 7},
        {"id": 17, "arrival_time": 0, "size": 3210, "execution_time": 3},
        {"id": 18, "arrival_time": 0, "size": 1380, "execution_time": 1},
        {"id": 19, "arrival_time": 0, "size": 9850, "execution_time": 9},
        {"id": 20, "arrival_time": 0, "size": 3610, "execution_time": 3},
        {"id": 21, "arrival_time": 0, "size": 7540, "execution_time": 7},
        {"id": 22, "arrival_time": 0, "size": 2710, "execution_time": 2},
        {"id": 23, "arrival_time": 0, "size": 8390, "execution_time": 8},
        {"id": 24, "arrival_time": 0, "size": 5950, "execution_time": 5},
        {"id": 25, "arrival_time": 0, "size": 760, "execution_time": 10}
    ]
    return [Job(**data) for data in jobs_data]


def initialize_memory_blocks():
    """
    Initializes a list of MemoryBlock objects based on the provided data.
    """
    memory_data = [
        {"id": 1, "size": 9500},
        {"id": 2, "size": 7000},
        {"id": 3, "size": 4500},
        {"id": 4, "size": 8500},
        {"id": 5, "size": 3000},
        {"id": 6, "size": 9000},
        {"id": 7, "size": 1000},
        {"id": 8, "size": 5500},
        {"id": 9, "size": 1500},
        {"id": 10, "size": 500}
    ]
    return [MemoryBlock(**data) for data in memory_data]


def first_fit(job, memory_blocks):
    """
    Allocates memory to a job using the First-Fit algorithm.
    """
    for i, block in enumerate(memory_blocks):
        if not block.is_allocated and block.size >= job.size:
            allocate_block(job, block)
            return True
    return False


def worst_fit(job, memory_blocks):
    """
    Allocates memory to a job using the Worst-Fit algorithm.
    """
    best_block_index = None
    max_diff = -1
    for i, block in enumerate(memory_blocks):
        if not block.is_allocated and block.size >= job.size:
            diff = block.size - job.size
            if diff > max_diff:
                max_diff = diff
                best_block_index = i
    if best_block_index is not None:
        allocate_block(job, memory_blocks[best_block_index])
        return True
    return False


def best_fit(job, memory_blocks):
    """
    Allocates memory to a job using the Best-Fit algorithm.
    """
    best_block_index = None
    min_diff = float('inf')
    for i, block in enumerate(memory_blocks):
        if not block.is_allocated and block.size >= job.size:
            diff = block.size - job.size
            if diff < min_diff:
                min_diff = diff
                best_block_index = i
    if best_block_index is not None:
        allocate_block(job, memory_blocks[best_block_index])
        return True
    return False


def allocate_block(job, block):
    """
    Allocates a memory block to a job.
    """
    block.is_allocated = True
    block.allocated_job = job
    job.start_time = current_time
    print(f"Time {current_time}ms: Allocated Job {job.id} to Memory Block {block.id}")


def process_jobs(memory_blocks, completed_jobs):
    """
    Process jobs in memory and return completed jobs.
    """
    internal_fragmentation = 0

    # Process running jobs
    for block in memory_blocks:
        if block.is_allocated:
            job = block.allocated_job
            job.remaining_time -= 1

            # Check if job has completed
            if job.remaining_time == 0:
                job.finish_time = current_time
                print(f"Time {current_time}s: Job {job.id} completed. Releasing Memory Block {block.id}")

                # Calculate internal fragmentation for this job
                fragment = block.size - job.size
                internal_fragmentation += fragment

                # Add to completed jobs
                completed_jobs.append(job)

                # Release memory block
                block.is_allocated = False
                block.allocated_job = None

    return internal_fragmentation


def print_memory_status(memory_blocks):
    """
    Print the current status of all memory blocks.
    """
    print("\nCurrent Memory Status:")
    for block in memory_blocks:
        if block.is_allocated:
            job = block.allocated_job
            print(f"  Block {block.id} ({block.size}): Job {job.id} ({job.size}) - {job.remaining_time}ms remaining")
        else:
            print(f"  Block {block.id} ({block.size}): Free")


def run_simulation(jobs, memory_blocks, allocation_strategy):
    """
    Runs the memory management simulation with a given allocation strategy.
    """
    global current_time
    current_time = 0

    job_queue = jobs.copy()
    waiting_jobs = []
    completed_jobs = []
    never_allocated_jobs = []

    total_internal_fragmentation = 0
    peak_queue_length = 0

    strategy_name = allocation_strategy.__name__.replace('_', ' ').title()
    print(f"\n{'='*50}")
    print(f"Starting {strategy_name} Simulation")
    print(f"{'='*50}")

    MAX_SIMULATION_TIME = 10000

    # Continue simulation until all jobs are completed
    while job_queue or waiting_jobs or any(block.is_allocated for block in memory_blocks):
        print(f"\nTime: {current_time}s")

        # 1. Update waiting time for jobs in waiting queue
        for job in waiting_jobs:
            job.waiting_time += 1

        # 2. Process jobs in memory and handle completed jobs
        internal_frag = process_jobs(memory_blocks, completed_jobs)
        total_internal_fragmentation += internal_frag

        # 3. Try to allocate waiting jobs
        waiting_jobs_copy = waiting_jobs.copy()
        for job in waiting_jobs_copy:
            if allocation_strategy(job, memory_blocks):
                waiting_jobs.remove(job)
                print(f"Time {current_time}s: Allocated waiting Job {job.id}")

        # 4. Handle arriving jobs
        arrived_jobs = [job for job in job_queue if job.arrival_time <= current_time]
        for job in arrived_jobs:
            job_queue.remove(job)
            if not can_be_allocated(job, memory_blocks):
                print(f"Job {job.id} is too large for any memory block and will never be allocated.")
                never_allocated_jobs.append(job)
                continue
            if allocation_strategy(job, memory_blocks):
                print(f"Time {current_time}ms: Job {job.id} arrived and was allocated immediately")
            else:
                waiting_jobs.append(job)
                print(f"Time {current_time}ms: Job {job.id} arrived and was added to waiting queue")

        # 5. Track peak queue length
        peak_queue_length = max(peak_queue_length, len(waiting_jobs))

        # 6. Print current memory status
        if any(block.is_allocated for block in memory_blocks) or waiting_jobs:
            print_memory_status(memory_blocks)
            if waiting_jobs:
                print(f"Waiting Queue: {[f'Job {j.id}' for j in waiting_jobs]}")

        # 7. Advance time if there's still work to do
        current_time += 1

        # Optional: Add a time limit to prevent infinite loops
        if current_time > MAX_SIMULATION_TIME:
            print("Simulation time limit reached. Some jobs may not have completed.")
            break

    # Calculate statistics
    total_jobs = len(completed_jobs)
    if total_jobs > 0:
        total_turnaround_time = sum(job.finish_time - job.arrival_time for job in completed_jobs)
        total_waiting_time = sum(job.waiting_time for job in completed_jobs)

        avg_turnaround_time = total_turnaround_time / total_jobs
        avg_waiting_time = total_waiting_time / total_jobs
        avg_internal_fragmentation = total_internal_fragmentation / total_jobs
        throughput = total_jobs / current_time if current_time > 0 else 0

        # Print statistics
        print(f"\n{'='*50}")
        print(f"{strategy_name} Simulation Results:")
        print(f"{'='*50}")
        print(f"Simulation ended at time: {current_time}ms")
        print(f"Total jobs completed: {total_jobs}")
        print(f"Average waiting time: {avg_waiting_time:.2f}ms")
        print(f"Average turnaround time: {avg_turnaround_time:.2f}ms")
        print(f"Throughput: {throughput:.4f} jobs/ms")
        print(f"Average internal fragmentation: {avg_internal_fragmentation:.2f} bytes per job")
        print(f"Peak waiting queue length: {peak_queue_length}")

        if waiting_jobs:
            print(f"\nJobs still waiting at end of simulation: {[job.id for job in waiting_jobs]}")
        if never_allocated_jobs:
            print(f"\nJobs that could never be allocated: {[job.id for job in never_allocated_jobs]}")
        incomplete_jobs = [block.allocated_job for block in memory_blocks if block.is_allocated]
        if incomplete_jobs:
            print(f"\nJobs still running at end of simulation: {[job.id for job in incomplete_jobs]}")

        for job in completed_jobs:
            print(f"Job {job.id}: Waiting Time = {job.waiting_time}, Completion Time = {job.finish_time}")

        return {
            "strategy": strategy_name,
            "avg_waiting_time": avg_waiting_time,
            "avg_turnaround_time": avg_turnaround_time,
            "throughput": throughput,
            "avg_internal_fragmentation": avg_internal_fragmentation,
            "peak_queue_length": peak_queue_length
        }
    else:
        print("No jobs completed in simulation")
        return None


def compare_strategies(results):
    """
    Compare the results of different allocation strategies.
    """
    print("\n" + "="*60)
    print("Strategy Comparison")
    print("="*60)

    headers = ["Strategy", "Avg Wait", "Avg Turnaround", "Throughput", "Internal Frag", "Peak Queue"]
    print(f"{headers[0]:<15} {headers[1]:<10} {headers[2]:<15} {headers[3]:<12} {headers[4]:<15} {headers[5]:<10}")
    print("-"*60)

    for result in results:
        if result:
            print(f"{result['strategy']:<15} {result['avg_waiting_time']:<10.2f} "
                  f"{result['avg_turnaround_time']:<15.2f} {result['throughput']:<12.4f} "
                  f"{result['avg_internal_fragmentation']:<15.2f} {result['peak_queue_length']:<10}")


def can_be_allocated(job, memory_blocks):
    return any(block.size >= job.size for block in memory_blocks)


if __name__ == "__main__":
    current_time = 0
    results = []

    # Run First-Fit Simulation
    jobs = initialize_jobs()
    memory_blocks = initialize_memory_blocks()
    results.append(run_simulation(jobs, memory_blocks, first_fit))

    # Run Worst-Fit Simulation
    jobs = initialize_jobs()
    memory_blocks = initialize_memory_blocks()
    results.append(run_simulation(jobs, memory_blocks, worst_fit))

    # Run Best-Fit Simulation
    jobs = initialize_jobs()
    memory_blocks = initialize_memory_blocks()
    results.append(run_simulation(jobs, memory_blocks, best_fit))

    # Compare strategies
    compare_strategies(results)
