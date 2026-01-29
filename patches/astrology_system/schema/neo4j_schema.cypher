// ============================================================================
// MYTHOS ASTROLOGY SYSTEM - Neo4j Schema
// ============================================================================
// This schema stores the MEANINGS: relationships, interpretations, patterns.
// Precise positional data lives in PostgreSQL.
// Bridge key: chart_id (UUID) exists in both systems.
// ============================================================================

// ============================================================================
// CONSTRAINTS & INDEXES
// ============================================================================

// Zodiac Signs
CREATE CONSTRAINT sign_name IF NOT EXISTS FOR (s:Sign) REQUIRE s.name IS UNIQUE;

// Celestial Bodies
CREATE CONSTRAINT body_name IF NOT EXISTS FOR (b:Body) REQUIRE b.name IS UNIQUE;

// Houses
CREATE CONSTRAINT house_number IF NOT EXISTS FOR (h:House) REQUIRE h.number IS UNIQUE;

// Aspects
CREATE CONSTRAINT aspect_name IF NOT EXISTS FOR (a:AspectType) REQUIRE a.name IS UNIQUE;

// Charts
CREATE CONSTRAINT chart_id IF NOT EXISTS FOR (c:Chart) REQUIRE c.chart_id IS UNIQUE;

// Elements
CREATE CONSTRAINT element_name IF NOT EXISTS FOR (e:Element) REQUIRE e.name IS UNIQUE;

// Modalities
CREATE CONSTRAINT modality_name IF NOT EXISTS FOR (m:Modality) REQUIRE m.name IS UNIQUE;

// Indexes for performance
CREATE INDEX chart_entity IF NOT EXISTS FOR (c:Chart) ON (c.entity_name);
CREATE INDEX placement_body IF NOT EXISTS FOR (p:Placement) ON (p.body_name);

// ============================================================================
// ELEMENTS
// ============================================================================

MERGE (e:Element {name: 'Fire'})
SET e.keywords = ['action', 'will', 'spirit', 'inspiration', 'enthusiasm', 'courage'],
    e.energy = 'yang',
    e.nature = 'hot and dry',
    e.temperament = 'choleric',
    e.theme = 'identity and self-expression';

MERGE (e:Element {name: 'Earth'})
SET e.keywords = ['material', 'practical', 'grounded', 'sensual', 'productive', 'stable'],
    e.energy = 'yin',
    e.nature = 'cold and dry',
    e.temperament = 'melancholic',
    e.theme = 'resources and manifestation';

MERGE (e:Element {name: 'Air'})
SET e.keywords = ['intellect', 'communication', 'social', 'ideas', 'connection', 'thought'],
    e.energy = 'yang',
    e.nature = 'hot and wet',
    e.temperament = 'sanguine',
    e.theme = 'relationship and exchange';

MERGE (e:Element {name: 'Water'})
SET e.keywords = ['emotion', 'intuition', 'soul', 'feeling', 'healing', 'depth'],
    e.energy = 'yin',
    e.nature = 'cold and wet',
    e.temperament = 'phlegmatic',
    e.theme = 'endings and transformation';

// ============================================================================
// MODALITIES
// ============================================================================

MERGE (m:Modality {name: 'Cardinal'})
SET m.keywords = ['initiating', 'leading', 'beginning', 'action', 'pioneering'],
    m.season_position = 'beginning',
    m.theme = 'starting new cycles';

MERGE (m:Modality {name: 'Fixed'})
SET m.keywords = ['stabilizing', 'persisting', 'sustaining', 'determined', 'stubborn'],
    m.season_position = 'middle',
    m.theme = 'maintaining and building';

MERGE (m:Modality {name: 'Mutable'})
SET m.keywords = ['adapting', 'changing', 'flexible', 'transitional', 'versatile'],
    m.season_position = 'ending',
    m.theme = 'transforming and releasing';

// ============================================================================
// ZODIAC SIGNS
// ============================================================================

// ARIES
MERGE (s:Sign {name: 'Aries'})
SET s.symbol = '♈',
    s.glyph = 'Ram',
    s.degree_start = 0,
    s.degree_end = 30,
    s.polarity = 'yang',
    s.keywords = ['initiative', 'courage', 'independence', 'pioneering', 'assertive', 'competitive'],
    s.shadow = ['impatience', 'aggression', 'selfishness', 'recklessness'],
    s.theme = 'I AM - the birth of self-awareness and individual identity',
    s.body_parts = ['head', 'face', 'brain', 'eyes'],
    s.tarot = 'The Emperor',
    s.season = 'early spring',
    s.color = 'red';

// TAURUS  
MERGE (s:Sign {name: 'Taurus'})
SET s.symbol = '♉',
    s.glyph = 'Bull',
    s.degree_start = 30,
    s.degree_end = 60,
    s.polarity = 'yin',
    s.keywords = ['stability', 'sensuality', 'patience', 'determination', 'values', 'pleasure'],
    s.shadow = ['stubbornness', 'possessiveness', 'materialism', 'resistance to change'],
    s.theme = 'I HAVE - embodiment, resources, and physical security',
    s.body_parts = ['neck', 'throat', 'thyroid', 'vocal cords'],
    s.tarot = 'The Hierophant',
    s.season = 'mid spring',
    s.color = 'green';

// GEMINI
MERGE (s:Sign {name: 'Gemini'})
SET s.symbol = '♊',
    s.glyph = 'Twins',
    s.degree_start = 60,
    s.degree_end = 90,
    s.polarity = 'yang',
    s.keywords = ['communication', 'curiosity', 'adaptability', 'wit', 'duality', 'learning'],
    s.shadow = ['superficiality', 'inconsistency', 'nervousness', 'gossip'],
    s.theme = 'I THINK - mental exploration and information exchange',
    s.body_parts = ['arms', 'hands', 'lungs', 'nervous system'],
    s.tarot = 'The Lovers',
    s.season = 'late spring',
    s.color = 'yellow';

// CANCER
MERGE (s:Sign {name: 'Cancer'})
SET s.symbol = '♋',
    s.glyph = 'Crab',
    s.degree_start = 90,
    s.degree_end = 120,
    s.polarity = 'yin',
    s.keywords = ['nurturing', 'protective', 'emotional', 'intuitive', 'home', 'family'],
    s.shadow = ['moodiness', 'clinginess', 'oversensitivity', 'manipulation'],
    s.theme = 'I FEEL - emotional foundations and belonging',
    s.body_parts = ['chest', 'breasts', 'stomach', 'womb'],
    s.tarot = 'The Chariot',
    s.season = 'early summer',
    s.color = 'silver';

// LEO
MERGE (s:Sign {name: 'Leo'})
SET s.symbol = '♌',
    s.glyph = 'Lion',
    s.degree_start = 120,
    s.degree_end = 150,
    s.polarity = 'yang',
    s.keywords = ['creativity', 'leadership', 'generosity', 'drama', 'self-expression', 'heart'],
    s.shadow = ['arrogance', 'vanity', 'domination', 'attention-seeking'],
    s.theme = 'I CREATE - radiant self-expression and creative power',
    s.body_parts = ['heart', 'spine', 'upper back'],
    s.tarot = 'Strength',
    s.season = 'mid summer',
    s.color = 'gold';

// VIRGO
MERGE (s:Sign {name: 'Virgo'})
SET s.symbol = '♍',
    s.glyph = 'Virgin/Maiden',
    s.degree_start = 150,
    s.degree_end = 180,
    s.polarity = 'yin',
    s.keywords = ['analysis', 'service', 'health', 'craft', 'discernment', 'improvement'],
    s.shadow = ['criticism', 'perfectionism', 'anxiety', 'overwork'],
    s.theme = 'I ANALYZE - refinement, healing, and sacred service',
    s.body_parts = ['intestines', 'digestive system', 'spleen'],
    s.tarot = 'The Hermit',
    s.season = 'late summer',
    s.color = 'navy blue';

// LIBRA
MERGE (s:Sign {name: 'Libra'})
SET s.symbol = '♎',
    s.glyph = 'Scales',
    s.degree_start = 180,
    s.degree_end = 210,
    s.polarity = 'yang',
    s.keywords = ['balance', 'partnership', 'harmony', 'justice', 'beauty', 'diplomacy'],
    s.shadow = ['indecision', 'people-pleasing', 'superficiality', 'avoidance'],
    s.theme = 'I RELATE - partnership, balance, and social harmony',
    s.body_parts = ['kidneys', 'lower back', 'skin'],
    s.tarot = 'Justice',
    s.season = 'early autumn',
    s.color = 'pink';

// SCORPIO
MERGE (s:Sign {name: 'Scorpio'})
SET s.symbol = '♏',
    s.glyph = 'Scorpion',
    s.degree_start = 210,
    s.degree_end = 240,
    s.polarity = 'yin',
    s.keywords = ['transformation', 'intensity', 'depth', 'power', 'regeneration', 'secrets'],
    s.shadow = ['jealousy', 'obsession', 'manipulation', 'vengeance'],
    s.theme = 'I TRANSFORM - death, rebirth, and profound merging',
    s.body_parts = ['reproductive organs', 'elimination organs', 'pelvis'],
    s.tarot = 'Death',
    s.season = 'mid autumn',
    s.color = 'dark red';

// SAGITTARIUS
MERGE (s:Sign {name: 'Sagittarius'})
SET s.symbol = '♐',
    s.glyph = 'Archer/Centaur',
    s.degree_start = 240,
    s.degree_end = 270,
    s.polarity = 'yang',
    s.keywords = ['expansion', 'philosophy', 'adventure', 'truth', 'optimism', 'wisdom'],
    s.shadow = ['excess', 'dogmatism', 'restlessness', 'tactlessness'],
    s.theme = 'I UNDERSTAND - meaning, expansion, and higher truth',
    s.body_parts = ['hips', 'thighs', 'liver'],
    s.tarot = 'Temperance',
    s.season = 'late autumn',
    s.color = 'purple';

// CAPRICORN
MERGE (s:Sign {name: 'Capricorn'})
SET s.symbol = '♑',
    s.glyph = 'Sea-Goat',
    s.degree_start = 270,
    s.degree_end = 300,
    s.polarity = 'yin',
    s.keywords = ['ambition', 'discipline', 'responsibility', 'mastery', 'structure', 'achievement'],
    s.shadow = ['rigidity', 'pessimism', 'coldness', 'workaholism'],
    s.theme = 'I USE - mastery, legacy, and worldly achievement',
    s.body_parts = ['knees', 'bones', 'skeleton', 'teeth'],
    s.tarot = 'The Devil',
    s.season = 'early winter',
    s.color = 'brown';

// AQUARIUS
MERGE (s:Sign {name: 'Aquarius'})
SET s.symbol = '♒',
    s.glyph = 'Water-Bearer',
    s.degree_start = 300,
    s.degree_end = 330,
    s.polarity = 'yang',
    s.keywords = ['innovation', 'humanity', 'individuality', 'freedom', 'vision', 'revolution'],
    s.shadow = ['detachment', 'eccentricity', 'rebellion', 'aloofness'],
    s.theme = 'I KNOW - collective consciousness and humanitarian vision',
    s.body_parts = ['ankles', 'calves', 'circulatory system'],
    s.tarot = 'The Star',
    s.season = 'mid winter',
    s.color = 'electric blue';

// PISCES
MERGE (s:Sign {name: 'Pisces'})
SET s.symbol = '♓',
    s.glyph = 'Fish',
    s.degree_start = 330,
    s.degree_end = 360,
    s.polarity = 'yin',
    s.keywords = ['transcendence', 'compassion', 'imagination', 'spirituality', 'unity', 'dreams'],
    s.shadow = ['escapism', 'victimhood', 'confusion', 'addiction'],
    s.theme = 'I BELIEVE - dissolution of ego and return to source',
    s.body_parts = ['feet', 'lymphatic system', 'pineal gland'],
    s.tarot = 'The Moon',
    s.season = 'late winter',
    s.color = 'sea green';

// ============================================================================
// SIGN RELATIONSHIPS
// ============================================================================

// Connect signs to elements
MATCH (s:Sign {name: 'Aries'}), (e:Element {name: 'Fire'}) MERGE (s)-[:HAS_ELEMENT]->(e);
MATCH (s:Sign {name: 'Taurus'}), (e:Element {name: 'Earth'}) MERGE (s)-[:HAS_ELEMENT]->(e);
MATCH (s:Sign {name: 'Gemini'}), (e:Element {name: 'Air'}) MERGE (s)-[:HAS_ELEMENT]->(e);
MATCH (s:Sign {name: 'Cancer'}), (e:Element {name: 'Water'}) MERGE (s)-[:HAS_ELEMENT]->(e);
MATCH (s:Sign {name: 'Leo'}), (e:Element {name: 'Fire'}) MERGE (s)-[:HAS_ELEMENT]->(e);
MATCH (s:Sign {name: 'Virgo'}), (e:Element {name: 'Earth'}) MERGE (s)-[:HAS_ELEMENT]->(e);
MATCH (s:Sign {name: 'Libra'}), (e:Element {name: 'Air'}) MERGE (s)-[:HAS_ELEMENT]->(e);
MATCH (s:Sign {name: 'Scorpio'}), (e:Element {name: 'Water'}) MERGE (s)-[:HAS_ELEMENT]->(e);
MATCH (s:Sign {name: 'Sagittarius'}), (e:Element {name: 'Fire'}) MERGE (s)-[:HAS_ELEMENT]->(e);
MATCH (s:Sign {name: 'Capricorn'}), (e:Element {name: 'Earth'}) MERGE (s)-[:HAS_ELEMENT]->(e);
MATCH (s:Sign {name: 'Aquarius'}), (e:Element {name: 'Air'}) MERGE (s)-[:HAS_ELEMENT]->(e);
MATCH (s:Sign {name: 'Pisces'}), (e:Element {name: 'Water'}) MERGE (s)-[:HAS_ELEMENT]->(e);

// Connect signs to modalities
MATCH (s:Sign {name: 'Aries'}), (m:Modality {name: 'Cardinal'}) MERGE (s)-[:HAS_MODALITY]->(m);
MATCH (s:Sign {name: 'Taurus'}), (m:Modality {name: 'Fixed'}) MERGE (s)-[:HAS_MODALITY]->(m);
MATCH (s:Sign {name: 'Gemini'}), (m:Modality {name: 'Mutable'}) MERGE (s)-[:HAS_MODALITY]->(m);
MATCH (s:Sign {name: 'Cancer'}), (m:Modality {name: 'Cardinal'}) MERGE (s)-[:HAS_MODALITY]->(m);
MATCH (s:Sign {name: 'Leo'}), (m:Modality {name: 'Fixed'}) MERGE (s)-[:HAS_MODALITY]->(m);
MATCH (s:Sign {name: 'Virgo'}), (m:Modality {name: 'Mutable'}) MERGE (s)-[:HAS_MODALITY]->(m);
MATCH (s:Sign {name: 'Libra'}), (m:Modality {name: 'Cardinal'}) MERGE (s)-[:HAS_MODALITY]->(m);
MATCH (s:Sign {name: 'Scorpio'}), (m:Modality {name: 'Fixed'}) MERGE (s)-[:HAS_MODALITY]->(m);
MATCH (s:Sign {name: 'Sagittarius'}), (m:Modality {name: 'Mutable'}) MERGE (s)-[:HAS_MODALITY]->(m);
MATCH (s:Sign {name: 'Capricorn'}), (m:Modality {name: 'Cardinal'}) MERGE (s)-[:HAS_MODALITY]->(m);
MATCH (s:Sign {name: 'Aquarius'}), (m:Modality {name: 'Fixed'}) MERGE (s)-[:HAS_MODALITY]->(m);
MATCH (s:Sign {name: 'Pisces'}), (m:Modality {name: 'Mutable'}) MERGE (s)-[:HAS_MODALITY]->(m);

// Opposite signs (axis relationships)
MATCH (s1:Sign {name: 'Aries'}), (s2:Sign {name: 'Libra'}) 
MERGE (s1)-[:OPPOSITE {axis: 'self-other'}]->(s2)
MERGE (s2)-[:OPPOSITE {axis: 'self-other'}]->(s1);

MATCH (s1:Sign {name: 'Taurus'}), (s2:Sign {name: 'Scorpio'}) 
MERGE (s1)-[:OPPOSITE {axis: 'resources-transformation'}]->(s2)
MERGE (s2)-[:OPPOSITE {axis: 'resources-transformation'}]->(s1);

MATCH (s1:Sign {name: 'Gemini'}), (s2:Sign {name: 'Sagittarius'}) 
MERGE (s1)-[:OPPOSITE {axis: 'information-wisdom'}]->(s2)
MERGE (s2)-[:OPPOSITE {axis: 'information-wisdom'}]->(s1);

MATCH (s1:Sign {name: 'Cancer'}), (s2:Sign {name: 'Capricorn'}) 
MERGE (s1)-[:OPPOSITE {axis: 'private-public'}]->(s2)
MERGE (s2)-[:OPPOSITE {axis: 'private-public'}]->(s1);

MATCH (s1:Sign {name: 'Leo'}), (s2:Sign {name: 'Aquarius'}) 
MERGE (s1)-[:OPPOSITE {axis: 'individual-collective'}]->(s2)
MERGE (s2)-[:OPPOSITE {axis: 'individual-collective'}]->(s1);

MATCH (s1:Sign {name: 'Virgo'}), (s2:Sign {name: 'Pisces'}) 
MERGE (s1)-[:OPPOSITE {axis: 'analysis-synthesis'}]->(s2)
MERGE (s2)-[:OPPOSITE {axis: 'analysis-synthesis'}]->(s1);

// ============================================================================
// CELESTIAL BODIES
// ============================================================================

// LUMINARIES
MERGE (b:Body {name: 'Sun'})
SET b.symbol = '☉',
    b.body_type = 'luminary',
    b.keywords = ['identity', 'vitality', 'ego', 'purpose', 'will', 'father', 'authority'],
    b.theme = 'The core self - who you are becoming',
    b.archetype = 'The Hero, The King, The Creator',
    b.represents = ['self', 'identity', 'life force', 'conscious will', 'father figure', 'authority'],
    b.rules_sign = 'Leo',
    b.exalted_in = 'Aries',
    b.detriment_in = 'Aquarius',
    b.fall_in = 'Libra',
    b.orbital_period_days = 365.25,
    b.glyph_meaning = 'Spirit (circle) with point of manifestation';

MERGE (b:Body {name: 'Moon'})
SET b.symbol = '☽',
    b.body_type = 'luminary',
    b.keywords = ['emotions', 'instincts', 'mother', 'home', 'comfort', 'habits', 'memory'],
    b.theme = 'The emotional self - what you need to feel safe',
    b.archetype = 'The Mother, The Nurturer, The Child',
    b.represents = ['emotions', 'instincts', 'subconscious', 'mother figure', 'the public', 'needs'],
    b.rules_sign = 'Cancer',
    b.exalted_in = 'Taurus',
    b.detriment_in = 'Capricorn',
    b.fall_in = 'Scorpio',
    b.orbital_period_days = 27.3,
    b.glyph_meaning = 'Soul (crescent) receiving spirit';

// PERSONAL PLANETS
MERGE (b:Body {name: 'Mercury'})
SET b.symbol = '☿',
    b.body_type = 'planet',
    b.keywords = ['communication', 'intellect', 'learning', 'travel', 'commerce', 'trickster'],
    b.theme = 'The mind - how you think and communicate',
    b.archetype = 'The Messenger, The Trickster, The Scribe',
    b.represents = ['mind', 'communication', 'siblings', 'short journeys', 'commerce', 'writing'],
    b.rules_signs = ['Gemini', 'Virgo'],
    b.exalted_in = 'Virgo',
    b.detriment_in = ['Sagittarius', 'Pisces'],
    b.fall_in = 'Pisces',
    b.orbital_period_days = 88,
    b.retrograde_frequency = '3-4 times per year',
    b.glyph_meaning = 'Spirit over soul over matter - the mediator';

MERGE (b:Body {name: 'Venus'})
SET b.symbol = '♀',
    b.body_type = 'planet',
    b.keywords = ['love', 'beauty', 'values', 'pleasure', 'art', 'harmony', 'attraction'],
    b.theme = 'The heart - what you love and value',
    b.archetype = 'The Lover, The Artist, The Peacemaker',
    b.represents = ['love', 'beauty', 'values', 'money', 'art', 'women', 'pleasure'],
    b.rules_signs = ['Taurus', 'Libra'],
    b.exalted_in = 'Pisces',
    b.detriment_in = ['Scorpio', 'Aries'],
    b.fall_in = 'Virgo',
    b.orbital_period_days = 225,
    b.retrograde_frequency = 'every 18 months',
    b.glyph_meaning = 'Spirit over matter - soul elevated';

MERGE (b:Body {name: 'Mars'})
SET b.symbol = '♂',
    b.body_type = 'planet',
    b.keywords = ['action', 'desire', 'aggression', 'courage', 'competition', 'sexuality'],
    b.theme = 'The will - how you assert yourself and pursue desires',
    b.archetype = 'The Warrior, The Pioneer, The Competitor',
    b.represents = ['action', 'desire', 'anger', 'sexuality', 'men', 'competition', 'surgery'],
    b.rules_signs = ['Aries', 'Scorpio'],
    b.exalted_in = 'Capricorn',
    b.detriment_in = ['Libra', 'Taurus'],
    b.fall_in = 'Cancer',
    b.orbital_period_days = 687,
    b.retrograde_frequency = 'every 2 years',
    b.glyph_meaning = 'Matter piercing spirit - will to action';

// SOCIAL PLANETS
MERGE (b:Body {name: 'Jupiter'})
SET b.symbol = '♃',
    b.body_type = 'planet',
    b.keywords = ['expansion', 'luck', 'wisdom', 'philosophy', 'abundance', 'faith', 'excess'],
    b.theme = 'The teacher - where you find meaning and growth',
    b.archetype = 'The Sage, The King, The Adventurer',
    b.represents = ['expansion', 'luck', 'higher education', 'religion', 'long journeys', 'law'],
    b.rules_signs = ['Sagittarius', 'Pisces'],
    b.exalted_in = 'Cancer',
    b.detriment_in = ['Gemini', 'Virgo'],
    b.fall_in = 'Capricorn',
    b.orbital_period_days = 4333,
    b.retrograde_frequency = 'once per year, 4 months',
    b.glyph_meaning = 'Soul rising above matter';

MERGE (b:Body {name: 'Saturn'})
SET b.symbol = '♄',
    b.body_type = 'planet',
    b.keywords = ['structure', 'discipline', 'limitation', 'karma', 'time', 'mastery', 'fear'],
    b.theme = 'The teacher of hard lessons - where you face limitations and build mastery',
    b.archetype = 'The Elder, The Judge, The Builder',
    b.represents = ['structure', 'limits', 'father', 'authority', 'karma', 'time', 'bones'],
    b.rules_signs = ['Capricorn', 'Aquarius'],
    b.exalted_in = 'Libra',
    b.detriment_in = ['Cancer', 'Leo'],
    b.fall_in = 'Aries',
    b.orbital_period_days = 10759,
    b.retrograde_frequency = 'once per year, 4.5 months',
    b.glyph_meaning = 'Matter dominating soul - crystallization';

// TRANSPERSONAL PLANETS
MERGE (b:Body {name: 'Uranus'})
SET b.symbol = '♅',
    b.body_type = 'planet',
    b.keywords = ['revolution', 'innovation', 'awakening', 'freedom', 'electricity', 'chaos'],
    b.theme = 'The awakener - where you break free and individuate',
    b.archetype = 'The Revolutionary, The Genius, The Eccentric',
    b.represents = ['sudden change', 'innovation', 'technology', 'rebellion', 'awakening'],
    b.rules_sign = 'Aquarius',
    b.exalted_in = 'Scorpio',
    b.detriment_in = 'Leo',
    b.fall_in = 'Taurus',
    b.orbital_period_days = 30687,
    b.discovered = 1781,
    b.glyph_meaning = 'Cross of matter between two crescents of soul';

MERGE (b:Body {name: 'Neptune'})
SET b.symbol = '♆',
    b.body_type = 'planet',
    b.keywords = ['transcendence', 'illusion', 'spirituality', 'dreams', 'dissolution', 'compassion'],
    b.theme = 'The mystic - where you dissolve boundaries and touch the divine',
    b.archetype = 'The Mystic, The Artist, The Martyr',
    b.represents = ['spirituality', 'illusion', 'dreams', 'addiction', 'film', 'ocean', 'dissolution'],
    b.rules_sign = 'Pisces',
    b.exalted_in = 'Leo',
    b.detriment_in = 'Virgo',
    b.fall_in = 'Aquarius',
    b.orbital_period_days = 60190,
    b.discovered = 1846,
    b.glyph_meaning = 'Trident of Poseidon - soul piercing matter';

MERGE (b:Body {name: 'Pluto'})
SET b.symbol = '♇',
    b.body_type = 'dwarf_planet',
    b.keywords = ['transformation', 'power', 'death', 'rebirth', 'shadow', 'obsession'],
    b.theme = 'The transformer - where you die and are reborn',
    b.archetype = 'The Shaman, The Destroyer, The Phoenix',
    b.represents = ['transformation', 'death/rebirth', 'power', 'shadow', 'secrets', 'plutocracy'],
    b.rules_sign = 'Scorpio',
    b.exalted_in = 'Aries',
    b.detriment_in = 'Taurus',
    b.fall_in = 'Libra',
    b.orbital_period_days = 90560,
    b.discovered = 1930,
    b.glyph_meaning = 'Spirit over soul over matter - total transformation';

// CHIRON
MERGE (b:Body {name: 'Chiron'})
SET b.symbol = '⚷',
    b.body_type = 'centaur',
    b.keywords = ['wound', 'healing', 'teaching', 'bridge', 'maverick', 'initiation'],
    b.theme = 'The wounded healer - where your deepest wound becomes your greatest gift',
    b.archetype = 'The Wounded Healer, The Mentor, The Shaman',
    b.represents = ['core wound', 'healing journey', 'teaching', 'alternative medicine', 'mentorship'],
    b.orbital_period_days = 18500,
    b.discovered = 1977,
    b.mythology = 'Centaur who taught heroes, wounded by poisoned arrow, gave up immortality';

// MAJOR ASTEROIDS
MERGE (b:Body {name: 'Ceres'})
SET b.symbol = '⚳',
    b.body_type = 'dwarf_planet',
    b.keywords = ['nurturing', 'mother', 'food', 'loss', 'cycles', 'agriculture'],
    b.theme = 'The great mother - how you nurture and experience loss',
    b.archetype = 'The Mother, The Nurturer, The Grieving Parent',
    b.represents = ['nurturing', 'food', 'motherhood', 'loss/grief', 'harvest cycles'],
    b.orbital_period_days = 1680,
    b.discovered = 1801,
    b.mythology = 'Goddess of harvest who grieved for Persephone';

MERGE (b:Body {name: 'Pallas'})
SET b.symbol = '⚴',
    b.body_type = 'asteroid',
    b.keywords = ['wisdom', 'strategy', 'pattern recognition', 'creative intelligence', 'politics'],
    b.theme = 'The strategist - how you see patterns and fight with wisdom',
    b.archetype = 'The Warrior Goddess, The Strategist, The Artisan',
    b.represents = ['wisdom', 'strategy', 'crafts', 'father-daughter', 'political acumen'],
    b.orbital_period_days = 1684,
    b.discovered = 1802,
    b.mythology = 'Athena Pallas - goddess of wisdom and strategic warfare';

MERGE (b:Body {name: 'Juno'})
SET b.symbol = '⚵',
    b.body_type = 'asteroid',
    b.keywords = ['partnership', 'marriage', 'commitment', 'jealousy', 'equality'],
    b.theme = 'The partner - what you need in committed relationship',
    b.archetype = 'The Wife, The Partner, The Committed One',
    b.represents = ['marriage', 'committed partnership', 'jealousy', 'equality in relationship'],
    b.orbital_period_days = 1594,
    b.discovered = 1804,
    b.mythology = 'Queen of gods, goddess of marriage';

MERGE (b:Body {name: 'Vesta'})
SET b.symbol = '⚶',
    b.body_type = 'asteroid',
    b.keywords = ['devotion', 'sacred flame', 'focus', 'purity', 'service', 'sexuality'],
    b.theme = 'The priestess - where you tend the sacred flame',
    b.archetype = 'The Priestess, The Devotee, The Sacred Worker',
    b.represents = ['devotion', 'focus', 'sacred sexuality', 'service', 'commitment to work'],
    b.orbital_period_days = 1325,
    b.discovered = 1807,
    b.mythology = 'Goddess of the hearth and sacred flame';

// LUNAR NODES
MERGE (b:Body {name: 'North Node'})
SET b.symbol = '☊',
    b.body_type = 'point',
    b.keywords = ['destiny', 'growth', 'future', 'dharma', 'soul purpose', 'unfamiliar'],
    b.theme = 'The path forward - where your soul is growing toward',
    b.archetype = 'The Future Self, The Destiny Point',
    b.represents = ['soul growth', 'destiny', 'what you are learning', 'unfamiliar territory'];

MERGE (b:Body {name: 'South Node'})
SET b.symbol = '☋',
    b.body_type = 'point',
    b.keywords = ['past', 'karma', 'gifts', 'habits', 'comfort zone', 'release'],
    b.theme = 'The past mastery - what you bring from before and must release',
    b.archetype = 'The Past Self, The Karmic Point',
    b.represents = ['past life gifts', 'karma', 'comfort zone', 'what to release'];

// BLACK MOON LILITH
MERGE (b:Body {name: 'Black Moon Lilith'})
SET b.symbol = '⚸',
    b.body_type = 'point',
    b.keywords = ['shadow', 'primal feminine', 'rage', 'exile', 'wild', 'taboo'],
    b.theme = 'The dark feminine - where you are exiled and reclaim your power',
    b.archetype = 'The Outcast, The Wild Woman, The Dark Goddess',
    b.represents = ['repressed rage', 'sexuality', 'what is exiled', 'primal feminine power'],
    b.mythology = 'First wife of Adam who refused submission';

// ============================================================================
// PLANETARY RULERSHIPS
// ============================================================================

// Modern rulerships
MATCH (b:Body {name: 'Sun'}), (s:Sign {name: 'Leo'}) MERGE (b)-[:RULES {type: 'domicile'}]->(s);
MATCH (b:Body {name: 'Moon'}), (s:Sign {name: 'Cancer'}) MERGE (b)-[:RULES {type: 'domicile'}]->(s);
MATCH (b:Body {name: 'Mercury'}), (s:Sign {name: 'Gemini'}) MERGE (b)-[:RULES {type: 'domicile'}]->(s);
MATCH (b:Body {name: 'Mercury'}), (s:Sign {name: 'Virgo'}) MERGE (b)-[:RULES {type: 'domicile'}]->(s);
MATCH (b:Body {name: 'Venus'}), (s:Sign {name: 'Taurus'}) MERGE (b)-[:RULES {type: 'domicile'}]->(s);
MATCH (b:Body {name: 'Venus'}), (s:Sign {name: 'Libra'}) MERGE (b)-[:RULES {type: 'domicile'}]->(s);
MATCH (b:Body {name: 'Mars'}), (s:Sign {name: 'Aries'}) MERGE (b)-[:RULES {type: 'domicile'}]->(s);
MATCH (b:Body {name: 'Jupiter'}), (s:Sign {name: 'Sagittarius'}) MERGE (b)-[:RULES {type: 'domicile'}]->(s);
MATCH (b:Body {name: 'Saturn'}), (s:Sign {name: 'Capricorn'}) MERGE (b)-[:RULES {type: 'domicile'}]->(s);
MATCH (b:Body {name: 'Uranus'}), (s:Sign {name: 'Aquarius'}) MERGE (b)-[:RULES {type: 'domicile'}]->(s);
MATCH (b:Body {name: 'Neptune'}), (s:Sign {name: 'Pisces'}) MERGE (b)-[:RULES {type: 'domicile'}]->(s);
MATCH (b:Body {name: 'Pluto'}), (s:Sign {name: 'Scorpio'}) MERGE (b)-[:RULES {type: 'domicile'}]->(s);

// Traditional rulerships (co-rulerships)
MATCH (b:Body {name: 'Mars'}), (s:Sign {name: 'Scorpio'}) MERGE (b)-[:RULES {type: 'traditional'}]->(s);
MATCH (b:Body {name: 'Jupiter'}), (s:Sign {name: 'Pisces'}) MERGE (b)-[:RULES {type: 'traditional'}]->(s);
MATCH (b:Body {name: 'Saturn'}), (s:Sign {name: 'Aquarius'}) MERGE (b)-[:RULES {type: 'traditional'}]->(s);

// ============================================================================
// HOUSES
// ============================================================================

MERGE (h:House {number: 1})
SET h.name = 'House of Self',
    h.natural_sign = 'Aries',
    h.natural_ruler = 'Mars',
    h.keywords = ['self', 'identity', 'appearance', 'beginnings', 'approach to life'],
    h.life_areas = ['physical body', 'self-image', 'first impressions', 'how you start things'],
    h.question = 'Who am I?',
    h.angular = true,
    h.theme = 'The mask you wear and the self you are becoming';

MERGE (h:House {number: 2})
SET h.name = 'House of Values',
    h.natural_sign = 'Taurus',
    h.natural_ruler = 'Venus',
    h.keywords = ['values', 'possessions', 'money', 'self-worth', 'resources'],
    h.life_areas = ['money', 'possessions', 'values', 'self-esteem', 'what you own'],
    h.question = 'What do I have?',
    h.succedent = true,
    h.theme = 'What you value and how you resource yourself';

MERGE (h:House {number: 3})
SET h.name = 'House of Communication',
    h.natural_sign = 'Gemini',
    h.natural_ruler = 'Mercury',
    h.keywords = ['communication', 'siblings', 'short trips', 'learning', 'neighbors'],
    h.life_areas = ['siblings', 'neighbors', 'short trips', 'early education', 'communication'],
    h.question = 'How do I communicate?',
    h.cadent = true,
    h.theme = 'How you think, speak, and connect locally';

MERGE (h:House {number: 4})
SET h.name = 'House of Home',
    h.natural_sign = 'Cancer',
    h.natural_ruler = 'Moon',
    h.keywords = ['home', 'family', 'roots', 'ancestry', 'private life', 'endings'],
    h.life_areas = ['home', 'family', 'mother/nurturing parent', 'ancestry', 'real estate'],
    h.question = 'Where do I come from?',
    h.angular = true,
    h.theme = 'Your roots, foundations, and inner sanctuary';

MERGE (h:House {number: 5})
SET h.name = 'House of Creativity',
    h.natural_sign = 'Leo',
    h.natural_ruler = 'Sun',
    h.keywords = ['creativity', 'children', 'romance', 'play', 'self-expression'],
    h.life_areas = ['creativity', 'children', 'romance', 'gambling', 'hobbies', 'fun'],
    h.question = 'What do I create?',
    h.succedent = true,
    h.theme = 'What you create, including children and joy';

MERGE (h:House {number: 6})
SET h.name = 'House of Health',
    h.natural_sign = 'Virgo',
    h.natural_ruler = 'Mercury',
    h.keywords = ['health', 'service', 'daily routines', 'work', 'pets'],
    h.life_areas = ['health', 'daily work', 'service', 'routines', 'pets', 'employees'],
    h.question = 'How do I serve?',
    h.cadent = true,
    h.theme = 'Daily rituals, health, and sacred service';

MERGE (h:House {number: 7})
SET h.name = 'House of Partnership',
    h.natural_sign = 'Libra',
    h.natural_ruler = 'Venus',
    h.keywords = ['partnership', 'marriage', 'contracts', 'open enemies', 'the other'],
    h.life_areas = ['marriage', 'business partners', 'contracts', 'open enemies', 'the public'],
    h.question = 'Who am I with others?',
    h.angular = true,
    h.theme = 'The mirror of relationship and committed partnership';

MERGE (h:House {number: 8})
SET h.name = 'House of Transformation',
    h.natural_sign = 'Scorpio',
    h.natural_ruler = 'Pluto',
    h.keywords = ['transformation', 'death', 'sex', 'shared resources', 'occult'],
    h.life_areas = ['death', 'inheritance', 'shared resources', 'sex', 'taxes', 'occult'],
    h.question = 'What must I release?',
    h.succedent = true,
    h.theme = 'Death, rebirth, and merging with the other';

MERGE (h:House {number: 9})
SET h.name = 'House of Philosophy',
    h.natural_sign = 'Sagittarius',
    h.natural_ruler = 'Jupiter',
    h.keywords = ['philosophy', 'higher learning', 'travel', 'religion', 'expansion'],
    h.life_areas = ['higher education', 'long journeys', 'philosophy', 'religion', 'publishing'],
    h.question = 'What do I believe?',
    h.cadent = true,
    h.theme = 'The search for meaning and expansion of consciousness';

MERGE (h:House {number: 10})
SET h.name = 'House of Career',
    h.natural_sign = 'Capricorn',
    h.natural_ruler = 'Saturn',
    h.keywords = ['career', 'reputation', 'authority', 'public life', 'legacy'],
    h.life_areas = ['career', 'public reputation', 'authority', 'father/authority parent', 'legacy'],
    h.question = 'What is my contribution?',
    h.angular = true,
    h.theme = 'Your public role and lasting contribution';

MERGE (h:House {number: 11})
SET h.name = 'House of Community',
    h.natural_sign = 'Aquarius',
    h.natural_ruler = 'Uranus',
    h.keywords = ['community', 'friends', 'hopes', 'groups', 'humanitarian'],
    h.life_areas = ['friends', 'groups', 'hopes/wishes', 'humanitarian causes', 'networks'],
    h.question = 'Where do I belong?',
    h.succedent = true,
    h.theme = 'Your tribe, hopes, and contribution to collective';

MERGE (h:House {number: 12})
SET h.name = 'House of the Unconscious',
    h.natural_sign = 'Pisces',
    h.natural_ruler = 'Neptune',
    h.keywords = ['unconscious', 'secrets', 'isolation', 'spirituality', 'self-undoing'],
    h.life_areas = ['unconscious', 'hidden enemies', 'hospitals', 'prisons', 'spirituality', 'karma'],
    h.question = 'What am I releasing?',
    h.cadent = true,
    h.theme = 'The hidden, the spiritual, and return to source';

// ============================================================================
// ASPECT TYPES
// ============================================================================

MERGE (a:AspectType {name: 'Conjunction'})
SET a.symbol = '☌',
    a.angle = 0,
    a.orb_default = 10,
    a.is_major = true,
    a.nature = 'fusion',
    a.keywords = ['merging', 'intensification', 'beginning', 'unification'],
    a.interpretation = 'Planets merge energies, intensifying both. The beginning of a new cycle. Can be challenging if planets are incompatible.';

MERGE (a:AspectType {name: 'Opposition'})
SET a.symbol = '☍',
    a.angle = 180,
    a.orb_default = 8,
    a.is_major = true,
    a.nature = 'tension',
    a.keywords = ['awareness', 'projection', 'balance', 'relationship'],
    a.interpretation = 'Planets in direct confrontation requiring integration. Often experienced through relationships. The peak of a cycle.';

MERGE (a:AspectType {name: 'Trine'})
SET a.symbol = '△',
    a.angle = 120,
    a.orb_default = 8,
    a.is_major = true,
    a.nature = 'harmony',
    a.keywords = ['flow', 'ease', 'talent', 'support'],
    a.interpretation = 'Natural harmony and flow between planets. Talents that come easily, sometimes too easily (lazy aspect).';

MERGE (a:AspectType {name: 'Square'})
SET a.symbol = '□',
    a.angle = 90,
    a.orb_default = 7,
    a.is_major = true,
    a.nature = 'tension',
    a.keywords = ['friction', 'action', 'growth', 'challenge'],
    a.interpretation = 'Dynamic tension requiring action. Frustrating but produces growth. The crisis points of a cycle.';

MERGE (a:AspectType {name: 'Sextile'})
SET a.symbol = '⚹',
    a.angle = 60,
    a.orb_default = 6,
    a.is_major = true,
    a.nature = 'harmony',
    a.keywords = ['opportunity', 'communication', 'skill', 'cooperation'],
    a.interpretation = 'Opportunity aspect requiring conscious activation. Skills that can be developed with effort.';

MERGE (a:AspectType {name: 'Quincunx'})
SET a.symbol = '⚻',
    a.angle = 150,
    a.orb_default = 3,
    a.is_major = false,
    a.nature = 'adjustment',
    a.keywords = ['adjustment', 'awkwardness', 'health', 'integration'],
    a.interpretation = 'Planets with nothing in common requiring constant adjustment. Often manifests in health issues.';

MERGE (a:AspectType {name: 'Semi-sextile'})
SET a.symbol = '⚺',
    a.angle = 30,
    a.orb_default = 2,
    a.is_major = false,
    a.nature = 'growth',
    a.keywords = ['growth', 'adjacent', 'slight tension'],
    a.interpretation = 'Subtle friction between adjacent signs requiring minor adjustments.';

MERGE (a:AspectType {name: 'Semi-square'})
SET a.angle = 45,
    a.orb_default = 2,
    a.is_major = false,
    a.nature = 'friction',
    a.keywords = ['irritation', 'minor friction', 'agitation'],
    a.interpretation = 'Internal friction producing irritation. Minor but persistent challenge.';

MERGE (a:AspectType {name: 'Sesquiquadrate'})
SET a.angle = 135,
    a.orb_default = 2,
    a.is_major = false,
    a.nature = 'friction',
    a.keywords = ['agitation', 'external friction', 'adjustment'],
    a.interpretation = 'External friction requiring adjustment. Similar to semi-square but more externalized.';

MERGE (a:AspectType {name: 'Quintile'})
SET a.angle = 72,
    a.orb_default = 2,
    a.is_major = false,
    a.nature = 'creative',
    a.keywords = ['talent', 'creativity', 'gift', 'unique ability'],
    a.interpretation = 'Creative talent and unique gifts. Associated with the 5th harmonic.';

MERGE (a:AspectType {name: 'Bi-quintile'})
SET a.angle = 144,
    a.orb_default = 2,
    a.is_major = false,
    a.nature = 'creative',
    a.keywords = ['creative expression', 'talent', 'gift'],
    a.interpretation = 'Similar to quintile - creative and artistic abilities.';

// ============================================================================
// CHART NODE (Template for actual charts)
// ============================================================================

// When a chart is created, it will be linked to its placements like this:
// (c:Chart {chart_id: 'uuid'})-[:HAS_PLACEMENT]->(p:Placement {body: 'Sun', sign: 'Aries', degree: 15.5})
// (p:Placement)-[:IN_SIGN]->(s:Sign {name: 'Aries'})
// (p:Placement)-[:IN_HOUSE]->(h:House {number: 1})
// (p1:Placement)-[:ASPECTS {type: 'conjunction', orb: 2.3}]->(p2:Placement)

// ============================================================================
// RETURN SUMMARY
// ============================================================================

MATCH (n) RETURN labels(n)[0] AS type, count(*) AS count ORDER BY type;
