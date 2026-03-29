"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV_ITEMS = [
  { href: "/", label: "홈", icon: "⌂" },
  { href: "/org", label: "조직 관리", icon: "🔗" },
  { href: "/map", label: "유세지 지도", icon: "📍" },
  { href: "/report", label: "전략 리포트", icon: "📋" },
];

export default function Navbar() {
  const pathname = usePathname();

  return (
    <nav className="h-14 bg-gray-900 border-b border-gray-700 flex items-center px-6 gap-6 shrink-0">
      <span className="font-bold text-white mr-2">선거 캠프</span>
      <div className="flex items-center gap-1">
        {NAV_ITEMS.map((item) => {
          const active =
            item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-sm transition-colors ${
                active
                  ? "bg-blue-600 text-white"
                  : "text-gray-400 hover:text-white hover:bg-gray-800"
              }`}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
