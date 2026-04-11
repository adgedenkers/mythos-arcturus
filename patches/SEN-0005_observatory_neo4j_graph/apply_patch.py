import sys
import os
import subprocess
sys.path.insert(0, '/opt/mythos/patches/scripts')
from patch_base import PatchBase

patch = PatchBase(
    stream='SEN',
    number=5,
    description='observatory neo4j graph builder',
    patch_type='MINOR',
)
patch.begin()

# Deploy graph builder
patch.deploy_file(
    'opt/mythos/observatory/graph/observatory_graph.py',
    '/opt/mythos/observatory/graph/observatory_graph.py'
)

# Run SQL migration
patch.run_sql('opt/mythos/migrations/SEN-0005_observatory_correlations.sql')

# Install systemd service
patch_dir = os.path.dirname(os.path.abspath(__file__))
service_src = os.path.join(patch_dir, 'mythos-obs-graph.service')
subprocess.run(['sudo', 'cp', service_src, '/etc/systemd/system/mythos-obs-graph.service'], check=True)
subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
subprocess.run(['sudo', 'systemctl', 'enable', 'mythos-obs-graph.service'], check=True)

patch.restart_service('mythos-obs-graph.service')

patch.finish()
print("SEN-0005 complete — observatory Neo4j graph builder deployed")
print("Service: mythos-obs-graph.service")
print("3-day backfill running — check: journalctl -u mythos-obs-graph -f")
