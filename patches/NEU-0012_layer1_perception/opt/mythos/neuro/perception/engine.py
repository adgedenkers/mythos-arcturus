#!/usr/bin/env python3
"""
Perception Engine — Layer 1 Knowledge Extraction
=================================================
Runs all 9 grid node perception prompts against a message exchange,
extracts knowledge, writes to manifest + knowledge_extractions + Neo4j.

This is the intake cortex. Every message passes through here.
Each node perceives through its own lens. The union of all 9
perceptions IS the total knowledge extracted from the message.

Usage:
    engine = PerceptionEngine()
    results = engine.process(
        exchange_id="abc-123",
        user_message="The electric bill was $180",
        assistant_response="I'll log that...",
        user_uuid="d01f...",
        conversation_id="chat-...",
        grid_scores={"anchor": 45, "beacon": 85, ...},
    )
"""

import os
import json
import re
import logging
import hashlib
import time
from typing import Dict, Any, List, Optional

import requests
from dotenv import load_dotenv

load_dotenv('/opt/mythos/.env')
logger = logging.getLogger('grid.perception')

# Import manifest and knowledge infrastructure
import sys
sys.path.insert(0, '/opt/mythos/neuro')
from grid_manifest import ManifestWriter, VersionRegistry, KnowledgeWriter
from perception import get_perception_prompt, get_all_active_nodes, get_node_domain

OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen3:30b-a3b')

# Minimum grid score to activate a node's perception
ACTIVATION_THRESHOLD = 15

# Significance threshold for Telegram notifications
NOTIFICATION_THRESHOLD = 4


class PerceptionEngine:
    """Runs Layer 1 perception across all 9 grid nodes."""

    def __init__(self):
        self.manifest = ManifestWriter()
        self.registry = VersionRegistry()
        self.knowledge = KnowledgeWriter()

    def process(
        self,
        exchange_id: str,
        user_message: str,
        assistant_response: str,
        user_uuid: str = None,
        conversation_id: str = None,
        grid_scores: Dict[str, int] = None,
    ) -> Dict[str, Any]:
        """
        Run Layer 1 perception on all 9 nodes for this exchange.

        Args:
            exchange_id: Unique exchange identifier
            user_message: The user's message text
            assistant_response: Iris's response text
            user_uuid: User UUID for provenance
            conversation_id: Conversation ID for provenance
            grid_scores: Dict of node→score from the grid scoring pass.
                         If None, all nodes run (no gating).

        Returns:
            Dict with total extractions, per-node results, timing.
        """
        start = time.time()
        nodes = get_all_active_nodes()
        results = {
            'exchange_id': exchange_id,
            'total_extractions': 0,
            'nodes_activated': 0,
            'nodes_skipped': 0,
            'node_results': {},
            'extractions': [],
        }

        combined_input = f"{user_message}\n{assistant_response or ''}"

        for node in nodes:
            score = (grid_scores or {}).get(node, 100)  # Default 100 if no scores (run all)
            version = self.registry.get_version(node, 1)

            if not self.registry.is_active(node, 1):
                self.manifest.record_skip(
                    exchange_id=exchange_id,
                    node=node, layer=1, version=version,
                    conversation_id=conversation_id,
                    user_uuid=user_uuid,
                    activation_score=score,
                    skipped_reason="node-layer disabled in registry",
                )
                results['nodes_skipped'] += 1
                continue

            if score < ACTIVATION_THRESHOLD:
                self.manifest.record_skip(
                    exchange_id=exchange_id,
                    node=node, layer=1, version=version,
                    conversation_id=conversation_id,
                    user_uuid=user_uuid,
                    activation_score=score,
                    skipped_reason=f"score below threshold ({score}/{ACTIVATION_THRESHOLD})",
                )
                results['nodes_skipped'] += 1
                results['node_results'][node] = {'status': 'skipped', 'score': score}
                continue

            # Run perception for this node
            node_result = self._run_node_perception(
                node=node,
                version=version,
                exchange_id=exchange_id,
                user_message=user_message,
                assistant_response=assistant_response,
                user_uuid=user_uuid,
                conversation_id=conversation_id,
                activation_score=score,
                input_content=combined_input,
            )

            results['nodes_activated'] += 1
            results['node_results'][node] = node_result
            results['total_extractions'] += node_result.get('extracted_count', 0)
            results['extractions'].extend(node_result.get('extractions', []))

        results['processing_ms'] = int((time.time() - start) * 1000)

        logger.info(
            f"Perception complete for {exchange_id[:16]}...: "
            f"{results['nodes_activated']} nodes, "
            f"{results['total_extractions']} extractions, "
            f"{results['processing_ms']}ms"
        )

        return results

    def _run_node_perception(
        self,
        node: str,
        version: str,
        exchange_id: str,
        user_message: str,
        assistant_response: str,
        user_uuid: str,
        conversation_id: str,
        activation_score: int,
        input_content: str,
    ) -> Dict[str, Any]:
        """Run a single node's Layer 1 perception prompt."""
        start = time.time()

        prompt = get_perception_prompt(node, user_message, assistant_response)
        if not prompt:
            return {'status': 'error', 'reason': 'no prompt for node'}

        prompt_hash = hashlib.sha256(prompt[:500].encode()).hexdigest()[:16]

        try:
            # Call Ollama
            response = requests.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                },
                timeout=60,
            )

            processing_ms = int((time.time() - start) * 1000)

            if response.status_code != 200:
                logger.error(f"Perception {node} L1: Ollama error {response.status_code}")
                self.manifest.record_activation(
                    exchange_id=exchange_id, node=node, layer=1, version=version,
                    conversation_id=conversation_id, user_uuid=user_uuid,
                    prompt_hash=prompt_hash, activation_score=activation_score,
                    input_content=input_content,
                    output_summary=f"Ollama error: {response.status_code}",
                    processing_ms=processing_ms, model_used=OLLAMA_MODEL,
                )
                return {'status': 'error', 'reason': f'ollama_{response.status_code}'}

            raw_text = response.json().get('response', '')
            extractions = self._parse_extractions(raw_text, node)
            extracted_count = len(extractions)

            # Write manifest entry
            summary_parts = []
            for ext in extractions[:3]:
                summary_parts.append(f"[{ext['type']}] {ext['content'][:40]}")
            output_summary = "; ".join(summary_parts) if summary_parts else "No extractions"

            manifest_id = self.manifest.record_activation(
                exchange_id=exchange_id, node=node, layer=1, version=version,
                conversation_id=conversation_id, user_uuid=user_uuid,
                prompt_hash=prompt_hash, activation_score=activation_score,
                input_content=input_content,
                output_summary=output_summary,
                extracted_count=extracted_count,
                output_json={'extractions': extractions},
                processing_ms=processing_ms, model_used=OLLAMA_MODEL,
            )

            # Write each extraction to knowledge store
            extraction_ids = []
            for ext in extractions:
                eid = self.knowledge.write(
                    exchange_id=exchange_id,
                    manifest_id=manifest_id,
                    node=node,
                    layer=1,
                    version=version,
                    knowledge_type=ext.get('type', 'fact'),
                    content=ext.get('content', ''),
                    subject=ext.get('subject'),
                    domain=ext.get('domain', get_node_domain(node)),
                    significance=ext.get('significance', 1),
                    confidence=ext.get('confidence', 0.8),
                )
                if eid:
                    extraction_ids.append(eid)

            logger.debug(
                f"Perception {node} L1 v{version}: "
                f"{extracted_count} extractions, {processing_ms}ms"
            )

            return {
                'status': 'success',
                'score': activation_score,
                'extracted_count': extracted_count,
                'extractions': extractions,
                'extraction_ids': extraction_ids,
                'processing_ms': processing_ms,
            }

        except requests.Timeout:
            processing_ms = int((time.time() - start) * 1000)
            logger.error(f"Perception {node} L1: timeout")
            self.manifest.record_activation(
                exchange_id=exchange_id, node=node, layer=1, version=version,
                conversation_id=conversation_id, user_uuid=user_uuid,
                prompt_hash=prompt_hash, activation_score=activation_score,
                output_summary="Timeout",
                processing_ms=processing_ms, model_used=OLLAMA_MODEL,
            )
            return {'status': 'timeout', 'processing_ms': processing_ms}

        except Exception as e:
            processing_ms = int((time.time() - start) * 1000)
            logger.error(f"Perception {node} L1 error: {e}")
            return {'status': 'error', 'reason': str(e), 'processing_ms': processing_ms}

    def _parse_extractions(self, raw_text: str, node: str) -> List[Dict]:
        """
        Parse LLM response into extraction dicts.
        Handles both clean JSON and JSON-in-thinking-tags (qwen3 style).
        """
        # Strip thinking tags if present (qwen3 outputs <think>...</think> before JSON)
        text = raw_text
        think_pattern = re.compile(r'<think>.*?</think>', re.DOTALL)
        text = think_pattern.sub('', text).strip()

        # Try to find JSON in the response
        # First try: direct parse
        try:
            parsed = json.loads(text)
            return self._validate_extractions(parsed.get('extractions', []), node)
        except json.JSONDecodeError:
            pass

        # Second try: find JSON block in text
        json_match = re.search(r'\{[^{}]*"extractions"[^{}]*\[.*?\]\s*\}', text, re.DOTALL)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                return self._validate_extractions(parsed.get('extractions', []), node)
            except json.JSONDecodeError:
                pass

        # Third try: find any JSON array
        array_match = re.search(r'\[.*?\]', text, re.DOTALL)
        if array_match:
            try:
                parsed = json.loads(array_match.group())
                if isinstance(parsed, list):
                    return self._validate_extractions(parsed, node)
            except json.JSONDecodeError:
                pass

        # Give up
        if text and len(text) > 10:
            logger.warning(f"Perception {node}: could not parse JSON from response ({len(text)} chars)")
        return []

    def _validate_extractions(self, extractions: list, node: str) -> List[Dict]:
        """Validate and clean extraction dicts."""
        valid = []
        valid_types = {'fact', 'preference', 'observation', 'directive'}

        for ext in extractions:
            if not isinstance(ext, dict):
                continue
            if not ext.get('content'):
                continue

            # Normalize type
            ext_type = str(ext.get('type', 'fact')).lower().strip()
            if ext_type not in valid_types:
                ext_type = 'fact'

            # Clamp significance
            try:
                sig = int(ext.get('significance', 1))
                sig = max(1, min(5, sig))
            except (ValueError, TypeError):
                sig = 1

            # Clamp confidence
            try:
                conf = float(ext.get('confidence', 0.8))
                conf = max(0.0, min(1.0, conf))
            except (ValueError, TypeError):
                conf = 0.8

            valid.append({
                'type': ext_type,
                'subject': ext.get('subject') or None,
                'content': str(ext['content']).strip(),
                'domain': ext.get('domain', get_node_domain(node)),
                'significance': sig,
                'confidence': conf,
            })

        return valid

    def close(self):
        """Clean up resources."""
        self.knowledge.close()
