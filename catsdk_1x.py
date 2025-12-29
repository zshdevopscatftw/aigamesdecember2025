#!/usr/bin/env python3
"""
CatSDK 1.X - An AutoGPT/ChatGPT-like Interface
A comprehensive Tkinter application with chatbot, code interpreter,
sandbox, compiler, and more - all without LLMs!
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox, font
import subprocess
import sys
import io
import os
import threading
import traceback
import re
import json
import code
import contextlib
from datetime import datetime
from collections import deque

# ============================================================================
# THEME AND STYLING - ChatGPT/AutoGPT Dark Theme
# ============================================================================
COLORS = {
    'bg_dark': '#0d1117',
    'bg_sidebar': '#161b22',
    'bg_chat': '#1a1f26',
    'bg_input': '#21262d',
    'bg_code': '#161b22',
    'accent': '#58a6ff',
    'accent_green': '#3fb950',
    'accent_orange': '#d29922',
    'accent_red': '#f85149',
    'accent_purple': '#a371f7',
    'text_primary': '#e6edf3',
    'text_secondary': '#8b949e',
    'text_muted': '#6e7681',
    'border': '#30363d',
    'button_hover': '#30363d',
    'user_bubble': '#1f6feb',
    'bot_bubble': '#21262d',
}

class CatSDKApp:
    """Main CatSDK Application - AutoGPT/ChatGPT-like Interface"""

    def __init__(self, root):
        self.root = root
        self.root.title("CatSDK 1.X - AI Assistant Interface")
        self.root.geometry("1400x900")
        self.root.configure(bg=COLORS['bg_dark'])

        # State
        self.conversations = {}
        self.current_conversation = None
        self.conversation_counter = 0
        self.code_history = deque(maxlen=100)
        self.sandbox_globals = {'__builtins__': __builtins__}
        self.sandbox_locals = {}

        # Command patterns for the chatbot
        self.commands = self._init_commands()

        # Setup UI
        self._setup_fonts()
        self._setup_styles()
        self._create_ui()
        self._bind_events()

        # Create initial conversation
        self.new_conversation()

    def _setup_fonts(self):
        """Setup custom fonts"""
        self.font_title = font.Font(family="Helvetica", size=14, weight="bold")
        self.font_normal = font.Font(family="Helvetica", size=11)
        self.font_small = font.Font(family="Helvetica", size=10)
        self.font_code = font.Font(family="Courier", size=11)
        self.font_chat = font.Font(family="Helvetica", size=12)

    def _setup_styles(self):
        """Setup ttk styles"""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Notebook style
        self.style.configure('Dark.TNotebook', background=COLORS['bg_dark'])
        self.style.configure('Dark.TNotebook.Tab',
                           background=COLORS['bg_sidebar'],
                           foreground=COLORS['text_primary'],
                           padding=[15, 8])
        self.style.map('Dark.TNotebook.Tab',
                      background=[('selected', COLORS['accent'])],
                      foreground=[('selected', '#ffffff')])

        # Button style
        self.style.configure('Dark.TButton',
                           background=COLORS['bg_input'],
                           foreground=COLORS['text_primary'],
                           borderwidth=0,
                           padding=[10, 5])

    def _create_ui(self):
        """Create the main UI layout"""
        # Main container
        self.main_container = tk.Frame(self.root, bg=COLORS['bg_dark'])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar
        self._create_sidebar()

        # Content area with notebook
        self._create_content_area()

    def _create_sidebar(self):
        """Create the sidebar with conversation history"""
        self.sidebar = tk.Frame(self.main_container, bg=COLORS['bg_sidebar'], width=280)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        # Logo/Title
        title_frame = tk.Frame(self.sidebar, bg=COLORS['bg_sidebar'])
        title_frame.pack(fill=tk.X, padx=15, pady=20)

        logo_label = tk.Label(title_frame, text="🐱 CatSDK 1.X",
                             font=self.font_title,
                             bg=COLORS['bg_sidebar'],
                             fg=COLORS['accent'])
        logo_label.pack(side=tk.LEFT)

        version_label = tk.Label(title_frame, text="v1.0.0",
                                font=self.font_small,
                                bg=COLORS['bg_sidebar'],
                                fg=COLORS['text_muted'])
        version_label.pack(side=tk.RIGHT, pady=5)

        # New Chat Button
        new_chat_btn = tk.Button(self.sidebar, text="+ New Chat",
                                font=self.font_normal,
                                bg=COLORS['accent'],
                                fg='white',
                                activebackground=COLORS['accent_green'],
                                activeforeground='white',
                                border=0,
                                cursor='hand2',
                                command=self.new_conversation)
        new_chat_btn.pack(fill=tk.X, padx=15, pady=10)

        # Separator
        sep = tk.Frame(self.sidebar, height=1, bg=COLORS['border'])
        sep.pack(fill=tk.X, padx=15, pady=10)

        # Conversations label
        conv_label = tk.Label(self.sidebar, text="Conversations",
                             font=self.font_small,
                             bg=COLORS['bg_sidebar'],
                             fg=COLORS['text_muted'])
        conv_label.pack(anchor=tk.W, padx=15)

        # Conversations list
        self.conv_frame = tk.Frame(self.sidebar, bg=COLORS['bg_sidebar'])
        self.conv_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Bottom section - Features
        bottom_frame = tk.Frame(self.sidebar, bg=COLORS['bg_sidebar'])
        bottom_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=15, pady=15)

        features = ["💻 Code Interpreter", "📦 Sandbox Mode", "🔧 Compiler", "📁 File Manager"]
        for feat in features:
            lbl = tk.Label(bottom_frame, text=feat,
                          font=self.font_small,
                          bg=COLORS['bg_sidebar'],
                          fg=COLORS['text_secondary'])
            lbl.pack(anchor=tk.W, pady=2)

    def _create_content_area(self):
        """Create the main content area with tabs"""
        self.content = tk.Frame(self.main_container, bg=COLORS['bg_dark'])
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Notebook for different modes
        self.notebook = ttk.Notebook(self.content, style='Dark.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create tabs
        self._create_chat_tab()
        self._create_code_interpreter_tab()
        self._create_sandbox_tab()
        self._create_compiler_tab()
        self._create_file_manager_tab()

    def _create_chat_tab(self):
        """Create the main chat interface tab"""
        chat_frame = tk.Frame(self.notebook, bg=COLORS['bg_chat'])
        self.notebook.add(chat_frame, text="💬 Chat")

        # Chat header
        header = tk.Frame(chat_frame, bg=COLORS['bg_dark'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        header_label = tk.Label(header, text="🐱 CatSDK Assistant",
                               font=self.font_title,
                               bg=COLORS['bg_dark'],
                               fg=COLORS['text_primary'])
        header_label.pack(side=tk.LEFT, padx=20, pady=15)

        status_label = tk.Label(header, text="● Online",
                               font=self.font_small,
                               bg=COLORS['bg_dark'],
                               fg=COLORS['accent_green'])
        status_label.pack(side=tk.RIGHT, padx=20)

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(chat_frame,
                                                      wrap=tk.WORD,
                                                      font=self.font_chat,
                                                      bg=COLORS['bg_chat'],
                                                      fg=COLORS['text_primary'],
                                                      insertbackground=COLORS['text_primary'],
                                                      selectbackground=COLORS['accent'],
                                                      relief=tk.FLAT,
                                                      padx=20,
                                                      pady=20)
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)

        # Configure tags for message styling
        self.chat_display.tag_configure('user', foreground=COLORS['accent'],
                                        font=font.Font(family="Helvetica", size=12, weight="bold"))
        self.chat_display.tag_configure('bot', foreground=COLORS['accent_green'],
                                        font=font.Font(family="Helvetica", size=12, weight="bold"))
        self.chat_display.tag_configure('code', foreground=COLORS['accent_orange'],
                                        font=self.font_code, background=COLORS['bg_code'])
        self.chat_display.tag_configure('error', foreground=COLORS['accent_red'])
        self.chat_display.tag_configure('system', foreground=COLORS['accent_purple'])

        # Input area
        input_frame = tk.Frame(chat_frame, bg=COLORS['bg_input'], height=100)
        input_frame.pack(fill=tk.X, padx=20, pady=20)

        # Input container with rounded appearance
        input_container = tk.Frame(input_frame, bg=COLORS['bg_input'])
        input_container.pack(fill=tk.X, pady=10, padx=10)

        self.chat_input = tk.Text(input_container,
                                  height=3,
                                  font=self.font_normal,
                                  bg=COLORS['bg_input'],
                                  fg=COLORS['text_primary'],
                                  insertbackground=COLORS['text_primary'],
                                  relief=tk.FLAT,
                                  wrap=tk.WORD)
        self.chat_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Send button
        send_btn = tk.Button(input_container, text="Send ➤",
                            font=self.font_normal,
                            bg=COLORS['accent'],
                            fg='white',
                            activebackground=COLORS['accent_green'],
                            border=0,
                            cursor='hand2',
                            command=self.send_message)
        send_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        # Quick actions
        actions_frame = tk.Frame(input_frame, bg=COLORS['bg_input'])
        actions_frame.pack(fill=tk.X, padx=10)

        quick_actions = [
            ("📁 Upload File", self.upload_file),
            ("💻 Run Code", lambda: self.notebook.select(1)),
            ("🔧 Compile", lambda: self.notebook.select(3)),
            ("❓ Help", self.show_help)
        ]

        for text, cmd in quick_actions:
            btn = tk.Button(actions_frame, text=text,
                           font=self.font_small,
                           bg=COLORS['bg_dark'],
                           fg=COLORS['text_secondary'],
                           activebackground=COLORS['button_hover'],
                           border=0,
                           cursor='hand2',
                           command=cmd)
            btn.pack(side=tk.LEFT, padx=5)

    def _create_code_interpreter_tab(self):
        """Create the code interpreter tab"""
        interp_frame = tk.Frame(self.notebook, bg=COLORS['bg_dark'])
        self.notebook.add(interp_frame, text="💻 Code Interpreter")

        # Split pane
        paned = tk.PanedWindow(interp_frame, orient=tk.HORIZONTAL,
                              bg=COLORS['border'], sashwidth=3)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Code editor
        editor_frame = tk.Frame(paned, bg=COLORS['bg_dark'])
        paned.add(editor_frame, width=700)

        # Editor header
        editor_header = tk.Frame(editor_frame, bg=COLORS['bg_sidebar'], height=40)
        editor_header.pack(fill=tk.X)
        editor_header.pack_propagate(False)

        tk.Label(editor_header, text="📝 Code Editor",
                font=self.font_normal,
                bg=COLORS['bg_sidebar'],
                fg=COLORS['text_primary']).pack(side=tk.LEFT, padx=15, pady=8)

        # Language selector
        self.lang_var = tk.StringVar(value="Python")
        lang_menu = ttk.Combobox(editor_header, textvariable=self.lang_var,
                                values=["Python", "JavaScript", "Bash", "JSON"],
                                width=12, state='readonly')
        lang_menu.pack(side=tk.RIGHT, padx=10, pady=8)

        # Line numbers + code editor
        code_container = tk.Frame(editor_frame, bg=COLORS['bg_code'])
        code_container.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(code_container, width=4,
                                   font=self.font_code,
                                   bg=COLORS['bg_sidebar'],
                                   fg=COLORS['text_muted'],
                                   relief=tk.FLAT,
                                   state=tk.DISABLED)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.code_editor = scrolledtext.ScrolledText(code_container,
                                                     font=self.font_code,
                                                     bg=COLORS['bg_code'],
                                                     fg=COLORS['text_primary'],
                                                     insertbackground=COLORS['accent'],
                                                     selectbackground=COLORS['accent'],
                                                     relief=tk.FLAT,
                                                     wrap=tk.NONE)
        self.code_editor.pack(fill=tk.BOTH, expand=True)
        self.code_editor.bind('<KeyRelease>', self._update_line_numbers)
        self.code_editor.bind('<MouseWheel>', self._sync_scroll)

        # Default code
        self.code_editor.insert('1.0', '''# CatSDK Code Interpreter
# Write your Python code here and click "Run" to execute

def greet(name):
    """Greet the user"""
    return f"Hello, {name}! Welcome to CatSDK 1.X"

# Example usage
message = greet("Developer")
print(message)

# Try more complex operations
numbers = [1, 2, 3, 4, 5]
squared = [n**2 for n in numbers]
print(f"Squared numbers: {squared}")
''')
        self._update_line_numbers()

        # Button bar
        btn_bar = tk.Frame(editor_frame, bg=COLORS['bg_sidebar'], height=50)
        btn_bar.pack(fill=tk.X)

        run_btn = tk.Button(btn_bar, text="▶ Run Code",
                           font=self.font_normal,
                           bg=COLORS['accent_green'],
                           fg='white',
                           border=0,
                           cursor='hand2',
                           command=self.run_code)
        run_btn.pack(side=tk.LEFT, padx=15, pady=10)

        clear_btn = tk.Button(btn_bar, text="🗑 Clear",
                             font=self.font_normal,
                             bg=COLORS['bg_input'],
                             fg=COLORS['text_primary'],
                             border=0,
                             cursor='hand2',
                             command=lambda: self.code_editor.delete('1.0', tk.END))
        clear_btn.pack(side=tk.LEFT, padx=5, pady=10)

        save_btn = tk.Button(btn_bar, text="💾 Save",
                            font=self.font_normal,
                            bg=COLORS['bg_input'],
                            fg=COLORS['text_primary'],
                            border=0,
                            cursor='hand2',
                            command=self.save_code)
        save_btn.pack(side=tk.LEFT, padx=5, pady=10)

        load_btn = tk.Button(btn_bar, text="📂 Load",
                            font=self.font_normal,
                            bg=COLORS['bg_input'],
                            fg=COLORS['text_primary'],
                            border=0,
                            cursor='hand2',
                            command=self.load_code)
        load_btn.pack(side=tk.LEFT, padx=5, pady=10)

        # Output panel
        output_frame = tk.Frame(paned, bg=COLORS['bg_dark'])
        paned.add(output_frame, width=500)

        # Output header
        output_header = tk.Frame(output_frame, bg=COLORS['bg_sidebar'], height=40)
        output_header.pack(fill=tk.X)
        output_header.pack_propagate(False)

        tk.Label(output_header, text="📤 Output",
                font=self.font_normal,
                bg=COLORS['bg_sidebar'],
                fg=COLORS['text_primary']).pack(side=tk.LEFT, padx=15, pady=8)

        clear_output_btn = tk.Button(output_header, text="Clear",
                                    font=self.font_small,
                                    bg=COLORS['bg_input'],
                                    fg=COLORS['text_secondary'],
                                    border=0,
                                    command=lambda: self.code_output.delete('1.0', tk.END))
        clear_output_btn.pack(side=tk.RIGHT, padx=10, pady=8)

        self.code_output = scrolledtext.ScrolledText(output_frame,
                                                     font=self.font_code,
                                                     bg=COLORS['bg_code'],
                                                     fg=COLORS['text_primary'],
                                                     relief=tk.FLAT)
        self.code_output.pack(fill=tk.BOTH, expand=True)
        self.code_output.tag_configure('error', foreground=COLORS['accent_red'])
        self.code_output.tag_configure('success', foreground=COLORS['accent_green'])

    def _create_sandbox_tab(self):
        """Create the sandbox/REPL tab"""
        sandbox_frame = tk.Frame(self.notebook, bg=COLORS['bg_dark'])
        self.notebook.add(sandbox_frame, text="📦 Sandbox")

        # Header
        header = tk.Frame(sandbox_frame, bg=COLORS['bg_sidebar'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="🐍 Python Sandbox (Interactive REPL)",
                font=self.font_normal,
                bg=COLORS['bg_sidebar'],
                fg=COLORS['text_primary']).pack(side=tk.LEFT, padx=15, pady=12)

        reset_btn = tk.Button(header, text="🔄 Reset Environment",
                             font=self.font_small,
                             bg=COLORS['accent_orange'],
                             fg='white',
                             border=0,
                             cursor='hand2',
                             command=self.reset_sandbox)
        reset_btn.pack(side=tk.RIGHT, padx=15, pady=10)

        # REPL output
        self.sandbox_output = scrolledtext.ScrolledText(sandbox_frame,
                                                        font=self.font_code,
                                                        bg=COLORS['bg_code'],
                                                        fg=COLORS['text_primary'],
                                                        relief=tk.FLAT)
        self.sandbox_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.sandbox_output.tag_configure('prompt', foreground=COLORS['accent_green'])
        self.sandbox_output.tag_configure('output', foreground=COLORS['text_primary'])
        self.sandbox_output.tag_configure('error', foreground=COLORS['accent_red'])
        self.sandbox_output.tag_configure('result', foreground=COLORS['accent_purple'])

        self.sandbox_output.insert(tk.END, "Python Sandbox - CatSDK 1.X\n", 'output')
        self.sandbox_output.insert(tk.END, f"Python {sys.version}\n", 'output')
        self.sandbox_output.insert(tk.END, "Type commands below and press Enter to execute.\n\n", 'output')

        # Input area
        input_frame = tk.Frame(sandbox_frame, bg=COLORS['bg_input'], height=50)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        input_frame.pack_propagate(False)

        prompt_label = tk.Label(input_frame, text=">>>",
                               font=self.font_code,
                               bg=COLORS['bg_input'],
                               fg=COLORS['accent_green'])
        prompt_label.pack(side=tk.LEFT, padx=10)

        self.sandbox_input = tk.Entry(input_frame,
                                      font=self.font_code,
                                      bg=COLORS['bg_input'],
                                      fg=COLORS['text_primary'],
                                      insertbackground=COLORS['accent'],
                                      relief=tk.FLAT)
        self.sandbox_input.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=10)
        self.sandbox_input.bind('<Return>', self.execute_sandbox)
        self.sandbox_input.bind('<Up>', self._sandbox_history_up)
        self.sandbox_input.bind('<Down>', self._sandbox_history_down)

        self.sandbox_history = []
        self.sandbox_history_idx = 0

    def _create_compiler_tab(self):
        """Create the compiler tab"""
        compiler_frame = tk.Frame(self.notebook, bg=COLORS['bg_dark'])
        self.notebook.add(compiler_frame, text="🔧 Compiler")

        # Header
        header = tk.Frame(compiler_frame, bg=COLORS['bg_sidebar'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="🔧 Multi-Language Compiler",
                font=self.font_normal,
                bg=COLORS['bg_sidebar'],
                fg=COLORS['text_primary']).pack(side=tk.LEFT, padx=15, pady=12)

        # Language selector
        self.compiler_lang = tk.StringVar(value="python")
        lang_frame = tk.Frame(header, bg=COLORS['bg_sidebar'])
        lang_frame.pack(side=tk.RIGHT, padx=15)

        languages = [("Python", "python"), ("Bash", "bash"), ("JavaScript", "node")]
        for text, val in languages:
            rb = tk.Radiobutton(lang_frame, text=text, variable=self.compiler_lang,
                               value=val, bg=COLORS['bg_sidebar'],
                               fg=COLORS['text_primary'],
                               selectcolor=COLORS['bg_input'],
                               activebackground=COLORS['bg_sidebar'])
            rb.pack(side=tk.LEFT, padx=5)

        # Split view
        paned = tk.PanedWindow(compiler_frame, orient=tk.VERTICAL,
                              bg=COLORS['border'], sashwidth=3)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Code input
        code_frame = tk.Frame(paned, bg=COLORS['bg_code'])
        paned.add(code_frame, height=400)

        tk.Label(code_frame, text="Source Code:",
                font=self.font_small,
                bg=COLORS['bg_code'],
                fg=COLORS['text_muted']).pack(anchor=tk.W, padx=10, pady=5)

        self.compiler_input = scrolledtext.ScrolledText(code_frame,
                                                        font=self.font_code,
                                                        bg=COLORS['bg_code'],
                                                        fg=COLORS['text_primary'],
                                                        relief=tk.FLAT)
        self.compiler_input.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.compiler_input.insert('1.0', '# Enter your code here\nprint("Hello from CatSDK Compiler!")')

        # Button bar
        btn_frame = tk.Frame(code_frame, bg=COLORS['bg_code'])
        btn_frame.pack(fill=tk.X, padx=10, pady=5)

        compile_btn = tk.Button(btn_frame, text="⚡ Compile & Run",
                               font=self.font_normal,
                               bg=COLORS['accent_green'],
                               fg='white',
                               border=0,
                               cursor='hand2',
                               command=self.compile_code)
        compile_btn.pack(side=tk.LEFT, padx=5)

        check_btn = tk.Button(btn_frame, text="✓ Syntax Check",
                             font=self.font_normal,
                             bg=COLORS['accent'],
                             fg='white',
                             border=0,
                             cursor='hand2',
                             command=self.syntax_check)
        check_btn.pack(side=tk.LEFT, padx=5)

        # Output
        output_frame = tk.Frame(paned, bg=COLORS['bg_code'])
        paned.add(output_frame, height=200)

        tk.Label(output_frame, text="Compiler Output:",
                font=self.font_small,
                bg=COLORS['bg_code'],
                fg=COLORS['text_muted']).pack(anchor=tk.W, padx=10, pady=5)

        self.compiler_output = scrolledtext.ScrolledText(output_frame,
                                                         font=self.font_code,
                                                         bg='#0d1117',
                                                         fg=COLORS['text_primary'],
                                                         relief=tk.FLAT)
        self.compiler_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.compiler_output.tag_configure('error', foreground=COLORS['accent_red'])
        self.compiler_output.tag_configure('success', foreground=COLORS['accent_green'])
        self.compiler_output.tag_configure('warning', foreground=COLORS['accent_orange'])

    def _create_file_manager_tab(self):
        """Create the file manager tab"""
        fm_frame = tk.Frame(self.notebook, bg=COLORS['bg_dark'])
        self.notebook.add(fm_frame, text="📁 Files")

        # Header with path
        header = tk.Frame(fm_frame, bg=COLORS['bg_sidebar'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="📁 File Manager",
                font=self.font_normal,
                bg=COLORS['bg_sidebar'],
                fg=COLORS['text_primary']).pack(side=tk.LEFT, padx=15, pady=12)

        self.path_var = tk.StringVar(value=os.getcwd())
        path_entry = tk.Entry(header, textvariable=self.path_var,
                             font=self.font_small,
                             bg=COLORS['bg_input'],
                             fg=COLORS['text_primary'],
                             width=50)
        path_entry.pack(side=tk.LEFT, padx=10, pady=10)
        path_entry.bind('<Return>', lambda e: self.refresh_files())

        refresh_btn = tk.Button(header, text="🔄 Refresh",
                               font=self.font_small,
                               bg=COLORS['bg_input'],
                               fg=COLORS['text_primary'],
                               border=0,
                               command=self.refresh_files)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        # File list
        list_frame = tk.Frame(fm_frame, bg=COLORS['bg_code'])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Treeview for files
        columns = ('name', 'size', 'modified')
        self.file_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        self.file_tree.heading('name', text='Name')
        self.file_tree.heading('size', text='Size')
        self.file_tree.heading('modified', text='Modified')
        self.file_tree.column('name', width=400)
        self.file_tree.column('size', width=100)
        self.file_tree.column('modified', width=200)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.file_tree.yview)
        self.file_tree.configure(yscrollcommand=scrollbar.set)

        self.file_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_tree.bind('<Double-1>', self.open_file)

        # Action buttons
        action_frame = tk.Frame(fm_frame, bg=COLORS['bg_sidebar'], height=50)
        action_frame.pack(fill=tk.X)

        actions = [
            ("📂 Open", self.open_selected_file),
            ("📝 Edit", self.edit_file),
            ("🗑 Delete", self.delete_file),
            ("📁 New Folder", self.new_folder),
            ("📄 New File", self.new_file)
        ]

        for text, cmd in actions:
            btn = tk.Button(action_frame, text=text,
                           font=self.font_small,
                           bg=COLORS['bg_input'],
                           fg=COLORS['text_primary'],
                           border=0,
                           cursor='hand2',
                           command=cmd)
            btn.pack(side=tk.LEFT, padx=10, pady=10)

        # Load initial files
        self.refresh_files()

    def _bind_events(self):
        """Bind keyboard events"""
        self.chat_input.bind('<Return>', self._handle_chat_return)
        self.chat_input.bind('<Shift-Return>', lambda e: None)  # Allow newline
        self.root.bind('<Control-n>', lambda e: self.new_conversation())
        self.root.bind('<Control-r>', lambda e: self.run_code())

    def _handle_chat_return(self, event):
        """Handle Enter key in chat input"""
        if not event.state & 0x1:  # Shift not pressed
            self.send_message()
            return 'break'

    # ========================================================================
    # COMMAND SYSTEM
    # ========================================================================

    def _init_commands(self):
        """Initialize chatbot commands"""
        return {
            'help': self._cmd_help,
            'run': self._cmd_run,
            'calc': self._cmd_calc,
            'time': self._cmd_time,
            'date': self._cmd_date,
            'clear': self._cmd_clear,
            'list': self._cmd_list,
            'pwd': self._cmd_pwd,
            'echo': self._cmd_echo,
            'about': self._cmd_about,
            'system': self._cmd_system,
            'analyze': self._cmd_analyze,
            'explain': self._cmd_explain,
        }

    def _cmd_help(self, args):
        """Show help information"""
        return """🐱 CatSDK 1.X - Available Commands:

📌 GENERAL:
  /help       - Show this help message
  /about      - About CatSDK
  /clear      - Clear chat history
  /time       - Show current time
  /date       - Show current date

💻 CODE & SYSTEM:
  /run <code> - Execute Python code
  /calc <expr> - Calculate expression
  /system <cmd> - Run system command
  /pwd        - Show current directory
  /list       - List files in directory

🔍 ANALYSIS:
  /analyze <code> - Analyze code structure
  /explain <topic> - Explain a topic

💡 Tips:
- Use the Code Interpreter tab for longer scripts
- Use the Sandbox for interactive Python sessions
- Use the Compiler for multi-language support"""

    def _cmd_run(self, args):
        """Run Python code"""
        if not args:
            return "❌ Usage: /run <python code>"
        try:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                exec(args, self.sandbox_globals, self.sandbox_locals)
            result = output.getvalue()
            return f"✅ Output:\n```\n{result}```" if result else "✅ Code executed (no output)"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def _cmd_calc(self, args):
        """Calculate expression"""
        if not args:
            return "❌ Usage: /calc <expression>"
        try:
            # Safe evaluation
            allowed = {'abs', 'round', 'min', 'max', 'sum', 'pow', 'len'}
            result = eval(args, {"__builtins__": {n: getattr(__builtins__, n) if hasattr(__builtins__, n) else __builtins__[n] for n in allowed}})
            return f"🔢 Result: {result}"
        except Exception as e:
            return f"❌ Calculation error: {str(e)}"

    def _cmd_time(self, args):
        """Show current time"""
        return f"🕐 Current time: {datetime.now().strftime('%H:%M:%S')}"

    def _cmd_date(self, args):
        """Show current date"""
        return f"📅 Current date: {datetime.now().strftime('%Y-%m-%d %A')}"

    def _cmd_clear(self, args):
        """Clear chat"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete('1.0', tk.END)
        self.chat_display.config(state=tk.DISABLED)
        return "💬 Chat cleared!"

    def _cmd_list(self, args):
        """List directory contents"""
        path = args.strip() if args else '.'
        try:
            files = os.listdir(path)
            return f"📁 Contents of '{path}':\n" + "\n".join(f"  {'📁' if os.path.isdir(os.path.join(path, f)) else '📄'} {f}" for f in sorted(files)[:20])
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def _cmd_pwd(self, args):
        """Show current directory"""
        return f"📁 Current directory: {os.getcwd()}"

    def _cmd_echo(self, args):
        """Echo text"""
        return args if args else ""

    def _cmd_about(self, args):
        """About CatSDK"""
        return """🐱 CatSDK 1.X
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

An AutoGPT/ChatGPT-like interface built with Python & Tkinter.

Features:
✓ Interactive Chat Interface
✓ Code Interpreter & Editor
✓ Python Sandbox (REPL)
✓ Multi-language Compiler
✓ File Manager

No LLMs required - Pure Python power! 🐍"""

    def _cmd_system(self, args):
        """Run system command"""
        if not args:
            return "❌ Usage: /system <command>"
        try:
            result = subprocess.run(args, shell=True, capture_output=True, text=True, timeout=30)
            output = result.stdout if result.stdout else result.stderr
            return f"💻 Output:\n```\n{output[:2000]}```"
        except subprocess.TimeoutExpired:
            return "❌ Command timed out"
        except Exception as e:
            return f"❌ Error: {str(e)}"

    def _cmd_analyze(self, args):
        """Analyze code"""
        if not args:
            return "❌ Usage: /analyze <code>"

        analysis = []
        analysis.append("📊 Code Analysis:")
        analysis.append(f"  • Characters: {len(args)}")
        analysis.append(f"  • Lines: {args.count(chr(10)) + 1}")
        analysis.append(f"  • Words: {len(args.split())}")

        # Find functions
        funcs = re.findall(r'def\s+(\w+)', args)
        if funcs:
            analysis.append(f"  • Functions: {', '.join(funcs)}")

        # Find classes
        classes = re.findall(r'class\s+(\w+)', args)
        if classes:
            analysis.append(f"  • Classes: {', '.join(classes)}")

        # Find imports
        imports = re.findall(r'import\s+(\w+)|from\s+(\w+)', args)
        if imports:
            mods = [i[0] or i[1] for i in imports]
            analysis.append(f"  • Imports: {', '.join(mods)}")

        return "\n".join(analysis)

    def _cmd_explain(self, args):
        """Explain topics"""
        topics = {
            'python': "🐍 Python is a high-level, interpreted programming language known for its readability and versatility.",
            'function': "📦 A function is a reusable block of code that performs a specific task. Defined with 'def' keyword.",
            'class': "🏗️ A class is a blueprint for creating objects, bundling data and functionality together.",
            'loop': "🔄 Loops repeat code: 'for' iterates over sequences, 'while' repeats while condition is true.",
            'variable': "📝 Variables store data values. In Python, they're created when you assign a value.",
            'list': "📋 Lists are ordered, mutable collections. Created with [] and can hold any data types.",
            'dict': "🗂️ Dictionaries store key-value pairs. Created with {} and allow fast lookups by key.",
        }

        if not args:
            return "❌ Usage: /explain <topic>\nAvailable: " + ", ".join(topics.keys())

        topic = args.lower().strip()
        return topics.get(topic, f"❓ Unknown topic: {topic}. Try: " + ", ".join(topics.keys()))

    # ========================================================================
    # CHAT FUNCTIONS
    # ========================================================================

    def send_message(self):
        """Send a message in the chat"""
        message = self.chat_input.get('1.0', tk.END).strip()
        if not message:
            return

        self.chat_input.delete('1.0', tk.END)

        # Display user message
        self._append_chat(f"\n👤 You:\n{message}\n", 'user')

        # Process and respond
        response = self._process_message(message)
        self._append_chat(f"\n🐱 CatSDK:\n{response}\n", 'bot')

        # Save to conversation
        if self.current_conversation in self.conversations:
            self.conversations[self.current_conversation].append({
                'user': message,
                'bot': response,
                'time': datetime.now().isoformat()
            })

    def _process_message(self, message):
        """Process user message and generate response"""
        # Check for commands
        if message.startswith('/'):
            parts = message[1:].split(maxsplit=1)
            cmd = parts[0].lower()
            args = parts[1] if len(parts) > 1 else ""

            if cmd in self.commands:
                return self.commands[cmd](args)
            else:
                return f"❓ Unknown command: /{cmd}. Type /help for available commands."

        # Smart responses based on keywords
        msg_lower = message.lower()

        if any(w in msg_lower for w in ['hello', 'hi', 'hey', 'greetings']):
            return "👋 Hello! I'm CatSDK, your Python-powered assistant. How can I help you today?\n\nTry:\n• /help - See available commands\n• /run <code> - Execute Python code\n• Use the tabs above for Code Interpreter, Sandbox, and more!"

        elif any(w in msg_lower for w in ['how are you', 'how do you do']):
            return "😊 I'm running great! All systems operational. Ready to help you with code, calculations, and more!"

        elif 'thank' in msg_lower:
            return "🎉 You're welcome! Happy to help. Let me know if you need anything else!"

        elif any(w in msg_lower for w in ['bye', 'goodbye', 'exit', 'quit']):
            return "👋 Goodbye! Thanks for using CatSDK. See you next time!"

        elif 'code' in msg_lower or 'python' in msg_lower:
            return "💻 I can help with Python code! Try:\n• /run <code> - Run code directly\n• /analyze <code> - Analyze code structure\n• Or use the Code Interpreter tab for a full editor experience!"

        elif any(w in msg_lower for w in ['calculate', 'math', 'compute']):
            return "🔢 For calculations, use:\n• /calc <expression> - e.g., /calc 2**10\n• /run import math; print(math.sqrt(144))"

        elif 'file' in msg_lower:
            return "📁 For file operations:\n• /list - List files in current directory\n• /pwd - Show current directory\n• Or use the Files tab for a full file manager!"

        elif 'what can you do' in msg_lower or 'capabilities' in msg_lower:
            return self._cmd_about("")

        else:
            # Default response with suggestions
            return f"""I received your message: "{message[:50]}{'...' if len(message) > 50 else ''}"

🐱 I'm CatSDK - a Python-powered assistant (no LLM needed!)

I can help you with:
• 💻 Running Python code: /run print("Hello!")
• 🔢 Calculations: /calc 2+2*10
• 📁 File operations: /list, /pwd
• 🕐 Date/Time: /time, /date
• 💡 Explanations: /explain python

Type /help for all commands, or use the tabs above for:
• Code Interpreter - Full code editor
• Sandbox - Interactive Python REPL
• Compiler - Multi-language support
• Files - File management"""

    def _append_chat(self, text, tag=None):
        """Append text to chat display"""
        self.chat_display.config(state=tk.NORMAL)
        if tag:
            self.chat_display.insert(tk.END, text, tag)
        else:
            self.chat_display.insert(tk.END, text)
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)

    def new_conversation(self):
        """Create a new conversation"""
        self.conversation_counter += 1
        conv_id = f"Chat {self.conversation_counter}"
        self.conversations[conv_id] = []
        self.current_conversation = conv_id

        # Clear chat display
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete('1.0', tk.END)
        self.chat_display.config(state=tk.DISABLED)

        # Welcome message
        welcome = """🐱 Welcome to CatSDK 1.X!

I'm your Python-powered assistant - no LLM required!

Quick Start:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• Type /help to see all available commands
• Use /run <code> to execute Python code
• Use /calc <expr> for quick calculations
• Explore the tabs above for more features!

What would you like to do today?
"""
        self._append_chat(welcome, 'system')

        # Update sidebar
        self._update_conversation_list()

    def _update_conversation_list(self):
        """Update the conversation list in sidebar"""
        # Clear existing
        for widget in self.conv_frame.winfo_children():
            widget.destroy()

        # Add conversations
        for conv_id in reversed(list(self.conversations.keys())):
            btn = tk.Button(self.conv_frame, text=f"💬 {conv_id}",
                           font=self.font_small,
                           bg=COLORS['accent'] if conv_id == self.current_conversation else COLORS['bg_sidebar'],
                           fg='white' if conv_id == self.current_conversation else COLORS['text_secondary'],
                           anchor='w',
                           border=0,
                           cursor='hand2',
                           command=lambda c=conv_id: self.switch_conversation(c))
            btn.pack(fill=tk.X, pady=2)

    def switch_conversation(self, conv_id):
        """Switch to a different conversation"""
        self.current_conversation = conv_id

        # Clear and reload chat
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete('1.0', tk.END)

        for msg in self.conversations.get(conv_id, []):
            self._append_chat(f"\n👤 You:\n{msg['user']}\n", 'user')
            self._append_chat(f"\n🐱 CatSDK:\n{msg['bot']}\n", 'bot')

        self.chat_display.config(state=tk.DISABLED)
        self._update_conversation_list()

    # ========================================================================
    # CODE INTERPRETER FUNCTIONS
    # ========================================================================

    def run_code(self):
        """Run code in the code interpreter"""
        code = self.code_editor.get('1.0', tk.END)
        lang = self.lang_var.get()

        self.code_output.delete('1.0', tk.END)
        self.code_output.insert(tk.END, f"⏳ Running {lang} code...\n\n")
        self.root.update()

        def execute():
            try:
                if lang == "Python":
                    # Capture output
                    output = io.StringIO()
                    error_output = io.StringIO()

                    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(error_output):
                        exec(code, {'__builtins__': __builtins__})

                    result = output.getvalue()
                    errors = error_output.getvalue()

                    self.root.after(0, lambda: self._show_code_result(result, errors))

                elif lang == "JavaScript":
                    result = subprocess.run(['node', '-e', code], capture_output=True, text=True, timeout=30)
                    self.root.after(0, lambda: self._show_code_result(result.stdout, result.stderr))

                elif lang == "Bash":
                    result = subprocess.run(code, shell=True, capture_output=True, text=True, timeout=30)
                    self.root.after(0, lambda: self._show_code_result(result.stdout, result.stderr))

                elif lang == "JSON":
                    # Validate JSON
                    parsed = json.loads(code)
                    formatted = json.dumps(parsed, indent=2)
                    self.root.after(0, lambda: self._show_code_result(f"✅ Valid JSON:\n{formatted}", ""))

            except Exception as e:
                self.root.after(0, lambda: self._show_code_result("", f"❌ Error: {str(e)}\n\n{traceback.format_exc()}"))

        threading.Thread(target=execute, daemon=True).start()

    def _show_code_result(self, output, errors):
        """Display code execution results"""
        self.code_output.delete('1.0', tk.END)

        if output:
            self.code_output.insert(tk.END, "✅ Output:\n", 'success')
            self.code_output.insert(tk.END, output + "\n")

        if errors:
            self.code_output.insert(tk.END, "\n❌ Errors:\n", 'error')
            self.code_output.insert(tk.END, errors, 'error')

        if not output and not errors:
            self.code_output.insert(tk.END, "✅ Code executed successfully (no output)\n", 'success')

    def _update_line_numbers(self, event=None):
        """Update line numbers in code editor"""
        lines = self.code_editor.get('1.0', tk.END).count('\n')
        line_nums = '\n'.join(str(i) for i in range(1, lines + 1))
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_nums)
        self.line_numbers.config(state=tk.DISABLED)

    def _sync_scroll(self, event):
        """Sync scroll between line numbers and code"""
        self.line_numbers.yview_moveto(self.code_editor.yview()[0])

    def save_code(self):
        """Save code to file"""
        code = self.code_editor.get('1.0', tk.END)
        filepath = filedialog.asksaveasfilename(
            defaultextension=".py",
            filetypes=[("Python", "*.py"), ("JavaScript", "*.js"), ("All", "*.*")]
        )
        if filepath:
            with open(filepath, 'w') as f:
                f.write(code)
            messagebox.showinfo("Saved", f"Code saved to {filepath}")

    def load_code(self):
        """Load code from file"""
        filepath = filedialog.askopenfilename(
            filetypes=[("Python", "*.py"), ("JavaScript", "*.js"), ("All", "*.*")]
        )
        if filepath:
            with open(filepath, 'r') as f:
                code = f.read()
            self.code_editor.delete('1.0', tk.END)
            self.code_editor.insert('1.0', code)
            self._update_line_numbers()

    # ========================================================================
    # SANDBOX FUNCTIONS
    # ========================================================================

    def execute_sandbox(self, event=None):
        """Execute command in sandbox"""
        cmd = self.sandbox_input.get().strip()
        if not cmd:
            return

        self.sandbox_history.append(cmd)
        self.sandbox_history_idx = len(self.sandbox_history)

        self.sandbox_output.insert(tk.END, f">>> {cmd}\n", 'prompt')
        self.sandbox_input.delete(0, tk.END)

        try:
            # Try eval first for expressions
            try:
                result = eval(cmd, self.sandbox_globals, self.sandbox_locals)
                if result is not None:
                    self.sandbox_output.insert(tk.END, f"{repr(result)}\n", 'result')
            except SyntaxError:
                # Fall back to exec for statements
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    exec(cmd, self.sandbox_globals, self.sandbox_locals)
                result = output.getvalue()
                if result:
                    self.sandbox_output.insert(tk.END, result, 'output')

        except Exception as e:
            self.sandbox_output.insert(tk.END, f"{type(e).__name__}: {e}\n", 'error')

        self.sandbox_output.see(tk.END)

    def _sandbox_history_up(self, event):
        """Navigate command history up"""
        if self.sandbox_history and self.sandbox_history_idx > 0:
            self.sandbox_history_idx -= 1
            self.sandbox_input.delete(0, tk.END)
            self.sandbox_input.insert(0, self.sandbox_history[self.sandbox_history_idx])

    def _sandbox_history_down(self, event):
        """Navigate command history down"""
        if self.sandbox_history_idx < len(self.sandbox_history) - 1:
            self.sandbox_history_idx += 1
            self.sandbox_input.delete(0, tk.END)
            self.sandbox_input.insert(0, self.sandbox_history[self.sandbox_history_idx])
        else:
            self.sandbox_history_idx = len(self.sandbox_history)
            self.sandbox_input.delete(0, tk.END)

    def reset_sandbox(self):
        """Reset sandbox environment"""
        self.sandbox_globals = {'__builtins__': __builtins__}
        self.sandbox_locals = {}
        self.sandbox_output.delete('1.0', tk.END)
        self.sandbox_output.insert(tk.END, "🔄 Sandbox environment reset!\n\n", 'success')
        self.sandbox_history.clear()
        self.sandbox_history_idx = 0

    # ========================================================================
    # COMPILER FUNCTIONS
    # ========================================================================

    def compile_code(self):
        """Compile and run code"""
        code = self.compiler_input.get('1.0', tk.END)
        lang = self.compiler_lang.get()

        self.compiler_output.delete('1.0', tk.END)
        self.compiler_output.insert(tk.END, f"⚡ Compiling {lang}...\n\n")
        self.root.update()

        def run():
            try:
                if lang == "python":
                    # Compile check
                    compile(code, '<string>', 'exec')
                    self.root.after(0, lambda: self.compiler_output.insert(tk.END, "✅ Compilation successful!\n\n", 'success'))

                    # Run
                    output = io.StringIO()
                    with contextlib.redirect_stdout(output):
                        exec(code)
                    result = output.getvalue()
                    self.root.after(0, lambda: self.compiler_output.insert(tk.END, f"Output:\n{result}"))

                elif lang == "bash":
                    result = subprocess.run(code, shell=True, capture_output=True, text=True, timeout=30)
                    self.root.after(0, lambda: self._show_compiler_result(result))

                elif lang == "node":
                    result = subprocess.run(['node', '-e', code], capture_output=True, text=True, timeout=30)
                    self.root.after(0, lambda: self._show_compiler_result(result))

            except SyntaxError as e:
                self.root.after(0, lambda: self.compiler_output.insert(tk.END, f"❌ Syntax Error at line {e.lineno}:\n{e.msg}\n", 'error'))
            except Exception as e:
                self.root.after(0, lambda: self.compiler_output.insert(tk.END, f"❌ Error: {str(e)}\n", 'error'))

        threading.Thread(target=run, daemon=True).start()

    def _show_compiler_result(self, result):
        """Show compiler subprocess result"""
        if result.returncode == 0:
            self.compiler_output.insert(tk.END, "✅ Execution successful!\n\n", 'success')
            self.compiler_output.insert(tk.END, result.stdout)
        else:
            self.compiler_output.insert(tk.END, "❌ Execution failed!\n\n", 'error')
            self.compiler_output.insert(tk.END, result.stderr, 'error')

    def syntax_check(self):
        """Check syntax only"""
        code = self.compiler_input.get('1.0', tk.END)
        lang = self.compiler_lang.get()

        self.compiler_output.delete('1.0', tk.END)

        try:
            if lang == "python":
                compile(code, '<string>', 'exec')
                self.compiler_output.insert(tk.END, "✅ Syntax is valid!\n", 'success')
            elif lang == "node":
                result = subprocess.run(['node', '--check', '-e', code], capture_output=True, text=True)
                if result.returncode == 0:
                    self.compiler_output.insert(tk.END, "✅ JavaScript syntax is valid!\n", 'success')
                else:
                    self.compiler_output.insert(tk.END, f"❌ Syntax errors:\n{result.stderr}", 'error')
            else:
                self.compiler_output.insert(tk.END, "ℹ️ Syntax check not available for Bash\n", 'warning')

        except SyntaxError as e:
            self.compiler_output.insert(tk.END, f"❌ Syntax Error at line {e.lineno}:\n{e.msg}\n", 'error')

    # ========================================================================
    # FILE MANAGER FUNCTIONS
    # ========================================================================

    def refresh_files(self):
        """Refresh file list"""
        path = self.path_var.get()

        # Clear existing
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)

        try:
            # Add parent directory
            if path != '/':
                self.file_tree.insert('', 'end', values=('📁 ..', '', ''))

            # List files
            for item in sorted(os.listdir(path)):
                full_path = os.path.join(path, item)
                try:
                    stat = os.stat(full_path)
                    size = self._format_size(stat.st_size)
                    modified = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')

                    if os.path.isdir(full_path):
                        self.file_tree.insert('', 'end', values=(f'📁 {item}', '<DIR>', modified))
                    else:
                        self.file_tree.insert('', 'end', values=(f'📄 {item}', size, modified))
                except:
                    pass

        except Exception as e:
            messagebox.showerror("Error", f"Cannot access path: {e}")

    def _format_size(self, size):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def open_file(self, event):
        """Handle double-click on file"""
        selection = self.file_tree.selection()
        if selection:
            item = self.file_tree.item(selection[0])
            name = item['values'][0]

            # Remove icon prefix
            name = name[2:].strip()

            if name == '..':
                # Go up
                self.path_var.set(os.path.dirname(self.path_var.get()))
                self.refresh_files()
            elif item['values'][1] == '<DIR>':
                # Enter directory
                self.path_var.set(os.path.join(self.path_var.get(), name))
                self.refresh_files()
            else:
                # Open file in code editor
                filepath = os.path.join(self.path_var.get(), name)
                try:
                    with open(filepath, 'r') as f:
                        content = f.read()
                    self.code_editor.delete('1.0', tk.END)
                    self.code_editor.insert('1.0', content)
                    self._update_line_numbers()
                    self.notebook.select(1)  # Switch to code interpreter
                except:
                    messagebox.showerror("Error", "Cannot open file")

    def open_selected_file(self):
        """Open selected file"""
        self.open_file(None)

    def edit_file(self):
        """Edit selected file"""
        self.open_file(None)

    def delete_file(self):
        """Delete selected file"""
        selection = self.file_tree.selection()
        if selection:
            item = self.file_tree.item(selection[0])
            name = item['values'][0][2:].strip()

            if messagebox.askyesno("Confirm", f"Delete '{name}'?"):
                filepath = os.path.join(self.path_var.get(), name)
                try:
                    if os.path.isdir(filepath):
                        os.rmdir(filepath)
                    else:
                        os.remove(filepath)
                    self.refresh_files()
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot delete: {e}")

    def new_folder(self):
        """Create new folder"""
        name = tk.simpledialog.askstring("New Folder", "Folder name:")
        if name:
            try:
                os.makedirs(os.path.join(self.path_var.get(), name))
                self.refresh_files()
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create folder: {e}")

    def new_file(self):
        """Create new file"""
        name = tk.simpledialog.askstring("New File", "File name:")
        if name:
            try:
                filepath = os.path.join(self.path_var.get(), name)
                with open(filepath, 'w') as f:
                    f.write('')
                self.refresh_files()
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create file: {e}")

    # ========================================================================
    # UTILITY FUNCTIONS
    # ========================================================================

    def upload_file(self):
        """Upload/import a file"""
        filepath = filedialog.askopenfilename()
        if filepath:
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                self._append_chat(f"\n📁 Uploaded: {os.path.basename(filepath)}\n", 'system')
                self._append_chat(f"```\n{content[:500]}{'...' if len(content) > 500 else ''}\n```\n")
            except Exception as e:
                self._append_chat(f"\n❌ Error uploading file: {e}\n", 'error')

    def show_help(self):
        """Show help dialog"""
        help_text = """🐱 CatSDK 1.X - Help Guide

CHAT TAB:
• Type messages to interact with CatSDK
• Use /commands for special actions
• Type /help to see all commands

CODE INTERPRETER:
• Write and run Python code
• Supports Python, JavaScript, Bash, JSON
• Use Ctrl+R to run code

SANDBOX:
• Interactive Python REPL
• Variables persist between commands
• Use Up/Down arrows for history

COMPILER:
• Multi-language compilation
• Syntax checking
• Error highlighting

FILES:
• Browse and manage files
• Double-click to open
• Edit files in code interpreter

KEYBOARD SHORTCUTS:
• Ctrl+N: New conversation
• Ctrl+R: Run code
• Enter: Send message
• Shift+Enter: New line in message
"""
        messagebox.showinfo("CatSDK Help", help_text)


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    root = tk.Tk()

    # Center window
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - 1400) // 2
    y = (screen_height - 900) // 2
    root.geometry(f"1400x900+{x}+{y}")

    # Import simpledialog for new file/folder
    import tkinter.simpledialog

    app = CatSDKApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
