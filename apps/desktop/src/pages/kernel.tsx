import { useState, useRef, useEffect } from "react";
import { Send, Brain, User, Plus, Check } from "lucide-react";
import { useProcessStore } from "../stores/process-store";

interface Message {
  role: "user" | "assistant";
  content: string;
}

interface ExtractedProcess {
  name: string;
  description?: string;
  goal?: string;
  deadline?: string;
  priority: number;
  estimatedEffortHours?: number;
}

export function KernelPage() {
  const addProcess = useProcessStore((s) => s.addProcess);
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content: "Hello! I am the TimeSlice AI Attention Kernel. Describe a project, ask for scheduling recommendations, or ask to optimize your calendar, and I will orchestrate the Process, Scheduling, and Calendar agents to assist you.",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  
  // Track parsed suggestions
  const [extractedProcess, setExtractedProcess] = useState<ExtractedProcess | null>(null);
  const [suggestedPolicy, setSuggestedPolicy] = useState<string | null>(null);
  const [isProcessAdded, setIsProcessAdded] = useState(false);

  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userPrompt = input.trim();
    setInput("");
    
    // Add user message to local chat list
    const updatedHistory = [...messages, { role: "user" as const, content: userPrompt }];
    setMessages(updatedHistory);
    setIsLoading(true);
    setExtractedProcess(null);
    setSuggestedPolicy(null);
    setIsProcessAdded(false);

    try {
      const payload = {
        message: userPrompt,
        history: updatedHistory.slice(1).map((m) => ({
          role: m.role,
          content: m.content,
        })),
      };

      const res = await fetch("http://localhost:8000/api/v1/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (res.ok) {
        const data = await res.json();
        
        // Append response messages
        if (data.messages && data.messages.length > 0) {
          // Find the last assistant response to show
          const assistantMsgs = data.messages.filter((m: any) => m.role === "assistant");
          if (assistantMsgs.length > 0) {
            setMessages((prev) => [...prev, { role: "assistant", content: assistantMsgs[assistantMsgs.length - 1].content }]);
          }
        }
        
        // Inspect extracted metadata
        if (data.currentProcess) {
          setExtractedProcess(data.currentProcess);
        }
        if (data.suggestedPolicy) {
          setSuggestedPolicy(data.suggestedPolicy);
        }
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: "Error: AI Kernel server returned an error." },
        ]);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "AI Kernel is currently offline. Please run the backend API server." },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddProcess = async () => {
    if (!extractedProcess) return;

    await addProcess({
      name: extractedProcess.name,
      description: extractedProcess.description || "",
      goal: extractedProcess.goal || "",
      deadline: extractedProcess.deadline || new Date(Date.now() + 7 * 86400000).toISOString().split("T")[0],
      priority: extractedProcess.priority || 3,
      estimatedEffort: extractedProcess.estimatedEffortHours || 10,
      status: "Active",
      notes: "",
    });

    setIsProcessAdded(true);
  };

  return (
    <div className="p-8 h-full flex flex-col max-w-4xl mx-auto">
      {/* Header */}
      <div className="mb-6 flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center">
          <Brain className="w-5 h-5 text-primary" />
        </div>
        <div>
          <h1 className="text-3xl font-semibold text-foreground">Attention Kernel</h1>
          <p className="text-sm text-muted-foreground mt-1">
            Natural language multi-agent scheduling interface
          </p>
        </div>
      </div>

      {/* Messages Window */}
      <div className="flex-1 min-h-0 bg-card border border-border rounded-2xl p-6 overflow-y-auto mb-4 space-y-4 shadow-inner">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex gap-4 ${msg.role === "user" ? "flex-row-reverse" : "flex-row"}`}
          >
            {/* Avatar */}
            <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 border ${
              msg.role === "user" 
                ? "bg-primary/10 border-primary/20 text-primary"
                : "bg-muted border-border text-muted-foreground"
            }`}>
              {msg.role === "user" ? <User className="w-4 h-4" /> : <Brain className="w-4 h-4" />}
            </div>
            
            {/* Text Bubble */}
            <div className={`max-w-[75%] rounded-xl p-4 text-sm ${
              msg.role === "user"
                ? "bg-primary text-primary-foreground"
                : "bg-muted text-foreground border border-border leading-relaxed"
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-4">
            <div className="w-8 h-8 rounded-lg bg-muted border border-border text-muted-foreground flex items-center justify-center animate-pulse">
              <Brain className="w-4 h-4" />
            </div>
            <div className="bg-muted text-muted-foreground rounded-xl p-4 text-sm border border-border animate-pulse">
              Kernel is thinking...
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* AI Extraction Cards */}
      {(extractedProcess || suggestedPolicy) && (
        <div className="flex gap-4 mb-4">
          {extractedProcess && (
            <div className="flex-1 bg-primary/5 border border-primary/20 rounded-xl p-4 flex items-center justify-between">
              <div>
                <p className="text-[10px] uppercase font-bold text-primary tracking-wide">AI Extracted Process</p>
                <h4 className="text-sm font-semibold text-foreground mt-1">{extractedProcess.name}</h4>
                <p className="text-xs text-muted-foreground mt-0.5">Priority: {extractedProcess.priority} | Est: {extractedProcess.estimatedEffortHours || 10}h</p>
              </div>
              <button
                onClick={handleAddProcess}
                disabled={isProcessAdded}
                className={`px-3 py-2 rounded-lg text-xs font-semibold flex items-center gap-1.5 transition-colors ${
                  isProcessAdded
                    ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20"
                    : "bg-primary text-primary-foreground hover:bg-primary/90"
                }`}
              >
                {isProcessAdded ? (
                  <>
                    <Check className="w-3.5 h-3.5" />
                    Added
                  </>
                ) : (
                  <>
                    <Plus className="w-3.5 h-3.5" />
                    Add Process
                  </>
                )}
              </button>
            </div>
          )}

          {suggestedPolicy && (
            <div className="flex-1 bg-amber-500/5 border border-amber-500/20 rounded-xl p-4 flex items-center">
              <div>
                <p className="text-[10px] uppercase font-bold text-amber-500 tracking-wide">AI Policy Suggestion</p>
                <h4 className="text-sm font-semibold text-foreground mt-1">Use {suggestedPolicy} Policy</h4>
                <p className="text-xs text-muted-foreground mt-0.5">Calculated to minimize overall attention debt.</p>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Prompt Form */}
      <form onSubmit={handleSend} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the kernel e.g., 'create a process for writing unit tests with high priority'"
          disabled={isLoading}
          className="flex-1 bg-input border border-border rounded-xl px-4 py-3.5 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50"
        />
        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="px-5 py-3.5 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-semibold flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send className="w-4 h-4" />
          Send
        </button>
      </form>
    </div>
  );
}
