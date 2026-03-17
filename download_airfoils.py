import urllib.request
import os
import time

# Large list of airfoils from UIUC database
# Selected to cover a wide range of camber, thickness, and airfoil families
print("start")
airfoil_list = [
    # NACA 4-digit series
    'naca0012', 'naca0015', 'naca1408', 'naca1412',
    'naca2408', 'naca2412', 'naca2415', 'naca2418',
    'naca4412', 'naca4415', 'naca4418', 'naca6409',
    # Eppler series (low Reynolds number)
    'e168', 'e174', 'e176', 'e186', 'e196',
    'e207', 'e210', 'e214', 'e216', 'e220',
    'e222', 'e228', 'e230', 'e387', 'e392',
    'e395', 'e398', 'e399',
    # Selig series (low Reynolds number)
    's1020', 's1021', 's1091', 's1210', 's1220',
    's1221', 's1223', 's1224', 's1225', 's1227',
    's1237', 's1238', 's1239', 's1240', 's1241',
    # Wortmann series
    'fx60126', 'fx63137', 'fx66s196', 'fx76mp140',
    # Gottingen series
    'goe225', 'goe226', 'goe227', 'goe228',
    # Clark series
    'clarky',
    # Liebeck series (high lift)
    'lb572',
    # AG series (model aircraft)
    'ag03', 'ag04', 'ag05', 'ag06', 'ag07', 'ag08',
    # MH series (model aircraft)
    'mh60', 'mh61', 'mh62', 'mh78', 'mh114',
    # SD series
    'sd7003', 'sd7032', 'sd7037', 'sd7062',
    'sd7080', 'sd7084',
    # Additional known airfoils
    'naca0009', 'naca0010', 'naca2410', 'naca2414',
    'naca4409', 'naca4410', 'naca4420',
    'e193', 'e195', 'e197', 'e200', 'e203',
    's1046', 's1048', 's2027', 's2048',
    'sd2030', 'sd6060', 'sd6080',
    'goe535', 'goe536', 'goe538',
    'mh32', 'mh42', 'mh43', 'mh44', 'mh45',
    'ag09', 'ag10', 'ag12', 'ag13', 'ag14',
    'fx61163', 'fx62k153',
]

base_url = "https://m-selig.ae.illinois.edu/ads/coord/"
save_dir = "data"
os.makedirs(save_dir, exist_ok=True)

successful = []
failed = []

print(f"Downloading {len(airfoil_list)} airfoils...")
print("-" * 40)

for name in airfoil_list:
    filepath = os.path.join(save_dir, f"{name}.dat")
    
    # Skip if already downloaded
    if os.path.exists(filepath):
        print(f"  Skipping {name} (already exists)")
        successful.append(name)
        continue
    
    url = f"{base_url}{name}.dat"
    
    try:
        urllib.request.urlretrieve(url, filepath)
        print(f"  Downloaded {name}")
        successful.append(name)
        time.sleep(0.3)  # be polite to the server
    except Exception as e:
        print(f"  Failed {name}: {e}")
        failed.append(name)

print("-" * 40)
print(f"Successfully downloaded: {len(successful)}")
print(f"Failed: {len(failed)}")
if failed:
    print(f"Failed airfoils: {failed}")