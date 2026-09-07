"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Radar, Users, Settings, Database, Folder, Activity, HelpCircle, ChevronRight, Menu } from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();

  const links = [
    { name: "Radar", href: "/", icon: Radar },
    { name: "Leads", href: "/leads", icon: Users },
    { name: "Deals", href: "#", icon: Folder },
    { name: "Reports", href: "#", icon: Activity },
  ];

  return (
    <div className="flex h-screen w-64 flex-col border-r border-line bg-surface text-ink flex-shrink-0">
      <div className="flex h-16 items-center px-5 gap-3 border-b border-line">
        <div className="h-8 w-8 rounded bg-accent flex items-center justify-center">
          <Database className="h-4 w-4 text-white" />
        </div>
        <h1 className="font-semibold text-[16px] tracking-tight text-ink">Pivora</h1>
        <button className="ml-auto p-1 text-muted hover:text-ink"><Menu className="h-4 w-4" /></button>
      </div>
      
      <div className="p-4 border-b border-line">
        <div className="flex items-center gap-3 p-2 rounded-lg hover:bg-surface-2 cursor-pointer transition-colors">
          <div className="h-8 w-8 rounded-full bg-accent-soft text-accent flex items-center justify-center font-bold text-xs">
            W
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-[13px] font-medium text-ink truncate">williams@mesh.com</p>
          </div>
          <ChevronRight className="h-4 w-4 text-muted" />
        </div>
      </div>

      <nav className="flex-1 space-y-1.5 px-3 py-4 overflow-y-auto">
        <div className="px-3 mb-2 text-[11px] font-medium text-muted uppercase tracking-wider">Dashboard</div>
        {links.map((link) => {
          const Icon = link.icon;
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.name}
              href={link.href}
              className={`flex items-center gap-3 rounded-full px-4 py-2.5 text-[13.5px] font-medium transition-colors ${
                isActive
                  ? "bg-accent-soft text-accent"
                  : "text-muted hover:bg-surface-2 hover:text-ink"
              }`}
            >
              <Icon className="h-4 w-4" />
              {link.name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-line space-y-4">
        <div className="px-2">
          <div className="flex items-center justify-between text-[12px] mb-2">
            <span className="font-medium text-ink">Cloud Storage</span>
            <span className="text-muted">90%</span>
          </div>
          <div className="h-1.5 w-full bg-line-soft rounded-full overflow-hidden">
            <div className="h-full bg-accent w-[90%] rounded-full"></div>
          </div>
          <p className="text-[11px] text-muted mt-2">14 GB of 15 GB used</p>
        </div>
        
        <div className="space-y-1">
          <div className="flex items-center gap-3 rounded-full px-3 py-2 text-[13px] font-medium text-muted hover:bg-surface-2 hover:text-ink cursor-pointer transition-colors">
            <Settings className="h-4 w-4" />
            Settings
          </div>
          <div className="flex items-center gap-3 rounded-full px-3 py-2 text-[13px] font-medium text-muted hover:bg-surface-2 hover:text-ink cursor-pointer transition-colors">
            <HelpCircle className="h-4 w-4" />
            Help Center
          </div>
        </div>
      </div>
    </div>
  );
}
