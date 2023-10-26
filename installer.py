import subprocess

def install_requirements():
    try:
        subprocess.run(["python", "-m", "pip", "install", "--upgrade", "pip", "setuptools"], check=True)
    except Exception as e:
        print(f"Error updating pip and setuptools: {e}")
        return
    with open("requirements.txt", "r") as f:
        packages = f.read().strip().splitlines()
    for package in packages:
        try:
            subprocess.run(["python", "-m", "pip", "install", package], check=True)
        except Exception as e:
            print(f"Error installing {package}: {e}")

if __name__ == "__main__":
    install_requirements()