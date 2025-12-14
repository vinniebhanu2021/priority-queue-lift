from typing import Set, List, Dict, Any, Optional
from dataclasses import dataclass, field
import time
from constants import Direction, EmergencyRequest, ElevatorStats


@dataclass
class RequestInfo:
    """Information about a pending request for display."""
    floor: int
    direction: Optional[str] = None
    request_time: float = field(default_factory=time.time)
    wait_time: float = 0.0


class QueueManager:
    """Manages all request queues with statistics tracking."""
    
    def __init__(self, num_floors: int = 10) -> None:
        self.num_floors: int = num_floors
        
        # Internal requests: floor numbers where someone pressed button inside
        self.internal_requests: Set[int] = set()
        
        # External requests: floor numbers for UP/DOWN calls
        self.external_up_requests: Set[int] = set()
        self.external_down_requests: Set[int] = set()
        
        # Emergency requests: list of EmergencyRequest objects
        self.emergency_requests: List[EmergencyRequest] = []
        
        # Paused normal requests (saved when emergency occurs)
        self.paused_internal: Set[int] = set()
        self.paused_external_up: Set[int] = set()
        self.paused_external_down: Set[int] = set()
        self.is_paused: bool = False
        
        # Request timestamps for wait time tracking
        self.request_times: Dict[str, float] = {}
        
        # Statistics
        self.stats = ElevatorStats()
        
    def _get_request_key(self, floor: int, req_type: str) -> str:
        """Generate a unique key for request tracking."""
        return f"{req_type}_{floor}"
    
    def add_internal_request(self, floor: int) -> bool:
        """
        Add an internal request (button pressed inside elevator).
        Returns True if request was added.
        """
        if not 1 <= floor <= self.num_floors:
            return False
            
        if self.is_paused:
            self.paused_internal.add(floor)
        else:
            if floor not in self.internal_requests:
                self.internal_requests.add(floor)
                self.request_times[self._get_request_key(floor, "internal")] = time.time()
        return True
    
    def add_external_request(self, floor: int, direction: str | Direction) -> bool:
        """
        Add an external request (UP or DOWN button pressed).
        Returns True if request was added.
        """
        if not 1 <= floor <= self.num_floors:
            return False
            
        if isinstance(direction, Direction):
            direction = str(direction)
            
        if self.is_paused:
            if direction == "UP":
                self.paused_external_up.add(floor)
            else:
                self.paused_external_down.add(floor)
        else:
            if direction == "UP":
                if floor not in self.external_up_requests:
                    self.external_up_requests.add(floor)
                    self.request_times[self._get_request_key(floor, "external_up")] = time.time()
            else:
                if floor not in self.external_down_requests:
                    self.external_down_requests.add(floor)
                    self.request_times[self._get_request_key(floor, "external_down")] = time.time()
        return True
    
    def add_emergency_request(self, from_floor: int, to_floor: int) -> bool:
        """
        Add an emergency request.
        Returns True if request was added.
        """
        if not (1 <= from_floor <= self.num_floors and 1 <= to_floor <= self.num_floors):
            return False
            
        emergency = EmergencyRequest(from_floor=from_floor, to_floor=to_floor)
        
        # Check for duplicates
        if emergency not in self.emergency_requests:
            self.emergency_requests.append(emergency)
            self.request_times[self._get_request_key(from_floor, f"emergency_{to_floor}")] = time.time()
        return True
    
    def pause_normal_requests(self) -> None:
        """Pause all normal requests and save them."""
        if not self.is_paused:
            self.paused_internal = self.internal_requests.copy()
            self.paused_external_up = self.external_up_requests.copy()
            self.paused_external_down = self.external_down_requests.copy()
            self.internal_requests.clear()
            self.external_up_requests.clear()
            self.external_down_requests.clear()
            self.is_paused = True
    
    def resume_normal_requests(self) -> None:
        """Resume normal requests after emergency is handled."""
        if self.is_paused:
            self.internal_requests = self.paused_internal.copy()
            self.external_up_requests = self.paused_external_up.copy()
            self.external_down_requests = self.paused_external_down.copy()
            self.paused_internal.clear()
            self.paused_external_up.clear()
            self.paused_external_down.clear()
            self.is_paused = False
    
    def remove_internal_request(self, floor: int) -> float:
        """
        Remove an internal request (elevator reached floor).
        Returns wait time for the request.
        """
        self.internal_requests.discard(floor)
        key = self._get_request_key(floor, "internal")
        wait_time = 0.0
        if key in self.request_times:
            wait_time = time.time() - self.request_times.pop(key)
            self.stats.total_wait_time += wait_time
            self.stats.normal_requests_served += 1
        return wait_time
    
    def remove_external_request(self, floor: int, direction: str | Direction) -> float:
        """
        Remove an external request (elevator reached floor).
        Returns wait time for the request.
        """
        if isinstance(direction, Direction):
            direction = str(direction)
            
        wait_time = 0.0
        if direction == "UP":
            self.external_up_requests.discard(floor)
            key = self._get_request_key(floor, "external_up")
        else:
            self.external_down_requests.discard(floor)
            key = self._get_request_key(floor, "external_down")
            
        if key in self.request_times:
            wait_time = time.time() - self.request_times.pop(key)
            self.stats.total_wait_time += wait_time
            self.stats.normal_requests_served += 1
        return wait_time
    
    def remove_emergency_request(self, from_floor: int, to_floor: int) -> float:
        """
        Remove an emergency request.
        Returns wait time for the request.
        """
        emergency = EmergencyRequest(from_floor=from_floor, to_floor=to_floor)
        if emergency in self.emergency_requests:
            self.emergency_requests.remove(emergency)
            
        key = self._get_request_key(from_floor, f"emergency_{to_floor}")
        wait_time = 0.0
        if key in self.request_times:
            wait_time = time.time() - self.request_times.pop(key)
            self.stats.total_wait_time += wait_time
            self.stats.emergency_requests_served += 1
        return wait_time
    
    def has_emergency_requests(self) -> bool:
        """Check if there are any emergency requests."""
        return len(self.emergency_requests) > 0
    
    def has_normal_requests(self) -> bool:
        """Check if there are any normal requests."""
        return (len(self.internal_requests) > 0 or 
                len(self.external_up_requests) > 0 or 
                len(self.external_down_requests) > 0)
    
    def has_paused_requests(self) -> bool:
        """Check if there are any paused normal requests."""
        return (len(self.paused_internal) > 0 or
                len(self.paused_external_up) > 0 or
                len(self.paused_external_down) > 0)
    
    def get_all_requests(self) -> Dict[str, Any]:
        """Get all current normal requests for display."""
        return {
            'internal': list(sorted(self.internal_requests)),
            'external_up': list(sorted(self.external_up_requests)),
            'external_down': list(sorted(self.external_down_requests, reverse=True))
        }
    
    def get_pending_requests_info(self) -> Dict[str, List[RequestInfo]]:
        """Get detailed info about all pending requests including wait times."""
        current_time = time.time()
        
        info = {
            'internal': [],
            'external_up': [],
            'external_down': [],
            'emergency': [],
            'paused': []
        }
        
        # Internal requests
        for floor in sorted(self.internal_requests):
            key = self._get_request_key(floor, "internal")
            req_time = self.request_times.get(key, current_time)
            info['internal'].append(RequestInfo(
                floor=floor,
                direction=None,
                request_time=req_time,
                wait_time=current_time - req_time
            ))
        
        # External UP requests
        for floor in sorted(self.external_up_requests):
            key = self._get_request_key(floor, "external_up")
            req_time = self.request_times.get(key, current_time)
            info['external_up'].append(RequestInfo(
                floor=floor,
                direction="UP",
                request_time=req_time,
                wait_time=current_time - req_time
            ))
        
        # External DOWN requests
        for floor in sorted(self.external_down_requests, reverse=True):
            key = self._get_request_key(floor, "external_down")
            req_time = self.request_times.get(key, current_time)
            info['external_down'].append(RequestInfo(
                floor=floor,
                direction="DOWN",
                request_time=req_time,
                wait_time=current_time - req_time
            ))
        
        # Emergency requests
        for emergency in self.emergency_requests:
            key = self._get_request_key(emergency.from_floor, f"emergency_{emergency.to_floor}")
            req_time = self.request_times.get(key, current_time)
            info['emergency'].append(RequestInfo(
                floor=emergency.from_floor,
                direction=f"→{emergency.to_floor}",
                request_time=req_time,
                wait_time=current_time - req_time
            ))
        
        # Paused requests count
        paused_count = len(self.paused_internal) + len(self.paused_external_up) + len(self.paused_external_down)
        if paused_count > 0:
            info['paused'].append(RequestInfo(
                floor=-1,
                direction=f"{paused_count} paused",
                request_time=current_time,
                wait_time=0
            ))
        
        return info
    
    def get_total_pending_count(self) -> int:
        """Get total count of all pending requests."""
        return (len(self.internal_requests) + 
                len(self.external_up_requests) + 
                len(self.external_down_requests) + 
                len(self.emergency_requests))
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get queue statistics."""
        return {
            'total_served': self.stats.total_requests_served,
            'normal_served': self.stats.normal_requests_served,
            'emergency_served': self.stats.emergency_requests_served,
            'average_wait': self.stats.average_wait_time,
            'total_wait': self.stats.total_wait_time,
            'pending_count': self.get_total_pending_count()
        }
