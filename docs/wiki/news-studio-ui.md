# News Studio UI

The **News Studio UI** is a dedicated internal web interface designed for the marketing team to manage the lifecycle of news content. It provides a visual layer over the news ingestion and adaptation pipeline, allowing users to filter news by relevance, edit AI-generated Instagram drafts, and oversee the transition from raw RSS data to approved social media posts.

### UI Architecture Overview

The interface is built using **FastAPI**'s `Jinja2Templates` engine [app/routers/ui.py:8-27](). It serves server-side rendered (SSR) HTML pages that interact with the backend via standard HTTP GET requests for navigation and asynchronous `fetch` calls (POST/PATCH) for data operations like saving drafts or triggering ingestion [app/templates/portal.html:122-128]().

The UI is divided into four primary views:
1.  **Brand Selector**: Entry point to choose between Althara (Real Estate) and Oxono (Tech).
2.  **Portal (Inbox/Drafts/Approved)**: A multi-tab dashboard for news management.
3.  **News Detail**: A deep-dive view of a single news item and its associated drafts.
4.  **IG Draft Editor**: A specialized tool for fine-tuning Instagram carousels and captions.

### System Mapping: UI to Code Entities

The following diagram maps the visual components of the News Studio to their corresponding backend routes and database models.

**UI Component to Code Mapping**
```mermaid
graph TD
    subgraph "Browser (Natural Language Space)"
        "Brand Selector" --> "Portal Dashboard"
        "Portal Dashboard" --> "News Detail View"
        "News Detail View" --> "Instagram Editor"
    end

    subgraph "Backend (Code Entity Space)"
        "Brand Selector" --- UI_SELECTOR["ui_selector() route<br/>app/routers/ui.py"]
        "Portal Dashboard" --- UI_PORTAL["ui_portal() route<br/>app/routers/ui.py"]
        "News Detail View" --- UI_NEWS_DETAIL["ui_news_detail() route<br/>app/routers/ui.py"]
        "Instagram Editor" --- UI_DRAFT_EDITOR["ui_draft_editor() route<br/>app/routers/ui.py"]
        
        UI_PORTAL --> NEWS_MODEL["News Model<br/>app/models/news.py"]
        UI_DRAFT_EDITOR --> DRAFT_MODEL["IGDraft Model<br/>app/models/ig_draft.py"]
    end

    UI_SELECTOR -.-> SELECTOR_HTML["selector.html"]
    UI_PORTAL -.-> PORTAL_HTML["portal.html"]
    UI_DRAFT_EDITOR -.-> EDITOR_HTML["draft_editor.html"]
```
Sources: [app/routers/ui.py:35-181](), [app/templates/selector.html:1-14](), [app/templates/portal.html:1-99](), [app/templates/draft_editor.html:1-138]()

---

### Core Navigation and Branding

The UI supports a multi-brand architecture defined in `app/brands.py`. Upon entering the `/ui` route, users are presented with brand cards [app/templates/selector.html:7-13](). Selecting a brand sets the context for all subsequent views, including the visual theme (CSS variables) and the data domain (e.g., `real_estate` for Althara or `tech` for Oxono) [app/routers/ui.py:59-66]().

*   **Brand Switcher**: A global dropdown in the header allows switching brands while maintaining the current view [app/templates/portal.html:9-15]().
*   **Domain Filtering**: The UI automatically filters the `News` table based on the `domain` associated with the active brand [app/routers/ui.py:66-67]().

For details on how routes handle brand-specific logic, see [UI Routing and Authentication](#6.1).

---

### Portal and News Management

The **Portal** (`/ui/{brand}`) is the central hub for the marketing team. It organizes news into three logical tabs based on their status and the existence of Instagram drafts [app/routers/ui.py:61-66]():

| Tab | Logic | Use Case |
| :--- | :--- | :--- |
| **Inbox** | All news for the domain. | General browsing and initial discovery. |
| **Drafts** | News with `IGDraft` in `DRAFT` status. | Active editing and refinement. |
| **Approved** | News with `IGDraft` in `APPROVED` or `PUBLISHED` status. | History and finalized content. |

The portal includes advanced filtering by category, search queries, and sorting by `relevance_score` or `published_at` [app/templates/portal.html:25-54](). It also features a "Generate more news" button that triggers the full ingestion and adaptation pipeline [app/templates/portal.html:55]().

Sources: [app/routers/ui.py:44-118](), [app/templates/portal.html:59-64]()

---

### Instagram Draft Editor

The **Draft Editor** (`/ui/{brand}/draft/{draft_id}`) is a specialized environment for content creators. It provides a split-pane layout:
1.  **Editor Pane**: Form fields for editing the Hook, Carousel Slides (Title/Body), Caption, Hashtags, and CTA [app/templates/draft_editor.html:30-85]().
2.  **Preview Pane**: A real-time "Instagram-style" phone mock-up that updates as the user types, allowing them to visualize how the carousel and caption will appear on a mobile device [app/templates/draft_editor.html:104-134]().

**Editor Workflow**
```mermaid
graph LR
    "User Input" --> "JS State Management"
    "JS State Management" --> "Live Preview"
    "JS State Management" --> SAVE["saveDraft() PATCH call"]
    SAVE --> DB[("IGDraft Table")]
```

For details on the JavaScript logic, hashtag chips, and the real-time preview engine, see [Templates and Frontend Logic](#6.2).

---

### Sub-Pages

- **[UI Routing and Authentication](#6.1)**: Details on the `ui.py` router, URL parameters for filtering, and BasicAuth security.
- **[Templates and Frontend Logic](#6.2)**: Technical breakdown of the Jinja2 templates, CSS themes, and the JavaScript-driven editor features.

Sources: [app/routers/ui.py:1-182](), [app/templates/draft_editor.html:1-160]()

---
