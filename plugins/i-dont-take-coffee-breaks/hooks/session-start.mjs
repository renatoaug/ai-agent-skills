// SessionStart hook: loads the skill's rules into every session, so they apply
// even when nothing in the conversation would trigger the skill itself.
// Never blocks session start: any failure exits 0 with no output.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

try {
  const here = path.dirname(fileURLToPath(import.meta.url));
  const skillPath = path.join(here, "..", "skills", "i-dont-take-coffee-breaks", "SKILL.md");
  const body = fs
    .readFileSync(skillPath, "utf8")
    .replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n/, "")
    .trim();

  process.stdout.write(
    "TIME ESTIMATES IN AGENT TIME (always-on). Apply the rules below to every duration you write in this session.\n\n" +
      body +
      "\n",
  );
} catch {
  process.exit(0);
}
