#!env/bin/python3

import subprocess
import os

CONTAINERS_PATH = "./scripts/containers"
CONTAINERS = ["fastapi","flask","express","codeserver","react","vue"]

def build_containers():
	for container in CONTAINERS:
		pwd = os.getcwd()
		os.chdir(f"{CONTAINERS_PATH}/{container}")
		print(f"Building {container} container...")
		subprocess.run(["docker","build","-t",f"{container}:latest","."])
		os.chdir(pwd)
		
if __name__ == "__main__":
	build_containers()