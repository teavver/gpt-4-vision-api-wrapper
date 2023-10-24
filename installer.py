import subprocess

def install_requirements():
    with open("requirements.txt", "r") as f:
        packages = f.read().splitlines()
    
    for package in packages:
        subprocess.check_call(["pip", "install", package])

if __name__ == "__main__":
    install_requirements()