#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenClaw Tray - System tray application for managing OpenClaw Gateway
"""

import subprocess
import webbrowser
import time
import threading
from pathlib import Path
from typing import Optional

import pystray
from PIL import Image, ImageDraw
import psutil

# Configuration
OPENCLAW_CMD = "openclaw"
GATEWAY_PORT = 18789
DASHBOARD_URL = f"http://127.0.0.1:{GATEWAY_PORT}/"
ICON_SIZE = 64

# Colors for status
COLOR_RUNNING = "#4CAF50"      # Green
COLOR_STOPPED = "#F44336"      # Red
COLOR_UNKNOWN = "#9E9E9E"      # Gray


class OpenClawManager:
    """Manager for OpenClaw Gateway service"""
    
    def __init__(self):
        self._status_cache = None
        self._last_check = 0
        
    def is_gateway_running(self) -> bool:
        """Check if OpenClaw Gateway is running"""
        try:
            # Check by port
            for conn in psutil.net_connections():
                if conn.laddr.port == GATEWAY_PORT and conn.status == 'LISTEN':
                    return True
            return False
        except Exception:
            return False
    
    def get_status(self) -> str:
        """Get current status string"""
        return "Running" if self.is_gateway_running() else "Stopped"
    
    def start_gateway(self) -> bool:
        """Start OpenClaw Gateway"""
        if self.is_gateway_running():
            return True
        try:
            subprocess.Popen(
                [OPENCLAW_CMD, "gateway", "start"],
                shell=True,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            time.sleep(2)  # Wait for startup
            return self.is_gateway_running()
        except Exception as e:
            print(f"Failed to start gateway: {e}")
            return False
    
    def stop_gateway(self) -> bool:
        """Stop OpenClaw Gateway"""
        try:
            subprocess.run(
                [OPENCLAW_CMD, "gateway", "stop"],
                shell=True,
                capture_output=True
            )
            time.sleep(1)
            return not self.is_gateway_running()
        except Exception as e:
            print(f"Failed to stop gateway: {e}")
            return False
    
    def restart_gateway(self) -> bool:
        """Restart OpenClaw Gateway"""
        self.stop_gateway()
        time.sleep(1)
        return self.start_gateway()
    
    def open_dashboard(self):
        """Open Dashboard in browser"""
        webbrowser.open(DASHBOARD_URL)


class TrayIcon:
    """System tray icon for OpenClaw"""
    
    def __init__(self, manager: OpenClawManager):
        self.manager = manager
        self.icon: Optional[pystray.Icon] = None
        self.running = True
        
    def create_icon_image(self, color: str) -> Image.Image:
        """Create icon image with specified color"""
        # Create a simple circle icon
        img = Image.new('RGBA', (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw circle
        margin = 8
        draw.ellipse(
            [margin, margin, ICON_SIZE - margin, ICON_SIZE - margin],
            fill=color,
            outline="white",
            width=2
        )
        
        # Draw "OC" text
        try:
            from PIL import ImageFont
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
        
        text = "OC"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (ICON_SIZE - text_width) // 2
        y = (ICON_SIZE - text_height) // 2 - 2
        draw.text((x, y), text, fill="white", font=font)
        
        return img
    
    def update_icon(self):
        """Update icon based on current status"""
        if self.icon is None:
            return
            
        if self.manager.is_gateway_running():
            img = self.create_icon_image(COLOR_RUNNING)
        else:
            img = self.create_icon_image(COLOR_STOPPED)
        
        self.icon.icon = img
        self.icon.title = f"OpenClaw - {self.manager.get_status()}"
    
    def create_menu(self) -> pystray.Menu:
        """Create context menu"""
        return pystray.Menu(
            pystray.MenuItem(
                lambda: f"Status: {self.manager.get_status()}",
                lambda: None,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Open Dashboard", self._on_open_dashboard),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Start", self._on_start, visible=self._show_start),
            pystray.MenuItem("Stop", self._on_stop, visible=self._show_stop),
            pystray.MenuItem("Restart", self._on_restart),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self._on_exit),
        )
    
    def _show_start(self) -> bool:
        return not self.manager.is_gateway_running()
    
    def _show_stop(self) -> bool:
        return self.manager.is_gateway_running()
    
    def _on_open_dashboard(self):
        self.manager.open_dashboard()
    
    def _on_start(self):
        self.manager.start_gateway()
        self.update_icon()
    
    def _on_stop(self):
        self.manager.stop_gateway()
        self.update_icon()
    
    def _on_restart(self):
        self.manager.restart_gateway()
        self.update_icon()
    
    def _on_exit(self):
        self.running = False
        if self.icon:
            self.icon.stop()
    
    def _status_monitor(self):
        """Background thread to monitor status"""
        while self.running:
            self.update_icon()
            time.sleep(5)  # Check every 5 seconds
    
    def run(self):
        """Run the tray icon"""
        # Create initial icon
        img = self.create_icon_image(COLOR_UNKNOWN)
        
        self.icon = pystray.Icon(
            "openclaw",
            img,
            "OpenClaw",
            menu=self.create_menu()
        )
        
        # Start status monitor thread
        monitor_thread = threading.Thread(target=self._status_monitor, daemon=True)
        monitor_thread.start()
        
        # Run icon (blocking)
        self.icon.run()


def main():
    """Main entry point"""
    print("Starting OpenClaw Tray...")
    
    manager = OpenClawManager()
    tray = TrayIcon(manager)
    tray.run()


if __name__ == "__main__":
    main()
