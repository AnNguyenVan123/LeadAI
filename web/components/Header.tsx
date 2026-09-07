import { Search, Bell, Download, Settings, LayoutDashboard } from "lucide-react";

export default function Header() {
  return (
    <header className="h-16 border-b border-line bg-surface px-6 flex items-center justify-between sticky top-0 z-10">
      <div className="flex items-center gap-3">
        <div className="h-8 w-8 rounded-lg bg-surface-2 border border-line flex items-center justify-center">
          <LayoutDashboard className="h-4 w-4 text-ink" />
        </div>
        <h2 className="font-semibold text-[15px] text-ink">Dashboard</h2>
      </div>
      
      <div className="flex items-center gap-4">
        <div className="relative hidden md:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted" />
          <input 
            type="text" 
            placeholder="Search AI Mode" 
            className="pl-9 pr-4 py-1.5 w-64 rounded-full border border-line bg-surface-2 text-[13px] outline-none focus:border-accent focus:bg-surface transition-colors"
          />
        </div>
        
        <div className="flex items-center gap-2 border-l border-line pl-4">
          <button className="p-1.5 text-muted hover:text-ink hover:bg-surface-2 rounded-full transition-colors">
            <Bell className="h-4 w-4" />
          </button>
          <button className="p-1.5 text-muted hover:text-ink hover:bg-surface-2 rounded-full transition-colors">
            <Settings className="h-4 w-4" />
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent text-white text-[13px] font-medium hover:brightness-110 transition-all ml-2">
            <Download className="h-3.5 w-3.5" />
            Exports
          </button>
        </div>
      </div>
    </header>
  );
}
