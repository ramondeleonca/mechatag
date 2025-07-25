# MechaTag - Apriltag localization for MechaLeague and small robots.

Apriltag localization for MechaLeague and small robots. MechaTag is a smart camera and software suite based on the Raspberry Pi Zero 2w, made to localize MechaLeague robots on the field

# Setup

### 1. Flash Raspberry Pi OS Lite (Bookworm)
Using [Raspberry Pi Imager](https://www.raspberrypi.com/software/), flash Raspberry Pi OS Lite (Bookworm) 64-bit to a 16GB or more micro SD card

![Raspberry Pi imager options](assets/rpiim.png)

**Why Bookworm and not Bullseye?** The library used my mechatag to scan apriltags (robotpy-apriltag) only has a precompiled version for glibc 2.36+ and Python 3.11, both of which Bookworm complies with but Bullseye doesn't.

### 2. Clone the repository
First install git with this command:
```sh
sudo apt update && sudo apt install git -y
```
Then clone this repository with git :
```sh
git clone <repo_url>
```

### 3. Install dependencies
Install debian packaged dependencies:
```sh
sudo apt install python3-flask python3-opencv python3-picamera2 python3-fastapi
```

Create a virtual environment for the project
```sh
python3 -m venv --system-site-packages .venv
```

Activate virtual environment
```sh
source .venv/bin/activate
```

Install apriltag detector
```sh
pip install robotpy-apriltag pyserial
```

### 4. Set up USB Ethernet Gadget Mode
Follow the steps in this repository https://github.com/charkster/rpi_gadget_mode/tree/main to set up USB Ethernet Gadget mode, for communicating via the OTG port on the Pi

From this point forward, you should be able to SSH into `192.168.1.2` when connected to the USB port on the Pi

### 5. Enable UART on the Raspberry Pi
Edit the config file
```sh
sudo nano /boot/firmware/config.txt
```

Below the other configs, over the other sections add
```sh
enable_uart=1
```

Save out of nano and reboot
```sh
sudo reboot
```

### Run main.py in venv
```sh
python3 ./src/main.py
```