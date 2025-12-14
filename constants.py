from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional
import time


class Direction(Enum):
    """Elevator direction states"""
    UP = "UP"
    DOWN = "DOWN"
    IDLE = "IDLE"
    
    def __str__(self) -> str:
        return self.value
    
    def opposite(self) -> 'Direction':
        """Get the opposite direction"""
        if self == Direction.UP:
            return Direction.DOWN
        elif self == Direction.DOWN:
            return Direction.UP
        return Direction.IDLE


class DoorState(Enum):
    """Elevator door states"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    OPENING = "OPENING"
    CLOSING = "CLOSING"
    
    def __str__(self) -> str:
        return self.value


class EmergencyPriority(Enum):
    """Emergency request priority levels"""
    NORMAL = 1
    HIGH = 2
    CRITICAL = 3
    
    def __str__(self) -> str:
        return self.name


@dataclass
class Request:
    """Represents an elevator request"""
    floor: int
    direction: Optional[Direction] = None
    timestamp: float = 0.0
    is_emergency: bool = False
    priority: EmergencyPriority = EmergencyPriority.NORMAL
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()


@dataclass
class EmergencyRequest:
    """Represents an emergency elevator request with pickup and destination"""
    from_floor: int
    to_floor: int
    priority: EmergencyPriority = EmergencyPriority.CRITICAL
    timestamp: float = 0.0
    is_picked_up: bool = False
    
    def __post_init__(self):
        if self.timestamp == 0.0:
            self.timestamp = time.time()
    
    def __eq__(self, other):
        if isinstance(other, EmergencyRequest):
            return self.from_floor == other.from_floor and self.to_floor == other.to_floor
        if isinstance(other, tuple):
            return (self.from_floor, self.to_floor) == other
        return False
    
    def __hash__(self):
        return hash((self.from_floor, self.to_floor))
    
    def to_tuple(self) -> tuple:
        return (self.from_floor, self.to_floor)


@dataclass
class ElevatorStats:
    """Statistics for elevator performance"""
    total_floors_traveled: int = 0
    normal_requests_served: int = 0
    emergency_requests_served: int = 0
    total_wait_time: float = 0.0
    current_passengers: int = 0
    max_capacity: int = 8
    
    @property
    def total_requests_served(self) -> int:
        return self.normal_requests_served + self.emergency_requests_served
    
    @property
    def average_wait_time(self) -> float:
        if self.total_requests_served == 0:
            return 0.0
        return self.total_wait_time / self.total_requests_served
    
    def add_passenger(self) -> bool:
        """Add a passenger if capacity allows"""
        if self.current_passengers < self.max_capacity:
            self.current_passengers += 1
            return True
        return False
    
    def remove_passenger(self) -> bool:
        """Remove a passenger"""
        if self.current_passengers > 0:
            self.current_passengers -= 1
            return True
        return False


# Color constants for UI
class Colors:
    """Modern color palette for the elevator UI"""
    # Base colors
    BG = '#0f0f23'
    CARD_BG = '#1a1a2e'
    CARD_BG_LIGHT = '#16213e'
    
    # Primary colors
    PRIMARY = '#4361ee'
    PRIMARY_HOVER = '#3a0ca3'
    PRIMARY_GLOW = '#4cc9f0'
    
    # Accent colors
    SUCCESS = '#06ffa5'
    SUCCESS_DARK = '#00b377'
    DANGER = '#ff006e'
    DANGER_GLOW = '#ff4d8d'
    WARNING = '#ffbe0b'
    
    # Text colors
    TEXT = '#ffffff'
    TEXT_SECONDARY = '#a0a0b8'
    TEXT_MUTED = '#6c6c8a'
    
    # Elevator colors
    ELEVATOR_UP = '#00f5d4'
    ELEVATOR_DOWN = '#00bbf9'
    ELEVATOR_IDLE = '#9b5de5'
    ELEVATOR_SHAFT = '#0a0a1a'
    FLOOR_MARKER = '#2a2a4a'
    
    # Emergency colors
    EMERGENCY = '#ff0054'
    EMERGENCY_GLOW = '#ff4081'
    EMERGENCY_BG = '#2a0015'
    
    # Border and shadow
    BORDER = '#2a2a4a'
    SHADOW = '#000000'
    GLOW = '#4cc9f0'
