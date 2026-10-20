"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ArrowLeft, FileText, AlertTriangle, CheckCircle, Info, AlertCircle, HelpCircle } from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Progress } from "@/components/ui/progress";
import { Skeleton } from "@/components/ui/skeleton";
import { Separator } from "@/components/ui/separator";
import { documentsApi } from "@/lib/api";

const severityConfig: Record<string, { color: string; icon: any; label: string }> = {
  info: { color: "bg-blue-100 text-blue-700", icon: Info, label: "Info" },
  attention: { color: "bg-amber-100 text-amber-700", icon: AlertTriangle, label: "Attention" },
  concerning: { color: "bg-orange-100 text-orange-700", icon: AlertCircle, label: "Concerning" },
  high_risk: { color: "bg-red-100 text-red-700", icon: AlertTriangle, label: "High Risk" },
  suspicious: { color: "bg-red-200 text-red-800", icon: AlertTriangle, label: "Suspicious" },
  missing: { color: "bg-slate-100 text-slate-700", icon: HelpCircle, label: "Missing Info" },
};

export default function DocumentAnalysisPage() {
  const params = useParams();
  const documentId = params.id as string;
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(false);

  useEffect(() => {
    loadAnalysis();
  }, [documentId]);

  async function loadAnalysis() {
    try {
      const data = await documentsApi.getAnalysis(documentId);
      setAnalysis(data);
      // If still processing, poll
      const processingStatuses = ["uploaded", "queued", "extracting", "ocr_processing", "segmenting", "analyzing", "calculating"];
      if (processingStatuses.includes(data.document?.status)) {
        setPolling(true);
        setTimeout(() => loadAnalysis(), 3000);
      } else {
        setPolling(false);
      }
    } catch {
      toast("Failed to load analysis");
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <div className="space-y-4">{[1, 2, 3].map(i => <Skeleton key={i} className="h-32 w-full" />)}</div>;
  if (!analysis) return <div className="text-center py-12 text-slate-500">Document not found</div>;

  const doc = analysis.document;
  const risk = analysis.risk_assessment;

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Link href="/dashboard/documents"><Button variant="ghost" size="icon"><ArrowLeft className="h-4 w-4" /></Button></Link>
        <div className="flex-1">
          <h1 className="text-2xl font-bold text-slate-900">{doc.name}</h1>
          <p className="text-sm text-slate-500">{doc.file_type?.toUpperCase()} • {doc.page_count || 0} pages • {doc.language || "auto"}</p>
        </div>
        <Badge className={doc.status === "completed" ? "bg-green-100 text-green-700" : doc.status === "failed" ? "bg-red-100 text-red-700" : "bg-blue-100 text-blue-700 animate-pulse"}>
          {polling ? `${doc.status}...` : doc.status}
        </Badge>
      </div>

      {/* Risk Summary */}
      {risk && (
        <Card>
          <CardHeader><CardTitle className="text-lg">Risk Assessment</CardTitle><CardDescription>{risk.risk_summary}</CardDescription></CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: "Overall Risk", value: risk.overall_score, color: risk.overall_score > 50 ? "text-red-600" : risk.overall_score > 25 ? "text-amber-600" : "text-green-600" },
                { label: "Document Risk", value: risk.document_risk_score, color: "text-slate-700" },
                { label: "Financial Risk", value: risk.financial_risk_score, color: "text-slate-700" },
                { label: "Fairness", value: risk.fairness_score, color: "text-green-600" },
              ].map((item, i) => (
                <div key={i} className="text-center">
                  <p className="text-xs text-slate-500 mb-1">{item.label}</p>
                  <p className={`text-2xl font-bold ${item.color}`}>{item.value?.toFixed(0) ?? "—"}</p>
                  <Progress value={item.value || 0} className="mt-2 h-1.5" />
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tabs */}
      <Tabs defaultValue="findings" className="space-y-4">
        <TabsList>
          <TabsTrigger value="findings">Findings ({analysis.findings?.length || 0})</TabsTrigger>
          <TabsTrigger value="clauses">Clauses ({analysis.clauses?.length || 0})</TabsTrigger>
        </TabsList>

        <TabsContent value="findings" className="space-y-3">
          {analysis.findings?.length === 0 ? (
            <Card><CardContent className="py-8 text-center text-slate-500"><CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" /><p>No significant findings identified</p></CardContent></Card>
          ) : (
            analysis.findings?.map((finding: any, i: number) => {
              const config = severityConfig[finding.severity] || severityConfig.info;
              const Icon = config.icon;
              return (
                <Card key={i} className="border-l-4" style={{ borderLeftColor: finding.severity === "high_risk" ? "#dc2626" : finding.severity === "concerning" ? "#f97316" : finding.severity === "attention" ? "#f59e0b" : "#94a3b8" }}>
                  <CardContent className="py-4">
                    <div className="flex items-start gap-3">
                      <Icon className="h-5 w-5 mt-0.5 flex-shrink-0" style={{ color: finding.severity === "high_risk" ? "#dc2626" : finding.severity === "concerning" ? "#f97316" : "#f59e0b" }} />
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <Badge className={config.color}>{config.label}</Badge>
                          {finding.confidence && <span className="text-xs text-slate-400">{(finding.confidence * 100).toFixed(0)}% confidence</span>}
                        </div>
                        <p className="text-sm text-slate-900 font-medium">{finding.explanation}</p>
                        {finding.why_it_matters && <p className="text-sm text-slate-600 mt-1">{finding.why_it_matters}</p>}
                        {finding.recommended_action && (
                          <div className="mt-2 p-2 bg-slate-50 rounded text-xs text-slate-600"><strong>Suggested action:</strong> {finding.recommended_action}</div>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              );
            })
          )}
        </TabsContent>

        <TabsContent value="clauses" className="space-y-3">
          {analysis.clauses?.map((clause: any, i: number) => (
            <Card key={i}>
              <CardContent className="py-4">
                <div className="flex items-center gap-2 mb-2">
                  <Badge variant="outline" className="text-xs">{clause.clause_type || "other"}</Badge>
                  <span className="text-xs text-slate-400">Page {clause.page_number}</span>
                </div>
                {clause.clause_heading && <p className="text-sm font-medium text-slate-900 mb-1">{clause.clause_heading}</p>}
                <p className="text-sm text-slate-600 whitespace-pre-wrap">{clause.original_text?.substring(0, 300)}{clause.original_text?.length > 300 ? "..." : ""}</p>
                {clause.extracted_values && Object.keys(clause.extracted_values).length > 0 && (
                  <div className="mt-2 flex gap-2 flex-wrap">
                    {clause.extracted_values.percentages?.map((p: number, j: number) => <Badge key={j} variant="outline" className="text-xs">{p}%</Badge>)}
                    {clause.extracted_values.amounts?.map((a: number, j: number) => <Badge key={j} variant="outline" className="text-xs">${a.toLocaleString()}</Badge>)}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </TabsContent>
      </Tabs>

      <p className="text-xs text-slate-400 text-center">All findings are analytical indicators, not legal or financial advice. Consult a qualified professional before making decisions.</p>
    </div>
  );
}

function toast(msg: string) { console.log(msg); }
