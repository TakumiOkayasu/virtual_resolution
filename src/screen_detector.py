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
Add-Type -AssemblyName System.Windows.Forms
$screen = [System.Windows.Forms.Screen]::PrimaryScreen
$physicalWidth = $screen.Bounds.Width
$physicalHeight = $screen.Bounds.Height

$videoController = Get-CimInstance Win32_VideoController | Select-Object -First 1
$effectiveWidth = $videoController.CurrentHorizontalResolution
$effectiveHeight = $videoController.CurrentVerticalResolution

if ($effectiveWidth -and $effectiveWidth -gt 0) {
    $scale = [math]::Round($physicalWidth / $effectiveWidth * 100)
} else {
    $scale = 100
}

Write-Output $physicalWidth
Write-Output $physicalHeight
Write-Output $scale
"""

    result = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command", ps_script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
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
