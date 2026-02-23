// =============================================================================
// PATCH 0114: Ontology v2 Schema Migration + Moon Data
// Run via: cat this_file.cypher | cypher-shell -u neo4j -p <password>
// =============================================================================

// ---------------------------------------------------------------------------
// PART 1: Migrate existing 71 nodes to v2 schema
// Adds new properties with safe defaults. Non-destructive.
// ---------------------------------------------------------------------------

MATCH (t:OntologyTerm)
WHERE t.confidence IS NULL
SET t.confidence = 1.0,
    t.source = "manual",
    t.version = 1,
    t.is_active = true,
    t.imported_from = "migration",
    t.subcategory = null,
    t.tradition = null,
    t.tags = [],
    t.cross_cultural = null,
    t.season = null,
    t.element = null,
    t.magical_focus = null,
    t.deity_association = null,
    t.superseded_by = null,
    t.superseded_at = null,
    t.batch_id = "migration_v2_2026-02-23"
RETURN count(t) + " nodes migrated to v2 schema";

// ---------------------------------------------------------------------------
// PART 2: Create parent grouping node
// ---------------------------------------------------------------------------

MERGE (parent:OntologyTerm {name: "Monthly Moon Cycle"})
ON CREATE SET
    parent.definition = "The cycle of 12-13 named full moons throughout the year. Nearly every culture on Earth has named the monthly moons, tying them to ecological markers, agricultural cycles, spiritual practices, and seasonal rhythms. The most commonly known names in North America derive from Algonquin tribal names adopted by Colonial Americans, but Celtic, Anglo-Saxon, Hindu, Chinese, Māori, and many other traditions maintain their own rich naming systems.",
    parent.category = "Lunar",
    parent.subcategory = "Overview",
    parent.aliases = ["Moon Names", "Named Moons", "Full Moon Names", "Lunar Month Names"],
    parent.confidence = 1.0,
    parent.source = "researched",
    parent.version = 1,
    parent.is_active = true,
    parent.imported_from = "bulk_ingest",
    parent.batch_id = "moon_terms_2026-02-23",
    parent.tags = ["lunar", "calendar", "cross-cultural", "seasonal"],
    parent.created_at = datetime().epochMillis,
    parent.updated_at = datetime().epochMillis
ON MATCH SET parent.updated_at = datetime().epochMillis;

// ---------------------------------------------------------------------------
// PART 3: Monthly Moon Terms (12)
// Each definition synthesizes across all traditions researched.
// ---------------------------------------------------------------------------

// JANUARY — Wolf Moon
MERGE (t:OntologyTerm {name: "Wolf Moon"})
ON CREATE SET
    t.definition = "January's full moon. Named for wolf howls echoing through midwinter — not from hunger, but territory marking and pack bonding. Across traditions: the Ojibwe call it Spirit Moon (Minado Giizis), a time of deep spiritual communion. The Lakota name it Moon of Frost in the Tipi. Celts call it the Quiet Moon — stillness before the cycle. In Hindu tradition, Pushya Purnima is auspicious for sacred bathing and charity. The Chinese 12th month (腊月 Làyuè, Sacrificial Month) is a time for ancestor offerings. Sri Lankan Duruthu Poya commemorates Buddha's first visit to Lanka. A moon of endurance, inner vision, and planning.",
    t.category = "Lunar",
    t.subcategory = "Monthly Moons",
    t.aliases = ["Old Moon", "Ice Moon", "Moon After Yule", "Spirit Moon", "Quiet Moon", "Pushya Purnima"],
    t.confidence = 0.95,
    t.source = "researched",
    t.version = 1,
    t.is_active = true,
    t.imported_from = "bulk_ingest",
    t.batch_id = "moon_terms_2026-02-23",
    t.tradition = "Cross-Cultural",
    t.tags = ["january", "winter", "wolves", "endurance", "spirit"],
    t.season = "winter",
    t.magical_focus = "Survival, endurance, protection, introspection, long-range planning",
    t.cross_cultural = '{"algonquin":"Wolf Moon","ojibwe":"Spirit Moon (Minado Giizis)","lakota":"Moon of Frost in the Tipi","celtic":"Quiet Moon","hindu":"Pushya Purnima","chinese":"Làyuè (Sacrificial Month)","maori":"Kohitātea","sri_lankan":"Duruthu Poya","neo_pagan":"Wolf Moon"}',
    t.created_at = datetime().epochMillis,
    t.updated_at = datetime().epochMillis;

// FEBRUARY — Snow Moon
MERGE (t:OntologyTerm {name: "Snow Moon"})
ON CREATE SET
    t.definition = "February's full moon. Named for the heavy snowfall blanketing North America. The Ojibwe call it Bear Moon (Makwa Giizis) — bears in deep hibernation, a time of rest and inner strength. The Lakota name it Moon When the Coyotes Are Frightened. Celts call it Moon of Ice — endurance and inner fire. Imbolc (Feb 1-2) falls in this month, honoring Brigid. Hindu Magha Purnima is considered extremely auspicious — bathing in the Ganges removes sins. Chinese New Year typically falls in this month, beginning Zhēngyuè (正月, the Capital Month). Sri Lankan Navam Poya commemorates the appointment of Buddha's chief disciples.",
    t.category = "Lunar",
    t.subcategory = "Monthly Moons",
    t.aliases = ["Hunger Moon", "Storm Moon", "Bone Moon", "Bear Moon", "Moon of Ice", "Magha Purnima"],
    t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tradition = "Cross-Cultural",
    t.tags = ["february", "winter", "snow", "purification", "endurance"],
    t.season = "winter",
    t.magical_focus = "Purification, patience, inner strength, cleansing, breaking curses",
    t.cross_cultural = '{"algonquin":"Snow Moon","ojibwe":"Bear Moon (Makwa Giizis)","lakota":"Moon When Coyotes Are Frightened","celtic":"Moon of Ice","hindu":"Magha Purnima","chinese":"Zhēngyuè (Capital Month)","maori":"Hui-tanguru","sri_lankan":"Navam Poya","neo_pagan":"Storm Moon"}',
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

// MARCH — Worm Moon
MERGE (t:OntologyTerm {name: "Worm Moon"})
ON CREATE SET
    t.definition = "March's full moon. Named for earthworm trails in newly thawed ground — or possibly beetle larvae emerging from bark. The Ojibwe call it Snow Crust Moon (Onaabidin Giizis) — the freeze-thaw crust that forms in late winter. The Lakota name it Moon of the Snowblind. Celts call it Seed Moon — the time to plant intentions (Ostara/Spring Equinox). Hindu Phalguna Purnima marks Holika Dahan and the start of Holi — burning away old karma, celebrating with colors. The Chinese 2nd month is Apricot Month (杏月 Xìngyuè). Sri Lankan Madin Poya commemorates Buddha's return to his father's palace.",
    t.category = "Lunar", t.subcategory = "Monthly Moons",
    t.aliases = ["Sap Moon", "Crow Moon", "Crust Moon", "Sugar Moon", "Seed Moon", "Chaste Moon", "Phalguna Purnima"],
    t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tradition = "Cross-Cultural",
    t.tags = ["march", "spring", "thaw", "new-beginnings", "equinox"],
    t.season = "spring",
    t.magical_focus = "New beginnings, breaking ground, fertility, sowing intentions",
    t.cross_cultural = '{"algonquin":"Worm Moon","ojibwe":"Snow Crust Moon (Onaabidin Giizis)","lakota":"Moon of the Snowblind","celtic":"Seed Moon","hindu":"Phalguna Purnima","chinese":"Xìngyuè (Apricot Month)","maori":"Poutū-te-rangi","sri_lankan":"Madin Poya","neo_pagan":"Chaste Moon"}',
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

// APRIL — Pink Moon
MERGE (t:OntologyTerm {name: "Pink Moon"})
ON CREATE SET
    t.definition = "April's full moon. Named for wild ground phlox (Phlox subulata), one of the first spring wildflowers. The Ojibwe call it Broken Snowshoe Moon (Popogami Giizis) — wet heavy snow breaking through. The Lakota name it Moon When Streams Are Again Navigable. Celts call it Growing Moon — tend what's been planted. Hindu Chaitra Purnima marks the beginning of the Hindu new year in many traditions; Hanuman Jayanti is celebrated. Chinese 3rd month is Peach Month (桃月 Táoyuè) — Qingming (Tomb Sweeping Day) falls here. Can also be the Paschal Moon, used to calculate Easter.",
    t.category = "Lunar", t.subcategory = "Monthly Moons",
    t.aliases = ["Sprouting Grass Moon", "Egg Moon", "Fish Moon", "Paschal Moon", "Growing Moon", "Chaitra Purnima"],
    t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tradition = "Cross-Cultural",
    t.tags = ["april", "spring", "wildflowers", "growth", "fertility"],
    t.season = "spring",
    t.magical_focus = "Growth, nurturing, romance, creativity, tending intentions",
    t.cross_cultural = '{"algonquin":"Pink Moon","ojibwe":"Broken Snowshoe Moon (Popogami Giizis)","lakota":"Moon When Streams Are Navigable","celtic":"Growing Moon","hindu":"Chaitra Purnima","chinese":"Táoyuè (Peach Month)","maori":"Paenga-whāwhā","sri_lankan":"Bak Poya","neo_pagan":"Seed Moon"}',
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

// MAY — Flower Moon
MERGE (t:OntologyTerm {name: "Flower Moon"})
ON CREATE SET
    t.definition = "May's full moon. Named for the abundance of flowers blooming as spring reaches full expression. The Ojibwe call it Sucker Moon (Nimebine Giizis) — sucker fish spawning in rivers, essential nutrition after winter. Celts also call it Flower Moon, associated with Beltane (May 1). Hindu Vaishakh Purnima is Buddha Purnima/Vesak — the most sacred Buddhist observance, commemorating the birth, enlightenment, and death of the Buddha. Chinese 4th month is Plum Flower Month (梅月 Méiyuè). Sri Lankan Vesak Poya is the holiest Poya day.",
    t.category = "Lunar", t.subcategory = "Monthly Moons",
    t.aliases = ["Corn Planting Moon", "Milk Moon", "Mothers' Moon", "Hare Moon", "Vaishakh Purnima", "Buddha Purnima"],
    t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tradition = "Cross-Cultural",
    t.tags = ["may", "spring", "flowers", "abundance", "beltane", "vesak"],
    t.season = "spring",
    t.magical_focus = "Abundance, beauty, sensuality, love magic, full creative expression",
    t.cross_cultural = '{"algonquin":"Flower Moon","ojibwe":"Sucker Moon (Nimebine Giizis)","lakota":"Moon When Ponies Shed","celtic":"Flower Moon","hindu":"Vaishakh/Buddha Purnima","chinese":"Méiyuè (Plum Flower Month)","maori":"Haratua","sri_lankan":"Vesak Poya","neo_pagan":"Hare Moon"}',
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

// JUNE — Strawberry Moon
MERGE (t:OntologyTerm {name: "Strawberry Moon"})
ON CREATE SET
    t.definition = "June's full moon. Named for the short strawberry harvesting season in the northeast. Europeans call it Rose Moon. The Ojibwe call it Blooming Moon (Waabigonii Giizis). The Lakota name it Moon of the June Berries. Celts call it Mead Moon — honey harvest begins, mead is brewed, celebration and partnership energy (Litha/Summer Solstice). The word 'honeymoon' may derive from June's Mead Moon tradition. Hindu Jyeshtha Purnima means 'eldest month.' Chinese 5th month is Pomegranate Month (榴月 Liúyuè) — Dragon Boat Festival falls here. The Māori new year (Matariki/Pleiades rising) begins in June with Pipiri.",
    t.category = "Lunar", t.subcategory = "Monthly Moons",
    t.aliases = ["Rose Moon", "Mead Moon", "Honey Moon", "Hot Moon", "Blooming Moon", "Jyeshtha Purnima"],
    t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tradition = "Cross-Cultural",
    t.tags = ["june", "summer", "strawberries", "solstice", "partnerships", "mead"],
    t.season = "summer",
    t.magical_focus = "Love, partnerships, celebration, commitment, abundance, solar peak",
    t.cross_cultural = '{"algonquin":"Strawberry Moon","ojibwe":"Blooming Moon (Waabigonii Giizis)","lakota":"Moon of June Berries","celtic":"Mead Moon","hindu":"Jyeshtha Purnima","chinese":"Liúyuè (Pomegranate Month)","maori":"Pipiri (New Year)","sri_lankan":"Poson Poya","neo_pagan":"Mead Moon"}',
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

// JULY — Buck Moon
MERGE (t:OntologyTerm {name: "Buck Moon"})
ON CREATE SET
    t.definition = "July's full moon. Named for the rapid velvet growth of male deer antlers during midsummer. The Ojibwe call it Berry Moon (Miin Giizis) — berries ripening everywhere. The Lakota name it Moon When the Chokecherries Are Ripe — Sun Dance season. Celts call it Horse Moon — sovereignty, travel, power. Hindu Ashadh Purnima is Guru Purnima — the most sacred day for honoring the spiritual teacher. Over 15,000 years ago, Shiva as Adi Guru imparted divine knowledge to the seven sages (Saptarishis) on this day. Chinese 6th month is Lotus Month (荷月 Héyuè). Sri Lankan Esala Poya commemorates the Buddha's first sermon.",
    t.category = "Lunar", t.subcategory = "Monthly Moons",
    t.aliases = ["Thunder Moon", "Hay Moon", "Wort Moon", "Berry Moon", "Horse Moon", "Guru Purnima"],
    t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tradition = "Cross-Cultural",
    t.tags = ["july", "summer", "antlers", "herbs", "guru", "sovereignty"],
    t.season = "summer",
    t.magical_focus = "Strength, masculine energy, herbal magic, teacher-student bonds, sovereignty",
    t.cross_cultural = '{"algonquin":"Buck Moon","ojibwe":"Berry Moon (Miin Giizis)","lakota":"Moon When Chokecherries Ripen","celtic":"Horse Moon","hindu":"Ashadh/Guru Purnima","chinese":"Héyuè (Lotus Month)","maori":"Hōngongoi","sri_lankan":"Esala Poya","neo_pagan":"Wort Moon"}',
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

// AUGUST — Sturgeon Moon
MERGE (t:OntologyTerm {name: "Sturgeon Moon"})
ON CREATE SET
    t.definition = "August's full moon. Named for the Great Lakes sturgeon — some over 6 feet long — most readily caught during August. The Ojibwe call it Grain Moon/Wild Rice Moon (Minoomini Giizis) — the sacred wild rice harvest, the most important food-gathering event of the Anishinaabe year. Celts call it Grain Moon or Dispute Moon — first harvest, time to resolve disputes (Lughnasadh/Lammas, Aug 1). Hindu Shravan Purnima brings Raksha Bandhan — the sacred bond between siblings, when sisters tie rakhi on brothers' wrists. Chinese 7th month is Orchid Month (兰月 Lányuè) — also Ghost Month, when spirits return to visit.",
    t.category = "Lunar", t.subcategory = "Monthly Moons",
    t.aliases = ["Green Corn Moon", "Grain Moon", "Red Moon", "Wild Rice Moon", "Shravan Purnima", "Raksha Bandhan Moon"],
    t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tradition = "Cross-Cultural",
    t.tags = ["august", "summer", "harvest", "sturgeon", "wild-rice", "sibling-bond"],
    t.season = "summer",
    t.magical_focus = "First harvest gratitude, gathering resources, sibling bonds, dispute resolution",
    t.cross_cultural = '{"algonquin":"Sturgeon Moon","ojibwe":"Wild Rice Moon (Minoomini Giizis)","lakota":"Moon of the Harvest","celtic":"Grain Moon","hindu":"Shravan Purnima (Raksha Bandhan)","chinese":"Lányuè (Orchid/Ghost Month)","maori":"Here-turi-kōkā","sri_lankan":"Nikini Poya","neo_pagan":"Wyrt Moon"}',
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

// SEPTEMBER — Corn Moon
MERGE (t:OntologyTerm {name: "Corn Moon"})
ON CREATE SET
    t.definition = "September's full moon. Named for the corn harvest at the end of the growing season. Can also be the Harvest Moon when it falls closest to the autumn equinox. The Ojibwe call it Changing Leaves Moon (Wabaabagaa Giizis). Celts call it Singing Moon or Wine Moon — harvest songs and wine-making begin (Mabon/Autumn Equinox). Hindu Bhadrapad Purnima brings Uma Maheshvara Vrata for marital harmony. Chinese 8th month is Osmanthus Month (桂月 Guìyuè) — the Mid-Autumn Festival (mooncakes, family reunion, moon viewing) is one of China's most important celebrations. Sri Lankan Binara Poya commemorates the establishment of the Buddhist order of nuns.",
    t.category = "Lunar", t.subcategory = "Monthly Moons",
    t.aliases = ["Harvest Moon", "Barley Moon", "Fruit Moon", "Singing Moon", "Wine Moon", "Bhadrapad Purnima"],
    t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tradition = "Cross-Cultural",
    t.tags = ["september", "autumn", "harvest", "equinox", "balance", "mid-autumn"],
    t.season = "autumn",
    t.magical_focus = "Harvest gratitude, balance, equinox magic, herbal preservation, wine-making",
    t.cross_cultural = '{"algonquin":"Corn Moon","ojibwe":"Changing Leaves Moon (Wabaabagaa Giizis)","lakota":"Moon When Calves Grow Hair","celtic":"Singing Moon","hindu":"Bhadrapad Purnima","chinese":"Guìyuè (Osmanthus/Mid-Autumn)","maori":"Mahuru","sri_lankan":"Binara Poya","neo_pagan":"Harvest Moon"}',
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

// OCTOBER — Hunter's Moon
MERGE (t:OntologyTerm {name: "Hunter's Moon"})
ON CREATE SET
    t.definition = "October's full moon. Named for the optimal hunting season — game fattened from summer, falling leaves reduce cover. The first full moon after the Harvest Moon. The Ojibwe call it Falling Leaves Moon (Binaakwe Giizis). Celts call it Seed Fall Moon — seeds fall for next year's growth, death feeding rebirth (Samhain, Oct 31-Nov 1). Hindu Ashvin/Sharad Purnima is remarkable — the moon is believed to radiate healing nectar (amrit). Kheer left under the moonlight absorbs this energy. Krishna's Raas Leela is commemorated. Chinese 9th month is Chrysanthemum Month (菊月 Júyuè) — Double Ninth/Chongyang Festival honors elders.",
    t.category = "Lunar", t.subcategory = "Monthly Moons",
    t.aliases = ["Blood Moon", "Sanguine Moon", "Falling Leaves Moon", "Seed Fall Moon", "Sharad Purnima"],
    t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tradition = "Cross-Cultural",
    t.tags = ["october", "autumn", "hunting", "samhain", "ancestors", "healing-nectar"],
    t.season = "autumn",
    t.magical_focus = "Hunting, culling, shadow work, ancestor communion, past life work, healing moonlight",
    t.cross_cultural = '{"algonquin":"Hunter''s Moon","ojibwe":"Falling Leaves Moon (Binaakwe Giizis)","lakota":"Moon of Changing Season","celtic":"Seed Fall Moon","hindu":"Sharad Purnima","chinese":"Júyuè (Chrysanthemum Month)","maori":"Whiringa-ā-nuku","sri_lankan":"Vap Poya","neo_pagan":"Blood Moon"}',
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

// NOVEMBER — Beaver Moon
MERGE (t:OntologyTerm {name: "Beaver Moon"})
ON CREATE SET
    t.definition = "November's full moon. Named for beavers making final winter preparations and retreating to their lodges. The Ojibwe call it Freezing Moon (Baashkaakodin Giizis) — lakes and rivers begin to freeze. The Lakota name it Moon When Deer Shed Their Antlers. Celts call it Dark Moon — the deepest darkness, veil thinnest, ancestors walk close. Hindu Kartik Purnima is Dev Deepavali — the gods celebrate their own Diwali in heaven. Shiva slaying the demon Tripurasura is commemorated. The Varanasi ghats are lit with thousands of oil lamps. Chinese 10th month is Positive Month (阳月 Yángyuè) — despite winter, yang energy begins its hidden return.",
    t.category = "Lunar", t.subcategory = "Monthly Moons",
    t.aliases = ["Frost Moon", "Freezing Moon", "Mourning Moon", "Dark Moon", "Kartik Purnima", "Dev Deepavali Moon"],
    t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tradition = "Cross-Cultural",
    t.tags = ["november", "autumn", "preparation", "ancestors", "veil", "divine-light"],
    t.season = "autumn",
    t.magical_focus = "Preparation, ancestor communion, divination, shadow work, divine celebration",
    t.cross_cultural = '{"algonquin":"Beaver Moon","ojibwe":"Freezing Moon (Baashkaakodin Giizis)","lakota":"Moon When Deer Shed Antlers","celtic":"Dark Moon","hindu":"Kartik Purnima (Dev Deepavali)","chinese":"Yángyuè (Positive Month)","maori":"Whiringa-ā-rangi","sri_lankan":"Ill Poya","neo_pagan":"Mourning Moon"}',
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

// DECEMBER — Cold Moon
MERGE (t:OntologyTerm {name: "Cold Moon"})
ON CREATE SET
    t.definition = "December's full moon. Named for winter's grip and the longest, darkest nights. The Ojibwe call it Little Spirit Moon (Minado Giisoonhs) — a quieter echo of January's Spirit Moon, completing the cycle. The Lakota name it Moon of the Popping Trees — trees crack from extreme cold in the deep silence of winter. Celts call it Oak Moon — the Oak King reigns at Yule, the return of light from the longest night (Winter Solstice). Hindu Margashirsha Purnima honors Dattatreya (combined avatar of Brahma, Vishnu, Shiva). Krishna declared: 'Among the months, I am Margashirsha.' Chinese 11th month (冬月 Dōngyuè) contains the Winter Solstice (Dōngzhì) — by calendar law, the solstice MUST fall in this month.",
    t.category = "Lunar", t.subcategory = "Monthly Moons",
    t.aliases = ["Long Night Moon", "Moon Before Yule", "Oak Moon", "Little Spirit Moon", "Margashirsha Purnima"],
    t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tradition = "Cross-Cultural",
    t.tags = ["december", "winter", "solstice", "yule", "death-rebirth", "longest-night"],
    t.season = "winter",
    t.magical_focus = "Rest, reflection, death and rebirth, solstice rituals, ancestral communion, dream work",
    t.cross_cultural = '{"algonquin":"Cold Moon","ojibwe":"Little Spirit Moon (Minado Giisoonhs)","lakota":"Moon of the Popping Trees","celtic":"Oak Moon","hindu":"Margashirsha Purnima (Datta Jayanti)","chinese":"Dōngyuè (Winter Solstice Month)","maori":"Hakihea","sri_lankan":"Unduvap Poya","neo_pagan":"Long Night Moon"}',
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

// ---------------------------------------------------------------------------
// PART 4: Special Moon Types (8)
// ---------------------------------------------------------------------------

MERGE (t:OntologyTerm {name: "Blue Moon"})
ON CREATE SET
    t.definition = "Two definitions: (1) The second full moon in a single calendar month (popular definition, from a 1946 Sky & Telescope misinterpretation). (2) The third full moon in a season with four full moons (original/seasonal definition from the Maine Farmer's Almanac). Occurs approximately every 2.5 years. Magically significant for amplified workings — goals that seem impossible, wild card manifestation, 'once in a blue moon' energy.",
    t.category = "Lunar", t.subcategory = "Special Moons",
    t.aliases = [], t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tags = ["rare", "amplified", "wild-card"],
    t.magical_focus = "Amplified magic, impossible goals, rare opportunity, wild card manifestation",
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

MERGE (t:OntologyTerm {name: "Black Moon"})
ON CREATE SET
    t.definition = "Multiple definitions: (1) The second new moon in a single calendar month. (2) A calendar month with no full moon (only February). (3) The third new moon in a season with four. Occurs approximately every 29 months. Extremely potent for dark moon workings — deep shadow integration, ancestor contact, void magic, powerful banishing, and working with the unseen.",
    t.category = "Lunar", t.subcategory = "Special Moons",
    t.aliases = [], t.confidence = 0.9, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tags = ["rare", "shadow", "void", "banishing"],
    t.magical_focus = "Shadow work, void magic, banishing, working with the unseen, ancestor contact",
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

MERGE (t:OntologyTerm {name: "Supermoon"})
ON CREATE SET
    t.definition = "A full moon occurring at or near perigee (closest approach to Earth). Appears approximately 14% larger and 30% brighter than average. Occurs 3-4 times per year. Term coined by astrologer Richard Nolle in 1979. Technically a 'perigee-syzygy.' Amplified emotional energy, heightened intuition, stronger tidal and energetic pull, enhanced manifestation potential.",
    t.category = "Lunar", t.subcategory = "Special Moons",
    t.aliases = ["Perigee Moon", "Perigee-Syzygy"], t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tags = ["amplified", "perigee", "emotional", "intuition"],
    t.magical_focus = "Amplified emotions, heightened intuition, enhanced manifestation",
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

MERGE (t:OntologyTerm {name: "Blood Moon"})
ON CREATE SET
    t.definition = "A total lunar eclipse where Earth's shadow gives the moon a reddish-copper color (from sunlight refracted through Earth's atmosphere — same physics as red sunsets). NOT the same as the Pagan 'Blood Moon' name for October's Hunter's Moon. Occurs 2-3 times per year (partial or total). Astrologically: massive transformation, portal energy, karmic culmination, death/rebirth cycles accelerated, whatever is hidden is revealed.",
    t.category = "Lunar", t.subcategory = "Special Moons",
    t.aliases = ["Lunar Eclipse", "Total Lunar Eclipse"], t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tags = ["eclipse", "transformation", "portal", "karmic"],
    t.magical_focus = "Massive transformation, karmic culmination, portal energy, revelation of hidden things",
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

MERGE (t:OntologyTerm {name: "Harvest Moon"})
ON CREATE SET
    t.definition = "The full moon closest to the autumn equinox (~September 22-23). The only full moon name determined by an equinox rather than a calendar month. Usually falls in September, but roughly every 3 years it's in October. Unique property: rises at nearly the same time for several consecutive nights, providing extended moonlight for harvesting. A moon of reaping what was sown, gratitude, abundance, and the balance point between light and dark.",
    t.category = "Lunar", t.subcategory = "Special Moons",
    t.aliases = [], t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tags = ["equinox", "harvest", "balance", "gratitude"],
    t.magical_focus = "Reaping, gratitude, abundance, culmination of seasonal work",
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

MERGE (t:OntologyTerm {name: "Void of Course Moon"})
ON CREATE SET
    t.definition = "The period after the moon makes its last major aspect in a sign before entering the next sign. Not a named moon but a critical lunar timing concept used in electional astrology. Occurs multiple times per month, lasting from minutes to hours. Actions initiated during void of course tend to 'come to nothing.' Excellent for meditation, rest, routine tasks, and releasing. Do NOT start new projects, sign contracts, or make important decisions.",
    t.category = "Lunar", t.subcategory = "Special Moons",
    t.aliases = ["VoC", "Void Moon"], t.confidence = 0.95, t.source = "researched", t.version = 1, t.is_active = true,
    t.imported_from = "bulk_ingest", t.batch_id = "moon_terms_2026-02-23",
    t.tags = ["timing", "electional", "void", "rest"],
    t.magical_focus = "Do NOT start new things. Meditate, rest, release, routine only.",
    t.created_at = datetime().epochMillis, t.updated_at = datetime().epochMillis;

// ---------------------------------------------------------------------------
// PART 5: Relationships — link moon terms together and to existing nodes
// ---------------------------------------------------------------------------

// Monthly moons → parent grouping
MATCH (parent:OntologyTerm {name: "Monthly Moon Cycle"})
MATCH (child:OntologyTerm)
WHERE child.subcategory = "Monthly Moons"
MERGE (child)-[:PART_OF]->(parent);

// Special moons → parent grouping
MATCH (parent:OntologyTerm {name: "Monthly Moon Cycle"})
MATCH (child:OntologyTerm)
WHERE child.subcategory = "Special Moons"
MERGE (child)-[:RELATED_TO {type: "special_variant"}]->(parent);

// Link to existing Transit term
MATCH (moon:OntologyTerm) WHERE moon.category = "Lunar"
MATCH (transit:OntologyTerm {name: "Transit"})
MERGE (moon)-[:RELATED_TO {type: "timing_mechanism"}]->(transit);

// Link Harvest Moon and Corn Moon (overlap concept)
MATCH (h:OntologyTerm {name: "Harvest Moon"})
MATCH (c:OntologyTerm {name: "Corn Moon"})
MERGE (h)-[:RELATED_TO {type: "overlapping_concept"}]->(c);

// Link Blood Moon (eclipse) to existing Aspect concepts
MATCH (blood:OntologyTerm {name: "Blood Moon"})
MATCH (opp:OntologyTerm {name: "Opposition"})
MERGE (blood)-[:RELATED_TO {type: "astronomical_basis"}]->(opp);

// Return summary
MATCH (t:OntologyTerm {batch_id: "moon_terms_2026-02-23"})
RETURN "Loaded " + count(t) + " moon terms" AS result;
