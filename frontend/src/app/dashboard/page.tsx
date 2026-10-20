"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { FileText, AlertTriangle, Upload, TrendingDown, ArrowRight, Clock } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Skeleton } from "@/components/ui/skeleton";
import { documentsApi } from "@/lib/api";

const statusColors: Record<string, string> = {
  uploaded: "bg-slate-100 text-slate-700",
  queued: "bg-blue-100 text-blue-700",
  extracting: "bg-blue-100 text-blue-700",
  analyzing: "bg-blue-100 text-blue-700",
  completed: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

export default function DashboardPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({ total: 0, attention: 0 });

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const data = await documentsApi.list(1, 5);
      setDocuments(data.items || []);
      const total = data.total || 0;
      const attention = (data.items || []).filter((d: any) => d.status === "failed").length;
      setStats({ total, attention });
    } catch {
      // API may not be running yet
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-slate-600 mt-1">Overview of your financial document analysis</p>
        </div>
        <Link href="/dashboard/documents">
          <Button className="bg-teal-600 hover:bg-teal-700">
            <Upload className="h-4 w-4 mr-2" /> Upload Document
          </Button>
        </Link>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Documents Analyzed</p>
                <p className="text-3xl font-bold text-slate-900 mt-1">{loading ? <Skeleton className="h-9 w-12" /> : stats.total}</p>
              </div>
              <div className="h-12 w-12 rounded-xl bg-teal-50 flex items-center justify-center">
                <FileText className="h-6 w-6 text-teal-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Needing Attention</p>
                <p className="text-3xl font-bold text-slate-900 mt-1">{loading ? <Skeleton className="h-9 w-12" /> : stats.attention}</p>
              </div>
              <div className="h-12 w-12 rounded-xl bg-amber-50 flex items-center justify-center">
                <AlertTriangle className="h-6 w-6 text-amber-600" />
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-slate-600">Quick Actions</p>
                <div className="mt-2 flex gap-2">
                  <Link href="/dashboard/finances"><Button size="sm" variant="outline">My Finances</Button></Link>
                  <Link href="/dashboard/stress-test"><Button size="sm" variant="outline">Stress Test</Button></Link>
                </div>
              </div>
              <div className="h-12 w-12 rounded-xl bg-blue-50 flex items-center justify-center">
                <TrendingDown className="h-6 w-6 text-blue-600" />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Documents */}
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div>
            <CardTitle className="text-lg">Recent Documents</CardTitle>
            <CardDescription>Your latest document analyses</CardDescription>
          </div>
          <Link href="/dashboard/documents">
            <Button variant="ghost" size="sm">View All <ArrowRight className="h-4 w-4 ml-1" /></Button>
          </Link>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="space-y-3">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-16 w-full" />)}</div>
          ) : documents.length === 0 ? (
            <div className="text-center py-12 text-slate-500">
              <FileText className="h-12 w-12 mx-auto mb-3 text-slate-300" />
              <p className="font-medium">No documents yet</p>
              <p className="text-sm mt-1">Upload a financial document to get started</p>
              <Link href="/dashboard/documents">
                <Button className="mt-4 bg-teal-600 hover:bg-teal-700" size="sm">
                  <Upload className="h-4 w-4 mr-2" /> Upload Document
                </Button>
              </Link>
            </div>
          ) : (
            <div className="space-y-3">
              {documents.map((doc: any) => (
                <Link key={doc.id} href={`/dashboard/documents/${doc.id}`}
                  className="flex items-center justify-between p-4 rounded-lg border border-slate-100 hover:bg-slate-50 transition-colors cursor-pointer">
                  <div className="flex items-center gap-3">
                    <FileText className="h-5 w-5 text-slate-400" />
                    <div>
                      <p className="font-medium text-slate-900 text-sm">{doc.name}</p>
                      <div className="flex items-center gap-2 mt-0.5">
                        <span className="text-xs text-slate-500">{doc.file_type?.toUpperCase()}</span>
                        <span className="text-xs text-slate-400">•</span>
                        <span className="text-xs text-slate-500 flex items-center gap-1">
                          <Clock className="h-3 w-3" />
                          {new Date(doc.created_at).toLocaleDateString()}
                        </span>
                      </div>
                    </div>
                  </div>
                  <Badge className={statusColors[doc.status] || "bg-slate-100 text-slate-700"}>
                    {doc.status}
                  </Badge>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Disclaimer */}
      <p className="text-xs text-slate-400 text-center">
        FinGuard is an analytical tool, not a financial or legal advisor. All findings are indicators, not definitive judgments.
      </p>
    </div>
  );
}
