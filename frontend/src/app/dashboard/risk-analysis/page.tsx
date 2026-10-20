"use client";
import { useEffect, useState } from "react";
import { AlertTriangle, FileText, Shield } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { documentsApi } from "@/lib/api";
import Link from "next/link";

export default function RiskAnalysisPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => { loadDocs(); }, []);

  async function loadDocs() {
    try {
      const data = await documentsApi.list(1, 50);
      const completed = (data.items || []).filter((d: any) => d.status === "completed");
      setDocuments(completed);
    } catch { } finally { setLoading(false); }
  }

  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-bold text-slate-900">Risk Analysis</h1><p className="text-slate-600 mt-1">Overview of risks across your analyzed documents</p></div>
      {loading ? <div className="space-y-3">{[1,2,3].map(i=><Skeleton key={i} className="h-24 w-full"/>)}</div> : documents.length === 0 ? (
        <Card><CardContent className="py-16 text-center"><AlertTriangle className="h-12 w-12 mx-auto text-slate-300 mb-3" /><p className="text-slate-500 font-medium">No analyzed documents yet</p><p className="text-sm text-slate-400 mt-1">Upload and analyze a document to see risk insights</p></CardContent></Card>
      ) : (
        <div className="space-y-4">{documents.map((doc: any) => (
          <Link key={doc.id} href={`/dashboard/documents/${doc.id}`}>
            <Card className="hover:shadow-md transition-shadow cursor-pointer">
              <CardContent className="py-4 flex items-center justify-between">
                <div className="flex items-center gap-3"><FileText className="h-5 w-5 text-slate-400"/><div><p className="font-medium text-slate-900">{doc.name}</p><p className="text-xs text-slate-500">{doc.page_count} pages • {doc.language}</p></div></div>
                <Badge className="bg-green-100 text-green-700">Analyzed</Badge>
              </CardContent>
            </Card>
          </Link>
        ))}</div>
      )}
    </div>
  );
}
