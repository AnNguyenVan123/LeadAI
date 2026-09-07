"use client";
import { useEffect, useState } from "react";
import { getSavedLeads, updateLead, deleteLead, type SavedLead } from "@/lib/api";
import { MessageSquare, ExternalLink, Trash2, Calendar, User, Search, Loader2 } from "lucide-react";

export default function LeadsPage() {
  const [leads, setLeads] = useState<SavedLead[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSavedLeads().then((data) => {
      setLeads(data);
      setLoading(false);
    });
  }, []);

  const handleStatusChange = async (id: string, newStatus: string) => {
    setLeads((prev) => prev.map((l) => (l.id === id ? { ...l, status: newStatus } : l)));
    await updateLead(id, { status: newStatus });
  };

  const handleNotesChange = async (id: string, notes: string) => {
    setLeads((prev) => prev.map((l) => (l.id === id ? { ...l, notes } : l)));
    await updateLead(id, { notes });
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Remove this lead from your CRM?")) return;
    setLeads((prev) => prev.filter((l) => l.id !== id));
    await deleteLead(id);
  };

  if (loading) {
    return <div className="flex h-full items-center justify-center text-muted"><Loader2 className="animate-spin h-6 w-6" /></div>;
  }

  return (
    <div className="p-10 max-w-[1200px] mx-auto">
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-cond font-bold tracking-tight text-main">Leads</h1>
          <p className="text-[14px] text-muted mt-1">Manage leads you've saved from the Radar.</p>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted" />
          <input type="text" placeholder="Search leads..." className="pl-9 pr-4 py-2 bg-surface border border-line rounded-md text-[14px] focus:outline-none focus:border-hot" />
        </div>
      </div>

      <div className="bg-surface/50 border border-line rounded-lg overflow-hidden">
        <table className="w-full text-left text-[14px]">
          <thead className="bg-surface text-muted text-[13px] uppercase tracking-wider">
            <tr>
              <th className="px-6 py-4 font-medium">Lead</th>
              <th className="px-6 py-4 font-medium w-[40%]">Problem & Context</th>
              <th className="px-6 py-4 font-medium">Status</th>
              <th className="px-6 py-4 font-medium">Notes</th>
              <th className="px-6 py-4 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-line">
            {leads.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-6 py-12 text-center text-muted">
                  No leads saved yet. Go to Radar to find and save leads.
                </td>
              </tr>
            ) : (
              leads.map((lead) => (
                <tr key={lead.id} className="hover:bg-surface/80 transition-colors group">
                  <td className="px-6 py-4 align-top">
                    <div className="flex items-center gap-2 font-medium text-main">
                      <User className="h-4 w-4 text-muted" />
                      u/{lead.author}
                    </div>
                    <div className="flex items-center gap-1.5 mt-1.5 text-[12.5px] text-muted">
                      <Calendar className="h-3.5 w-3.5" />
                      {new Date(lead.saved_at * 1000).toLocaleDateString("en-US")}
                    </div>
                  </td>
                  <td className="px-6 py-4 align-top">
                    <div className="text-main mb-1 line-clamp-2">{lead.problem}</div>
                    <span className="inline-flex items-center rounded-full bg-surface px-2 py-0.5 text-[12px] font-medium text-muted">
                      {lead.stage}
                    </span>
                  </td>
                  <td className="px-6 py-4 align-top">
                    <select
                      value={lead.status}
                      onChange={(e) => handleStatusChange(lead.id, e.target.value)}
                      className={`text-[13px] rounded px-2 py-1 border focus:outline-none ${
                        lead.status === "New" ? "bg-surface border-line text-main" :
                        lead.status === "Contacted" ? "bg-hot/10 border-hot/20 text-hot" :
                        "bg-green-500/10 border-green-500/20 text-green-600"
                      }`}
                    >
                      <option value="New">New</option>
                      <option value="Contacted">Contacted</option>
                      <option value="Replied">Replied</option>
                    </select>
                  </td>
                  <td className="px-6 py-4 align-top">
                    <input
                      type="text"
                      value={lead.notes}
                      onChange={(e) => handleNotesChange(lead.id, e.target.value)}
                      placeholder="Email, phone..."
                      className="bg-transparent border-b border-transparent hover:border-line focus:border-hot focus:outline-none w-full text-[13.5px] py-1 transition-colors"
                    />
                  </td>
                  <td className="px-6 py-4 align-top text-right">
                    <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      <a href={`https://www.reddit.com/message/compose/?to=${lead.author}`} target="_blank" rel="noopener noreferrer" className="p-1.5 text-muted hover:text-main hover:bg-surface rounded" title="Send message">
                        <MessageSquare className="h-4 w-4" />
                      </a>
                      <a href={lead.url} target="_blank" rel="noopener noreferrer" className="p-1.5 text-muted hover:text-main hover:bg-surface rounded" title="View post">
                        <ExternalLink className="h-4 w-4" />
                      </a>
                      <button onClick={() => handleDelete(lead.id)} className="p-1.5 text-muted hover:text-red-500 hover:bg-red-500/10 rounded" title="Delete">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
