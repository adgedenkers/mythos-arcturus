import { useState } from "react";

// ─── INTERPRETATION ENGINE ──────────────────────────────────────────────────

const INTERPRETATIONS = {
  Moon: {
    conjunction: { keyword: "Lunar Return", area: "Emotional reset", tone: "critical" },
    opposition: { keyword: "Inner split", area: "Self vs. feelings", tone: "hard" },
    square: { keyword: "Emotional friction", area: "Inner tension", tone: "hard" },
    trine: { keyword: "Emotional ease", area: "Feeling flows", tone: "soft" },
    sextile: { keyword: "Gentle feelings", area: "Subtle comfort", tone: "soft" },
    quincunx: { keyword: "Mood drift", area: "Emotional unease", tone: "tense" },
  },
  IC: {
    conjunction: { keyword: "Root descent", area: "Home / ancestry", tone: "critical" },
    opposition: { keyword: "Private goes public", area: "Inner life exposed", tone: "hard" },
    square: { keyword: "Foundation shaken", area: "Home / safety", tone: "hard" },
    trine: { keyword: "Rooted ease", area: "Home harmony", tone: "soft" },
    sextile: { keyword: "Quiet anchor", area: "Subtle grounding", tone: "soft" },
    quincunx: { keyword: "Restless roots", area: "Home unease", tone: "tense" },
  },
  "South Node": {
    conjunction: { keyword: "Karmic pull", area: "Old patterns", tone: "critical" },
    opposition: { keyword: "Growth edge", area: "Called forward", tone: "hard" },
    square: { keyword: "Karmic friction", area: "Past vs. future", tone: "hard" },
    trine: { keyword: "Lineage flow", area: "Channel opens", tone: "soft" },
    sextile: { keyword: "Past-life whisper", area: "Subtle knowing", tone: "soft" },
    quincunx: { keyword: "Karmic itch", area: "Old pull, can't place", tone: "tense" },
  },
  Neptune: {
    conjunction: { keyword: "Psychic flood", area: "Boundaries dissolve", tone: "critical" },
    opposition: { keyword: "Fog vs. clarity", area: "Confusion / truth", tone: "hard" },
    square: { keyword: "Psychic overload", area: "Picking up everything", tone: "hard" },
    trine: { keyword: "Clean channel", area: "Downloads flow", tone: "soft" },
    sextile: { keyword: "Intuition hums", area: "Subtle psychic", tone: "soft" },
    quincunx: { keyword: "Signal noise", area: "Can't sort what's hers", tone: "tense" },
  },
  Pluto: {
    conjunction: { keyword: "Deep power surge", area: "Ancestral / shadow", tone: "critical" },
    opposition: { keyword: "Power confronted", area: "Control dynamics", tone: "hard" },
    square: { keyword: "Volcanic pressure", area: "Suppressed rage", tone: "hard" },
    trine: { keyword: "Transformation flows", area: "Deep shifts easy", tone: "soft" },
    sextile: { keyword: "Subtle depth", area: "Quiet power", tone: "soft" },
    quincunx: { keyword: "Something rising", area: "Can't name it yet", tone: "tense" },
  },
  Ascendant: {
    conjunction: { keyword: "Mask cracks", area: "Emotions visible", tone: "critical" },
    opposition: { keyword: "Projected onto others", area: "Sees self in you", tone: "hard" },
    square: { keyword: "Self-image friction", area: "How she's seen", tone: "hard" },
    trine: { keyword: "Presence softens", area: "Natural magnetism", tone: "soft" },
    sextile: { keyword: "Easy showing", area: "Gentle visibility", tone: "soft" },
    quincunx: { keyword: "Skin doesn't fit", area: "Presentation off", tone: "tense" },
  },
  MC: {
    conjunction: { keyword: "Purpose lit up", area: "Public role / calling", tone: "critical" },
    opposition: { keyword: "Purpose questioned", area: "Inner vs. outer path", tone: "hard" },
    square: { keyword: "Career pressure", area: "Public friction", tone: "hard" },
    trine: { keyword: "Purpose flows", area: "Work alignment", tone: "soft" },
    sextile: { keyword: "Subtle recognition", area: "Gentle career nudge", tone: "soft" },
    quincunx: { keyword: "Role discomfort", area: "Doesn't fit today", tone: "tense" },
  },
  Descendant: {
    conjunction: { keyword: "Relationship surge", area: "Partnership", tone: "critical" },
    opposition: { keyword: "Self vs. other", area: "Boundary with partner", tone: "hard" },
    square: { keyword: "Relationship tension", area: "Partnership friction", tone: "hard" },
    trine: { keyword: "Partnership ease", area: "Connection flows", tone: "soft" },
    sextile: { keyword: "Gentle closeness", area: "Subtle bonding", tone: "soft" },
    quincunx: { keyword: "Partner unease", area: "Something off between", tone: "tense" },
  },
  Sun: {
    conjunction: { keyword: "Identity blazes", area: "Vitality / self", tone: "critical" },
    opposition: { keyword: "Will vs. feeling", area: "Purpose tension", tone: "hard" },
    square: { keyword: "Ego friction", area: "Identity challenged", tone: "hard" },
    trine: { keyword: "Creative fire", area: "Self-expression", tone: "soft" },
    sextile: { keyword: "Quiet confidence", area: "Gentle vitality", tone: "soft" },
    quincunx: { keyword: "Identity itch", area: "Doesn't feel like herself", tone: "tense" },
  },
  Mercury: {
    conjunction: { keyword: "Words ignite", area: "Communication", tone: "critical" },
    opposition: { keyword: "Mind vs. heart", area: "Thought tension", tone: "hard" },
    square: { keyword: "Mental friction", area: "Miscommunication", tone: "hard" },
    trine: { keyword: "Thoughts flow", area: "Clear expression", tone: "soft" },
    sextile: { keyword: "Quick mind", area: "Ideas land", tone: "soft" },
    quincunx: { keyword: "Can't find words", area: "Mental fog", tone: "tense" },
  },
  Venus: {
    conjunction: { keyword: "Heart opens", area: "Love / beauty", tone: "sweet" },
    opposition: { keyword: "Love tension", area: "Values challenged", tone: "hard" },
    square: { keyword: "Heart friction", area: "Desire vs. reality", tone: "hard" },
    trine: { keyword: "Tenderness", area: "Love flows", tone: "soft" },
    sextile: { keyword: "Gentle sweetness", area: "Small pleasures", tone: "soft" },
    quincunx: { keyword: "Heart restless", area: "Wants something, unsure", tone: "tense" },
  },
  Mars: {
    conjunction: { keyword: "Drive surges", area: "Action / anger", tone: "critical" },
    opposition: { keyword: "Confrontation", area: "Pushed to fight", tone: "hard" },
    square: { keyword: "Frustration builds", area: "Blocked action", tone: "hard" },
    trine: { keyword: "Energy flows", area: "Healthy drive", tone: "soft" },
    sextile: { keyword: "Quiet initiative", area: "Subtle motivation", tone: "soft" },
    quincunx: { keyword: "Irritable edge", area: "Anger sideways", tone: "tense" },
  },
  Jupiter: {
    conjunction: { keyword: "Expansion", area: "Spirit / abundance", tone: "sweet" },
    opposition: { keyword: "Overextended", area: "Too much feeling", tone: "hard" },
    square: { keyword: "Excess pressure", area: "Overwhelm", tone: "hard" },
    trine: { keyword: "Blessings flow", area: "Grace / ease", tone: "soft" },
    sextile: { keyword: "Quiet abundance", area: "Small blessings", tone: "soft" },
    quincunx: { keyword: "Restless faith", area: "Belief questioned", tone: "tense" },
  },
  Saturn: {
    conjunction: { keyword: "Weight descends", area: "Duty / restriction", tone: "critical" },
    opposition: { keyword: "Authority pressure", area: "External limits", tone: "hard" },
    square: { keyword: "Heavy mood", area: "Doubt / burden", tone: "hard" },
    trine: { keyword: "Disciplined calm", area: "Structure helps", tone: "soft" },
    sextile: { keyword: "Steady ground", area: "Quiet discipline", tone: "soft" },
    quincunx: { keyword: "Burden shifts", area: "Responsibility nags", tone: "tense" },
  },
  Uranus: {
    conjunction: { keyword: "Lightning bolt", area: "Sudden insight", tone: "critical" },
    opposition: { keyword: "Disruption", area: "Sudden change", tone: "hard" },
    square: { keyword: "Electric tension", area: "Restless / wired", tone: "hard" },
    trine: { keyword: "Breakthrough", area: "Clean download", tone: "soft" },
    sextile: { keyword: "Subtle spark", area: "Quiet awakening", tone: "soft" },
    quincunx: { keyword: "Wired but why", area: "Restless, no source", tone: "tense" },
  },
  Lilith: {
    conjunction: { keyword: "Shadow rises", area: "Raw feminine", tone: "critical" },
    opposition: { keyword: "Shadow confronted", area: "Can't ignore it", tone: "hard" },
    square: { keyword: "Shadow friction", area: "Wildness vs. safety", tone: "hard" },
    trine: { keyword: "Shadow integrates", area: "Wild self at ease", tone: "soft" },
    sextile: { keyword: "Shadow whisper", area: "Subtle wildness", tone: "soft" },
    quincunx: { keyword: "Untamed itch", area: "Refuses to comply", tone: "tense" },
  },
  "North Node": {
    conjunction: { keyword: "Growth call", area: "Destiny nudge", tone: "critical" },
    opposition: { keyword: "Past pulls back", area: "Comfort vs. growth", tone: "hard" },
    square: { keyword: "Karmic crossroads", area: "Friction on path", tone: "hard" },
    trine: { keyword: "Growth flows", area: "Path opens", tone: "soft" },
    sextile: { keyword: "Gentle direction", area: "Subtle guidance", tone: "soft" },
    quincunx: { keyword: "Path unclear", area: "Direction shifts", tone: "tense" },
  },
};

function getEventKeyword(ev) {
  const pointInterp = INTERPRETATIONS[ev.point];
  if (!pointInterp) return { keyword: ev.point, area: ev.category, tone: "neutral" };
  const aspectInterp = pointInterp[ev.aspectName];
  if (!aspectInterp) return { keyword: ev.point, area: ev.category, tone: "neutral" };
  return aspectInterp;
}

function getDayKeywords(day) {
  const events = EVENTS.filter((e) => e.day === day);
  if (events.length === 0) return [];
  const toneWeight = { critical: 3, hard: 2.5, tense: 1.5, sweet: 2, soft: 0.5, neutral: 1 };
  const scored = events.map((ev) => {
    const interp = getEventKeyword(ev);
    return { ...interp, score: ev.intensity * (toneWeight[interp.tone] || 1), intensity: ev.intensity };
  });
  const seen = new Map();
  scored.forEach((s) => {
    const existing = seen.get(s.keyword);
    if (!existing || s.score > existing.score) seen.set(s.keyword, s);
  });
  return Array.from(seen.values()).sort((a, b) => b.score - a.score).slice(0, 4);
}

// ─── MARCH 2026 DATA ────────────────────────────────────────────────────────

const MOON_SIGNS = {
  1: { sign: "Leo", glyph: "♌", element: "Fire" },
  2: { sign: "Virgo", glyph: "♍", element: "Earth" },
  3: { sign: "Virgo", glyph: "♍", element: "Earth" },
  4: { sign: "Virgo", glyph: "♍", element: "Earth" },
  5: { sign: "Libra", glyph: "♎", element: "Air" },
  6: { sign: "Libra", glyph: "♎", element: "Air" },
  7: { sign: "Scorpio", glyph: "♏", element: "Water" },
  8: { sign: "Scorpio", glyph: "♏", element: "Water" },
  9: { sign: "Sagittarius", glyph: "♐", element: "Fire" },
  10: { sign: "Sagittarius", glyph: "♐", element: "Fire" },
  11: { sign: "Sagittarius", glyph: "♐", element: "Fire" },
  12: { sign: "Capricorn", glyph: "♑", element: "Earth" },
  13: { sign: "Capricorn", glyph: "♑", element: "Earth" },
  14: { sign: "Aquarius", glyph: "♒", element: "Air" },
  15: { sign: "Aquarius", glyph: "♒", element: "Air" },
  16: { sign: "Aquarius", glyph: "♒", element: "Air" },
  17: { sign: "Pisces", glyph: "♓", element: "Water" },
  18: { sign: "Pisces", glyph: "♓", element: "Water" },
  19: { sign: "Aries", glyph: "♈", element: "Fire" },
  20: { sign: "Aries", glyph: "♈", element: "Fire" },
  21: { sign: "Taurus", glyph: "♉", element: "Earth" },
  22: { sign: "Taurus", glyph: "♉", element: "Earth" },
  23: { sign: "Gemini", glyph: "♊", element: "Air" },
  24: { sign: "Gemini", glyph: "♊", element: "Air" },
  25: { sign: "Cancer", glyph: "♋", element: "Water" },
  26: { sign: "Cancer", glyph: "♋", element: "Water" },
  27: { sign: "Leo", glyph: "♌", element: "Fire" },
  28: { sign: "Leo", glyph: "♌", element: "Fire" },
  29: { sign: "Leo", glyph: "♌", element: "Fire" },
  30: { sign: "Virgo", glyph: "♍", element: "Earth" },
  31: { sign: "Virgo", glyph: "♍", element: "Earth" },
};

const EVENTS = [
  { day: 1, time: "01:18 AM", aspect: "⚹", aspectName: "sextile", point: "Venus", category: "HEART & DRIVE", intensity: 3 },
  { day: 1, time: "02:11 AM", aspect: "□", aspectName: "square", point: "Uranus", category: "HEAVYWEIGHTS", intensity: 12 },
  { day: 1, time: "05:45 AM", aspect: "⚻", aspectName: "quincunx", point: "Moon", category: "LUNAR CORE", intensity: 15 },
  { day: 1, time: "05:47 AM", aspect: "⚹", aspectName: "sextile", point: "Pluto", category: "PSYCHIC AXIS", intensity: 4 },
  { day: 1, time: "07:11 AM", aspect: "△", aspectName: "trine", point: "Neptune", category: "PSYCHIC AXIS", intensity: 10 },
  { day: 1, time: "11:17 PM", aspect: "☌", aspectName: "conjunction", point: "Mercury", category: "THE LIGHTS", intensity: 10 },
  { day: 2, time: "01:57 AM", aspect: "□", aspectName: "square", point: "Ascendant", category: "ANGLES", intensity: 12 },
  { day: 2, time: "01:57 AM", aspect: "□", aspectName: "square", point: "Descendant", category: "ANGLES", intensity: 8 },
  { day: 2, time: "02:11 AM", aspect: "☌", aspectName: "conjunction", point: "Sun", category: "THE LIGHTS", intensity: 15 },
  { day: 2, time: "03:11 AM", aspect: "⚻", aspectName: "quincunx", point: "South Node", category: "LUNAR CORE", intensity: 9 },
  { day: 2, time: "01:51 PM", aspect: "☌", aspectName: "conjunction", point: "Saturn", category: "HEAVYWEIGHTS", intensity: 15 },
  { day: 3, time: "04:40 AM", aspect: "☌", aspectName: "conjunction", point: "MC", category: "ANGLES", intensity: 15 },
  { day: 3, time: "04:40 AM", aspect: "☍", aspectName: "opposition", point: "IC", category: "LUNAR CORE", intensity: 20 },
  { day: 3, time: "07:15 AM", aspect: "⚹", aspectName: "sextile", point: "Uranus", category: "HEAVYWEIGHTS", intensity: 3 },
  { day: 3, time: "10:57 AM", aspect: "☍", aspectName: "opposition", point: "Moon", category: "LUNAR CORE", intensity: 20 },
  { day: 3, time: "12:27 PM", aspect: "□", aspectName: "square", point: "Neptune", category: "PSYCHIC AXIS", intensity: 20 },
  { day: 4, time: "03:47 AM", aspect: "⚹", aspectName: "sextile", point: "Lilith", category: "SHADOW", intensity: 3 },
  { day: 4, time: "08:01 AM", aspect: "⚹", aspectName: "sextile", point: "Ascendant", category: "ANGLES", intensity: 3 },
  { day: 4, time: "08:01 AM", aspect: "△", aspectName: "trine", point: "Descendant", category: "ANGLES", intensity: 4 },
  { day: 4, time: "08:45 AM", aspect: "⚹", aspectName: "sextile", point: "Jupiter", category: "HEAVYWEIGHTS", intensity: 3 },
  { day: 4, time: "09:18 AM", aspect: "☌", aspectName: "conjunction", point: "North Node", category: "SHADOW", intensity: 10 },
  { day: 4, time: "09:18 AM", aspect: "☍", aspectName: "opposition", point: "South Node", category: "LUNAR CORE", intensity: 12 },
  { day: 5, time: "08:58 AM", aspect: "☌", aspectName: "conjunction", point: "Mars", category: "HEART & DRIVE", intensity: 15 },
  { day: 5, time: "12:01 PM", aspect: "⚻", aspectName: "quincunx", point: "IC", category: "LUNAR CORE", intensity: 15 },
  { day: 5, time: "01:45 PM", aspect: "☌", aspectName: "conjunction", point: "Venus", category: "HEART & DRIVE", intensity: 15 },
  { day: 5, time: "06:37 PM", aspect: "⚻", aspectName: "quincunx", point: "Moon", category: "LUNAR CORE", intensity: 15 },
  { day: 5, time: "06:39 PM", aspect: "☌", aspectName: "conjunction", point: "Pluto", category: "PSYCHIC AXIS", intensity: 20 },
  { day: 5, time: "08:11 PM", aspect: "⚹", aspectName: "sextile", point: "Neptune", category: "PSYCHIC AXIS", intensity: 5 },
  { day: 6, time: "12:18 PM", aspect: "□", aspectName: "square", point: "Lilith", category: "SHADOW", intensity: 12 },
  { day: 6, time: "01:49 PM", aspect: "⚹", aspectName: "sextile", point: "Mercury", category: "THE LIGHTS", intensity: 2 },
  { day: 6, time: "04:45 PM", aspect: "⚻", aspectName: "quincunx", point: "Descendant", category: "ANGLES", intensity: 6 },
  { day: 6, time: "05:00 PM", aspect: "⚹", aspectName: "sextile", point: "Sun", category: "THE LIGHTS", intensity: 3 },
  { day: 6, time: "05:32 PM", aspect: "□", aspectName: "square", point: "Jupiter", category: "HEAVYWEIGHTS", intensity: 12 },
  { day: 6, time: "06:07 PM", aspect: "⚻", aspectName: "quincunx", point: "South Node", category: "LUNAR CORE", intensity: 9 },
  { day: 7, time: "05:50 AM", aspect: "⚹", aspectName: "sextile", point: "Saturn", category: "HEAVYWEIGHTS", intensity: 3 },
  { day: 7, time: "10:08 PM", aspect: "⚹", aspectName: "sextile", point: "MC", category: "ANGLES", intensity: 3 },
  { day: 7, time: "10:08 PM", aspect: "△", aspectName: "trine", point: "IC", category: "LUNAR CORE", intensity: 10 },
  { day: 8, time: "12:58 AM", aspect: "☌", aspectName: "conjunction", point: "Uranus", category: "HEAVYWEIGHTS", intensity: 15 },
  { day: 8, time: "05:02 AM", aspect: "△", aspectName: "trine", point: "Moon", category: "LUNAR CORE", intensity: 10 },
  { day: 8, time: "11:28 PM", aspect: "△", aspectName: "trine", point: "Lilith", category: "SHADOW", intensity: 6 },
  { day: 9, time: "01:03 AM", aspect: "□", aspectName: "square", point: "Mercury", category: "THE LIGHTS", intensity: 8 },
  { day: 9, time: "04:05 AM", aspect: "☌", aspectName: "conjunction", point: "Ascendant", category: "ANGLES", intensity: 15 },
  { day: 9, time: "04:05 AM", aspect: "☍", aspectName: "opposition", point: "Descendant", category: "ANGLES", intensity: 8 },
  { day: 9, time: "04:21 AM", aspect: "□", aspectName: "square", point: "Sun", category: "THE LIGHTS", intensity: 12 },
  { day: 9, time: "04:54 AM", aspect: "△", aspectName: "trine", point: "Jupiter", category: "HEAVYWEIGHTS", intensity: 6 },
  { day: 9, time: "05:30 AM", aspect: "⚹", aspectName: "sextile", point: "North Node", category: "SHADOW", intensity: 2 },
  { day: 9, time: "05:30 AM", aspect: "△", aspectName: "trine", point: "South Node", category: "LUNAR CORE", intensity: 6 },
  { day: 9, time: "05:37 PM", aspect: "□", aspectName: "square", point: "Saturn", category: "HEAVYWEIGHTS", intensity: 12 },
  { day: 10, time: "07:04 AM", aspect: "⚹", aspectName: "sextile", point: "Mars", category: "HEART & DRIVE", intensity: 3 },
  { day: 10, time: "10:19 AM", aspect: "□", aspectName: "square", point: "MC", category: "ANGLES", intensity: 12 },
  { day: 10, time: "10:19 AM", aspect: "□", aspectName: "square", point: "IC", category: "LUNAR CORE", intensity: 20 },
  { day: 10, time: "12:11 PM", aspect: "⚹", aspectName: "sextile", point: "Venus", category: "HEART & DRIVE", intensity: 3 },
  { day: 10, time: "05:21 PM", aspect: "□", aspectName: "square", point: "Moon", category: "LUNAR CORE", intensity: 20 },
  { day: 10, time: "05:23 PM", aspect: "⚹", aspectName: "sextile", point: "Pluto", category: "PSYCHIC AXIS", intensity: 4 },
  { day: 10, time: "07:01 PM", aspect: "☌", aspectName: "conjunction", point: "Neptune", category: "PSYCHIC AXIS", intensity: 25 },
  { day: 11, time: "11:59 AM", aspect: "⚻", aspectName: "quincunx", point: "Lilith", category: "SHADOW", intensity: 9 },
  { day: 11, time: "01:33 PM", aspect: "△", aspectName: "trine", point: "Mercury", category: "THE LIGHTS", intensity: 4 },
  { day: 11, time: "04:36 PM", aspect: "⚻", aspectName: "quincunx", point: "Descendant", category: "ANGLES", intensity: 6 },
  { day: 11, time: "04:52 PM", aspect: "△", aspectName: "trine", point: "Sun", category: "THE LIGHTS", intensity: 6 },
  { day: 11, time: "05:25 PM", aspect: "⚻", aspectName: "quincunx", point: "Jupiter", category: "HEAVYWEIGHTS", intensity: 9 },
  { day: 11, time: "06:01 PM", aspect: "□", aspectName: "square", point: "North Node", category: "SHADOW", intensity: 8 },
  { day: 11, time: "06:01 PM", aspect: "□", aspectName: "square", point: "South Node", category: "LUNAR CORE", intensity: 12 },
  { day: 12, time: "06:05 AM", aspect: "△", aspectName: "trine", point: "Saturn", category: "HEAVYWEIGHTS", intensity: 6 },
  { day: 12, time: "07:23 PM", aspect: "□", aspectName: "square", point: "Mars", category: "HEART & DRIVE", intensity: 12 },
  { day: 12, time: "10:34 PM", aspect: "△", aspectName: "trine", point: "MC", category: "ANGLES", intensity: 6 },
  { day: 12, time: "10:34 PM", aspect: "⚹", aspectName: "sextile", point: "IC", category: "LUNAR CORE", intensity: 5 },
  { day: 13, time: "12:23 AM", aspect: "□", aspectName: "square", point: "Venus", category: "HEART & DRIVE", intensity: 12 },
  { day: 13, time: "01:24 AM", aspect: "⚹", aspectName: "sextile", point: "Uranus", category: "HEAVYWEIGHTS", intensity: 3 },
  { day: 13, time: "05:27 AM", aspect: "⚹", aspectName: "sextile", point: "Moon", category: "LUNAR CORE", intensity: 5 },
  { day: 13, time: "05:29 AM", aspect: "□", aspectName: "square", point: "Pluto", category: "PSYCHIC AXIS", intensity: 16 },
  { day: 13, time: "11:33 PM", aspect: "☍", aspectName: "opposition", point: "Lilith", category: "SHADOW", intensity: 12 },
  { day: 14, time: "01:04 AM", aspect: "⚻", aspectName: "quincunx", point: "Mercury", category: "THE LIGHTS", intensity: 6 },
  { day: 14, time: "04:00 AM", aspect: "⚹", aspectName: "sextile", point: "Ascendant", category: "ANGLES", intensity: 3 },
  { day: 14, time: "04:00 AM", aspect: "△", aspectName: "trine", point: "Descendant", category: "ANGLES", intensity: 4 },
  { day: 14, time: "04:15 AM", aspect: "⚻", aspectName: "quincunx", point: "Sun", category: "THE LIGHTS", intensity: 9 },
  { day: 14, time: "04:47 AM", aspect: "☍", aspectName: "opposition", point: "Jupiter", category: "HEAVYWEIGHTS", intensity: 12 },
  { day: 14, time: "05:22 AM", aspect: "△", aspectName: "trine", point: "North Node", category: "SHADOW", intensity: 4 },
  { day: 14, time: "05:22 AM", aspect: "⚹", aspectName: "sextile", point: "South Node", category: "LUNAR CORE", intensity: 3 },
  { day: 14, time: "04:56 PM", aspect: "⚻", aspectName: "quincunx", point: "Saturn", category: "HEAVYWEIGHTS", intensity: 9 },
  { day: 15, time: "05:37 AM", aspect: "△", aspectName: "trine", point: "Mars", category: "HEART & DRIVE", intensity: 6 },
  { day: 15, time: "08:39 AM", aspect: "⚻", aspectName: "quincunx", point: "MC", category: "ANGLES", intensity: 9 },
  { day: 15, time: "10:22 AM", aspect: "△", aspectName: "trine", point: "Venus", category: "HEART & DRIVE", intensity: 6 },
  { day: 15, time: "11:20 AM", aspect: "□", aspectName: "square", point: "Uranus", category: "HEAVYWEIGHTS", intensity: 12 },
  { day: 15, time: "03:12 PM", aspect: "△", aspectName: "trine", point: "Pluto", category: "PSYCHIC AXIS", intensity: 8 },
  { day: 15, time: "04:43 PM", aspect: "⚹", aspectName: "sextile", point: "Neptune", category: "PSYCHIC AXIS", intensity: 5 },
  { day: 16, time: "08:16 AM", aspect: "⚻", aspectName: "quincunx", point: "Lilith", category: "SHADOW", intensity: 9 },
  { day: 16, time: "09:42 AM", aspect: "☍", aspectName: "opposition", point: "Mercury", category: "THE LIGHTS", intensity: 8 },
  { day: 16, time: "12:28 PM", aspect: "□", aspectName: "square", point: "Ascendant", category: "ANGLES", intensity: 12 },
  { day: 16, time: "12:28 PM", aspect: "□", aspectName: "square", point: "Descendant", category: "ANGLES", intensity: 8 },
  { day: 16, time: "12:42 PM", aspect: "☍", aspectName: "opposition", point: "Sun", category: "THE LIGHTS", intensity: 12 },
  { day: 16, time: "01:12 PM", aspect: "⚻", aspectName: "quincunx", point: "Jupiter", category: "HEAVYWEIGHTS", intensity: 9 },
  { day: 16, time: "01:44 PM", aspect: "⚻", aspectName: "quincunx", point: "North Node", category: "SHADOW", intensity: 6 },
  { day: 17, time: "12:38 AM", aspect: "☍", aspectName: "opposition", point: "Saturn", category: "HEAVYWEIGHTS", intensity: 12 },
  { day: 17, time: "12:33 PM", aspect: "⚻", aspectName: "quincunx", point: "Mars", category: "HEART & DRIVE", intensity: 9 },
  { day: 17, time: "03:24 PM", aspect: "☌", aspectName: "conjunction", point: "IC", category: "LUNAR CORE", intensity: 25 },
  { day: 17, time: "03:24 PM", aspect: "☍", aspectName: "opposition", point: "MC", category: "ANGLES", intensity: 12 },
  { day: 17, time: "05:02 PM", aspect: "⚻", aspectName: "quincunx", point: "Venus", category: "HEART & DRIVE", intensity: 9 },
  { day: 17, time: "05:56 PM", aspect: "△", aspectName: "trine", point: "Uranus", category: "HEAVYWEIGHTS", intensity: 6 },
  { day: 17, time: "09:33 PM", aspect: "☌", aspectName: "conjunction", point: "Moon", category: "LUNAR CORE", intensity: 25 },
  { day: 17, time: "09:35 PM", aspect: "⚻", aspectName: "quincunx", point: "Pluto", category: "PSYCHIC AXIS", intensity: 12 },
  { day: 17, time: "11:00 PM", aspect: "□", aspectName: "square", point: "Neptune", category: "PSYCHIC AXIS", intensity: 20 },
  { day: 18, time: "01:39 PM", aspect: "△", aspectName: "trine", point: "Lilith", category: "SHADOW", intensity: 6 },
  { day: 18, time: "03:00 PM", aspect: "⚻", aspectName: "quincunx", point: "Mercury", category: "THE LIGHTS", intensity: 6 },
  { day: 18, time: "05:37 PM", aspect: "△", aspectName: "trine", point: "Ascendant", category: "ANGLES", intensity: 6 },
  { day: 18, time: "05:37 PM", aspect: "⚹", aspectName: "sextile", point: "Descendant", category: "ANGLES", intensity: 2 },
  { day: 18, time: "05:50 PM", aspect: "⚻", aspectName: "quincunx", point: "Sun", category: "THE LIGHTS", intensity: 9 },
  { day: 18, time: "06:19 PM", aspect: "△", aspectName: "trine", point: "Jupiter", category: "HEAVYWEIGHTS", intensity: 6 },
  { day: 18, time: "06:49 PM", aspect: "☌", aspectName: "conjunction", point: "South Node", category: "LUNAR CORE", intensity: 15 },
  { day: 18, time: "06:49 PM", aspect: "☍", aspectName: "opposition", point: "North Node", category: "SHADOW", intensity: 8 },
  { day: 19, time: "05:08 AM", aspect: "⚻", aspectName: "quincunx", point: "Saturn", category: "HEAVYWEIGHTS", intensity: 9 },
  { day: 19, time: "04:28 PM", aspect: "☍", aspectName: "opposition", point: "Mars", category: "HEART & DRIVE", intensity: 12 },
  { day: 19, time: "07:12 PM", aspect: "⚻", aspectName: "quincunx", point: "MC", category: "ANGLES", intensity: 9 },
  { day: 19, time: "08:45 PM", aspect: "☍", aspectName: "opposition", point: "Venus", category: "HEART & DRIVE", intensity: 12 },
  { day: 19, time: "09:37 PM", aspect: "⚻", aspectName: "quincunx", point: "Uranus", category: "HEAVYWEIGHTS", intensity: 9 },
  { day: 20, time: "01:05 AM", aspect: "☍", aspectName: "opposition", point: "Pluto", category: "PSYCHIC AXIS", intensity: 16 },
  { day: 20, time: "02:27 AM", aspect: "△", aspectName: "trine", point: "Neptune", category: "PSYCHIC AXIS", intensity: 10 },
  { day: 20, time: "04:32 PM", aspect: "□", aspectName: "square", point: "Lilith", category: "SHADOW", intensity: 12 },
  { day: 20, time: "05:50 PM", aspect: "△", aspectName: "trine", point: "Mercury", category: "THE LIGHTS", intensity: 4 },
  { day: 20, time: "08:22 PM", aspect: "⚻", aspectName: "quincunx", point: "Ascendant", category: "ANGLES", intensity: 9 },
  { day: 20, time: "08:34 PM", aspect: "△", aspectName: "trine", point: "Sun", category: "THE LIGHTS", intensity: 6 },
  { day: 20, time: "09:02 PM", aspect: "□", aspectName: "square", point: "Jupiter", category: "HEAVYWEIGHTS", intensity: 12 },
  { day: 20, time: "09:32 PM", aspect: "⚻", aspectName: "quincunx", point: "North Node", category: "SHADOW", intensity: 6 },
  { day: 21, time: "07:32 AM", aspect: "△", aspectName: "trine", point: "Saturn", category: "HEAVYWEIGHTS", intensity: 6 },
  { day: 21, time: "06:35 PM", aspect: "⚻", aspectName: "quincunx", point: "Mars", category: "HEART & DRIVE", intensity: 9 },
  { day: 21, time: "09:15 PM", aspect: "△", aspectName: "trine", point: "MC", category: "ANGLES", intensity: 6 },
  { day: 21, time: "09:15 PM", aspect: "⚹", aspectName: "sextile", point: "IC", category: "LUNAR CORE", intensity: 5 },
  { day: 21, time: "10:46 PM", aspect: "⚻", aspectName: "quincunx", point: "Venus", category: "HEART & DRIVE", intensity: 9 },
  { day: 21, time: "11:37 PM", aspect: "☍", aspectName: "opposition", point: "Uranus", category: "HEAVYWEIGHTS", intensity: 12 },
  { day: 22, time: "03:01 AM", aspect: "⚹", aspectName: "sextile", point: "Moon", category: "LUNAR CORE", intensity: 5 },
  { day: 22, time: "03:03 AM", aspect: "⚻", aspectName: "quincunx", point: "Pluto", category: "PSYCHIC AXIS", intensity: 12 },
  { day: 22, time: "04:23 AM", aspect: "⚻", aspectName: "quincunx", point: "Neptune", category: "PSYCHIC AXIS", intensity: 15 },
  { day: 22, time: "06:18 PM", aspect: "⚹", aspectName: "sextile", point: "Lilith", category: "SHADOW", intensity: 3 },
  { day: 22, time: "07:36 PM", aspect: "□", aspectName: "square", point: "Mercury", category: "THE LIGHTS", intensity: 8 },
  { day: 22, time: "10:06 PM", aspect: "☌", aspectName: "conjunction", point: "Descendant", category: "ANGLES", intensity: 10 },
  { day: 22, time: "10:06 PM", aspect: "☍", aspectName: "opposition", point: "Ascendant", category: "ANGLES", intensity: 12 },
  { day: 22, time: "10:19 PM", aspect: "□", aspectName: "square", point: "Sun", category: "THE LIGHTS", intensity: 12 },
  { day: 22, time: "10:47 PM", aspect: "⚹", aspectName: "sextile", point: "Jupiter", category: "HEAVYWEIGHTS", intensity: 3 },
  { day: 22, time: "11:16 PM", aspect: "△", aspectName: "trine", point: "North Node", category: "SHADOW", intensity: 4 },
  { day: 22, time: "11:16 PM", aspect: "⚹", aspectName: "sextile", point: "South Node", category: "LUNAR CORE", intensity: 3 },
  { day: 23, time: "09:15 AM", aspect: "□", aspectName: "square", point: "Saturn", category: "HEAVYWEIGHTS", intensity: 12 },
  { day: 23, time: "08:21 PM", aspect: "△", aspectName: "trine", point: "Mars", category: "HEART & DRIVE", intensity: 6 },
  { day: 23, time: "11:02 PM", aspect: "□", aspectName: "square", point: "MC", category: "ANGLES", intensity: 12 },
  { day: 23, time: "11:02 PM", aspect: "□", aspectName: "square", point: "IC", category: "LUNAR CORE", intensity: 20 },
  { day: 24, time: "12:34 AM", aspect: "△", aspectName: "trine", point: "Venus", category: "HEART & DRIVE", intensity: 6 },
  { day: 24, time: "01:25 AM", aspect: "⚻", aspectName: "quincunx", point: "Uranus", category: "HEAVYWEIGHTS", intensity: 9 },
  { day: 24, time: "04:51 AM", aspect: "□", aspectName: "square", point: "Moon", category: "LUNAR CORE", intensity: 20 },
  { day: 24, time: "04:53 AM", aspect: "△", aspectName: "trine", point: "Pluto", category: "PSYCHIC AXIS", intensity: 8 },
  { day: 24, time: "06:14 AM", aspect: "☍", aspectName: "opposition", point: "Neptune", category: "PSYCHIC AXIS", intensity: 20 },
  { day: 24, time: "09:40 PM", aspect: "⚹", aspectName: "sextile", point: "Mercury", category: "THE LIGHTS", intensity: 2 },
  { day: 25, time: "12:13 AM", aspect: "⚻", aspectName: "quincunx", point: "Ascendant", category: "ANGLES", intensity: 9 },
  { day: 25, time: "12:26 AM", aspect: "⚹", aspectName: "sextile", point: "Sun", category: "THE LIGHTS", intensity: 3 },
  { day: 25, time: "01:24 AM", aspect: "□", aspectName: "square", point: "North Node", category: "SHADOW", intensity: 8 },
  { day: 25, time: "01:24 AM", aspect: "□", aspectName: "square", point: "South Node", category: "LUNAR CORE", intensity: 12 },
  { day: 25, time: "11:36 AM", aspect: "⚹", aspectName: "sextile", point: "Saturn", category: "HEAVYWEIGHTS", intensity: 3 },
  { day: 25, time: "10:58 PM", aspect: "□", aspectName: "square", point: "Mars", category: "HEART & DRIVE", intensity: 12 },
  { day: 26, time: "01:43 AM", aspect: "⚹", aspectName: "sextile", point: "MC", category: "ANGLES", intensity: 3 },
  { day: 26, time: "01:43 AM", aspect: "△", aspectName: "trine", point: "IC", category: "LUNAR CORE", intensity: 10 },
  { day: 26, time: "03:18 AM", aspect: "□", aspectName: "square", point: "Venus", category: "HEART & DRIVE", intensity: 12 },
  { day: 26, time: "04:10 AM", aspect: "△", aspectName: "trine", point: "Uranus", category: "HEAVYWEIGHTS", intensity: 6 },
  { day: 26, time: "07:41 AM", aspect: "△", aspectName: "trine", point: "Moon", category: "LUNAR CORE", intensity: 10 },
  { day: 26, time: "07:43 AM", aspect: "□", aspectName: "square", point: "Pluto", category: "PSYCHIC AXIS", intensity: 16 },
  { day: 26, time: "09:07 AM", aspect: "⚻", aspectName: "quincunx", point: "Neptune", category: "PSYCHIC AXIS", intensity: 15 },
  { day: 26, time: "11:39 PM", aspect: "☌", aspectName: "conjunction", point: "Lilith", category: "SHADOW", intensity: 15 },
  { day: 27, time: "03:38 AM", aspect: "△", aspectName: "trine", point: "Ascendant", category: "ANGLES", intensity: 6 },
  { day: 27, time: "03:38 AM", aspect: "⚹", aspectName: "sextile", point: "Descendant", category: "ANGLES", intensity: 2 },
  { day: 27, time: "04:21 AM", aspect: "☌", aspectName: "conjunction", point: "Jupiter", category: "HEAVYWEIGHTS", intensity: 15 },
  { day: 27, time: "04:52 AM", aspect: "⚹", aspectName: "sextile", point: "North Node", category: "SHADOW", intensity: 2 },
  { day: 27, time: "04:52 AM", aspect: "△", aspectName: "trine", point: "South Node", category: "LUNAR CORE", intensity: 6 },
  { day: 28, time: "03:08 AM", aspect: "⚹", aspectName: "sextile", point: "Mars", category: "HEART & DRIVE", intensity: 3 },
  { day: 28, time: "05:59 AM", aspect: "⚻", aspectName: "quincunx", point: "IC", category: "LUNAR CORE", intensity: 15 },
  { day: 28, time: "07:36 AM", aspect: "⚹", aspectName: "sextile", point: "Venus", category: "HEART & DRIVE", intensity: 3 },
  { day: 28, time: "08:31 AM", aspect: "□", aspectName: "square", point: "Uranus", category: "HEAVYWEIGHTS", intensity: 12 },
  { day: 28, time: "12:09 PM", aspect: "⚻", aspectName: "quincunx", point: "Moon", category: "LUNAR CORE", intensity: 15 },
  { day: 28, time: "12:11 PM", aspect: "⚹", aspectName: "sextile", point: "Pluto", category: "PSYCHIC AXIS", intensity: 4 },
  { day: 28, time: "01:38 PM", aspect: "△", aspectName: "trine", point: "Neptune", category: "PSYCHIC AXIS", intensity: 10 },
  { day: 29, time: "06:04 AM", aspect: "☌", aspectName: "conjunction", point: "Mercury", category: "THE LIGHTS", intensity: 10 },
  { day: 29, time: "08:48 AM", aspect: "□", aspectName: "square", point: "Ascendant", category: "ANGLES", intensity: 12 },
  { day: 29, time: "08:48 AM", aspect: "□", aspectName: "square", point: "Descendant", category: "ANGLES", intensity: 8 },
  { day: 29, time: "09:02 AM", aspect: "☌", aspectName: "conjunction", point: "Sun", category: "THE LIGHTS", intensity: 15 },
  { day: 29, time: "10:04 AM", aspect: "⚻", aspectName: "quincunx", point: "South Node", category: "LUNAR CORE", intensity: 9 },
  { day: 29, time: "08:57 PM", aspect: "☌", aspectName: "conjunction", point: "Saturn", category: "HEAVYWEIGHTS", intensity: 15 },
  { day: 30, time: "12:04 PM", aspect: "☌", aspectName: "conjunction", point: "MC", category: "ANGLES", intensity: 15 },
  { day: 30, time: "12:04 PM", aspect: "☍", aspectName: "opposition", point: "IC", category: "LUNAR CORE", intensity: 20 },
  { day: 30, time: "02:41 PM", aspect: "⚹", aspectName: "sextile", point: "Uranus", category: "HEAVYWEIGHTS", intensity: 3 },
  { day: 30, time: "06:28 PM", aspect: "☍", aspectName: "opposition", point: "Moon", category: "LUNAR CORE", intensity: 20 },
  { day: 30, time: "07:59 PM", aspect: "□", aspectName: "square", point: "Neptune", category: "PSYCHIC AXIS", intensity: 20 },
  { day: 31, time: "11:33 AM", aspect: "⚹", aspectName: "sextile", point: "Lilith", category: "SHADOW", intensity: 3 },
  { day: 31, time: "03:51 PM", aspect: "⚹", aspectName: "sextile", point: "Ascendant", category: "ANGLES", intensity: 3 },
  { day: 31, time: "03:51 PM", aspect: "△", aspectName: "trine", point: "Descendant", category: "ANGLES", intensity: 4 },
  { day: 31, time: "04:36 PM", aspect: "⚹", aspectName: "sextile", point: "Jupiter", category: "HEAVYWEIGHTS", intensity: 3 },
  { day: 31, time: "05:09 PM", aspect: "☌", aspectName: "conjunction", point: "North Node", category: "SHADOW", intensity: 10 },
  { day: 31, time: "05:09 PM", aspect: "☍", aspectName: "opposition", point: "South Node", category: "LUNAR CORE", intensity: 12 },
];

const SPECIAL_DAYS = {
  5: { label: "HEART OPENING", color: "#4ade80", icon: "💚" },
  10: { label: "PSYCHIC FLOODING", color: "#f97316", icon: "🟠" },
  17: { label: "LUNAR RETURN", color: "#ef4444", icon: "🔴" },
};

const ELEMENT_COLORS = {
  Fire: { bg: "#1a0f08", border: "#b45309", text: "#fbbf24", subtle: "#92400e" },
  Earth: { bg: "#0a1a0a", border: "#15803d", text: "#86efac", subtle: "#166534" },
  Air: { bg: "#0c0c1a", border: "#6366f1", text: "#a5b4fc", subtle: "#4338ca" },
  Water: { bg: "#081520", border: "#0ea5e9", text: "#7dd3fc", subtle: "#0369a1" },
};

const CATEGORY_COLORS = {
  "LUNAR CORE": "#c084fc", "PSYCHIC AXIS": "#f472b6", "ANGLES": "#60a5fa",
  "THE LIGHTS": "#fbbf24", "HEART & DRIVE": "#f87171", "HEAVYWEIGHTS": "#a78bfa", "SHADOW": "#94a3b8",
};

const TONE_COLORS = { critical: "#ef4444", hard: "#f97316", tense: "#eab308", sweet: "#4ade80", soft: "#67e8f9", neutral: "#94a3b8" };

const ASPECT_STYLES = {
  conjunction: { color: "#fbbf24", weight: "bold" }, opposition: { color: "#f87171", weight: "bold" },
  square: { color: "#fb923c", weight: "normal" }, trine: { color: "#4ade80", weight: "normal" },
  sextile: { color: "#67e8f9", weight: "normal" }, quincunx: { color: "#a78bfa", weight: "normal" },
};

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function getDayEvents(day) { return EVENTS.filter((e) => e.day === day); }
function getDayIntensity(day) { const e = getDayEvents(day); return e.length === 0 ? 0 : e.reduce((s, ev) => s + ev.intensity, 0); }
function getMaxIntensity() { let m = 0; for (let d = 1; d <= 31; d++) m = Math.max(m, getDayIntensity(d)); return m; }
function getDayCategories(day) {
  const cats = {}; getDayEvents(day).forEach((e) => { cats[e.category] = (cats[e.category] || 0) + e.intensity; });
  return Object.entries(cats).sort((a, b) => b[1] - a[1]).map(([c]) => c);
}

function IntensityBar({ value, max }) {
  const pct = Math.min((value / max) * 100, 100);
  const hue = pct > 70 ? 0 : pct > 40 ? 30 : 140;
  return (
    <div style={{ width: "100%", height: 3, borderRadius: 2, background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
      <div style={{ width: `${pct}%`, height: "100%", borderRadius: 2, background: `hsl(${hue}, 80%, 55%)` }} />
    </div>
  );
}

function DayCell({ day, isSelected, onClick }) {
  const moonData = MOON_SIGNS[day];
  const elem = ELEMENT_COLORS[moonData.element];
  const intensity = getDayIntensity(day);
  const maxI = getMaxIntensity();
  const special = SPECIAL_DAYS[day];
  const keywords = getDayKeywords(day);

  return (
    <div onClick={() => onClick(day)} style={{
      background: isSelected ? "rgba(255,255,255,0.08)" : elem.bg,
      border: `1px solid ${isSelected ? elem.text : "rgba(255,255,255,0.06)"}`,
      borderRadius: 6, padding: "5px 6px", cursor: "pointer", position: "relative",
      minHeight: 130, display: "flex", flexDirection: "column", transition: "all 0.15s ease", overflow: "hidden",
    }}>
      {special && <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: special.color }} />}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 2 }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: "#e2e8f0", fontFamily: "'JetBrains Mono', monospace" }}>{day}</span>
        <span style={{ fontSize: 15 }} title={moonData.sign}>{moonData.glyph}</span>
      </div>
      <div style={{ fontSize: 9, color: elem.text, fontFamily: "'JetBrains Mono', monospace", opacity: 0.7, marginBottom: 3 }}>{moonData.sign}</div>
      <IntensityBar value={intensity} max={maxI} />
      <div style={{ fontSize: 8, color: "rgba(255,255,255,0.35)", marginTop: 1, fontFamily: "'JetBrains Mono', monospace" }}>{intensity}</div>
      {keywords.length > 0 && (
        <div style={{ marginTop: "auto", paddingTop: 3, borderTop: "1px solid rgba(255,255,255,0.04)", display: "flex", flexDirection: "column", gap: 1 }}>
          {keywords.map((kw, i) => (
            <div key={i} style={{ fontSize: 8.5, lineHeight: 1.2, color: TONE_COLORS[kw.tone] || "#94a3b8", fontFamily: "'JetBrains Mono', monospace", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {kw.keyword}
            </div>
          ))}
        </div>
      )}
      {special && <div style={{ position: "absolute", top: 4, right: 4, fontSize: 9 }}>{special.icon}</div>}
    </div>
  );
}

function DayDetail({ day, onClose }) {
  const moonData = MOON_SIGNS[day];
  const elem = ELEMENT_COLORS[moonData.element];
  const events = getDayEvents(day);
  const intensity = getDayIntensity(day);
  const special = SPECIAL_DAYS[day];
  const categories = getDayCategories(day);
  const keywords = getDayKeywords(day);

  return (
    <div style={{ background: "#0f1117", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 10, padding: 20, marginTop: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 16 }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{ fontSize: 28, fontWeight: 700, color: "#e2e8f0", fontFamily: "'Cinzel', serif" }}>March {day}</span>
            <span style={{ fontSize: 28 }}>{moonData.glyph}</span>
            {special && <span style={{ fontSize: 16 }}>{special.icon}</span>}
          </div>
          <div style={{ fontSize: 14, color: elem.text, marginTop: 4, fontFamily: "'JetBrains Mono', monospace" }}>Moon in {moonData.sign} · {moonData.element}</div>
          {special && <div style={{ display: "inline-block", marginTop: 8, padding: "3px 10px", background: special.color + "22", border: `1px solid ${special.color}55`, borderRadius: 4, fontSize: 11, fontWeight: 600, color: special.color, fontFamily: "'JetBrains Mono', monospace", letterSpacing: "0.05em" }}>{special.label}</div>}
        </div>
        <button onClick={onClose} style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6, color: "#94a3b8", cursor: "pointer", padding: "4px 10px", fontSize: 13 }}>✕</button>
      </div>
      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        <div style={{ padding: "6px 12px", borderRadius: 6, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)" }}>
          <div style={{ fontSize: 9, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.08em", fontFamily: "'JetBrains Mono', monospace" }}>Intensity</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: "#e2e8f0", fontFamily: "'JetBrains Mono', monospace" }}>{intensity}</div>
        </div>
        <div style={{ padding: "6px 12px", borderRadius: 6, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)" }}>
          <div style={{ fontSize: 9, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.08em", fontFamily: "'JetBrains Mono', monospace" }}>Aspects</div>
          <div style={{ fontSize: 22, fontWeight: 700, color: "#e2e8f0", fontFamily: "'JetBrains Mono', monospace" }}>{events.length}</div>
        </div>
        <div style={{ padding: "6px 12px", borderRadius: 6, flex: 1, minWidth: 160, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)" }}>
          <div style={{ fontSize: 9, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.08em", fontFamily: "'JetBrains Mono', monospace", marginBottom: 4 }}>Areas</div>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {categories.map((cat) => <span key={cat} style={{ fontSize: 10, padding: "2px 6px", borderRadius: 3, background: CATEGORY_COLORS[cat] + "22", color: CATEGORY_COLORS[cat], fontFamily: "'JetBrains Mono', monospace" }}>{cat}</span>)}
          </div>
        </div>
      </div>
      <div style={{ background: "rgba(255,255,255,0.03)", borderRadius: 8, padding: 14, border: "1px solid rgba(255,255,255,0.06)", marginBottom: 16 }}>
        <div style={{ fontSize: 9, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.1em", fontFamily: "'JetBrains Mono', monospace", marginBottom: 10 }}>What she feels today</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
          {keywords.map((kw, i) => (
            <div key={i} style={{ padding: "6px 10px", borderRadius: 6, background: (TONE_COLORS[kw.tone] || "#666") + "15", border: `1px solid ${(TONE_COLORS[kw.tone] || "#666")}30` }}>
              <div style={{ fontSize: 12, fontWeight: 600, color: TONE_COLORS[kw.tone] || "#e2e8f0", fontFamily: "'JetBrains Mono', monospace" }}>{kw.keyword}</div>
              <div style={{ fontSize: 10, color: "rgba(255,255,255,0.5)", fontFamily: "'JetBrains Mono', monospace", marginTop: 2 }}>{kw.area}</div>
            </div>
          ))}
        </div>
      </div>
      <div style={{ background: "rgba(255,255,255,0.02)", borderRadius: 6, border: "1px solid rgba(255,255,255,0.06)", overflow: "hidden" }}>
        <div style={{ display: "grid", gridTemplateColumns: "70px 28px 1fr auto 55px", padding: "8px 12px", borderBottom: "1px solid rgba(255,255,255,0.06)", fontSize: 9, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.08em", fontFamily: "'JetBrains Mono', monospace" }}>
          <span>Time</span><span></span><span>Transit</span><span>Meaning</span><span style={{ textAlign: "right" }}>Power</span>
        </div>
        {events.sort((a, b) => {
          const isPMA = a.time.includes("PM"), isPMB = b.time.includes("PM");
          let hA = parseInt(a.time); if (isPMA && hA !== 12) hA += 12; if (!isPMA && hA === 12) hA = 0;
          let hB = parseInt(b.time); if (isPMB && hB !== 12) hB += 12; if (!isPMB && hB === 12) hB = 0;
          return hA - hB || a.time.localeCompare(b.time);
        }).map((ev, i) => {
          const aspStyle = ASPECT_STYLES[ev.aspectName] || {};
          const interp = getEventKeyword(ev);
          return (
            <div key={i} style={{ display: "grid", gridTemplateColumns: "70px 28px 1fr auto 55px", padding: "6px 12px", borderBottom: "1px solid rgba(255,255,255,0.03)", alignItems: "center" }}>
              <span style={{ fontSize: 11, color: "#94a3b8", fontFamily: "'JetBrains Mono', monospace" }}>{ev.time}</span>
              <span style={{ fontSize: 15, color: aspStyle.color || "#999", textAlign: "center" }}>{ev.aspect}</span>
              <div>
                <span style={{ fontSize: 12, color: aspStyle.color || "#e2e8f0", fontWeight: aspStyle.weight || "normal", fontFamily: "'JetBrains Mono', monospace" }}>{ev.point}</span>
                <span style={{ fontSize: 9, marginLeft: 8, color: CATEGORY_COLORS[ev.category] || "#666", opacity: 0.7, fontFamily: "'JetBrains Mono', monospace" }}>{ev.category}</span>
              </div>
              <span style={{ fontSize: 10, color: TONE_COLORS[interp.tone] || "#94a3b8", fontFamily: "'JetBrains Mono', monospace", paddingRight: 8 }}>{interp.keyword}</span>
              <div style={{ textAlign: "right" }}>
                <span style={{ fontSize: 11, fontWeight: 600, color: ev.intensity >= 20 ? "#f87171" : ev.intensity >= 12 ? "#fbbf24" : "#86efac", fontFamily: "'JetBrains Mono', monospace" }}>{ev.intensity}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function Legend() {
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 10, padding: "10px 14px", background: "rgba(255,255,255,0.02)", borderRadius: 8, border: "1px solid rgba(255,255,255,0.06)", marginBottom: 14 }}>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, width: "100%" }}>
        <span style={{ fontSize: 9, color: "#64748b", fontFamily: "'JetBrains Mono', monospace", textTransform: "uppercase", letterSpacing: "0.08em", marginRight: 4 }}>Tone:</span>
        {Object.entries(TONE_COLORS).map(([t, c]) => <div key={t} style={{ display: "flex", alignItems: "center", gap: 3 }}><div style={{ width: 6, height: 6, borderRadius: 1, background: c }} /><span style={{ fontSize: 9, color: "#94a3b8", fontFamily: "'JetBrains Mono', monospace" }}>{t}</span></div>)}
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 8, width: "100%" }}>
        <span style={{ fontSize: 9, color: "#64748b", fontFamily: "'JetBrains Mono', monospace", textTransform: "uppercase", letterSpacing: "0.08em", marginRight: 4 }}>Element:</span>
        {Object.entries(ELEMENT_COLORS).map(([e, c]) => <div key={e} style={{ display: "flex", alignItems: "center", gap: 3 }}><div style={{ width: 10, height: 7, borderRadius: 2, background: c.bg, border: `1px solid ${c.border}` }} /><span style={{ fontSize: 9, color: c.text, fontFamily: "'JetBrains Mono', monospace" }}>{e}</span></div>)}
      </div>
    </div>
  );
}

export default function SerapheLunarCalendar() {
  const [selectedDay, setSelectedDay] = useState(null);
  const startDayOfWeek = new Date(2026, 2, 1).getDay();
  const cells = [];
  for (let i = 0; i < startDayOfWeek; i++) cells.push(null);
  for (let d = 1; d <= 31; d++) cells.push(d);

  return (
    <div style={{ background: "#0a0b0f", minHeight: "100vh", padding: "20px 12px", fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" }}>
      <div style={{ maxWidth: 980, margin: "0 auto" }}>
        <div style={{ textAlign: "center", marginBottom: 20 }}>
          <div style={{ fontSize: 10, color: "#64748b", textTransform: "uppercase", letterSpacing: "0.2em", fontFamily: "'JetBrains Mono', monospace", marginBottom: 4 }}>Seraphe · Lunar Transit Map</div>
          <h1 style={{ fontSize: 32, fontWeight: 300, color: "#e2e8f0", fontFamily: "'Cinzel', serif", margin: 0, letterSpacing: "0.04em" }}>March 2026</h1>
          <div style={{ fontSize: 11, color: "#475569", fontFamily: "'JetBrains Mono', monospace", marginTop: 4 }}>194 aspects · 16 natal points · Swiss Ephemeris · EDT</div>
        </div>
        <Legend />
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 4, marginBottom: 4 }}>
          {WEEKDAYS.map((wd) => <div key={wd} style={{ textAlign: "center", fontSize: 10, color: "#475569", fontFamily: "'JetBrains Mono', monospace", textTransform: "uppercase", letterSpacing: "0.1em", padding: "3px 0" }}>{wd}</div>)}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(7, 1fr)", gap: 4 }}>
          {cells.map((day, i) => day === null ? <div key={`e-${i}`} style={{ minHeight: 130 }} /> : <DayCell key={day} day={day} isSelected={selectedDay === day} onClick={setSelectedDay} />)}
        </div>
        {selectedDay && <DayDetail day={selectedDay} onClose={() => setSelectedDay(null)} />}
        <div style={{ textAlign: "center", marginTop: 16, fontSize: 9, color: "#334155", fontFamily: "'JetBrains Mono', monospace" }}>Birth: August 19, 1978 · 2:02 PM EDT · Norwich, NY · Placidus · Swiss Ephemeris</div>
      </div>
    </div>
  );
}
