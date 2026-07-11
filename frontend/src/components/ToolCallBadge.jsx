const TOOL_LABELS = {
  log_interaction: { label: "Log Interaction", color: "bg-clinical-100 text-clinical-700" },
  edit_interaction: { label: "Edit Interaction", color: "bg-accent/20 text-amber-800" },
  get_hcp_profile: { label: "Get HCP Profile", color: "bg-slate-100 text-slate-700" },
  schedule_follow_up: { label: "Schedule Follow-up", color: "bg-indigo-100 text-indigo-700" },
  suggest_next_best_action: { label: "Suggest Next Action", color: "bg-rose-100 text-rose-700" },
};

export default function ToolCallBadge({ toolCall }) {
  const meta = TOOL_LABELS[toolCall.tool_name] || {
    label: toolCall.tool_name,
    color: "bg-slate-100 text-slate-700",
  };

  return (
    <details className="mt-2 rounded-lg border border-slate-200 bg-slate-50 open:bg-white">
      <summary
        className={`cursor-pointer select-none list-none px-3 py-1.5 rounded-lg text-xs
                    font-semibold inline-flex items-center gap-1.5 ${meta.color}`}
      >
        <span className="w-1.5 h-1.5 rounded-full bg-current" />
        Tool called: {meta.label}
      </summary>
      <div className="px-3 pb-3 pt-1 text-xs font-mono text-slate-600 space-y-1">
        <div>
          <span className="text-slate-400">input:</span>{" "}
          {JSON.stringify(toolCall.tool_input)}
        </div>
        <div className="break-all">
          <span className="text-slate-400">output:</span> {toolCall.tool_output}
        </div>
      </div>
    </details>
  );
}
