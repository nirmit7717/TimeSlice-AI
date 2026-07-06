import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ArrowLeft } from "lucide-react";
import { useProcessStore, type ProcessStatus } from "../stores/process-store";

export function ProcessCreatePage() {
  const navigate = useNavigate();
  const addProcess = useProcessStore((s) => s.addProcess);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [goal, setGoal] = useState("");
  const [deadline, setDeadline] = useState("");
  const [priority, setPriority] = useState(3);
  const [estimatedEffort, setEstimatedEffort] = useState<number>(10);
  const [status, setStatus] = useState<ProcessStatus>("Active");
  const [notes, setNotes] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!name.trim()) return;

    addProcess({
      name: name.trim(),
      description: description.trim(),
      goal: goal.trim(),
      deadline: deadline || new Date(Date.now() + 7 * 86400000).toISOString().split("T")[0],
      priority,
      estimatedEffort,
      status,
      notes: notes.trim(),
    });

    navigate("/processes");
  };

  return (
    <div className="p-8 max-w-2xl">
      {/* Back Link */}
      <Link
        to="/processes"
        className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-6"
      >
        <ArrowLeft className="w-4 h-4" />
        Back to Processes
      </Link>

      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-semibold text-foreground">
          Create Process
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          Define a new project that will compete for your attention
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Name */}
        <div>
          <label className="block text-xs uppercase tracking-wide text-muted-foreground mb-2 font-medium">
            Process Name *
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g., Backend Scheduler API"
            required
            className="w-full bg-input border border-border rounded-lg px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50"
          />
        </div>

        {/* Description */}
        <div>
          <label className="block text-xs uppercase tracking-wide text-muted-foreground mb-2 font-medium">
            Description
          </label>
          <textarea
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Brief description of this process..."
            className="w-full bg-input border border-border rounded-lg px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 resize-none"
          />
        </div>

        {/* Goal */}
        <div>
          <label className="block text-xs uppercase tracking-wide text-muted-foreground mb-2 font-medium">
            Goal
          </label>
          <textarea
            rows={2}
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            placeholder="What does completion look like?"
            className="w-full bg-input border border-border rounded-lg px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 resize-none"
          />
        </div>

        {/* Two columns: Deadline + Priority */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs uppercase tracking-wide text-muted-foreground mb-2 font-medium">
              Deadline
            </label>
            <input
              type="date"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              className="w-full bg-input border border-border rounded-lg px-4 py-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50"
            />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-wide text-muted-foreground mb-2 font-medium">
              Priority (1–5)
            </label>
            <select
              value={priority}
              onChange={(e) => setPriority(Number(e.target.value))}
              className="w-full bg-input border border-border rounded-lg px-4 py-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50"
            >
              <option value={1}>1 — Low</option>
              <option value={2}>2 — Below Average</option>
              <option value={3}>3 — Medium</option>
              <option value={4}>4 — High</option>
              <option value={5}>5 — Critical</option>
            </select>
          </div>
        </div>

        {/* Two columns: Estimated Effort + Status */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs uppercase tracking-wide text-muted-foreground mb-2 font-medium">
              Estimated Effort (hours)
            </label>
            <input
              type="number"
              min={1}
              value={estimatedEffort}
              onChange={(e) => setEstimatedEffort(Number(e.target.value))}
              placeholder="e.g., 40"
              className="w-full bg-input border border-border rounded-lg px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50"
            />
          </div>
          <div>
            <label className="block text-xs uppercase tracking-wide text-muted-foreground mb-2 font-medium">
              Initial Status
            </label>
            <select
              value={status}
              onChange={(e) => setStatus(e.target.value as ProcessStatus)}
              className="w-full bg-input border border-border rounded-lg px-4 py-3 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50"
            >
              <option value="Active">Active</option>
              <option value="Paused">Paused</option>
            </select>
          </div>
        </div>

        {/* Notes */}
        <div>
          <label className="block text-xs uppercase tracking-wide text-muted-foreground mb-2 font-medium">
            Notes (optional)
          </label>
          <textarea
            rows={3}
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Any additional context or notes..."
            className="w-full bg-input border border-border rounded-lg px-4 py-3 text-sm text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary/50 resize-none"
          />
        </div>

        {/* Actions */}
        <div className="flex gap-3 pt-4">
          <button
            type="submit"
            className="px-6 py-2.5 rounded-lg text-sm font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-colors"
          >
            Create Process
          </button>
          <Link
            to="/processes"
            className="px-4 py-2.5 rounded-lg text-sm font-medium text-muted-foreground bg-muted hover:bg-muted/80 transition-colors"
          >
            Cancel
          </Link>
        </div>
      </form>
    </div>
  );
}
