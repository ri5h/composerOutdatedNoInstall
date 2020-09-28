# composerOutdatedNoInstall
Get a list of outdated packages based on version constraints in composer.json

The main motivation behind the script was to find a way trying to run `composer outdate --direct` without running `composer install`

**How to run**
1. Make sure all above packages are installed
2. python3 outdated.py --path <repo-relative-path>


**outdated.py** 
1. Looks into composer.json for constraints
2. Looks into composer.lock for current version
3. Uses packagist to find latest version under those constraints
4. Puts it in a dictionary




Note: *This is not meant for production, but can act as a starting point.*
