import urllib.request
base = "https://m-selig.ae.illinois.edu/pd/pub/lsat/volume01/"
for f in ["DRAG01.TXT", "LIFT01.TXT", "FORMAT01.TXT"]:
    urllib.request.urlretrieve(base + f, f"data/experimental/{f}")
    print("got", f)