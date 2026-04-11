import sys
import os
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='LOG',
    number=6,
    description='SDIP access membrane - FastAPI routes for document/chunk access',
    patch_type='MINOR',
)
patch.begin()

# Deploy membrane
patch.deploy_file('opt/mythos/sdip/sdip_membrane.py', '/opt/mythos/sdip/sdip_membrane.py')

# Wire into FastAPI main.py
main_path = '/opt/mythos/api/main.py'
with open(main_path, 'r') as f:
    content = f.read()

# Check if already wired
if 'sdip_membrane' not in content:
    # Add import after the last existing route import
    import_line = 'from api.routes.public_files import router as public_files_router'
    sdip_import = 'from api.routes.public_files import router as public_files_router\n\n# SDIP Access Membrane\nsys.path.insert(0, "/opt/mythos/sdip")\nfrom sdip_membrane import router as sdip_router'
    content = content.replace(import_line, sdip_import)

    # Add include_router after the last existing one
    include_line = 'app.include_router(public_files_router)'
    sdip_include = 'app.include_router(public_files_router)\napp.include_router(sdip_router)'
    content = content.replace(include_line, sdip_include)

    with open(main_path, 'w') as f:
        f.write(content)
    print("  ✓ Wired SDIP routes into FastAPI main.py")
else:
    print("  ℹ SDIP routes already wired in main.py")

patch.finish()
