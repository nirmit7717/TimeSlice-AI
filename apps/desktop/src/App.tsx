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
import { PlaceholderPage } from "./pages/placeholder";

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
  return (
    <BrowserRouter>
      <AppLayout>
        <Routes>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/processes" element={<ProcessesPage />} />
          <Route path="/processes/new" element={<ProcessCreatePage />} />
          <Route path="/calendar" element={<CalendarPage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route
            path="/kernel"
            element={
              <PlaceholderPage
                title="Attention Kernel"
                description="Natural language chat with the AI kernel for scheduling recommendations, process management, and checklist generation."
              />
            }
          />
          <Route
            path="/vault"
            element={
              <PlaceholderPage
                title="Context Vault"
                description="Long-term contextual memory, embeddings, notes, and project knowledge stored locally."
              />
            }
          />
          <Route path="/settings" element={<SettingsPage />} />
        </Routes>
      </AppLayout>
    </BrowserRouter>
  );
}

export default App;
