#!/bin/bash
# Quick doc creator for Mythos
# Usage: ./new_doc.sh <category> <name> "Title"
# Example: ./new_doc.sh tools my_tool "My New Tool"

CATEGORY=$1
NAME=$2
TITLE=$3

if [ -z "$CATEGORY" ] || [ -z "$NAME" ]; then
    echo "Usage: $0 <category> <name> [title]"
    echo "Categories: tools, patches, architecture, api"
    echo "Example: $0 tools my_tool \"My New Tool\""
    exit 1
fi

TITLE=${TITLE:-$NAME}
FILE="/opt/mythos/docs/${CATEGORY}/${NAME}.md"

mkdir -p "/opt/mythos/docs/${CATEGORY}"

cat > "$FILE" << TEMPLATE
# ${TITLE}

**Location:** \`/opt/mythos/...\`  
**Created:** $(date +%Y-%m-%d)  
**Patch:** 

## Overview

[Description]

## Quick Start

\`\`\`bash
[Commands]
\`\`\`

## Usage

[Details]

## Configuration

[Config details]

## Related

- [Related doc](link.md)

---
*Last updated: $(date +%Y-%m-%d)*
TEMPLATE

echo "Created: $FILE"
