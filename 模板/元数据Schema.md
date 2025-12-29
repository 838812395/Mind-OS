---
date: '2025-12-28'
last_modified: 2025-12-28 21:58
tags: []
title: 元数据Schema
---

# Mind-OS Metadata Schema (Draft)

To ensure consistency across the system, all `.md` files in the following directories MUST contain a YAML frontmatter block.

## 1. 📂 知识画像 (Knowledge Profiles)
**Path**: `知识画像/*.md`
```yaml
---
type: knowledge
level: L1 | L2 | L3 | L4 | L5 | L6
confidence: 0.0 - 1.0
evidence_count: integer
last_updated: YYYY-MM-DD
tags: [list]
---
```

## 2. 🧠 心理画像 (Psychological Profiles)
**Path**: `心理画像/*.md`
```yaml
---
type: psychological
category: trait | driver | fear
intensity: 1 - 10
stability: 0.0 - 1.0 (how often this trait changes)
evidence_links: [list of conversation IDs or files]
---
```

## 3. 📊 量化数据 (Quantitative Data)
**Path**: `量化算法/*.md`
```yaml
---
type: metric
dimension: 认知力 | 执行力 | 情感力 | 社交力 | 创造力
current_score: 0 - 100
delta: float (change since last update)
last_vouched_by: behavior | self-report | external
---
```

## 4. 🧪 增量/觉察 (Increments & Awareness)
**Path**: `深度觉察/*.md`, `增量引擎/*.md`
```yaml
---
type: growth_log
mode: red_team | cbt | shadow_work
breakthrough_achieved: boolean
critical_bias_detected: [list]
---
```
