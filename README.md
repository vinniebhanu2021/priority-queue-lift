# 🏢 Priority Queue Elevator Control System

A sophisticated elevator control system with priority queue management, emergency handling, and real-time GUI visualization. This project demonstrates advanced scheduling algorithms for elevator operations with support for normal and emergency requests.

## 📋 Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [System Architecture](#system-architecture)
- [Key Components](#key-components)
- [How It Works](#how-it-works)
- [Testing](#testing)
- [Technologies Used](#technologies-used)

## ✨ Features

### Core Functionality
- **Priority Queue Management**: Intelligent scheduling of elevator requests
- **Emergency Request Handling**: High-priority emergency requests that pause normal operations
- **Normal Request Types**:
  - Internal requests (buttons pressed inside the elevator)
  - External requests (UP/DOWN buttons on floors)
- **Smart Direction Control**: Efficient movement based on current direction and pending requests
- **Real-time Statistics**: Track floors traveled, requests served, wait times, and more

### User Interface
- **Modern GUI**: Beautiful, intuitive interface built with tkinter
- **Real-time Visualization**: Animated elevator shaft showing current position and movement
- **Live Status Display**: Current floor, direction, emergency mode, and passenger count
- **Pending Requests Panel**: Real-time view of all queued requests
- **Activity Log**: Detailed log of all elevator operations
- **Speed Control**: Adjustable simulation speed (0.2x to 3.0x)
- **Pause/Resume**: Control simulation execution

### Emergency System
- **Priority Handling**: Emergency requests automatically pause normal operations
- **Group-based Scheduling**: Emergency requests sorted into priority groups (A, B, C)
- **Automatic Resume**: Normal operations resume after all emergencies are handled
- **Visual Indicators**: Clear visual feedback for emergency mode

## 📁 Project Structure

```
priority-queue-lift/
├── main.py                 # Entry point - launches the GUI
├── elevator_system.py      # Central coordinator for the elevator system
├── elevator_controller.py  # Physical state and movement control
├── queue_manager.py        # Request queue management with statistics
├── emergency_handler.py    # Emergency request detection and prioritization
├── elevator_ui.py          # GUI interface with tkinter
├── constants.py            # Constants, enums, and data classes
├── test_scenario.py       # Test scenarios and validation
└── README.md              # This file
```

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- tkinter (usually included with Python)

### Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd priority-queue-lift
   ```

2. **Verify Python installation**:
   ```bash
   python --version
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

No additional dependencies are required! The project uses only Python standard library.

## 💻 Usage

### Starting the Application

Run the main script:
```bash
python main.py
```

The GUI window will open with:
- **Elevator Shaft Visualization** (left): Shows the elevator's current position
- **Control Panels** (center): Request buttons and emergency controls
- **Status Panels** (right): Pending requests and activity log

### Making Requests

#### Normal Requests

1. **External Requests** (Call Elevator):
   - Click the **↑** button to call elevator going UP
   - Click the **↓** button to call elevator going DOWN
   - Select the floor number from the list

2. **Internal Requests** (Select Floor):
   - Click any floor number button in the "Select Floor" panel
   - The elevator will serve the request when it reaches that floor

#### Emergency Requests

1. **Setup Emergency Request**:
   - In the "Emergency Requests" panel, select a "From" floor and "To" floor
   - Check the checkbox or click the 🚨 button to select the request
   - Repeat for multiple emergency requests

2. **Execute Emergency Requests**:
   - Click the **EXECUTE** button to activate all selected emergency requests
   - Normal operations will pause automatically
   - The elevator will prioritize emergency requests

### Controls

- **Speed Slider**: Adjust simulation speed (0.2x to 3.0x)
- **Pause/Resume Button**: Pause or resume the simulation
- **Activity Log**: View detailed log of all operations

## 🏗️ System Architecture

The system follows a modular architecture with clear separation of concerns:

```
┌─────────────────────────────────────────┐
│         ElevatorSystem                  │
│  (Central Coordinator)                  │
├─────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐   │
│  │  Controller   │  │ QueueManager │   │
│  │  (Movement)  │  │  (Requests)  │   │
│  └──────────────┘  └──────────────┘   │
│  ┌──────────────────────────────────┐  │
│  │    EmergencyHandler              │  │
│  │    (Priority Management)         │  │
│  └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────┐
│         ElevatorUI                      │
│  (User Interface & Visualization)       │
└─────────────────────────────────────────┘
```

## 🔧 Key Components

### ElevatorSystem
The central coordinator that manages:
- Elevator controller (movement and state)
- Queue manager (request handling)
- Emergency handler (priority management)
- Event logging and statistics

### ElevatorController
Manages the physical elevator:
- Current floor and direction
- Door states (OPEN, CLOSED, OPENING, CLOSING)
- Movement between floors
- Passenger capacity tracking
- Statistics collection

### QueueManager
Handles all request queues:
- Internal requests (from inside elevator)
- External requests (UP/DOWN calls)
- Emergency requests
- Request timing and statistics
- Pause/resume functionality for normal requests

### EmergencyHandler
Manages emergency operations:
- Emergency mode activation
- Request prioritization (Groups A, B, C)
- Direction-based sorting
- Automatic mode switching

### ElevatorUI
Modern GUI interface featuring:
- Real-time elevator visualization
- Interactive control panels
- Live status updates
- Activity logging
- Statistics display

## 🔄 How It Works

### Request Processing Flow

1. **Request Addition**:
   - User makes a request (internal/external/emergency)
   - Request is added to appropriate queue
   - Timestamp is recorded for wait time calculation

2. **Target Selection**:
   - System determines next target floor based on:
     - Current floor and direction
     - Pending requests
     - Emergency priority (if active)

3. **Movement**:
   - Elevator moves toward target floor
   - Doors open when arriving at requested floor
   - Request is removed from queue
   - Statistics are updated

### Emergency Priority System

When emergency mode is active:

1. **Normal requests are paused** and saved
2. **Emergency requests are sorted** into groups:
   - **Group A**: In current direction (highest priority)
   - **Group B**: Opposite direction (medium priority)
   - **Group C**: Edge cases (lowest priority)
3. **Elevator serves emergencies** in priority order
4. **Normal operations resume** after all emergencies are handled

### Direction Control

The system uses intelligent direction control:
- **SCAN Algorithm**: Serves requests in current direction before reversing
- **Closest Floor**: When idle, goes to nearest requested floor
- **Direction Optimization**: Minimizes unnecessary direction changes

## 🧪 Testing

Run the test scenarios:

```bash
python test_scenario.py
```

The test suite includes:
- Comprehensive scenario testing
- Single emergency request validation
- Normal request handling verification
- Emergency priority validation

## 🛠️ Technologies Used

- **Python 3.8+**: Core programming language
- **tkinter**: GUI framework (included with Python)
- **Object-Oriented Design**: Modular, maintainable code structure
- **Enum Types**: Type-safe constants and states
- **Dataclasses**: Clean data structure definitions

## 📊 Statistics Tracked

The system tracks comprehensive statistics:
- Total floors traveled
- Requests served (normal and emergency)
- Average wait time
- Current passenger count
- Maximum capacity utilization

## 🎯 Key Algorithms

### Priority Queue Algorithm
- Emergency requests have highest priority
- Normal requests follow SCAN algorithm
- Direction-based optimization

### Emergency Grouping
- Group A: Requests in current direction
- Group B: Requests requiring direction change
- Group C: Edge cases and special situations

### Request Scheduling
- Internal requests prioritized when in elevator
- External requests handled based on direction
- Closest floor selection when idle

## 📝 Notes

- The elevator has a maximum capacity of 8 passengers (configurable in `constants.py`)
- Door operations take 2 simulation steps
- Emergency mode automatically pauses normal requests
- All requests are timestamped for wait time calculation

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available for educational purposes.

## 👤 Author

Created as part of an elevator control system project demonstrating priority queue algorithms and real-time system design.

---

**Enjoy exploring the Priority Queue Elevator Control System!** 🏢🛗

