from dataclasses import dataclass
import subprocess


@dataclass
class ScreenInfo:
    width: int
    height: int
    scale_factor: float

    @property
    def effective_width(self) -> int:
        return int(self.width / self.scale_factor)

    @property
    def effective_height(self) -> int:
        return int(self.height / self.scale_factor)


def detect_screen_info() -> ScreenInfo:
    """Detect screen resolution and scaling factor from Windows via PowerShell."""
    ps_script = """
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class DisplayInfo {
    [DllImport("user32.dll")]
    public static extern int GetSystemMetrics(int nIndex);
    [DllImport("gdi32.dll")]
    public static extern int GetDeviceCaps(IntPtr hdc, int nIndex);
    [DllImport("user32.dll")]
    public static extern IntPtr GetDC(IntPtr hWnd);
    [DllImport("user32.dll")]
    public static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);
}
"@
$hdc = [DisplayInfo]::GetDC([IntPtr]::Zero)
$dpiX = [DisplayInfo]::GetDeviceCaps($hdc, 88)
[DisplayInfo]::ReleaseDC([IntPtr]::Zero, $hdc) | Out-Null
$width = [DisplayInfo]::GetSystemMetrics(0)
$height = [DisplayInfo]::GetSystemMetrics(1)
$scale = [math]::Round($dpiX / 96 * 100)
Write-Output $width
Write-Output $height
Write-Output $scale
"""

    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", ps_script],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Failed to detect screen info: {result.stderr}")

    lines = result.stdout.strip().split("\n")
    width = int(lines[0])
    height = int(lines[1])
    scale_percent = int(lines[2])

    return ScreenInfo(
        width=width,
        height=height,
        scale_factor=scale_percent / 100.0,
    )
