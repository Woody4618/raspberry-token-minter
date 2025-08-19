#!/usr/bin/env python3
"""
MP3-TF-16P Player for Raspberry Pi
With correct command format and checksum calculation
"""

import serial
import time
import os
from typing import Optional

class MP3Player:
    def __init__(self, port='/dev/serial0', baudrate=9600, timeout=1):
        """
        Initialize MP3-TF-16P player for Raspberry Pi
        
        Args:
            port: Serial port (use /dev/serial0 for Pi)
            baudrate: Communication speed (default 9600)
            timeout: Serial timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.serial = None
        self.is_connected = False
        
    def connect(self) -> bool:
        """Connect to the MP3-TF-16P module"""
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            self.is_connected = True
            print(f"✅ Connected to MP3-TF-16P on {self.port}")
            return True
        except serial.SerialException as e:
            print(f"❌ Failed to connect to {self.port}: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the MP3-TF-16P module"""
        if self.serial and self.serial.is_open:
            self.serial.close()
            self.is_connected = False
            print("🔌 Disconnected from MP3-TF-16P")
    
    def build_command(self, cmd, param1=0, param2=0):
        """
        Build command with proper format and checksum
        
        Args:
            cmd: Command byte
            param1: First parameter
            param2: Second parameter
            
        Returns:
            List of bytes representing the command
        """
        command = [
            0x7E, 0xFF, 0x06, cmd, 0x00,
            param1, param2,
            0x00, 0x00, 0xEF
        ]
        
        # Calculate checksum
        checksum = 0 - sum(command[1:7])
        command[7] = (checksum >> 8) & 0xFF
        command[8] = checksum & 0xFF
        
        return command
    
    def send_command(self, command: list, description: str = "") -> bool:
        """
        Send command to MP3-TF-16P
        
        Args:
            command: List of bytes to send
            description: Description of the command
            
        Returns:
            True if command sent successfully
        """
        if not self.is_connected or not self.serial:
            print("❌ Not connected to MP3-TF-16P")
            return False
        
        try:
            print(f"🎵 {description}")
            print(f"Command: {[hex(x) for x in command]}")
            self.serial.write(bytes(command))
            time.sleep(0.1)  # Small delay for command processing
            return True
        except Exception as e:
            print(f"❌ Error sending command: {e}")
            return False
    
    def play_track(self, track_number: int) -> bool:
        """
        Play a specific track by number
        
        Args:
            track_number: Track number (1-255)
            
        Returns:
            True if command sent successfully
        """
        if track_number < 1 or track_number > 255:
            print("❌ Track number must be between 1 and 255")
            return False
        
        command = self.build_command(0x03, 0x00, track_number)
        return self.send_command(command, f"Playing track {track_number}")
    
    def play_folder_track(self, folder: int, track: int) -> bool:
        """
        Play a track from a specific folder
        
        Args:
            folder: Folder number (1-99)
            track: Track number within folder (1-255)
            
        Returns:
            True if command sent successfully
        """
        if folder < 1 or folder > 99:
            print("❌ Folder number must be between 1 and 99")
            return False
        if track < 1 or track > 255:
            print("❌ Track number must be between 1 and 255")
            return False
        
        command = self.build_command(0x0F, folder, track)
        return self.send_command(command, f"Playing track {track} from folder {folder}")
    
    def pause(self) -> bool:
        """Pause playback"""
        command = self.build_command(0x02)
        return self.send_command(command, "Pausing playback")
    
    def resume(self) -> bool:
        """Resume playback"""
        command = self.build_command(0x0D)
        return self.send_command(command, "Resuming playback")
    
    def stop(self) -> bool:
        """Stop playback"""
        command = self.build_command(0x16)
        return self.send_command(command, "Stopping playback")
    
    def set_volume(self, volume: int) -> bool:
        """
        Set playback volume
        
        Args:
            volume: Volume level (0-30, where 0 is mute)
            
        Returns:
            True if command sent successfully
        """
        if volume < 0 or volume > 30:
            print("❌ Volume must be between 0 and 30")
            return False
        
        command = self.build_command(0x06, 0x00, volume)
        return self.send_command(command, f"Setting volume to {volume}")
    
    def get_status(self) -> Optional[dict]:
        """
        Get current playback status
        
        Returns:
            Dictionary with status info or None if error
        """
        command = self.build_command(0x42)
        if not self.send_command(command, "Getting status"):
            return None
        
        # Wait for response
        time.sleep(0.1)
        if self.serial.in_waiting:
            response = self.serial.read(self.serial.in_waiting)
            print(f"📊 Status response: {response.hex()}")
            return {"raw_response": response.hex()}
        return None
    
    def play_random(self) -> bool:
        """Play tracks in random order"""
        command = self.build_command(0x18)
        return self.send_command(command, "Playing in random order")
    
    def play_loop(self, enable: bool = True) -> bool:
        """
        Enable/disable loop playback
        
        Args:
            enable: True to enable loop, False to disable
            
        Returns:
            True if command sent successfully
        """
        command = self.build_command(0x19, 0x00, 0x01 if enable else 0x00)
        action = "enabling" if enable else "disabling"
        return self.send_command(command, f"{action.capitalize()} loop playback")
    
    def play_next(self) -> bool:
        """Play next track"""
        command = self.build_command(0x01)
        return self.send_command(command, "Playing next track")
    
    def play_previous(self) -> bool:
        """Play previous track"""
        command = self.build_command(0x02)
        return self.send_command(command, "Playing previous track")

def main():
    """Example usage of the MP3 player"""
    print("🎵 MP3-TF-16P Player for Raspberry Pi (Correct Format)")
    print("=" * 50)
    
    # Initialize player with correct Pi port
    player = MP3Player(port='/dev/serial0')
    
    if not player.connect():
        print("❌ Could not connect to MP3-TF-16P module")
        print("💡 Check your wiring and UART configuration")
        return
    
    try:
        # Example usage
        print("\n🎵 MP3 Player Commands:")
        print("1. Play track 1")
        print("2. Play track 2 from folder 1")
        print("3. Set volume")
        print("4. Pause/Resume")
        print("5. Stop")
        print("6. Next/Previous")
        print("7. Get status")
        print("8. Random play")
        print("9. Loop on/off")
        print("0. Exit")
        
        while True:
            choice = input("\nEnter your choice (0-9): ").strip()
            
            if choice == '1':
                player.play_track(1)
            elif choice == '2':
                player.play_folder_track(1, 2)
            elif choice == '3':
                volume = int(input("Enter volume (0-30): "))
                player.set_volume(volume)
            elif choice == '4':
                action = input("Pause (p) or Resume (r)? ").strip().lower()
                if action == 'p':
                    player.pause()
                elif action == 'r':
                    player.resume()
            elif choice == '5':
                player.stop()
            elif choice == '6':
                direction = input("Next (n) or Previous (p)? ").strip().lower()
                if direction == 'n':
                    player.play_next()
                elif direction == 'p':
                    player.play_previous()
            elif choice == '7':
                status = player.get_status()
                if status:
                    print(f"Status: {status}")
            elif choice == '8':
                player.play_random()
            elif choice == '9':
                enable = input("Enable (e) or Disable (d) loop? ").strip().lower()
                player.play_loop(enable == 'e')
            elif choice == '0':
                break
            else:
                print("❌ Invalid choice")
    
    except KeyboardInterrupt:
        print("\n🛑 Stopping player...")
    finally:
        player.stop()
        player.disconnect()

if __name__ == "__main__":
    main() 