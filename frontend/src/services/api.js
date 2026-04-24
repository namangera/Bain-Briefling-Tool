const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export async function generateBriefing(company, filters = {}) {
  const body = { company };

  if (filters.fromDate) body.from_date = filters.fromDate;
  if (filters.toDate) body.to_date = filters.toDate;
  if (filters.sortBy) body.sort_by = filters.sortBy;
  if (filters.domains?.length > 0) body.domains = filters.domains.join(",");

  const response = await fetch(`${API_URL}/api/brief`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "An unexpected error occurred");
  }

  return data;
}
