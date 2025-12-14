from typing import List, Tuple, Optional
from constants import Direction, EmergencyRequest


class EmergencyHandler:
    """Manages emergency request detection, triggering, and prioritization."""
    
    def __init__(self, queue_manager) -> None:
        self.queue_manager = queue_manager
        self.emergency_mode: bool = False
        self.emergency_count: int = 0
        
    def trigger_emergency(self) -> None:
        """Trigger emergency mode - pause all normal requests."""
        if not self.emergency_mode:
            self.emergency_mode = True
            self.queue_manager.pause_normal_requests()
            self.emergency_count += 1
    
    def end_emergency_mode(self) -> None:
        """End emergency mode - resume normal requests."""
        if self.emergency_mode and not self.queue_manager.has_emergency_requests():
            self.emergency_mode = False
            self.queue_manager.resume_normal_requests()
    
    def is_emergency_mode(self) -> bool:
        """Check if emergency mode is active."""
        return self.emergency_mode
    
    def get_emergency_count(self) -> int:
        """Get the total number of emergencies triggered."""
        return self.emergency_count
    
    def sort_emergency_requests(
        self, 
        current_floor: int, 
        current_direction: Direction | str
    ) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Sort emergency requests into groups:
        - Group A: In current direction (from_floor is reachable in current direction)
        - Group B: Opposite direction (from_floor requires direction change)
        - Group C: Future (edge cases)
        
        Returns: (group_a, group_b, group_c) as lists of (from_floor, to_floor) tuples
        """
        # Convert direction to enum if string
        if isinstance(current_direction, str):
            try:
                current_direction = Direction(current_direction)
            except ValueError:
                current_direction = Direction.IDLE
        
        group_a: List[Tuple[int, int]] = []  # Current direction
        group_b: List[Tuple[int, int]] = []  # Opposite direction
        group_c: List[Tuple[int, int]] = []  # Edge cases
        
        for emergency in self.queue_manager.emergency_requests:
            if isinstance(emergency, EmergencyRequest):
                from_floor = emergency.from_floor
                to_floor = emergency.to_floor
            else:
                from_floor, to_floor = emergency
            
            if current_direction == Direction.UP:
                # Group A: from_floor is above current floor and in current direction
                if from_floor > current_floor:
                    group_a.append((from_floor, to_floor))
                # Group B: from_floor is below current floor (opposite direction)
                elif from_floor < current_floor:
                    group_b.append((from_floor, to_floor))
                # If from_floor == current_floor, we're already there, prioritize by destination
                elif from_floor == current_floor:
                    if to_floor > current_floor:
                        group_a.append((from_floor, to_floor))
                    else:
                        group_b.append((from_floor, to_floor))
                else:
                    group_c.append((from_floor, to_floor))
                    
            elif current_direction == Direction.DOWN:
                # Group A: from_floor is below current floor and in current direction
                if from_floor < current_floor:
                    group_a.append((from_floor, to_floor))
                # Group B: from_floor is above current floor (opposite direction)
                elif from_floor > current_floor:
                    group_b.append((from_floor, to_floor))
                # If from_floor == current_floor, we're already there
                elif from_floor == current_floor:
                    if to_floor < current_floor:
                        group_a.append((from_floor, to_floor))
                    else:
                        group_b.append((from_floor, to_floor))
                else:
                    group_c.append((from_floor, to_floor))
                    
            else:  # IDLE
                # When idle, determine direction based on from_floor position
                if from_floor > current_floor:
                    group_a.append((from_floor, to_floor))
                elif from_floor < current_floor:
                    group_b.append((from_floor, to_floor))
                else:  # from_floor == current_floor
                    # Already at pickup point, determine by destination
                    if to_floor > current_floor:
                        group_a.append((from_floor, to_floor))
                    else:
                        group_b.append((from_floor, to_floor))
        
        # Sort groups by priority
        # Group A: sort by from_floor (ascending for UP, descending for DOWN)
        if current_direction == Direction.UP:
            group_a.sort(key=lambda x: x[0])  # Sort by from_floor ascending
        elif current_direction == Direction.DOWN:
            group_a.sort(key=lambda x: x[0], reverse=True)  # Sort by from_floor descending
        else:
            group_a.sort(key=lambda x: abs(x[0] - current_floor))  # Closest first when idle
        
        # Group B: sort by from_floor (opposite of current direction)
        if current_direction == Direction.UP:
            group_b.sort(key=lambda x: x[0], reverse=True)  # Descending (going down)
        elif current_direction == Direction.DOWN:
            group_b.sort(key=lambda x: x[0])  # Ascending (going up)
        else:
            group_b.sort(key=lambda x: abs(x[0] - current_floor))  # Closest first when idle
        
        # Group C: sort by to_floor
        group_c.sort(key=lambda x: abs(x[1] - current_floor))
        
        return group_a, group_b, group_c
    
    def get_next_emergency_target(
        self, 
        current_floor: int, 
        current_direction: Direction | str
    ) -> Tuple[Optional[int], bool]:
        """
        Get the next target floor for emergency handling.
        Returns: (target_floor, is_pickup) where is_pickup indicates if we're going to pickup or destination
        """
        if not self.queue_manager.has_emergency_requests():
            return None, False
        
        group_a, group_b, group_c = self.sort_emergency_requests(current_floor, current_direction)
        
        # Priority: Group A > Group B > Group C
        if group_a:
            # Return the from_floor (pickup point) of the first request in Group A
            from_floor, to_floor = group_a[0]
            # Check if we're already at the pickup point
            if current_floor == from_floor:
                return to_floor, False  # Go to destination
            else:
                return from_floor, True  # Go to pickup point
        
        if group_b:
            from_floor, to_floor = group_b[0]
            if current_floor == from_floor:
                return to_floor, False
            else:
                return from_floor, True
        
        if group_c:
            from_floor, to_floor = group_c[0]
            if current_floor == from_floor:
                return to_floor, False
            else:
                return from_floor, True
        
        return None, False
    
    def get_groups_info(
        self, 
        current_floor: int, 
        current_direction: Direction | str
    ) -> dict:
        """Get information about the current emergency groups for display."""
        group_a, group_b, group_c = self.sort_emergency_requests(current_floor, current_direction)
        return {
            'group_a': group_a,
            'group_b': group_b,
            'group_c': group_c,
            'total': len(group_a) + len(group_b) + len(group_c)
        }
    
    def complete_emergency_request(self, from_floor: int, to_floor: int) -> None:
        """Mark an emergency request as completed."""
        self.queue_manager.remove_emergency_request(from_floor, to_floor)
        # Check if we should end emergency mode
        if not self.queue_manager.has_emergency_requests():
            self.end_emergency_mode()
