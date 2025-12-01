'use client';

import { useEffect, useRef, useState } from 'react';

interface IssueLocation {
  id: string;
  lat: number;
  lng: number;
  status: 'active' | 'resolved' | 'pending';
  title: string;
}

interface GeographicMapProps {
  issues: IssueLocation[];
  height?: string;
}

// India's approximate bounding box
const INDIA_BOUNDS = {
  minLat: 6.5,
  maxLat: 37.1,
  minLng: 68.1,
  maxLng: 97.4,
};

// Delhi NCR approximate bounds for zoom
const DELHI_NCR_BOUNDS = {
  minLat: 28.4,
  maxLat: 28.8,
  minLng: 76.8,
  maxLng: 77.4,
};

// Simplified India outline path (approximate)
const INDIA_OUTLINE = "M 150 50 L 180 60 L 220 70 L 250 85 L 280 100 L 300 120 L 320 140 L 340 160 L 360 180 L 380 200 L 400 220 L 420 240 L 440 260 L 460 280 L 480 300 L 500 320 L 520 340 L 540 360 L 560 380 L 580 400 L 600 420 L 620 440 L 640 450 L 660 455 L 680 450 L 700 440 L 720 420 L 740 400 L 750 380 L 760 360 L 770 340 L 775 320 L 780 300 L 785 280 L 790 260 L 795 240 L 800 220 L 800 200 L 795 180 L 790 160 L 785 140 L 780 120 L 775 100 L 770 80 L 760 70 L 750 65 L 740 60 L 720 55 L 700 50 L 680 48 L 660 46 L 640 45 L 620 44 L 600 43 L 580 42 L 560 41 L 540 40 L 520 39 L 500 38 L 480 37 L 460 36 L 440 35 L 420 34 L 400 33 L 380 32 L 360 31 L 340 30 L 320 28 L 300 26 L 280 24 L 250 22 L 220 20 L 180 18 L 150 16 L 120 14 L 100 12 L 80 10 L 60 8 L 40 6 L 20 4 L 0 2 L 0 50 Z";

export default function GeographicMap({ issues, height = '500px' }: GeographicMapProps) {
  const mapRef = useRef<HTMLDivElement>(null);
  const [zoomLevel, setZoomLevel] = useState(1); // 1 = India view, 2 = Delhi NCR zoom
  const [panX, setPanX] = useState(0);
  const [panY, setPanY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });

  // Convert lat/lng to SVG coordinates for India view
  const latLngToSVG = (lat: number, lng: number, zoom: number = 1) => {
    if (zoom === 1) {
      // India view
      const x = ((lng - INDIA_BOUNDS.minLng) / (INDIA_BOUNDS.maxLng - INDIA_BOUNDS.minLng)) * 800;
      const y = ((INDIA_BOUNDS.maxLat - lat) / (INDIA_BOUNDS.maxLat - INDIA_BOUNDS.minLat)) * 500;
      return { x, y };
    } else {
      // Delhi NCR zoom view
      const x = ((lng - DELHI_NCR_BOUNDS.minLng) / (DELHI_NCR_BOUNDS.maxLng - DELHI_NCR_BOUNDS.minLng)) * 800;
      const y = ((DELHI_NCR_BOUNDS.maxLat - lat) / (DELHI_NCR_BOUNDS.maxLat - DELHI_NCR_BOUNDS.minLat)) * 500;
      return { x, y };
    }
  };

  useEffect(() => {
    if (!mapRef.current) return;

    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('width', '100%');
    svg.setAttribute('height', height);
    svg.setAttribute('viewBox', `0 0 800 500`);
    svg.style.background = 'linear-gradient(to bottom, #e0f2fe 0%, #bae6fd 50%, #7dd3fc 100%)';
    svg.style.borderRadius = '12px';
    svg.style.border = '2px solid #e5e7eb';
    svg.style.cursor = zoomLevel > 1 ? 'move' : 'default';

    // Create defs for gradients and filters
    const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
    
    // Map gradient
    const gradient = document.createElementNS('http://www.w3.org/2000/svg', 'linearGradient');
    gradient.setAttribute('id', 'mapGradient');
    gradient.setAttribute('x1', '0%');
    gradient.setAttribute('y1', '0%');
    gradient.setAttribute('x2', '0%');
    gradient.setAttribute('y2', '100%');
    
    const stop1 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop1.setAttribute('offset', '0%');
    stop1.setAttribute('stop-color', '#e0f2fe');
    gradient.appendChild(stop1);
    
    const stop2 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop2.setAttribute('offset', '50%');
    stop2.setAttribute('stop-color', '#bae6fd');
    gradient.appendChild(stop2);
    
    const stop3 = document.createElementNS('http://www.w3.org/2000/svg', 'stop');
    stop3.setAttribute('offset', '100%');
    stop3.setAttribute('stop-color', '#7dd3fc');
    gradient.appendChild(stop3);
    
    defs.appendChild(gradient);
    svg.appendChild(defs);

    // Draw background
    const background = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
    background.setAttribute('width', '100%');
    background.setAttribute('height', '100%');
    background.setAttribute('fill', 'url(#mapGradient)');
    svg.appendChild(background);

    // Draw India outline (simplified)
    if (zoomLevel === 1) {
      const indiaPath = document.createElementNS('http://www.w3.org/2000/svg', 'path');
      indiaPath.setAttribute('d', INDIA_OUTLINE);
      indiaPath.setAttribute('fill', '#f0f9ff');
      indiaPath.setAttribute('stroke', '#0284c7');
      indiaPath.setAttribute('stroke-width', '2');
      indiaPath.setAttribute('opacity', '0.8');
      svg.appendChild(indiaPath);
    } else {
      // Draw Delhi NCR region outline
      const delhiRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      delhiRect.setAttribute('x', '200');
      delhiRect.setAttribute('y', '150');
      delhiRect.setAttribute('width', '400');
      delhiRect.setAttribute('height', '200');
      delhiRect.setAttribute('fill', '#f0f9ff');
      delhiRect.setAttribute('stroke', '#0284c7');
      delhiRect.setAttribute('stroke-width', '2');
      delhiRect.setAttribute('opacity', '0.8');
      delhiRect.setAttribute('rx', '10');
      svg.appendChild(delhiRect);
    }

    // Draw grid lines
    for (let i = 0; i < 10; i++) {
      const lineH = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      lineH.setAttribute('x1', '0');
      lineH.setAttribute('y1', `${(i + 1) * 50}`);
      lineH.setAttribute('x2', '800');
      lineH.setAttribute('y2', `${(i + 1) * 50}`);
      lineH.setAttribute('stroke', 'rgba(148, 163, 184, 0.2)');
      lineH.setAttribute('stroke-width', '1');
      svg.appendChild(lineH);

      const lineV = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      lineV.setAttribute('x1', `${(i + 1) * 80}`);
      lineV.setAttribute('y1', '0');
      lineV.setAttribute('x2', `${(i + 1) * 80}`);
      lineV.setAttribute('y2', '500');
      lineV.setAttribute('stroke', 'rgba(148, 163, 184, 0.2)');
      lineV.setAttribute('stroke-width', '1');
      svg.appendChild(lineV);
    }

    // Plot issues as scatter points
    issues.forEach((issue) => {
      const coords = latLngToSVG(issue.lat, issue.lng, zoomLevel);
      const x = coords.x + panX;
      const y = coords.y + panY;

      // Only show markers within viewport
      if (x < -50 || x > 850 || y < -50 || y > 550) return;

      const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
      g.setAttribute('transform', `translate(${x}, ${y})`);

      const colors = {
        active: '#ef4444',
        resolved: '#10b981',
        pending: '#f59e0b',
      };

      // Draw circle marker
      const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
      circle.setAttribute('r', zoomLevel > 1 ? '10' : '8');
      circle.setAttribute('fill', colors[issue.status]);
      circle.setAttribute('stroke', 'white');
      circle.setAttribute('stroke-width', '2');
      circle.setAttribute('opacity', '0.9');
      circle.style.cursor = 'pointer';
      g.appendChild(circle);

      // Add pulse animation for active issues
      if (issue.status === 'active') {
        const pulse = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        pulse.setAttribute('r', zoomLevel > 1 ? '10' : '8');
        pulse.setAttribute('fill', 'none');
        pulse.setAttribute('stroke', colors[issue.status]);
        pulse.setAttribute('stroke-width', '2');
        pulse.setAttribute('opacity', '0.6');
        pulse.style.animation = 'pulse 2s infinite';
        g.appendChild(pulse);
      }

      // Add label for zoomed view
      if (zoomLevel > 1) {
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', '15');
        text.setAttribute('y', '5');
        text.setAttribute('font-size', '10');
        text.setAttribute('fill', '#1f2937');
        text.setAttribute('font-weight', '500');
        text.textContent = issue.title.split(' - ')[0];
        g.appendChild(text);
      }

      // Add tooltip
      const title = document.createElementNS('http://www.w3.org/2000/svg', 'title');
      title.textContent = `${issue.title} (${issue.status})`;
      g.appendChild(title);

      svg.appendChild(g);
    });

    mapRef.current.innerHTML = '';
    mapRef.current.appendChild(svg);

    // Add CSS animation
    if (!document.getElementById('map-pulse-style')) {
      const style = document.createElement('style');
      style.id = 'map-pulse-style';
      style.textContent = `
        @keyframes pulse {
          0%, 100% {
            transform: scale(1);
            opacity: 0.6;
          }
          50% {
            transform: scale(2);
            opacity: 0;
          }
        }
      `;
      document.head.appendChild(style);
    }
  }, [issues, height, zoomLevel, panX, panY]);

  const handleZoomIn = () => {
    if (zoomLevel < 2) {
      setZoomLevel(2);
      setPanX(0);
      setPanY(0);
    }
  };

  const handleZoomOut = () => {
    if (zoomLevel > 1) {
      setZoomLevel(1);
      setPanX(0);
      setPanY(0);
    }
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (zoomLevel > 1) {
      setIsDragging(true);
      setDragStart({ x: e.clientX - panX, y: e.clientY - panY });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging && zoomLevel > 1) {
      setPanX(e.clientX - dragStart.x);
      setPanY(e.clientY - dragStart.y);
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  return (
    <div className="relative w-full rounded-xl overflow-hidden shadow-lg border border-blue-200/50">
      <div 
        ref={mapRef} 
        className="w-full select-none" 
        style={{ height }}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
      ></div>
      
      {/* Zoom Controls */}
      <div className="absolute top-4 right-4 flex flex-col space-y-2">
        <button
          onClick={handleZoomIn}
          disabled={zoomLevel >= 2}
          className="w-10 h-10 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg border border-blue-200/50 flex items-center justify-center hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          title="Zoom to Delhi NCR"
        >
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v6m3-3H7" />
          </svg>
        </button>
        <button
          onClick={handleZoomOut}
          disabled={zoomLevel <= 1}
          className="w-10 h-10 bg-white/90 backdrop-blur-sm rounded-lg shadow-lg border border-blue-200/50 flex items-center justify-center hover:bg-blue-50 disabled:opacity-50 disabled:cursor-not-allowed transition-all"
          title="Zoom to India"
        >
          <svg className="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7" />
          </svg>
        </button>
      </div>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg px-4 py-3 shadow-lg border border-blue-200/50">
        <h4 className="text-xs font-semibold text-blue-700 mb-2">Issue Status</h4>
        <div className="flex flex-col space-y-1.5">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-rose-500 shadow-sm"></div>
            <span className="text-xs text-blue-600/80 font-medium">Active</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-emerald-500 shadow-sm"></div>
            <span className="text-xs text-blue-600/80 font-medium">Resolved</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-amber-500 shadow-sm"></div>
            <span className="text-xs text-blue-600/80 font-medium">Pending</span>
          </div>
        </div>
      </div>

      {/* Zoom Indicator */}
      <div className="absolute top-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow-lg border border-blue-200/50">
        <span className="text-xs font-semibold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
          {zoomLevel === 1 ? 'India View' : 'Delhi NCR'}
        </span>
      </div>
    </div>
  );
}

