import LogInteractionScreen from "./components/LogInteractionScreen";
import RepNameInput from "./components/RepNameInput";

export default function App() {
  return (
    <div className="min-h-screen bg-[#F7F9F9]">
      <nav className="bg-white border-b border-slate-100 px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-md bg-clinical-500 flex items-center justify-center text-white text-xs font-bold">
            AI
          </div>
          <span className="font-semibold text-ink">AI-First CRM</span>
          <span className="text-slate-300">/</span>
          <span className="text-slate-500 text-sm">HCP Module</span>
        </div>
        <RepNameInput />
      </nav>
      <LogInteractionScreen />
    </div>
  );
}
