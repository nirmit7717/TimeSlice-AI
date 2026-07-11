import { Sparkles, PlusCircle, Clock, Target, Zap } from "lucide-react";

interface OnboardingProps {
  onCreateProcess?: () => void;
}

export function Onboarding({ onCreateProcess }: OnboardingProps) {
  return (
    <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-8">
      {/* Icon / Hero */}
      <div className="relative mb-8">
        <div className="w-24 h-24 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center">
          <Sparkles className="w-12 h-12 text-primary" />
        </div>
        <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-emerald-400 flex items-center justify-center">
          <span className="text-black text-xs font-bold">✓</span>
        </div>
      </div>

      {/* Headline */}
      <h1 className="text-3xl font-bold text-foreground mb-3">
        Welcome to TimeSlice AI
      </h1>
      <p className="text-muted-foreground text-base max-w-md mb-10">
        Your personal attention OS. Create your first Process and the Attention
        Kernel will take care of the rest — scheduling, reminders, and adaptive
        recommendations.
      </p>

      {/* Steps */}
      <div className="grid grid-cols-3 gap-6 mb-12 max-w-2xl w-full">
        {[
          {
            icon: PlusCircle,
            color: "text-blue-400 bg-blue-400/10 border-blue-400/20",
            step: "1",
            title: "Create a Process",
            desc: "Define a goal, set a deadline, and estimate your effort.",
          },
          {
            icon: Target,
            color: "text-purple-400 bg-purple-400/10 border-purple-400/20",
            step: "2",
            title: "Generate a Plan",
            desc: "The Scheduling Engine allocates your attention automatically.",
          },
          {
            icon: Zap,
            color: "text-amber-400 bg-amber-400/10 border-amber-400/20",
            step: "3",
            title: "Execute & Reflect",
            desc: "Work in Time Slices. The system learns and improves for you.",
          },
        ].map(({ icon: Icon, color, step, title, desc }) => (
          <div
            key={step}
            className="bg-card border border-border rounded-xl p-6 flex flex-col items-center text-center"
          >
            <div
              className={`w-12 h-12 rounded-xl border flex items-center justify-center mb-4 ${color}`}
            >
              <Icon className="w-6 h-6" />
            </div>
            <p className="text-xs text-muted-foreground mb-1">Step {step}</p>
            <p className="text-sm font-semibold text-foreground mb-2">{title}</p>
            <p className="text-xs text-muted-foreground leading-relaxed">{desc}</p>
          </div>
        ))}
      </div>

      {/* CTA */}
      <button
        onClick={onCreateProcess}
        className="px-8 py-3.5 rounded-xl text-base font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all hover:scale-105 active:scale-100 flex items-center gap-3 shadow-lg shadow-primary/25"
      >
        <PlusCircle className="w-5 h-5" />
        Create Your First Process
      </button>

      <div className="mt-6 flex items-center gap-2 text-xs text-muted-foreground">
        <Clock className="w-3.5 h-3.5" />
        <span>Takes less than 2 minutes to set up</span>
      </div>
    </div>
  );
}
