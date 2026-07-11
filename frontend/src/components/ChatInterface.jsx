import { useState, useRef, useEffect } from "react";
import { useDispatch, useSelector } from "react-redux";
import { sendChatMessage } from "../store/chatSlice";
import { fetchHcpHistory } from "../store/hcpSlice";
import ToolCallBadge from "./ToolCallBadge";

export default function ChatInterface() {
  const dispatch = useDispatch();
  const { messages, status } = useSelector((s) => s.chat);
  const { selectedHcpId } = useSelector((s) => s.hcps);
  const [input, setInput] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || !selectedHcpId) return;
    const message = input;
    setInput("");
    await dispatch(sendChatMessage({ message, hcpId: selectedHcpId, repName: "Field Rep" }));
    dispatch(fetchHcpHistory(selectedHcpId));
  };

  return (
    <div className="bg-white rounded-xl shadow-card border border-slate-100 flex flex-col h-full">
      <div className="px-5 py-3 border-b border-slate-100">
        <h3 className="text-sm font-semibold text-ink">FieldMate Agent</h3>
        <p className="text-xs text-slate-400">Describe the visit in your own words</p>
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-3 min-h-[280px]">
        {messages.length === 0 && (
          <div className="text-sm text-slate-400 bg-slate-50 rounded-lg p-3">
            Try: "Met Dr. Rao this morning, discussed CardioGuard XR dosing for elderly
            patients, she seemed positive and I left 2 samples. Remind me to follow up in
            a week."
          </div>
        )}
        {messages.map((m, idx) => (
          <div key={idx} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
            <div className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-sm
                             ${m.role === "user"
                               ? "bg-clinical-500 text-white rounded-br-sm"
                               : "bg-slate-100 text-ink rounded-bl-sm"}`}>
              <p>{m.content}</p>
              {m.toolCalls?.map((tc, i) => (
                <ToolCallBadge key={i} toolCall={tc} />
              ))}
            </div>
          </div>
        ))}
        {status === "loading" && (
          <div className="text-xs text-slate-400 italic">FieldMate is thinking…</div>
        )}
        <div ref={bottomRef} />
      </div>

      <form onSubmit={handleSend} className="border-t border-slate-100 p-3 flex gap-2">
        <input
          className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm
                     focus:outline-none focus:ring-2 focus:ring-clinical-400"
          placeholder="Log or edit an interaction, or ask what to discuss next…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={!selectedHcpId}
        />
        <button
          type="submit"
          disabled={!selectedHcpId || status === "loading"}
          className="rounded-lg bg-clinical-500 hover:bg-clinical-600 disabled:opacity-50
                     text-white text-sm font-semibold px-4 transition-colors"
        >
          Send
        </button>
      </form>
    </div>
  );
}
