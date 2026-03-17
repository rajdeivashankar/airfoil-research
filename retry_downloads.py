import urllib.request
import os
import time

# Alternative filenames for failed airfoils
alternatives = {
    'naca0012': 'naca0012.dat',
    'naca6409': 'naca6409.dat', 
    'e196': 'e19600.dat',
    's1021': 's1021.dat',
    's1220': 's1220.dat',
    's1224': 's1224.dat',
    's1225': 's1225.dat',
    's1227': 's1227.dat',
    's1237': 's1237.dat',
    's1238': 's1238.dat',
    's1239': 's1239.dat',
    's1240': 's1240.dat',
    's1241': 's1241.dat',
    'lb572': 'lb572.dat',
    'ag05': 'ag05.dat',
    'ag06': 'ag06.dat',
    'ag07': 'ag07.dat',
}

# Alternative URL patterns to try
url_patterns = [
    "https://m-selig.ae.illinois.edu/ads/coord/{name}.dat",
    "https://m-selig.ae.illinois.edu/ads/coord/{name}a.dat",
    "https://m-selig.ae.illinois.edu/ads/coord/{name}-il.dat",
]

save_dir = "data"
recovered = []
still_failed = []

print("Retrying failed downloads with alternative names...")
print("-" * 40)

for name in alternatives.keys():
    filepath = os.path.join(save_dir, f"{name}.dat")
    
    if os.path.exists(filepath):
        print(f"  Already have {name}")
        recovered.append(name)
        continue
    
    success = False
    for pattern in url_patterns:
        url = pattern.format(name=name)
        try:
            urllib.request.urlretrieve(url, filepath)
            print(f"  Recovered {name} from {url}")
            recovered.append(name)
            success = True
            time.sleep(0.3)
            break
        except:
            continue
    
    if not success:
        print(f"  Could not recover {name}")
        still_failed.append(name)

print("-" * 40)
print(f"Recovered: {len(recovered)}")
print(f"Still failed: {len(still_failed)}")
print(f"Still failed list: {still_failed}")
print(f"\nTotal airfoils in data folder: {len(os.listdir(save_dir))}")