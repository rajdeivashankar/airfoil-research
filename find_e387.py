with open("data/experimental/DRAG01.TXT") as fh:
    text = fh.read()
for i, line in enumerate(text.splitlines()):
    if "E387" in line.upper():
        print(i, repr(line))

with open("data/experimental/DRAG01.TXT") as fh:
    lines = fh.read().splitlines()

# print from the E387 header for ~120 lines to capture all its Re blocks
for i in range(361, 481):
    print(i, lines[i])