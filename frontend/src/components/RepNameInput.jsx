import { useDispatch, useSelector } from "react-redux";
import { setRepName } from "../store/repSlice";

export default function RepNameInput() {
  const dispatch = useDispatch();
  const repName = useSelector((s) => s.rep.name);

  return (
    <div className="flex items-center gap-2">
      <label htmlFor="rep-name-input" className="text-xs font-medium text-slate-500">
        Rep name
      </label>
      <input
        id="rep-name-input"
        name="repName"
        type="text"
        placeholder="Your name"
        value={repName}
        onChange={(e) => dispatch(setRepName(e.target.value))}
        className="w-40 rounded-lg border border-slate-200 px-3 py-1.5 text-sm
                   focus:outline-none focus:ring-2 focus:ring-clinical-400"
      />
    </div>
  );
}

