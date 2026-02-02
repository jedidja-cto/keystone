"use client";

import { useState } from "react";

export default function ReportsPage() {
    const [studentId, setStudentId] = useState("");
    const [termId, setTermId] = useState("");
    const [report, setReport] = useState<any>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const generateReport = async () => {
        if (!studentId || !termId) return;

        setLoading(true);
        setError(null);

        try {
            const res = await fetch(`http://localhost:8000/reports/student/${studentId}/${termId}`);
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail);
            }
            const data = await res.json();
            setReport(data);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="space-y-8">
            <header>
                <h1 className="font-outfit text-4xl font-bold">Reports</h1>
                <p className="text-gray-400 mt-2">Generate and preview student progress reports.</p>
            </header>

            <div className="grid md:grid-cols-3 gap-8">
                <section className="bg-white/5 border border-white/10 rounded-2xl p-6">
                    <h2 className="font-outfit text-xl font-semibold mb-4">Generate Report</h2>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm text-gray-400 mb-2">Student ID</label>
                            <input
                                type="text"
                                value={studentId}
                                onChange={(e) => setStudentId(e.target.value)}
                                placeholder="Enter student ID"
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-purple-500 focus:outline-none transition-all"
                            />
                        </div>

                        <div>
                            <label className="block text-sm text-gray-400 mb-2">Term ID</label>
                            <input
                                type="text"
                                value={termId}
                                onChange={(e) => setTermId(e.target.value)}
                                placeholder="Enter term ID"
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-purple-500 focus:outline-none transition-all"
                            />
                        </div>

                        <button
                            onClick={generateReport}
                            disabled={loading}
                            className="w-full py-3 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 rounded-xl font-semibold transition-all"
                        >
                            {loading ? "Generating..." : "Generate Report"}
                        </button>
                    </div>
                </section>

                <section className="md:col-span-2 bg-white/5 border border-white/10 rounded-2xl p-6">
                    <h2 className="font-outfit text-xl font-semibold mb-4">Report Preview</h2>

                    {error && (
                        <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
                            {error}
                        </div>
                    )}

                    {!report && !error && (
                        <p className="text-gray-500">Enter student and term IDs to generate a report.</p>
                    )}

                    {report && (
                        <div className="space-y-4 text-sm">
                            <div className="p-4 bg-white/5 rounded-xl">
                                <h3 className="font-semibold mb-2">Student Information</h3>
                                <p className="text-gray-400">{JSON.stringify(report.student, null, 2)}</p>
                            </div>

                            <div className="p-4 bg-white/5 rounded-xl">
                                <h3 className="font-semibold mb-2">Academic Performance</h3>
                                <pre className="text-gray-400 overflow-auto">
                                    {JSON.stringify(report.subjects, null, 2)}
                                </pre>
                            </div>
                        </div>
                    )}
                </section>
            </div>
        </div>
    );
}
