import platform
import subprocess
import sys

'''
Install Python packages using pip based on the operating system.
'''
def install_python_packages():
    system = platform.system()
    if system == "Linux":
        distro = ""
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        distro = line.strip().split("=")[1].strip('"')
                        break
        except FileNotFoundError:
            pass

        if distro in ["ubuntu", "debian"]:
            subprocess.run(["sudo", "apt-get", "update"])
            subprocess.run(["sudo", "apt-get", "install", "-y", "python3-pip"])
        elif distro in ["fedora"]:
            subprocess.run(["sudo", "dnf", "install", "-y", "python3-pip"])
        elif distro in ["arch"]:
            subprocess.run(["sudo", "pacman", "-Syu", "--noconfirm", "python-pip"])
        else:
            print(f"Unsupported Linux distribution: {distro}")
            sys.exit(1)
    elif system == "Darwin":
        try:
            subprocess.run(["brew", "install", "python3"], check=True)
        except subprocess.CalledProcessError:
            print("Homebrew is not installed or failed to install Python3.")
            sys.exit(1)
    elif system == "Windows":
        print("Please install Python3 and pip manually from https://www.python.org/downloads/windows/")
        sys.exit(1)
    else:
        print(f"Unsupported operating system: {system}")
        sys.exit(1)

    subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

'''
Install non-Python dependencies based on the operating system.
'''
def install_dependencies():
    system = platform.system()
    if system == "Linux":
        distro = ""
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("ID="):
                        distro = line.strip().split("=")[1].strip('"')
                        break
        except FileNotFoundError:
            pass

        if distro in ["ubuntu", "debian"]:
            subprocess.run(["sudo", "apt-get", "install", "-y", "ffmpeg", "libsm6", "libxext6", "ImageMagick"])
        elif distro in ["fedora"]:
            subprocess.run(["sudo", "dnf", "install", "-y", "ffmpeg", "libSM", "libXext", "ImageMagick"])
        elif distro in ["arch"]:
            subprocess.run(["sudo", "pacman", "-Syu", "--noconfirm", "ffmpeg", "libsm", "libxext", "ImageMagick"])
        else:
            print(f"Unsupported Linux distribution: {distro}")
            sys.exit(1)
    elif system == "Darwin":
        try:
            subprocess.run(["brew", "install", "ffmpeg", "ImageMagick"], check=True)
        except subprocess.CalledProcessError:
            print("Homebrew is not installed or failed to install ffmpeg.")
            sys.exit(1)
    elif system == "Windows":
        print("Please install ffmpeg manually from https://ffmpeg.org/download.html")
        print("Please install ImageMagick manually from https://imagemagick.org/script/download.php#windows")
        sys.exit(1)
    else:
        print(f"Unsupported operating system: {system}")
        sys.exit(1)