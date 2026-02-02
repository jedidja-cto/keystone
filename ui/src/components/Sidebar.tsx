"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
    { href: "/", label: "Dashboard", icon: "📊" },
    { href: "/planning", label: "Lesson Planning", icon: "📅" },
    { href: "/assessments", label: "Assessments", icon: "📝" },
    { href: "/observations", label: "Observations", icon: "👁️" },
    { href: "/reports", label: "Reports", icon: "📄" },
];

export default function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="fixed left-0 top-0 h-screen w-64 bg-[#0f0f12] border-r border-white/10 p-6 flex flex-col">
            <div className="mb-10">
                <h1 className="font-outfit text-2xl font-bold tracking-tight bg-gradient-to-r from-white to-purple-400 bg-clip-text text-transparent">
                    KEYSTONE
                </h1>
                <p className="text-xs text-gray-500 mt-1">Teacher Dashboard</p>
            </div>

            <nav className="flex-1 space-y-2">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-300 ${isActive
                                    ? "bg-purple-600/20 text-purple-400 border border-purple-500/30"
                                    : "text-gray-400 hover:bg-white/5 hover:text-white"
                                }`}
                        >
                            <span className="text-lg">{item.icon}</span>
                            <span className="font-medium">{item.label}</span>
                        </Link>
                    );
                })}
            </nav>

            <div className="pt-6 border-t border-white/10">
                <p className="text-xs text-gray-600">v1.0.0 | © 2026 Keystone</p>
            </div>
        </aside>
    );
}
