import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "@/contexts/AuthContext";
import { Button } from "@/components/ui/button";
import { Zap, Menu, X, LogOut, LogIn } from "lucide-react";

const navLinks = [
  { to: "/", label: "Home", protected: false },
  { to: "/architecture", label: "Architecture", protected: true },
  { to: "/extension-setup", label: "Extension", protected: true },
  { to: "/middleware-install", label: "Middleware", protected: true },
  { to: "/model-config", label: "Models", protected: true },
  { to: "/query-routing", label: "Routing", protected: true },
  { to: "/environmental-impact", label: "Impact", protected: true },
  { to: "/dataset", label: "Dataset", protected: true },
  { to: "/api-docs", label: "API", protected: true },
];

const Navbar = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [open, setOpen] = useState(false);

  const visibleLinks = navLinks.filter((l) => !l.protected || user);

  return (
    <nav className="sticky top-0 z-50 glass border-b border-border/50">
      <div className="container flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <Zap className="h-6 w-6 text-primary" />
          <span className="text-lg font-bold text-gradient">NeuroRoute</span>
        </Link>

        {/* Desktop */}
        <div className="hidden lg:flex items-center gap-1">
          {visibleLinks.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                location.pathname === l.to
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground hover:text-foreground"
              }`}
            >
              {l.label}
            </Link>
          ))}
          {user ? (
            <Button variant="ghost" size="sm" onClick={logout} className="ml-2 text-muted-foreground">
              <LogOut className="h-4 w-4 mr-1" /> Logout
            </Button>
          ) : (
            <Button variant="ghost" size="sm" asChild className="ml-2 text-muted-foreground">
              <Link to="/login"><LogIn className="h-4 w-4 mr-1" /> Login</Link>
            </Button>
          )}
        </div>

        {/* Mobile toggle */}
        <button className="lg:hidden text-foreground" onClick={() => setOpen(!open)}>
          {open ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
        </button>
      </div>

      {/* Mobile menu */}
      {open && (
        <div className="lg:hidden glass border-t border-border/50 p-4 space-y-1">
          {visibleLinks.map((l) => (
            <Link
              key={l.to}
              to={l.to}
              onClick={() => setOpen(false)}
              className={`block px-3 py-2 rounded-md text-sm font-medium ${
                location.pathname === l.to
                  ? "bg-accent text-accent-foreground"
                  : "text-muted-foreground"
              }`}
            >
              {l.label}
            </Link>
          ))}
          {user ? (
            <button onClick={() => { logout(); setOpen(false); }} className="w-full text-left px-3 py-2 text-sm text-muted-foreground">
              Logout
            </button>
          ) : (
            <Link to="/login" onClick={() => setOpen(false)} className="block px-3 py-2 text-sm text-muted-foreground">
              Login
            </Link>
          )}
        </div>
      )}
    </nav>
  );
};

export default Navbar;
