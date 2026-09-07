"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Radar, Users, Settings } from "lucide-react";

export default function Sidebar() {
  const pathname = usePathname();

  const links = [
    { name: "Radar", href: "/", icon: Radar },
    { name: "My Leads", href: "/leads", icon: Users },
  ];

  return (
    <div className="flex h-screen w-64 flex-col border-r border-line bg-surface/50 text-main">
      <div className="flex h-16 items-center px-6">
        <h1 className="font-cond font-bold text-xl tracking-tight text-main">LeadAI CRM</h1>
      </div>
      <nav className="flex-1 space-y-1 px-3 py-4">
        {links.map((link) => {
          const Icon = link.icon;
          const isActive = pathname === link.href;
          return (
            <Link
              key={link.name}
              href={link.href}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-[14px] font-medium transition-colors ${
                isActive
                  ? "bg-hot/10 text-hot"
                  : "text-muted hover:bg-surface hover:text-main"
              }`}
            >
              <Icon className="h-5 w-5" />
              {link.name}
            </Link>
          );
        })}
      </nav>
      <div className="p-4 border-t border-line">
        <div className="flex items-center gap-3 rounded-lg px-3 py-2 text-[14px] font-medium text-muted hover:bg-surface hover:text-main cursor-not-allowed opacity-50">
          <Settings className="h-5 w-5" />
          Cài đặt
        </div>
      </div>
    </div>
  );
}
