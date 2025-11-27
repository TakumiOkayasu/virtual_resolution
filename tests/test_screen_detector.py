import pytest
from unittest.mock import patch, MagicMock
from screen_detector import ScreenInfo, detect_screen_info


class TestScreenInfo:
    def test_screen_info_creation(self):
        info = ScreenInfo(width=1920, height=1080, scale_factor=1.0)
        assert info.width == 1920
        assert info.height == 1080
        assert info.scale_factor == 1.0

    def test_effective_resolution_no_scaling(self):
        info = ScreenInfo(width=1920, height=1080, scale_factor=1.0)
        assert info.effective_width == 1920
        assert info.effective_height == 1080

    def test_effective_resolution_with_200_percent_scaling(self):
        # 4K monitor with 200% scaling -> effective 1920x1080
        info = ScreenInfo(width=3840, height=2160, scale_factor=2.0)
        assert info.effective_width == 1920
        assert info.effective_height == 1080

    def test_effective_resolution_with_150_percent_scaling(self):
        # 4K monitor with 150% scaling -> effective 2560x1440
        info = ScreenInfo(width=3840, height=2160, scale_factor=1.5)
        assert info.effective_width == 2560
        assert info.effective_height == 1440

    def test_effective_resolution_with_125_percent_scaling(self):
        info = ScreenInfo(width=1920, height=1080, scale_factor=1.25)
        assert info.effective_width == 1536
        assert info.effective_height == 864


class TestDetectScreenInfo:
    def test_detect_returns_screen_info(self):
        result = detect_screen_info()
        assert isinstance(result, ScreenInfo)
        assert result.width > 0
        assert result.height > 0
        assert result.scale_factor > 0

    def test_detect_with_mocked_powershell_4k_200_percent(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "3840\n2160\n200"

        with patch("subprocess.run", return_value=mock_result):
            result = detect_screen_info()
            assert result.width == 3840
            assert result.height == 2160
            assert result.scale_factor == 2.0
            assert result.effective_width == 1920
            assert result.effective_height == 1080

    def test_detect_with_mocked_powershell_1080p_100_percent(self):
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "1920\n1080\n100"

        with patch("subprocess.run", return_value=mock_result):
            result = detect_screen_info()
            assert result.width == 1920
            assert result.height == 1080
            assert result.scale_factor == 1.0
