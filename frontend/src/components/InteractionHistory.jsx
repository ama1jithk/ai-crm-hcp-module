import { useSelector } from "react-redux";

const SENTIMENT_DOT = {
  positive: "bg-emerald-500",
  neutral: "bg-slate-400",
  negative: "bg-rose-500",
};

export default function InteractionHistory() {
  const { selectedHcpId, historyByHcp } = useSelector((s) => s.hcps);
  const history = historyByHcp[selectedHcpId] || [];

  return (
    <div className="bg-white rounded-xl shadow-card border border-slate-100 p-4 h-full flex flex-col">
      <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-3">
        Interaction History
      </h3>
      <div className="space-y-3 overflow-y-auto pr-1">
        {history.length === 0 && (
          <p className="text-sm text-slate-400">No interactions logged yet.</p>
        )}
        {history.map((i) => (
          <div key={i.id} className="border border-slate-100 rounded-lg p-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-slate-500">
                {new Date(i.interaction_date).toLocaleDateString()} · {i.interaction_type}
              </span>
              <span
                className={`w-2 h-2 rounded-full ${SENTIMENT_DOT[i.sentiment] || "bg-slate-300"}`}
                title={i.sentiment}
              />
            </div>
            <p className="text-sm text-ink mt-1">{i.summary}</p>
            {i.products_discussed?.length > 0 && (
              <p className="text-xs text-clinical-600 mt-1">
                {i.products_discussed.join(", ")}
              </p>
            )}
            {i.is_edited && (
              <span className="text-[10px] uppercase tracking-wide text-amber-600">edited</span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
