"use client";

import { useState } from "react";

export default function PlanningPage() {
    const [plans, setPlans] = useState<any[]>([]);
    const [loading, setLoading] = useState(false);

    return (
        <div className="space-y-8">
            <header className="flex items-center justify-between">
                <div>
                    <h1 className="font-outfit text-4xl font-bold">Lesson Planning</h1>
                    <p className="text-gray-400 mt-2">Create and manage your lesson plans.</p>
                </div>
                <button className="px-6 py-3 bg-purple-600 hover:bg-purple-700 rounded-xl font-semibold transition-all">
                    + New Plan
                </button>
            </header>

            <div className="grid gap-4">
                <div className="bg-white/5 border border-white/10 rounded-2xl p-6">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="font-semibold text-lg">Today's Schedule</h3>
                        <span className="text-sm text-gray-500">February 2026</span>
                    </div>

                    <div className="space-y-3">
                        <PlanCard
                            time="08:00 - 09:30"
                            subject="Mathematics"
                            topic="Introduction to Calculus"
                            class_name="Grade 12A"
                        />
                        <PlanCard
                            time="10:00 - 11:30"
                            subject="Physics"
                            topic="Newton's Laws of Motion"
                            class_name="Grade 11B"
                        />
                        <PlanCard
                            time="13:00 - 14:30"
                            subject="Mathematics"
                            topic="Geometry Basics"
                            class_name="Grade 10C"
                        />
                    </div>
                </div>
            </div>

            <section className="bg-gradient-to-br from-purple-500/10 to-transparent border border-purple-500/20 rounded-2xl p-6">
                <h2 className="font-outfit text-xl font-semibold mb-2">Pacing Suggestion</h2>
                <p className="text-gray-400">Based on your calendar, you're on track for this term. Consider reviewing the upcoming exam period for Grade 12.</p>
            </section>
        </div>
    );
}

function PlanCard({ time, subject, topic, class_name }: { time: string; subject: string; topic: string; class_name: string }) {
    return (
        <div className="flex items-center gap-4 p-4 bg-white/5 border border-white/10 rounded-xl hover:border-purple-500/30 transition-all cursor-pointer">
            <div className="text-sm text-gray-500 w-28">{time}</div>
            <div className="flex-1">
                <h4 className="font-semibold">{subject}</h4>
                <p className="text-sm text-gray-400">{topic}</p>
            </div>
            <span className="text-xs text-gray-500 bg-white/10 px-3 py-1 rounded-full">{class_name}</span>
        </div>
    );
}
