"use client";

import { useEffect, useState } from "react";
import { Wallet, Save, DollarSign, Percent, PiggyBank, Users } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { financialApi } from "@/lib/api";
import { toast } from "sonner";

export default function FinancesPage() {
  const [profile, setProfile] = useState<any>({
    monthly_income: "", income_basis: "net", employment_type: "full_time",
    income_stability: "stable", essential_expenses: "", existing_debt_payments: "",
    savings: "", dependents: 0,
  });
  const [saving, setSaving] = useState(false);
  const [affordability, setAffordability] = useState<any>(null);
  const [proposedPayment, setProposedPayment] = useState("");

  useEffect(() => { loadProfile(); }, []);

  async function loadProfile() {
    try {
      const data = await financialApi.getProfile();
      if (data) setProfile({
        monthly_income: data.monthly_income || "", income_basis: data.income_basis || "net",
        employment_type: data.employment_type || "full_time", income_stability: data.income_stability || "stable",
        essential_expenses: data.essential_expenses || "", existing_debt_payments: data.existing_debt_payments || "",
        savings: data.savings || "", dependents: data.dependents || 0,
      });
    } catch { }
  }

  async function handleSave() {
    setSaving(true);
    try {
      const payload: any = {};
      if (profile.monthly_income !== "") payload.monthly_income = parseFloat(profile.monthly_income);
      if (profile.essential_expenses !== "") payload.essential_expenses = parseFloat(profile.essential_expenses);
      if (profile.existing_debt_payments !== "") payload.existing_debt_payments = parseFloat(profile.existing_debt_payments);
      if (profile.savings !== "") payload.savings = parseFloat(profile.savings);
      payload.income_basis = profile.income_basis;
      payload.employment_type = profile.employment_type;
      payload.income_stability = profile.income_stability;
      payload.dependents = parseInt(profile.dependents) || 0;
      await financialApi.updateProfile(payload);
      toast.success("Profile saved!");
      if (proposedPayment) loadAffordability();
    } catch (err: any) { toast.error(err.message || "Failed to save"); }
    finally { setSaving(false); }
  }

  async function loadAffordability() {
    if (!proposedPayment) return;
    try {
      const data = await financialApi.getAffordability(parseFloat(proposedPayment));
      setAffordability(data);
    } catch { }
  }

  const income = parseFloat(profile.monthly_income) || 0;
  const expenses = parseFloat(profile.essential_expenses) || 0;
  const debt = parseFloat(profile.existing_debt_payments) || 0;
  const savings = parseFloat(profile.savings) || 0;
  const cashflow = income - expenses - debt;
  const dti = income > 0 ? ((debt / income) * 100).toFixed(1) : "—";
  const emergencyMonths = expenses > 0 ? (savings / expenses).toFixed(1) : "—";

  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-bold text-slate-900">My Finances</h1><p className="text-slate-600 mt-1">Your financial profile for affordability analysis</p></div>

      <div className="grid lg:grid-cols-3 gap-6">
        {/* Form */}
        <div className="lg:col-span-2 space-y-6">
          <Card>
            <CardHeader><CardTitle>Income</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2"><Label>Monthly Income</Label><Input type="number" placeholder="5000" value={profile.monthly_income} onChange={(e) => setProfile({...profile, monthly_income: e.target.value})} /></div>
                <div className="space-y-2"><Label>Income Basis</Label>
                  <Select value={profile.income_basis} onValueChange={(v) => setProfile({...profile, income_basis: v})}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>
                    <SelectItem value="net">Net (After Tax)</SelectItem><SelectItem value="gross">Gross (Before Tax)</SelectItem>
                  </SelectContent></Select></div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2"><Label>Employment Type</Label>
                  <Select value={profile.employment_type} onValueChange={(v) => setProfile({...profile, employment_type: v})}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>
                    <SelectItem value="full_time">Full-time</SelectItem><SelectItem value="part_time">Part-time</SelectItem><SelectItem value="contract">Contract</SelectItem><SelectItem value="self_employed">Self-employed</SelectItem>
                  </SelectContent></Select></div>
                <div className="space-y-2"><Label>Income Stability</Label>
                  <Select value={profile.income_stability} onValueChange={(v) => setProfile({...profile, income_stability: v})}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>
                    <SelectItem value="stable">Stable</SelectItem><SelectItem value="variable">Variable</SelectItem><SelectItem value="seasonal">Seasonal</SelectItem>
                  </SelectContent></Select></div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Expenses & Obligations</CardTitle></CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2"><Label>Essential Monthly Expenses</Label><Input type="number" placeholder="2000" value={profile.essential_expenses} onChange={(e) => setProfile({...profile, essential_expenses: e.target.value})} /></div>
                <div className="space-y-2"><Label>Existing Debt Payments</Label><Input type="number" placeholder="350" value={profile.existing_debt_payments} onChange={(e) => setProfile({...profile, existing_debt_payments: e.target.value})} /></div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2"><Label>Total Savings</Label><Input type="number" placeholder="15000" value={profile.savings} onChange={(e) => setProfile({...profile, savings: e.target.value})} /></div>
                <div className="space-y-2"><Label>Dependents</Label><Input type="number" placeholder="0" value={profile.dependents} onChange={(e) => setProfile({...profile, dependents: e.target.value})} /></div>
              </div>
            </CardContent>
          </Card>

          <Button onClick={handleSave} disabled={saving} className="bg-teal-600 hover:bg-teal-700"><Save className="h-4 w-4 mr-2" /> {saving ? "Saving..." : "Save Profile"}</Button>
        </div>

        {/* Indicators */}
        <div className="space-y-4">
          <Card>
            <CardHeader><CardTitle className="text-base">Financial Indicators</CardTitle><CardDescription>Based on your profile data</CardDescription></CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between"><span className="text-sm text-slate-600">Monthly Cash Flow</span>
                <span className={`font-bold ${cashflow >= 0 ? "text-green-600" : "text-red-600"}`}>${cashflow.toLocaleString()}</span></div>
              <Separator />
              <div className="flex items-center justify-between"><span className="text-sm text-slate-600">DTI Ratio</span>
                <span className="font-bold text-slate-900">{dti}%</span></div>
              <Separator />
              <div className="flex items-center justify-between"><span className="text-sm text-slate-600">Emergency Fund</span>
                <span className="font-bold text-slate-900">{emergencyMonths} months</span></div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle className="text-base">Test Affordability</CardTitle></CardHeader>
            <CardContent className="space-y-3">
              <div className="space-y-2"><Label>Proposed Monthly Payment</Label>
                <Input type="number" placeholder="500" value={proposedPayment} onChange={(e) => setProposedPayment(e.target.value)} /></div>
              <Button variant="outline" className="w-full" onClick={loadAffordability}>Check Affordability</Button>
              {affordability && (
                <div className="space-y-2 mt-3">
                  <p className="text-sm text-slate-700">{affordability.assessment}</p>
                  {affordability.warnings?.map((w: string, i: number) => (
                    <p key={i} className="text-xs text-amber-700 bg-amber-50 p-2 rounded">{w}</p>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          <p className="text-xs text-slate-400">These are analytical indicators, not financial advice. Thresholds shown are commonly referenced ranges, not universal rules.</p>
        </div>
      </div>
    </div>
  );
}
