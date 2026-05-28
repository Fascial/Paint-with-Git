import os
import argparse
import subprocess

if os.system("git --version"):
    print("git isn't installed, install git to use this tool")

parser = argparse.ArgumentParser(description="Paint with Git")
parser.add_argument("--dir", type=str, default="../.test", help="Directory for the painting with agent")
parser.add_argument("--dates", type=str, default=".dates", help="Directory for the commit dates")

args = parser.parse_args()

try:
    with open(".dates", "r") as file:
        dates = list(map(lambda x: x.replace("\n", ""), file.readlines()))
except FileNotFoundError:
    print(f"The dates file .date not found {'here' if os.curdir == '.' else os.curdir}")

try:
    os.chdir(args.dir)
except FileNotFoundError as e:
    print(f"The directory {args.dir} does not exist")
    exit()

if not ".git" in os.listdir():
    os.system("git init .")

message = "Commit made by paint with commit tool"
co_author = "Co-authored-by: Fascial <ID+Fascial@://github.com>"

for date in dates:
    command = ["git", "commit", "--allow-empty" ,f"--date='{date} 12:00:00'", "-m", message, "-m", co_author]
    subprocess.run(command)

if not bool(subprocess.run("git remote -v", capture_output=True).stdout):
    print("This repository isn't connected to a Github/Remote Repository")
else:
    os.system("git push")
