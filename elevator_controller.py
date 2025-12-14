from typing import Optional
from constants import Direction, DoorState, ElevatorStats


class ElevatorController:
    """Controls the physical state and movement of the elevator."""
    
    def __init__(self, num_floors: int = 10, start_floor: int = 1) -> None:
        self.num_floors: int = num_floors
        self.current_floor: int = start_floor
        self.direction: Direction = Direction.IDLE
        self.door_state: DoorState = DoorState.CLOSED
        self.is_moving: bool = False
        self.target_floor: Optional[int] = None
        self.stats: ElevatorStats = ElevatorStats()
        
        # Door timing (in simulation steps)
        self.door_timer: int = 0
        self.door_open_duration: int = 2  # Steps to keep door open
        
    def get_current_floor(self) -> int:
        """Get the current floor number."""
        return self.current_floor
    
    def get_direction(self) -> Direction:
        """Get the current direction."""
        return self.direction
    
    def get_direction_str(self) -> str:
        """Get direction as string for display."""
        return str(self.direction)
    
    def get_door_state(self) -> DoorState:
        """Get the current door state."""
        return self.door_state
    
    def set_direction(self, direction: Direction | str) -> None:
        """Set direction: Direction.UP, Direction.DOWN, or Direction.IDLE"""
        if isinstance(direction, str):
            direction = Direction(direction)
        self.direction = direction
    
    def open_doors(self) -> None:
        """Start opening the doors."""
        if self.door_state == DoorState.CLOSED:
            self.door_state = DoorState.OPENING
            self.door_timer = 1
    
    def close_doors(self) -> None:
        """Start closing the doors."""
        if self.door_state == DoorState.OPEN:
            self.door_state = DoorState.CLOSING
            self.door_timer = 1
    
    def update_doors(self) -> bool:
        """
        Update door state based on timer.
        Returns True if doors are currently in transition.
        """
        if self.door_state == DoorState.OPENING:
            self.door_timer -= 1
            if self.door_timer <= 0:
                self.door_state = DoorState.OPEN
                self.door_timer = self.door_open_duration
            return True
            
        elif self.door_state == DoorState.OPEN:
            self.door_timer -= 1
            if self.door_timer <= 0:
                self.door_state = DoorState.CLOSING
                self.door_timer = 1
            return True
            
        elif self.door_state == DoorState.CLOSING:
            self.door_timer -= 1
            if self.door_timer <= 0:
                self.door_state = DoorState.CLOSED
            return True
            
        return False
    
    def can_move(self) -> bool:
        """Check if elevator can move (doors must be closed)."""
        return self.door_state == DoorState.CLOSED
    
    def move_to_floor(self, target_floor: int) -> None:
        """Set target floor and determine direction."""
        if target_floor == self.current_floor:
            self.direction = Direction.IDLE
            self.target_floor = None
            return
        
        if not 1 <= target_floor <= self.num_floors:
            return  # Invalid floor
        
        self.target_floor = target_floor
        if target_floor > self.current_floor:
            self.direction = Direction.UP
        else:
            self.direction = Direction.DOWN
        self.is_moving = True
    
    def step(self) -> bool:
        """
        Simulate one step of elevator movement.
        Returns True if arrived at target floor.
        """
        # Handle door transitions first
        if self.door_state != DoorState.CLOSED:
            self.update_doors()
            return False
        
        if self.target_floor is None:
            self.is_moving = False
            self.direction = Direction.IDLE
            return False
        
        if self.current_floor == self.target_floor:
            self.is_moving = False
            self.target_floor = None
            # Note: Don't auto-open doors here - let the system control this
            # based on whether we should serve a request at this floor
            return True  # Arrived at target
        
        # Move one floor
        if self.direction == Direction.UP:
            self.current_floor += 1
            self.stats.total_floors_traveled += 1
        elif self.direction == Direction.DOWN:
            self.current_floor -= 1
            self.stats.total_floors_traveled += 1
        
        return False  # Still moving
    
    def is_at_floor(self, floor: int) -> bool:
        """Check if elevator is at a specific floor."""
        return self.current_floor == floor
    
    def get_next_floor(self) -> Optional[int]:
        """Get the next floor the elevator will reach."""
        if self.target_floor is None:
            return None
        if self.direction == Direction.UP:
            return min(self.current_floor + 1, self.target_floor)
        elif self.direction == Direction.DOWN:
            return max(self.current_floor - 1, self.target_floor)
        return None
    
    def get_distance_to(self, floor: int) -> int:
        """Calculate distance to a floor."""
        return abs(self.current_floor - floor)
    
    def add_passenger(self) -> bool:
        """Add a passenger to the elevator."""
        return self.stats.add_passenger()
    
    def remove_passenger(self) -> bool:
        """Remove a passenger from the elevator."""
        return self.stats.remove_passenger()
    
    def get_passenger_count(self) -> int:
        """Get current passenger count."""
        return self.stats.current_passengers
    
    def is_full(self) -> bool:
        """Check if elevator is at capacity."""
        return self.stats.current_passengers >= self.stats.max_capacity
