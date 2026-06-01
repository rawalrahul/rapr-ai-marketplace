import os
import zipfile
import json
import io

def get_mit_license(author):
    return f"""MIT License

Copyright (c) 2026 {author}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

def update_catalog(catalog_path):
    print(f"Updating catalog at {catalog_path}...")
    with open(catalog_path, 'r', encoding='utf-8') as f:
        catalog = json.load(f)
    
    updated_count = 0
    for item in catalog.get('items', []):
        if 'license' not in item:
            item['license'] = 'MIT'
            updated_count += 1
        if 'license_scope' not in item:
            item['license_scope'] = 'The listed license applies to the RAPR marketplace wrapper package and does not relicense the upstream project.'
            
    with open(catalog_path, 'w', encoding='utf-8') as f:
        json.dump(catalog, f, indent=2, ensure_ascii=False)
    
    print(f"Updated {updated_count} items in catalog.json with package license metadata.")
    return catalog

def update_packages(pkg_dir, catalog):
    catalog_map = {item['slug']: item for item in catalog.get('items', [])}
    pkgs = [f for f in os.listdir(pkg_dir) if f.endswith('.raprpkg')]
    
    print(f"Auditing and updating {len(pkgs)} packages in {pkg_dir}...")
    
    added_license_count = 0
    already_had_count = 0
    errors = 0
    
    for p in pkgs:
        path = os.path.join(pkg_dir, p)
        
        # Read the zip in memory first
        try:
            with open(path, 'rb') as f:
                zip_data = f.read()
            
            in_mem_zip = io.BytesIO(zip_data)
            has_license = False
            author = "RAPR AI"
            
            with zipfile.ZipFile(in_mem_zip, 'r') as z:
                namelist = z.namelist()
                license_files = [n for n in namelist if 'license' in n.lower()]
                if license_files:
                    has_license = True
                
                # Try to get author from manifest.json
                if 'manifest.json' in namelist:
                    try:
                        manifest = json.loads(z.read('manifest.json').decode('utf-8-sig', errors='ignore'))
                        author = manifest.get('author', author)
                    except Exception as me:
                        # Fallback to catalog author
                        pass
            
            if has_license:
                already_had_count += 1
                continue
                
            # If not has_license, we need to add one.
            # Get author from catalog if manifest was not enough or to match catalog
            slug = p.split('-1.0.0')[0].split('-5.0.7')[0].split('-1.1.0')[0]
            catalog_item = catalog_map.get(slug)
            if not catalog_item:
                for k, v in catalog_map.items():
                    if p.startswith(k + '-'):
                        catalog_item = v
                        break
            if catalog_item:
                author = catalog_item.get('author', author)
            
            # Create a new zip with the license file appended
            out_mem_zip = io.BytesIO()
            with zipfile.ZipFile(out_mem_zip, 'w', zipfile.ZIP_DEFLATED) as zout:
                # Copy all existing files
                with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zin:
                    for item_info in zin.infolist():
                        content = zin.read(item_info.filename)
                        zout.writestr(item_info, content)
                
                # Write the new LICENSE file
                license_text = get_mit_license(author)
                zout.writestr('LICENSE', license_text)
            
            # Write back the new zip data
            with open(path, 'wb') as f:
                f.write(out_mem_zip.getvalue())
                
            added_license_count += 1
            
        except Exception as e:
            print(f"Error processing package {p}: {e}")
            errors += 1
            
    print(f"Update completed. Added LICENSE to {added_license_count} packages. {already_had_count} packages already had a LICENSE file. Errors: {errors}")

if __name__ == "__main__":
    catalog_path = 'public/marketplace/catalog.json'
    pkg_dir = 'public/marketplace/packages'
    
    catalog = update_catalog(catalog_path)
    update_packages(pkg_dir, catalog)
