"use client";

import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip, LineChart, Line, XAxis, YAxis, CartesianGrid } from "recharts";

const lime = "#c8ff32";
const dark = "#10120f";

export function RiskDistribution({ data }: { data: { name: string; value: number }[] }) {
  return <div className="h-72 w-full"><ResponsiveContainer><PieChart><Pie data={data} dataKey="value" nameKey="name" innerRadius={72} outerRadius={104} paddingAngle={3}>{data.map((entry, index) => <Cell key={entry.name} fill={index === 2 ? dark : index === 1 ? "#89917f" : "#ccd2c6"} />)}</Pie><Tooltip contentStyle={{ borderRadius: 14, border: 0 }} /></PieChart></ResponsiveContainer></div>;
}

export function ActivityChart({ data }: { data: { hour: string; count: number }[] }) {
  return <div className="h-72 w-full"><ResponsiveContainer><LineChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="rgba(16,18,15,.08)" /><XAxis dataKey="hour" tick={{ fontSize: 11 }} /><YAxis tick={{ fontSize: 11 }} /><Tooltip contentStyle={{ borderRadius: 14, border: 0 }} /><Line type="monotone" dataKey="count" stroke={dark} strokeWidth={3} dot={false} /></LineChart></ResponsiveContainer></div>;
}

export function ThresholdChart({ data }: { data: { threshold: number; precision: number; recall: number; f1: number }[] }) {
  return <div className="h-80 w-full"><ResponsiveContainer><LineChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="rgba(16,18,15,.08)" /><XAxis dataKey="threshold" tick={{ fontSize: 11 }} /><YAxis domain={[0, 1]} tick={{ fontSize: 11 }} /><Tooltip formatter={(value) => Number(value).toFixed(3)} contentStyle={{ borderRadius: 14, border: 0 }} /><Line type="monotone" dataKey="precision" stroke={dark} strokeWidth={3} dot={false} /><Line type="monotone" dataKey="recall" stroke="#8c9684" strokeWidth={3} dot={false} /><Line type="monotone" dataKey="f1" stroke={lime} strokeWidth={3} dot={false} /></LineChart></ResponsiveContainer></div>;
}
