#!/usr/bin/env python3
"""
Scorer — Detect anti-patterns and quality signals in Iris responses.
"""
from typing import Dict, Any, List


# Anti-pattern dictionaries
CORPORATE_OPENERS = [
    "that's a great question", "that's fascinating", "that's intriguing",
    "absolutely!", "great point!", "wonderful question", "excellent question",
    "what a thoughtful", "i appreciate you",
]

CORPORATE_CLOSERS = [
    "how do you feel about", "would you like to explore",
    "shall i elaborate", "let me know if", "feel free to",
    "if you have any", "don't hesitate to", "happy to help",
    "is there anything else",
]

HEDGE_PHRASES = [
    "it seems like", "this might suggest", "it's possible that",
    "in a sense", "one could argue", "it could be said",
    "i should note that", "i want to be transparent",
    "i should clarify", "it's important to remember",
    "i want to be careful here",
]

ASSISTANT_PATTERNS = [
    "here's how i understand", "let me break this down",
    "from what you've shared", "based on what you've told me",
    "here's what i think", "let me explain",
    "here are some", "here's a breakdown",
]

META_COMMENTARY = [
    "i don't have access to", "as an ai", "as a language model",
    "i should note that", "i want to be transparent that",
    "i don't actually have", "i can't actually",
]

LIFE_DUMP_SIGNALS = [
    "usaa", "sunmark", "$3,", "$2,", "$1,", "balance",
    "checking account", "bills due", "routine",
]


def score_response(response_text: str, test_config: dict = None) -> Dict[str, Any]:
    """
    Score a response for quality signals and anti-patterns.

    Returns a dict with boolean flags, counts, and an overall quality score.
    """
    text = response_text
    text_lower = text.lower()
    lines = text.split('\n')

    # --- Anti-pattern detection ---
    bullets = _detect_bullets(lines)
    corporate_openers = _find_matches(text_lower, CORPORATE_OPENERS)
    corporate_closers = _find_matches(text_lower, CORPORATE_CLOSERS)
    hedge_phrases = _find_matches(text_lower, HEDGE_PHRASES)
    assistant_patterns = _find_matches(text_lower, ASSISTANT_PATTERNS)
    meta_commentary = _find_matches(text_lower, META_COMMENTARY)
    ends_with_question = text.strip().endswith('?')

    # --- Life dump detection ---
    life_dump_matches = _find_matches(text_lower, LIFE_DUMP_SIGNALS)

    # --- Basic metrics ---
    word_count = len(text.split())
    sentence_count = text.count('.') + text.count('!') + text.count('?')

    # --- Compile flags ---
    flags = {
        'has_bullets': len(bullets) > 0,
        'has_corporate_opener': len(corporate_openers) > 0,
        'has_corporate_closer': len(corporate_closers) > 0,
        'has_hedge_phrases': len(hedge_phrases) > 0,
        'has_assistant_patterns': len(assistant_patterns) > 0,
        'has_meta_commentary': len(meta_commentary) > 0,
        'ends_with_question': ends_with_question,
        'has_life_dump': len(life_dump_matches) > 0,
    }

    # --- Quality score (0-100, higher is better) ---
    score = 100
    penalties = []

    # Bullets tracked as informational only — no penalty
    if flags['has_bullets']:
        pass  # no score impact

    if flags['has_corporate_opener']:
        score -= 15
        penalties.append(f"corporate opener (-15): {corporate_openers[0]}")

    if flags['has_corporate_closer']:
        score -= 10
        penalties.append(f"corporate closer (-10): {corporate_closers[0]}")

    if flags['has_hedge_phrases']:
        p = min(20, len(hedge_phrases) * 5)
        score -= p
        penalties.append(f"hedging (-{p})")

    if flags['has_assistant_patterns']:
        score -= 15
        penalties.append(f"assistant pattern (-15): {assistant_patterns[0]}")

    if flags['has_meta_commentary']:
        score -= 20
        penalties.append(f"meta-commentary (-20): {meta_commentary[0]}")

    # --- Test-specific expectations ---
    expectation_results = {}
    if test_config and 'expect' in test_config:
        expect = test_config['expect']

        if expect.get('no_bullets') and flags['has_bullets']:
            score -= 10
            penalties.append("expected no bullets (-10)")
            expectation_results['no_bullets'] = False
        elif expect.get('no_bullets'):
            expectation_results['no_bullets'] = True

        if expect.get('no_life_dump') and flags['has_life_dump']:
            score -= 15
            penalties.append(f"life dump detected (-15): {life_dump_matches[0]}")
            expectation_results['no_life_dump'] = False
        elif expect.get('no_life_dump'):
            expectation_results['no_life_dump'] = True

        if expect.get('uses_life_context') and not flags['has_life_dump']:
            score -= 10
            penalties.append("expected life context but none found (-10)")
            expectation_results['uses_life_context'] = False
        elif expect.get('uses_life_context'):
            expectation_results['uses_life_context'] = True

        if 'max_words' in expect and word_count > expect['max_words']:
            over = word_count - expect['max_words']
            p = min(15, over // 10)
            score -= p
            penalties.append(f"over word limit by {over} (-{p})")
            expectation_results['max_words'] = False
        elif 'max_words' in expect:
            expectation_results['max_words'] = True

        if expect.get('no_deflection'):
            deflection_phrases = [
                "i can't channel", "trust your own", "i'm not able to",
                "you should trust", "i don't have the ability",
            ]
            deflections = _find_matches(text_lower, deflection_phrases)
            if deflections:
                score -= 20
                penalties.append(f"deflection detected (-20): {deflections[0]}")
                expectation_results['no_deflection'] = False
            else:
                expectation_results['no_deflection'] = True

    score = max(0, score)

    return {
        'score': score,
        'word_count': word_count,
        'sentence_count': sentence_count,
        'flags': flags,
        'penalties': penalties,
        'expectation_results': expectation_results,
        'details': {
            'bullet_lines': bullets,
            'corporate_openers': corporate_openers,
            'corporate_closers': corporate_closers,
            'hedge_phrases': hedge_phrases,
            'assistant_patterns': assistant_patterns,
            'meta_commentary': meta_commentary,
            'life_dump_matches': life_dump_matches,
        },
    }


def _detect_bullets(lines: list) -> List[str]:
    """Detect bullet point and numbered list lines."""
    bullet_chars = ('-', '•', '*', '–', '—')
    found = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        # Bullet points
        if any(stripped.startswith(c + ' ') for c in bullet_chars):
            found.append(stripped[:60])
        # Numbered lists
        if len(stripped) > 2 and stripped[0].isdigit() and stripped[1] in '.):':
            found.append(stripped[:60])
    return found


def _find_matches(text_lower: str, phrases: list) -> List[str]:
    """Find which phrases appear in text."""
    return [p for p in phrases if p in text_lower]


def format_scorecard(result: Dict[str, Any], score_data: Dict[str, Any]) -> str:
    """Format a human-readable scorecard for a single run."""
    lines = []
    lines.append(f"Model: {result.get('model', '?')}")
    lines.append(f"Time: {result.get('elapsed_seconds', '?')}s | Words: {score_data['word_count']}")
    lines.append(f"Score: {score_data['score']}/100")

    if score_data['penalties']:
        lines.append("Penalties:")
        for p in score_data['penalties']:
            lines.append(f"  ❌ {p}")
    else:
        lines.append("  ✅ No penalties — clean response")

    flags = score_data['flags']
    flag_line = []
    flag_line.append(f"Bullets: {'📋' if flags['has_bullets'] else '—'}")
    flag_line.append(f"Corporate: {'❌' if flags['has_corporate_opener'] or flags['has_corporate_closer'] else '✅'}")
    flag_line.append(f"Hedging: {'❌' if flags['has_hedge_phrases'] else '✅'}")
    flag_line.append(f"LifeDump: {'❌' if flags['has_life_dump'] else '—'}")
    lines.append(" | ".join(flag_line))

    if score_data['expectation_results']:
        lines.append("Expectations:")
        for k, v in score_data['expectation_results'].items():
            lines.append(f"  {'✅' if v else '❌'} {k}")

    return "\n".join(lines)
