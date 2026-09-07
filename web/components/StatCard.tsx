import { Info, ArrowUp, ArrowDown } from "lucide-react";

export default function StatCard({ 
  title, 
  value, 
  trend, 
  trendValue, 
  subtitle 
}: { 
  title: string; 
  value: string; 
  trend: "up" | "down"; 
  trendValue: string; 
  subtitle: string;
}) {
  return (
    <div className="rounded-lg border border-line bg-surface p-5">
      <div className="flex items-center justify-between mb-2">
        <h3 className="font-semibold text-[14px] text-ink flex items-center gap-2">
          {title}
          <Info className="h-3.5 w-3.5 text-muted cursor-help" />
        </h3>
      </div>
      <div className="flex items-baseline gap-2 mt-4">
        <span className="font-bold text-2xl text-ink">{value}</span>
        <span className={`flex items-center text-[12px] font-medium px-1.5 py-0.5 rounded ${
          trend === "up" ? "text-cool bg-cool-soft" : "text-hot bg-hot-soft"
        }`}>
          {trend === "up" ? <ArrowUp className="h-3 w-3 mr-0.5" /> : <ArrowDown className="h-3 w-3 mr-0.5" />}
          {trendValue}
        </span>
      </div>
      <p className="text-[12px] text-muted mt-2 font-medium">{subtitle}</p>
    </div>
  );
}
