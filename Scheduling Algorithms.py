class Process:
    def __init__(self, pid, arrival_time, burst_time, priority=0):
        self.pid = pid
        self.arrival_time = arrival_time
        self.burst_time = burst_time
        self.priority = priority
        self.remaining_time = burst_time
        self.completion_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.response_time = -1

class CPUScheduler:
    def __init__(self, processes):
        self.processes = processes
        self.gantt_chart = []
        self.timeline = []
        
    def reset_processes(self):
        """Reset process states for new simulation"""
        for process in self.processes:
            process.remaining_time = process.burst_time
            process.completion_time = 0
            process.turnaround_time = 0
            process.waiting_time = 0
            process.response_time = -1
        self.gantt_chart = []
        self.timeline = []
    
    def fcfs(self):
        """First-Come, First-Served Scheduling"""
        self.reset_processes()
        # Sort by arrival time
        sorted_processes = sorted(self.processes, key=lambda x: x.arrival_time)
        
        current_time = 0
        for process in sorted_processes:
            if current_time < process.arrival_time:
                current_time = process.arrival_time
            
            # Response time is when process first gets CPU
            process.response_time = current_time - process.arrival_time
            
            # Add to Gantt chart
            self.gantt_chart.append(f"P{process.pid}")
            self.timeline.append(current_time)
            
            current_time += process.burst_time
            process.completion_time = current_time
            process.turnaround_time = process.completion_time - process.arrival_time
            process.waiting_time = process.turnaround_time - process.burst_time
        
        self.timeline.append(current_time)
    
    def spn(self):
        """Shortest Process Next (Non-preemptive)"""
        self.reset_processes()
        ready_queue = []
        completed = []
        current_time = 0
        
        while len(completed) < len(self.processes):
            # Add arriving processes to ready queue
            for process in self.processes:
                if (process.arrival_time <= current_time and 
                    process not in ready_queue and process not in completed):
                    ready_queue.append(process)
            
            if ready_queue:
                # Select process with shortest burst time
                current_process = min(ready_queue, key=lambda x: x.burst_time)
                ready_queue.remove(current_process)
                
                # Set response time if first time running
                if current_process.response_time == -1:
                    current_process.response_time = current_time - current_process.arrival_time
                
                # Add to Gantt chart
                self.gantt_chart.append(f"P{current_process.pid}")
                self.timeline.append(current_time)
                
                current_time += current_process.burst_time
                current_process.completion_time = current_time
                current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                completed.append(current_process)
            else:
                current_time += 1
        
        self.timeline.append(current_time)
    
    def srt(self):
        """Shortest Remaining Time (Preemptive)"""
        self.reset_processes()
        ready_queue = []
        completed = []
        current_time = 0
        current_process = None
        
        while len(completed) < len(self.processes):
            # Add arriving processes to ready queue
            for process in self.processes:
                if (process.arrival_time <= current_time and 
                    process not in ready_queue and process not in completed):
                    ready_queue.append(process)
            
            if ready_queue:
                # Select process with shortest remaining time
                shortest_process = min(ready_queue, key=lambda x: x.remaining_time)
                
                # Preemption check
                if current_process != shortest_process:
                    # Only add timeline entry if we're switching processes
                    if len(self.gantt_chart) > 0:  # If there was a previous process
                        self.timeline.append(current_time)
                    
                    current_process = shortest_process
                    self.gantt_chart.append(f"P{current_process.pid}")
                    
                    # Add start time only if this is the first process
                    if len(self.timeline) == 0:
                        self.timeline.append(current_time)
                    
                    # Set response time if first time running
                    if current_process.response_time == -1:
                        current_process.response_time = current_time - current_process.arrival_time
                
                # Execute for 1 time unit
                current_process.remaining_time -= 1
                current_time += 1
                
                # Check if process completed
                if current_process.remaining_time == 0:
                    current_process.completion_time = current_time
                    current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                    current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                    completed.append(current_process)
                    ready_queue.remove(current_process)
                    current_process = None
            else:
                current_time += 1
        
        # Add final timeline entry
        if self.timeline and self.timeline[-1] != current_time:
            self.timeline.append(current_time)
    
    def round_robin(self, quantum=3):
        """Round Robin Scheduling"""
        self.reset_processes()
        ready_queue = []
        completed = []
        current_time = 0
        
        while len(completed) < len(self.processes):
            # Add arriving processes to ready queue
            for process in self.processes:
                if (process.arrival_time <= current_time and 
                    process not in ready_queue and process not in completed):
                    ready_queue.append(process)
            
            if ready_queue:
                current_process = ready_queue.pop(0)
                
                # Set response time if first time running
                if current_process.response_time == -1:
                    current_process.response_time = current_time - current_process.arrival_time
                
                # Add to Gantt chart
                self.gantt_chart.append(f"P{current_process.pid}")
                self.timeline.append(current_time)
                
                # Execute for quantum time or remaining time
                execution_time = min(quantum, current_process.remaining_time)
                current_process.remaining_time -= execution_time
                current_time += execution_time
                
                # Check if process completed
                if current_process.remaining_time == 0:
                    current_process.completion_time = current_time
                    current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                    current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                    completed.append(current_process)
                else:
                    # Add back to ready queue if not completed
                    ready_queue.append(current_process)
            else:
                current_time += 1
        
        self.timeline.append(current_time)
    
    def priority_scheduling(self):
        """Priority Scheduling (Non-preemptive) - Lower number = Higher priority"""
        self.reset_processes()
        ready_queue = []
        completed = []
        current_time = 0
        
        while len(completed) < len(self.processes):
            # Add arriving processes to ready queue
            for process in self.processes:
                if (process.arrival_time <= current_time and 
                    process not in ready_queue and process not in completed):
                    ready_queue.append(process)
            
            if ready_queue:
                # Select process with highest priority (lowest number)
                current_process = min(ready_queue, key=lambda x: x.priority)
                ready_queue.remove(current_process)
                
                # Set response time if first time running
                if current_process.response_time == -1:
                    current_process.response_time = current_time - current_process.arrival_time
                
                # Add to Gantt chart
                self.gantt_chart.append(f"P{current_process.pid}")
                self.timeline.append(current_time)
                
                current_time += current_process.burst_time
                current_process.completion_time = current_time
                current_process.turnaround_time = current_process.completion_time - current_process.arrival_time
                current_process.waiting_time = current_process.turnaround_time - current_process.burst_time
                completed.append(current_process)
            else:
                current_time += 1
        
        self.timeline.append(current_time)
    
    def display_gantt_chart(self):
        """Display Gantt chart visualization"""
        if not self.gantt_chart:
            print("No scheduling data available.")
            return
        
        print("\nGantt Chart Visualization:")
        # Display process boxes
        chart_line = "| " + " | ".join(self.gantt_chart) + " |"
        print(chart_line)
        
        # Display timeline
        timeline_str = ""
        for i, time in enumerate(self.timeline):
            if i == 0:
                timeline_str += str(time)
            else:
                # Calculate spacing based on process name length
                # Use i-1 but ensure it's within gantt_chart bounds
                if i-1 < len(self.gantt_chart):
                    prev_process_len = len(self.gantt_chart[i-1])
                    spacing = " " * (prev_process_len + 2)  # +2 for "| "
                    timeline_str += spacing + str(time)
                else:
                    # If we're at the end, just add some default spacing
                    spacing = " " * 4  # Default spacing
                    timeline_str += spacing + str(time)
        
        print(timeline_str)
    
    def calculate_metrics(self):
        """Calculate and display performance metrics"""
        if not self.processes:
            return
        
        total_waiting_time = sum(p.waiting_time for p in self.processes)
        total_turnaround_time = sum(p.turnaround_time for p in self.processes)
        total_response_time = sum(p.response_time for p in self.processes)
        
        n = len(self.processes)
        avg_waiting_time = total_waiting_time / n
        avg_turnaround_time = total_turnaround_time / n
        avg_response_time = total_response_time / n
        
        print(f"\nPerformance Metrics:")
        print(f"Average Waiting Time: {avg_waiting_time:.2f}")
        print(f"Average Turnaround Time: {avg_turnaround_time:.2f}")
        print(f"Average Response Time: {avg_response_time:.2f}")
        
        return avg_waiting_time, avg_turnaround_time, avg_response_time
    
    def display_detailed_metrics(self):
        """Display detailed per-process metrics"""
        print(f"\nDetailed Process Metrics:")
        print(f"{'Process':<8} {'Arrival':<8} {'Burst':<6} {'Completion':<11} {'Turnaround':<11} {'Waiting':<8} {'Response':<8}")
        print("-" * 70)
        
        for process in sorted(self.processes, key=lambda x: x.pid):
            print(f"P{process.pid:<7} {process.arrival_time:<8} {process.burst_time:<6} "
                  f"{process.completion_time:<11} {process.turnaround_time:<11} "
                  f"{process.waiting_time:<8} {process.response_time:<8}")

def get_user_input():
    """Get process information from user"""
    try:
        n = int(input("Enter the number of processes: "))
        processes = []
        
        print("Enter the information of each process below ..")
        for i in range(n):
            print(f"Process {i+1}:")
            arrival_time = int(input("Arrival Time: "))
            burst_time = int(input("Burst Time: "))
            priority = int(input("Priority: "))
            
            process = Process(i+1, arrival_time, burst_time, priority)
            processes.append(process)
        
        return processes
    except ValueError:
        print("Invalid input. Please enter valid integers.")
        return None

def display_algorithm_menu():
    """Display scheduling algorithm options"""
    print("\nSelect Scheduling Algorithm:")
    print("1. First-Come, First-Served (FCFS)")
    print("2. Shortest Process Next (SPN)")
    print("3. Shortest Remaining Time (SRT)")
    print("4. Round Robin (RR)")
    print("5. Priority Scheduling (Non-Preemptive)")

def run_algorithm(scheduler, choice):
    """Run the selected algorithm"""
    try:
        if choice == 1:
            print("\n=== FIRST-COME, FIRST-SERVED (FCFS) ===")
            scheduler.fcfs()
        elif choice == 2:
            print("\n=== SHORTEST PROCESS NEXT (SPN) ===")
            scheduler.spn()
        elif choice == 3:
            print("\n=== SHORTEST REMAINING TIME (SRT) ===")
            scheduler.srt()
        elif choice == 4:
            print("\n=== ROUND ROBIN (RR) ===")
            quantum = int(input("Enter time quantum for Round Robin (recommended: 3): "))
            scheduler.round_robin(quantum)
        elif choice == 5:
            print("\n=== PRIORITY SCHEDULING (Non-Preemptive) ===")
            scheduler.priority_scheduling()
        else:
            print("Invalid choice. Please select 1-5.")
            return False
        
        # Display results
        scheduler.display_gantt_chart()
        scheduler.calculate_metrics()
        scheduler.display_detailed_metrics()
        return True
        
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return False

def display_test_data_menu():
    """Display test data options"""
    print("\nWould you like to:")
    print("1. Enter your own process data")
    print("2. Use predefined test data")
    
def get_test_data(test_set):
    """Return predefined test data sets"""
    test_data = {
        1: [  # Test Set 1: Basic Mixed Workload
            Process(1, 0, 6, 3),
            Process(2, 2, 8, 1),
            Process(3, 4, 7, 2),
            Process(4, 6, 3, 4),
            Process(5, 8, 4, 2)
        ],
        2: [  # Test Set 2: Simultaneous Arrivals
            Process(1, 0, 10, 2),
            Process(2, 0, 1, 1),
            Process(3, 0, 2, 3),
            Process(4, 0, 5, 1)
        ],
        3: [  # Test Set 3: Equal Burst Times
            Process(1, 0, 5, 4),
            Process(2, 1, 5, 2),
            Process(3, 2, 5, 1),
            Process(4, 3, 5, 3)
        ],
        4: [  # Test Set 4: High Priority Variation
            Process(1, 0, 4, 5),
            Process(2, 1, 3, 1),
            Process(3, 2, 6, 3),
            Process(4, 3, 2, 1),
            Process(5, 4, 8, 2),
            Process(6, 5, 1, 4)
        ],
        5: [  # Test Set 5: Large Burst Time Variation
            Process(1, 0, 20, 3),
            Process(2, 2, 1, 2),
            Process(3, 4, 15, 1),
            Process(4, 6, 2, 4),
            Process(5, 8, 1, 5)
        ]
    }
    return test_data.get(test_set, [])

def display_process_table(processes):
    """Display process information in table format"""
    print(f"\nProcess Information:")
    print(f"{'Process':<8} {'Arrival':<8} {'Burst':<6} {'Priority':<8}")
    print("-" * 32)
    
    for process in processes:
        print(f"P{process.pid:<7} {process.arrival_time:<8} {process.burst_time:<6} {process.priority:<8}")

def main():
    """Main function to run the CPU scheduler simulator"""
    print("=== CPU Scheduling Algorithms Simulator ===")
    
    # Ask user for input method
    display_test_data_menu()
    
    try:
        input_choice = int(input("Enter your choice (1-2): "))
        
        if input_choice == 1:
            # Get user input
            processes = get_user_input()
            if not processes:
                return
        elif input_choice == 2:
            # Use predefined test data
            print("\nAvailable Test Sets:")
            print("1. Basic Mixed Workload")
            print("2. Simultaneous Arrivals")
            print("3. Equal Burst Times")
            print("4. High Priority Variation")
            print("5. Large Burst Time Variation")
            
            test_choice = int(input("Select test set (1-5): "))
            processes = get_test_data(test_choice)
            if not processes:
                print("Invalid test set selection.")
                return
            
            # Display the selected  data
            test_names = {
                1: "Basic Mixed Workload",
                2: "Simultaneous Arrivals",
                3: "Equal Burst Times",
                4: "High Priority Variation",
                5: "Large Burst Time Variation"
            }
            print(f"\n=== TEST SET {test_choice}: {test_names[test_choice]} ===")
            display_process_table(processes)
        else:
            print("Invalid choice.")
            return
    
    except ValueError:
        print("Invalid input. Please enter a valid number.")
        return
    
    # Creeate scheduler
    scheduler = CPUScheduler(processes)
    
    # main algorithm testing loop
    while True:
        display_algorithm_menu()
        
        try:
            choice = int(input("Enter your choice (1-5): "))
            
            if run_algorithm(scheduler, choice):
                # Ask if user wants to try another algorithm
                try_again = input("\nWould you like to try another algorithm? (y/n): ").lower()
                if try_again != 'y':
                    break
            else:
                continue
                
        except ValueError:
            print("Invalid input. Please enter a valid number.")
            continue
    
    print("\nThank you for using the CPU Scheduling Simulator!")

if __name__ == "__main__":
    main()