# Workflow Loader Frontend Update

## Overview
Updated the frontend workflow generation loader to support the new 4-agent AI planning workflow with policy retrieval.

## Changes Made

### 1. Updated Types (`frontend/components/workflow-loader/types.ts`)

#### New Types
- Added `Policy` interface for retrieved policy documents
- Added `agent3Status` and `agent4Status` to `LoaderState`
- Added `retrievedPolicies: Policy[]` to track retrieved policies
- Updated `LoaderStage` to include all 4 stages: `'policy_retrieval' | 'activity_selection' | 'workflow_generation' | 'plan_validation'`

#### Updated AGENTS Configuration
```typescript
AGENTS = [
  Agent 1: Policy Retrieval (📚, cyan)
  Agent 2: Activity Selector (🤖, blue)
  Agent 3: Plan Maker (🧠, purple)
  Agent 4: Plan Validator (✅, green)
]
```

### 2. Updated Main Component (`frontend/components/workflow-loader/Main.tsx`)

#### Changes
- Added `agent3Status` and `agent4Status` to initial state
- Added `retrievedPolicies: []` to initial state
- Updated initial stage to `'policy_retrieval'`
- Updated initial message to reflect policy retrieval
- Added 4th agent card to the grid
- Imported and added `PolicyGrid` component

### 3. Updated Progress Timeline (`frontend/components/workflow-loader/ProgressTimeline.tsx`)

#### New Timeline Structure
```
1. Policy Retrieval (cyan)
   ↓
2. Activity Selection (blue)
   ↓
3. Workflow Planning (purple)
   ↓
4. Plan Validation (green)
   ↓
✓ Complete (emerald)
```

#### Features
- Added horizontal scrolling for mobile responsiveness
- 5 steps total (4 agents + completion)
- Color-coded progress indicators
- Smooth transitions between stages

### 4. New PolicyGrid Component (`frontend/components/workflow-loader/PolicyGrid.tsx`)

#### Purpose
Displays retrieved policy documents with relevance scores

#### Features
- Shows policy heading and author
- Displays similarity score as percentage
- Animated fade-in effect
- Responsive grid layout (1-3 columns)
- Scrollable when many policies
- Cyan color theme to match Agent 1

#### Example Display
```
📚 Retrieved Policies (3)
┌─────────────────────────────┐
│ Water Supply Policy    95%  │
│ by Water Department         │
└─────────────────────────────┘
```

### 5. Updated Primitives (`frontend/components/workflow-loader/Primitives.tsx`)

#### LoadingDots Enhancement
Added support for all agent colors:
- cyan (Agent 1 - Policy Retrieval)
- blue (Agent 2 - Activity Selector)
- purple (Agent 3 - Plan Maker)
- green (Agent 4 - Plan Validator)

### 6. Updated GenerateWorkflowModal (`frontend/app/(main)/workflows/_components/GenerateWorkflowModal.tsx`)

#### New Event Handlers
Added handlers for all new streaming events:

1. **policy_retrieval_start**
   - Activates Agent 1
   - Sets stage to 'policy_retrieval'

2. **policy_retrieval_complete**
   - Completes Agent 1
   - Stores retrieved policies
   - Updates message

3. **activity_selection_start**
   - Activates Agent 2
   - Sets stage to 'activity_selection'

4. **activity_selection_complete**
   - Completes Agent 2
   - Stores selected activities
   - Updates message

5. **workflow_generation_start**
   - Activates Agent 3
   - Sets stage to 'workflow_generation'

6. **workflow_generation_complete**
   - Completes Agent 3
   - Updates message

7. **plan_validation_start**
   - Activates Agent 4
   - Sets stage to 'plan_validation'

8. **plan_validation_complete**
   - Completes Agent 4
   - Updates message

9. **workflow_saved**
   - Sets stage to 'complete'

10. **done**
    - Closes loader after 2 seconds
    - Refreshes workflow list

## Event Flow

```
User submits problem statement
         ↓
policy_retrieval_start
         ↓
policy_retrieval_complete (with policies data)
         ↓
activity_selection_start
         ↓
activity_selection_complete (with activities data)
         ↓
workflow_generation_start
         ↓
workflow_generation_complete
         ↓
plan_validation_start
         ↓
plan_validation_complete
         ↓
workflow_saved
         ↓
done (auto-close)
```

## Data Structures

### Policy Object
```typescript
{
  heading: string;
  author: string;
  similarity_score: number; // 0.0 to 1.0
}
```

### Component/Activity Object
```typescript
{
  id: string;
  name: string;
  description: string;
}
```

## Visual Design

### Color Scheme
- **Cyan** (#06b6d4): Policy Retrieval - Knowledge/Information
- **Blue** (#3b82f6): Activity Selection - Analysis/Logic
- **Purple** (#a855f7): Workflow Planning - Creativity/Strategy
- **Green** (#22c55e): Plan Validation - Success/Verification
- **Emerald** (#10b981): Completion - Final Success

### Layout
- 2x2 grid for agent cards on desktop
- Responsive stacking on mobile
- Horizontal scrolling timeline on small screens
- Separate sections for policies and activities

## Responsive Design

### Desktop (≥768px)
- 2x2 agent card grid
- Full timeline visible
- 3-column policy/activity grids

### Tablet (≥640px)
- 2x2 agent card grid
- Scrollable timeline
- 2-column policy/activity grids

### Mobile (<640px)
- Stacked agent cards
- Horizontal scroll timeline
- Single column policy/activity grids

## Testing Checklist

- [ ] All 4 agents display correctly
- [ ] Timeline shows all 5 steps
- [ ] Policy retrieval events update UI
- [ ] Activity selection events update UI
- [ ] Workflow generation events update UI
- [ ] Plan validation events update UI
- [ ] Policies display with correct formatting
- [ ] Activities display with correct formatting
- [ ] Colors match agent roles
- [ ] Animations work smoothly
- [ ] Responsive design works on all screen sizes
- [ ] Error handling displays correctly
- [ ] Auto-close works after completion

## Future Enhancements

1. **Policy Details Modal**: Click on policy to see full content
2. **Activity Dependencies**: Show relationships between activities
3. **Validation Results**: Display specific validation checks
4. **Progress Percentage**: Show overall completion percentage
5. **Time Estimates**: Display estimated time for each stage
6. **Retry Mechanism**: Allow retry on specific failed stages
7. **Export Results**: Download workflow plan as PDF/JSON
8. **Real-time Logs**: Show detailed logs in expandable section

## Troubleshooting

### Policies Not Displaying
- Check backend is sending `policies` array in `policy_retrieval_complete` event
- Verify policy objects have required fields: `heading`, `author`, `similarity_score`
- Check browser console for errors

### Agent Cards Not Updating
- Verify event names match exactly between backend and frontend
- Check `__updateLoaderState` is being called correctly
- Ensure state updates are not being batched incorrectly

### Timeline Not Progressing
- Verify `stage` is being updated in state
- Check agent status transitions (idle → active → complete)
- Ensure event handlers are firing in correct order

### Colors Not Showing
- Verify Tailwind CSS includes cyan, blue, purple, green, emerald colors
- Check dynamic class names are whitelisted in Tailwind config
- Ensure color map in LoadingDots includes all colors
