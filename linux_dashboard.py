from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
import subprocess
import typer
import shutil

app = typer.Typer()
console = Console()


def run_command(command):
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return result.stderr.strip()
    except Exception as e:
        return str(e)


def ensure_package_installed(package_name, install_command):
    if not shutil.which(package_name):
        with Progress(SpinnerColumn(), TextColumn(f"Installing [bold]{package_name}[/bold]...")) as progress:
            progress.add_task(f"install-{package_name}", total=None)
            run_command(install_command)


def render_system_dashboard():
    console.print("[bold green]System Dashboard[/bold green]".center(100, "="))
    
    ensure_package_installed("clamscan", "sudo apt-get install -y clamav")
    ensure_package_installed("rkhunter", "sudo apt-get install -y rkhunter")

    system_info = run_command("hostnamectl")
    limited_support_packages = run_command("sudo check-support-status | grep 'Source:' | awk -F 'Source:' '{print $2}' | tr -d ' '")
    user_list = run_command("getent passwd | awk -F: '$7 ~ /(\/bin\/bash|\/bin\/sh)/ {print $1}'")
    sudo_users = run_command("grep -Po '^sudo.+:\K.*$' /etc/group")
    group_list = run_command("getent group | awk -F: '$3 >= 1000 {print $1}'")
    login_history = run_command("last | awk '!/reboot/ {print $1, $2, $3, $4, $5, $6, $7, $8, $9, $10}'")
    clamav_scan = run_command("clamscan -i -r")
    rkhunter_scan = run_command("sudo rkhunter --check -q --sk --propupd; sudo grep -E 'Warning:' /var/log/rkhunter.log")

    sysinfo_panel = Panel(f"[bold]System Information[/bold]:\n{system_info}\n\n[bold]Limited Security Support Packages[/bold]:\n{limited_support_packages}", title="System Info", border_style="blue")
    users_panel = Panel(f"[bold]Users[/bold]:\n{user_list}\n\n[bold]Sudo Users[/bold]:\n{sudo_users}", title="Users", border_style="blue")
    groups_panel = Panel(group_list, title="Groups", border_style="blue")
    login_panel = Panel(login_history, title="Recent Logins", border_style="blue")
    clamav_panel = Panel(clamav_scan, title="ClamAV Scan Results", border_style="blue")
    rkhunter_panel = Panel(rkhunter_scan, title="Rkhunter Warnings", border_style="blue", height=10)

    layout = Layout()
    layout.split_column(
        Layout(name="top"),
        Layout(name="middle"),
        Layout(rkhunter_panel, name="bottom")
    )
    layout["top"].split_row(
        Layout(sysinfo_panel, name="top_left"),
        Layout(name="top_right")
    )
    layout["top_right"].split_row(
        Layout(users_panel, name="top_right_left"),
        Layout(groups_panel, name="top_right_right")
    )
    layout["middle"].split_row(
        Layout(login_panel, name="middle_left"),
        Layout(clamav_panel, name="middle_right")
    )

    console.print(layout)

    input("Press Enter to proceed to the Network Dashboard...")


def render_network_dashboard():
    console.print("[bold green]Network Dashboard[/bold green]".center(100, "="))

    ensure_package_installed("ufw", "sudo apt-get install -y ufw")
    
    # network information
    ip_info = run_command("ip -4 -o addr show | awk '{print $1, $2, $3, $4}'")
    route_info = run_command("ip route show | awk -F 'src' '{print $1}'")
    rule_info = run_command('ip rule show')
    ufw_status = run_command('sudo ufw status verbose')
    network_connections = run_command('netstat -tulpna')
    process_info = run_command('ps aux --sort=-%cpu | head')

    ip_panel = Panel(f"[bold]IP Addresses[/bold]:\n{ip_info}\n\n[bold]Routing Table[/bold]:\n{route_info}\n\n[bold]Routing Rules[/bold]:\n{rule_info}", title="IP Information", border_style="blue")
    ufw_panel = Panel(ufw_status, title="UFW Status", border_style="blue")
    netstat_panel = Panel(network_connections, title="Active Network Connections", border_style="blue")
    process_panel = Panel(process_info, title="Top Processes by CPU Usage", border_style="blue")

    layout = Layout()
    layout.split_column(
        Layout(name="top"),
        Layout(netstat_panel, name="middle"),
        Layout(process_panel, name="bottom")
    )
    layout["top"].split_row(
        Layout(ip_panel, name="top_left"),
        Layout(ufw_panel, name="top_right")
    )

    console.print(layout)


@app.command()
def render_dashboards():
    render_system_dashboard()
    render_network_dashboard()

if __name__ == "__main__":
    app()
