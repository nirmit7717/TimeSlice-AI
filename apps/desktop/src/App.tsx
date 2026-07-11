import { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { Sidebar } from "./components/layout/sidebar";
import { Header } from "./components/layout/header";
import { AttentionKernelPanel } from "./components/shared/attention-kernel-panel";
import { OfflineBanner } from "./components/shared/offline-banner";
import { DashboardPage } from "./pages/dashboard";
import { ProcessesPage } from "./pages/processes";
import { ProcessCreatePage } from "./pages/process-create";
import { CalendarPage } from "./pages/calendar";
import { AnalyticsPage } from "./pages/analytics";
import { SettingsPage } from "./pages/settings";
import { KernelPage } from "./pages/kernel";
import { VaultPage } from "./pages/vault";
import { useProcessStore } from "./stores/process-store";
import { useAuthStore } from "./stores/auth-store";
import { LoginOverlay } from "./components/layout/login-overlay";

function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <OfflineBanner />
        <Header />
        <div className="flex-1 flex overflow-hidden">
          <div className="flex-1 overflow-y-auto">{children}</div>
          <AttentionKernelPanel />
        </div>
      </div>
    </div>
  );
}

function App() {
  const fetchProcesses = useProcessStore((state) => state.fetchProcesses);
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  useEffect(() => {
    if (isAuthenticated) {
      fetchProcesses();
    }
  }, [fetchProcesses, isAuthenticated]);

  if (!isAuthenticated) {
    return <LoginOverlay />;
  }

  return (
    <BrowserRouter>
      <AppLayout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/processes" element={<ProcessesPage />} />
          <Route path="/processes/new" element={<ProcessCreatePage />} />
          <Route path="/calendar" element={<CalendarPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/kernel" element={<KernelPage />} />
          <Route path="/vault" element={<VaultPage />} />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  );
}

export default App;
