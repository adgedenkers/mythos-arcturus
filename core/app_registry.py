#!/usr/bin/env python3
"""
Neo4j Application Registry
===========================
Manages application ownership of Neo4j node labels and relationship types.

Every application that writes to Neo4j MUST register itself here.
This module provides:
  - Registration of apps and their owned labels/relationships
  - Lookup: "which app owns this label?"
  - Audit: "how many nodes does this app own?"
  - Cleanup: "generate delete queries for an app's data"

Usage:
    from core.app_registry import AppRegistry

    registry = AppRegistry(neo4j_driver)
    
    # Check who owns a label
    owner = registry.get_label_owner('GenPerson')
    # => 'genealogy'
    
    # Get all apps and their node counts
    audit = registry.audit_all()
    # => [{'app_id': 'genealogy', 'labels': [...], 'node_count': 3872}, ...]
    
    # Get cleanup query for an app
    query = registry.get_cleanup_query('genealogy')
    # => 'MATCH (n) WHERE n:GenPerson OR n:GenPlace ... DETACH DELETE n'
"""

import os
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


# ============================================================================
# CANONICAL APP DEFINITIONS
# ============================================================================
# This is the single source of truth for what apps exist and what they own.
# APP_REGISTRY.md is generated from this. Neo4j :AppRegistry nodes mirror this.
# If you add a new app, add it HERE first.
# ============================================================================

APP_DEFINITIONS = {
    'genealogy': {
        'display_name': 'Genealogical Research Data',
        'description': 'GEDCOM-imported family tree data from genealogical research',
        'source_files': ['/opt/mythos/assistants/db_manager.py'],
        'owned_labels': ['GenPerson', 'GenPlace', 'GenFamily', 'GenSurname'],
        'owned_relationships': [
            'PARENT_OF', 'CHILD_OF', 'BORN_IN', 'DIED_IN',
            'MARRIED_TO', 'MARRIED_IN', 'BELONGS_TO_FAMILY', 'HAS_SURNAME'
        ],
        'protected': False,
    },
    'grid_worker': {
        'display_name': 'Arcturian Grid Processing',
        'description': '9-node consciousness grid analysis and dimensional output',
        'source_files': ['/opt/mythos/workers/grid_worker.py'],
        'owned_labels': [
            'GridNode', 'Theme',
            # Grid dimension outputs
            'AnchorOutput', 'EchoOutput', 'BeaconOutput', 'SynthOutput',
            'NexusOutput', 'MirrorOutput', 'GlyphOutput', 'HarmoniaOutput',
            'GatewayOutput', 'GridMasterOutput', 'GatewaySafetyCheck',
            # Grid sub-nodes (created by grid analysis)
            'Value', 'Emotion', 'EmotionalNeed', 'Symbol', 'Relationship',
            'Event', 'Direction', 'Location', 'Integration', 'IntegrationGap',
            'Commitment', 'DecisionGate', 'Shadow', 'Wound', 'Archetype',
            'SacredObject', 'Role', 'Threshold', 'Portal', 'Dream',
            'Defense', 'PotentialTrigger', 'MagicalAct', 'SupportGap',
            'Transmission', 'Activation', 'Rupture', 'Repair',
            'CommunicationGap', 'BoundaryNeeded', 'CapacityAssessment',
            'ConvergencePoint', 'Boundary', 'FinancialCondition',
            'PlannedExpense', 'Manifestation', 'ValueTension',
            'RitualElement', 'RitualGap', 'Concern',
        ],
        'owned_relationships': [
            'HAS_THEME', 'ACTIVATED', 'DISCUSSED', 'INVOLVES',
            'ANCHOR_OBJECT', 'ANCHOR_LOCATION', 'ANCHOR_CONCERN', 'ANCHOR_ASSESSMENT',
            'ECHO_EVENT', 'ECHO_PATTERN', 'ECHO_IDENTITY', 'ECHO_ASSESSMENT',
            'BEACON_VALUE', 'BEACON_DIRECTION', 'BEACON_FINANCIAL', 'BEACON_EXPENSE',
            'BEACON_MANIFESTED', 'BEACON_TENSION', 'BEACON_ASSESSMENT',
            'SYNTH_SYSTEM', 'SYNTH_INTEGRATION', 'SYNTH_GAP',
            'SYNTH_TOOL_NEEDED', 'SYNTH_TOOL_USED', 'SYNTH_ASSESSMENT',
            'NEXUS_COMMITMENT', 'NEXUS_GATE', 'NEXUS_BOUNDARY_NEEDED',
            'NEXUS_CAPACITY', 'NEXUS_CONVERGENCE', 'NEXUS_BOUNDARY', 'NEXUS_ASSESSMENT',
            'MIRROR_EMOTION', 'MIRROR_NEED', 'MIRROR_SHADOW', 'MIRROR_WOUND',
            'MIRROR_DEFENSE', 'MIRROR_TRIGGER_POTENTIAL', 'MIRROR_ASSESSMENT',
            'GLYPH_SYMBOL', 'GLYPH_ARCHETYPE', 'GLYPH_SACRED_OBJECT',
            'GLYPH_MAGIC', 'GLYPH_RITUAL', 'GLYPH_RITUAL_GAP', 'GLYPH_ASSESSMENT',
            'HARMONIA_RELATIONSHIP', 'HARMONIA_ROLE', 'HARMONIA_SUPPORT_GAP',
            'HARMONIA_RUPTURE', 'HARMONIA_REPAIR', 'HARMONIA_COMM_GAP', 'HARMONIA_ASSESSMENT',
            'GATEWAY_THRESHOLD', 'GATEWAY_PORTAL', 'GATEWAY_TRANSMISSION',
            'GATEWAY_ACTIVATION', 'GATEWAY_DREAM', 'GATEWAY_ASSESSMENT',
            'SAFETY_CHECK', 'GRID_MASTER_OUTPUT',
        ],
        'protected': False,
    },
    'ontology': {
        'display_name': 'Ontology & Concept System',
        'description': 'Ontological vocabulary terms and abstract concepts',
        'source_files': [
            '/opt/mythos/core/ontology_seed.py',
            '/opt/mythos/api/routes/ontology.py',
        ],
        'owned_labels': ['OntologyTerm', 'Concept'],
        'owned_relationships': [
            'RELATED_TO', 'DESCRIBES', 'DEFINES', 'CONTAINS', 'PART_OF', 'REFERS_TO'
        ],
        'protected': False,
    },
    'conversation_logger': {
        'display_name': 'Conversation & Exchange Tracking',
        'description': 'Logs conversations and message exchanges to the graph',
        'source_files': [
            '/opt/mythos/llm_diagnostics/src/conversation_logger.py',
        ],
        'owned_labels': ['Exchange', 'Conversation'],
        'owned_relationships': [
            'HAD_CONVERSATION', 'INCLUDES', 'FOLLOWED_BY', 'MENTIONED'
        ],
        'protected': False,
    },
    'people_manager': {
        'display_name': 'People & Contact Management',
        'description': 'Living people, contacts, known individuals (not genealogy)',
        'source_files': [
            '/opt/mythos/api/routes/people.py',
            '/opt/mythos/api/routes/rolodex.py',
        ],
        'owned_labels': ['Person', 'PersonOwner'],
        'owned_relationships': [
            'INVOLVES', 'MENTIONED', 'IDENTITY_OF', 'BETWEEN'
        ],
        'protected': False,
    },
    'system_monitor': {
        'display_name': 'System Infrastructure Mapping',
        'description': 'Maps Arcturus system infrastructure into the graph',
        'source_files': [
            '/opt/mythos/graph_logging/src/system_monitor.py',
            '/opt/mythos/graph_logging/src/event_logger.py',
        ],
        'owned_labels': [
            'Process', 'System', 'Service', 'File', 'Directory',
            'Function', 'Tool', 'TestMachine', 'TestRun'
        ],
        'owned_relationships': [
            'RUNS', 'RUNS_SERVICE', 'CONTAINS', 'CALLS', 'READS_CONFIG',
            'IMPLEMENTS', 'IMPORTS', 'USES', 'HAD_TEST_RUN', 'TESTED_BY',
            'CONNECTS_TO'
        ],
        'protected': False,
    },
    'astrology': {
        'display_name': 'Natal Charts & Numerology',
        'description': 'Astrological charts, numerology, Soul Stratigraphy',
        'source_files': [
            '/opt/mythos/patches/astrology_system/charts/chart_calculator.py',
        ],
        'owned_labels': ['Chart', 'Numerology', 'SoulStratigraphy'],
        'owned_relationships': [
            'HAS_CHART', 'HAS_NUMEROLOGY', 'HAS_STRATIGRAPHY'
        ],
        'protected': False,
    },
    'spiritual_core': {
        'display_name': 'Soul Identity & Incarnation Registry',
        'description': 'Sacred core — souls, incarnations, lineages. DO NOT DELETE without explicit instruction.',
        'source_files': ['/opt/mythos/assistants/db_manager.py'],
        'owned_labels': ['Soul', 'Incarnation', 'Lineage'],
        'owned_relationships': [
            'CURRENTLY_EMBODIED_AS', 'INCARNATED_AS', 'MANIFESTED_AS',
            'HAS_SOUL', 'EMBODIES', 'ACTIVATED_BY', 'CARRIES_LINEAGE'
        ],
        'protected': True,
    },
    'research_framework': {
        'display_name': 'Research & Analysis Engine',
        'description': 'Entity extraction and pattern analysis from research sessions',
        'source_files': [
            '/opt/mythos/core/research_router.py',
            '/opt/mythos/core/convergence.py',
            '/opt/mythos/core/node_executor.py',
        ],
        'owned_labels': ['Entity', 'Pattern', 'IdentityThread', 'Object', 'Quote'],
        'owned_relationships': [
            'INVOLVES', 'SYNTHESIZES', 'ASPECT_OF', 'PRECEDES',
            'FEEDS_INTO', 'MOTIVATES', 'LEADS_TO', 'ADDRESSES'
        ],
        'protected': False,
    },
}


class AppRegistry:
    """Query and manage the Neo4j application registry."""

    def __init__(self, neo4j_driver=None):
        self.driver = neo4j_driver
        # Build reverse lookup: label → app_id
        self._label_to_app = {}
        for app_id, defn in APP_DEFINITIONS.items():
            for label in defn['owned_labels']:
                self._label_to_app[label] = app_id

    def get_label_owner(self, label: str) -> Optional[str]:
        """Which app owns this label? Returns app_id or None."""
        return self._label_to_app.get(label)

    def get_app_labels(self, app_id: str) -> list:
        """Get all labels owned by an app."""
        defn = APP_DEFINITIONS.get(app_id)
        return defn['owned_labels'] if defn else []

    def get_app_relationships(self, app_id: str) -> list:
        """Get all relationship types owned by an app."""
        defn = APP_DEFINITIONS.get(app_id)
        return defn['owned_relationships'] if defn else []

    def is_protected(self, app_id: str) -> bool:
        """Is this app marked as protected (requires explicit confirmation to delete)?"""
        defn = APP_DEFINITIONS.get(app_id)
        return defn.get('protected', False) if defn else False

    def list_apps(self) -> list:
        """List all registered app IDs."""
        return list(APP_DEFINITIONS.keys())

    def get_app_info(self, app_id: str) -> Optional[dict]:
        """Get full definition for an app."""
        return APP_DEFINITIONS.get(app_id)

    def find_orphan_labels(self) -> list:
        """
        Find labels in Neo4j that aren't registered to any app.
        Requires neo4j_driver.
        """
        if not self.driver:
            raise RuntimeError("Neo4j driver required for orphan detection")

        registered = set(self._label_to_app.keys())
        registered.add('AppRegistry')  # Self-referential

        with self.driver.session() as session:
            result = session.run(
                "MATCH (n) "
                "WITH labels(n)[0] AS label, count(*) AS cnt "
                "RETURN label, cnt ORDER BY cnt DESC"
            )
            orphans = []
            for record in result:
                label = record['label']
                if label and label not in registered:
                    orphans.append({
                        'label': label,
                        'count': record['cnt'],
                    })
            return orphans

    def audit_app(self, app_id: str) -> Optional[dict]:
        """
        Count all nodes belonging to an app.
        Requires neo4j_driver.
        """
        if not self.driver:
            raise RuntimeError("Neo4j driver required for audit")

        defn = APP_DEFINITIONS.get(app_id)
        if not defn:
            return None

        labels = defn['owned_labels']
        if not labels:
            return {'app_id': app_id, 'labels': {}, 'total_nodes': 0}

        # Build query
        conditions = ' OR '.join(f'n:{label}' for label in labels)
        query = (
            f"MATCH (n) WHERE {conditions} "
            f"RETURN labels(n)[0] AS label, count(*) AS cnt "
            f"ORDER BY cnt DESC"
        )

        with self.driver.session() as session:
            result = session.run(query)
            label_counts = {}
            total = 0
            for record in result:
                label_counts[record['label']] = record['cnt']
                total += record['cnt']

            return {
                'app_id': app_id,
                'display_name': defn['display_name'],
                'protected': defn.get('protected', False),
                'labels': label_counts,
                'total_nodes': total,
            }

    def audit_all(self) -> list:
        """Audit all registered apps. Requires neo4j_driver."""
        results = []
        for app_id in APP_DEFINITIONS:
            audit = self.audit_app(app_id)
            if audit:
                results.append(audit)
        results.sort(key=lambda x: x['total_nodes'], reverse=True)
        return results

    def get_cleanup_query(self, app_id: str, dry_run: bool = True) -> Optional[str]:
        """
        Generate a Cypher query to count or delete all nodes for an app.
        dry_run=True returns a COUNT query. dry_run=False returns a DELETE query.
        """
        defn = APP_DEFINITIONS.get(app_id)
        if not defn:
            return None

        if defn.get('protected') and not dry_run:
            return f"// ⚠️ App '{app_id}' is PROTECTED. Delete manually with explicit confirmation."

        labels = defn['owned_labels']
        if not labels:
            return None

        conditions = ' OR '.join(f'n:{label}' for label in labels)

        if dry_run:
            return (
                f"// Count nodes for app: {app_id}\n"
                f"MATCH (n) WHERE {conditions}\n"
                f"RETURN labels(n)[0] AS label, count(*) AS count\n"
                f"ORDER BY count DESC"
            )
        else:
            return (
                f"// ⚠️ DELETE all nodes for app: {app_id}\n"
                f"// This will remove {', '.join(labels)} and all their relationships\n"
                f"MATCH (n) WHERE {conditions}\n"
                f"DETACH DELETE n"
            )

    def seed_neo4j(self):
        """
        Create/update :AppRegistry nodes in Neo4j to mirror APP_DEFINITIONS.
        Idempotent — uses MERGE on app_id.
        """
        if not self.driver:
            raise RuntimeError("Neo4j driver required for seeding")

        with self.driver.session() as session:
            for app_id, defn in APP_DEFINITIONS.items():
                session.run(
                    """
                    MERGE (a:AppRegistry {app_id: $app_id})
                    SET a.display_name = $display_name,
                        a.description = $description,
                        a.source_files = $source_files,
                        a.owned_labels = $owned_labels,
                        a.owned_relationships = $owned_relationships,
                        a.protected = $protected,
                        a.updated_at = datetime()
                    """,
                    app_id=app_id,
                    display_name=defn['display_name'],
                    description=defn['description'],
                    source_files=defn['source_files'],
                    owned_labels=defn['owned_labels'],
                    owned_relationships=defn['owned_relationships'],
                    protected=defn.get('protected', False),
                )
            logger.info(f"Seeded {len(APP_DEFINITIONS)} AppRegistry nodes in Neo4j")

    def format_audit_report(self, include_orphans: bool = True) -> str:
        """Generate a formatted text report of the full registry audit."""
        lines = []
        lines.append("═══ NEO4J APPLICATION REGISTRY AUDIT ═══\n")

        audits = self.audit_all()
        grand_total = sum(a['total_nodes'] for a in audits)

        for audit in audits:
            protected = " 🔒" if audit['protected'] else ""
            lines.append(
                f"📦 {audit['display_name']}{protected}  "
                f"[{audit['app_id']}]  —  {audit['total_nodes']:,} nodes"
            )
            for label, count in sorted(audit['labels'].items(), key=lambda x: -x[1]):
                lines.append(f"   • {label}: {count:,}")
            lines.append("")

        lines.append(f"═══ TOTAL REGISTERED: {grand_total:,} nodes ═══\n")

        if include_orphans:
            orphans = self.find_orphan_labels()
            if orphans:
                orphan_total = sum(o['count'] for o in orphans)
                lines.append(f"⚠️  ORPHAN LABELS ({orphan_total:,} nodes):")
                for o in orphans:
                    lines.append(f"   • {o['label']}: {o['count']:,}")
                lines.append("")
            else:
                lines.append("✅ No orphan labels found.\n")

        return '\n'.join(lines)
