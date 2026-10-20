"use client";
import { useState } from "react";
import { Settings, User, Globe, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { useAuth } from "@/lib/auth";

export default function SettingsPage() {
  const { user } = useAuth();
  const [language, setLanguage] = useState("en");

  return (
    <div className="space-y-6 max-w-2xl">
      <div><h1 className="text-2xl font-bold text-slate-900">Settings</h1><p className="text-slate-600 mt-1">Manage your account and preferences</p></div>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><User className="h-5 w-5"/>Profile</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2"><Label>Full Name</Label><Input value={user?.full_name || ""} disabled className="bg-slate-50" /></div>
          <div className="space-y-2"><Label>Email</Label><Input value={user?.email || ""} disabled className="bg-slate-50" /></div>
          <p className="text-xs text-slate-400">Contact support to update your profile information.</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader><CardTitle className="flex items-center gap-2"><Globe className="h-5 w-5"/>Language</CardTitle></CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2"><Label>Interface Language</Label>
            <Select value={language} onValueChange={setLanguage}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>
              <SelectItem value="en">English</SelectItem><SelectItem value="km">ខ្មែរ (Khmer) — Coming Soon</SelectItem>
            </SelectContent></Select></div>
        </CardContent>
      </Card>

      <Card className="border-red-200">
        <CardHeader><CardTitle className="text-red-600 flex items-center gap-2"><Trash2 className="h-5 w-5"/>Danger Zone</CardTitle><CardDescription>Irreversible actions</CardDescription></CardHeader>
        <CardContent><Button variant="outline" className="text-red-600 border-red-200 hover:bg-red-50">Delete Account & All Data</Button><p className="text-xs text-slate-400 mt-2">This will permanently delete your account, all documents, and analysis data.</p></CardContent>
      </Card>
    </div>
  );
}
