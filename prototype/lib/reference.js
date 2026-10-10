import fs from "node:fs";
import path from "node:path";

export function getReferenceBody(filename) {
  const source = fs.readFileSync(path.join(process.cwd(), "reference", filename), "utf8");
  const body = source.match(/<body[^>]*>([\s\S]*?)<\/body>/i)?.[1] ?? "";

  return body
    .replace(/<script\b[^>]*>[\s\S]*?<\/script>/gi, "")
    .replaceAll("workspace-preview.html", "/workspace")
    .replaceAll("index.html", "/")
    .replaceAll('src="assets/', 'src="/assets/')
    .replaceAll('poster="assets/', 'poster="/assets/')
    .replace('<div class="hero-grid"></div>', "");
}
