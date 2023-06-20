#!env/bin/python3

import os
import subprocess

CONTAINERS_PATH = "./scripts/containers"
CONTAINERS = ["fastapi","flask","express","codeserver","react","vue","php"]

def main():
	for container in CONTAINERS:
		pwd = os.getcwd()
		os.chdir(f"{CONTAINERS_PATH}/{container}")
		print(f"Building {container} container...")
		subprocess.run(["docker","build","-t",f"{container}:latest","."])
		os.chdir(pwd)
		
if __name__ == "__main__":
	main()