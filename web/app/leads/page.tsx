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
    <div className="p-6 h-full flex flex-col">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold tracking-tight text-ink">Leads Management</h1>
          <p className="text-[13px] text-muted mt-1">Manage leads you've saved from the Radar.</p>
        </div>
        <div className="relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted" />
          <input type="text" placeholder="Search leads..." className="pl-9 pr-4 py-2 w-64 bg-surface-2 border border-line rounded-lg text-[13px] outline-none focus:border-accent focus:bg-surface transition-colors" />
        </div>
      </div>

      <div className="bg-surface border border-line rounded-lg shadow-sm overflow-hidden flex-1 flex flex-col">
        <table className="w-full text-left text-[13.5px]">
          <thead className="bg-surface-2 text-muted text-[12px] font-medium border-b border-line">
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
                <tr key={lead.id} className="hover:bg-surface-2 transition-colors group">
                  <td className="px-6 py-4 align-top">
                    <div className="flex items-center gap-2 font-medium text-ink">
                      <User className="h-4 w-4 text-muted" />
                      u/{lead.author}
                    </div>
                    <div className="flex items-center gap-1.5 mt-1.5 text-[12.5px] text-muted">
                      <Calendar className="h-3.5 w-3.5" />
                      {new Date(lead.saved_at * 1000).toLocaleDateString("en-US")}
                    </div>
                  </td>
                  <td className="px-6 py-4 align-top">
                    <div className="text-ink mb-2 line-clamp-2 leading-relaxed">{lead.problem}</div>
                    <span className="inline-flex items-center rounded bg-surface-2 border border-line px-2 py-0.5 text-[11px] font-medium text-muted uppercase tracking-wider">
                      {lead.stage}
                    </span>
                  </td>
                  <td className="px-6 py-4 align-top">
                    <select
                      value={lead.status}
                      onChange={(e) => handleStatusChange(lead.id, e.target.value)}
                      className={`text-[12px] font-medium rounded-full px-3 py-1 border focus:outline-none transition-colors ${
                        lead.status === "New" ? "bg-surface-2 border-line text-ink" :
                        lead.status === "Contacted" ? "bg-accent-soft border-accent/20 text-accent" :
                        "bg-cool-soft border-cool/20 text-cool"
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
                    <div className="flex justify-end gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                      <a href={`https://www.reddit.com/message/compose/?to=${lead.author}`} target="_blank" rel="noopener noreferrer" className="p-1.5 text-muted hover:text-accent hover:bg-accent-soft rounded-full transition-colors" title="Send message">
                        <MessageSquare className="h-4 w-4" />
                      </a>
                      <a href={lead.url} target="_blank" rel="noopener noreferrer" className="p-1.5 text-muted hover:text-ink hover:bg-surface-2 rounded-full transition-colors" title="View post">
                        <ExternalLink className="h-4 w-4" />
                      </a>
                      <button onClick={() => handleDelete(lead.id)} className="p-1.5 text-muted hover:text-hot hover:bg-hot-soft rounded-full transition-colors" title="Delete">
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
