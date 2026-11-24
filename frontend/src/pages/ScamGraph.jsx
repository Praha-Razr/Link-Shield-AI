import React, { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  ReactFlow,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  MarkerType,
  ReactFlowProvider,
  useReactFlow,
  Handle,
  Position
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import {
  Network,
  Search,
  Filter,
  RefreshCw,
  ExternalLink,
  X,
  Phone,
  AtSign,
  Globe,
  Mail,
  CreditCard,
  Coins,
  ShieldAlert,
  Info,
  Calendar,
  Layers,
  ArrowRight,
  Maximize2,
  RotateCcw,
  Eye,
  CheckCircle,
  HelpCircle,
  FolderOpen,
  ChevronLeft,
  ChevronRight,
  Radio,
  Flame,
  Activity,
  Target,
  ZoomIn,
  ZoomOut,
  MapPin
} from 'lucide-react';
import { api } from '../services/api';
import RiskBadge from '../components/RiskBadge';
import DemoBadge from '../components/DemoBadge';
import EmptyState from '../components/EmptyState';
import LoadingSpinner from '../components/LoadingSpinner';
import ErrorBanner from '../components/ErrorBanner';

// Node Type Color Palette & Icons
const TYPE_CONFIG = {
  domain: { bg: '#0369A1', border: '#38BDF8', glow: 'rgba(56, 189, 248, 0.4)', icon: Globe, label: 'DOMAIN' },
  phone: { bg: '#065F46', border: '#34D399', glow: 'rgba(52, 211, 153, 0.4)', icon: Phone, label: 'PHONE' },
  upi: { bg: '#581C87', border: '#C084FC', glow: 'rgba(192, 132, 252, 0.4)', icon: AtSign, label: 'UPI' },
  email: { bg: '#854D0E', border: '#FBBF24', glow: 'rgba(251, 191, 36, 0.4)', icon: Mail, label: 'EMAIL' },
  url: { bg: '#0F766E', border: '#2DD4BF', glow: 'rgba(45, 212, 191, 0.4)', icon: Globe, label: 'URL' },
  bank_account: { bg: '#3730A3', border: '#818CF8', glow: 'rgba(129, 140, 248, 0.4)', icon: CreditCard, label: 'BANK ACC' },
  crypto_wallet: { bg: '#831843', border: '#F472B6', glow: 'rgba(244, 114, 182, 0.4)', icon: Coins, label: 'CRYPTO' }
};

// ---------------------------------------------------------------------
// CUSTOM NODE COMPONENTS (Sleek cyber capsules with multi-directional handles)
// ---------------------------------------------------------------------

// 1. Kingpin / Infrastructure Hub Node (Center of the Syndicate Radar)
function HubNode({ data, selected }) {
  const config = TYPE_CONFIG[data.raw?.type] || TYPE_CONFIG.domain;
  const HubIcon = config.icon || Globe;
  const isPrimary = data.isPrimary;
  const caseCount = data.raw?.case_count || data.raw?.connected_cases?.length || 1;

  return (
    <div
      className={`relative rounded-2xl select-none transition-all duration-300 ${
        selected
          ? 'ring-2 ring-cyan-400 ring-offset-2 ring-offset-slate-900 scale-105'
          : 'hover:scale-[1.02]'
      }`}
      style={{
        background: 'linear-gradient(145deg, #0B132B 0%, #1C2541 100%)',
        border: `2px solid ${isPrimary ? '#38BDF8' : config.border}`,
        boxShadow: selected
          ? `0 0 35px ${config.glow}, 0 8px 24px rgba(0,0,0,0.6)`
          : `0 0 20px ${config.glow}, 0 4px 16px rgba(0,0,0,0.5)`,
        width: isPrimary ? 240 : 210,
        padding: '12px 14px'
      }}
    >
      {/* Invisible Handles on all 4 quadrants for smooth ray connections */}
      <Handle type="target" position={Position.Top} id="t" className="opacity-0" />
      <Handle type="target" position={Position.Right} id="r" className="opacity-0" />
      <Handle type="target" position={Position.Bottom} id="b" className="opacity-0" />
      <Handle type="target" position={Position.Left} id="l" className="opacity-0" />
      <Handle type="source" position={Position.Top} id="st" className="opacity-0" />
      <Handle type="source" position={Position.Right} id="sr" className="opacity-0" />
      <Handle type="source" position={Position.Bottom} id="sb" className="opacity-0" />
      <Handle type="source" position={Position.Left} id="sl" className="opacity-0" />

      {/* Header Tag */}
      <div className="flex items-center justify-between gap-1 mb-1.5">
        <span
          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold tracking-wider"
          style={{ background: `${config.bg}99`, color: '#FFFFFF', border: `1px solid ${config.border}66` }}
        >
          <HubIcon className="w-3 h-3" />
          {config.label}
        </span>
        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-500/40 text-[10px] font-mono font-bold text-cyan-300">
          <Activity className="w-2.5 h-2.5 animate-pulse text-cyan-400" />
          {caseCount} {caseCount === 1 ? 'case' : 'cases'}
        </span>
      </div>

      {/* Main Identifier Value */}
      <div className="font-mono font-bold text-xs text-white truncate max-w-[210px] tracking-tight" title={data.raw?.value}>
        {data.raw?.value}
      </div>

      {/* Role / Subtitle */}
      <div className="mt-1 flex items-center justify-between text-[9px] text-slate-400 font-medium border-t border-slate-700/60 pt-1">
        <span className="text-cyan-400 font-semibold">
          {isPrimary ? 'Primary Anchor Hub' : 'Associated Asset'}
        </span>
        <span className="text-slate-500 hover:text-cyan-300 transition-colors">Click to inspect &rarr;</span>
      </div>
    </div>
  );
}

// 2. Case Node (Orbiting Satellite Capsule)
function CaseNode({ data, selected }) {
  const c = data.raw;
  const isHigh = c?.risk_level === 'HIGH';
  const isMed = c?.risk_level === 'MEDIUM';

  const riskColor = isHigh ? '#F43F5E' : isMed ? '#F59E0B' : '#10B981';
  const riskBorder = isHigh ? 'border-rose-500/70' : isMed ? 'border-amber-500/70' : 'border-emerald-500/70';
  const riskGlow = isHigh ? 'rgba(244, 63, 94, 0.35)' : isMed ? 'rgba(245, 158, 11, 0.35)' : 'rgba(16, 185, 129, 0.35)';

  const cleanSubject = c?.label?.replace(/\[.*?\]\s*/, '') || c?.subject || c?.id;
  const cleanId = (c?.id || '').replace('case-', '');

  return (
    <div
      className={`relative rounded-xl select-none transition-all duration-300 ${riskBorder} ${
        selected
          ? 'ring-2 ring-cyan-400 ring-offset-2 ring-offset-slate-900 scale-105'
          : 'hover:scale-[1.03]'
      }`}
      style={{
        background: '#090E1A',
        borderWidth: '1.5px',
        borderStyle: 'solid',
        boxShadow: selected
          ? `0 0 25px rgba(56, 189, 248, 0.8), 0 4px 12px rgba(0,0,0,0.5)`
          : `0 0 12px ${riskGlow}, 0 2px 8px rgba(0,0,0,0.4)`,
        width: 185,
        padding: '8px 10px'
      }}
    >
      {/* Invisible Handles */}
      <Handle type="target" position={Position.Top} id="t" className="opacity-0" />
      <Handle type="target" position={Position.Right} id="r" className="opacity-0" />
      <Handle type="target" position={Position.Bottom} id="b" className="opacity-0" />
      <Handle type="target" position={Position.Left} id="l" className="opacity-0" />
      <Handle type="source" position={Position.Top} id="st" className="opacity-0" />
      <Handle type="source" position={Position.Right} id="sr" className="opacity-0" />
      <Handle type="source" position={Position.Bottom} id="sb" className="opacity-0" />
      <Handle type="source" position={Position.Left} id="sl" className="opacity-0" />

      {/* Top Header: Case ID + Risk Pill */}
      <div className="flex items-center justify-between text-[10px] font-mono">
        <span className="font-bold text-white flex items-center gap-1">
          <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: riskColor }} />
          {cleanId}
        </span>
        <span
          className="px-1.5 py-0.2 rounded-full font-bold text-[9px] uppercase tracking-wider"
          style={{
            backgroundColor: `${riskColor}22`,
            color: riskColor,
            border: `1px solid ${riskColor}55`
          }}
        >
          {c?.risk_level || 'LOW'}
        </span>
      </div>

      {/* Subject Line */}
      <div
        className="text-[11px] font-medium text-slate-200 truncate mt-1 leading-tight"
        title={cleanSubject}
      >
        {cleanSubject}
      </div>

      {/* Category / Scam Type Pill */}
      <div className="flex items-center justify-between text-[9px] text-slate-400 mt-1.5 pt-1 border-t border-slate-800/80">
        <span className="capitalize text-slate-300 truncate max-w-[110px]">
          {(c?.category || 'scam').replace(/_/g, ' ')}
        </span>
        <span className="font-mono text-cyan-400 font-bold">
          {typeof c?.risk_score === 'number'
            ? `${c.risk_score}/100`
            : c?.risk_level === 'HIGH'
            ? '85/100'
            : c?.risk_level === 'MEDIUM'
            ? '55/100'
            : '20/100'}
        </span>
      </div>
    </div>
  );
}

const nodeTypes = {
  hubNode: HubNode,
  caseNode: CaseNode
};

// ---------------------------------------------------------------------
// CONNECTED SYNDICATE ALGORITHM
// ---------------------------------------------------------------------
function computeSyndicates(nodes, edges) {
  const adj = new Map();
  nodes.forEach((n) => adj.set(n.id, []));
  edges.forEach((e) => {
    if (adj.has(e.source) && adj.has(e.target)) {
      adj.get(e.source).push(e.target);
      adj.get(e.target).push(e.source);
    }
  });

  const visited = new Set();
  const components = [];

  nodes.forEach((n) => {
    if (!visited.has(n.id)) {
      const compIds = [];
      const queue = [n.id];
      visited.add(n.id);

      while (queue.length > 0) {
        const curr = queue.shift();
        compIds.push(curr);
        for (const neighbor of adj.get(curr) || []) {
          if (!visited.has(neighbor)) {
            visited.add(neighbor);
            queue.push(neighbor);
          }
        }
      }
      components.push(compIds);
    }
  });

  const nodeMap = new Map(nodes.map((n) => [n.id, n]));

  // Build Syndicate objects
  const syndicates = components
    .map((compIds, idx) => {
      const compNodes = compIds.map((id) => nodeMap.get(id)).filter(Boolean);
      const idents = compNodes.filter((n) => n.type !== 'case');
      const cases = compNodes.filter((n) => n.type === 'case');

      // Sort idents by case_count
      idents.sort((a, b) => (b.case_count || 0) - (a.case_count || 0));
      const primaryHub = idents[0] || null;

      let highestRisk = 'LOW';
      let maxScore = 0;
      cases.forEach((c) => {
        if (c.risk_level === 'HIGH') highestRisk = 'HIGH';
        else if (c.risk_level === 'MEDIUM' && highestRisk !== 'HIGH') highestRisk = 'MEDIUM';
        if (typeof c.risk_score === 'number' && c.risk_score > maxScore) {
          maxScore = c.risk_score;
        }
      });

      // Also check connected_cases metadata in identifiers if case nodes had unpopulated scores
      idents.forEach((ident) => {
        (ident.connected_cases || []).forEach((cc) => {
          if (typeof cc.risk_score === 'number' && cc.risk_score > maxScore) {
            maxScore = cc.risk_score;
          }
        });
      });

      // Ensure a valid peak threat score baseline derived from risk tier
      if (maxScore === 0) {
        maxScore = highestRisk === 'HIGH' ? 85 : highestRisk === 'MEDIUM' ? 55 : 20;
      }

      const title = primaryHub
        ? `${primaryHub.type.toUpperCase()}: ${primaryHub.value}`
        : cases.length > 0
        ? `Case Cluster (${cases[0].id.replace('case-', '')})`
        : `Syndicate #${idx + 1}`;

      return {
        id: `syndicate-${idx + 1}`,
        title,
        primaryHub,
        caseCount: cases.length,
        identCount: idents.length,
        highestRisk,
        maxScore,
        nodeIds: new Set(compIds),
        nodes: compNodes,
        cases,
        identifiers: idents
      };
    })
    // Only keep real clusters (at least 2 cases and 1 shared hub)
    .filter((s) => s.caseCount >= 2 && s.identCount >= 1);

  // Sort by case count descending so the largest syndicate is first
  syndicates.sort((a, b) => b.caseCount - a.caseCount);
  return syndicates;
}

// Helper: Determine facing handle quadrant based on radial angle
function getRadialHandles(angle) {
  let a = angle;
  while (a > Math.PI) a -= 2 * Math.PI;
  while (a < -Math.PI) a += 2 * Math.PI;

  if (a >= (-3 * Math.PI) / 4 && a < -Math.PI / 4) {
    return { sourceHandle: 'st', targetHandle: 'b' };
  } else if (a >= -Math.PI / 4 && a < Math.PI / 4) {
    return { sourceHandle: 'sr', targetHandle: 'l' };
  } else if (a >= Math.PI / 4 && a < (3 * Math.PI) / 4) {
    return { sourceHandle: 'sb', targetHandle: 't' };
  } else {
    return { sourceHandle: 'sl', targetHandle: 'r' };
  }
}

// ---------------------------------------------------------------------
// RADIAL SYNDICATE RADAR LAYOUT GENERATOR (With generous celestial spacing)
// ---------------------------------------------------------------------
function generateSyndicateRadarLayout({
  activeSyndicate,
  allSyndicates,
  isMacroView,
  selectedNodeId,
  searchTerm
}) {
  const layoutedNodes = [];
  const layoutedEdges = [];

  const syndicatesToRender = isMacroView
    ? allSyndicates
    : activeSyndicate
    ? [activeSyndicate]
    : allSyndicates.slice(0, 1);

  if (syndicatesToRender.length === 0) {
    return { nodes: [], edges: [] };
  }

  const cols = isMacroView ? Math.min(2, Math.max(1, syndicatesToRender.length)) : 1;
  const CELL_WIDTH = 1350;
  const CELL_HEIGHT = 1100;

  syndicatesToRender.forEach((syndicate, sIdx) => {
    const col = sIdx % cols;
    const row = Math.floor(sIdx / cols);
    const centerX = isMacroView ? col * CELL_WIDTH + 675 : 650;
    const centerY = isMacroView ? row * CELL_HEIGHT + 550 : 480;

    const hubs = syndicate.identifiers;
    const cases = syndicate.cases;
    const primaryHub = syndicate.primaryHub;

    // 1. PLACE HUBS IN INNER RADAR CORE
    if (hubs.length === 1 || !primaryHub) {
      const h = hubs[0] || primaryHub;
      if (h) {
        layoutedNodes.push({
          id: h.id,
          type: 'hubNode',
          position: { x: centerX - 120, y: centerY - 45 },
          data: {
            raw: h,
            isPrimary: true,
            syndicateId: syndicate.id
          }
        });
      }
    } else {
      // Primary in exact center
      layoutedNodes.push({
        id: primaryHub.id,
        type: 'hubNode',
        position: { x: centerX - 120, y: centerY - 45 },
        data: {
          raw: primaryHub,
          isPrimary: true,
          syndicateId: syndicate.id
        }
      });

      // Secondary hubs placed in a clean inner circle with radius 275px
      const secondaryHubs = hubs.filter((h) => h.id !== primaryHub.id);
      const numSec = Math.max(secondaryHubs.length, 1);
      const numCases = Math.max(cases.length, 1);

      secondaryHubs.forEach((sh, shIdx) => {
        // Offset secondary angle by half a case sector so they never share rays with cases
        const angle = (2 * Math.PI * shIdx) / numSec - Math.PI / 2 + (Math.PI / numCases);
        const hx = centerX + 275 * Math.cos(angle);
        const hy = centerY + 245 * Math.sin(angle);

        layoutedNodes.push({
          id: sh.id,
          type: 'hubNode',
          position: { x: hx - 105, y: hy - 40 },
          data: {
            raw: sh,
            isPrimary: false,
            syndicateId: syndicate.id
          }
        });

        // Conduit between primary hub and secondary hub
        const conduitHandles = getRadialHandles(angle);
        layoutedEdges.push({
          id: `conduit-${primaryHub.id}-${sh.id}`,
          source: primaryHub.id,
          target: sh.id,
          sourceHandle: conduitHandles.sourceHandle,
          targetHandle: conduitHandles.targetHandle,
          type: 'smoothstep',
          animated: true,
          style: {
            stroke: '#FBBF24',
            strokeWidth: 2,
            strokeDasharray: '4 4',
            opacity: 0.85
          }
        });
      });
    }

    // 2. PLACE CASES IN OUTER CELESTIAL ORBIT
    const numCases = Math.max(cases.length, 1);
    
    // Generous radial spacing:
    // If numCases <= 4 (e.g. Syndicate 2 with 4 cases): R = 300px
    // If numCases <= 8: R = 380px
    // If numCases > 8 (e.g. Syndicate 1 with 15 cases): staggered R = 520px / 590px
    const baseRadius = numCases <= 4 ? 300 : numCases <= 8 ? 380 : 520;

    cases.forEach((caseNode, cIdx) => {
      const angle = (2 * Math.PI * cIdx) / numCases - Math.PI / 2;
      const r = numCases > 8 ? (cIdx % 2 === 0 ? baseRadius : baseRadius + 70) : baseRadius;
      const cx = centerX + r * Math.cos(angle);
      const cy = centerY + r * 0.95 * Math.sin(angle);

      layoutedNodes.push({
        id: caseNode.id,
        type: 'caseNode',
        position: { x: cx - 92, y: cy - 32 },
        data: {
          raw: caseNode,
          syndicateId: syndicate.id
        }
      });

      // Edge from Hub to this Case
      const targetHubId = primaryHub ? primaryHub.id : hubs[0]?.id;
      if (targetHubId) {
        const isSelected = selectedNodeId === caseNode.id || selectedNodeId === targetHubId;
        const edgeColor = caseNode.risk_level === 'HIGH' ? '#F43F5E' : '#38BDF8';
        const caseHandles = getRadialHandles(angle);

        layoutedEdges.push({
          id: `edge-${targetHubId}-${caseNode.id}`,
          source: targetHubId,
          target: caseNode.id,
          sourceHandle: caseHandles.sourceHandle,
          targetHandle: caseHandles.targetHandle,
          type: 'bezier',
          animated: isSelected || !isMacroView,
          style: {
            stroke: isSelected ? '#38BDF8' : edgeColor,
            strokeWidth: isSelected ? 2.5 : 1.5,
            opacity: isSelected ? 1.0 : 0.55
          },
          markerEnd: {
            type: MarkerType.ArrowClosed,
            color: isSelected ? '#38BDF8' : edgeColor,
            width: 8,
            height: 8
          }
        });
      }
    });
  });

  return { nodes: layoutedNodes, edges: layoutedEdges };
}

// ---------------------------------------------------------------------
// INNER GRAPH CANVAS COMPONENT
// ---------------------------------------------------------------------
function ScamGraphInner() {
  const navigate = useNavigate();
  const reactFlow = useReactFlow();

  const [includeDemo, setIncludeDemo] = useState(true);
  const [isMacroView, setIsMacroView] = useState(false);
  const [typeFilter, setTypeFilter] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [showMiniMap, setShowMiniMap] = useState(false);

  const [rawGraph, setRawGraph] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Active Syndicate & Selected Node
  const [activeSyndicateId, setActiveSyndicateId] = useState(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [campaignSidebarOpen, setCampaignSidebarOpen] = useState(true);

  // React Flow state
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  // Fetch graph data from backend
  const fetchGraphData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await api.getGraph(includeDemo, 2);
      setRawGraph(data || { nodes: [], edges: [] });
    } catch (err) {
      setError(err.message || 'Failed to fetch graph data from intelligence engine.');
    } finally {
      setLoading(false);
    }
  }, [includeDemo]);

  useEffect(() => {
    fetchGraphData();
  }, [fetchGraphData]);

  // Compute Syndicates from raw graph
  const allSyndicates = useMemo(() => {
    if (!rawGraph.nodes || rawGraph.nodes.length === 0) return [];

    let idents = rawGraph.nodes.filter((n) => n.type !== 'case');
    const cases = rawGraph.nodes.filter((n) => n.type === 'case');

    if (typeFilter !== 'ALL') {
      idents = idents.filter((n) => n.type === typeFilter);
    }

    const activeIdentIds = new Set(idents.map((i) => i.id));
    const activeEdges = rawGraph.edges.filter(
      (e) => activeIdentIds.has(e.source) || activeIdentIds.has(e.target)
    );

    const activeNodes = [...idents, ...cases];
    return computeSyndicates(activeNodes, activeEdges);
  }, [rawGraph, typeFilter]);

  // Default to Syndicate #1 if none active
  useEffect(() => {
    if (allSyndicates.length > 0 && !activeSyndicateId) {
      setActiveSyndicateId(allSyndicates[0].id);
    }
  }, [allSyndicates, activeSyndicateId]);

  const activeSyndicate = useMemo(() => {
    return allSyndicates.find((s) => s.id === activeSyndicateId) || allSyndicates[0] || null;
  }, [allSyndicates, activeSyndicateId]);

  // Compute Layout whenever active syndicate, macro view, or search changes
  useEffect(() => {
    if (!activeSyndicate && allSyndicates.length === 0) {
      setNodes([]);
      setEdges([]);
      return;
    }

    const { nodes: newNodes, edges: newEdges } = generateSyndicateRadarLayout({
      activeSyndicate,
      allSyndicates,
      isMacroView,
      selectedNodeId: selectedNode?.id,
      searchTerm
    });

    setNodes(newNodes);
    setEdges(newEdges);
  }, [activeSyndicate, allSyndicates, isMacroView, selectedNode?.id, searchTerm]);

  // Auto-fit radar view when switching syndicate or when inspector drawer opens/closes
  useEffect(() => {
    if (nodes.length > 0) {
      const timer = setTimeout(() => {
        reactFlow.fitView({ padding: 0.25, duration: 450 });
      }, 100);
      return () => clearTimeout(timer);
    }
  }, [activeSyndicateId, isMacroView, selectedNode === null, reactFlow]);

  // Handler: Click a node
  const onNodeClick = (_, node) => {
    const raw = node.data.raw;
    setSelectedNode(raw);
  };

  // Handler: Click canvas background
  const onPaneClick = () => {
    setSelectedNode(null);
  };

  // Handler: Search submit
  const handleSearchSubmit = (e) => {
    e?.preventDefault();
    if (!searchTerm.trim()) return;

    const term = searchTerm.toLowerCase();
    for (const syn of allSyndicates) {
      const matchHub = syn.identifiers.find(
        (h) => h.value?.toLowerCase().includes(term) || h.id?.toLowerCase().includes(term)
      );
      const matchCase = syn.cases.find(
        (c) =>
          c.id?.toLowerCase().includes(term) ||
          c.label?.toLowerCase().includes(term) ||
          c.subject?.toLowerCase().includes(term)
      );

      if (matchHub) {
        setActiveSyndicateId(syn.id);
        setIsMacroView(false);
        setSelectedNode(matchHub);
        return;
      }
      if (matchCase) {
        setActiveSyndicateId(syn.id);
        setIsMacroView(false);
        setSelectedNode(matchCase);
        return;
      }
    }
  };

  // Handler: Reset view
  const handleResetView = () => {
    setSelectedNode(null);
    setSearchTerm('');
    if (allSyndicates.length > 0) {
      setActiveSyndicateId(allSyndicates[0].id);
      setIsMacroView(false);
    }
    reactFlow.fitView({ padding: 0.25, duration: 450 });
  };

  return (
    <div className="space-y-4">
      {/* 1. PAGE HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Radio className="w-6 h-6 text-primary-600 animate-pulse" />
            Scam Syndicate Intelligence &amp; Radar Graph
          </h1>
          <p className="text-slate-600 text-sm mt-1">
            Deep-space cybercrime infrastructure radar clustering connected criminal syndicates.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={fetchGraphData}
            disabled={loading}
            className="inline-flex items-center gap-1.5 px-3 py-2 rounded-lg bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 text-xs font-semibold shadow-xs transition-colors cursor-pointer"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh Intelligence</span>
          </button>
        </div>
      </div>

      {/* 2. SYNDICATE SPOTLIGHT SELECTOR BAR (Primary Navigation - Does NOT open drawer automatically) */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-md text-white">
        <div className="flex items-center justify-between gap-2 mb-2 pb-2 border-b border-slate-800/80">
          <div className="flex items-center gap-2">
            <Target className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-bold uppercase tracking-wider text-slate-300">
              Active Criminal Syndicates ({allSyndicates.length} Detected)
            </span>
          </div>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => {
                setIsMacroView(!isMacroView);
                setSelectedNode(null);
              }}
              className={`px-2.5 py-1 rounded-md text-xs font-semibold flex items-center gap-1.5 transition-all cursor-pointer ${
                isMacroView
                  ? 'bg-cyan-500 text-slate-950 shadow-sm font-bold'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              <Layers className="w-3.5 h-3.5" />
              <span>{isMacroView ? 'Exit Macro Grid' : 'Macro Grid View'}</span>
            </button>
          </div>
        </div>

        {/* Syndicate Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-thin">
          {allSyndicates.map((syn, idx) => {
            const isActive = !isMacroView && activeSyndicateId === syn.id;
            const isHigh = syn.highestRisk === 'HIGH';

            return (
              <button
                key={syn.id}
                type="button"
                onClick={() => {
                  setIsMacroView(false);
                  setActiveSyndicateId(syn.id);
                  setSelectedNode(null); // Keep drawer closed so user enjoys full space
                }}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium whitespace-nowrap transition-all flex items-center gap-2 cursor-pointer ${
                  isActive
                    ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-[0_0_15px_rgba(56,189,248,0.4)] font-bold ring-1 ring-cyan-400'
                    : 'bg-slate-800/90 text-slate-300 hover:bg-slate-750 hover:text-white border border-slate-700/60'
                }`}
              >
                <span className="flex items-center gap-1 font-mono">
                  {isHigh ? (
                    <Flame className="w-3.5 h-3.5 text-rose-400" />
                  ) : (
                    <ShieldAlert className="w-3.5 h-3.5 text-amber-400" />
                  )}
                  <span>Syndicate #{idx + 1}</span>
                </span>
                <span className="text-slate-300 text-[11px] font-sans truncate max-w-[150px]">
                  {syn.primaryHub?.value || syn.title}
                </span>
                <span
                  className={`px-1.5 py-0.2 rounded-full text-[10px] font-mono ${
                    isActive ? 'bg-white/20 text-white' : 'bg-slate-900 text-cyan-300'
                  }`}
                >
                  {syn.caseCount} cases
                </span>
              </button>
            );
          })}
        </div>

        {/* Active Syndicate Info Bar */}
        {activeSyndicate && !isMacroView && (
          <div className="mt-2 pt-2 border-t border-slate-800/60 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2">
            <div className="flex items-center gap-3">
              <span className="text-slate-300 font-semibold flex items-center gap-1">
                <Globe className="w-3.5 h-3.5 text-cyan-400" />
                Primary Anchor: <strong className="text-white font-mono">{activeSyndicate.primaryHub?.value}</strong>
              </span>
              <span>&bull;</span>
              <span>{activeSyndicate.caseCount} Victim Cases Linked</span>
              <span>&bull;</span>
              <span>{activeSyndicate.identCount} Technical Identifiers</span>
              <span>&bull;</span>
              <span className="flex items-center gap-1">
                Peak Threat:
                <strong
                  className={
                    activeSyndicate.highestRisk === 'HIGH' ? 'text-rose-400' : 'text-amber-400'
                  }
                >
                  {activeSyndicate.highestRisk} ({activeSyndicate.maxScore}/100)
                </strong>
              </span>
            </div>
            {activeSyndicate.primaryHub?.value && (
              <Link
                to={`/cases?q=${encodeURIComponent(activeSyndicate.primaryHub.value)}`}
                className="text-cyan-400 hover:text-cyan-300 flex items-center gap-1 text-[11px] font-semibold"
              >
                <span>Filter all {activeSyndicate.caseCount} cases in repository</span>
                <ExternalLink className="w-3 h-3" />
              </Link>
            )}
          </div>
        )}
      </div>

      {/* 3. TOOLBAR (Search, Filters, Demo Toggle, Controls) */}
      <div className="bg-white rounded-xl border border-slate-200 p-3 shadow-xs flex flex-wrap items-center justify-between gap-3 text-xs">
        {/* Search & Filter */}
        <div className="flex flex-wrap items-center gap-3 flex-1 min-w-[280px]">
          <form onSubmit={handleSearchSubmit} className="relative min-w-[220px] max-w-sm">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-slate-400">
              <Search className="w-4 h-4" />
            </div>
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search domain, phone, UPI, case ID..."
              className="w-full pl-9 pr-3 py-1.5 rounded-lg border border-slate-300 text-xs text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white"
            />
          </form>

          <div className="flex items-center gap-1.5">
            <Filter className="w-3.5 h-3.5 text-slate-400" />
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-2.5 py-1.5 rounded-lg border border-slate-300 text-xs bg-white text-slate-800 focus:ring-2 focus:ring-blue-500"
            >
              <option value="ALL">All Hub Types</option>
              <option value="domain">Domains</option>
              <option value="phone">Phones</option>
              <option value="upi">UPI Handles</option>
              <option value="email">Emails</option>
              <option value="bank_account">Bank Accounts</option>
              <option value="crypto_wallet">Crypto Wallets</option>
            </select>
          </div>
        </div>

        {/* Right Tools */}
        <div className="flex items-center gap-3">
          <label className="flex items-center gap-1.5 cursor-pointer font-medium text-slate-700 select-none text-xs">
            <input
              type="checkbox"
              checked={includeDemo}
              onChange={(e) => setIncludeDemo(e.target.checked)}
              className="rounded border-slate-300 text-primary-600 focus:ring-primary-500 h-3.5 w-3.5"
            />
            <span>Include Demo Data</span>
          </label>

          <div className="h-4 w-px bg-slate-200" />

          <button
            type="button"
            onClick={() => reactFlow.fitView({ padding: 0.25, duration: 450 })}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-medium cursor-pointer"
            title="Fit graph to viewport"
          >
            <Maximize2 className="w-3.5 h-3.5" />
            <span>Fit Radar</span>
          </button>

          <button
            type="button"
            onClick={handleResetView}
            className="inline-flex items-center gap-1 px-2.5 py-1.5 rounded-lg border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-medium cursor-pointer"
            title="Reset focus"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset</span>
          </button>
        </div>
      </div>

      {/* 4. MAIN CANVAS CONTAINER (Radar Canvas + Left Drawer + Non-overlapping Right Inspector) */}
      <div className="relative h-[720px] w-full rounded-2xl border border-slate-800 bg-[#060913] shadow-2xl overflow-hidden flex">
        {/* LEFT SYNDICATE DRAWER */}
        <div
          className={`h-full bg-slate-950/95 border-r border-slate-800 text-white z-20 flex flex-col shrink-0 transition-all duration-300 ${
            campaignSidebarOpen ? 'w-72 sm:w-80' : 'w-12'
          }`}
        >
          {/* Header */}
          <div className="p-3 border-b border-slate-800 flex items-center justify-between">
            {campaignSidebarOpen ? (
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-cyan-400" />
                <span className="font-bold text-xs uppercase tracking-wider text-slate-200">
                  Syndicates ({allSyndicates.length})
                </span>
              </div>
            ) : (
              <Target className="w-4 h-4 text-cyan-400 mx-auto" />
            )}
            <button
              type="button"
              onClick={() => setCampaignSidebarOpen(!campaignSidebarOpen)}
              className="p-1 rounded text-slate-400 hover:text-white hover:bg-slate-800 cursor-pointer"
              title={campaignSidebarOpen ? 'Collapse syndicate panel' : 'Expand syndicate panel'}
            >
              {campaignSidebarOpen ? (
                <ChevronLeft className="w-4 h-4" />
              ) : (
                <ChevronRight className="w-4 h-4" />
              )}
            </button>
          </div>

          {/* Syndicate List */}
          {campaignSidebarOpen && (
            <div className="flex-1 overflow-y-auto p-2 space-y-2">
              <div className="text-[11px] text-slate-400 px-1 pt-1 pb-1">
                Select a syndicate to focus radar:
              </div>

              {allSyndicates.length === 0 ? (
                <div className="p-4 text-center text-xs text-slate-500 italic">
                  No criminal syndicates found with current filters.
                </div>
              ) : (
                allSyndicates.map((syn, idx) => {
                  const isActive = !isMacroView && activeSyndicateId === syn.id;
                  const config = TYPE_CONFIG[syn.primaryHub?.type] || TYPE_CONFIG.domain;
                  const HubIcon = config.icon || Globe;

                  return (
                    <div
                      key={syn.id}
                      onClick={() => {
                        setIsMacroView(false);
                        setActiveSyndicateId(syn.id);
                        setSelectedNode(null); // Keep inspector closed so user enjoys spacious radar
                      }}
                      className={`p-3 rounded-xl border transition-all cursor-pointer ${
                        isActive
                          ? 'bg-blue-950/80 border-cyan-400 ring-1 ring-cyan-400/50 shadow-md'
                          : 'bg-slate-900/80 border-slate-800 hover:border-slate-700 hover:bg-slate-850'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1.5">
                        <span className="text-[10px] font-mono font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1">
                          <span className="text-cyan-400">#{idx + 1}</span>
                          <span>Syndicate</span>
                        </span>
                        <RiskBadge level={syn.highestRisk} showScore={false} size="xs" />
                      </div>

                      <div className="font-mono text-xs font-bold text-white truncate flex items-center gap-1.5 mb-2">
                        <HubIcon className="w-3.5 h-3.5 text-cyan-400 shrink-0" />
                        <span title={syn.primaryHub?.value || syn.title}>
                          {syn.primaryHub?.value || syn.title}
                        </span>
                      </div>

                      <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1.5 border-t border-slate-800/80">
                        <span className="font-semibold text-slate-300">
                          {syn.caseCount} linked cases
                        </span>
                        <span className="text-[10px] text-slate-400">
                          {syn.identCount} {syn.identCount === 1 ? 'asset' : 'assets'}
                        </span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          )}
        </div>

        {/* CENTER DEEP-SPACE RADAR CANVAS */}
        <div className="flex-1 h-full relative overflow-hidden">
          {loading ? (
            <div className="absolute inset-0 flex items-center justify-center bg-slate-900/80 z-30">
              <LoadingSpinner size="lg" message="Calibrating syndicate intelligence radar..." />
            </div>
          ) : error ? (
            <div className="p-6">
              <ErrorBanner message={error} />
            </div>
          ) : nodes.length === 0 ? (
            <div className="absolute inset-0 flex items-center justify-center p-8">
              <EmptyState
                icon={Network}
                title="No Syndicates Found"
                description="No shared criminal infrastructure found for the current filter settings. Try enabling Demo Data."
              />
            </div>
          ) : (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              nodeTypes={nodeTypes}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              onPaneClick={onPaneClick}
              panOnDrag={true}
              zoomOnScroll={true}
              zoomOnPinch={true}
              panOnScroll={false}
              zoomOnDoubleClick={true}
              minZoom={0.08}
              maxZoom={3.5}
              nodesDraggable={true}
              defaultEdgeOptions={{ animated: true }}
            >
              <Background color="#0284C7" gap={32} size={1.2} style={{ opacity: 0.08 }} />

              {/* TOP-RIGHT MINIMAP (Toggled via Controller, NEVER collides with Legend) */}
              {showMiniMap && (
                <MiniMap
                  position="top-right"
                  nodeColor={(n) => {
                    if (n.type === 'caseNode') {
                      return n.data?.raw?.risk_level === 'HIGH' ? '#F43F5E' : '#F59E0B';
                    }
                    return '#38BDF8';
                  }}
                  maskColor="rgba(6, 9, 19, 0.85)"
                  className="bg-slate-950 border border-slate-800 rounded-xl shadow-2xl m-4"
                  style={{ width: 150, height: 100 }}
                />
              )}
            </ReactFlow>
          )}

          {/* CUSTOM CYBER CONTROLS (BOTTOM LEFT) - ZERO UGLY WHITE BOX */}
          <div className="absolute bottom-4 left-4 z-10 flex flex-col gap-1.5 bg-slate-900/95 backdrop-blur-md border border-slate-700/80 p-1.5 rounded-xl shadow-2xl">
            <button
              type="button"
              onClick={() => reactFlow.zoomIn({ duration: 300 })}
              className="p-2 rounded-lg text-slate-300 hover:text-cyan-300 hover:bg-slate-800 transition-colors cursor-pointer flex items-center justify-center"
              title="Zoom In (+)"
            >
              <ZoomIn className="w-4 h-4 text-cyan-400" />
            </button>
            <button
              type="button"
              onClick={() => reactFlow.zoomOut({ duration: 300 })}
              className="p-2 rounded-lg text-slate-300 hover:text-cyan-300 hover:bg-slate-800 transition-colors cursor-pointer flex items-center justify-center"
              title="Zoom Out (-)"
            >
              <ZoomOut className="w-4 h-4 text-cyan-400" />
            </button>
            <div className="h-px bg-slate-700/60 my-0.5" />
            <button
              type="button"
              onClick={() => reactFlow.fitView({ padding: 0.25, duration: 400 })}
              className="p-2 rounded-lg text-slate-300 hover:text-cyan-300 hover:bg-slate-800 transition-colors cursor-pointer flex items-center justify-center"
              title="Fit Radar to Screen"
            >
              <Maximize2 className="w-4 h-4 text-slate-300" />
            </button>
            <button
              type="button"
              onClick={handleResetView}
              className="p-2 rounded-lg text-slate-300 hover:text-cyan-300 hover:bg-slate-800 transition-colors cursor-pointer flex items-center justify-center"
              title="Reset Radar View"
            >
              <RotateCcw className="w-4 h-4 text-slate-300" />
            </button>
            <button
              type="button"
              onClick={() => setShowMiniMap((prev) => !prev)}
              className={`p-2 rounded-lg transition-colors cursor-pointer flex items-center justify-center ${
                showMiniMap
                  ? 'bg-cyan-950 text-cyan-400 border border-cyan-500/50'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
              }`}
              title={showMiniMap ? 'Hide MiniMap' : 'Show MiniMap'}
            >
              <MapPin className="w-4 h-4" />
            </button>
          </div>

          {/* FLOATING RADAR HUD (BOTTOM RIGHT) - COMPLETELY SEPARATED FROM MINIMAP */}
          <div className="absolute bottom-4 right-4 z-10 bg-slate-950/90 backdrop-blur-md border border-slate-800 rounded-xl p-3 text-[11px] text-slate-300 shadow-xl hidden md:block">
            <div className="font-bold text-xs uppercase text-slate-400 mb-2 flex items-center gap-1.5">
              <HelpCircle className="w-3.5 h-3.5 text-cyan-400" />
              <span>Syndicate Radar Legend</span>
            </div>
            <div className="grid grid-cols-2 gap-x-4 gap-y-1.5">
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-cyan-400 shadow-[0_0_8px_#38BDF8]" />
                <span>Primary Hub</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-400" />
                <span>Associated Asset</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500 shadow-[0_0_8px_#F43F5E]" />
                <span>HIGH Risk Case</span>
              </div>
              <div className="flex items-center gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                <span>MEDIUM Risk Case</span>
              </div>
            </div>
          </div>
        </div>

        {/* RIGHT NODE INSPECTOR DRAWER - DEDICATED FLEX COLUMN (NEVER OVERLAYS OR CUTS OFF GRAPH) */}
        {selectedNode && (
          <div className="w-80 sm:w-96 h-full bg-white shadow-2xl border-l border-slate-200 flex flex-col shrink-0 z-30 transition-all duration-300">
            {/* Header */}
            <div className="p-4 bg-slate-900 text-white flex items-center justify-between border-b border-slate-800">
              <div className="flex items-center gap-2">
                <ShieldAlert className="w-5 h-5 text-cyan-400" />
                <div>
                  <div className="text-[10px] font-mono uppercase tracking-wider text-slate-400">
                    {selectedNode.type === 'case' ? 'Investigation Case' : 'Infrastructure Asset'}
                  </div>
                  <div className="font-mono text-sm font-bold text-white truncate max-w-[220px]">
                    {selectedNode.type === 'case'
                      ? (selectedNode.id || '').replace('case-', '')
                      : selectedNode.value}
                  </div>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setSelectedNode(null)}
                className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 cursor-pointer"
                title="Close Inspector"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Body */}
            <div className="flex-1 overflow-y-auto p-5 space-y-4 text-xs">
              {selectedNode.type === 'case' ? (
                <>
                  <div className="space-y-1">
                    <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">
                      Incident Subject
                    </span>
                    <h3 className="text-sm font-bold text-slate-900 leading-snug">
                      {selectedNode.label?.replace(/\[.*?\]\s*/, '') || selectedNode.subject}
                    </h3>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                      <span className="text-[10px] uppercase font-bold text-slate-500 block">
                        Assessed Risk
                      </span>
                      <div className="mt-1">
                        <RiskBadge
                          level={selectedNode.risk_level}
                          score={selectedNode.risk_score}
                          size="xs"
                        />
                      </div>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                      <span className="text-[10px] uppercase font-bold text-slate-500 block">
                        Category
                      </span>
                      <span className="font-semibold text-slate-800 capitalize mt-1 block">
                        {(selectedNode.category || 'scam').replace(/_/g, ' ')}
                      </span>
                    </div>
                  </div>

                  <div className="pt-2">
                    <button
                      type="button"
                      onClick={() =>
                        navigate(`/cases?open=${(selectedNode.id || '').replace('case-', '')}`)
                      }
                      className="w-full py-2.5 px-3 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-bold text-xs flex items-center justify-center gap-1.5 shadow-sm transition-colors cursor-pointer"
                    >
                      <FolderOpen className="w-4 h-4" />
                      <span>Open Case Dossier</span>
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <div className="p-3 rounded-lg bg-slate-50 border border-slate-200 space-y-1">
                    <div className="text-[10px] font-bold uppercase text-slate-500">
                      Identifier Value
                    </div>
                    <div className="font-mono text-xs font-bold text-slate-900 break-all">
                      {selectedNode.value}
                    </div>
                    <div className="text-[10px] text-slate-500 uppercase tracking-wider">
                      Type: <strong>{selectedNode.type}</strong>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                      <div className="text-[10px] font-bold uppercase text-slate-500">
                        Connected Cases
                      </div>
                      <div className="text-xl font-bold font-mono text-slate-900 mt-0.5">
                        {selectedNode.case_count || selectedNode.connected_cases?.length || 1}
                      </div>
                    </div>
                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-200">
                      <div className="text-[10px] font-bold uppercase text-slate-500">
                        First Seen
                      </div>
                      <div className="text-[11px] font-semibold text-slate-800 mt-1">
                        {selectedNode.first_seen
                          ? new Date(selectedNode.first_seen).toLocaleDateString()
                          : 'Recorded in DB'}
                      </div>
                    </div>
                  </div>

                  {/* Connected Cases in this Syndicate */}
                  <div>
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2">
                      Linked Cases ({selectedNode.connected_cases?.length || 0})
                    </h4>
                    <div className="space-y-2 max-h-56 overflow-y-auto">
                      {(selectedNode.connected_cases || []).map((c) => (
                        <div
                          key={c.id}
                          onClick={() => navigate(`/cases?open=${c.id}`)}
                          className="p-2.5 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50/50 transition-colors cursor-pointer flex items-center justify-between"
                        >
                          <div>
                            <span className="font-mono font-bold text-blue-700">{c.id}</span>
                            <div className="text-[11px] text-slate-600 truncate max-w-[190px]">
                              {c.subject}
                            </div>
                          </div>
                          <RiskBadge level={c.risk_level} showScore={false} size="xs" />
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="pt-2">
                    <Link
                      to={`/cases?q=${encodeURIComponent(selectedNode.value)}`}
                      className="w-full py-2 px-3 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold text-xs flex items-center justify-center gap-1.5 transition-colors"
                    >
                      <span>Filter in Case Management</span>
                      <ExternalLink className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ---------------------------------------------------------------------
// MAIN EXPORT WRAPPED WITH PROVIDER
// ---------------------------------------------------------------------
export default function ScamGraph() {
  return (
    <ReactFlowProvider>
      <ScamGraphInner />
    </ReactFlowProvider>
  );
}
