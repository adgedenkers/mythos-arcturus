import os
print("✓ Test patch executed")
print(f"  Running as uid: {os.getuid()}")
print(f"  Effective user: root" if os.getuid() == 0 else f"  Effective user: {os.getenv('USER')}")
