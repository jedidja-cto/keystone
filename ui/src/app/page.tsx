"use client";

import { useEffect, useState } from "react";

interface DashboardStats {
  total_students: number;
  total_classes: number;
  active_plans: number;
  recent_alerts: string[];
}

export default function DashboardPage() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("http://localhost:8000/dashboard/stats")
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch dashboard stats");
        return res.json();
      })
      .then((data) => {
        setStats(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-pulse text-purple-400">Loading dashboard...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6 bg-red-500/10 border border-red-500/30 rounded-2xl">
        <p className="text-red-400">Error: {error}</p>
        <p className="text-sm text-gray-500 mt-2">Make sure the API server is running on port 8000.</p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <header>
        <h1 className="font-outfit text-4xl font-bold">Welcome back, Teacher</h1>
        <p className="text-gray-400 mt-2">Here's your operational overview for today.</p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard
          title="Total Students"
          value={stats?.total_students ?? 0}
          icon="👨‍🎓"
          color="purple"
        />
        <StatCard
          title="Active Classes"
          value={stats?.total_classes ?? 0}
          icon="🏫"
          color="cyan"
        />
        <StatCard
          title="Lesson Plans"
          value={stats?.active_plans ?? 0}
          icon="📚"
          color="emerald"
        />
      </div>

      <section className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6">
        <h2 className="font-outfit text-xl font-semibold mb-4">Quick Actions</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <QuickAction href="/planning" label="New Lesson" icon="➕" />
          <QuickAction href="/assessments" label="Log Marks" icon="✏️" />
          <QuickAction href="/observations" label="Add Note" icon="📝" />
          <QuickAction href="/reports" label="Generate Report" icon="📄" />
        </div>
      </section>
    </div>
  );
}

function StatCard({ title, value, icon, color }: { title: string; value: number; icon: string; color: string }) {
  const colorClasses: Record<string, string> = {
    purple: "from-purple-500/20 to-purple-600/5 border-purple-500/30",
    cyan: "from-cyan-500/20 to-cyan-600/5 border-cyan-500/30",
    emerald: "from-emerald-500/20 to-emerald-600/5 border-emerald-500/30",
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} border rounded-2xl p-6 transition-transform hover:scale-105`}>
      <div className="flex items-center justify-between">
        <span className="text-3xl">{icon}</span>
        <span className="font-outfit text-4xl font-bold">{value}</span>
      </div>
      <p className="text-gray-400 mt-2">{title}</p>
    </div>
  );
}

function QuickAction({ href, label, icon }: { href: string; label: string; icon: string }) {
  return (
    <a
      href={href}
      className="flex flex-col items-center justify-center gap-2 p-4 bg-white/5 border border-white/10 rounded-xl hover:bg-purple-600/10 hover:border-purple-500/30 transition-all"
    >
      <span className="text-2xl">{icon}</span>
      <span className="text-sm text-gray-300">{label}</span>
    </a>
  );
}
