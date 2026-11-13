import { get } from "@/server/local-api.mjs";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export async function GET(request, context) { const { id } = await context.params; return get(request, "result", id); }
