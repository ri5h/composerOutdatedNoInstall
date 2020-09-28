import json
import unicodedata
import sys
import argparse
import requests
import semantic_version as semver
import re

################## How To Run #########################
## 1. Make sure all above packages are installed
## 2. python3 test.py --path in
#######################################################


# Which directory have composer.json and composer.lock
parser = argparse.ArgumentParser()
parser.add_argument('--path', help='Relative directory that contains the composer files')
cdir = parser.parse_args().path

# Reads composer.json for constraints
reqPack = {}
with open(cdir +'/composer.json') as json_file:
    data = json.loads(json.dumps(json.load(json_file)))
    for package in data['require']:
        packageStr = str(package)
        if package == 'php':
            continue
        if package.startswith('ext-'):
            continue
        if package.startswith('internations'):
            continue
        reqPack[packageStr] = str(data['require'][package])

# Reads composer.lock for installed versions
inPack = {}
with open(cdir + '/composer.lock') as json_file:
    lockdata = json.loads(json.dumps(json.load(json_file)))
    for package in lockdata['packages']:
        for key in package:
            if str(key) == 'name' and str(package[key]) in reqPack:
                inPack[str(package['name'])] = str(package['version'])

# Read the latest version available from packagist
finalRes = []
for package in reqPack:
    finalPackageResult = {
        'name': package
    }

    # Find current installed version
    try:
        cur_ver = semver.Version.coerce(inPack[package])
    except ValueError:
        if re.search("^v[0-9].*$", inPack[package]):
            cur_ver = semver.Version.coerce(inPack[package][1:])
        else:
            finalPackageResult['msg'] = 'current installed version ' + inPack[package] + ' unreadable'
            finalPackageResult['status'] = 'failed'
            finalRes.append(finalPackageResult)
            continue

    # Get version constraints
    try:
        versionSpec = semver.NpmSpec(reqPack[package])
    except ValueError:
        finalPackageResult['msg'] = 'cannot understand constraint ' + reqPack[package]
        finalPackageResult['status'] = 'failed'
        finalRes.append(finalPackageResult)
        continue

    # Try to get info from packagist
    url = 'https://repo.packagist.org/packages/' + package + '.json'
    jsonMetaRes = requests.get(url)
    if jsonMetaRes.status_code != 200:
        finalPackageResult['msg'] = 'packagist error for url: ' + url
        finalPackageResult['status'] = 'failed'
        finalRes.append(finalPackageResult)
        continue

    jsonMeta = jsonMetaRes.json()['package']


    # Find Best version for given constraints
    cur_best = semver.Version('0.0.0')
    for versionStr in jsonMeta['versions']:
        try:
            version = semver.Version(versionStr)
            if version in versionSpec and version > cur_best:
                cur_best = version
        except ValueError: continue

    # Add to list if better version is available
    if cur_best > cur_ver:
        finalRes.append({
            'package':package,
            'constraint':reqPack[package],
            'current':inPack[package],
            'recommended':str(cur_best),
            'status': 'success'
        })
    else:
        finalPackageResult['msg'] = 'Already best version '
        finalPackageResult['status'] = 'meh'
        finalRes.append(finalPackageResult)

meh = []
success = []
fail = []

for result in finalRes:
    if result['status'] == 'success': success.append(result)
    elif result['status'] == 'failed': fail.append(result)
    else: meh.append(result)

print({
    'behind' : success,
    'unknown' : fail,
    'latest' : meh
})
