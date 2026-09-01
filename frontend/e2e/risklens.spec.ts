import { test, expect } from "@playwright/test";

const csv = [
  "transaction_id,amount,customer_id,account_age_days,device_id,country,transactions_last_10m,transactions_last_1h,failed_payments,previous_avg_amount,is_new_device,is_new_location,distance_from_previous_location,device_transaction_count,ip_transaction_count,payment_method,hour,customer_transaction_count",
  "E2E_NORMAL,1200,C1,500,D1,IN,1,3,0,1100,0,0,10,2,1,upi,13,60",
  "E2E_RISKY,42850,C2,24,D2,US,8,16,4,10100,1,1,2100,15,11,card,2,18",
].join("\n");

function attachConsoleGuard(page: import("@playwright/test").Page) {
  const errors: string[] = [];
  page.on("pageerror", (error) => errors.push(`pageerror: ${error.message}`));
  page.on("console", (message) => {
    if (message.type() === "error") errors.push(`console: ${message.text()}`);
  });
  return () => expect(errors, errors.join("\n")).toEqual([]);
}

test.describe("RiskLens core journeys", () => {
  test("desktop routes and main navigation render without browser errors", async ({ page }) => {
    const assertNoErrors = attachConsoleGuard(page);
    await page.goto("/");
    await expect(page.getByRole("heading", { name: /Stop fraud/i })).toBeVisible();
    await page.getByRole("link", { name: "Dashboard", exact: true }).click();
    await expect(page).toHaveURL(/\/dashboard$/);
    await expect(page.getByRole("heading", { name: /Know your risk/i })).toBeVisible();
    await page.getByRole("link", { name: "Analyze", exact: true }).click();
    await expect(page).toHaveURL(/\/analyze$/);
    await expect(page.getByRole("heading", { name: /Every payment carries a risk signal/i })).toBeVisible();
    await page.getByRole("link", { name: "Transactions", exact: true }).click();
    await expect(page).toHaveURL(/\/transactions$/);
    await expect(page.getByRole("heading", { name: /Review the signal/i })).toBeVisible();
    await page.getByRole("link", { name: "Model", exact: true }).click();
    await expect(page).toHaveURL(/\/model$/);
    await expect(page.getByRole("heading", { name: /Trust, then verify/i })).toBeVisible();
    assertNoErrors();
  });

  test("single transaction analysis flows into review detail", async ({ page }) => {
    const assertNoErrors = attachConsoleGuard(page);
    await page.goto("/analyze");
    await page.getByRole("button", { name: "Analyze risk" }).click();
    await expect(page.getByText("Risk result")).toBeVisible();
    await expect(page.getByText(/Fraud probability/i)).toBeVisible();
    await expect(page.getByRole("link", { name: "Review transaction" })).toBeVisible();
    await page.getByRole("link", { name: "Review transaction" }).click();
    await expect(page).toHaveURL(/\/transactions\/.+/);
    await expect(page.getByText(/Risk contributors/i)).toBeVisible();
    assertNoErrors();
  });

  test("CSV upload produces a real batch summary", async ({ page }) => {
    const assertNoErrors = attachConsoleGuard(page);
    await page.goto("/analyze");
    await page.getByRole("button", { name: "CSV upload" }).click();
    await page.locator('input[type="file"]').setInputFiles({ name: "e2e.csv", mimeType: "text/csv", buffer: Buffer.from(csv) });
    await expect(page.getByText("Batch summary")).toBeVisible();
    await expect(page.getByText("Valid transactions")).toBeVisible();
    await expect(page.getByText("2", { exact: true }).first()).toBeVisible();
    await expect(page.getByRole("link", { name: "Download results CSV" })).toHaveAttribute("href", /\/api\/transactions\/export$/);
    assertNoErrors();
  });

  test("mobile navigation exposes and activates all major sections", async ({ page }) => {
    const assertNoErrors = attachConsoleGuard(page);
    await page.goto("/");
    await page.getByRole("button", { name: /Toggle navigation/i }).click();
    await expect(page.getByRole("link", { name: "Dashboard", exact: true }).last()).toBeVisible();
    await page.getByRole("link", { name: "Model", exact: true }).last().click();
    await expect(page).toHaveURL(/\/model$/);
    assertNoErrors();
  });
});
