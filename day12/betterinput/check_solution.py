import sys
from pathlib import Path

def check(answer):
    path = Path(__file__).parent / "solution.txt"
    encoded = open(path, "rb").read()
    decoded = bytes(b ^ (answer % 256) for b in encoded).decode(errors='replace')
    return decoded

if __name__ == "__main__":
    if len(sys.argv) > 1:
        answer = int(sys.argv[1])
    else:
        answer = int(input("Your answer: "))
    print(check(answer))
