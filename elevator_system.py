from typing import Dict, Any, Optional, Tuple, List
from elevator_controller import ElevatorController
from queue_manager import QueueManager
from emergency_handler import EmergencyHandler
from constants import Direction, DoorState


class ElevatorSystem:
    """
    Central coordinator for the elevator system.
    Manages the controller, queue manager, and emergency handler.
    """
    
    def __init__(
        self, 
        num_floors: int = 10, 
        start_floor: int = 1, 
        start_direction: str | Direction = Direction.UP
    ) -> None:
        self.num_floors: int = num_floors
        self.controller = ElevatorController(num_floors, start_floor)
        
        # Convert string direction to enum
        if isinstance(start_direction, str):
            start_direction = Direction(start_direction)
        self.controller.set_direction(start_direction)
        
        self.queue_manager = QueueManager(num_floors)
        self.emergency_handler = EmergencyHandler(self.queue_manager)
        
        # Track current emergency request being handled
        self.current_emergency_pickup: Optional[Tuple[int, int]] = None
        self.current_emergency_destination: Optional[Tuple[int, int]] = None
        
        # Simulation state
        self.is_paused: bool = False
        self.speed_multiplier: float = 1.0
        
        # Event log for recent activities
        self.event_log: List[str] = []
        self.max_log_entries: int = 100
        
    def log_event(self, message: str) -> None:
        """Add an event to the log."""
        self.event_log.append(message)
        if len(self.event_log) > self.max_log_entries:
            self.event_log.pop(0)
    
    def add_internal_request(self, floor: int) -> bool:
        """Add internal request (button pressed inside elevator)."""
        if self.emergency_handler.is_emergency_mode():
            return False
        result = self.queue_manager.add_internal_request(floor)
        if result:
            self.log_event(f"Internal request: Floor {floor}")
        return result
    
    def add_external_request(self, floor: int, direction: str | Direction) -> bool:
        """Add external request (UP/DOWN button pressed)."""
        if self.emergency_handler.is_emergency_mode():
            return False
        result = self.queue_manager.add_external_request(floor, direction)
        if result:
            self.log_event(f"External {direction} request: Floor {floor}")
        return result
    
    def add_emergency_request(self, from_floor: int, to_floor: int) -> bool:
        """Add emergency request."""
        result = self.queue_manager.add_emergency_request(from_floor, to_floor)
        if result:
            self.emergency_handler.trigger_emergency()
            self.log_event(f"🚨 EMERGENCY: Floor {from_floor} → Floor {to_floor}")
        return result
    
    def get_next_target(self) -> Optional[int]:
        """
        Determine the next target floor based on current state.
        Priority: Emergency requests > Normal requests
        """
        current_floor = self.controller.get_current_floor()
        current_direction = self.controller.get_direction()
        
        # If we're currently handling an emergency destination, continue to it
        if self.current_emergency_destination:
            from_floor, to_floor = self.current_emergency_destination
            if current_floor != to_floor:
                return to_floor
        
        # If we're currently handling an emergency pickup, continue to it
        if self.current_emergency_pickup:
            from_floor, to_floor = self.current_emergency_pickup
            if current_floor != from_floor:
                return from_floor
        
        # Check for emergency requests first
        if self.emergency_handler.is_emergency_mode() and self.queue_manager.has_emergency_requests():
            target, is_pickup = self.emergency_handler.get_next_emergency_target(
                current_floor, current_direction
            )
            if target is not None:
                if is_pickup:
                    # Find which emergency request this pickup is for
                    group_a, group_b, group_c = self.emergency_handler.sort_emergency_requests(
                        current_floor, current_direction
                    )
                    if group_a:
                        self.current_emergency_pickup = group_a[0]
                    elif group_b:
                        self.current_emergency_pickup = group_b[0]
                    elif group_c:
                        self.current_emergency_pickup = group_c[0]
                return target
        
        # Handle normal requests
        if not self.emergency_handler.is_emergency_mode():
            return self._get_next_normal_target(current_floor, current_direction)
        
        return None
    
    def _get_next_normal_target(
        self, 
        current_floor: int, 
        current_direction: Direction
    ) -> Optional[int]:
        """Get next target for normal (non-emergency) operation."""
        # Check internal requests first
        if self.queue_manager.internal_requests:
            if current_direction == Direction.UP:
                # Find next floor above current
                candidates = [f for f in self.queue_manager.internal_requests if f > current_floor]
                if candidates:
                    return min(candidates)
                # No floors above, check if we should reverse
                if self.queue_manager.internal_requests:
                    return max(self.queue_manager.internal_requests)
                    
            elif current_direction == Direction.DOWN:
                # Find next floor below current
                candidates = [f for f in self.queue_manager.internal_requests if f < current_floor]
                if candidates:
                    return max(candidates)
                # No floors below, check if we should reverse
                if self.queue_manager.internal_requests:
                    return min(self.queue_manager.internal_requests)
                    
            else:  # IDLE
                if self.queue_manager.internal_requests:
                    # Go to closest floor
                    closest = min(self.queue_manager.internal_requests, 
                                key=lambda x: abs(x - current_floor))
                    return closest
        
        # Check external requests
        if current_direction == Direction.UP:
            # Check external UP requests
            candidates = [f for f in self.queue_manager.external_up_requests if f > current_floor]
            if candidates:
                return min(candidates)
            # Check external DOWN requests (need to reverse)
            if self.queue_manager.external_down_requests:
                return max(self.queue_manager.external_down_requests)
            # Check internal requests in opposite direction
            if self.queue_manager.internal_requests:
                return max(self.queue_manager.internal_requests)
                
        elif current_direction == Direction.DOWN:
            # Check external DOWN requests
            candidates = [f for f in self.queue_manager.external_down_requests if f < current_floor]
            if candidates:
                return max(candidates)
            # Check external UP requests (need to reverse)
            if self.queue_manager.external_up_requests:
                return min(self.queue_manager.external_up_requests)
            # Check internal requests in opposite direction
            if self.queue_manager.internal_requests:
                return min(self.queue_manager.internal_requests)
                
        else:  # IDLE
            # Check all external requests
            all_external = list(self.queue_manager.external_up_requests) + \
                         list(self.queue_manager.external_down_requests)
            if all_external:
                closest = min(all_external, key=lambda x: abs(x - current_floor))
                return closest
        
        return None
    
    def step(self) -> Tuple[bool, Optional[str]]:
        """
        Execute one simulation step.
        Returns: (arrived_at_floor, message)
        """
        if self.is_paused:
            return False, None
            
        current_floor = self.controller.get_current_floor()
        
        # Check if we've arrived at a floor
        arrived = self.controller.step()
        
        if arrived:
            new_floor = self.controller.get_current_floor()
            message = f"Arrived at Floor {new_floor}"
            
            # Handle emergency requests
            if self.emergency_handler.is_emergency_mode():
                should_open_doors = False
                
                # Check if we're at a pickup point
                if self.current_emergency_pickup:
                    from_floor, to_floor = self.current_emergency_pickup
                    if new_floor == from_floor:
                        # Picked up, now go to destination
                        self.current_emergency_destination = self.current_emergency_pickup
                        self.current_emergency_pickup = None
                        message += f" [🚨 Emergency Pickup]"
                        self.controller.add_passenger()
                        should_open_doors = True
                
                # Check if we're at a destination
                if self.current_emergency_destination:
                    from_floor, to_floor = self.current_emergency_destination
                    if new_floor == to_floor:
                        # Reached destination, complete the emergency
                        self.queue_manager.remove_emergency_request(from_floor, to_floor)
                        self.emergency_handler.complete_emergency_request(from_floor, to_floor)
                        self.current_emergency_destination = None
                        message += f" [✅ Emergency Complete: {from_floor}→{to_floor}]"
                        self.controller.remove_passenger()
                        should_open_doors = True
                
                # Only open doors at emergency stops
                if should_open_doors:
                    self.controller.open_doors()
            
            # Handle normal requests
            if not self.emergency_handler.is_emergency_mode():
                should_open_doors = False
                
                # Remove internal request if present
                if new_floor in self.queue_manager.internal_requests:
                    self.queue_manager.remove_internal_request(new_floor)
                    message += " [Internal Served]"
                    self.controller.remove_passenger()
                    should_open_doors = True
                
                # Remove external requests if present
                current_dir = self.controller.get_direction()
                if new_floor in self.queue_manager.external_up_requests:
                    self.queue_manager.remove_external_request(new_floor, "UP")
                    message += " [External ↑ Served]"
                    self.controller.add_passenger()
                    should_open_doors = True
                if new_floor in self.queue_manager.external_down_requests:
                    self.queue_manager.remove_external_request(new_floor, "DOWN")
                    message += " [External ↓ Served]"
                    self.controller.add_passenger()
                    should_open_doors = True
                
                # Open doors when serving requests
                if should_open_doors:
                    self.controller.open_doors()
            
            self.log_event(message)
            
            # Determine next target
            next_target = self.get_next_target()
            if next_target is not None:
                self.controller.move_to_floor(next_target)
            else:
                self.controller.set_direction(Direction.IDLE)
            
            return True, message
        
        # Still moving
        return False, None
    
    def update(self) -> Tuple[bool, Optional[str]]:
        """Update the elevator system - called periodically."""
        if self.is_paused:
            return False, None
            
        # If no target is set, find one
        if self.controller.target_floor is None:
            next_target = self.get_next_target()
            if next_target is not None:
                self.controller.move_to_floor(next_target)
        
        # Execute step
        return self.step()
    
    def pause(self) -> None:
        """Pause the simulation."""
        self.is_paused = True
    
    def resume(self) -> None:
        """Resume the simulation."""
        self.is_paused = False
    
    def toggle_pause(self) -> bool:
        """Toggle pause state. Returns new pause state."""
        self.is_paused = not self.is_paused
        return self.is_paused
    
    def set_speed(self, multiplier: float) -> None:
        """Set simulation speed multiplier."""
        self.speed_multiplier = max(0.1, min(3.0, multiplier))
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status for display."""
        return {
            'floor': self.controller.get_current_floor(),
            'direction': str(self.controller.get_direction()),
            'direction_enum': self.controller.get_direction(),
            'door_state': str(self.controller.get_door_state()),
            'emergency_mode': self.emergency_handler.is_emergency_mode(),
            'has_emergency': self.queue_manager.has_emergency_requests(),
            'emergency_count': len(self.queue_manager.emergency_requests),
            'normal_requests': self.queue_manager.get_all_requests(),
            'is_paused': self.is_paused,
            'speed': self.speed_multiplier,
            'passengers': self.controller.get_passenger_count(),
            'max_capacity': self.controller.stats.max_capacity,
            'target_floor': self.controller.target_floor
        }
    
    def get_detailed_status(self) -> Dict[str, Any]:
        """Get detailed status including statistics and pending requests."""
        status = self.get_status()
        status.update({
            'stats': {
                'floors_traveled': self.controller.stats.total_floors_traveled,
                'requests_served': self.queue_manager.stats.total_requests_served,
                'normal_served': self.queue_manager.stats.normal_requests_served,
                'emergency_served': self.queue_manager.stats.emergency_requests_served,
                'average_wait': self.queue_manager.stats.average_wait_time,
            },
            'pending_requests': self.queue_manager.get_pending_requests_info(),
            'emergency_groups': self.emergency_handler.get_groups_info(
                self.controller.get_current_floor(),
                self.controller.get_direction()
            ) if self.emergency_handler.is_emergency_mode() else None,
            'recent_events': self.event_log[-10:] if self.event_log else []
        })
        return status
