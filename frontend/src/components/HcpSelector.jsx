import { useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { fetchHcps, selectHcp, fetchHcpHistory } from "../store/hcpSlice";

export default function HcpSelector() {
  const dispatch = useDispatch();
  const { list, selectedHcpId, status } = useSelector((s) => s.hcps);

  useEffect(() => {
    dispatch(fetchHcps());
  }, [dispatch]);

  useEffect(() => {
    if (selectedHcpId) dispatch(fetchHcpHistory(selectedHcpId));
  }, [dispatch, selectedHcpId]);

  const selected = list.find((h) => h.id === selectedHcpId);

  return (
    <div className="bg-white rounded-xl shadow-card border border-slate-100 p-4">
      <label className="text-xs font-semibold uppercase tracking-wide text-slate-500">
        Healthcare Professional
      </label>
      {status === "loading" && list.length === 0 ? (
        <div className="mt-2 h-9 rounded-lg bg-slate-100 animate-pulse" />
      ) : (
        <select
          className="mt-2 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-clinical-400"
          value={selectedHcpId || ""}
          onChange={(e) => dispatch(selectHcp(e.target.value))}
        >
          {list.map((h) => (
            <option key={h.id} value={h.id}>
              Dr. {h.first_name} {h.last_name} — {h.specialty}
            </option>
          ))}
        </select>
      )}
      {selected && (
        <div className="mt-3 text-sm text-slate-600 space-y-0.5">
          <p className="font-medium text-ink">{selected.institution}</p>
          <p>{selected.territory}</p>
          {selected.preferred_products?.length > 0 && (
            <p className="text-xs text-clinical-600 mt-1">
              Preferred: {selected.preferred_products.join(", ")}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
