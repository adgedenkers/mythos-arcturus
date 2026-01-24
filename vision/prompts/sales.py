"""
Prompts for sales item analysis
"""

ITEM_ANALYSIS = """You are analyzing photos of an item being listed for sale.
Examine all photos carefully to extract accurate information.

TASK: Extract item details and generate marketplace listing content.

RULES:
- Read text from labels/tags exactly as written
- If you cannot determine something with confidence, use null
- Be conservative with condition assessment
- Price should reflect fair resale value (not retail)
- For shoes, check for box/packaging in photos

OUTPUT FORMAT - Respond with ONLY this JSON, no other text:

{
  "item_type": "clothing|shoes|other",
  "brand": "string or null",
  "model": "string or null (style name if visible)",
  "category": "string (jeans, sneakers, boots, shirt, dress, jacket, etc.)",
  "gender_category": "mens|womens|unisex|kids",
  "size_label": "string (exactly as written on tag)",
  "size_numeric": number or null,
  "size_width": "narrow|medium|wide|null (shoes only)",
  "condition": "new_with_tags|new_without_tags|like_new|gently_used|used|well_worn",
  "colors": ["array", "of", "colors"],
  "materials": ["array", "of", "materials"] or null,
  "features": {
    "waterproof": boolean or null,
    "heel_height": "flat|low|mid|high|null",
    "closure_type": "lace|slip-on|zipper|button|velcro|null",
    "style": "string describing style (bootcut, skinny, athletic, etc.)",
    "other": "any other notable features"
  },
  "country_of_manufacture": "string or null",
  "care_instructions": "string or null (from care label)",
  "estimated_price": number (fair USD resale price),
  "confidence_score": 0.0-1.0 (your confidence in extraction accuracy),
  "inferred_fields": ["list", "of", "fields", "that", "were", "guessed"],
  "extraction_notes": "any notes about what you couldn't determine",
  "title": "Marketplace title, 60-80 chars, brand + item + size + condition",
  "description": "Compelling description 100-200 words. Include: brand, size, condition, materials, features. Professional but friendly tone."
}"""


ITEM_ANALYSIS_SIMPLE = """Analyze this item for sale. Extract:
- Type (clothing/shoes/other)
- Brand
- Size
- Condition
- Estimated price

Respond in JSON format."""


CONDITION_CHECK = """Examine this item's condition carefully.
Look for: wear, stains, damage, tags, original packaging.

Rate the condition as one of:
- new_with_tags: Never worn, original tags attached
- new_without_tags: Never worn, no tags
- like_new: Worn once or twice, no visible wear
- gently_used: Light wear, good condition
- used: Normal wear, still functional
- well_worn: Significant wear, still usable

Respond with just the condition rating and a brief explanation."""


BRAND_IDENTIFICATION = """Identify the brand of this item.
Look for logos, labels, tags, and distinctive design elements.

Respond with:
- Brand name
- Confidence (high/medium/low)
- How you identified it"""
