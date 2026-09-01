export const API_URL = (process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api").replace(/\/$/, "");

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, { cache: "no-store", ...init });
  const text = await response.text();
  let payload: unknown = null;
  try { payload = text ? JSON.parse(text) : null; } catch { payload = { detail: text }; }
  if (!response.ok) {
    const detail = typeof payload === "object" && payload && "detail" in payload ? String((payload as { detail: unknown }).detail) : "Request failed";
    throw new Error(detail);
  }
  return payload as T;
}

export type Prediction = {
  transaction_id: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  fraud_probability: number;
  reasons: string[];
  top_features: { feature: string; importance: number; signal: number; direction: string }[];
  recommended_action: string;
  transaction: Record<string, unknown>;
};

export type Dashboard = {
  transactions_analyzed: number;
  high_risk: number;
  medium_risk: number;
  low_risk: number;
  estimated_loss_prevented: number;
  estimated_high_risk_exposure: number;
  model_precision: number;
  risk_distribution: { name: string; value: number }[];
  activity: { hour: string; count: number }[];
  model_available: boolean;
  recent_transactions: TransactionSummary[];
};

export type TransactionSummary = {
  transaction_id: string;
  amount: number;
  customer_id: string;
  country: string;
  payment_method: string;
  risk_score: number;
  risk_level: "LOW" | "MEDIUM" | "HIGH";
  fraud_probability: number;
  reasons: string[];
  created_at: string;
};

export type Metrics = {
  model_name: string;
  test_size: number;
  fraud_prevalence: number;
  threshold: number;
  precision: number;
  recall: number;
  f1: number;
  roc_auc: number;
  false_positive_rate: number;
  false_positive_cost: number;
  false_negative_cost: number;
  estimated_prevented_loss: number;
  confusion_matrix: number[][];
  feature_importance: { feature: string; importance: number }[];
  baseline_validation_roc_auc?: number;
  final_validation_roc_auc?: number;
  threshold_curve: { threshold: number; precision: number; recall: number; f1: number }[];
  evaluation_note: string;
  cost_assumptions: Record<string, string>;
};
