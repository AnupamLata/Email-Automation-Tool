import csv
import re
import threading
import time
from datetime import datetime
from email_sender import send_email, validate_email
from logger import log_email_send, get_log_summary, view_logs, clear_logs
from email_reader import EmailReader
from auto_reply_engine import AutoReplyEngine

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import track
    from rich.prompt import Prompt, Confirm
    from rich.syntax import Syntax
except ImportError:
    class Console:
        def print(self, *args, **kwargs):
            print(*args)

    class Panel:
        def __init__(self, renderable, title=None, border_style=None):
            self.renderable = renderable
            self.title = title

        def __str__(self):
            if self.title:
                return f"{self.title}\n{self.renderable}"
            return str(self.renderable)

    class Table:
        def __init__(self, title=None, border_style=None):
            self.title = title
            self.columns = []
            self.rows = []

        @classmethod
        def grid(cls, padding=0):
            return cls()

        def add_column(self, header, **kwargs):
            self.columns.append(header)

        def add_row(self, *values):
            self.rows.append(values)

        def __str__(self):
            lines = []
            if self.title:
                lines.append(self.title)
            if self.columns:
                lines.append(" | ".join(self.columns))
                lines.append("-" * max(3, len(lines[-1])))
            for row in self.rows:
                lines.append(" | ".join(str(value) for value in row))
            return "\n".join(lines)

    def track(iterable, description=""):
        if description:
            print(description, end="", flush=True)
        for item in iterable:
            yield item
        if description:
            print()

    class Prompt:
        @staticmethod
        def ask(prompt_text, choices=None):
            while True:
                value = input(f"{prompt_text}: ").strip()
                if not choices or value in choices:
                    return value
                print(f"Please choose one of: {', '.join(choices)}")

    class Confirm:
        @staticmethod
        def ask(prompt_text):
            while True:
                value = input(f"{prompt_text} [y/n]: ").strip().lower()
                if value in {"y", "yes"}:
                    return True
                if value in {"n", "no"}:
                    return False

    class Syntax:
        def __init__(self, *args, **kwargs):
            pass

console = Console()

def display_banner():
    """Display colorful banner
    
    Shows ASCII art banner with app name and tagline.
    Uses rich library for cyan color styling.
    """
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║        📧  EMAIL AUTOMATION TOOL  📧                   ║
    ║                                                          ║
    ║         Powerful & Professional Email Manager            ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")

def display_menu():
    """Display main menu
    
    Shows 8 menu options with colors:
    1. Send Single Email
    2. Send Bulk Email
    3. View Email Logs
    4. Clear Logs
    5. Manage Auto-Replies
    6. Check Auto-Reply Status
    7. Monitor Incoming Emails
    8. Exit
    
    Uses rich Table.grid for formatting.
    """
    menu = Table.grid(padding=1)
    menu.add_row("[bold green]1.[/bold green] Send Single Email")
    menu.add_row("[bold green]2.[/bold green] Send Bulk Email")
    menu.add_row("[bold green]3.[/bold green] View Email Logs")
    menu.add_row("[bold green]4.[/bold green] Clear Logs")
    menu.add_row("[bold cyan]5.[/bold cyan] Manage Auto-Replies")
    menu.add_row("[bold cyan]6.[/bold cyan] Check Auto-Reply Status")
    menu.add_row("[bold magenta]7.[/bold magenta] Monitor Incoming Emails")
    menu.add_row("[bold red]8.[/bold red] Exit")
    
    console.print(Panel(menu, title="[bold]Main Menu[/bold]", border_style="blue"))

def send_single_email():
    console.print("\n[bold yellow]📬 Single Email Mode[/bold yellow]\n")
    
    while True:
        receiver = Prompt.ask("Enter receiver email").strip()
        if not validate_email(receiver):
            console.print("[red]❌ Invalid email format. Please try again.[/red]")
            continue
        break
    
    subject = Prompt.ask("Enter subject").strip()
    if not subject:
        console.print("[red]❌ Subject cannot be empty[/red]")
        return
    
    message = Prompt.ask("Enter message").strip()
    if not message:
        console.print("[red]❌ Message cannot be empty[/red]")
        return
    
    summary_table = Table(title="Email Summary", border_style="cyan")
    summary_table.add_column("Field", style="blue")
    summary_table.add_column("Value", style="green")
    summary_table.add_row("To", receiver)
    summary_table.add_row("Subject", subject[:50] + "..." if len(subject) > 50 else subject)
    summary_table.add_row("Message", message[:50] + "..." if len(message) > 50 else message)
    
    console.print(summary_table)
    
    if Confirm.ask("\n[cyan]✅ Confirm sending email?[/cyan]"):
        success, metadata = send_email(receiver, subject, message)
        if success:
            console.print(f"\n[green]✅ Email sent successfully to {receiver}![/green]\n")
        else:
            console.print(f"\n[red]❌ Failed to send email: {metadata.get('message', 'Unknown error')}[/red]\n")
    else:
        console.print("[yellow]⚠️  Email sending cancelled[/yellow]\n")

def send_bulk_email():
    console.print("\n[bold yellow]📨 Bulk Email Mode[/bold yellow]\n")
    
    try:
        with open("contacts.csv") as file:
            reader = csv.DictReader(file)
            contacts = list(reader)
    except FileNotFoundError:
        console.print("[red]❌ contacts.csv file not found[/red]\n")
        return
    except Exception as e:
        console.print(f"[red]❌ Error reading contacts: {e}[/red]\n")
        return
    
    if not contacts:
        console.print("[red]❌ No contacts found in contacts.csv[/red]\n")
        return
    
    table = Table(title="📋 Contacts to Send", border_style="blue")
    table.add_column("No.", style="yellow", width=5)
    table.add_column("Name", style="cyan", width=15)
    table.add_column("Email", style="green", width=25)
    
    for idx, contact in enumerate(contacts, 1):
        table.add_row(
            str(idx),
            contact.get("name", "N/A")[:14],
            contact.get("email", "N/A")
        )
    
    console.print(table)
    
    subject = Prompt.ask("\n[cyan]Enter subject[/cyan]").strip()
    if not subject:
        console.print("[red]❌ Subject cannot be empty[/red]")
        return
    
    message = Prompt.ask("[cyan]Enter message[/cyan]").strip()
    if not message:
        console.print("[red]❌ Message cannot be empty[/red]")
        return
    
    if Confirm.ask(f"\n[yellow]Send email to {len(contacts)} contact(s)?[/yellow]"):
        console.print("\n[bold]🚀 Sending emails...[/bold]\n")
        
        sent = 0
        failed = 0
        failed_list = []
        send_details = []
        
        for contact in track(contacts, description="[green]Progress:"):
            email = contact.get("email", "").strip()
            name = contact.get("name", "Recipient")
            
            if validate_email(email):
                success, metadata = send_email(email, subject, message)
                if success:
                    sent += 1
                    send_details.append({
                        "name": name,
                        "email": email,
                        "status": "✅ SUCCESS",
                        "time": metadata.get("timestamp", "")
                    })
                else:
                    failed += 1
                    failed_list.append(email)
                    send_details.append({
                        "name": name,
                        "email": email,
                        "status": "❌ FAILED",
                        "time": metadata.get("timestamp", ""),
                        "reason": metadata.get("message", "Unknown error")
                    })
            else:
                console.print(f"[red]⚠️  Skipped invalid email: {email}[/red]")
                failed += 1
                failed_list.append(email)
        
        summary_title = f"📊 Bulk Send Summary - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        summary = Table(title=summary_title, border_style="green")
        summary.add_column("Metric", style="blue", width=15)
        summary.add_column("Count", style="bold", width=10)
        summary.add_column("Percentage", style="cyan", width=15)
        
        total = len(contacts)
        sent_pct = f"{(sent/total*100):.1f}%" if total > 0 else "0%"
        failed_pct = f"{(failed/total*100):.1f}%" if total > 0 else "0%"
        
        summary.add_row(f"[green]✅ Sent[/green]", f"[bold green]{sent}[/bold green]", f"[green]{sent_pct}[/green]")
        summary.add_row(f"[red]❌ Failed[/red]", f"[bold red]{failed}[/bold red]", f"[red]{failed_pct}[/red]")
        summary.add_row(f"[cyan]📊 Total[/cyan]", f"[bold cyan]{total}[/bold cyan]", "100%")
        
        console.print(Panel(summary, border_style="green"))
        
        if failed_list:
            console.print("\n[bold red]Failed Email Addresses:[/bold red]")
            for email in failed_list:
                console.print(f"  • {email}", style="red")
        
        console.print()
    else:
        console.print("[yellow]⚠️  Bulk email sending cancelled[/yellow]\n")

def view_email_logs():
    console.print("\n[bold cyan]📜 Email Logs[/bold cyan]\n")
    
    logs = view_logs()
    if not logs:
        console.print("[yellow]⚠️  No logs found[/yellow]\n")
        return
    
    log_table = Table(title="📋 Recent Email Activity", border_style="blue")
    log_table.add_column("Timestamp", style="cyan", width=20)
    log_table.add_column("Recipient", style="green", width=25)
    log_table.add_column("Status", style="magenta", width=12)
    
    for log_line in logs[-20:]:
        try:
            if "[" in log_line and "]" in log_line:
                timestamp = log_line[1:log_line.index("]")]
                
                if "To:" in log_line:
                    email_start = log_line.index("To:") + 4
                    email_end = log_line.index("|", email_start)
                    email = log_line[email_start:email_end].strip()
                    
                    if "SUCCESS" in log_line:
                        status = "✅ SUCCESS"
                        status_style = "green"
                    elif "FAILED" in log_line:
                        status = "❌ FAILED"
                        status_style = "red"
                    else:
                        status = "⚠️  UNKNOWN"
                        status_style = "yellow"
                    
                    log_table.add_row(timestamp, email, f"[{status_style}]{status}[/{status_style}]")
        except Exception:
            continue
    
    console.print(log_table)
    
    stats = get_log_summary()
    console.print(f"\n[bold cyan]📊 Log Statistics:[/bold cyan]")
    console.print(f"  • [green]Total Successful:[/green] {stats['success']}")
    console.print(f"  • [red]Total Failed:[/red] {stats['failed']}")
    console.print(f"  • [cyan]Total Entries:[/cyan] {stats['total']}")
    console.print()

def clear_email_logs():
    console.print("\n[bold red]⚠️  Clear Email Logs[/bold red]\n")
    
    if Confirm.ask("[yellow]Are you sure you want to clear all logs?[/yellow]"):
        clear_logs()
        console.print("[green]✅ All logs cleared successfully![/green]\n")
    else:
        console.print("[yellow]Logs not cleared[/yellow]\n")

def manage_auto_replies():
    engine = AutoReplyEngine()
    
    while True:
        console.print("\n[bold cyan]🤖 Auto-Reply Management[/bold cyan]\n")
        
        menu = Table.grid(padding=1)
        menu.add_row("[bold green]1.[/bold green] View Auto-Reply Rules")
        menu.add_row("[bold green]2.[/bold green] Add New Auto-Reply")
        menu.add_row("[bold yellow]3.[/bold yellow] View Blacklist")
        menu.add_row("[bold yellow]4.[/bold yellow] Add Email to Blacklist")
        menu.add_row("[bold red]5.[/bold red] Back to Main Menu")
        
        console.print(Panel(menu, title="[bold]Auto-Reply Menu[/bold]", border_style="cyan"))
        
        choice = Prompt.ask("[bold cyan]Enter your choice[/bold cyan]", choices=["1", "2", "3", "4", "5"])
        
        if choice == "1":
            view_auto_replies(engine)
        elif choice == "2":
            add_auto_reply(engine)
        elif choice == "3":
            view_blacklist(engine)
        elif choice == "4":
            add_to_blacklist(engine)
        elif choice == "5":
            break

def view_auto_replies(engine):
    rules = engine.auto_replies
    
    if not rules:
        console.print("[yellow]⚠️  No auto-reply rules configured[/yellow]\n")
        return
    
    table = Table(title="📋 Auto-Reply Rules (Keyword-Based Matching)", border_style="blue")
    table.add_column("No.", style="yellow", width=5)
    table.add_column("Keyword Match", style="cyan", width=30)
    table.add_column("Reply Message", style="green", width=50)
    
    for idx, rule in enumerate(rules, 1):
        subject = rule.get("subject", "N/A")
        message = rule.get("reply_message", "N/A")
        msg_preview = message[:45] + "..." if len(message) > 45 else message
        table.add_row(str(idx), subject, msg_preview)
    
    console.print(table)     
    console.print(f"\n[cyan]Total Rules: {len(rules)}[/cyan]")
    console.print("[yellow]💡 Tip: Keywords are matched anywhere in the subject (case-insensitive)[/yellow]\n")

def add_auto_reply(engine):
    console.print("\n[bold cyan]➕ Add New Auto-Reply[/bold cyan]\n")
    
    subject = Prompt.ask("Enter email subject to match (e.g., 'Hello', 'Support')").strip()
    if not subject:
        console.print("[red]❌ Subject cannot be empty[/red]\n")
        return
    
    message = Prompt.ask("Enter reply message").strip()
    if not message:
        console.print("[red]❌ Reply message cannot be empty[/red]\n")
        return
    
    if engine.add_auto_reply(subject, message):
        console.print(f"[green]✅ Auto-reply added for '{subject}'[/green]\n")
    else:
        console.print("[red]❌ Failed to add auto-reply[/red]\n")

def view_blacklist(engine):
    blacklist = engine.blacklist
    
    if not blacklist:
        console.print("[yellow]⚠️  No blacklisted emails[/yellow]\n")
        return
    
    table = Table(title="📋 Blacklisted Emails", border_style="red")
    table.add_column("No.", style="yellow", width=5)
    table.add_column("Email Address", style="red", width=50)
    
    for idx, email in enumerate(blacklist, 1):
        table.add_row(str(idx), email)
    
    console.print(table)
    console.print(f"\n[cyan]Total Blacklisted: {len(blacklist)}[/cyan]\n")

def add_to_blacklist(engine):
    console.print("\n[bold cyan]➕ Add Email to Blacklist[/bold cyan]\n")
    
    email = Prompt.ask("Enter email address to blacklist").strip()
    if not validate_email(email):
        console.print("[red]❌ Invalid email format[/red]\n")
        return
    
    if engine.add_blacklist(email):
        console.print(f"[green]✅ {email} added to blacklist[/green]\n")
    else:
        console.print("[red]❌ Failed to add email to blacklist[/red]\n")

def check_auto_reply_status():
    engine = AutoReplyEngine()
    stats = engine.get_stats()
    
    console.print("\n[bold cyan]📊 Auto-Reply Status[/bold cyan]\n")
    
    table = Table(border_style="blue")
    table.add_column("Metric", style="cyan", width=30)
    table.add_column("Count", style="green", width=20)
    
    table.add_row("Total Rules", f"[green]{stats['total_rules']}[/green]")
    table.add_row("Blacklisted Emails", f"[red]{stats['blacklisted']}[/red]")
    table.add_row("Emails Already Replied", f"[yellow]{stats['replied']}[/yellow]")
    
    console.print(table)
    console.print()

def monitor_incoming_emails():
    console.print("\n[bold magenta]📧 Email Monitoring[/bold magenta]\n")
    
    reader = EmailReader()
    engine = AutoReplyEngine()
    
    if not reader.connect():
        console.print("[red]❌ Failed to connect to Gmail IMAP[/red]\n")
        return
    
    console.print("[cyan]Fetching unread emails from last 1 hour...[/cyan]")
    emails = reader.fetch_unread_emails(hours_back=1)
    
    reader.disconnect()
    
    if not emails:
        console.print("[yellow]⚠️  No unread emails from last 1 hour[/yellow]\n")
        return
    
    console.print(f"\n[cyan]Processing {len(emails)} email(s)...[/cyan]\n")
    
    results_table = Table(title="📧 Processing Results", border_style="blue")
    results_table.add_column("From", style="cyan", width=30)
    results_table.add_column("Subject", style="green", width=35)
    results_table.add_column("Status", style="magenta", width=20)
    
    for email in emails:
        sender = email.get("from", "Unknown")
        subject = email.get("subject", "No Subject")
        
        sender_email = sender.split("<")[1].split(">")[0] if "<" in sender else sender
        
        success, message = engine.process_email(sender_email, subject)
        
        status = f"[green]✅ Replied[/green]" if success else f"[yellow]⏭️  Skipped[/yellow]"
        
        subject_preview = subject[:30] + "..." if len(subject) > 30 else subject
        results_table.add_row(sender_email, subject_preview, status)
    
    console.print(results_table)
    console.print()

def main():
    try:
        display_banner()
        
        while True:
            display_menu()
            choice = Prompt.ask("[bold cyan]Enter your choice[/bold cyan]", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "1":
                send_single_email()
            elif choice == "2":
                send_bulk_email()
            elif choice == "3":
                view_email_logs()
            elif choice == "4":
                clear_email_logs()
            elif choice == "5":
                manage_auto_replies()
            elif choice == "6":
                check_auto_reply_status()
            elif choice == "7":
                monitor_incoming_emails()
            elif choice == "8":
                console.print("\n[bold cyan]👋 Thank you for using Email Automation Tool![/bold cyan]\n")
                break
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Application interrupted by user[/yellow]\n")
    except Exception as e:
        console.print(f"[red]❌ Unexpected error: {e}[/red]\n")

if __name__ == "__main__":
    main()
