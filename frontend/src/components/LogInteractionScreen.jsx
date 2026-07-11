import { useState } from "react";
import HcpSelector from "./HcpSelector";
import StructuredForm from "./StructuredForm";
import ChatInterface from "./ChatInterface";
import InteractionHistory from "./InteractionHistory";

export default function LogInteractionScreen() {
  const [mode, setMode] = useState("chat"); // "chat" | "form"

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <header className="mb-6">
        <p className="text-xs font-semibold tracking-widest text-clinical-500 uppercase">
          HCP Module
        </p>
        <h1 className="text-2xl font-bold text-ink mt-1">Log Interaction</h1>
        <p className="text-sm text-slate-500 mt-1">
          Capture a Healthcare Professional interaction via a structured form or by
          talking to the FieldMate agent.
        </p>
      </header>

      <div className="grid grid-cols-3 gap-6">
        <div className="col-span-1 space-y-6">
          <HcpSelector />
          <InteractionHistory />
        </div>

        <div className="col-span-2">
          <div className="inline-flex bg-slate-100 rounded-lg p-1 mb-4">
            {["chat", "form"].map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`px-4 py-1.5 rounded-md text-sm font-semibold transition-colors
                            ${mode === m ? "bg-white shadow-card text-ink" : "text-slate-500"}`}
              >
                {m === "chat" ? "Conversational" : "Structured Form"}
              </button>
            ))}
          </div>

          <div className="h-[520px]">
            {mode === "chat" ? <ChatInterface /> : <StructuredForm />}
          </div>
        </div>
      </div>
    </div>
  );
}
