"use client";

import { useCallback, useRef } from "react";
import { ForceGraph2D } from "react-force-graph";

interface GraphNode {
  id: string;
  name: string;
  label: string;
  [key: string]: unknown;
}

interface GraphLink {
  source: string;
  target: string;
  type: string;
}

interface Props {
  nodes: GraphNode[];
  links: GraphLink[];
}

const NODE_COLORS: Record<string, string> = {
  Candidate: "#ef4444",
  CoreMember: "#3b82f6",
  Supporter: "#22c55e",
  Organization: "#f59e0b",
};

const LABEL_KO: Record<string, string> = {
  Candidate: "후보자",
  CoreMember: "핵심 당원",
  Supporter: "지지자",
  Organization: "조직",
};

export default function OrgTree({ nodes, links }: Props) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const fgRef = useRef<any>(null);

  const handleNodeClick = useCallback((node: GraphNode) => {
    fgRef.current?.centerAt(
      node.x as number,
      node.y as number,
      800
    );
    fgRef.current?.zoom(3, 800);
  }, []);

  return (
    <div className="w-full h-full bg-gray-950 rounded-lg overflow-hidden">
      <ForceGraph2D
        ref={fgRef}
        graphData={{ nodes, links }}
        nodeId="id"
        nodeLabel={(n) => `${(n as GraphNode).name} (${LABEL_KO[(n as GraphNode).label] ?? (n as GraphNode).label})`}
        nodeColor={(n) => NODE_COLORS[(n as GraphNode).label] ?? "#6b7280"}
        nodeRelSize={6}
        linkLabel={(l) => (l as GraphLink).type}
        linkColor={() => "#4b5563"}
        linkWidth={1.5}
        linkDirectionalArrowLength={4}
        linkDirectionalArrowRelPos={1}
        onNodeClick={handleNodeClick as (node: object) => void}
        backgroundColor="#030712"
        nodeCanvasObjectMode={() => "after"}
        nodeCanvasObject={(node, ctx, globalScale) => {
          const n = node as GraphNode & { x: number; y: number };
          const label = n.name;
          const fontSize = 12 / globalScale;
          ctx.font = `${fontSize}px Sans-Serif`;
          ctx.textAlign = "center";
          ctx.textBaseline = "middle";
          ctx.fillStyle = "#e5e7eb";
          ctx.fillText(label, n.x, n.y + 10 / globalScale);
        }}
      />
    </div>
  );
}
