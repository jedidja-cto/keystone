"use client";

import { useState } from "react";

export default function AssessmentsPage() {
    const [studentId, setStudentId] = useState("");
    const [assessmentId, setAssessmentId] = useState("");
    const [value, setValue] = useState("");
    const [status, setStatus] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setStatus("Submitting...");

        try {
            const res = await fetch("http://localhost:8000/marks", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    student_id: studentId,
                    assessment_id: assessmentId,
                    value: parseFloat(value),
                }),
            });

            if (res.ok) {
                setStatus("✓ Mark logged successfully!");
                setStudentId("");
                setAssessmentId("");
                setValue("");
            } else {
                const err = await res.json();
                setStatus(`Error: ${err.detail}`);
            }
        } catch (err) {
            setStatus("Failed to connect to API");
        }
    };

    return (
        <div className="space-y-8">
            <header>
                <h1 className="font-outfit text-4xl font-bold">Assessments</h1>
                <p className="text-gray-400 mt-2">Log and manage student assessment marks.</p>
            </header>

            <div className="grid md:grid-cols-2 gap-8">
                <section className="bg-white/5 border border-white/10 rounded-2xl p-6">
                    <h2 className="font-outfit text-xl font-semibold mb-4">Log New Mark</h2>

                    <form onSubmit={handleSubmit} className="space-y-4">
                        <div>
                            <label className="block text-sm text-gray-400 mb-2">Student ID</label>
                            <input
                                type="text"
                                value={studentId}
                                onChange={(e) => setStudentId(e.target.value)}
                                placeholder="Enter student ID"
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-purple-500 focus:outline-none transition-all"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm text-gray-400 mb-2">Assessment ID</label>
                            <input
                                type="text"
                                value={assessmentId}
                                onChange={(e) => setAssessmentId(e.target.value)}
                                placeholder="Enter assessment ID"
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-purple-500 focus:outline-none transition-all"
                                required
                            />
                        </div>

                        <div>
                            <label className="block text-sm text-gray-400 mb-2">Mark Value</label>
                            <input
                                type="number"
                                value={value}
                                onChange={(e) => setValue(e.target.value)}
                                placeholder="e.g., 85"
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-purple-500 focus:outline-none transition-all"
                                required
                            />
                        </div>

                        <button
                            type="submit"
                            className="w-full py-3 bg-purple-600 hover:bg-purple-700 rounded-xl font-semibold transition-all"
                        >
                            Submit Mark
                        </button>

                        {status && (
                            <p className={`text-sm ${status.startsWith("✓") ? "text-green-400" : "text-yellow-400"}`}>
                                {status}
                            </p>
                        )}
                    </form>
                </section>

                <section className="bg-white/5 border border-white/10 rounded-2xl p-6">
                    <h2 className="font-outfit text-xl font-semibold mb-4">Recent Entries</h2>
                    <p className="text-gray-500 text-sm">No recent marks logged. Start by adding a new entry.</p>
                </section>
            </div>
        </div>
    );
}
