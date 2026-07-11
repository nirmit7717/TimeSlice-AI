import { useState } from "react";
import { Brain, Lock, Mail, User } from "lucide-react";
import { useAuthStore } from "../../stores/auth-store";

export function LoginOverlay() {
  const login = useAuthStore((s) => s.login);
  const signup = useAuthStore((s) => s.signup);

  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (!email.trim() || !password.trim()) {
      setError("Please fill out all fields.");
      return;
    }

    if (isSignUp) {
      if (!name.trim()) {
        setError("Please enter your name.");
        return;
      }
      signup(email.trim(), name.trim());
    } else {
      login(email.trim(), email.split("@")[0]);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/95 backdrop-blur-sm p-4">
      <div className="w-full max-w-md bg-card border border-border rounded-2xl p-8 shadow-2xl relative overflow-hidden">
        {/* Decorative background glow */}
        <div className="absolute -top-24 -right-24 w-48 h-48 rounded-full bg-primary/10 blur-3xl"></div>
        <div className="absolute -bottom-24 -left-24 w-48 h-48 rounded-full bg-secondary/10 blur-3xl"></div>

        {/* Logo */}
        <div className="flex flex-col items-center mb-8 relative">
          <div className="w-12 h-12 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center mb-3">
            <Brain className="w-6 h-6 text-primary animate-pulse" />
          </div>
          <h2 className="text-2xl font-bold text-foreground">TimeSlice AI</h2>
          <p className="text-xs text-muted-foreground mt-1">
            {isSignUp ? "Create your local-first account" : "Sign in to manage your attention"}
          </p>
        </div>

        {error && (
          <div className="bg-destructive/10 border border-destructive/20 rounded-xl p-3 mb-4 text-xs text-destructive text-center">
            {error}
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4 relative">
          {isSignUp && (
            <div>
              <label className="block text-[10px] uppercase tracking-wide text-muted-foreground mb-1.5 font-semibold">
                Full Name
              </label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="John Doe"
                  required
                  className="w-full bg-input border border-border rounded-lg pl-10 pr-4 py-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
                />
              </div>
            </div>
          )}

          <div>
            <label className="block text-[10px] uppercase tracking-wide text-muted-foreground mb-1.5 font-semibold">
              Email Address
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="developer@timeslice.ai"
                required
                className="w-full bg-input border border-border rounded-lg pl-10 pr-4 py-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
          </div>

          <div>
            <label className="block text-[10px] uppercase tracking-wide text-muted-foreground mb-1.5 font-semibold">
              Password
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                className="w-full bg-input border border-border rounded-lg pl-10 pr-4 py-2.5 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-primary/50"
              />
            </div>
          </div>

          <button
            type="submit"
            className="w-full mt-2 py-3 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-sm transition-colors shadow-lg shadow-primary/20"
          >
            {isSignUp ? "Sign Up" : "Sign In"}
          </button>
        </form>

        {/* Form Toggle */}
        <div className="text-center mt-6 text-xs text-muted-foreground relative">
          <span>{isSignUp ? "Already have an account?" : "New to TimeSlice?"} </span>
          <button
            onClick={() => {
              setIsSignUp(!isSignUp);
              setError("");
            }}
            className="text-primary hover:underline font-semibold"
          >
            {isSignUp ? "Sign In" : "Create Account"}
          </button>
        </div>
      </div>
    </div>
  );
}
