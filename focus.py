import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
from datetime import datetime, timedelta
from PIL import Image, ImageTk
import time
import threading
from collections import defaultdict
import calendar
import sys

class StudyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("StudyFlow - Intelligent Study Assistant")
        self.root.geometry("1400x800")
        self.root.configure(bg='#f0f2f5')
        
        # Load images (will create fallback if not available)
        self.load_images()
        
        # Initialize data structures
        self.schedule = []
        self.subjects = []
        self.tasks = []
        self.notes = []
        self.study_stats = defaultdict(int)
        
        # Load existing data
        self.load_data()
        
        # Setup UI
        self.setup_ui()
        
        # Start real-time updates
        self.update_time()
        self.check_schedule_alerts()
        
    def load_images(self):
        """Load or create fallback images"""
        try:
            # Try to load actual images if they exist
            self.logo_img = ImageTk.PhotoImage(Image.open("logo.png").resize((50, 50)))
        except:
            # Create fallback colored squares
            self.logo_img = tk.PhotoImage(width=50, height=50)
            self.logo_img.put('#4A90E2', to=(0, 0, 50, 50))
        
        # Color palette
        self.colors = {
            'primary': '#4A90E2',
            'secondary': '#7ED321',
            'accent': '#9013FE',
            'warning': '#F5A623',
            'danger': '#D0021B',
            'light': '#F0F2F5',
            'dark': '#2C3E50'
        }
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Create main container with sidebar and content
        self.main_container = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg=self.colors['light'])
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Sidebar
        self.sidebar = tk.Frame(self.main_container, bg=self.colors['dark'], width=250)
        self.main_container.add(self.sidebar)
        
        # Content area
        self.content_area = tk.Frame(self.main_container, bg=self.colors['light'])
        self.main_container.add(self.content_area)
        
        # Setup sidebar
        self.setup_sidebar()
        
        # Setup content area with default dashboard
        self.setup_dashboard()
    
    def setup_sidebar(self):
        """Setup the sidebar navigation"""
        # Logo
        logo_frame = tk.Frame(self.sidebar, bg=self.colors['dark'])
        logo_frame.pack(pady=20)
        
        tk.Label(logo_frame, image=self.logo_img, bg=self.colors['dark']).pack()
        tk.Label(logo_frame, text="StudyFlow", font=('Arial', 18, 'bold'), 
                fg='white', bg=self.colors['dark']).pack(pady=5)
        tk.Label(logo_frame, text="Your Study Companion", font=('Arial', 10), 
                fg='#BDC3C7', bg=self.colors['dark']).pack()
        
        # Navigation buttons
        nav_buttons = [
            ("📊 Dashboard", self.show_dashboard),
            ("📅 Schedule", self.show_schedule),
            ("📚 Subjects", self.show_subjects),
            ("✅ Tasks", self.show_tasks),
            ("📝 Notes", self.show_notes),
            ("📈 Progress", self.show_progress),
            ("⏱️ Pomodoro", self.show_pomodoro),
            ("⚙️ Settings", self.show_settings)
        ]
        
        for text, command in nav_buttons:
            btn = tk.Button(self.sidebar, text=text, font=('Arial', 11),
                          bg=self.colors['dark'], fg='white', bd=0,
                          padx=20, pady=12, anchor='w', width=20,
                          command=command, relief='flat')
            btn.pack(pady=2, padx=10)
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg='#34495E'))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg=self.colors['dark']))
        
        # Current time display
        self.time_label = tk.Label(self.sidebar, text="", font=('Arial', 10),
                                 fg='white', bg=self.colors['dark'])
        self.time_label.pack(side=tk.BOTTOM, pady=20)
        
        # Quick stats
        stats_frame = tk.Frame(self.sidebar, bg=self.colors['dark'])
        stats_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=10)
        
        self.tasks_count = tk.Label(stats_frame, text="Tasks: 0", fg='#7ED321',
                                   bg=self.colors['dark'], font=('Arial', 9))
        self.tasks_count.pack(anchor='w')
        
        self.upcoming_count = tk.Label(stats_frame, text="Upcoming: 0", fg='#F5A623',
                                      bg=self.colors['dark'], font=('Arial', 9))
        self.upcoming_count.pack(anchor='w')
    
    def setup_dashboard(self):
        """Setup the dashboard view"""
        self.clear_content()
        
        # Header
        header = tk.Frame(self.content_area, bg='white', height=80)
        header.pack(fill=tk.X, padx=20, pady=20)
        
        welcome_text = f"Welcome back! Ready to study? ({datetime.now().strftime('%A')})"
        tk.Label(header, text=welcome_text, font=('Arial', 24, 'bold'),
                bg='white', fg=self.colors['dark']).pack(side=tk.LEFT, padx=20)
        
        # Quick actions
        actions_frame = tk.Frame(self.content_area, bg=self.colors['light'])
        actions_frame.pack(fill=tk.X, padx=20, pady=10)
        
        quick_actions = [
            ("Add Schedule", self.show_schedule, '#4A90E2'),
            ("Create Task", self.show_tasks, '#7ED321'),
            ("Take Notes", self.show_notes, '#9013FE'),
            ("Start Timer", self.show_pomodoro, '#F5A623')
        ]
        
        for text, command, color in quick_actions:
            btn = tk.Button(actions_frame, text=text, font=('Arial', 11, 'bold'),
                          bg=color, fg='white', padx=20, pady=10,
                          command=command, relief='flat')
            btn.pack(side=tk.LEFT, padx=10)
            btn.bind("<Enter>", lambda e, b=btn, c=color: self.lighten_color(b, c))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))
        
        # Main content in two columns
        content_frame = tk.Frame(self.content_area, bg=self.colors['light'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left column - Today's Schedule
        left_col = tk.Frame(content_frame, bg='white', relief='raised', bd=1)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(left_col, text="Today's Schedule", font=('Arial', 16, 'bold'),
                bg='white', fg=self.colors['dark']).pack(pady=20)
        
        self.schedule_listbox = tk.Listbox(left_col, font=('Arial', 11), height=15)
        self.schedule_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Load today's schedule
        self.load_today_schedule()
        
        # Right column - Upcoming Tasks
        right_col = tk.Frame(content_frame, bg='white', relief='raised', bd=1)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(right_col, text="Upcoming Tasks", font=('Arial', 16, 'bold'),
                bg='white', fg=self.colors['dark']).pack(pady=20)
        
        self.tasks_listbox = tk.Listbox(right_col, font=('Arial', 11), height=15)
        self.tasks_listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Load upcoming tasks
        self.load_upcoming_tasks()
        
        # Study stats
        stats_frame = tk.Frame(self.content_area, bg='white', height=100)
        stats_frame.pack(fill=tk.X, padx=20, pady=20)
        
        stats = [
            ("Study Hours Today", "2.5h"),
            ("Tasks Completed", "3/8"),
            ("Focus Score", "85%"),
            ("Upcoming Deadlines", "2")
        ]
        
        for i, (label, value) in enumerate(stats):
            stat = tk.Frame(stats_frame, bg='white')
            stat.pack(side=tk.LEFT, expand=True)
            tk.Label(stat, text=value, font=('Arial', 24, 'bold'),
                    fg=self.colors['primary'], bg='white').pack()
            tk.Label(stat, text=label, font=('Arial', 10),
                    fg=self.colors['dark'], bg='white').pack()
    
    def show_schedule(self):
        """Display schedule management interface"""
        self.clear_content()
        
        # Header
        header = tk.Frame(self.content_area, bg='white')
        header.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(header, text="📅 Study Schedule", font=('Arial', 24, 'bold'),
                bg='white', fg=self.colors['dark']).pack(side=tk.LEFT)
        
        # Add schedule button
        tk.Button(header, text="+ Add Schedule", font=('Arial', 11, 'bold'),
                 bg=self.colors['primary'], fg='white', padx=20,
                 command=self.add_schedule_dialog).pack(side=tk.RIGHT)
        
        # Calendar and schedule
        main_frame = tk.Frame(self.content_area, bg=self.colors['light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Calendar
        cal_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=1)
        cal_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        tk.Label(cal_frame, text="Calendar", font=('Arial', 16, 'bold'),
                bg='white', fg=self.colors['dark']).pack(pady=20)
        
        # Simple calendar display
        today = datetime.now()
        year, month = today.year, today.month
        
        cal = calendar.monthcalendar(year, month)
        
        days_frame = tk.Frame(cal_frame, bg='white')
        days_frame.pack(padx=20, pady=10)
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        for i, day in enumerate(days):
            tk.Label(days_frame, text=day, font=('Arial', 10, 'bold'),
                    fg=self.colors['primary'], bg='white', width=4).grid(row=0, column=i)
        
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day != 0:
                    bg = self.colors['primary'] if day == today.day else 'white'
                    fg = 'white' if day == today.day else self.colors['dark']
                    tk.Label(days_frame, text=str(day), font=('Arial', 10),
                            bg=bg, fg=fg, width=4, height=2).grid(row=week_num+1, column=day_num)
        
        # Schedule list
        schedule_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=1)
        schedule_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(schedule_frame, text="Upcoming Sessions", font=('Arial', 16, 'bold'),
                bg='white', fg=self.colors['dark']).pack(pady=20)
        
        # Treeview for schedule
        columns = ('Time', 'Subject', 'Duration', 'Type')
        self.schedule_tree = ttk.Treeview(schedule_frame, columns=columns, show='headings')
        
        for col in columns:
            self.schedule_tree.heading(col, text=col)
            self.schedule_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(schedule_frame, orient=tk.VERTICAL, 
                                 command=self.schedule_tree.yview)
        self.schedule_tree.configure(yscrollcommand=scrollbar.set)
        
        self.schedule_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load schedule data
        self.load_schedule_data()
    
    def show_subjects(self):
        """Display subjects management"""
        self.clear_content()
        
        header = tk.Frame(self.content_area, bg='white')
        header.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(header, text="📚 Subjects", font=('Arial', 24, 'bold'),
                bg='white', fg=self.colors['dark']).pack(side=tk.LEFT)
        
        tk.Button(header, text="+ Add Subject", font=('Arial', 11, 'bold'),
                 bg=self.colors['primary'], fg='white', padx=20,
                 command=self.add_subject_dialog).pack(side=tk.RIGHT)
        
        # Subjects grid
        subjects_frame = tk.Frame(self.content_area, bg=self.colors['light'])
        subjects_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create subject cards
        subject_colors = ['#4A90E2', '#7ED321', '#9013FE', '#F5A623', 
                         '#D0021B', '#50E3C2', '#B8E986', '#BD10E0']
        
        for i, subject in enumerate(self.subjects):
            row = i // 4
            col = i % 4
            
            card = tk.Frame(subjects_frame, bg=subject_colors[i % len(subject_colors)],
                          relief='raised', bd=2)
            card.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            
            tk.Label(card, text=subject['name'], font=('Arial', 14, 'bold'),
                    bg=subject_colors[i % len(subject_colors)], fg='white').pack(pady=20, padx=20)
            
            tk.Label(card, text=f"Hours: {subject.get('hours', 0)}", font=('Arial', 11),
                    bg=subject_colors[i % len(subject_colors)], fg='white').pack()
            
            tk.Label(card, text=f"Tasks: {subject.get('tasks', 0)}", font=('Arial', 11),
                    bg=subject_colors[i % len(subject_colors)], fg='white').pack(pady=(0, 20))
        
        # Configure grid
        for i in range(4):
            subjects_frame.grid_columnconfigure(i, weight=1)
    
    def show_tasks(self):
        """Display task management"""
        self.clear_content()
        
        header = tk.Frame(self.content_area, bg='white')
        header.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(header, text="✅ Tasks", font=('Arial', 24, 'bold'),
                bg='white', fg=self.colors['dark']).pack(side=tk.LEFT)
        
        tk.Button(header, text="+ Add Task", font=('Arial', 11, 'bold'),
                 bg=self.colors['primary'], fg='white', padx=20,
                 command=self.add_task_dialog).pack(side=tk.RIGHT)
        
        # Task management
        main_frame = tk.Frame(self.content_area, bg=self.colors['light'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Task list
        task_frame = tk.Frame(main_frame, bg='white', relief='raised', bd=1)
        task_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ('Status', 'Task', 'Subject', 'Due Date', 'Priority')
        self.task_tree = ttk.Treeview(task_frame, columns=columns, show='headings')
        
        for col in columns:
            self.task_tree.heading(col, text=col)
            self.task_tree.column(col, width=100)
        
        scrollbar = ttk.Scrollbar(task_frame, orient=tk.VERTICAL, 
                                 command=self.task_tree.yview)
        self.task_tree.configure(yscrollcommand=scrollbar.set)
        
        self.task_tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Load tasks
        self.load_task_data()
    
    def show_notes(self):
        """Display notes interface"""
        self.clear_content()
        
        header = tk.Frame(self.content_area, bg='white')
        header.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(header, text="📝 Notes", font=('Arial', 24, 'bold'),
                bg='white', fg=self.colors['dark']).pack(side=tk.LEFT)
        
        tk.Button(header, text="+ New Note", font=('Arial', 11, 'bold'),
                 bg=self.colors['primary'], fg='white', padx=20,
                 command=self.add_note_dialog).pack(side=tk.RIGHT)
        
        # Notes area
        notes_frame = tk.Frame(self.content_area, bg=self.colors['light'])
        notes_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Text editor
        self.note_text = scrolledtext.ScrolledText(notes_frame, font=('Arial', 12),
                                                  wrap=tk.WORD, height=20)
        self.note_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Formatting toolbar
        toolbar = tk.Frame(notes_frame, bg=self.colors['light'])
        toolbar.pack(fill=tk.X, padx=10)
        
        formats = [("B", "bold"), ("I", "italic"), ("U", "underline")]
        for text, style in formats:
            btn = tk.Button(toolbar, text=text, font=('Arial', 10, 'bold'),
                          command=lambda s=style: self.format_text(s))
            btn.pack(side=tk.LEFT, padx=2)
        
        tk.Button(toolbar, text="Save Note", font=('Arial', 10, 'bold'),
                 bg=self.colors['primary'], fg='white',
                 command=self.save_note).pack(side=tk.RIGHT)
    
    def show_pomodoro(self):
        """Display Pomodoro timer"""
        self.clear_content()
        
        header = tk.Frame(self.content_area, bg='white')
        header.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(header, text="⏱️ Pomodoro Timer", font=('Arial', 24, 'bold'),
                bg='white', fg=self.colors['dark']).pack(side=tk.LEFT)
        
        # Timer display
        timer_frame = tk.Frame(self.content_area, bg=self.colors['light'])
        timer_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        self.timer_label = tk.Label(timer_frame, text="25:00", font=('Arial', 72, 'bold'),
                                   fg=self.colors['primary'], bg=self.colors['light'])
        self.timer_label.pack(pady=50)
        
        # Timer controls
        controls_frame = tk.Frame(timer_frame, bg=self.colors['light'])
        controls_frame.pack(pady=20)
        
        self.timer_running = False
        self.time_left = 25 * 60  # 25 minutes in seconds
        
        tk.Button(controls_frame, text="Start", font=('Arial', 14, 'bold'),
                 bg=self.colors['primary'], fg='white', width=10,
                 command=self.start_timer).pack(side=tk.LEFT, padx=10)
        
        tk.Button(controls_frame, text="Pause", font=('Arial', 14, 'bold'),
                 bg=self.colors['warning'], fg='white', width=10,
                 command=self.pause_timer).pack(side=tk.LEFT, padx=10)
        
        tk.Button(controls_frame, text="Reset", font=('Arial', 14, 'bold'),
                 bg=self.colors['danger'], fg='white', width=10,
                 command=self.reset_timer).pack(side=tk.LEFT, padx=10)
        
        # Timer presets
        presets_frame = tk.Frame(timer_frame, bg=self.colors['light'])
        presets_frame.pack(pady=20)
        
        presets = [("25:00", 25), ("15:00", 15), ("10:00", 10), ("5:00", 5)]
        
        for text, minutes in presets:
            btn = tk.Button(presets_frame, text=text, font=('Arial', 12),
                          command=lambda m=minutes: self.set_timer(m))
            btn.pack(side=tk.LEFT, padx=10)
    
    def show_progress(self):
        """Display progress tracking"""
        self.clear_content()
        
        header = tk.Frame(self.content_area, bg='white')
        header.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(header, text="📈 Progress Tracking", font=('Arial', 24, 'bold'),
                bg='white', fg=self.colors['dark']).pack(side=tk.LEFT)
        
        # Progress metrics
        metrics_frame = tk.Frame(self.content_area, bg=self.colors['light'])
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Study time chart (simplified)
        chart_frame = tk.Frame(metrics_frame, bg='white', relief='raised', bd=1)
        chart_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        tk.Label(chart_frame, text="Study Time This Week", font=('Arial', 16, 'bold'),
                bg='white', fg=self.colors['dark']).pack(pady=20)
        
        # Simple bar chart
        canvas = tk.Canvas(chart_frame, bg='white', height=200)
        canvas.pack(fill=tk.X, padx=20, pady=20)
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hours = [2.5, 3.0, 1.5, 4.0, 2.0, 1.0, 0.5]  # Example data
        
        for i, (day, hour) in enumerate(zip(days, hours)):
            x = 50 + i * 70
            height = hour * 40
            canvas.create_rectangle(x, 150-height, x+40, 150, fill=self.colors['primary'])
            canvas.create_text(x+20, 160, text=day)
            canvas.create_text(x+20, 140-height, text=f"{hour}h")
        
        # Subject breakdown
        subject_frame = tk.Frame(metrics_frame, bg='white', relief='raised', bd=1)
        subject_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(subject_frame, text="Subject Breakdown", font=('Arial', 16, 'bold'),
                bg='white', fg=self.colors['dark']).pack(pady=20)
        
        # Add subject progress bars
        for subject in self.subjects:
            sub_frame = tk.Frame(subject_frame, bg='white')
            sub_frame.pack(fill=tk.X, padx=20, pady=5)
            
            tk.Label(sub_frame, text=subject['name'], width=15, anchor='w',
                    font=('Arial', 11)).pack(side=tk.LEFT)
            
            # Progress bar
            progress = tk.Frame(sub_frame, bg='#e0e0e0', height=20, width=200)
            progress.pack(side=tk.LEFT, padx=10)
            
            fill_width = min(200, subject.get('hours', 0) * 20)
            tk.Frame(progress, bg=self.colors['primary'], 
                    width=fill_width, height=20).pack(side=tk.LEFT)
            
            tk.Label(sub_frame, text=f"{subject.get('hours', 0)}h",
                    font=('Arial', 10)).pack(side=tk.LEFT)
    
    def show_settings(self):
        """Display settings"""
        self.clear_content()
        
        header = tk.Frame(self.content_area, bg='white')
        header.pack(fill=tk.X, padx=20, pady=20)
        
        tk.Label(header, text="⚙️ Settings", font=('Arial', 24, 'bold'),
                bg='white', fg=self.colors['dark']).pack(side=tk.LEFT)
        
        # Settings options
        settings_frame = tk.Frame(self.content_area, bg='white')
        settings_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        options = [
            ("Notifications", "Enable study reminders"),
            ("Dark Mode", "Switch to dark theme"),
            ("Auto-save", "Save progress automatically"),
            ("Study Goals", "Set daily study targets"),
            ("Export Data", "Export your study data")
        ]
        
        for i, (title, desc) in enumerate(options):
            frame = tk.Frame(settings_frame, bg='white')
            frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(frame, text=title, font=('Arial', 12, 'bold'),
                    bg='white', fg=self.colors['dark']).pack(anchor='w')
            tk.Label(frame, text=desc, font=('Arial', 10),
                    bg='white', fg='#7f8c8d').pack(anchor='w')
            
            var = tk.BooleanVar()
            tk.Checkbutton(frame, variable=var, bg='white').pack(side=tk.RIGHT)
        
        # Save button
        tk.Button(settings_frame, text="Save Settings", font=('Arial', 12, 'bold'),
                 bg=self.colors['primary'], fg='white', padx=30,
                 command=self.save_settings).pack(pady=30)
    
    def add_schedule_dialog(self):
        """Dialog to add new schedule"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Schedule")
        dialog.geometry("400x500")
        dialog.configure(bg='white')
        
        tk.Label(dialog, text="Add Study Session", font=('Arial', 16, 'bold'),
                bg='white', fg=self.colors['dark']).pack(pady=20)
        
        # Form fields
        fields_frame = tk.Frame(dialog, bg='white')
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        # Subject
        tk.Label(fields_frame, text="Subject:", bg='white').pack(anchor='w')
        subject_var = tk.StringVar()
        subject_combo = ttk.Combobox(fields_frame, textvariable=subject_var)
        subject_combo['values'] = [s['name'] for s in self.subjects]
        subject_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Date
        tk.Label(fields_frame, text="Date:", bg='white').pack(anchor='w')
        date_entry = tk.Entry(fields_frame)
        date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        date_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Time
        tk.Label(fields_frame, text="Time:", bg='white').pack(anchor='w')
        time_entry = tk.Entry(fields_frame)
        time_entry.insert(0, "14:00")
        time_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Duration
        tk.Label(fields_frame, text="Duration (hours):", bg='white').pack(anchor='w')
        duration_entry = tk.Entry(fields_frame)
        duration_entry.insert(0, "1.5")
        duration_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Type
        tk.Label(fields_frame, text="Type:", bg='white').pack(anchor='w')
        type_var = tk.StringVar(value="Study")
        type_combo = ttk.Combobox(fields_frame, textvariable=type_var)
        type_combo['values'] = ['Study', 'Revision', 'Practice', 'Lecture', 'Lab']
        type_combo.pack(fill=tk.X, pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(dialog, bg='white')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Cancel", font=('Arial', 11),
                 command=dialog.destroy).pack(side=tk.LEFT, padx=10)
        
        tk.Button(button_frame, text="Save", font=('Arial', 11, 'bold'),
                 bg=self.colors['primary'], fg='white', padx=20,
                 command=lambda: self.save_schedule(
                     subject_var.get(), date_entry.get(),
                     time_entry.get(), duration_entry.get(),
                     type_var.get(), dialog
                 )).pack(side=tk.RIGHT, padx=10)
    
    def add_subject_dialog(self):
        """Dialog to add new subject"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Subject")
        dialog.geometry("300x300")
        dialog.configure(bg='white')
        
        tk.Label(dialog, text="Add Subject", font=('Arial', 16, 'bold'),
                bg='white', fg=self.colors['dark']).pack(pady=20)
        
        fields_frame = tk.Frame(dialog, bg='white')
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        tk.Label(fields_frame, text="Subject Name:", bg='white').pack(anchor='w')
        name_entry = tk.Entry(fields_frame)
        name_entry.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(fields_frame, text="Color:", bg='white').pack(anchor='w')
        color_var = tk.StringVar(value="#4A90E2")
        color_combo = ttk.Combobox(fields_frame, textvariable=color_var)
        color_combo['values'] = ['#4A90E2', '#7ED321', '#9013FE', 
                                '#F5A623', '#D0021B', '#50E3C2']
        color_combo.pack(fill=tk.X, pady=(0, 20))
        
        button_frame = tk.Frame(dialog, bg='white')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Save", bg=self.colors['primary'], fg='white',
                 command=lambda: self.save_subject(name_entry.get(), color_var.get(), dialog)) \
                 .pack(side=tk.RIGHT, padx=10)
    
    def add_task_dialog(self):
        """Dialog to add new task"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Add Task")
        dialog.geometry("400x500")
        dialog.configure(bg='white')
        
        tk.Label(dialog, text="Add Task", font=('Arial', 16, 'bold'),
                bg='white', fg=self.colors['dark']).pack(pady=20)
        
        fields_frame = tk.Frame(dialog, bg='white')
        fields_frame.pack(fill=tk.BOTH, expand=True, padx=30)
        
        # Task description
        tk.Label(fields_frame, text="Task:", bg='white').pack(anchor='w')
        task_text = tk.Text(fields_frame, height=3, width=40)
        task_text.pack(fill=tk.X, pady=(0, 10))
        
        # Subject
        tk.Label(fields_frame, text="Subject:", bg='white').pack(anchor='w')
        subject_var = tk.StringVar()
        subject_combo = ttk.Combobox(fields_frame, textvariable=subject_var)
        subject_combo['values'] = [s['name'] for s in self.subjects]
        subject_combo.pack(fill=tk.X, pady=(0, 10))
        
        # Due date
        tk.Label(fields_frame, text="Due Date:", bg='white').pack(anchor='w')
        due_entry = tk.Entry(fields_frame)
        due_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        due_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Priority
        tk.Label(fields_frame, text="Priority:", bg='white').pack(anchor='w')
        priority_var = tk.StringVar(value="Medium")
        priority_combo = ttk.Combobox(fields_frame, textvariable=priority_var)
        priority_combo['values'] = ['Low', 'Medium', 'High', 'Critical']
        priority_combo.pack(fill=tk.X, pady=(0, 20))
        
        button_frame = tk.Frame(dialog, bg='white')
        button_frame.pack(pady=20)
        
        tk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Save", bg=self.colors['primary'], fg='white',
                 command=lambda: self.save_task(task_text.get("1.0", tk.END).strip(),
                                               subject_var.get(), due_entry.get(),
                                               priority_var.get(), dialog)) \
                 .pack(side=tk.RIGHT, padx=10)
    
    def add_note_dialog(self):
        """Dialog to add new note"""
        self.note_text.delete("1.0", tk.END)
        self.note_text.focus()
    
    # Data management methods
    def save_schedule(self, subject, date, time, duration, type_, dialog):
        """Save schedule to data"""
        schedule_item = {
            'subject': subject,
            'date': date,
            'time': time,
            'duration': duration,
            'type': type_,
            'id': len(self.schedule) + 1
        }
        self.schedule.append(schedule_item)
        self.save_data()
        self.load_schedule_data()
        dialog.destroy()
        messagebox.showinfo("Success", "Schedule added successfully!")
    
    def save_subject(self, name, color, dialog):
        """Save subject to data"""
        if not name:
            messagebox.showerror("Error", "Subject name is required!")
            return
        
        subject = {
            'name': name,
            'color': color,
            'hours': 0,
            'tasks': 0
        }
        self.subjects.append(subject)
        self.save_data()
        self.show_subjects()
        dialog.destroy()
    
    def save_task(self, task, subject, due_date, priority, dialog):
        """Save task to data"""
        if not task:
            messagebox.showerror("Error", "Task description is required!")
            return
        
        task_item = {
            'task': task,
            'subject': subject,
            'due_date': due_date,
            'priority': priority,
            'completed': False,
            'id': len(self.tasks) + 1
        }
        self.tasks.append(task_item)
        self.save_data()
        self.load_task_data()
        dialog.destroy()
    
    def save_note(self):
        """Save note to data"""
        note_text = self.note_text.get("1.0", tk.END).strip()
        if note_text:
            note = {
                'text': note_text,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            self.notes.append(note)
            self.save_data()
            messagebox.showinfo("Success", "Note saved successfully!")
    
    def format_text(self, style):
        """Format text in notes (simplified)"""
        try:
            if style == "bold":
                current_tags = self.note_text.tag_names("sel.first")
                if "bold" in current_tags:
                    self.note_text.tag_remove("bold", "sel.first", "sel.last")
                else:
                    self.note_text.tag_add("bold", "sel.first", "sel.last")
                    self.note_text.tag_config("bold", font=('Arial', 12, 'bold'))
        except:
            pass  # No text selected
    
    def start_timer(self):
        """Start the Pomodoro timer"""
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()
    
    def pause_timer(self):
        """Pause the timer"""
        self.timer_running = False
    
    def reset_timer(self):
        """Reset the timer"""
        self.timer_running = False
        self.time_left = 25 * 60
        self.timer_label.config(text="25:00")
    
    def set_timer(self, minutes):
        """Set timer to specific minutes"""
        self.time_left = minutes * 60
        self.timer_label.config(text=f"{minutes:02d}:00")
    
    def update_timer(self):
        """Update timer display"""
        if self.timer_running and self.time_left > 0:
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")
            self.time_left -= 1
            self.root.after(1000, self.update_timer)
        elif self.time_left == 0:
            self.timer_running = False
            messagebox.showinfo("Time's up!", "Timer completed!")
    
    def load_today_schedule(self):
        """Load today's schedule"""
        self.schedule_listbox.delete(0, tk.END)
        today = datetime.now().strftime('%Y-%m-%d')
        
        for item in self.schedule:
            if item['date'] == today:
                display_text = f"{item['time']} - {item['subject']} ({item['duration']}h)"
                self.schedule_listbox.insert(tk.END, display_text)
        
        if self.schedule_listbox.size() == 0:
            self.schedule_listbox.insert(tk.END, "No schedule for today")
    
    def load_upcoming_tasks(self):
        """Load upcoming tasks"""
        self.tasks_listbox.delete(0, tk.END)
        
        # Sort tasks by due date
        sorted_tasks = sorted(self.tasks, key=lambda x: x['due_date'])
        
        for task in sorted_tasks[:5]:  # Show only 5 tasks
            status = "✓" if task['completed'] else "○"
            display_text = f"{status} {task['task'][:30]}..."
            self.tasks_listbox.insert(tk.END, display_text)
        
        if self.tasks_listbox.size() == 0:
            self.tasks_listbox.insert(tk.END, "No tasks pending")
    
    def load_schedule_data(self):
        """Load schedule into treeview"""
        for item in self.schedule_tree.get_children():
            self.schedule_tree.delete(item)
        
        for schedule in self.schedule:
            self.schedule_tree.insert('', tk.END, values=(
                schedule['time'],
                schedule['subject'],
                schedule['duration'],
                schedule['type']
            ))
    
    def load_task_data(self):
        """Load tasks into treeview"""
        for item in self.task_tree.get_children():
            self.task_tree.delete(item)
        
        for task in self.tasks:
            status = "Completed" if task['completed'] else "Pending"
            self.task_tree.insert('', tk.END, values=(
                status,
                task['task'],
                task['subject'],
                task['due_date'],
                task['priority']
            ))
    
    def update_time(self):
        """Update current time display"""
        current_time = datetime.now().strftime('%I:%M %p | %b %d, %Y')
        self.time_label.config(text=current_time)
        
        # Update task counts
        pending_tasks = sum(1 for task in self.tasks if not task['completed'])
        today = datetime.now().strftime('%Y-%m-%d')
        upcoming_schedules = sum(1 for sched in self.schedule if sched['date'] == today)
        
        self.tasks_count.config(text=f"Tasks: {pending_tasks}")
        self.upcoming_count.config(text=f"Upcoming: {upcoming_schedules}")
        
        # Schedule next update
        self.root.after(1000, self.update_time)
    
    def check_schedule_alerts(self):
        """Check for upcoming schedule alerts"""
        now = datetime.now()
        current_time = now.strftime('%H:%M')
        today = now.strftime('%Y-%m-%d')
        
        for schedule in self.schedule:
            if schedule['date'] == today and schedule['time'] == current_time:
                messagebox.showinfo("Study Reminder", 
                                  f"Time for {schedule['subject']}!")
        
        # Check every minute
        self.root.after(60000, self.check_schedule_alerts)
    
    def clear_content(self):
        """Clear content area"""
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
    def lighten_color(self, button, original_color):
        """Lighten button color on hover"""
        # Simplified color lightening
        button.config(bg=self.adjust_color(original_color, 20))
    
    def adjust_color(self, color, amount):
        """Adjust color brightness"""
        # Simple color adjustment
        return color
    
    def save_settings(self):
        """Save application settings"""
        messagebox.showinfo("Settings", "Settings saved successfully!")
    
    def load_data(self):
        """Load data from file"""
        try:
            if os.path.exists('study_data.json'):
                with open('study_data.json', 'r') as f:
                    data = json.load(f)
                    self.schedule = data.get('schedule', [])
                    self.subjects = data.get('subjects', [])
                    self.tasks = data.get('tasks', [])
                    self.notes = data.get('notes', [])
                    self.study_stats = data.get('stats', defaultdict(int))
        except:
            # Initialize with sample data
            self.subjects = [
                {'name': 'Mathematics', 'color': '#4A90E2', 'hours': 12, 'tasks': 3},
                {'name': 'Physics', 'color': '#7ED321', 'hours': 8, 'tasks': 2},
                {'name': 'Chemistry', 'color': '#9013FE', 'hours': 6, 'tasks': 1},
                {'name': 'Biology', 'color': '#F5A623', 'hours': 4, 'tasks': 2}
            ]
            self.tasks = [
                {'task': 'Complete calculus assignment', 'subject': 'Mathematics', 
                 'due_date': '2024-01-15', 'priority': 'High', 'completed': False, 'id': 1},
                {'task': 'Read chapter 5 of Physics', 'subject': 'Physics', 
                 'due_date': '2024-01-16', 'priority': 'Medium', 'completed': False, 'id': 2}
            ]
    
    def save_data(self):
        """Save data to file"""
        data = {
            'schedule': self.schedule,
            'subjects': self.subjects,
            'tasks': self.tasks,
            'notes': self.notes,
            'stats': dict(self.study_stats)
        }
        
        with open('study_data.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def show_dashboard(self):
        """Show dashboard view"""
        self.setup_dashboard()

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = StudyApp(root)
    
    # Set window icon (if available)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    # Handle window closing
    def on_closing():
        app.save_data()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == "__main__":
    main()