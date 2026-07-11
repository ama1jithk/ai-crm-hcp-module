import { useState } from "react";
import { useDispatch, useSelector } from "react-redux";
import { createInteraction } from "../store/interactionsSlice";
import { fetchHcpHistory } from "../store/hcpSlice";

const TYPES = ["visit", "call", "email", "event", "sample_drop"];
const SENTIMENTS = ["positive", "neutral", "negative"];

const EMPTY = {
  interaction_type: "visit",
  topics: "",
  products: "",
  samples: "",
  sentiment: "neutral",
  follow_up_required: false,
  follow_up_notes: "",
  summary: "",
};

export default function StructuredForm() {
  const dispatch = useDispatch();
  const { selectedHcpId } = useSelector((s) => s.hcps);
  const { formStatus } = useSelector((s) => s.interactions);
  const repName = useSelector((s) => s.rep.name);
  const [form, setForm] = useState(EMPTY);

  const set = (key) => (e) =>
    setForm((f) => ({
      ...f,
      [key]: e.target.type === "checkbox" ? e.target.checked : e.target.value,
    }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedHcpId) return;
    await dispatch(
      createInteraction({
        hcp_id: selectedHcpId,
        rep_name: repName || "Field Rep",
        channel: "form",
        interaction_type: form.interaction_type,
        summary: form.summary,
        topics_discussed: form.topics.split(",").map((t) => t.trim()).filter(Boolean),
        products_discussed: form.products.split(",").map((t) => t.trim()).filter(Boolean),
        samples_provided: form.samples.split(",").map((t) => t.trim()).filter(Boolean),
        sentiment: form.sentiment,
        follow_up_required: form.follow_up_required,
        follow_up_notes: form.follow_up_notes,
      })
    );
    dispatch(fetchHcpHistory(selectedHcpId));
    setForm(EMPTY);
  };

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-xl shadow-card border border-slate-100 p-5 space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="text-xs font-semibold text-slate-500">Interaction Type</label>
          <select
            className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
            value={form.interaction_type}
            onChange={set("interaction_type")}
          >
            {TYPES.map((t) => (
              <option key={t} value={t}>{t.replace("_", " ")}</option>
            ))}
          </select>
        </div>
        <div>
          <label className="text-xs font-semibold text-slate-500">Sentiment</label>
          <select
            className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
            value={form.sentiment}
            onChange={set("sentiment")}
          >
            {SENTIMENTS.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
      </div>

      <div>
        <label className="text-xs font-semibold text-slate-500">Summary</label>
        <textarea
          className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm min-h-[70px]"
          placeholder="Discussed CardioGuard XR dosing for elderly patients..."
          value={form.summary}
          onChange={set("summary")}
          required
        />
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div>
          <label className="text-xs font-semibold text-slate-500">Topics (comma-sep)</label>
          <input className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                 value={form.topics} onChange={set("topics")} placeholder="efficacy, side-effects" />
        </div>
        <div>
          <label className="text-xs font-semibold text-slate-500">Products (comma-sep)</label>
          <input className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                 value={form.products} onChange={set("products")} placeholder="CardioGuard XR" />
        </div>
        <div>
          <label className="text-xs font-semibold text-slate-500">Samples (comma-sep)</label>
          <input className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                 value={form.samples} onChange={set("samples")} placeholder="2x CardioGuard 10mg" />
        </div>
      </div>

      <div className="flex items-center gap-3">
        <label className="flex items-center gap-2 text-sm text-slate-600">
          <input type="checkbox" checked={form.follow_up_required} onChange={set("follow_up_required")} />
          Follow-up required
        </label>
        {form.follow_up_required && (
          <input
            className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm"
            placeholder="Follow-up note"
            value={form.follow_up_notes}
            onChange={set("follow_up_notes")}
          />
        )}
      </div>

      <button
        type="submit"
        disabled={!selectedHcpId || formStatus === "saving"}
        className="w-full rounded-lg bg-clinical-500 hover:bg-clinical-600 disabled:opacity-50
                   text-white text-sm font-semibold py-2.5 transition-colors"
      >
        {formStatus === "saving" ? "Saving..." : "Log Interaction"}
      </button>
    </form>
  );
}
