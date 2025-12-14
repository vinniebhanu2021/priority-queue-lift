from elevator_system import ElevatorSystem
from constants import Direction
import time
import sys

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')


def print_header(text: str, char: str = "=") -> None:
    """Print a formatted header."""
    print(f"\n{char * 60}")
    print(f"  {text}")
    print(f"{char * 60}\n")


def print_status(step: int, message: str, status: dict) -> None:
    """Print formatted step status."""
    emergency_indicator = "[!]" if status['emergency_mode'] else "[OK]"
    print(f"Step {step:2d}: {message}")
    print(f"         {emergency_indicator} Floor: {status['floor']}, "
          f"Direction: {status['direction']}, "
          f"Emergency: {'ON' if status['emergency_mode'] else 'OFF'}")


def test_section_7_scenario() -> None:
    """Test the comprehensive scenario from Section 7."""
    print_header("Section 7 Comprehensive Scenario Test")
    
    # Initialize elevator at Floor 3, Direction UP
    elevator = ElevatorSystem(num_floors=10, start_floor=3, start_direction=Direction.UP)
    
    print(f"Initial state:")
    print(f"  * Floor: {elevator.controller.get_current_floor()}")
    print(f"  * Direction: {elevator.controller.get_direction()}")
    
    # Add normal requests
    print("\n[NORMAL] Adding normal requests:")
    elevator.add_external_request(4, "UP")
    print("  * External UP request at Floor 4")
    elevator.add_external_request(6, "DOWN")
    print("  * External DOWN request at Floor 6")
    elevator.add_external_request(7, "UP")
    print("  * External UP request at Floor 7")
    
    # Add emergency requests
    print("\n[EMERGENCY] Adding emergency requests:")
    elevator.add_emergency_request(4, 10)
    print("  * Emergency: Floor 4 -> Floor 10")
    elevator.add_emergency_request(2, 1)
    print("  * Emergency: Floor 2 -> Floor 1")
    
    print_header("Expected Behavior", "-")
    print("  1. Emergency mode activated - normal requests paused")
    print("  2. Go to Floor 4 (pickup for emergency 4->10) - Group A")
    print("  3. Go to Floor 10 (destination for emergency 4->10)")
    print("  4. Reverse direction, go to Floor 2 (pickup for emergency 2->1) - Group B")
    print("  5. Go to Floor 1 (destination for emergency 2->1)")
    print("  6. Resume normal requests: Floor 6 (DOWN), Floor 7 (UP)")
    
    print_header("Simulation Output", "-")
    
    # Run simulation
    step_count = 0
    max_steps = 50  # Prevent infinite loops
    last_floor = elevator.controller.get_current_floor()
    
    while step_count < max_steps:
        step_count += 1
        arrived, message = elevator.update()
        
        if message:
            status = elevator.get_status()
            print_status(step_count, message, status)
            
            # Check if we've completed all requests
            if (not status['emergency_mode'] and 
                not elevator.queue_manager.has_normal_requests() and
                str(elevator.controller.get_direction()) == "IDLE"):
                print("\n[SUCCESS] All requests completed!")
                break
        
        # Detect if elevator is stuck
        current_floor = elevator.controller.get_current_floor()
        if current_floor == last_floor and step_count > 5:
            # Check if there's nothing to do
            if elevator.controller.target_floor is None:
                if not elevator.queue_manager.has_normal_requests() and \
                   not elevator.queue_manager.has_emergency_requests():
                    print("\n[SUCCESS] All requests completed!")
                    break
        last_floor = current_floor
        
        time.sleep(0.05)  # Small delay for readability
    
    # Print final statistics
    print_header("Final Statistics", "-")
    stats = elevator.get_detailed_status()['stats']
    print(f"  * Floors Traveled: {stats['floors_traveled']}")
    print(f"  * Normal Requests Served: {stats['normal_served']}")
    print(f"  * Emergency Requests Served: {stats['emergency_served']}")
    print(f"  * Total Requests Served: {stats['requests_served']}")
    
    print_header("Test Completed")


def test_single_emergency() -> None:
    """Test a single emergency request."""
    print_header("Single Emergency Test")
    
    elevator = ElevatorSystem(num_floors=10, start_floor=5, start_direction=Direction.UP)
    
    print("Adding internal request to Floor 8")
    elevator.add_internal_request(8)
    
    print("Adding emergency: Floor 2 -> Floor 9")
    elevator.add_emergency_request(2, 9)
    
    print("\nSimulating...")
    for _ in range(30):
        arrived, message = elevator.update()
        if message:
            status = elevator.get_status()
            print(f"  {message}")
            if str(elevator.controller.get_direction()) == "IDLE":
                break
        time.sleep(0.02)
    
    print("\n[SUCCESS] Test completed")


if __name__ == "__main__":
    test_section_7_scenario()
    print("\n" + "=" * 60 + "\n")
    test_single_emergency()
