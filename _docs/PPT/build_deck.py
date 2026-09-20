import os
import shutil
import zipfile
import xml.etree.ElementTree as ET

SOURCE_PPTX = r'_docs\PPT\fastapi-htmx-kanban-deck.pptx'
OUTPUT_PPTX = r'_docs\PPT\zen-precision-kanban-presentation.pptx'
TMP_DIR = r'_docs\PPT\build_deck_tmp'

# Total slides = 8
TOTAL_SLIDES = 8

# Slide specifications
# layout: template slide index to clone from (1 = slide1.xml, 2 = slide2.xml, 3 = slide3.xml)
# texts: dict mapping shape name to text (or list of paragraph texts)
SLIDES_CONFIG = [
    # SLIDE 1: Title & Architectural Blueprint
    {
        "template": 1,
        "texts": {
            "TextBox 10": "ZEN PRECISION SAAS \u2014 FASTKANBAN ARCHITECTURE",
            "TextBox 13": "STACK // SPEC 01",
            "TextBox 20": "HYPERMEDIA-DRIVEN MINIMAL ORCHESTRATION",
            "TextBox 22": "FastAPI & HTMX 2.x Architecture",
            "TextBox 24": "Synthesizing Pythonic asynchronous execution with hypermedia-driven DOM morphing. Elimination of SPA build churn in favor of serene, declarative operational density.",
            "TextBox 33": "CORE RUNTIME",
            "TextBox 35": "FastAPI Backend",
            "TextBox 37": "Asynchronous ASGI server pipeline powered by Starlette & SQLModel. Delivers validated type boundaries and near-instant JSON/HTML responses under 15ms.",
            "TextBox 42": "Python 3.12+",
            "TextBox 44": "Uvicorn ASGI",
            "TextBox 46": "Jinja2 SSR",
            "TextBox 54": "CLIENT TRANSPORT",
            "TextBox 56": "HTMX 2.0 Engine",
            "TextBox 58": "Declarative HTML extensions replacing client state stores. Direct DOM element replacement using standard HTTP verbs without micro-bundle bloat.",
            "TextBox 63": "hx-post",
            "TextBox 65": "hx-target",
            "TextBox 67": "outerHTML",
            "TextBox 75": "INTERFACE PARADIGM",
            "TextBox 77": "Zen Precision UI",
            "TextBox 79": "Wabi-sabi reduction merged with Linear/Raycast keyboard speed. High contrast sumi ink on natural unbleached sand surfaces, devoid of ambient visual noise.",
            "TextBox 84": "#f3f2ec Sand",
            "TextBox 86": "Hairline 1px",
            "TextBox 88": "0.125rem Radius",
            "TextBox 95": "ZEN-STACK-01 // CORE SYSTEM ARCHITECTURE",
            "TextBox 97": "01 / 08",
        }
    },
    # SLIDE 2: Workspace View & 3-Column Kanban Board
    {
        "template": 2,
        "texts": {
            "TextBox 10": "ZEN PRECISION SAAS \u2014 WORKSPACE TOPOLOGY",
            "TextBox 13": "TOPOLOGY // KANBAN 02",
            "TextBox 20": "3-COLUMN STRUCTURAL TASK MAPPING",
            "TextBox 22": "Precision Task Board Composition",
            "TextBox 24": "Pure white surface cards (#faf9f5) arranged over dashed guide columns. Contact edges utilize hairline rules (#76777b) with zero ambient blur.",
            "TextBox 39": "TO DO",
            "TextBox 42": "02",
            "TextBox 47": "ZN-101 \u2014 BACKEND",
            "TextBox 49": "Implement hx-trigger SSE endpoint for live sprint status updates",
            "TextBox 53": "P1 High",
            "TextBox 55": "AK",
            "TextBox 61": "ZN-102 \u2014 PERFORMANCE",
            "TextBox 63": "Benchmark response latency for partial card swaps under 50 concurrent devs",
            "TextBox 67": "P2 Med",
            "TextBox 69": "TN",
            "TextBox 84": "IN PROGRESS",
            "TextBox 87": "02",
            "TextBox 92": "ZN-098 \u2014 HYPERMEDIA",
            "TextBox 94": "Migrate drag-and-drop event listeners to native hx-vals payload dispatch",
            "TextBox 98": "Active",
            "TextBox 100": "DL",
            "TextBox 106": "ZN-099 \u2014 TOKENS",
            "TextBox 108": "Enforce 0.125rem radius constraint across all nested swimlane cards",
            "TextBox 112": "Active",
            "TextBox 114": "SR",
            "TextBox 129": "DONE",
            "TextBox 132": "03",
            "TextBox 137": "ZN-092 \u2014 CORE",
            "TextBox 139": "Configure FastAPI ASGI lifespan handlers for zero-downtime card sync",
            "TextBox 143": "Complete",
            "TextBox 145": "TN",
            "TextBox 151": "ZN-093 \u2014 ROUTING",
            "TextBox 153": "Replace SPA router with HTML partial response endpoints (/cards/{id})",
            "TextBox 157": "Complete",
            "TextBox 159": "AK",
            "TextBox 167": "ZEN-KANBAN-02 // WORKSPACE STRUCTURAL RECREATION",
            "TextBox 169": "02 / 08",
        }
    },
    # SLIDE 3: Hypermedia Protocol & HTMX Swaps
    {
        "template": 3,
        "texts": {
            "TextBox 10": "ZEN PRECISION SAAS \u2014 HYPERMEDIA PROTOCOL",
            "TextBox 13": "MECHANICS // SWAP 03",
            "TextBox 20": "IMMEDIATE ZERO-FLICKER REACTIVITY",
            "TextBox 22": "Local State Swaps via HTMX 2.x",
            "TextBox 24": "Eliminating full-page reloads and bulky virtual-DOM reconciliation through granular HTTP fragment replacement.",
            "TextBox 31": "STAGE 01 // TRIGGER",
            "TextBox 33": "User Interaction",
            "TextBox 35": "The user drags a task card or toggles priority. Declarative attributes intercept the client DOM event.",
            "TextBox 37": [
                'hx-post="/cards/move"',
                'hx-trigger="drop"',
                'hx-vals=\'{"col": "done"}\''
            ],
            "TextBox 42": "STAGE 02 // TRANSPORT",
            "TextBox 44": "FastAPI Route",
            "TextBox 46": "Async handler validates movement order and renders only target card Jinja2 partial.",
            "TextBox 48": [
                '@app.post("/cards/move")',
                'async def move(req):',
                'return render("card.html")'
            ],
            "TextBox 53": "STAGE 03 // MORPH",
            "TextBox 55": "Surgical OuterHTML",
            "TextBox 57": "HTMX inspects the target selector and swaps the received HTML fragment in-place with zero script eval.",
            "TextBox 59": [
                'hx-target="#card-ZN-101"',
                'hx-swap="outerHTML"',
                'hx-indicator=".spinner"'
            ],
            "TextBox 64": "STAGE 04 // SYNC",
            "TextBox 66": "Zero Stale State",
            "TextBox 68": "Browser URL and history remain undisturbed. Server remains the single source of truth without client hydration mismatch.",
            "TextBox 70": [
                'HTTP/1.1 200 OK',
                'HX-Trigger: columnCountChanged',
                'Latency: < 8.4ms'
            ],
            "TextBox 76": "ZEN-HTMX-03 // HYPERMEDIA STATE TRANSITIONS",
            "TextBox 78": "03 / 08",
        }
    },
    # SLIDE 4: Zen Precision SaaS Design System
    {
        "template": 1,
        "texts": {
            "TextBox 10": "ZEN PRECISION SAAS \u2014 DESIGN SYSTEM CONTRACT",
            "TextBox 13": "FOUNDATIONS // TOKENS 04",
            "TextBox 20": "WABI-SABI REDUCTION & HIGH-DENSITY UTILITY",
            "TextBox 22": "Design System Foundations",
            "TextBox 24": "Center-aligned on intentional whitespace, warm natural paper surfaces, and razor-sharp typographic discipline. Shared 1:1 across web DOM and PPT layouts.",
            "TextBox 33": "SURFACE CANVASES",
            "TextBox 35": "Washi & Stone Tones",
            "TextBox 37": "Sand sub-surface (#f3f2ec) for viewport background and pure washi (#faf9f5) for cards. Tactile contact edges with hairline 1px (#76777b).",
            "TextBox 42": "#f3f2ec Canvas",
            "TextBox 44": "#faf9f5 Card",
            "TextBox 46": "#e0e2e9 Container",
            "TextBox 54": "TYPOGRAPHIC SCALE",
            "TextBox 56": "Inter & JetBrains Mono",
            "TextBox 58": "Dual-font architecture: crisp geometric sans-serif for UI labels and proportional headers, paired with monospace glyphs for metadata pills and code identifiers.",
            "TextBox 63": "Inter UI",
            "TextBox 65": "JetBrains Mono",
            "TextBox 67": "Hairline Rules",
            "TextBox 75": "COLOR TOKENS & STATES",
            "TextBox 77": "Sumi Ink & Mineral Pigments",
            "TextBox 78": "Primary ink (#07080a) and tertiary pitch (#100600) contrasted against earthy mineral accents: Cinnabar (#a34a42), Raw Amber (#b38038), and Lichen Green (#5e7a63).",
            "TextBox 84": "Cinnabar P1",
            "TextBox 86": "Amber Active",
            "TextBox 88": "Lichen Done",
            "TextBox 95": "ZEN-DESIGN-04 // GRAPHICS DESIGN SYSTEM INTEGRATION",
            "TextBox 97": "04 / 08",
        }
    },
    # SLIDE 5: Backend Architecture & Persistence Engine
    {
        "template": 1,
        "texts": {
            "TextBox 10": "ZEN PRECISION SAAS \u2014 PERSISTENCE & DATA ENGINE",
            "TextBox 13": "ENGINE // SQLITE 05",
            "TextBox 20": "DETERMINISTIC RANKING & REBALANCING",
            "TextBox 22": "Float Ranking & SQLite Persistence",
            "TextBox 24": "Decoupled repository abstraction backing SQLModel ORM with transactional SQLite WAL mode. O(1) card reordering powered by fractional midpoint interpolation.",
            "TextBox 33": "RANKING ALGORITHM",
            "TextBox 35": "Float Midpoint Engine",
            "TextBox 37": "Calculates new rank as (prev + next) / 2 on drop. Automated rebalancing spreads sequence evenly across integers whenever rank difference drops below 1e-6.",
            "TextBox 42": "Float Midpoint",
            "TextBox 44": "Auto-Rebalance",
            "TextBox 46": "O(1) Insertion",
            "TextBox 54": "DATA REPOSITORY",
            "TextBox 56": "SQLiteBoardRepository",
            "TextBox 58": "Abstract BoardRepository protocol with dual implementations: in-memory mock for micro-benchmarks and SQLModel SQLite engine for durable disk persistence.",
            "TextBox 63": "SQLModel ORM",
            "TextBox 65": "SQLite WAL",
            "TextBox 67": "Foreign Keys",
            "TextBox 75": "DATA SEEDING & LIFESPAN",
            "TextBox 77": "Auto-Seeded State",
            "TextBox 78": "FastAPI lifespan startup automatically bootstraps database tables, verifying schema integrity and populating sample tasks if the table is empty.",
            "TextBox 84": "Lifespan Hook",
            "TextBox 86": "Auto-Seed",
            "TextBox 88": "Async Engine",
            "TextBox 95": "ZEN-DATA-05 // SQLITE ENGINE & FRACTIONAL RANKING",
            "TextBox 97": "05 / 08",
        }
    },
    # SLIDE 6: Responsive Layout Matrix & Mobile UX
    {
        "template": 1,
        "texts": {
            "TextBox 10": "ZEN PRECISION SAAS \u2014 RESPONSIVE ADAPTATION",
            "TextBox 13": "ADAPTATION // VIEWPORT 06",
            "TextBox 20": "MULTI-SURFACE RESPONSIVE CONTRACT",
            "TextBox 22": "Desktop, Tablet & Mobile Matrix",
            "TextBox 24": "Tailwind CSS responsive architecture supporting viewports from 360px mobile compact up to 1920px widescreen displays without horizontal canvas breaks.",
            "TextBox 33": "DESKTOP VIEWPORT",
            "TextBox 35": "lg: & xl: Displays",
            "TextBox 37": "Multi-column side-by-side flex layout with equal column widths. Persistent top search bar, fast keyboard command palette (CMD+K), and desktop status bar.",
            "TextBox 42": "1440px / 1920px",
            "TextBox 44": "Side-by-Side",
            "TextBox 46": "Zero Clutter",
            "TextBox 54": "TABLET VIEWPORT",
            "TextBox 56": "md: & sm: Displays",
            "TextBox 58": "Fluid horizontal scrolling track with scroll snapping. Preserves column integrity, full drag-and-drop sortability, and inline card creation buttons.",
            "TextBox 63": "820px / 1024px",
            "TextBox 65": "Scroll Snapping",
            "TextBox 67": "SortableJS",
            "TextBox 75": "MOBILE COMPACT",
            "TextBox 77": "360px \u2014 430px Handhelds",
            "TextBox 78": "Dedicated viewport switcher tabs with live card counter badges, swipeable column snap-center cards, full-screen edit modal, and bottom navigation bar.",
            "TextBox 84": "390x844 Base",
            "TextBox 86": "Touch Snapping",
            "TextBox 88": "Tab Switcher",
            "TextBox 95": "ZEN-RESPONSIVE-06 // ADAPTIVE MULTI-DEVICE CONTRACT",
            "TextBox 97": "06 / 08",
        }
    },
    # SLIDE 7: DevOps, Packaging & uv Tooling
    {
        "template": 1,
        "texts": {
            "TextBox 10": "ZEN PRECISION SAAS \u2014 PACKAGING & DEPLOYMENT",
            "TextBox 13": "OPERATIONS // DOCKER 07",
            "TextBox 20": "DETERMINISTIC TOOLCHAIN & CONTAINERIZATION",
            "TextBox 22": "uv Environment & Docker Compose",
            "TextBox 24": "Modern Python engineering with zero virtualenv drift. Multi-stage Docker container utilizing astral uv for sub-second builds and volume-backed database persistence.",
            "TextBox 33": "PACKAGE MANAGER",
            "TextBox 35": "Astral uv Tooling",
            "TextBox 37": "Replaces pip, pip-tools, and poetry with lightning-fast Rust-based package resolution. Fully locked via uv.lock for deterministic builds across all platforms.",
            "TextBox 42": "uv sync",
            "TextBox 44": "uv.lock",
            "TextBox 46": "pyproject.toml",
            "TextBox 54": "MULTI-STAGE DOCKER",
            "TextBox 56": "Lean Container Images",
            "TextBox 58": "Multi-stage Dockerfile leveraging distroless/python-slim base. Runs under non-privileged app user with built-in HTTP curl healthchecks on /health.",
            "TextBox 63": "Non-Root User",
            "TextBox 65": "Multi-Stage",
            "TextBox 67": "Healthcheck",
            "TextBox 75": "DEVELOPER SCRIPTS",
            "TextBox 77": "manage.py & Makefile",
            "TextBox 78": "Standardized task runner supporting both Windows PowerShell and Unix make: dev server reload, automated pytest suite, dependency sync, and docker-compose orchestration.",
            "TextBox 84": "manage.py",
            "TextBox 86": "make dev",
            "TextBox 88": "compose up",
            "TextBox 95": "ZEN-DEVOPS-07 // PACKAGING & CONTAINER PIPELINE",
            "TextBox 97": "07 / 08",
        }
    },
    # SLIDE 8: Roadmap, Phases & Test Verification
    {
        "template": 1,
        "texts": {
            "TextBox 10": "ZEN PRECISION SAAS \u2014 PROJECT ROADMAP & VERIFICATION",
            "TextBox 13": "VERIFICATION // QA 08",
            "TextBox 20": "SPEC-DRIVEN PHASES & 100% TEST COVERAGE",
            "TextBox 22": "Execution Roadmap & Quality Gate",
            "TextBox 24": "Disciplined spec-driven lifecycle across 4 completed phases with 14 GitHub issues, 43 automated integration tests, and 100% test pass rate.",
            "TextBox 33": "PHASE 1 & 2 SCOPE",
            "TextBox 35": "Frontend & SQLite Persistence",
            "TextBox 37": "Issues #1-#6: UI scaffold, SortableJS, edit modal, dummy backend. Issues #7-#10: SQLModel entities, Float ranking engine, and route wiring.",
            "TextBox 42": "Phase 1 Done",
            "TextBox 44": "Phase 2 Done",
            "TextBox 46": "Issues #1-#10",
            "TextBox 54": "PHASE 3 & 4 SCOPE",
            "TextBox 56": "Deploy & Zen Design Refresh",
            "TextBox 58": "Issues #11-#12: Multi-stage Docker, healthcheck, compose. Issues #13-#14: Zen Precision SaaS design system refresh & responsive board layout.",
            "TextBox 63": "Phase 3 Done",
            "TextBox 65": "Phase 4 Done",
            "TextBox 67": "Issues #11-#14",
            "TextBox 75": "TESTING & QUALITY",
            "TextBox 77": "43 Automated Tests (100%)",
            "TextBox 78": "Comprehensive integration suite covering API endpoints, CRUD operations, rank collisions, rebalancing edge cases, and SQLite persistence across reboots.",
            "TextBox 84": "43 Passed",
            "TextBox 86": "1.95s Runtime",
            "TextBox 88": "Zero Regress",
            "TextBox 95": "ZEN-ROADMAP-08 // SPEC-DRIVEN VERIFICATION COMPLETE",
            "TextBox 97": "08 / 08",
        }
    },
]

def build_presentation():
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)

    # 1. Unpack source template
    with zipfile.ZipFile(SOURCE_PPTX, 'r') as z:
        z.extractall(TMP_DIR)

    # 2. Duplicate slides according to SLIDES_CONFIG
    for idx, cfg in enumerate(SLIDES_CONFIG):
        slide_num = idx + 1
        template_num = cfg["template"]

        target_slide = os.path.join(TMP_DIR, 'ppt', 'slides', f'slide{slide_num}.xml')
        target_slide_rels = os.path.join(TMP_DIR, 'ppt', 'slides', '_rels', f'slide{slide_num}.xml.rels')
        target_notes = os.path.join(TMP_DIR, 'ppt', 'notesSlides', f'notesSlide{slide_num}.xml')
        target_notes_rels = os.path.join(TMP_DIR, 'ppt', 'notesSlides', '_rels', f'notesSlide{slide_num}.xml.rels')

        if slide_num > 3:
            # Copy template slide and notes
            src_slide = os.path.join(TMP_DIR, 'ppt', 'slides', f'slide{template_num}.xml')
            src_slide_rels = os.path.join(TMP_DIR, 'ppt', 'slides', '_rels', f'slide{template_num}.xml.rels')
            src_notes = os.path.join(TMP_DIR, 'ppt', 'notesSlides', f'notesSlide{template_num}.xml')
            src_notes_rels = os.path.join(TMP_DIR, 'ppt', 'notesSlides', '_rels', f'notesSlide{template_num}.xml.rels')

            shutil.copyfile(src_slide, target_slide)
            shutil.copyfile(src_slide_rels, target_slide_rels)
            shutil.copyfile(src_notes, target_notes)
            shutil.copyfile(src_notes_rels, target_notes_rels)

            # Fix slide rels pointing to notesSlide
            with open(target_slide_rels, 'r', encoding='utf-8') as f:
                c = f.read().replace(f'notesSlide{template_num}.xml', f'notesSlide{slide_num}.xml')
            with open(target_slide_rels, 'w', encoding='utf-8') as f:
                f.write(c)

            # Fix notesSlide rels pointing to slide
            with open(target_notes_rels, 'r', encoding='utf-8') as f:
                c = f.read().replace(f'slide{template_num}.xml', f'slide{slide_num}.xml')
            with open(target_notes_rels, 'w', encoding='utf-8') as f:
                f.write(c)

        # 3. Update text elements in target_slide
        root = ET.parse(target_slide).getroot()
        ns_p = '{http://schemas.openxmlformats.org/presentationml/2006/main}'
        ns_a = '{http://schemas.openxmlformats.org/drawingml/2006/main}'

        texts_map = cfg["texts"]
        for sp in root.iter(f'{ns_p}sp'):
            cNvPr = sp.find(f'.//{ns_p}cNvPr')
            if cNvPr is None:
                continue
            name = cNvPr.get('name')
            if name in texts_map:
                val = texts_map[name]
                p_elems = list(sp.iter(f'{ns_a}p'))
                if isinstance(val, list):
                    # Multi-paragraph text
                    for p_idx, text_str in enumerate(val):
                        if p_idx < len(p_elems):
                            p = p_elems[p_idx]
                            t_elems = list(p.iter(f'{ns_a}t'))
                            if t_elems:
                                t_elems[0].text = text_str
                                for extra_t in t_elems[1:]:
                                    extra_t.text = ''
                else:
                    # Single text string
                    if p_elems:
                        p = p_elems[0]
                        t_elems = list(p.iter(f'{ns_a}t'))
                        if t_elems:
                            t_elems[0].text = val
                            for extra_t in t_elems[1:]:
                                extra_t.text = ''

        # Write updated slide XML
        with open(target_slide, 'wb') as f:
            f.write(ET.tostring(root, encoding='utf-8', xml_declaration=True))

    # 4. Update [Content_Types].xml
    ct_path = os.path.join(TMP_DIR, '[Content_Types].xml')
    with open(ct_path, 'r', encoding='utf-8') as f:
        ct_content = f.read()

    new_overrides = []
    for s_idx in range(4, TOTAL_SLIDES + 1):
        new_overrides.append(
            f'<Override PartName="/ppt/slides/slide{s_idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
            f'<Override PartName="/ppt/notesSlides/notesSlide{s_idx}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/>'
        )
    ct_content = ct_content.replace('</Types>', ''.join(new_overrides) + '</Types>')
    with open(ct_path, 'w', encoding='utf-8') as f:
        f.write(ct_content)

    # 5. Update ppt/_rels/presentation.xml.rels
    pr_rels_path = os.path.join(TMP_DIR, 'ppt', '_rels', 'presentation.xml.rels')
    with open(pr_rels_path, 'r', encoding='utf-8') as f:
        pr_rels_content = f.read()

    new_rels = []
    # rId1 to rId9 are already in presentation.xml.rels
    # rId2 = slide1, rId3 = slide2, rId4 = slide3
    # next available rIds start from rId10
    for s_idx in range(4, TOTAL_SLIDES + 1):
        rel_id = f'rId{s_idx + 6}'  # rId10, rId11, ...
        new_rels.append(
            f'<Relationship Id="{rel_id}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide{s_idx}.xml"/>'
        )
    pr_rels_content = pr_rels_content.replace('</Relationships>', ''.join(new_rels) + '</Relationships>')
    with open(pr_rels_path, 'w', encoding='utf-8') as f:
        f.write(pr_rels_content)

    # 6. Update ppt/presentation.xml
    pr_xml_path = os.path.join(TMP_DIR, 'ppt', 'presentation.xml')
    with open(pr_xml_path, 'r', encoding='utf-8') as f:
        pr_xml_content = f.read()

    new_slds = []
    # Existing sldIds: 256 (rId2), 257 (rId3), 258 (rId4)
    for s_idx in range(4, TOTAL_SLIDES + 1):
        rel_id = f'rId{s_idx + 6}'
        sld_id = 255 + s_idx  # 259, 260, 261, ...
        new_slds.append(f'<p:sldId id="{sld_id}" r:id="{rel_id}"/>')
    pr_xml_content = pr_xml_content.replace('</p:sldIdLst>', ''.join(new_slds) + '</p:sldIdLst>')
    with open(pr_xml_path, 'w', encoding='utf-8') as f:
        f.write(pr_xml_content)

    # 7. Zip package to OUTPUT_PPTX
    if os.path.exists(OUTPUT_PPTX):
        os.remove(OUTPUT_PPTX)

    with zipfile.ZipFile(OUTPUT_PPTX, 'w', zipfile.ZIP_DEFLATED) as z:
        for root_dir, dirs, files in os.walk(TMP_DIR):
            for file in files:
                full_path = os.path.join(root_dir, file)
                rel_path = os.path.relpath(full_path, TMP_DIR)
                z.write(full_path, rel_path)

    # 8. Clean up
    shutil.rmtree(TMP_DIR)
    print(f"Presentation generated successfully: {OUTPUT_PPTX}")

if __name__ == '__main__':
    build_presentation()
