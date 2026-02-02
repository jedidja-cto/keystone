"use client";

import { useState } from "react";

const categories = ["Academic", "Behavioral", "Social", "Emotional", "Other"];

export default function ObservationsPage() {
    const [category, setCategory] = useState("Academic");
    const [note, setNote] = useState("");

    return (
        <div className="space-y-8">
            <header>
                <h1 className="font-outfit text-4xl font-bold">Observations</h1>
                <p className="text-gray-400 mt-2">Capture qualitative student observations.</p>
            </header>

            <div className="grid md:grid-cols-2 gap-8">
                <section className="bg-white/5 border border-white/10 rounded-2xl p-6">
                    <h2 className="font-outfit text-xl font-semibold mb-4">New Observation</h2>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm text-gray-400 mb-2">Category</label>
                            <div className="flex flex-wrap gap-2">
                                {categories.map((cat) => (
                                    <button
                                        key={cat}
                                        onClick={() => setCategory(cat)}
                                        className={`px-4 py-2 rounded-xl text-sm transition-all ${category === cat
                                                ? "bg-purple-600 text-white"
                                                : "bg-white/5 border border-white/10 text-gray-400 hover:bg-white/10"
                                            }`}
                                    >
                                        {cat}
                                    </button>
                                ))}
                            </div>
                        </div>

                        <div>
                            <label className="block text-sm text-gray-400 mb-2">Observation Note</label>
                            <textarea
                                value={note}
                                onChange={(e) => setNote(e.target.value)}
                                placeholder="Describe what you observed..."
                                rows={4}
                                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-xl focus:border-purple-500 focus:outline-none transition-all resize-none"
                            />
                        </div>

                        <button className="w-full py-3 bg-purple-600 hover:bg-purple-700 rounded-xl font-semibold transition-all">
                            Save Observation
                        </button>
                    </div>
                </section>

                <section className="bg-white/5 border border-white/10 rounded-2xl p-6">
                    <h2 className="font-outfit text-xl font-semibold mb-4">Filter by Category</h2>

                    <div className="space-y-3">
                        {categories.map((cat) => (
                            <div
                                key={cat}
                                className="flex items-center justify-between p-3 bg-white/5 rounded-xl"
                            >
                                <span>{cat}</span>
                                <span className="text-xs text-gray-500">0 entries</span>
                            </div>
                        ))}
                    </div>
                </section>
            </div>
        </div>
    );
}
