// Helpers to drive SurrealDB Studio (cloud) in a take: open the instance, switch namespace/database, open a table.
// STUDIO_URL = the instance page the user is logged into, e.g. https://studio.surrealdb.com/<org>/instances/<instance>
export const STUDIO = process.env.STUDIO_URL;
export async function studioOpen(p) {
  if (!STUDIO) throw new Error('set STUDIO_URL');
  await p.goto(STUDIO, { waitUntil: 'networkidle' });
  await p.getByText('Got it').click({ timeout: 2500 }).catch(() => {});
  await p.locator('button[aria-label*="lose"], [aria-label="Close"]').first().click({ timeout: 1500 }).catch(() => {});
}
// crumb = current db name shown in breadcrumb
export async function pickDb(p, db) {
  // the db switcher is the breadcrumb right after the instance name (STUDIO_INSTANCE = that name)
  const crumb = p.getByText(process.env.STUDIO_INSTANCE, { exact: true }).first().locator('xpath=following::*[normalize-space(text())!=""][2]');
  console.log('crumb', await crumb.textContent());
  await crumb.click(); await p.waitForTimeout(700);
  const menu = p.getByPlaceholder('Search databases').locator('xpath=ancestor::*[.//*[normalize-space(text())="Manage databases"]][1]');
  await menu.getByText(db, { exact: true }).last().click(); await p.waitForTimeout(1500);
}

export async function openTable(p, name) {
  await p.getByText('Tables', { exact: true }).first().click().catch(() => {});
  const item = p.getByText(name, { exact: true }).first();
  await item.waitFor({ timeout: 20000 }); await item.click(); await p.waitForTimeout(2000);
}
export async function openDbMenu(p) {
  const crumb = p.getByText(process.env.STUDIO_INSTANCE, { exact: true }).first().locator('xpath=following::*[normalize-space(text())!=""][2]');
  await crumb.click(); await p.waitForTimeout(700);
  return p.getByPlaceholder('Search databases').locator('xpath=ancestor::*[.//*[normalize-space(text())="Manage databases"]][1]');
}
