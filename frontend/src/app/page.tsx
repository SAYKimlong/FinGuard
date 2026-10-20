"use client";

import Link from "next/link";
import {
  Shield, FileSearch, Calculator, TrendingDown, Globe2, Lock,
  ArrowRight, CheckCircle2, Upload, Brain, BarChart3, ChevronRight,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="border-b border-slate-100 bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <Shield className="h-8 w-8 text-teal-600" />
              <span className="text-xl font-bold text-slate-900">FinGuard</span>
            </div>
            <div className="hidden md:flex items-center gap-8">
              <a href="#features" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">Features</a>
              <a href="#how-it-works" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">How It Works</a>
              <a href="#security" className="text-sm text-slate-600 hover:text-slate-900 transition-colors">Security</a>
            </div>
            <div className="flex items-center gap-3">
              <Link href="/login">
                <Button variant="ghost" size="sm">Log in</Button>
              </Link>
              <Link href="/register">
                <Button size="sm" className="bg-teal-600 hover:bg-teal-700">Get Started</Button>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-slate-50 via-white to-teal-50/30" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 lg:py-32">
          <div className="max-w-3xl">
            <Badge variant="outline" className="mb-4 text-teal-700 border-teal-200 bg-teal-50">
              AI Personal Finance Assistant
            </Badge>
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-slate-900 tracking-tight leading-tight">
              Understand the risk{" "}
              <span className="text-teal-600">before you sign.</span>
            </h1>
            <p className="mt-6 text-lg text-slate-600 leading-relaxed max-w-2xl">
              Upload your financial agreements and let AI identify concerning clauses, 
              calculate true borrowing costs, and stress-test your finances — 
              all before you commit.
            </p>
            <div className="mt-8 flex flex-col sm:flex-row gap-3">
              <Link href="/register">
                <Button size="lg" className="bg-teal-600 hover:bg-teal-700 text-base px-8">
                  Get Started Free <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/login">
                <Button size="lg" variant="outline" className="text-base px-8">
                  View Demo
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Problem */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl font-bold text-slate-900">Financial agreements are complicated</h2>
            <p className="mt-4 text-slate-600">Most people sign financial documents they don&apos;t fully understand.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { title: "Hidden Costs", desc: "Multiple fees, compounding penalties, and insurance requirements buried in fine print." },
              { title: "Unclear Terms", desc: "Vague language like 'at our discretion' that gives lenders flexibility to change terms." },
              { title: "Language Barriers", desc: "Financial documents in unfamiliar languages with specialized terminology." },
            ].map((item, i) => (
              <Card key={i} className="border-slate-200 bg-white">
                <CardContent className="pt-6">
                  <h3 className="font-semibold text-slate-900 text-lg">{item.title}</h3>
                  <p className="mt-2 text-slate-600 text-sm">{item.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl font-bold text-slate-900">How FinGuard Works</h2>
            <p className="mt-4 text-slate-600">Three steps to understanding your financial agreements.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: Upload, step: "1", title: "Upload Document", desc: "Upload your loan agreement, contract, or financial document in PDF, DOCX, or image format." },
              { icon: Brain, step: "2", title: "AI Analysis", desc: "Our AI extracts clauses, identifies risks, and calculates true costs using verified financial formulas." },
              { icon: BarChart3, step: "3", title: "Clear Insights", desc: "Get plain-language explanations, risk assessments, and stress-test your finances interactively." },
            ].map((item, i) => (
              <div key={i} className="text-center">
                <div className="w-16 h-16 rounded-2xl bg-teal-50 flex items-center justify-center mx-auto mb-4">
                  <item.icon className="h-8 w-8 text-teal-600" />
                </div>
                <div className="text-sm font-medium text-teal-600 mb-2">Step {item.step}</div>
                <h3 className="text-xl font-semibold text-slate-900 mb-2">{item.title}</h3>
                <p className="text-slate-600 text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl font-bold text-slate-900">Everything you need</h2>
            <p className="mt-4 text-slate-600">Comprehensive financial document analysis and personal finance tools.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { icon: FileSearch, title: "Document Intelligence", desc: "Extract and understand clauses from PDFs, DOCX, and scanned documents with AI-powered analysis." },
              { icon: Shield, title: "Risk Detection", desc: "Identify potentially unfair clauses, hidden fees, and concerning terms automatically." },
              { icon: Calculator, title: "Financial Calculator", desc: "Calculate true borrowing costs, monthly payments, and total repayment with deterministic formulas." },
              { icon: TrendingDown, title: "Stress Testing", desc: "Simulate income changes, unexpected expenses, and rate increases to test affordability." },
              { icon: Globe2, title: "Multilingual Support", desc: "Analyze documents in English and Khmer, with ASEAN language expansion planned." },
              { icon: Lock, title: "Privacy First", desc: "Your documents are encrypted, isolated, and never shared. You control your data." },
            ].map((item, i) => (
              <Card key={i} className="border-slate-200 bg-white hover:shadow-md transition-shadow">
                <CardContent className="pt-6">
                  <div className="w-10 h-10 rounded-lg bg-teal-50 flex items-center justify-center mb-4">
                    <item.icon className="h-5 w-5 text-teal-600" />
                  </div>
                  <h3 className="font-semibold text-slate-900">{item.title}</h3>
                  <p className="mt-2 text-slate-600 text-sm">{item.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Language Support */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl font-bold text-slate-900">Multilingual by Design</h2>
            <p className="mt-4 text-slate-600">Built to serve ASEAN consumers across languages.</p>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto">
            {[
              { lang: "English", status: "Production", color: "bg-green-100 text-green-700" },
              { lang: "ខ្មែរ (Khmer)", status: "Beta", color: "bg-amber-100 text-amber-700" },
              { lang: "ไทย (Thai)", status: "Planned", color: "bg-slate-100 text-slate-600" },
              { lang: "Tiếng Việt", status: "Planned", color: "bg-slate-100 text-slate-600" },
            ].map((item, i) => (
              <div key={i} className="text-center p-4 rounded-xl border border-slate-200 bg-white">
                <div className="font-medium text-slate-900">{item.lang}</div>
                <span className={`inline-block mt-2 text-xs font-medium px-2 py-0.5 rounded-full ${item.color}`}>
                  {item.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Security */}
      <section id="security" className="py-20 bg-slate-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-12">
            <h2 className="text-3xl font-bold">Security & Privacy</h2>
            <p className="mt-4 text-slate-400">Your financial data deserves the highest protection.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: Lock, title: "Data Isolation", desc: "Every user's documents and data are completely isolated. No cross-user access." },
              { icon: Shield, title: "Encrypted Storage", desc: "Documents stored securely with access controls. No plaintext passwords." },
              { icon: CheckCircle2, title: "No Data Selling", desc: "Your financial documents are never used for training or sold to third parties." },
            ].map((item, i) => (
              <div key={i} className="text-center">
                <item.icon className="h-8 w-8 text-teal-400 mx-auto mb-4" />
                <h3 className="font-semibold text-white mb-2">{item.title}</h3>
                <p className="text-slate-400 text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20">
        <div className="max-w-3xl mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-slate-900">Ready to understand your financial agreements?</h2>
          <p className="mt-4 text-slate-600">Start analyzing documents in minutes. No credit card required.</p>
          <Link href="/register">
            <Button size="lg" className="mt-8 bg-teal-600 hover:bg-teal-700 text-base px-8">
              Get Started <ChevronRight className="ml-1 h-4 w-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 py-12 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div className="flex items-center gap-2">
              <Shield className="h-5 w-5 text-teal-600" />
              <span className="font-semibold text-slate-900">FinGuard</span>
            </div>
            <p className="text-xs text-slate-500 text-center max-w-lg">
              FinGuard is a consumer information tool, not a financial or legal advisor. 
              Findings are analytical indicators, not legal judgments. 
              Always consult qualified professionals for financial and legal decisions.
            </p>
            <p className="text-xs text-slate-400">© 2026 FinGuard</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
