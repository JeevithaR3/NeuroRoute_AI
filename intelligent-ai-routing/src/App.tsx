import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Route, Routes } from "react-router-dom";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/contexts/AuthContext";
import ProtectedRoute from "@/components/ProtectedRoute";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import Index from "./pages/Index";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Architecture from "./pages/Architecture";
import ExtensionSetup from "./pages/ExtensionSetup";
import MiddlewareInstall from "./pages/MiddlewareInstall";
import ModelConfig from "./pages/ModelConfig";
import QueryRouting from "./pages/QueryRouting";
import EnvironmentalImpact from "./pages/EnvironmentalImpact";
import DatasetGeneration from "./pages/DatasetGeneration";
import ApiDocs from "./pages/ApiDocs";
import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const ProtectedLayout = ({ children }: { children: React.ReactNode }) => (
  <ProtectedRoute>
    <Navbar />
    {children}
    <Footer />
  </ProtectedRoute>
);

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/" element={<><Navbar /><Index /><Footer /></>} />
            <Route path="/login" element={<Login />} />
            <Route path="/signup" element={<Signup />} />

            {/* Protected routes - require login */}
            <Route path="/architecture" element={<ProtectedLayout><Architecture /></ProtectedLayout>} />
            <Route path="/extension-setup" element={<ProtectedLayout><ExtensionSetup /></ProtectedLayout>} />
            <Route path="/middleware-install" element={<ProtectedLayout><MiddlewareInstall /></ProtectedLayout>} />
            <Route path="/model-config" element={<ProtectedLayout><ModelConfig /></ProtectedLayout>} />
            <Route path="/query-routing" element={<ProtectedLayout><QueryRouting /></ProtectedLayout>} />
            <Route path="/environmental-impact" element={<ProtectedLayout><EnvironmentalImpact /></ProtectedLayout>} />
            <Route path="/dataset" element={<ProtectedLayout><DatasetGeneration /></ProtectedLayout>} />
            <Route path="/api-docs" element={<ProtectedLayout><ApiDocs /></ProtectedLayout>} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;
