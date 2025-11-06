# Gmail Sidebar UI/UX Design
## TASK-022: Design Documentation

### Design Principles

**1. Non-Intrusive Integration**
- Sidebar appears on the right side of Gmail
- Does not interfere with Gmail's native functionality
- Can be collapsed to minimize space

**2. Gmail-Like Styling**
- Matches Gmail's visual design language
- Uses Gmail's color scheme (#1a73e8 for primary actions)
- Consistent typography (Google Sans, Roboto)

**3. Responsive Layout**
- Default width: 320px
- Collapsible to 48px (icon only)
- Responsive on smaller screens (280px)

**4. Dark Mode Support**
- Automatically detects system preference
- Seamless theme switching
- Maintains readability in both modes

### Layout Structure

```
┌─────────────────────────────────────┐
│  Header                             │
│  [Projects] [Refresh] [Collapse]    │
├─────────────────────────────────────┤
│  Search Bar                         │
│  [🔍 Search projects...]            │
├─────────────────────────────────────┤
│  Projects List                      │
│  ┌─────────────────────────────┐   │
│  │ 📁 Project Name              │   │
│  │    📍 Address                │   │
│  │    👤 Client Name            │   │
│  │    5 emails • 2 hours ago    │   │
│  └─────────────────────────────┘   │
│  ...                                │
├─────────────────────────────────────┤
│  Footer                             │
│  12 projects                        │
└─────────────────────────────────────┘
```

### Component Hierarchy

1. **Sidebar Container** (Drawer)
   - Persistent right-side drawer
   - Fixed positioning
   - Z-index: 1300

2. **Header**
   - Title: "Projects"
   - Actions: Refresh, Collapse

3. **Search Bar**
   - Full-width text field
   - Search icon
   - Real-time filtering

4. **Projects List**
   - Scrollable list
   - Project items with details
   - Selection highlighting

5. **Project Item**
   - Project name (primary)
   - Address (if available)
   - Client name (if available)
   - Email count and last email time
   - Status badge
   - Warning icon (if needs review)

6. **Footer**
   - Project count
   - Status summary

### Visual Design

**Colors:**
- Primary: #1a73e8 (Gmail blue)
- Background: #ffffff (light) / #202124 (dark)
- Text: #202124 (light) / #e8eaed (dark)
- Border: #dadce0 (light) / #5f6368 (dark)

**Typography:**
- Font Family: "Google Sans", Roboto, Arial
- Headings: 600 weight
- Body: 400 weight
- Captions: 0.75rem

**Spacing:**
- Padding: 16px (standard), 12px (compact)
- Border radius: 8px (items), 4px (badges)
- Gaps: 8px (small), 16px (medium)

### Interactions

**Hover States:**
- Project items: Light background highlight
- Buttons: Slight opacity change

**Selection:**
- Selected project: Primary color background
- Visual feedback on click

**Loading States:**
- Circular progress indicator
- Skeleton loading (future enhancement)

**Empty States:**
- "No projects yet" message
- Helpful placeholder text

### Accessibility

- ARIA labels for screen readers
- Keyboard navigation support
- Focus indicators
- Color contrast compliance (WCAG AA)

### Wireframes

**Desktop View:**
- Sidebar width: 320px
- Full project details visible
- Search and filter controls

**Tablet View:**
- Sidebar width: 280px
- Slightly compacted layout
- Maintains all functionality

**Mobile View (Future):**
- Bottom sheet overlay
- Collapsible to icon
- Touch-optimized controls

### Dark Mode

**Design Considerations:**
- Automatic theme detection
- Consistent color palette
- Maintains contrast ratios
- Smooth theme transitions

**Color Mapping:**
- Light background → Dark background
- Dark text → Light text
- Subtle borders and shadows

---

**Status:** Design Complete ✅
**Next:** Implementation (TASK-023, TASK-024, TASK-025)

