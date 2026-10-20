"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { FileBarChart, FileText, Download } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { documentsApi } from "@/lib/api";

export default function ReportsPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try { const data = await documentsApi.list(1, 50); setDocuments((data.items || []).filter((d: any) => d.status === "completed")); } catch {} finally { setLoading(false); }
    }
    load();
  }, []);

  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-bold text-slate-900">Reports</h1><p className="text-slate-600 mt-1">View analysis reports for your documents</p></div>
      {loading ? <div className="space-y-3">{[1,2].map(i=><Skeleton key={i} className="h-20 w-full"/>)}</div> : documents.length === 0 ? (
        <Card><CardContent className="py-16 text-center"><FileBarChart className="h-12 w-12 mx-auto text-slate-300 mb-3" /><p className="text-slate-500 font-medium">No reports available</p><p className="text-sm text-slate-400 mt-1">Reports are generated after document analysis completes</p></CardContent></Card>
      ) : (
        <div className="space-y-3">{documents.map((doc: any) => (
          <Link key={doc.id} href={`/dashboard/documents/${doc.id}`}>
            <Card className="hover:shadow-md transition-shadow cursor-pointer"><CardContent className="py-4 flex items-center justify-between">
              <div className="flex items-center gap-3"><FileText className="h-5 w-5 text-slate-400"/><div><p className="font-medium text-slate-900">{doc.name}</p><p className="text-xs text-slate-500">{new Date(doc.created_at).toLocaleDateString()}</p></div></div>
              <Badge className="bg-teal-100 text-teal-700">View Report</Badge>
            </CardContent></Card>
          </Link>
        ))}</div>
      )}
    </div>
  );
}
