"use client";

import { useEffect, useState } from "react";
import { TrendingDown, Play, BarChart3 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { financialApi } from "@/lib/api";
import { toast } from "sonner";

const scenarios = [
  { value: "income_reduction", label: "Income Reduction", desc: "What if your income drops?" },
  { value: "unexpected_expense", label: "Unexpected Expense", desc: "What if you face a large unplanned cost?" },
  { value: "expense_increase", label: "Expense Increase", desc: "What if your essential costs rise?" },
  { value: "late_payment", label: "Late Payment", desc: "What if you miss a payment deadline?" },
];

export default function StressTestPage() {
  const [scenario, setScenario] = useState("income_reduction");
  const [params, setParams] = useState<Record<string, string>>({ reduction_pct: "20", proposed_payment: "500" });
  const [result, setResult] = useState<any>(null);
  const [running, setRunning] = useState(false);
  const [history, setHistory] = useState<any[]>([]);

  useEffect(() => { loadHistory(); }, []);

  async function loadHistory() {
    try { const data = await financialApi.listStressTests(); setHistory(data || []); } catch { }
  }

  function updateParam(key: string, value: string) { setParams(prev => ({ ...prev, [key]: value })); }

  async function runTest() {
    setRunning(true);
    try {
      const numParams: Record<string, number> = {};
      Object.entries(params).forEach(([k, v]) => { if (v) numParams[k] = parseFloat(v); });
      const data = await financialApi.createStressTest({ scenario_type: scenario, parameters: numParams });
      setResult(data);
      toast.success("Stress test completed!");
      loadHistory();
    } catch (err: any) { toast.error(err.message || "Please set up your financial profile first"); }
    finally { setRunning(false); }
  }

  const renderParams = () => {
    switch (scenario) {
      case "income_reduction": return (
        <div className="space-y-2"><Label>Income Reduction (%)</Label><Input type="number" value={params.reduction_pct || "20"} onChange={(e) => updateParam("reduction_pct", e.target.value)} /><p className="text-xs text-slate-400">Common scenarios: 10%, 20%, 40%</p></div>
      );
      case "unexpected_expense": return (
        <div className="space-y-2"><Label>Expense Amount ($)</Label><Input type="number" value={params.expense_amount || "1000"} onChange={(e) => updateParam("expense_amount", e.target.value)} /></div>
      );
      case "expense_increase": return (
        <div className="space-y-2"><Label>Expense Increase (%)</Label><Input type="number" value={params.increase_pct || "15"} onChange={(e) => updateParam("increase_pct", e.target.value)} /></div>
      );
      case "late_payment": return (
        <div className="space-y-2"><Label>Late Fee Amount ($)</Label><Input type="number" value={params.late_fee || "50"} onChange={(e) => updateParam("late_fee", e.target.value)} /></div>
      );
    }
  };

  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-bold text-slate-900">Stress Test</h1><p className="text-slate-600 mt-1">Explore how financial changes could affect your budget</p></div>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Config */}
        <Card>
          <CardHeader><CardTitle>Configure Scenario</CardTitle><CardDescription>Select a scenario and adjust parameters</CardDescription></CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2"><Label>Scenario Type</Label>
              <Select value={scenario} onValueChange={(v) => { setScenario(v); setResult(null); }}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>
                {scenarios.map(s => <SelectItem key={s.value} value={s.value}>{s.label}</SelectItem>)}
              </SelectContent></Select>
              <p className="text-xs text-slate-500">{scenarios.find(s => s.value === scenario)?.desc}</p>
            </div>
            <Separator />
            {renderParams()}
            <div className="space-y-2"><Label>Proposed Monthly Payment ($)</Label><Input type="number" value={params.proposed_payment || "0"} onChange={(e) => updateParam("proposed_payment", e.target.value)} /><p className="text-xs text-slate-400">Monthly payment for the loan you&apos;re considering</p></div>
            <Button onClick={runTest} disabled={running} className="w-full bg-teal-600 hover:bg-teal-700"><Play className="h-4 w-4 mr-2" /> {running ? "Running..." : "Run Stress Test"}</Button>
          </CardContent>
        </Card>

        {/* Results */}
        <div className="space-y-4">
          {result ? (
            <Card>
              <CardHeader><CardTitle>Results</CardTitle></CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="p-4 bg-green-50 rounded-lg text-center">
                    <p className="text-xs text-green-600 mb-1">Baseline Cash Flow</p>
                    <p className="text-2xl font-bold text-green-700">${result.baseline_cashflow?.toLocaleString()}</p>
                  </div>
                  <div className={`p-4 rounded-lg text-center ${result.stressed_cashflow < 0 ? "bg-red-50" : "bg-amber-50"}`}>
                    <p className={`text-xs mb-1 ${result.stressed_cashflow < 0 ? "text-red-600" : "text-amber-600"}`}>Stressed Cash Flow</p>
                    <p className={`text-2xl font-bold ${result.stressed_cashflow < 0 ? "text-red-700" : "text-amber-700"}`}>${result.stressed_cashflow?.toLocaleString()}</p>
                  </div>
                </div>
                <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <span className="text-sm text-slate-600">Impact</span>
                  <span className="font-bold text-red-600">-${result.impact_amount?.toLocaleString()} ({result.impact_percentage?.toFixed(1)}%)</span>
                </div>
                {result.suggestions?.length > 0 && (
                  <div className="space-y-2">{result.suggestions.map((s: string, i: number) => <p key={i} className="text-sm text-slate-600 bg-slate-50 p-3 rounded-lg">{s}</p>)}</div>
                )}
                {result.assumptions && (
                  <div className="p-3 bg-amber-50 rounded-lg"><p className="text-xs text-amber-700 font-medium">Assumptions</p><p className="text-xs text-amber-600 mt-1">{result.assumptions.scenario}</p><p className="text-xs text-amber-500 mt-1">{result.assumptions.note}</p></div>
                )}
              </CardContent>
            </Card>
          ) : (
            <Card><CardContent className="py-16 text-center"><TrendingDown className="h-12 w-12 mx-auto text-slate-300 mb-3" /><p className="text-slate-500 font-medium">Run a scenario to see results</p><p className="text-sm text-slate-400 mt-1">Adjust parameters and click &quot;Run Stress Test&quot;</p></CardContent></Card>
          )}

          {history.length > 0 && (
            <Card>
              <CardHeader><CardTitle className="text-base">Recent Tests</CardTitle></CardHeader>
              <CardContent className="space-y-2">
                {history.slice(0, 5).map((test: any, i: number) => (
                  <div key={i} className="flex items-center justify-between p-2 border border-slate-100 rounded">
                    <div>
                      <Badge variant="outline" className="text-xs">{test.scenario_type?.replace("_", " ")}</Badge>
                      <span className="text-xs text-slate-400 ml-2">{new Date(test.created_at).toLocaleDateString()}</span>
                    </div>
                    <span className={`text-sm font-medium ${test.stressed_cashflow < 0 ? "text-red-600" : "text-green-600"}`}>${test.stressed_cashflow?.toLocaleString()}</span>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>
      </div>

      <p className="text-xs text-slate-400 text-center">Stress test results are hypothetical scenarios, not predictions. They are designed to help you think through financial risks.</p>
    </div>
  );
}
