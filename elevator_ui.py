import tkinter as tk
from tkinter import ttk, messagebox
import math
from elevator_system import ElevatorSystem
from constants import Direction, DoorState, Colors


class ModernButton(tk.Canvas):
    """Custom modern button with hover effects and rounded corners."""
    
    def __init__(self, parent, text="", command=None, width=60, height=35, 
                 bg_color=Colors.PRIMARY, hover_color=Colors.PRIMARY_HOVER, 
                 text_color=Colors.TEXT, font_size=10, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=parent.cget('bg'), highlightthickness=0, **kwargs)
        
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = bg_color
        self.text = text
        self.font_size = font_size
        self.is_pressed = False
        
        self.draw()
        
        self.bind('<Enter>', self.on_enter)
        self.bind('<Leave>', self.on_leave)
        self.bind('<Button-1>', self.on_press)
        self.bind('<ButtonRelease-1>', self.on_release)
    
    def draw(self):
        self.delete('all')
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        r = 8  # Corner radius
        
        # Draw rounded rectangle
        self.create_rounded_rect(2, 2, w-2, h-2, r, fill=self.current_color, outline='')
        
        # Draw text
        self.create_text(w//2, h//2, text=self.text, fill=self.text_color,
                        font=('Segoe UI', self.font_size, 'bold'))
    
    def create_rounded_rect(self, x1, y1, x2, y2, r, **kwargs):
        points = [
            x1+r, y1, x2-r, y1, x2, y1, x2, y1+r,
            x2, y2-r, x2, y2, x2-r, y2, x1+r, y2,
            x1, y2, x1, y2-r, x1, y1+r, x1, y1
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, event):
        self.current_color = self.hover_color
        self.draw()
    
    def on_leave(self, event):
        self.current_color = self.bg_color
        self.draw()
    
    def on_press(self, event):
        self.is_pressed = True
    
    def on_release(self, event):
        if self.is_pressed and self.command:
            self.command()
        self.is_pressed = False


class ElevatorShaftVisualization(tk.Canvas):
    """Visual representation of the elevator shaft with animated elevator car."""
    
    def __init__(self, parent, num_floors=10, width=120, **kwargs):
        height = num_floors * 50 + 60
        super().__init__(parent, width=width, height=height, 
                        bg=Colors.ELEVATOR_SHAFT, highlightthickness=0, **kwargs)
        
        self.num_floors = num_floors
        self.floor_height = 50
        self.elevator_width = 60
        self.elevator_height = 40
        
        self.current_floor = 1
        self.target_y = self._floor_to_y(1)
        self.current_y = self.target_y
        self.door_state = DoorState.CLOSED
        self.is_emergency = False
        
        self.animation_speed = 3
        self.glow_phase = 0
        
        self.draw_static()
        self.draw_elevator()
        self.animate()
    
    def _floor_to_y(self, floor):
        """Convert floor number to Y coordinate."""
        return (self.num_floors - floor) * self.floor_height + 30
    
    def draw_static(self):
        """Draw static elements (floor markers, labels)."""
        self.delete('static')
        
        w = self.winfo_reqwidth()
        
        # Draw shaft border with gradient effect
        self.create_rectangle(20, 10, w-20, self.num_floors * self.floor_height + 50,
                             fill=Colors.ELEVATOR_SHAFT, outline=Colors.BORDER, 
                             width=2, tags='static')
        
        # Draw floor lines and labels
        for floor in range(1, self.num_floors + 1):
            y = self._floor_to_y(floor) + self.elevator_height // 2
            
            # Floor line
            self.create_line(22, y + 15, w-22, y + 15, 
                           fill=Colors.FLOOR_MARKER, width=1, tags='static')
            
            # Floor number
            self.create_text(w - 8, y, text=str(floor), 
                           fill=Colors.TEXT_SECONDARY, 
                           font=('Segoe UI', 9, 'bold'), 
                           anchor='e', tags='static')
    
    def draw_elevator(self):
        """Draw the elevator car."""
        self.delete('elevator')
        
        w = self.winfo_reqwidth()
        x = (w - self.elevator_width) // 2
        y = self.current_y
        
        # Glow effect for emergency mode
        if self.is_emergency:
            glow_intensity = (math.sin(self.glow_phase) + 1) / 2
            glow_color = self._blend_color(Colors.DANGER, Colors.EMERGENCY_GLOW, glow_intensity)
            
            # Draw glow
            for i in range(3, 0, -1):
                alpha_color = self._adjust_brightness(glow_color, 0.3 + (3-i) * 0.2)
                self.create_rectangle(
                    x - i*2, y - i*2, 
                    x + self.elevator_width + i*2, y + self.elevator_height + i*2,
                    fill=alpha_color, outline='', tags='elevator'
                )
        
        # Elevator car body
        car_color = Colors.DANGER if self.is_emergency else Colors.PRIMARY
        self.create_rectangle(x, y, x + self.elevator_width, y + self.elevator_height,
                             fill=car_color, outline=Colors.PRIMARY_GLOW if not self.is_emergency else Colors.DANGER_GLOW, 
                             width=2, tags='elevator')
        
        # Elevator doors
        door_gap = 2 if self.door_state == DoorState.OPEN else 0
        door_width = (self.elevator_width - 8) // 2 - door_gap
        
        # Left door
        self.create_rectangle(x + 4, y + 4, 
                             x + 4 + door_width - door_gap, y + self.elevator_height - 4,
                             fill=Colors.CARD_BG, outline='', tags='elevator')
        
        # Right door
        self.create_rectangle(x + self.elevator_width - 4 - door_width + door_gap, y + 4,
                             x + self.elevator_width - 4, y + self.elevator_height - 4,
                             fill=Colors.CARD_BG, outline='', tags='elevator')
        
        # Direction indicator
        center_x = x + self.elevator_width // 2
        indicator_y = y - 8
        
        if self._direction == Direction.UP:
            self.create_polygon(center_x - 5, indicator_y + 5, 
                              center_x, indicator_y - 3,
                              center_x + 5, indicator_y + 5,
                              fill=Colors.ELEVATOR_UP, tags='elevator')
        elif self._direction == Direction.DOWN:
            self.create_polygon(center_x - 5, indicator_y - 3, 
                              center_x, indicator_y + 5,
                              center_x + 5, indicator_y - 3,
                              fill=Colors.ELEVATOR_DOWN, tags='elevator')
    
    def _blend_color(self, color1, color2, ratio):
        """Blend two hex colors."""
        r1, g1, b1 = int(color1[1:3], 16), int(color1[3:5], 16), int(color1[5:7], 16)
        r2, g2, b2 = int(color2[1:3], 16), int(color2[3:5], 16), int(color2[5:7], 16)
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        return f'#{r:02x}{g:02x}{b:02x}'
    
    def _adjust_brightness(self, color, factor):
        """Adjust color brightness."""
        r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
        r = min(255, int(r * factor))
        g = min(255, int(g * factor))
        b = min(255, int(b * factor))
        return f'#{r:02x}{g:02x}{b:02x}'
    
    _direction = Direction.IDLE
    
    def update_state(self, floor, direction, door_state, is_emergency):
        """Update elevator state."""
        self.target_y = self._floor_to_y(floor)
        self._direction = direction
        self.door_state = door_state
        self.is_emergency = is_emergency
        self.current_floor = floor
    
    def animate(self):
        """Animation loop."""
        # Smooth movement
        if abs(self.current_y - self.target_y) > 1:
            diff = self.target_y - self.current_y
            self.current_y += diff * 0.15
        else:
            self.current_y = self.target_y
        
        # Glow animation
        self.glow_phase += 0.15
        if self.glow_phase > math.pi * 2:
            self.glow_phase = 0
        
        self.draw_elevator()
        self.after(16, self.animate)  # ~60 FPS


class StatsCard(tk.Frame):
    """A card displaying a statistic with label and value."""
    
    def __init__(self, parent, label, value="0", icon="📊", **kwargs):
        super().__init__(parent, bg=Colors.CARD_BG, **kwargs)
        
        self.configure(highlightbackground=Colors.BORDER, highlightthickness=1)
        
        # Horizontal layout for compactness
        content = tk.Frame(self, bg=Colors.CARD_BG)
        content.pack(fill=tk.X, padx=8, pady=6)
        
        # Icon
        tk.Label(content, text=icon, font=('Segoe UI', 10), 
                bg=Colors.CARD_BG, fg=Colors.TEXT).pack(side=tk.LEFT)
        
        # Label
        tk.Label(content, text=label, font=('Segoe UI', 8), 
                bg=Colors.CARD_BG, fg=Colors.TEXT_SECONDARY).pack(side=tk.LEFT, padx=(4, 0))
        
        # Value (right aligned)
        self.value_label = tk.Label(content, text=value, font=('Segoe UI', 12, 'bold'),
                                   bg=Colors.CARD_BG, fg=Colors.PRIMARY_GLOW)
        self.value_label.pack(side=tk.RIGHT)
    
    def set_value(self, value, color=None):
        self.value_label.config(text=str(value))
        if color:
            self.value_label.config(fg=color)


class PendingRequestsPanel(tk.Frame):
    """Panel showing all pending requests in real-time."""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Colors.CARD_BG, **kwargs)
        
        self.configure(highlightbackground=Colors.BORDER, highlightthickness=1)
        
        # Title
        tk.Label(self, text="📋 Pending Requests", font=('Segoe UI', 11, 'bold'),
                bg=Colors.CARD_BG, fg=Colors.TEXT).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Requests list
        self.list_frame = tk.Frame(self, bg=Colors.CARD_BG)
        self.list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.request_labels = []
    
    def update_requests(self, pending_info):
        """Update the displayed requests."""
        # Clear existing
        for label in self.request_labels:
            label.destroy()
        self.request_labels = []
        
        row = 0
        
        # Internal requests
        for req in pending_info.get('internal', []):
            label = tk.Label(self.list_frame, 
                           text=f"🔵 Internal → Floor {req.floor}",
                           font=('Segoe UI', 9), bg=Colors.CARD_BG, fg=Colors.PRIMARY_GLOW)
            label.grid(row=row, column=0, sticky='w', pady=1)
            self.request_labels.append(label)
            row += 1
        
        # External UP requests
        for req in pending_info.get('external_up', []):
            label = tk.Label(self.list_frame, 
                           text=f"🟢 Floor {req.floor} ↑",
                           font=('Segoe UI', 9), bg=Colors.CARD_BG, fg=Colors.ELEVATOR_UP)
            label.grid(row=row, column=0, sticky='w', pady=1)
            self.request_labels.append(label)
            row += 1
        
        # External DOWN requests
        for req in pending_info.get('external_down', []):
            label = tk.Label(self.list_frame, 
                           text=f"🔵 Floor {req.floor} ↓",
                           font=('Segoe UI', 9), bg=Colors.CARD_BG, fg=Colors.ELEVATOR_DOWN)
            label.grid(row=row, column=0, sticky='w', pady=1)
            self.request_labels.append(label)
            row += 1
        
        # Emergency requests
        for req in pending_info.get('emergency', []):
            label = tk.Label(self.list_frame, 
                           text=f"🚨 Emergency: Floor {req.floor} {req.direction}",
                           font=('Segoe UI', 9, 'bold'), bg=Colors.CARD_BG, fg=Colors.DANGER)
            label.grid(row=row, column=0, sticky='w', pady=1)
            self.request_labels.append(label)
            row += 1
        
        # Paused indicator
        for req in pending_info.get('paused', []):
            label = tk.Label(self.list_frame, 
                           text=f"⏸️ {req.direction}",
                           font=('Segoe UI', 9), bg=Colors.CARD_BG, fg=Colors.WARNING)
            label.grid(row=row, column=0, sticky='w', pady=1)
            self.request_labels.append(label)
            row += 1
        
        if row == 0:
            label = tk.Label(self.list_frame, 
                           text="No pending requests",
                           font=('Segoe UI', 9), bg=Colors.CARD_BG, fg=Colors.TEXT_MUTED)
            label.grid(row=0, column=0, sticky='w', pady=1)
            self.request_labels.append(label)


class ElevatorUI:
    """Main elevator control interface with modern design."""
    
    def __init__(self, root, num_floors=10, start_floor=3, start_direction="UP"):
        self.root = root
        self.root.title("🏢 Emergency Elevator Control System")
        self.root.geometry("1400x900")
        self.root.configure(bg=Colors.BG)
        
        # Set minimum size
        self.root.minsize(1200, 700)
        
        self.num_floors = num_floors
        self.elevator = ElevatorSystem(num_floors, start_floor, start_direction)
        
        # UI update interval (milliseconds)
        self.base_interval = 400
        self.update_interval = self.base_interval
        
        self.setup_styles()
        self.setup_ui()
        self.start_simulation()
    
    def setup_styles(self):
        """Configure ttk styles."""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Scrollbar style
        style.configure('Custom.Vertical.TScrollbar',
                       background=Colors.CARD_BG,
                       troughcolor=Colors.BG,
                       bordercolor=Colors.BORDER,
                       arrowcolor=Colors.TEXT)
        
        # Combobox style
        style.configure('Custom.TCombobox',
                       fieldbackground='#e0e0e0',
                       background='#e0e0e0',
                       foreground='#000000',
                       bordercolor='#b0b0b0',
                       arrowcolor='#000000',
                       borderwidth=1)
        style.map('Custom.TCombobox',
                 fieldbackground=[('readonly', '#e0e0e0')],
                 background=[('readonly', '#e0e0e0')],
                 foreground=[('readonly', '#000000')])
        
        # Scale style
        style.configure('Custom.Horizontal.TScale',
                       background=Colors.BG,
                       troughcolor=Colors.CARD_BG,
                       sliderrelief='flat')
    
    def setup_ui(self):
        """Create the UI components."""
        # Main container
        main_frame = tk.Frame(self.root, bg=Colors.BG, padx=20, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self._create_header(main_frame)
        
        # Content area
        content = tk.Frame(main_frame, bg=Colors.BG)
        content.pack(fill=tk.BOTH, expand=True, pady=15)
        
        # Left column: Elevator shaft & Stats
        left_col = tk.Frame(content, bg=Colors.BG)
        left_col.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        self._create_elevator_shaft(left_col)
        self._create_stats_panel(left_col)
        
        # Middle column: Controls
        middle_col = tk.Frame(content, bg=Colors.BG)
        middle_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        self._create_control_panels(middle_col)
        
        # Right column: Pending requests & Log
        right_col = tk.Frame(content, bg=Colors.BG, width=300)
        right_col.pack(side=tk.RIGHT, fill=tk.Y)
        right_col.pack_propagate(False)
        
        self._create_pending_panel(right_col)
        self._create_log_panel(right_col)
    
    def _create_header(self, parent):
        """Create the header with title and status."""
        header = tk.Frame(parent, bg=Colors.BG)
        header.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        title_frame = tk.Frame(header, bg=Colors.BG)
        title_frame.pack(side=tk.LEFT)
        
        tk.Label(title_frame, text="🏢", font=('Segoe UI', 28),
                bg=Colors.BG, fg=Colors.TEXT).pack(side=tk.LEFT)
        
        title_text = tk.Frame(title_frame, bg=Colors.BG)
        title_text.pack(side=tk.LEFT, padx=(10, 0))
        
        tk.Label(title_text, text="Emergency Elevator Control System",
                font=('Segoe UI', 20, 'bold'), bg=Colors.BG, fg=Colors.TEXT).pack(anchor=tk.W)
        tk.Label(title_text, text="Advanced Scheduling with Priority Queue",
                font=('Segoe UI', 10), bg=Colors.BG, fg=Colors.TEXT_SECONDARY).pack(anchor=tk.W)
        
        # Status indicators
        status_frame = tk.Frame(header, bg=Colors.BG)
        status_frame.pack(side=tk.RIGHT)
        
        # Current floor
        floor_card = tk.Frame(status_frame, bg=Colors.CARD_BG, 
                             highlightbackground=Colors.BORDER, highlightthickness=1)
        floor_card.pack(side=tk.LEFT, padx=5)
        tk.Label(floor_card, text="FLOOR", font=('Segoe UI', 8),
                bg=Colors.CARD_BG, fg=Colors.TEXT_SECONDARY).pack(padx=15, pady=(5, 0))
        self.floor_label = tk.Label(floor_card, text="3", font=('Segoe UI', 24, 'bold'),
                                   bg=Colors.CARD_BG, fg=Colors.PRIMARY_GLOW)
        self.floor_label.pack(padx=15, pady=(0, 5))
        
        # Direction
        dir_card = tk.Frame(status_frame, bg=Colors.CARD_BG,
                           highlightbackground=Colors.BORDER, highlightthickness=1)
        dir_card.pack(side=tk.LEFT, padx=5)
        tk.Label(dir_card, text="DIRECTION", font=('Segoe UI', 8),
                bg=Colors.CARD_BG, fg=Colors.TEXT_SECONDARY).pack(padx=15, pady=(5, 0))
        self.direction_label = tk.Label(dir_card, text="UP ↑", font=('Segoe UI', 18, 'bold'),
                                       bg=Colors.CARD_BG, fg=Colors.ELEVATOR_UP)
        self.direction_label.pack(padx=15, pady=(0, 5))
        
        # Emergency status
        self.emergency_card = tk.Frame(status_frame, bg=Colors.CARD_BG,
                                       highlightbackground=Colors.BORDER, highlightthickness=1)
        self.emergency_card.pack(side=tk.LEFT, padx=5)
        tk.Label(self.emergency_card, text="EMERGENCY", font=('Segoe UI', 8),
                bg=Colors.CARD_BG, fg=Colors.TEXT_SECONDARY).pack(padx=15, pady=(5, 0))
        self.emergency_label = tk.Label(self.emergency_card, text="OFF", 
                                       font=('Segoe UI', 18, 'bold'),
                                       bg=Colors.CARD_BG, fg=Colors.TEXT_MUTED)
        self.emergency_label.pack(padx=15, pady=(0, 5))
    
    def _create_elevator_shaft(self, parent):
        """Create the elevator shaft visualization."""
        shaft_frame = tk.Frame(parent, bg=Colors.CARD_BG,
                              highlightbackground=Colors.BORDER, highlightthickness=1)
        shaft_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(shaft_frame, text="Elevator Shaft", font=('Segoe UI', 11, 'bold'),
                bg=Colors.CARD_BG, fg=Colors.TEXT).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        self.shaft_viz = ElevatorShaftVisualization(shaft_frame, self.num_floors)
        self.shaft_viz.pack(padx=10, pady=(0, 10))
    
    def _create_stats_panel(self, parent):
        """Create the statistics panel."""
        stats_frame = tk.Frame(parent, bg=Colors.BG)
        stats_frame.pack(fill=tk.X)
        
        self.floors_stat = StatsCard(stats_frame, "Floors Traveled", "0", "🛗")
        self.floors_stat.pack(fill=tk.X, pady=(0, 5))
        
        self.served_stat = StatsCard(stats_frame, "Requests Served", "0", "✅")
        self.served_stat.pack(fill=tk.X)
    
    def _create_control_panels(self, parent):
        """Create the main control panels."""
        # Speed control
        speed_frame = tk.Frame(parent, bg=Colors.CARD_BG,
                              highlightbackground=Colors.BORDER, highlightthickness=1)
        speed_frame.pack(fill=tk.X, pady=(0, 10))
        
        speed_header = tk.Frame(speed_frame, bg=Colors.CARD_BG)
        speed_header.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(speed_header, text="⚡ Simulation Speed", font=('Segoe UI', 11, 'bold'),
                bg=Colors.CARD_BG, fg=Colors.TEXT).pack(side=tk.LEFT)
        
        self.speed_label = tk.Label(speed_header, text="1.0x", font=('Segoe UI', 11),
                                   bg=Colors.CARD_BG, fg=Colors.PRIMARY_GLOW)
        self.speed_label.pack(side=tk.RIGHT)
        
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_scale = ttk.Scale(speed_frame, from_=0.2, to=3.0, variable=self.speed_var,
                               orient=tk.HORIZONTAL, command=self.on_speed_change,
                               style='Custom.Horizontal.TScale')
        speed_scale.pack(fill=tk.X, padx=15, pady=(0, 5))
        
        # Pause button
        pause_frame = tk.Frame(speed_frame, bg=Colors.CARD_BG)
        pause_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        self.pause_btn = tk.Button(pause_frame, text="⏸️ Pause", font=('Segoe UI', 10, 'bold'),
                                  bg=Colors.WARNING, fg=Colors.BG, relief='flat',
                                  activebackground=Colors.WARNING, cursor='hand2',
                                  command=self.toggle_pause)
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Control panels container
        controls_container = tk.Frame(parent, bg=Colors.BG)
        controls_container.pack(fill=tk.BOTH, expand=True)
        
        # External controls
        external_frame = tk.Frame(controls_container, bg=Colors.CARD_BG,
                                 highlightbackground=Colors.BORDER, highlightthickness=1)
        external_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(external_frame, text="🔔 Call Elevator (External)", 
                font=('Segoe UI', 11, 'bold'),
                bg=Colors.CARD_BG, fg=Colors.TEXT).pack(anchor=tk.W, padx=15, pady=(10, 5))
        
        # Scrollable external buttons
        ext_canvas = tk.Canvas(external_frame, bg=Colors.CARD_BG, highlightthickness=0)
        ext_scrollbar = ttk.Scrollbar(external_frame, orient="vertical", 
                                      command=ext_canvas.yview)
        ext_scrollable = tk.Frame(ext_canvas, bg=Colors.CARD_BG)
        
        ext_scrollable.bind("<Configure>", 
                           lambda e: ext_canvas.configure(scrollregion=ext_canvas.bbox("all")))
        ext_canvas.create_window((0, 0), window=ext_scrollable, anchor="nw")
        ext_canvas.configure(yscrollcommand=ext_scrollbar.set)
        
        self.external_buttons = {}
        for floor in range(self.num_floors, 0, -1):
            row = tk.Frame(ext_scrollable, bg=Colors.CARD_BG)
            row.pack(fill=tk.X, padx=10, pady=3)
            
            tk.Label(row, text=f"F{floor}", font=('Segoe UI', 10, 'bold'),
                    bg=Colors.CARD_BG, fg=Colors.TEXT, width=4).pack(side=tk.LEFT)
            
            up_btn = tk.Button(row, text="↑", font=('Segoe UI', 12, 'bold'),
                              bg=Colors.ELEVATOR_UP, fg=Colors.BG,
                              width=3, relief='flat', cursor='hand2',
                              activebackground=Colors.SUCCESS,
                              command=lambda f=floor: self.handle_external(f, "UP"))
            up_btn.pack(side=tk.LEFT, padx=3)
            
            down_btn = tk.Button(row, text="↓", font=('Segoe UI', 12, 'bold'),
                                bg=Colors.ELEVATOR_DOWN, fg=Colors.BG,
                                width=3, relief='flat', cursor='hand2',
                                activebackground=Colors.PRIMARY,
                                command=lambda f=floor: self.handle_external(f, "DOWN"))
            down_btn.pack(side=tk.LEFT, padx=3)
            
            self.external_buttons[floor] = (up_btn, down_btn)
        
        ext_canvas.pack(side="left", fill="both", expand=True, padx=5)
        ext_scrollbar.pack(side="right", fill="y")
        
        # Internal controls
        internal_frame = tk.Frame(controls_container, bg=Colors.CARD_BG,
                                 highlightbackground=Colors.BORDER, highlightthickness=1)
        internal_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(internal_frame, text="🔢 Select Floor (Internal)", 
                font=('Segoe UI', 11, 'bold'),
                bg=Colors.CARD_BG, fg=Colors.TEXT).pack(anchor=tk.W, padx=15, pady=(10, 10))
        
        internal_grid = tk.Frame(internal_frame, bg=Colors.CARD_BG)
        internal_grid.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        cols = 3
        for i, floor in enumerate(range(self.num_floors, 0, -1)):
            row, col = i // cols, i % cols
            btn = tk.Button(internal_grid, text=str(floor), 
                           font=('Segoe UI', 14, 'bold'),
                           bg=Colors.CARD_BG_LIGHT, fg='#000000',
                           width=4, height=2, relief='flat', cursor='hand2',
                           activebackground=Colors.PRIMARY,
                           activeforeground='#000000',
                           command=lambda f=floor: self.handle_internal(f))
            btn.grid(row=row, column=col, padx=5, pady=5, sticky='nsew')
        
        for i in range(cols):
            internal_grid.columnconfigure(i, weight=1)
        
        # Emergency controls
        emergency_frame = tk.Frame(controls_container, bg='#ffffff',
                                  highlightbackground=Colors.BORDER, highlightthickness=1)
        emergency_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Title section
        title_frame = tk.Frame(emergency_frame, bg='#ffffff')
        title_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        
        tk.Label(title_frame, text="Emergency Requests", 
                font=('Segoe UI', 12, 'bold'),
                bg='#ffffff', fg='#000000').pack(anchor=tk.W)
        
        tk.Label(title_frame, text="From → To", 
                font=('Segoe UI', 9),
                bg='#ffffff', fg='#666666').pack(anchor=tk.W, pady=(2, 0))
        
        # Scrollable table container
        table_container = tk.Frame(emergency_frame, bg='#ffffff')
        table_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=(10, 10))
        
        # Canvas for scrolling
        canvas = tk.Canvas(table_container, bg='#ffffff', highlightthickness=0)
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#ffffff')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Store emergency rows
        self.emergency_rows = []
        
        # Create initial rows (10 rows as shown in image)
        # Set initial values matching the image pattern
        initial_values = [
            (10, 10), (9, 10), (8, 9), (7, 8), (6, 7),
            (5, 6), (4, 10), (3, 4), (2, 1), (1, 2)
        ]
        for i in range(10):
            row_data = self._add_emergency_row(scrollable_frame, i)
            if i < len(initial_values):
                row_data['from_var'].set(str(initial_values[i][0]))
                row_data['to_var'].set(str(initial_values[i][1]))
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # EXECUTE button at the bottom
        execute_frame = tk.Frame(emergency_frame, bg='#ffffff')
        execute_frame.pack(fill=tk.X, padx=15, pady=(0, 15))
        
        self.execute_btn = tk.Button(execute_frame, text="EXECUTE", 
                                     font=('Segoe UI', 12, 'bold'),
                                     bg=Colors.SUCCESS, fg='#000000',
                                     relief='flat', cursor='hand2',
                                     activebackground=Colors.SUCCESS_DARK,
                                     command=self.execute_emergency_requests)
        self.execute_btn.pack(fill=tk.X, pady=5)
    
    def _create_pending_panel(self, parent):
        """Create the pending requests panel."""
        self.pending_panel = PendingRequestsPanel(parent)
        self.pending_panel.pack(fill=tk.X, pady=(0, 10))
    
    def _create_log_panel(self, parent):
        """Create the activity log panel."""
        log_frame = tk.Frame(parent, bg=Colors.CARD_BG,
                            highlightbackground=Colors.BORDER, highlightthickness=1)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(log_frame, text="📜 Activity Log", font=('Segoe UI', 11, 'bold'),
                bg=Colors.CARD_BG, fg=Colors.TEXT).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        log_container = tk.Frame(log_frame, bg=Colors.CARD_BG)
        log_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.log_text = tk.Text(log_container, height=12, wrap=tk.WORD,
                               font=('Consolas', 9),
                               bg=Colors.BG, fg=Colors.TEXT,
                               relief='flat', borderwidth=0,
                               insertbackground=Colors.TEXT)
        log_scroll = ttk.Scrollbar(log_container, orient=tk.VERTICAL, 
                                   command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scroll.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configure log colors
        self.log_text.tag_configure('emergency', foreground=Colors.DANGER)
        self.log_text.tag_configure('success', foreground=Colors.SUCCESS)
        self.log_text.tag_configure('info', foreground=Colors.PRIMARY_GLOW)
        
        self.log("System initialized", 'info')
        self.log(f"Starting at Floor {self.elevator.controller.get_current_floor()}", 'info')
    
    def log(self, message, tag=''):
        """Add a message to the log."""
        self.log_text.insert(tk.END, f"• {message}\n", tag)
        self.log_text.see(tk.END)
    
    def on_speed_change(self, value):
        """Handle speed slider change."""
        speed = float(value)
        self.speed_label.config(text=f"{speed:.1f}x")
        self.update_interval = int(self.base_interval / speed)
        self.elevator.set_speed(speed)
    
    def toggle_pause(self):
        """Toggle simulation pause state."""
        is_paused = self.elevator.toggle_pause()
        if is_paused:
            self.pause_btn.config(text="▶️ Resume", bg=Colors.SUCCESS)
            self.log("Simulation paused", 'info')
        else:
            self.pause_btn.config(text="⏸️ Pause", bg=Colors.WARNING)
            self.log("Simulation resumed", 'info')
    
    def handle_external(self, floor, direction):
        """Handle external button press."""
        if self.elevator.emergency_handler.is_emergency_mode():
            self.log(f"⚠️ External {direction} at F{floor} - BLOCKED (Emergency Mode)", 'emergency')
            return
        
        self.elevator.add_external_request(floor, direction)
        self.log(f"External {direction} request: Floor {floor}", 'info')
    
    def handle_internal(self, floor):
        """Handle internal button press."""
        if self.elevator.emergency_handler.is_emergency_mode():
            self.log(f"⚠️ Internal F{floor} - BLOCKED (Emergency Mode)", 'emergency')
            return
        
        self.elevator.add_internal_request(floor)
        self.log(f"Internal request: Floor {floor}", 'info')
    
    def _add_emergency_row(self, parent, row_index):
        """Add a new emergency request row to the table."""
        row_frame = tk.Frame(parent, bg='#ffffff')
        row_frame.pack(fill=tk.X, pady=3)
        
        # Checkbox for selection
        selected_var = tk.BooleanVar(value=False)
        checkbox = tk.Checkbutton(row_frame, variable=selected_var,
                                  bg='#ffffff', activebackground='#ffffff',
                                  selectcolor='#ffffff', cursor='hand2')
        checkbox.pack(side=tk.LEFT, padx=(0, 8))
        
        # From dropdown
        from_var = tk.StringVar(value=str(row_index + 1))
        from_combo = ttk.Combobox(row_frame, textvariable=from_var,
                                 values=[str(i) for i in range(1, self.num_floors + 1)],
                                 width=8, state='readonly', style='Custom.TCombobox')
        from_combo.pack(side=tk.LEFT, padx=(0, 8))
        
        # Arrow
        arrow_label = tk.Label(row_frame, text="→", font=('Segoe UI', 14),
                              bg='#ffffff', fg='#000000')
        arrow_label.pack(side=tk.LEFT, padx=5)
        
        # To dropdown
        to_var = tk.StringVar(value=str(min(self.num_floors, row_index + 2)))
        to_combo = ttk.Combobox(row_frame, textvariable=to_var,
                               values=[str(i) for i in range(1, self.num_floors + 1)],
                               width=8, state='readonly', style='Custom.TCombobox')
        to_combo.pack(side=tk.LEFT, padx=5)
        
        # Action button (red with emergency icon and white border)
        # Wrap in frame for white border effect
        btn_frame = tk.Frame(row_frame, bg='#ffffff')
        btn_frame.pack(side=tk.LEFT, padx=(10, 0))
        
        action_btn = tk.Button(btn_frame, text="🚨", font=('Segoe UI', 12),
                              bg=Colors.DANGER, fg=Colors.TEXT,
                              relief='flat', cursor='hand2',
                              activebackground=Colors.DANGER_GLOW,
                              width=4, height=1,
                              borderwidth=1,
                              highlightthickness=1,
                              highlightbackground='#ffffff',
                              highlightcolor='#ffffff',
                              command=lambda: self.toggle_row_selection(row_index))
        action_btn.pack()
        
        # Store row data
        row_data = {
            'frame': row_frame,
            'selected_var': selected_var,
            'checkbox': checkbox,
            'from_var': from_var,
            'to_var': to_var,
            'from_combo': from_combo,
            'to_combo': to_combo,
            'action_btn': action_btn
        }
        self.emergency_rows.append(row_data)
        
        return row_data
    
    def toggle_row_selection(self, row_index):
        """Toggle the selection state of a row when action button is clicked."""
        if row_index < len(self.emergency_rows):
            row_data = self.emergency_rows[row_index]
            current_state = row_data['selected_var'].get()
            row_data['selected_var'].set(not current_state)
    
    def execute_emergency_requests(self):
        """Execute all selected emergency requests."""
        selected_requests = []
        invalid_requests = []
        
        # Collect all selected requests
        for i, row_data in enumerate(self.emergency_rows):
            if row_data['selected_var'].get():
                try:
                    from_floor = int(row_data['from_var'].get())
                    to_floor = int(row_data['to_var'].get())
                    
                    if from_floor == to_floor:
                        invalid_requests.append(f"Row {i+1}: From and To floors cannot be the same!")
                    else:
                        selected_requests.append((from_floor, to_floor))
                except ValueError:
                    invalid_requests.append(f"Row {i+1}: Invalid floor selection")
        
        # Show warnings for invalid requests
        if invalid_requests:
            messagebox.showwarning("Invalid Requests", 
                                 "Some requests are invalid:\n" + "\n".join(invalid_requests))
        
        # Execute valid requests
        if selected_requests:
            executed_count = 0
            for from_floor, to_floor in selected_requests:
                self.elevator.add_emergency_request(from_floor, to_floor)
                self.log(f"🚨 EMERGENCY: Floor {from_floor} → Floor {to_floor}", 'emergency')
                executed_count += 1
            
            # Clear selections after execution
            for row_data in self.emergency_rows:
                row_data['selected_var'].set(False)
            
            messagebox.showinfo("Success", 
                              f"Executed {executed_count} emergency request(s)!")
        else:
            if not invalid_requests:
                messagebox.showinfo("No Selection", "Please select at least one emergency request to execute.")
    
    def update_display(self):
        """Update all display elements."""
        status = self.elevator.get_detailed_status()
        
        # Update floor display
        self.floor_label.config(text=str(status['floor']))
        
        # Update direction display
        direction = status['direction']
        if direction == "UP":
            self.direction_label.config(text="UP ↑", fg=Colors.ELEVATOR_UP)
        elif direction == "DOWN":
            self.direction_label.config(text="DOWN ↓", fg=Colors.ELEVATOR_DOWN)
        else:
            self.direction_label.config(text="IDLE ●", fg=Colors.ELEVATOR_IDLE)
        
        # Update emergency display
        if status['emergency_mode']:
            self.emergency_label.config(text=f"ON ({status['emergency_count']})", fg=Colors.DANGER)
            self.emergency_card.config(highlightbackground=Colors.DANGER, highlightthickness=2)
        else:
            self.emergency_label.config(text="OFF", fg=Colors.TEXT_MUTED)
            self.emergency_card.config(highlightbackground=Colors.BORDER, highlightthickness=1)
        
        # Update elevator shaft visualization
        self.shaft_viz.update_state(
            status['floor'],
            status['direction_enum'],
            DoorState(status['door_state']),
            status['emergency_mode']
        )
        
        # Update stats
        stats = status.get('stats', {})
        self.floors_stat.set_value(stats.get('floors_traveled', 0))
        self.served_stat.set_value(stats.get('requests_served', 0))
        
        # Update pending requests
        self.pending_panel.update_requests(status.get('pending_requests', {}))
    
    def start_simulation(self):
        """Start the simulation loop."""
        def simulation_step():
            arrived, message = self.elevator.update()
            if message:
                tag = 'emergency' if '🚨' in message or 'Emergency' in message else 'success'
                self.log(message, tag)
            
            self.update_display()
            self.root.after(self.update_interval, simulation_step)
        
        self.root.after(self.update_interval, simulation_step)


def main():
    root = tk.Tk()
    app = ElevatorUI(root, num_floors=10, start_floor=3, start_direction="UP")
    root.mainloop()


if __name__ == "__main__":
    main()
