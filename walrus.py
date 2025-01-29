import curses
import subprocess
from typing import Dict, List, Tuple, Optional

# Command structure: {command: (description, required_args, optional_args, command_specific_options)}
COMMANDS = {
    "json": (
        "Run the client by specifying arguments in JSON string",
        ["JSON_STRING"],
        [],
        {}
    ),
    "store": (
        "Store a new blob into Walrus", 
        ["FILE_PATH"],
        [],
        {
            "--epochs": "Number of epochs to store the blob (required)",
            "--deletable": "Make the blob deletable before expiry",
            "--share": "Create as shared blob",
            "--force": "Force store even if already exists",
            "--amount": "Amount to fund if creating as shared blob"
        }
    ),
    "read": (
        "Read a blob from Walrus",
        ["BLOB_ID"],
        [],
        {
            "--out": "Output file name (default: stdout)",
            "--rpc-url": "Specify custom Sui RPC node URL"
        }
    ),
    "blob-status": (
        "Get the status of a blob",
        [],
        [],
        {
            "--blob-id": "Check status by blob ID",
            "--file": "Check status by file path"
        }
    ),
    "info": (
        "Print information about the Walrus storage system",
        [],
        [],
        {
            "--all": "Show all information including dev details"
        }
    ),
    "list-blobs": (
        "List all registered blobs for the current wallet",
        [],
        [],
        {
            "--include-expired": "Include expired blob objects in listing"
        }
    ),
    "delete": (
        "Delete a blob from Walrus",
        [],
        [],
        {
            "--blob-id": "Delete blob by ID",
            "--file": "Delete blob by deriving ID from file",
            "--object-id": "Delete blob by Sui object ID",
            "--yes": "Skip deletion confirmation",
            "--no-status-check": "Skip post-deletion status check"
        }
    ),
    "share": (
        "Share a blob",
        [],
        [],
        {
            "--blob-obj-id": "Blob object ID to share",
            "--amount": "Amount to fund the shared blob"
        }
    ),
    "fund-shared-blob": (
        "Fund a shared blob",
        ["BLOB_ID"],
        [],
        {
            "--amount": "Amount to fund the shared blob"
        }
    ),
    "extend": ("Extend a shared blob", ["BLOB_ID"], [], {}),
    "stake": ("Stake with storage node", ["NODE_ADDRESS"], [], {}),
    "generate-sui-wallet": ("Generates a new Sui wallet", [], [], {}),
    "get-wal": ("Exchange SUI for WAL", ["AMOUNT"], [], {}),
    "burn-blobs": ("Burns owned Blob objects on Sui", ["BLOB_IDS"], [], {}),
    "publisher": ("Run a publisher service", ["NETWORK_ADDRESS"], [], {}),
    "aggregator": ("Run an aggregator service", ["NETWORK_ADDRESS"], [], {}),
    "daemon": ("Run a client daemon", ["NETWORK_ADDRESS"], [], {}),
    "exit": ("Exit the program", [], [], {})
}

# Global options (optional)
GLOBAL_OPTIONS = {
    "--config": "Path to the Walrus configuration file",
    "--wallet": "Path to the Sui wallet configuration file",
    "--gas-budget": "Set the gas budget for transactions (default: 100000000)",
    "--json": "Write output as JSON format",
}

def menu(stdscr) -> str:
    """Curses-based terminal menu for selecting Walrus CLI commands"""
    curses.curs_set(0)  # Hide cursor
    curses.start_color()
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    
    selected = 0
    commands_list = list(COMMANDS.keys())
    
    while True:
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Calculate the maximum items that can be displayed
        max_display = height - 4  # We need to leave room for the header
        start_idx = max(0, selected - max_display + 1)
        
        # Header
        header = "Walrus CLI Menu"
        stdscr.addstr(0, 0, header.center(width), curses.color_pair(1) | curses.A_BOLD)
        stdscr.addstr(1, 0, "Use ↑/↓ or j/k to navigate, Enter to select, q to quit", curses.color_pair(2))
        
        # Commands
        for i, cmd in enumerate(commands_list[start_idx:start_idx + max_display], start=start_idx):
            y = i - start_idx + 2
            desc = COMMANDS[cmd][0]
            if i == selected:
                stdscr.attron(curses.A_REVERSE)
                stdscr.addstr(y, 2, f"> {cmd}: {desc}"[:width-3])
                stdscr.attroff(curses.A_REVERSE)
            else:
                stdscr.addstr(y, 2, f"  {cmd}: {desc}"[:width-3])
        
        stdscr.refresh()
        key = stdscr.getch()
        
        if key in [curses.KEY_UP, ord('k')]:
            selected = (selected - 1) % len(commands_list)
        elif key in [curses.KEY_DOWN, ord('j')]:
            selected = (selected + 1) % len(commands_list)
        elif key in [curses.KEY_ENTER, 10, 13]:
            return commands_list[selected]
        elif key in [ord('q')]:
            return "exit"

def get_user_input(prompt: str, required: bool = True) -> str:
    """Prompt user for input and enforce required fields"""
    while True:
        value = input(f"{prompt}: ").strip()
        if value or not required:
            return value
        print("This input is required. Please try again.")

def get_yes_no_input(prompt: str) -> bool:
    """Get yes/no input from user"""
    while True:
        response = input(f"{prompt} (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        if response in ['', 'n', 'no']:
            return False
        print("Please answer 'y' or 'n'")

def handle_delete_command() -> List[str]:
    """Special handler for delete command with mutually exclusive options"""
    print("\nDelete blob - Choose one of the following options:")
    print("1. Delete by blob ID")
    print("2. Delete by file path")
    print("3. Delete by object ID")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        args = []
        
        if choice == "1":
            blob_id = get_user_input("Enter blob ID")
            args.extend(["--blob-id", blob_id])
        elif choice == "2":
            file_path = get_user_input("Enter file path")
            args.extend(["--file", file_path])
        elif choice == "3":
            object_id = get_user_input("Enter object ID")
            args.extend(["--object-id", object_id])
        else:
            print("Invalid choice. Please try again.")
            continue
            
        if get_yes_no_input("Skip confirmation prompt?"):
            args.append("--yes")
            
        if get_yes_no_input("Skip status check after deletion?"):
            args.append("--no-status-check")
            
        return args

def handle_blob_status_command() -> List[str]:
    """Special handler for blob-status command with mutually exclusive options"""
    print("\nCheck blob status - Choose one of the following options:")
    print("1. Check by blob ID")
    print("2. Check by file path")
    
    while True:
        choice = input("\nEnter your choice (1-2): ").strip()
        if choice == "1":
            blob_id = get_user_input("Enter blob ID")
            return ["--blob-id", blob_id]
        elif choice == "2":
            file_path = get_user_input("Enter file path")
            return ["--file", file_path]
        else:
            print("Invalid choice. Please try again.")

def get_command_options(command: str) -> List[str]:
    """Get command-specific options based on the command"""
    options = []
    command_options = COMMANDS[command][3]
    
    if not command_options:
        return options
        
    print(f"\nAvailable options for '{command}':")
    for option, description in command_options.items():
        print(f"  {option}: {description}")
        
    while True:
        option = input("\nEnter an option (press Enter when done): ").strip()
        if not option:
            break
            
        if option in command_options:
            options.append(option)
            if option not in ["--deletable", "--force", "--yes", "--no-status-check", "--include-expired"]:
                value = get_user_input(f"Enter value for {option}")
                options.append(value)
        else:
            print(f"Invalid option: {option}")
            
    return options

def handle_store_command() -> List[str]:
    """Special handler for store command"""
    args = []
    
    file_path = get_user_input("Enter file path")
    args.append(file_path)
    
    epochs = get_user_input("Enter number of epochs (or 'max' for maximum)")
    args.extend(["--epochs", epochs])
    
    if get_yes_no_input("Make blob deletable?"):
        args.append("--deletable")
    
    if get_yes_no_input("Create as shared blob?"):
        args.append("--share")
        amount = get_user_input("Enter amount to fund (optional)", required=False)
        if amount:
            args.extend(["--amount", amount])
    
    if get_yes_no_input("Force store even if already exists?"):
        args.append("--force")
    
    return args

def handle_read_command() -> List[str]:
    """Special handler for read command"""
    args = []
    
    blob_id = get_user_input("Enter blob ID")
    args.append(blob_id)
    
    if get_yes_no_input("Specify output file?"):
        out_file = get_user_input("Enter output file path")
        args.extend(["--out", out_file])
    
    if get_yes_no_input("Use custom RPC URL?"):
        rpc_url = get_user_input("Enter RPC URL")
        args.extend(["--rpc-url", rpc_url])
    
    return args

def handle_list_blobs_command() -> List[str]:
    """Special handler for list-blobs command"""
    args = []
    
    if get_yes_no_input("Include expired blobs?"):
        args.append("--include-expired")
    
    return args

def get_command_args(command: str) -> List[str]:
    """Get command-specific arguments based on command type"""
    if command == "delete":
        return handle_delete_command()
    elif command == "store":
        return handle_store_command()
    elif command == "read":
        return handle_read_command()
    elif command == "list-blobs":
        return handle_list_blobs_command()
    elif command == "blob-status":
        return handle_blob_status_command()
    else:
        args = []
        for arg in COMMANDS[command][1]:
            value = get_user_input(f"Enter {arg}", required=True)
            args.append(value)
        args.extend(get_command_options(command))
        return args

def get_global_options() -> List[str]:
    """Ask user for optional global flags"""
    args = []
    for flag, desc in GLOBAL_OPTIONS.items():
        if get_yes_no_input(f"Do you want to set {flag}?"):
            if flag == "--json":  # JSON flag has no argument
                args.append(flag)
            else:
                value = get_user_input(desc, required=True)
                args.extend([flag, value])
    return args

def main():
    """Main function for the interactive Walrus CLI wrapper"""
    try:
        selected_command = curses.wrapper(menu)

        if selected_command == "exit":
            print("Goodbye!")
            return

        # Get command-specific arguments and options
        command_args = get_command_args(selected_command)
        
        # Get optional global flags
        global_options = get_global_options()

        # Build the command
        full_command = ["walrus", selected_command] + command_args + global_options
        print(f"\nExecuting: {' '.join(full_command)}\n")

        # Run the command
        subprocess.run(full_command)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")

if __name__ == "__main__":
    main()
