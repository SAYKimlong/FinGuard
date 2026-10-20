"use client";

import { useEffect, useState, useCallback } from "react";
import Link from "next/link";
import { FileText, Upload, Clock, Trash2, Eye, Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Skeleton } from "@/components/ui/skeleton";
import { documentsApi } from "@/lib/api";
import { toast } from "sonner";
import { useDropzone } from "react-dropzone";

const statusColors: Record<string, string> = {
  uploaded: "bg-slate-100 text-slate-700",
  queued: "bg-blue-100 text-blue-700",
  extracting: "bg-blue-100 text-blue-700 animate-pulse",
  ocr_processing: "bg-blue-100 text-blue-700 animate-pulse",
  segmenting: "bg-blue-100 text-blue-700 animate-pulse",
  analyzing: "bg-indigo-100 text-indigo-700 animate-pulse",
  calculating: "bg-indigo-100 text-indigo-700 animate-pulse",
  completed: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [docName, setDocName] = useState("");
  const [docType, setDocType] = useState("loan_agreement");
  const [docLanguage, setDocLanguage] = useState("auto");
  const [docCountry, setDocCountry] = useState("");

  const loadDocuments = async () => {
    try {
      const data = await documentsApi.list();
      setDocuments(data.items || []);
    } catch { } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadDocuments(); }, []);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setUploadFile(acceptedFiles[0]);
      if (!docName) setDocName(acceptedFiles[0].name.replace(/\.[^/.]+$/, ""));
    }
  }, [docName]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
      "image/jpeg": [".jpg", ".jpeg"],
      "image/png": [".png"],
    },
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024,
  });

  const handleUpload = async () => {
    if (!uploadFile || !docName) { toast.error("Please select a file and enter a name"); return; }
    setUploading(true);
    try {
      const formData = new FormData();
      formData.append("file", uploadFile);
      formData.append("name", docName);
      formData.append("document_type", docType);
      formData.append("language", docLanguage);
      formData.append("country", docCountry);
      await documentsApi.upload(formData);
      toast.success("Document uploaded and queued for analysis!");
      setUploadOpen(false);
      setUploadFile(null);
      setDocName("");
      loadDocuments();
    } catch (err: any) {
      toast.error(err.message || "Upload failed");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string, e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (!confirm("Delete this document and its analysis?")) return;
    try {
      await documentsApi.delete(id);
      toast.success("Document deleted");
      loadDocuments();
    } catch { toast.error("Delete failed"); }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Documents</h1>
          <p className="text-slate-600 mt-1">Upload and manage your financial documents</p>
        </div>
        <Dialog open={uploadOpen} onOpenChange={setUploadOpen}>
          <DialogTrigger asChild>
            <Button className="bg-teal-600 hover:bg-teal-700"><Upload className="h-4 w-4 mr-2" /> Upload</Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-lg">
            <DialogHeader>
              <DialogTitle>Upload Document</DialogTitle>
              <DialogDescription>Upload a financial document for AI analysis</DialogDescription>
            </DialogHeader>
            <div className="space-y-4">
              <div {...getRootProps()} className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${isDragActive ? "border-teal-400 bg-teal-50" : "border-slate-200 hover:border-slate-300"}`}>
                <input {...getInputProps()} />
                <Upload className="h-8 w-8 mx-auto text-slate-400 mb-2" />
                {uploadFile ? (
                  <p className="text-sm font-medium text-slate-900">{uploadFile.name} <span className="text-slate-500">({(uploadFile.size / 1024 / 1024).toFixed(1)}MB)</span></p>
                ) : (
                  <><p className="text-sm text-slate-600">Drag & drop or click to select</p><p className="text-xs text-slate-400 mt-1">PDF, DOCX, JPG, PNG — Max 50MB</p></>
                )}
              </div>
              <div className="space-y-2"><Label>Document Name</Label><Input value={docName} onChange={(e) => setDocName(e.target.value)} placeholder="e.g. Personal Loan Agreement" /></div>
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2"><Label>Document Type</Label>
                  <Select value={docType} onValueChange={setDocType}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>
                    <SelectItem value="loan_agreement">Loan Agreement</SelectItem>
                    <SelectItem value="credit_card">Credit Card Agreement</SelectItem>
                    <SelectItem value="mortgage">Mortgage</SelectItem>
                    <SelectItem value="insurance">Insurance Policy</SelectItem>
                    <SelectItem value="other">Other</SelectItem>
                  </SelectContent></Select></div>
                <div className="space-y-2"><Label>Language</Label>
                  <Select value={docLanguage} onValueChange={setDocLanguage}><SelectTrigger><SelectValue /></SelectTrigger><SelectContent>
                    <SelectItem value="auto">Auto-detect</SelectItem>
                    <SelectItem value="en">English</SelectItem>
                    <SelectItem value="km">Khmer</SelectItem>
                  </SelectContent></Select></div>
              </div>
              <div className="space-y-2"><Label>Country/Jurisdiction (optional)</Label><Input value={docCountry} onChange={(e) => setDocCountry(e.target.value)} placeholder="e.g. Cambodia, USA" /></div>
              <Button onClick={handleUpload} disabled={uploading || !uploadFile} className="w-full bg-teal-600 hover:bg-teal-700">{uploading ? "Uploading..." : "Upload & Analyze"}</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <div className="space-y-3">{[1, 2, 3].map((i) => <Skeleton key={i} className="h-20 w-full" />)}</div>
      ) : documents.length === 0 ? (
        <Card><CardContent className="py-16 text-center">
          <FileText className="h-16 w-16 mx-auto text-slate-300 mb-4" />
          <h3 className="text-lg font-medium text-slate-900">No documents yet</h3>
          <p className="text-sm text-slate-500 mt-2 max-w-sm mx-auto">Upload a financial document to get AI-powered analysis of clauses, risks, and costs.</p>
          <Button className="mt-6 bg-teal-600 hover:bg-teal-700" onClick={() => setUploadOpen(true)}><Upload className="h-4 w-4 mr-2" /> Upload Your First Document</Button>
        </CardContent></Card>
      ) : (
        <div className="space-y-3">
          {documents.map((doc: any) => (
            <Link key={doc.id} href={`/dashboard/documents/${doc.id}`}>
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="h-10 w-10 rounded-lg bg-slate-100 flex items-center justify-center"><FileText className="h-5 w-5 text-slate-500" /></div>
                      <div>
                        <p className="font-medium text-slate-900">{doc.name}</p>
                        <div className="flex items-center gap-3 mt-0.5 text-xs text-slate-500">
                          <span>{doc.file_type?.toUpperCase()}</span>
                          <span>•</span>
                          <span>{(doc.file_size / 1024).toFixed(0)} KB</span>
                          <span>•</span>
                          <span className="flex items-center gap-1"><Clock className="h-3 w-3" />{new Date(doc.created_at).toLocaleDateString()}</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge className={statusColors[doc.status] || "bg-slate-100"}>{doc.status}</Badge>
                      <Button variant="ghost" size="icon" className="text-slate-400 hover:text-red-600" onClick={(e) => handleDelete(doc.id, e)}><Trash2 className="h-4 w-4" /></Button>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
