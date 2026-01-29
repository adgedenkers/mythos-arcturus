// Triad Memory System - Neo4j Schema
// Run these to set up constraints and indexes

// ============================================
// CONSTRAINTS (ensure uniqueness)
// ============================================

CREATE CONSTRAINT triad_conversation_id IF NOT EXISTS
FOR (c:TriadConversation) REQUIRE c.id IS UNIQUE;

CREATE CONSTRAINT triad_pattern_signature IF NOT EXISTS
FOR (p:TriadPattern) REQUIRE p.signature IS UNIQUE;

CREATE CONSTRAINT triad_domain_name IF NOT EXISTS
FOR (d:TriadDomain) REQUIRE d.name IS UNIQUE;

CREATE CONSTRAINT triad_seed_id IF NOT EXISTS
FOR (s:TriadSeed) REQUIRE s.id IS UNIQUE;

// ============================================
// INDEXES (for query performance)
// ============================================

CREATE INDEX triad_conv_timestamp IF NOT EXISTS
FOR (c:TriadConversation) ON (c.timestamp);

CREATE INDEX triad_conv_spiral IF NOT EXISTS
FOR (c:TriadConversation) ON (c.spiral_cycle, c.spiral_day);

CREATE INDEX triad_pattern_domain IF NOT EXISTS
FOR (p:TriadPattern) ON (p.domain);

// ============================================
// INITIAL DOMAIN NODES
// ============================================

MERGE (d:TriadDomain {name: 'spiritual'})
MERGE (d:TriadDomain {name: 'technical'})
MERGE (d:TriadDomain {name: 'relational'})
MERGE (d:TriadDomain {name: 'financial'})
MERGE (d:TriadDomain {name: 'ancestral'})
MERGE (d:TriadDomain {name: 'somatic'})
MERGE (d:TriadDomain {name: 'creative'})
MERGE (d:TriadDomain {name: 'planetary'});

// ============================================
// EXAMPLE RELATIONSHIP QUERIES
// (For reference - not executed on setup)
// ============================================

// Link conversation to pattern:
// MATCH (c:TriadConversation {id: $conv_id})
// MERGE (p:TriadPattern {signature: $pattern_signature})
// MERGE (c)-[:ACTIVATES {weight: $weight}]->(p)

// Link conversation to domains:
// MATCH (c:TriadConversation {id: $conv_id})
// MATCH (d:TriadDomain {name: $domain_name})
// MERGE (c)-[:TOUCHES]->(d)

// Pattern echoes (conversation echoes earlier pattern work):
// MATCH (c1:TriadConversation {id: $conv_id})
// MATCH (c2:TriadConversation {id: $earlier_id})
// MERGE (c1)-[:ECHOES {depth: $spiral_depth}]->(c2)

// Resolution chain:
// MATCH (c1:TriadConversation {id: $conv_id})
// MATCH (c2:TriadConversation {id: $resolved_id})
// MERGE (c1)-[:RESOLVES]->(c2)

// Seed planted -> Seed bloomed:
// MATCH (c1:TriadConversation {id: $planting_conv})
// MERGE (s:TriadSeed {id: $seed_id, name: $seed_name, planted_at: $timestamp})
// MERGE (c1)-[:PLANTS]->(s)
//
// Later when seed blooms:
// MATCH (s:TriadSeed {id: $seed_id})
// MATCH (c2:TriadConversation {id: $blooming_conv})
// MERGE (c2)-[:BLOOMS]->(s)

// Convergence tracking:
// MATCH (c1:TriadConversation {id: $conv_id})
// MATCH (c2:TriadConversation {id: $converging_with})
// MERGE (c1)-[:CONVERGES_WITH {strength: $strength}]->(c2)

// ============================================
// USEFUL QUERY PATTERNS
// ============================================

// Find repeating patterns without resolution:
// MATCH (c:TriadConversation)-[:ACTIVATES]->(p:TriadPattern)
// WHERE NOT EXISTS { (c)-[:RESOLVES]->() }
// WITH p, count(c) as activations
// WHERE activations > 2
// RETURN p.signature, activations
// ORDER BY activations DESC

// Find seeds ready to bloom (planted > 30 days ago, not yet bloomed):
// MATCH (c:TriadConversation)-[:PLANTS]->(s:TriadSeed)
// WHERE NOT EXISTS { ()-[:BLOOMS]->(s) }
// AND s.planted_at < datetime() - duration('P30D')
// RETURN s.name, s.planted_at, c.id

// Trace a pattern's resolution journey:
// MATCH path = (start:TriadConversation)-[:ECHOES|RESOLVES*1..10]->(end:TriadConversation)
// WHERE start.id = $conv_id
// RETURN path

// Domain heat map (which domains are most active recently):
// MATCH (c:TriadConversation)-[:TOUCHES]->(d:TriadDomain)
// WHERE c.timestamp > datetime() - duration('P30D')
// RETURN d.name, count(c) as touches
// ORDER BY touches DESC
