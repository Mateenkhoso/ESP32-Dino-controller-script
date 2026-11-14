"""
ESP32 Ultrasonic Gesture Controller for Chrome Dino Game
------------------------------------------------------
HOW TO USE:
1. Upload the embedded C++ code below to your ESP32 using Arduino IDE.
2. Install Python dependencies: pip install pyserial pyautogui
3. Update SERIAL_PORT below to match your ESP32 COM port.
4. Run this script: python controller.py
5. Open chrome://dino, click the window, and use your hand over the sensor!
"""

# =====================================================================
# PART 1: EMBEDDED FIRMWARE (C++)
# Copy this block into the Arduino IDE and upload it to your ESP32 board.
# =====================================================================
"""
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

const int trigPin = 5;
const int echoPin = 18;

void setup() {
  Serial.begin(115200);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

  if (!display.begin(SSD1306_SWITCHCAPVCC, 0x3C)) {
    for (;;);
  }
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
}

void loop() {
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);

  long duration = pulseIn(echoPin, HIGH, 30000);
  int distance = duration * 0.034 / 2;

  display.clearDisplay();
  display.setTextSize(2);
  display.setCursor(10, 10);
  display.print(distance);
  display.println(" cm");

  display.setTextSize(1);
  display.setCursor(10, 40);

  if (distance > 2 && distance <= 15) {
    display.print("ACTION: JUMP");
    Serial.println("JUMP");
  } else if (distance > 15 && distance <= 28) {
    display.print("ACTION: DUCK");
    Serial.println("DUCK");
  } else {
    display.print("ACTION: RUN");
    Serial.println("RUN");
  }

  display.display();
  delay(30);
}
"""


# =====================================================================
# PART 2: HOST DESKTOP CONTROLLER (Python)
# Run this file directly on your laptop.
# =====================================================================

import serial
import pyautogui

# Configuration
pyautogui.PAUSE = 0
SERIAL_PORT = 'COM3'  # Change to match your ESP32 port (e.g., 'COM4' or '/dev/ttyUSB0')
BAUD_RATE = 115200

is_ducking = False
has_jumped = False

def main():
    global is_ducking, has_jumped
    
    print(f"Connecting to ESP32 on {SERIAL_PORT}...")
    try:
        esp = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0.01)
        print("Connected successfully! Dino Controller Active. Press Ctrl+C to exit.")
        
        while True:
            if esp.in_waiting > 0:
                cmd = esp.readline().decode('utf-8', errors='ignore').strip()
                
                if cmd == "JUMP":
                    if is_ducking:
                        pyautogui.keyUp('down')
                        is_ducking = False
                    if not has_jumped:
                        pyautogui.press('space')
                        has_jumped = True
                        
                elif cmd == "DUCK":
                    has_jumped = False
                    if not is_ducking:
                        pyautogui.keyDown('down')
                        is_ducking = True
                        
                elif cmd == "RUN":
                    has_jumped = False
                    if is_ducking:
                        pyautogui.keyUp('down')
                        is_ducking = False

    except serial.SerialException:
        print(f"Error: Could not open port {SERIAL_PORT}. Make sure Arduino Serial Monitor is closed.")
    except KeyboardInterrupt:
        if is_ducking:
            pyautogui.keyUp('down')
        print("\nController stopped.")

if __name__ == "__main__":
    main()
