import React, { ErrorInfo } from "react";
import { AlertTriangle, RotateCcw, Trash2 } from "lucide-react";

interface Props {
  children: React.ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends React.Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
    errorInfo: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error, errorInfo: null };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    this.setState({ errorInfo });
    this.logErrorToTelemetry(error, errorInfo);
  }

  private async logErrorToTelemetry(error: Error, errorInfo: ErrorInfo) {
    try {
      const payload = {
        error: error.toString(),
        stack: error.stack,
        componentStack: errorInfo.componentStack,
        timestamp: new Date().toISOString(),
        platform: "Tauri Desktop",
      };

      // Mock telemetry HTTP report POST call
      await fetch("http://localhost:8000/api/v1/telemetry/crash", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      console.warn("Crash report sent successfully to telemetry server.");
    } catch (err) {
      console.error("Failed to send crash report:", err);
    }
  }

  private handleReload = () => {
    window.location.reload();
  };

  private handleResetCache = () => {
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = "/";
  };

  public render() {
    if (this.state.hasError) {
      return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-background p-6">
          <div className="w-full max-w-2xl bg-card border border-border rounded-2xl p-8 shadow-2xl relative overflow-hidden">
            <div className="absolute -top-24 -right-24 w-48 h-48 rounded-full bg-destructive/10 blur-3xl"></div>

            <div className="flex items-center gap-4 mb-6">
              <div className="w-12 h-12 rounded-2xl bg-destructive/10 border border-destructive/20 flex items-center justify-center shrink-0">
                <AlertTriangle className="w-6 h-6 text-destructive" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-foreground">Application Crash Detected</h1>
                <p className="text-xs text-muted-foreground mt-0.5">
                  TimeSlice AI encountered an unexpected rendering exception.
                </p>
              </div>
            </div>

            {/* Error Message */}
            <div className="bg-destructive/5 border border-destructive/10 rounded-xl p-4 mb-6">
              <p className="text-xs font-mono text-destructive font-semibold">
                {this.state.error?.toString()}
              </p>
            </div>

            {/* Stack trace */}
            <div className="mb-6">
              <label className="block text-[10px] uppercase tracking-wide text-muted-foreground mb-2 font-semibold">
                Error Trace Log
              </label>
              <pre className="w-full h-40 bg-muted border border-border rounded-lg p-4 font-mono text-[10px] text-muted-foreground overflow-auto whitespace-pre-wrap leading-relaxed select-text">
                {this.state.error?.stack || "No trace log available."}
                {"\n\nComponent Stack:\n"}
                {this.state.errorInfo?.componentStack || "No component stack available."}
              </pre>
            </div>

            {/* Actions */}
            <div className="flex gap-3 justify-end pt-2 border-t border-border">
              <button
                onClick={this.handleResetCache}
                className="px-4 py-2 rounded-lg border border-border bg-muted hover:bg-muted/80 text-xs font-semibold text-muted-foreground flex items-center gap-1.5 transition-colors"
              >
                <Trash2 className="w-3.5 h-3.5" />
                Clear Cache & Reset
              </button>
              <button
                onClick={this.handleReload}
                className="px-5 py-2 rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground text-xs font-semibold flex items-center gap-1.5 transition-colors shadow-lg shadow-primary/10"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Reload Application
              </button>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
