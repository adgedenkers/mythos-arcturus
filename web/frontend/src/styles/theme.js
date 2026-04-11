export const T = {
  bg: "#0a0e17",
  bgCard: "#111827",
  bgHover: "#1a2332",
  border: "#1e293b",
  borderLight: "#293548",
  text: "#e2e8f0",
  textDim: "#64748b",
  textMuted: "#475569",
  green: "#22c55e",
  greenBg: "rgba(34,197,94,0.08)",
  red: "#ef4444",
  redBg: "rgba(239,68,68,0.08)",
  amber: "#f59e0b",
  amberBg: "rgba(245,158,11,0.08)",
  blue: "#3b82f6",
  blueBg: "rgba(59,130,246,0.08)",
  cyan: "#06b6d4",
  cyanBg: "rgba(6,182,212,0.08)",
  purple: "#a855f7",
  purpleBg: "rgba(168,85,247,0.08)",
  gold: "#d4a574",
};

export const mono = { fontFamily: "'JetBrains Mono', monospace" };
export const serif = { fontFamily: "'Cinzel', serif" };

export const fmt = (n) => {
  if (n == null) return "\u2014";
  const abs = Math.abs(n);
  return `${n < 0 ? "-" : ""}$${abs.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
};

export const fmtShort = (n) => {
  if (n == null) return "\u2014";
  const abs = Math.abs(n);
  if (abs >= 1000) return `${n < 0 ? "-" : ""}$${(abs / 1000).toFixed(1)}k`;
  return `${n < 0 ? "-" : ""}$${abs.toFixed(0)}`;
};
