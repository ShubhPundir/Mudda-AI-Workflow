'use client';

import { WorkflowStep } from '@/lib/type';

interface WorkflowGraphProps {
  steps: WorkflowStep[];
}

export default function WorkflowGraph({ steps }: WorkflowGraphProps) {
  if (!steps || steps.length === 0) return null;

  // Create a map of step_id to step for quick lookup
  const stepMap = new Map(steps.map(step => [step.step_id, step]));
  
  // Calculate positions for nodes (horizontal layout - left to right)
  const nodePositions: Map<string, { x: number; y: number }> = new Map();
  const nodeWidth = 120;
  const nodeHeight = 70;
  const horizontalSpacing = 180; // Space between columns
  const verticalSpacing = 100; // Space between nodes in same column
  const padding = 40;
  const startX = padding;
  const startY = padding + 20;

  // Find root nodes (nodes that are not in any 'next' array)
  const allNextSteps = new Set<string>();
  steps.forEach(step => {
    step.next.forEach(nextId => allNextSteps.add(nextId));
  });
  
  const rootNodes = steps.filter(step => !allNextSteps.has(step.step_id));
  
  // BFS to assign levels (columns)
  const levelMap = new Map<string, number>();
  const queue: { stepId: string; level: number }[] = [];
  
  rootNodes.forEach(step => {
    queue.push({ stepId: step.step_id, level: 0 });
    levelMap.set(step.step_id, 0);
  });
  
  while (queue.length > 0) {
    const { stepId, level } = queue.shift()!;
    const step = stepMap.get(stepId);
    if (!step) continue;
    
    step.next.forEach(nextId => {
      if (!levelMap.has(nextId)) {
        levelMap.set(nextId, level + 1);
        queue.push({ stepId: nextId, level: level + 1 });
      }
    });
  }
  
  // Group by level (columns)
  const levelGroups = new Map<number, string[]>();
  steps.forEach(step => {
    const level = levelMap.get(step.step_id) ?? 0;
    if (!levelGroups.has(level)) {
      levelGroups.set(level, []);
    }
    levelGroups.get(level)!.push(step.step_id);
  });
  
  // Calculate positions (horizontal: levels are columns on x-axis)
  levelGroups.forEach((stepIds, level) => {
    const x = startX + level * horizontalSpacing;
    const totalHeight = stepIds.length * verticalSpacing;
    const startYForColumn = startY + (Math.max(...Array.from(levelGroups.values()).map(arr => arr.length)) * verticalSpacing - totalHeight) / 2;
    
    stepIds.forEach((stepId, index) => {
      const y = startYForColumn + index * verticalSpacing;
      nodePositions.set(stepId, { x, y });
    });
  });

  // Calculate SVG dimensions (allow full width for scrolling)
  const maxLevel = Math.max(...Array.from(levelGroups.keys()));
  const maxNodesInColumn = Math.max(...Array.from(levelGroups.values()).map(arr => arr.length));
  const svgWidth = Math.max(800, startX + (maxLevel + 1) * horizontalSpacing + padding);
  const svgHeight = Math.max(200, startY + maxNodesInColumn * verticalSpacing + padding);

  // Generate connections
  const connections: Array<{ from: { x: number; y: number }; to: { x: number; y: number }; stepId: string }> = [];
  steps.forEach(step => {
    const fromPos = nodePositions.get(step.step_id);
    if (!fromPos) return;
    
    step.next.forEach(nextId => {
      const toPos = nodePositions.get(nextId);
      if (toPos) {
        connections.push({
          from: fromPos,
          to: toPos,
          stepId: step.step_id,
        });
      }
    });
  });

  return (
    <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200/50">
      <h4 className="text-sm font-semibold text-gray-700 mb-4 flex items-center">
        <svg className="w-4 h-4 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 20l-5.447-2.724A1 1 0 013 16.382V5.618a1 1 0 011.447-.894L9 7m0 13l6-3m-6 3V7m6 10l4.553 2.276A1 1 0 0021 18.382V7.618a1 1 0 00-.553-.894L15 4m0 13V4m0 0L9 7" />
        </svg>
        Workflow Graph
      </h4>
      <div className="overflow-x-auto overflow-y-auto max-h-96 w-full border border-blue-200/30 rounded-md bg-white/50 p-2 scrollbar-thin scrollbar-thumb-blue-300 scrollbar-track-blue-100">
        <svg
          width={svgWidth}
          height={svgHeight}
          viewBox={`0 0 ${svgWidth} ${svgHeight}`}
          style={{ minWidth: `${svgWidth}px` }}
          preserveAspectRatio="xMinYMin meet"
        >
          {/* Draw connections */}
          {connections.map((conn, idx) => (
            <g key={`conn-${idx}`}>
              <line
                x1={conn.from.x + nodeWidth}
                y1={conn.from.y + nodeHeight / 2}
                x2={conn.to.x}
                y2={conn.to.y + nodeHeight / 2}
                stroke="#6366f1"
                strokeWidth="2"
                markerEnd="url(#arrowhead)"
                className="opacity-60"
              />
            </g>
          ))}
          
          {/* Arrow marker definition */}
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="10"
              refX="9"
              refY="3"
              orient="auto"
            >
              <polygon
                points="0 0, 10 3, 0 6"
                fill="#6366f1"
                className="opacity-60"
              />
            </marker>
          </defs>

          {/* Draw nodes */}
          {steps.map((step, idx) => {
            const pos = nodePositions.get(step.step_id);
            if (!pos) return null;
            
            return (
              <g key={step.step_id}>
                {/* Node background */}
                <rect
                  x={pos.x}
                  y={pos.y}
                  width={nodeWidth}
                  height={nodeHeight}
                  rx="8"
                  fill="white"
                  stroke={step.requires_approval ? "#f59e0b" : "#3b82f6"}
                  strokeWidth="2"
                  className="shadow-md hover:shadow-lg transition-shadow"
                />
                
                 {/* Step ID */}
                 <text
                   x={pos.x + nodeWidth / 2}
                   y={pos.y + 35}
                   textAnchor="middle"
                   className="text-xs font-bold fill-gray-900"
                   fontSize="10"
                 >
                   {step.step_id.length > 12 ? step.step_id.substring(0, 12) + '...' : step.step_id}
                 </text>
                 
                 {/* Approval badge */}
                {step.requires_approval && (
                  <circle
                    cx={pos.x + nodeWidth - 10}
                    cy={pos.y + 10}
                    r="5"
                    fill="#f59e0b"
                  />
                )}
                
                {/* Step number badge */}
                <circle
                  cx={pos.x + nodeWidth / 2}
                  cy={pos.y - 10}
                  r="10"
                  fill="#3b82f6"
                  className="shadow-sm"
                />
                <text
                  x={pos.x + nodeWidth / 2}
                  y={pos.y - 10 + 3}
                  textAnchor="middle"
                  className="text-xs font-bold fill-white"
                  fontSize="9"
                >
                  {idx + 1}
                </text>
              </g>
            );
          })}
        </svg>
      </div>
    </div>
  );
}

